#!/usr/bin/env bash
# Provision what the console's Gemini agent needs: Vertex AI and the Firestore database that holds the
# append-only advisory audit log. Idempotent.
#
# Usage: PROJECT=argmax-cyclone-2026 REGION=asia-south1 infra/agent.sh
set -euo pipefail

PROJECT="${PROJECT:-argmax-cyclone-2026}"
REGION="${REGION:-asia-south1}"
GCLOUD=(gcloud --project "${PROJECT}" --quiet)

echo "==> Enabling APIs"
"${GCLOUD[@]}" services enable aiplatform.googleapis.com firestore.googleapis.com

echo "==> Firestore (default) database in ${REGION}"
if ! "${GCLOUD[@]}" firestore databases describe --database="(default)" >/dev/null 2>&1; then
  "${GCLOUD[@]}" firestore databases create --database="(default)" --location="${REGION}" --type=firestore-native
fi

echo "Done. Audit log collection: advisories"
