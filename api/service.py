import time
from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from psycopg2.extensions import connection as PGConnection


class CourseCatalogCache:
    """Cache en memoria con TTL para el catalogo estatico de cursos (etapa M3)."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self._ttl = ttl_seconds
        self._data: Optional[Dict[str, Tuple[str, int, str]]] = None
        self._loaded_at: float = 0.0

    def clear(self) -> None:
        self._data = None
        self._loaded_at = 0.0

    def get_or_load(self, conn: PGConnection) -> Dict[str, Tuple[str, int, str]]:
        now = time.monotonic()
        if self._data is not None and (now - self._loaded_at) < self._ttl:
            return self._data

        with conn.cursor() as cur:
            cur.execute(
                "SELECT course_code, course_name, credits, department FROM courses"
            )
            rows = cur.fetchall()

        self._data = {
            row[0]: (row[1], int(row[2]), row[3])
            for row in rows
        }
        self._loaded_at = now
        return self._data


_course_cache = CourseCatalogCache(ttl_seconds=300)


def reset_cache() -> None:
    _course_cache.clear()


def _build_student_summary(
    student_code: str,
    records: List[Tuple[str, str, Decimal, str]],
    credits_lookup: Dict[str, int],
) -> Dict[str, Any]:
    total_credits = 0
    approved_credits = 0
    weighted_sum = 0.0
    terms = set()

    for course_code, term_code, grade, status in records:
        credits = credits_lookup[course_code]
        grade_f = float(grade)
        total_credits += credits
        weighted_sum += grade_f * credits
        if status == "APPROVED":
            approved_credits += credits
        terms.add(term_code)

    weighted_gpa = round(weighted_sum / total_credits, 2) if total_credits > 0 else 0.0
    return {
        "student_code": student_code,
        "enrolled_courses": len(records),
        "terms_count": len(terms),
        "total_credits": total_credits,
        "approved_credits": approved_credits,
        "weighted_gpa": weighted_gpa,
    }


def _consolidate_m0(
    conn: PGConnection, student_codes: List[str]
) -> List[Dict[str, Any]]:
    """
    M0 (Linea base sin optimizar):
    - Antipattern N+1: ejecuta 1 consulta SQL por cada estudiante del lote.
    - Predicado no sargable: UPPER(student_code) = UPPER(%s) impide usar indice.
    - Sin cache y busqueda lineal sobre el catalogo de cursos en capa de aplicacion.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT course_code, course_name, credits, department FROM courses"
        )
        courses_list = cur.fetchall()

    summaries: List[Dict[str, Any]] = []
    with conn.cursor() as cur:
        for raw_code in sorted(student_codes):
            cur.execute(
                """
                SELECT course_code, term_code, grade, status
                FROM enrollments
                WHERE UPPER(student_code) = UPPER(%s)
                ORDER BY term_code, course_code
                """,
                (raw_code,),
            )
            rows = cur.fetchall()

            total_credits = 0
            approved_credits = 0
            weighted_sum = 0.0
            terms = set()

            for course_code, term_code, grade, status in rows:
                credits = 0
                for c_code, _c_name, c_credits, _c_dept in courses_list:
                    if c_code == course_code:
                        credits = int(c_credits)
                        break
                grade_f = float(grade)
                total_credits += credits
                weighted_sum += grade_f * credits
                if status == "APPROVED":
                    approved_credits += credits
                terms.add(term_code)

            weighted_gpa = (
                round(weighted_sum / total_credits, 2) if total_credits > 0 else 0.0
            )
            summaries.append(
                {
                    "student_code": raw_code.strip().upper(),
                    "enrolled_courses": len(rows),
                    "terms_count": len(terms),
                    "total_credits": total_credits,
                    "approved_credits": approved_credits,
                    "weighted_gpa": weighted_gpa,
                }
            )
    return summaries


