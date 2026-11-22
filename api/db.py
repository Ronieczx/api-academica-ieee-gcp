from contextlib import contextmanager
from typing import Generator, Optional
from psycopg2 import pool
from psycopg2.extensions import connection as PGConnection

from api.config import get_settings

_pool: Optional[pool.ThreadedConnectionPool] = None


def init_pool(database_url: Optional[str] = None) -> None:
    global _pool
    if _pool is not None:
        return
    settings = get_settings()
    dsn = database_url or settings.database_url
    _pool = pool.ThreadedConnectionPool(
        minconn=settings.db_pool_min,
        maxconn=settings.db_pool_max,
        dsn=dsn,
    )


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_connection() -> Generator[PGConnection, None, None]:
    if _pool is None:
        init_pool()
    assert _pool is not None
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)
