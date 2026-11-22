import platform
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from api.config import VALID_STAGES, get_settings
from api.db import close_pool, get_connection, init_pool
from api.service import consolidate_records


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_pool()
    try:
        yield
    finally:
        close_pool()


app = FastAPI(
    title="API de Consolidacion de Historiales Academicos",
    version="1.0.0",
    lifespan=lifespan,
)


class ConsolidateRequest(BaseModel):
    student_codes: List[str] = Field(
        ..., min_length=1, max_length=2000, description="Codigos de estudiantes"
    )


@app.get("/api/v1/health")
def health_check() -> Dict[str, Any]:
    settings = get_settings()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM enrollments")
            enrollments_count = cur.fetchone()[0]
            cur.execute("SELECT version()")
            pg_version = cur.fetchone()[0]
    return {
        "status": "ok",
        "engine_stage": settings.engine_stage,
        "git_commit": settings.git_commit,
        "python_version": platform.python_version(),
        "enrollments_count": enrollments_count,
        "postgres_version": pg_version,
    }


@app.post("/api/v1/consolidate")
def consolidate_endpoint(
    payload: ConsolidateRequest, response: Response
) -> Dict[str, Any]:
    settings = get_settings()
    t0 = time.perf_counter()
    with get_connection() as conn:
        summaries = consolidate_records(
            conn=conn,
            student_codes=payload.student_codes,
            stage=settings.engine_stage,
        )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.3f}"
    response.headers["X-Engine-Stage"] = settings.engine_stage
    response.headers["X-Git-Commit"] = settings.git_commit

    return {
        "engine_stage": settings.engine_stage,
        "git_commit": settings.git_commit,
        "batch_size": len(summaries),
        "process_time_ms": round(elapsed_ms, 3),
        "summaries": summaries,
    }


@app.get("/api/v1/explain")
def explain_query(stage: str = "m1", batch_size: int = 100) -> Dict[str, Any]:
    """Devuelve EXPLAIN ANALYZE real en PostgreSQL para evidenciar Seq Scan vs Index Scan (OE1)."""
    stage_norm = stage.strip().lower()
    if stage_norm not in VALID_STAGES:
        raise HTTPException(status_code=400, detail="Etapa invalida")
    if not (1 <= batch_size <= 1000):
        raise HTTPException(status_code=400, detail="batch_size fuera de rango")

    codes = [f"STU{i:05d}" for i in range(1, batch_size + 1)]
    with get_connection() as conn:
        with conn.cursor() as cur:
            if stage_norm in ("m0", "m1"):
                cur.execute(
                    """
                    EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
                    SELECT student_code, course_code, term_code, grade, status
                    FROM enrollments
                    WHERE UPPER(student_code) = ANY(%s)
                    """,
                    (codes,),
                )
            else:
                cur.execute(
                    """
                    EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
                    SELECT student_code, course_code, term_code, grade, status
                    FROM enrollments
                    WHERE student_code = ANY(%s)
                    """,
                    (codes,),
                )
            plan_lines = [row[0] for row in cur.fetchall()]
    return {"stage": stage_norm, "batch_size": batch_size, "plan": plan_lines}