def _consolidate_m1(
    conn: PGConnection, student_codes: List[str]
) -> List[Dict[str, Any]]:
    """
    M1 (OE2 - Capa de aplicacion):
    - Elimina N+1 mediante una sola consulta agrupada (ANY).
    - Estructura hash (dict) O(1) para catalogo de cursos y agrupacion en memoria.
    - Mantiene predicado no sargable UPPER(student_code) para aislar OE2 de OE3.
    """
    normalized = sorted({c.strip().upper() for c in student_codes})
    with conn.cursor() as cur:
        cur.execute(
            "SELECT course_code, credits FROM courses"
        )
        credits_map = {code: int(cr) for code, cr in cur.fetchall()}

        cur.execute(
            """
            SELECT student_code, course_code, term_code, grade, status
            FROM enrollments
            WHERE UPPER(student_code) = ANY(%s)
            """,
            (normalized,),
        )
        rows = cur.fetchall()

    grouped: Dict[str, List[Tuple[str, str, Decimal, str]]] = defaultdict(list)
    for s_code, c_code, t_code, grade, status in rows:
        grouped[s_code].append((c_code, t_code, grade, status))

    return [
        _build_student_summary(code, grouped.get(code, []), credits_map)
        for code in normalized
    ]


def _consolidate_m2(
    conn: PGConnection, student_codes: List[str]
) -> List[Dict[str, Any]]:
    """
    M2 (OE3 - Capa de persistencia):
    - Consulta agrupada + predicado sargable student_code = ANY(%s)
      que habilita el indice compuesto idx_enrollments_student_term.
    - Aun consulta la tabla courses en cada solicitud (sin cache).
    """
    normalized = sorted({c.strip().upper() for c in student_codes})
    with conn.cursor() as cur:
        cur.execute(
            "SELECT course_code, credits FROM courses"
        )
        credits_map = {code: int(cr) for code, cr in cur.fetchall()}

        cur.execute(
            """
            SELECT student_code, course_code, term_code, grade, status
            FROM enrollments
            WHERE student_code = ANY(%s)
            """,
            (normalized,),
        )
        rows = cur.fetchall()

    grouped: Dict[str, List[Tuple[str, str, Decimal, str]]] = defaultdict(list)
    for s_code, c_code, t_code, grade, status in rows:
        grouped[s_code].append((c_code, t_code, grade, status))

    return [
        _build_student_summary(code, grouped.get(code, []), credits_map)
        for code in normalized
    ]


def _consolidate_m3(
    conn: PGConnection, student_codes: List[str]
) -> List[Dict[str, Any]]:
    """
    M3 (OE3 - Cache en memoria):
    - Misma consulta sargable indexada de M2.
    - Reutiliza el catalogo estatico de cursos desde cache en memoria (TTL 300s).
    """
    normalized = sorted({c.strip().upper() for c in student_codes})
    catalog = _course_cache.get_or_load(conn)
    credits_map = {code: meta[1] for code, meta in catalog.items()}

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT student_code, course_code, term_code, grade, status
            FROM enrollments
            WHERE student_code = ANY(%s)
            """,
            (normalized,),
        )
        rows = cur.fetchall()

    grouped: Dict[str, List[Tuple[str, str, Decimal, str]]] = defaultdict(list)
    for s_code, c_code, t_code, grade, status in rows:
        grouped[s_code].append((c_code, t_code, grade, status))

    return [
        _build_student_summary(code, grouped.get(code, []), credits_map)
        for code in normalized
    ]


def consolidate_records(
    conn: PGConnection, student_codes: List[str], stage: str
) -> List[Dict[str, Any]]:
    unique_codes = sorted({c.strip().upper() for c in student_codes if c.strip()})
    if stage == "m0":
        return _consolidate_m0(conn, unique_codes)
    if stage == "m1":
        return _consolidate_m1(conn, unique_codes)
    if stage == "m2":
        return _consolidate_m2(conn, unique_codes)
    if stage == "m3":
        return _consolidate_m3(conn, unique_codes)
    raise ValueError(f"Etapa desconocida: {stage}")
