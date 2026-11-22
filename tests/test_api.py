import os
import pytest
from fastapi.testclient import TestClient

from api.db import close_pool, get_connection, init_pool
from api.main import app
from api.service import consolidate_records, reset_cache
from scripts.seed_db import seed_database

TEST_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/academica_db",
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Semilla pequena y deterministica para CI rapido sobre PostgreSQL real (200 estudiantes = 2000 filas)
    seed_database(TEST_DB_URL, num_students=200, enrollments_per_student=10)
    init_pool(TEST_DB_URL)
    yield
    close_pool()


def test_functional_equivalence_across_all_stages():
    """
    Prueba obligatoria de equivalencia funcional (Clase 6):
    M0, M1, M2 y M3 deben producir exactamente el mismo resultado consolidado.
    """
    batch = [f"STU{i:05d}" for i in range(1, 26)]
    reset_cache()

    with get_connection() as conn:
        res_m0 = consolidate_records(conn, batch, "m0")
        res_m1 = consolidate_records(conn, batch, "m1")
        res_m2 = consolidate_records(conn, batch, "m2")
        res_m3_cold = consolidate_records(conn, batch, "m3")
        res_m3_warm = consolidate_records(conn, batch, "m3")

    assert len(res_m0) == 25
    assert res_m0 == res_m1, "M1 difiere funcionalmente de M0"
    assert res_m0 == res_m2, "M2 difiere funcionalmente de M0"
    assert res_m0 == res_m3_cold, "M3 (frio) difiere funcionalmente de M0"
    assert res_m0 == res_m3_warm, "M3 (caliente) difiere funcionalmente de M0"


@pytest.mark.parametrize("stage", ["m0", "m1", "m2", "m3"])
def test_http_integration_health_and_consolidate(monkeypatch, stage):
    monkeypatch.setenv("ENGINE_STAGE", stage)
    monkeypatch.setenv("GIT_COMMIT", "ci-test-sha")
    reset_cache()

    with TestClient(app) as client:
        h = client.get("/api/v1/health")
        assert h.status_code == 200
        h_data = h.json()
        assert h_data["status"] == "ok"
        assert h_data["engine_stage"] == stage

        payload = {"student_codes": ["STU00001", "STU00002", "STU00003"]}
        r = client.post("/api/v1/consolidate", json=payload)
        assert r.status_code == 200
        assert "X-Process-Time-Ms" in r.headers
        assert r.headers["X-Engine-Stage"] == stage
        body = r.json()
        assert body["batch_size"] == 3
        assert len(body["summaries"]) == 3
