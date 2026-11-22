# ADR-001: Arquitectura de ejecucion en Google Cloud Platform para la evaluacion incremental de consolidacion academica

- **Fecha:** 2026-11-22
- **Autor:** Roni Echavarria Coronado (UNAJMA)
- **Estado:** Aceptada

## Contexto
En una API REST en Python sobre un historial academico de 200 000 registros en PostgreSQL, la consolidacion sincrona por lote presenta tiempos elevados incluso con un unico usuario concurrente, superando el umbral operativo predeclarado de p95 <= 1,0 s (1000 ms). El experimento exige desplegar el sistema en infraestructura en la nube garantizando aislamiento de la variable independiente (etapas M0 a M3) y reproducibilidad auditable.

## Decision
Adoptar una **arquitectura monolitica modular en FastAPI (Python 3.12)** desplegada en **Google Cloud Run** (`region: southamerica-west1`) con escalado bloqueado (`--min-instances=1 --max-instances=1 --cpu=1 --memory=512Mi --no-cpu-throttling --concurrency=1`), conectada mediante socket privado a una unica instancia de **Cloud SQL for PostgreSQL 16** (`db-custom-2-3840`). Las cuatro etapas (M0, M1, M2, M3) se despliegan desde el mismo commit e imagen Docker inmutable, diferenciandose unicamente por la variable `ENGINE_STAGE`. Las pruebas unitarias, de equivalencia funcional y de carga (`k6`) se ejecutan desde GitHub Actions.

## Alternativas evaluadas
1. **Arquitectura de microservicios en nube** (servicios separados de catalogo y consolidacion): descartada porque el problema ocurre con un solo usuario concurrente; partir la aplicacion introduce latencia de red entre servicios y consistencia distribuida como variables confundidas.
2. **Despliegue en capa gratuita serverless con scale-to-zero**: descartada porque la suspension automatica introduce arranques en frio no deterministicos y limites variables de CPU que contaminan la comparacion entre etapas.

## Consecuencias
- **A favor:**
  - Mantiene fijas la region, el hardware asignado, la version de Python/PostgreSQL, el volcado deterministico de 200 000 filas y el commit ejecutado.
  - Garantiza atribucion causal limpia de la reduccion de latencia a cada etapa (M0 -> M1 -> M2 -> M3).
  - La infraestructura, las pruebas y el script de carga quedan versionados en texto plano en el repositorio publico.
- **En contra:**
  - Al operar sobre infraestructura cloud compartida, persiste exposicion a ruido de vecinos y variabilidad de red entre el runner de GitHub Actions y Cloud Run (mitigado midiendo el cronometro dentro del servidor via `X-Process-Time-Ms` y descartando 5 corridas de calentamiento).
  - Fijar una sola instancia y evaluar carga secuencial de 1 usuario impide medir elasticidad horizontal y capacidad bajo alta concurrencia; los resultados no se generalizan fuera de la configuracion declarada sin replicacion.
