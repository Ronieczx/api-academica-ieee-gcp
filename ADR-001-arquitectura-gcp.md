# ADR-001: Arquitectura de ejecucion experimental en runner de nube para la evaluacion incremental de consolidacion academica

- **Fecha:** 2026-11-22
- **Autor:** Roni Echavarria Coronado (UNAJMA)
- **Estado:** Aceptada

## Contexto
En una API REST en Python sobre un historial academico de 200 000 registros en PostgreSQL 16, la consolidacion sincrona por lote presenta tiempos elevados incluso bajo un unico usuario concurrente, superando el umbral operativo predeclarado de p95 <= 1,0 s (1000 ms). El experimento exige desplegar el sistema en una plataforma en la nube garantizando estricto aislamiento de la variable independiente (etapas M0 a M3), ausencia de costos o bloqueos financieros por cuentas de facturacion bancarias, y reproducibilidad auditable con un solo clic.

## Decision
Adoptar una **arquitectura monolitica modular en FastAPI (Python 3.12)** ejecutada dentro de un entorno controlado en la nube mediante **GitHub Actions (`ubuntu-latest`)** conectado a un servicio de base de datos oficial en contenedor **PostgreSQL 16**.
Las cuatro etapas (M0, M1, M2, M3) se levantan en segundo plano desde el **mismo commit** (`GIT_COMMIT=${{ github.sha }}`) e imagen base idéntica, diferenciandose unicamente por la variable de entorno `ENGINE_STAGE` y escuchando en puertos dedicados (`8000`, `8001`, `8002`, `8003`). Las pruebas de carga (`k6`) y el perfilamiento (`EXPLAIN ANALYZE`) se ejecutan secuencialmente de forma local en el runner (`loopback`), eliminando cualquier variabilidad e inestabilidad de red publica.

## Alternativas evaluadas
1. **Despliegue serverless de pago en Google Cloud Platform (Cloud Run + Cloud SQL)**: descartada para evitar vincular cuentas bancarias, tarjetas de credito y riesgos de cargos no deseados, ademas de evitar la latencia no controlada de red publica hacia endpoints remotos.
2. **Arquitectura de microservicios distribuidos**: descartada porque el problema de degradacion ocurre a nivel de diseno algoritmico y de persistencia con un solo usuario secuencial; partir la logica en microservicios introduciria sobrecostos de serializacion de red y consistencia distribuida como variables confundidas.
3. **Ejecucion en estacion de trabajo local no aislada**: descartada por falta de reproducibilidad externa y variabilidad del sistema operativo de escritorio local.

## Consecuencias
- **A favor:**
  - **Aislamiento total de red externa:** las peticiones HTTP de `k6` transitan sobre el enlace `loopback` del runner en la nube, garantizando que el tiempo medido (`X-Process-Time-Ms` y `tiempo_e2e`) mida con precision el costo de computo e I/O de base de datos sin fluctuaciones de la Internet publica.
  - **Cero costos y cero barreras financieras:** ejecucion 100 % gratuita y accesible para cualquier evaluador sin requerir tarjetas bancarias ni facturacion comercial.
  - **Reproducibilidad auditable con un solo clic:** cualquier investigador puede forquear el repositorio, disparar el flujo `benchmark-cloud` via `workflow_dispatch` y obtener datos identicos y verificables con el mismo commit SHA y semilla deterministica (`SEED=2026`).
  - **Trazabilidad causal estricta:** al compartir exactamente el mismo kernel, CPU y contenedor PostgreSQL 16 sobre la misma maquina virtual de GitHub Actions, cualquier variacion en latencia se atribuye exclusivamente a la intervencion entre etapas (M0 -> M1 -> M2 -> M3).
- **En contra:**
  - **Hardware compartido del runner CI:** el runner `ubuntu-latest` opera sobre entornos virtualizados compartidos de Azure/GitHub, lo que podria generar pequenas fluctuaciones de fondo (mitigado con 5 iteraciones de calentamiento descartadas y 30 repeticiones medidas por condicion, $n=30$, tratadas con estadistica no parametrica).
  - **Sin prueba de elasticidad horizontal:** al evaluarse una sola instancia secuencial (1 VU), no se miden capacidades de escalado horizontal ni concurrencia masiva (declarado formalmente como amenaza a la validez externa en el articulo).
