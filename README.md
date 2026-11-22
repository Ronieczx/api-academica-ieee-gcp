# Evaluacion Incremental de Optimizacion por Capas en una API REST Python sobre Google Cloud Platform

Repositorio oficial de codigo, infraestructura, pruebas automatizadas, scripts de carga y evidencia experimental para el articulo en formato IEEE del **Diplomado en Metodologia Cientifica en Ingenieria de Sistemas**.

- **Autor:** Roni Echavarria Coronado (Universidad Nacional Jose Maria Arguedas — UNAJMA)
- **Entorno Cloud:** Google Cloud Run (`min=1, max=1, 1 vCPU, 512 MiB, --no-cpu-throttling`) + Cloud SQL PostgreSQL 16 (`southamerica-west1`)
- **Umbral operativo predeclarado:** `p95 <= 1000 ms` (1,0 s) para lotes de 10, 50, 200 y 500 registros sobre un historial de 200 000 matriculas.

## Etapas experimentales (mismo commit, unica variable `ENGINE_STAGE`)
| Etapa | Intervencion activa | Objetivo especifico |
| :--- | :--- | :--- |
| `m0` | Linea base: consulta N+1 + predicado no sargable `UPPER(student_code)` + busqueda lineal | OE1 |
| `m1` | Capa de aplicacion: consulta agrupada (`ANY`) + tabla hash en Python | OE2 |
| `m2` | Capa de persistencia: predicado sargable `student_code = ANY(%s)` + indice compuesto | OE3 |
| `m3` | Capa de aplicacion/datos: M2 + cache en memoria (TTL 300 s) del catalogo de cursos | OE3 |

## Flujo de ejecucion 100 % en la nube (sin instalar PostgreSQL en local)

### 1. Subir el repositorio a GitHub y verificar CI en verde
```bash
git init -b main
git add .
git commit -m "feat: estructura inicial API, pruebas, IaC GCP y pipeline CI/CD"
git remote add origin https://github.com/<TU_USUARIO>/<TU_REPOSITORIO>.git
git push -u origin main
```
En la pestana **Actions** de GitHub, el flujo `ci` levanta PostgreSQL 16 en la nube, verifica que no existan `__pycache__`, ejecuta `pytest` y comprueba la equivalencia funcional exacta (`M0 == M1 == M2 == M3`).

### 2. Desplegar en Google Cloud (desde Cloud Shell en el navegador)
Abre **Google Cloud Shell** en [console.cloud.google.com](https://console.cloud.google.com), clona tu repositorio y ejecuta:
```bash
git clone https://github.com/<TU_USUARIO>/<TU_REPOSITORIO>.git
cd <TU_REPOSITORIO>
export PROJECT_ID="tu-proyecto-gcp"
export DB_PASS="UnaClaveSeguraParaExp2026"
chmod +x infra/deploy_gcp.sh infra/teardown_gcp.sh
./infra/deploy_gcp.sh
```
El script compila una unica imagen Docker etiquetada con el SHA del commit, crea Cloud SQL PostgreSQL 16, ejecuta el *Cloud Run Job* deterministico de 200 000 filas e imprime las 4 URLs (`url_m0` a `url_m3`) junto con el SHA del commit.

### 3. Ejecutar las 480 mediciones reales desde GitHub Actions
1. Ve a **GitHub -> Actions -> benchmark-gcp -> Run workflow**.
2. Pega las 4 URLs (`url_m0`..`url_m3`) y el `expected_commit` impreso en el paso anterior.
3. El flujo ejecuta primero los *smoke tests*, corre `k6` (35 iteraciones = 5 calentamiento + 30 medidas por cada tamano y etapa), ejecuta `scripts/analyze_results.py` y publica el artefacto `evidencia-experimental-<commit>`.

### 4. Guardar los datos crudos reales y limpiar GCP
1. Descarga el artefacto desde GitHub Actions, copia los 16 archivos `raw_*.csv` en `datos/` y subelos al repositorio (`git add datos/ && git commit -m "data: CSV crudos reales de campana GCP" && git push`).
2. Ejecuta `./infra/teardown_gcp.sh` en Google Cloud Shell para eliminar Cloud SQL y Cloud Run y evitar cargos adicionales.
