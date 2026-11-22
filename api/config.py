import os
from dataclasses import dataclass

VALID_STAGES = ("m0", "m1", "m2", "m3")


@dataclass(frozen=True)
class Settings:
    database_url: str
    engine_stage: str
    git_commit: str
    cache_ttl_seconds: int
    db_pool_min: int
    db_pool_max: int


def get_settings() -> Settings:
    stage = os.getenv("ENGINE_STAGE", "m0").strip().lower()
    if stage not in VALID_STAGES:
        raise ValueError(f"ENGINE_STAGE invalido: '{stage}'. Validos: {VALID_STAGES}")

    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/academica_db",
        ),
        engine_stage=stage,
        git_commit=os.getenv("GIT_COMMIT", "unknown"),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
        db_pool_min=int(os.getenv("DB_POOL_MIN", "1")),
        db_pool_max=int(os.getenv("DB_POOL_MAX", "5")),
    )
