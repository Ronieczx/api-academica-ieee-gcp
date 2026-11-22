"""
Generador deterministico del catalogo academico de prueba:
- 500 cursos (CUR001..CUR500)
- 20 000 estudiantes (STU00001..STU20000) x 10 matriculas = 200 000 registros
Semilla fija (SEED=2026) para garantizar reproducibilidad exacta en Cloud SQL y CI.
"""
import hashlib
import os
import random
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

SEED = 2026
NUM_COURSES = 500
NUM_STUDENTS = 20_000
ENROLLMENTS_PER_STUDENT = 10
TERMS = ["2022-I", "2022-II", "2023-I", "2023-II", "2024-I", "2024-II", "2025-I", "2025-II", "2026-I", "2026-II"]
DEPARTMENTS = ["Sistemas", "Matematicas", "Administracion", "Fisica", "Economia"]


def seed_database(
    database_url: str,
    num_students: int = NUM_STUDENTS,
    enrollments_per_student: int = ENROLLMENTS_PER_STUDENT,
) -> str:
    rng = random.Random(SEED)
    schema_path = Path(__file__).resolve().parents[1] / "db" / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)

            courses = []
            for idx in range(1, NUM_COURSES + 1):
                code = f"CUR{idx:03d}"
                name = f"Asignatura Academica {idx:03d}"
                credits = rng.choice([2, 3, 4, 5])
                dept = DEPARTMENTS[idx % len(DEPARTMENTS)]
                year = 2019 + (idx % 6)
                courses.append((code, name, credits, dept, year))

            execute_values(
                cur,
                "INSERT INTO courses (course_code, course_name, credits, department, curriculum_year) VALUES %s",
                courses,
                page_size=500,
            )

            course_codes = [c[0] for c in courses]
            batch = []
            batch_size = 5000
            for s_idx in range(1, num_students + 1):
                s_code = f"STU{s_idx:05d}"
                chosen_courses = rng.sample(course_codes, enrollments_per_student)
                for pos, c_code in enumerate(chosen_courses):
                    term = TERMS[pos % len(TERMS)]
                    grade = round(rng.uniform(7.0, 20.0), 2)
                    status = "APPROVED" if grade >= 10.5 else "FAILED"
                    batch.append((s_code, c_code, term, grade, status))
                    if len(batch) >= batch_size:
                        execute_values(
                            cur,
                            "INSERT INTO enrollments (student_code, course_code, term_code, grade, status) VALUES %s",
                            batch,
                            page_size=batch_size,
                        )
                        batch.clear()

            if batch:
                execute_values(
                    cur,
                    "INSERT INTO enrollments (student_code, course_code, term_code, grade, status) VALUES %s",
                    batch,
                    page_size=batch_size,
                )

            cur.execute("ANALYZE courses;")
            cur.execute("ANALYZE enrollments;")

            cur.execute("SELECT COUNT(*), ROUND(AVG(grade)::numeric, 4) FROM enrollments;")
            total_rows, avg_grade = cur.fetchone()
            digest = hashlib.sha256(f"{total_rows}:{avg_grade}:{SEED}".encode()).hexdigest()[:16]
        conn.commit()
        print(
            f"[OK] Base poblada: {NUM_COURSES} cursos, {total_rows} matriculas "
            f"(promedio={avg_grade}, checksum={digest})"
        )
        return digest
    finally:
        conn.close()


if __name__ == "__main__":
    db_url = os.environ["DATABASE_URL"]
    n_students = int(os.getenv("SEED_STUDENTS", str(NUM_STUDENTS)))
    seed_database(db_url, num_students=n_students)
