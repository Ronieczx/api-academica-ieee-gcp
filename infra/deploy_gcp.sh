#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Despliegue reproducible en Google Cloud Platform (Cloud Run + Cloud SQL)
# Region: southamerica-west1 (Santiago) - misma region para API y PostgreSQL
# Restricciones de control experimental:
#   - Mismo commit y misma imagen Docker en las 4 etapas (m0, m1, m2, m3)
#   - min-instances=1, max-instances=1 (bloquea autoescalado y evita cold starts)
#   - cpu=1, memory=512Mi, --no-cpu-throttling, concurrency=1
# ==============================================================================

PROJECT_ID="${PROJECT_ID:?Define PROJECT_ID antes de ejecutar}"
REGION="${REGION:-southamerica-west1}"
REPO_NAME="${REPO_NAME:-api-academica-repo}"
SQL_INSTANCE="${SQL_INSTANCE:-pg-academica-exp}"
DB_NAME="${DB_NAME:-academica_db}"
DB_USER="${DB_USER:-exp_user}"
DB_PASS="${DB_PASS:?Define DB_PASS alfanumerico antes de ejecutar (no subir al repo)}"
GIT_COMMIT="$(git rev-parse --short HEAD)"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/api-academica:${GIT_COMMIT}"

echo ">>> [1/6] Configurando proyecto y habilitando APIs de GCP..."
gcloud config set project "${PROJECT_ID}"
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com

echo ">>> [2/6] Creando repositorio en Artifact Registry (si no existe)..."
gcloud artifacts repositories describe "${REPO_NAME}" --location="${REGION}" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Imagenes experimentales API academica IEEE"

echo ">>> [3/6] Construyendo imagen inmutable para commit ${GIT_COMMIT}..."
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions="_IMAGE_URI=${IMAGE_URI},_GIT_COMMIT=${GIT_COMMIT}" .

echo ">>> [4/6] Creando instancia Cloud SQL PostgreSQL 16 (si no existe)..."
if ! gcloud sql instances describe "${SQL_INSTANCE}" >/dev/null 2>&1; then
  gcloud sql instances create "${SQL_INSTANCE}" \
    --database-version=POSTGRES_16 \
    --tier=db-custom-2-3840 \
    --region="${REGION}" \
    --storage-size=10GB \
    --storage-type=SSD
fi

gcloud sql databases describe "${DB_NAME}" --instance="${SQL_INSTANCE}" >/dev/null 2>&1 || \
  gcloud sql databases create "${DB_NAME}" --instance="${SQL_INSTANCE}"

gcloud sql users list --instance="${SQL_INSTANCE}" --format="value(name)" | grep -qx "${DB_USER}" || \
  gcloud sql users create "${DB_USER}" --instance="${SQL_INSTANCE}" --password="${DB_PASS}"

INSTANCE_CONN="$(gcloud sql instances describe "${SQL_INSTANCE}" --format='value(connectionName)')"
DATABASE_URL="postgresql://${DB_USER}:${DB_PASS}@/${DB_NAME}?host=/cloudsql/${INSTANCE_CONN}"

echo ">>> [5/6] Poblando 200 000 registros deterministicos mediante Cloud Run Job..."
gcloud run jobs deploy seed-academica-db \
  --image="${IMAGE_URI}" \
  --region="${REGION}" \
  --set-cloudsql-instances="${INSTANCE_CONN}" \
  --set-env-vars="DATABASE_URL=${DATABASE_URL}" \
  --command="python" \
  --args="scripts/seed_db.py" \
  --memory=1Gi \
  --cpu=1 \
  --task-timeout=15m

gcloud run jobs execute seed-academica-db --region="${REGION}" --wait

echo ">>> [6/6] Desplegando los 4 entornos (M0..M3) desde la MISMA imagen (${GIT_COMMIT})..."
for STAGE in m0 m1 m2 m3; do
  SERVICE="api-academica-${STAGE}"
  gcloud run deploy "${SERVICE}" \
    --image="${IMAGE_URI}" \
    --region="${REGION}" \
    --platform=managed \
    --allow-unauthenticated \
    --add-cloudsql-instances="${INSTANCE_CONN}" \
    --set-env-vars="ENGINE_STAGE=${STAGE},GIT_COMMIT=${GIT_COMMIT},DATABASE_URL=${DATABASE_URL}" \
    --min-instances=1 \
    --max-instances=1 \
    --cpu=1 \
    --memory=512Mi \
    --concurrency=1 \
    --no-cpu-throttling \
    --timeout=300
done

echo ""
echo "======================================================================"
echo "DESPLIEGUE COMPLETADO - COMMIT: ${GIT_COMMIT}"
for STAGE in m0 m1 m2 m3; do
  URL="$(gcloud run services describe "api-academica-${STAGE}" --region="${REGION}" --format='value(status.url)')"
  echo "  url_${STAGE}: ${URL}"
done
echo "======================================================================"
