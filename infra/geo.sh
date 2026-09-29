#!/usr/bin/env bash
# Deploy the ShadowCast geo API: scenario bucket, read-only service account and Cloud Run service.
# Idempotent. The build writes artifacts straight to the bucket; the service loads them at startup.
#
# Usage: PROJECT=argmax-cyclone-2026 REGION=asia-south1 infra/geo.sh
# Build artifacts with:  cd services/geo && uv run --all-extras python -m shadowcast_geo.build
set -euo pipefail

PROJECT="${PROJECT:-argmax-cyclone-2026}"
REGION="${REGION:-asia-south1}"
BUCKET="${BUCKET:-${PROJECT}-scenarios}"
ARCHIVE_BUCKET="${ARCHIVE_BUCKET:-${PROJECT}-archive}"
SERVICE="${SERVICE:-shadowcast-geo}"
ALLOWED_ORIGINS="${ALLOWED_ORIGINS:-*}"
SA_NAME="shadowcast-geo"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GCLOUD=(gcloud --project "${PROJECT}" --quiet)

echo "==> Enabling APIs"
"${GCLOUD[@]}" services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  storage.googleapis.com iam.googleapis.com

echo "==> Bucket gs://${BUCKET}"
if ! "${GCLOUD[@]}" storage buckets describe "gs://${BUCKET}" >/dev/null 2>&1; then
  "${GCLOUD[@]}" storage buckets create "gs://${BUCKET}" --location="${REGION}" \
    --uniform-bucket-level-access --public-access-prevention
fi

echo "==> Service account ${SA}"
if ! "${GCLOUD[@]}" iam service-accounts describe "${SA}" >/dev/null 2>&1; then
  "${GCLOUD[@]}" iam service-accounts create "${SA_NAME}" --display-name="ShadowCast geo API"
fi
# Least privilege: the API only reads built artifacts and the feed archive (for the live picture).
for bucket in "${BUCKET}" "${ARCHIVE_BUCKET}"; do
  "${GCLOUD[@]}" storage buckets add-iam-policy-binding "gs://${bucket}" \
    --member="serviceAccount:${SA}" --role="roles/storage.objectViewer" >/dev/null
done

echo "==> Cloud Run service ${SERVICE} (${REGION})"
# Public, read-only endpoints serving data derived from public sources; instance count capped to bound cost.
"${GCLOUD[@]}" run deploy "${SERVICE}" \
  --source="${ROOT}/services/geo" \
  --region="${REGION}" \
  --service-account="${SA}" \
  --set-env-vars="^|^GEO_BUCKET=${BUCKET}|GEO_ARCHIVE_BUCKET=${ARCHIVE_BUCKET}|GEO_ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" \
  --allow-unauthenticated --cpu=1 --memory=1Gi --min-instances=0 --max-instances=3 --concurrency=40

URL="$("${GCLOUD[@]}" run services describe "${SERVICE}" --region="${REGION}" --format='value(status.url)')"
echo "Done. API: ${URL}  Docs: ${URL}/docs"
