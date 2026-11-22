#!/usr/bin/env bash
set -euo pipefail

# Elimina los recursos en GCP al concluir la campana experimental para evitar costos recurrentes.
PROJECT_ID="${PROJECT_ID:?Define PROJECT_ID antes de ejecutar}"
REGION="${REGION:-southamerica-west1}"
SQL_INSTANCE="${SQL_INSTANCE:-pg-academica-exp}"

gcloud config set project "${PROJECT_ID}"

for STAGE in m0 m1 m2 m3; do
  gcloud run services delete "api-academica-${STAGE}" --region="${REGION}" --quiet || true
done

gcloud run jobs delete seed-academica-db --region="${REGION}" --quiet || true
gcloud sql instances delete "${SQL_INSTANCE}" --quiet || true

echo "[OK] Recursos de experimento eliminados en GCP."
