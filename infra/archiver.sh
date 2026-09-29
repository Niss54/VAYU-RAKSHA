#!/usr/bin/env bash
# Deploy the ShadowCast feed archiver: archive bucket, service account, Cloud Run Job and a 6-hourly
# Cloud Scheduler trigger. Idempotent: re-running updates the job image and schedule in place.
#
# Usage: PROJECT=argmax-cyclone-2026 REGION=asia-south1 infra/archiver.sh [--run]
#   --run   execute the job once after deploying and wait for it to finish.
set -euo pipefail

PROJECT="${PROJECT:-argmax-cyclone-2026}"
REGION="${REGION:-asia-south1}"
BUCKET="${BUCKET:-${PROJECT}-archive}"
JOB="${JOB:-shadowcast-archiver}"
SCHEDULE="${SCHEDULE:-15 */6 * * *}"
SA_NAME="shadowcast-archiver"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GCLOUD=(gcloud --project "${PROJECT}" --quiet)

echo "==> Enabling APIs"
"${GCLOUD[@]}" services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com storage.googleapis.com iam.googleapis.com

echo "==> Bucket gs://${BUCKET}"
if ! "${GCLOUD[@]}" storage buckets describe "gs://${BUCKET}" >/dev/null 2>&1; then
  "${GCLOUD[@]}" storage buckets create "gs://${BUCKET}" --location="${REGION}" \
    --uniform-bucket-level-access --public-access-prevention
fi

echo "==> Service account ${SA}"
if ! "${GCLOUD[@]}" iam service-accounts describe "${SA}" >/dev/null 2>&1; then
  "${GCLOUD[@]}" iam service-accounts create "${SA_NAME}" --display-name="ShadowCast feed archiver"
fi
# Least privilege: create new objects in the archive bucket only (runs never overwrite earlier snapshots).
"${GCLOUD[@]}" storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --member="serviceAccount:${SA}" --role="roles/storage.objectCreator" >/dev/null

echo "==> Cloud Run Job ${JOB} (${REGION})"
"${GCLOUD[@]}" run jobs deploy "${JOB}" \
  --source="${ROOT}/services/archiver" \
  --region="${REGION}" \
  --service-account="${SA}" \
  --set-env-vars="ARCHIVE_BUCKET=${BUCKET}" \
  --task-timeout=15m --max-retries=1 --cpu=1 --memory=1Gi
"${GCLOUD[@]}" run jobs add-iam-policy-binding "${JOB}" --region="${REGION}" \
  --member="serviceAccount:${SA}" --role="roles/run.invoker" >/dev/null

echo "==> Cloud Scheduler trigger (${SCHEDULE} UTC)"
TRIGGER="${JOB}-trigger"
SCHEDULER_ARGS=(
  --location="${REGION}" --schedule="${SCHEDULE}" --time-zone="Etc/UTC"
  --uri="https://run.googleapis.com/v2/projects/${PROJECT}/locations/${REGION}/jobs/${JOB}:run"
  --http-method=POST --oauth-service-account-email="${SA}"
  --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform"
)
if "${GCLOUD[@]}" scheduler jobs describe "${TRIGGER}" --location="${REGION}" >/dev/null 2>&1; then
  "${GCLOUD[@]}" scheduler jobs update http "${TRIGGER}" "${SCHEDULER_ARGS[@]}"
else
  "${GCLOUD[@]}" scheduler jobs create http "${TRIGGER}" "${SCHEDULER_ARGS[@]}"
fi

if [[ "${1:-}" == "--run" ]]; then
  echo "==> Executing ${JOB} once"
  "${GCLOUD[@]}" run jobs execute "${JOB}" --region="${REGION}" --wait
fi
echo "Done. Archive: gs://${BUCKET}   Manifests: gs://${BUCKET}/manifests/"
