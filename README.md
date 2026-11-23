# Evaluacion Incremental de Optimizacion por Capas en una API REST Python en Entorno Cloud Controlado

Repositorio oficial de codigo, infraestructura como codigo, pruebas automatizadas, scripts de carga y evidencia experimental para el articulo en formato IEEE del **Diplomado en Metodologia Cientifica en Ingenieria de Sistemas**.

- **Autor:** Roni Echavarria Coronado (Universidad Nacional Jose Maria Arguedas — UNAJMA)
- **Entorno Cloud:** GitHub Actions Runner (`ubuntu-latest`, Python 3.12) + Servicio Contenedorizado PostgreSQL 16
- **Umbral operativo predeclarado:** `p95 <= 1000 ms` (1,0 s) para lotes de 10, 50, 200 y 500 registros sobre un historial de 200 000 matriculas academicas.

## Etapas experimentales (mismo commit, variable `ENGINE_STAGE`)
| Etapa | Puerto | Intervencion activa | Objetivo especifico |
| :--- | :--- | :--- | :--- |
| `m0` | `:8000` | Linea base: consulta N+1 + predicado no sargable `UPPER(student_code)` + busqueda lineal | OE1 |
| `m1` | `:8001` | Capa de aplicacion: consulta agrupada (`ANY`) + tabla hash en Python (mantiene no sargable) | OE2 |
| `m2` | `:8002` | Capa de persistencia: predicado sargable `student_code = ANY(%s)` + indice compuesto | OE3 |
| `m3` | `:8003` | Capa de datos/aplicacion: M2 + cache en memoria (TTL 300 s) del catalogo de cursos | OE3 |

## Flujo de ejecucion 100 % en la nube (sin costos ni tarjetas)

### 1. Verificacion de CI
En cada `push` o `pull_request`, el flujo `.github/workflows/ci.yml`:
1. Levanta un servicio PostgreSQL 16 en contenedor.
2. Verifica que el repositorio este limpio de archivos temporales `__pycache__`.
3. Instala dependencias exactas (`requirements.txt`).
4. Ejecuta `pytest` comprobando la equivalencia funcional estricta ($M0 \equiv M1 \equiv M2 \equiv M3$).

### 2. Campana de medicion experimental automatizada
El flujo `.github/workflows/benchmark.yml` se dispara mediante `workflow_dispatch` (un clic en la pestana **Actions -> benchmark-cloud -> Run workflow**):
1. Aprovisiona PostgreSQL 16 en la nube de GitHub Actions.
2. Puebla determinísticamente los 500 cursos y 200 000 matrículas con semilla fija (`SEED=2026`).
3. Levanta en segundo plano las 4 etapas (`M0..M3`) desde el mismo commit exacto.
4. Ejecuta los *smoke tests* de validacion de integridad.
5. Captura los planes reales `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` en `datos/explain_plans.json`.
6. Corre la campana de carga secuencial en `k6` (1 VU, 35 iteraciones = 5 calentamiento + 30 medidas por condicion, 16 condiciones = 560 ejecuciones totales, 480 medidas).
7. Ejecuta el analisis estadistico no parametrico (`Mann-Whitney U`, `Delta de Cliff`, `Bootstrap 10 000 remuestreos`) con `scripts/analyze_results.py`.
8. Publica el artefacto descargable `evidencia-experimental-<commit>` conteniendo los 16 CSV crudos, planes de ejecucion y figuras vectoriales.

### 3. Descarga de datos crudos para el articulo
Los datos crudos generados por el runner se incorporan en la carpeta `datos/` y sustentan directamente las tablas V y VI y las figuras del manuscrito cientifico.
