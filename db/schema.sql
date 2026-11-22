-- Esquema relacional para el experimento de consolidacion de historiales academicos
-- Motor objetivo: PostgreSQL 16 (Cloud SQL / CI)

DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS courses CASCADE;

CREATE TABLE courses (
    course_code VARCHAR(16) PRIMARY KEY,
    course_name VARCHAR(120) NOT NULL,
    credits SMALLINT NOT NULL CHECK (credits BETWEEN 1 AND 8),
    department VARCHAR(60) NOT NULL,
    curriculum_year SMALLINT NOT NULL
);

CREATE TABLE enrollments (
    id BIGSERIAL PRIMARY KEY,
    student_code VARCHAR(16) NOT NULL,
    course_code VARCHAR(16) NOT NULL REFERENCES courses(course_code),
    term_code VARCHAR(10) NOT NULL,
    grade NUMERIC(4, 2) NOT NULL CHECK (grade BETWEEN 0.00 AND 20.00),
    status VARCHAR(12) NOT NULL CHECK (status IN ('APPROVED', 'FAILED'))
);

-- Indice compuesto utilizado en M2 y M3 (predicado sargable: student_code = ANY(%s)).
-- En M0 y M1 el predicado no sargable UPPER(student_code) impide su uso y fuerza Seq Scan.
CREATE INDEX idx_enrollments_student_term
    ON enrollments (student_code, term_code);
