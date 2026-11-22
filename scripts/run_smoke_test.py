"""
Prueba de humo obligatoria antes de cada tanda experimental (Clase 7):
Verifica que la URL responde HTTP 200, corresponde al ENGINE_STAGE esperado,
pertenece al mismo GIT_COMMIT y devuelve una consolidacion valida.
"""
import os
import sys
import requests


def main() -> None:
    base_url = os.environ["BASE_URL"].rstrip("/")
    expected_stage = os.environ["EXPECTED_STAGE"].strip().lower()
    expected_commit = os.getenv("EXPECTED_COMMIT", "").strip()

    health_resp = requests.get(f"{base_url}/api/v1/health", timeout=30)
    if health_resp.status_code != 200:
        sys.exit(f"[ERROR] /health retorno {health_resp.status_code}: {health_resp.text}")

    health = health_resp.json()
    if health.get("engine_stage") != expected_stage:
        sys.exit(
            f"[ERROR] Etapa incorrecta en {base_url}: esperado={expected_stage}, "
            f"recibido={health.get('engine_stage')}"
        )

    if expected_commit and health.get("git_commit") != expected_commit:
        sys.exit(
            f"[ERROR] Commit inconsistente: esperado={expected_commit}, "
            f"recibido={health.get('git_commit')}"
        )

    payload = {"student_codes": [f"STU{i:05d}" for i in range(1, 11)]}
    post_resp = requests.post(
        f"{base_url}/api/v1/consolidate",
        json=payload,
        timeout=60,
    )
    if post_resp.status_code != 200:
        sys.exit(f"[ERROR] /consolidate retorno {post_resp.status_code}: {post_resp.text}")

    body = post_resp.json()
    if body.get("batch_size") != 10 or len(body.get("summaries", [])) != 10:
        sys.exit(f"[ERROR] Cuerpo invalido en /consolidate: {body}")

    print(
        f"[OK] Smoke test superado | stage={health['engine_stage']} | "
        f"commit={health['git_commit']} | rows={health['enrollments_count']} | "
        f"server_ms={body['process_time_ms']}"
    )


if __name__ == "__main__":
    main()
