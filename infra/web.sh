#!/usr/bin/env bash
# Let the Vercel-hosted console call Gemini (Vertex AI) and Firestore without any service-account key:
# Workload Identity Federation trusts Vercel's OIDC tokens for one Vercel project, which may impersonate a
# least-privilege service account. Idempotent. Prints the environment variables to set on Vercel.
#
# Usage: VERCEL_TEAM=<team-slug> [VERCEL_PROJECT=shadowcast] PROJECT=argmax-cyclone-2026 infra/web.sh
set -euo pipefail

PROJECT="${PROJECT:-argmax-cyclone-2026}"
VERCEL_TEAM="${VERCEL_TEAM:?set VERCEL_TEAM to the Vercel team slug}"
VERCEL_PROJECT="${VERCEL_PROJECT:-shadowcast}"
POOL="vercel"
PROVIDER="vercel"
SA_NAME="shadowcast-web"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
GCLOUD=(gcloud --project "${PROJECT}" --quiet)
NUMBER="$("${GCLOUD[@]}" projects describe "${PROJECT}" --format='value(projectNumber)')"

echo "==> Enabling APIs"
"${GCLOUD[@]}" services enable iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com \
  aiplatform.googleapis.com firestore.googleapis.com

echo "==> Service account ${SA}"
if ! "${GCLOUD[@]}" iam service-accounts describe "${SA}" >/dev/null 2>&1; then
  "${GCLOUD[@]}" iam service-accounts create "${SA_NAME}" --display-name="ShadowCast console (Vercel)"
fi
# Least privilege: call Gemini, and read/write the advisory audit log.
for role in roles/aiplatform.user roles/datastore.user; do
  "${GCLOUD[@]}" projects add-iam-policy-binding "${PROJECT}" --member="serviceAccount:${SA}" --role="${role}" \
    --condition=None >/dev/null
done

echo "==> Workload identity pool ${POOL} and provider ${PROVIDER}"
if ! "${GCLOUD[@]}" iam workload-identity-pools describe "${POOL}" --location=global >/dev/null 2>&1; then
  "${GCLOUD[@]}" iam workload-identity-pools create "${POOL}" --location=global --display-name="Vercel"
fi
if ! "${GCLOUD[@]}" iam workload-identity-pools providers describe "${PROVIDER}" --location=global \
  --workload-identity-pool="${POOL}" >/dev/null 2>&1; then
  "${GCLOUD[@]}" iam workload-identity-pools providers create-oidc "${PROVIDER}" --location=global \
    --workload-identity-pool="${POOL}" --display-name="Vercel ${VERCEL_TEAM}" \
    --issuer-uri="https://oidc.vercel.com/${VERCEL_TEAM}" \
    --allowed-audiences="https://vercel.com/${VERCEL_TEAM}" \
    --attribute-mapping="google.subject=assertion.sub,attribute.project=assertion.project,attribute.environment=assertion.environment" \
    --attribute-condition="assertion.owner == '${VERCEL_TEAM}'"
fi

echo "==> Allowing Vercel project ${VERCEL_PROJECT} to impersonate ${SA}"
"${GCLOUD[@]}" iam service-accounts add-iam-policy-binding "${SA}" --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${NUMBER}/locations/global/workloadIdentityPools/${POOL}/attribute.project/${VERCEL_PROJECT}" \
  >/dev/null

echo "Done. Set on Vercel:"
echo "  GCP_WORKLOAD_IDENTITY_PROVIDER=projects/${NUMBER}/locations/global/workloadIdentityPools/${POOL}/providers/${PROVIDER}"
echo "  GCP_SERVICE_ACCOUNT_EMAIL=${SA}"
