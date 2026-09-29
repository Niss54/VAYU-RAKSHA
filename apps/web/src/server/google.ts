/**
 * Google Cloud clients for the server: Gemini on Vertex AI, the Firestore audit log and the cache of bulletin readings.
 * Locally they use Application Default Credentials (gcloud); on Vercel they use Workload Identity Federation, with no
 * service-account key anywhere.
 */
import { Firestore } from "@google-cloud/firestore";
import { createVertex } from "@ai-sdk/google-vertex";
import { getVercelOidcToken } from "@vercel/oidc";
import { type ExternalAccountClientOptions, ExternalAccountClient } from "google-auth-library";

import type { Advisory, AdvisorySummary } from "@/lib/advisory";

const PROJECT = process.env.GOOGLE_CLOUD_PROJECT ?? "argmax-cyclone-2026";
const PROVIDER = process.env.GCP_WORKLOAD_IDENTITY_PROVIDER; // projects/<number>/locations/global/workloadIdentityPools/<pool>/providers/<provider>
const SERVICE_ACCOUNT = process.env.GCP_SERVICE_ACCOUNT_EMAIL;

/** On Vercel: exchange the deployment's OIDC token for short-lived credentials of a least-privilege service account. */
const federated: ExternalAccountClientOptions | undefined =
  PROVIDER && SERVICE_ACCOUNT
    ? {
        type: "external_account",
        audience: `//iam.googleapis.com/${PROVIDER}`,
        subject_token_type: "urn:ietf:params:oauth:token-type:jwt",
        token_url: "https://sts.googleapis.com/v1/token",
        service_account_impersonation_url: `https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${SERVICE_ACCOUNT}:generateAccessToken`,
        subject_token_supplier: { getSubjectToken: () => getVercelOidcToken() },
      }
    : undefined;

export const GEMINI_MODEL = "gemini-3.8-flash";

/** Gemini 3.x models are served only from the global Vertex AI endpoint. */
export const vertex = createVertex({
  project: PROJECT,
  location: "global",
  googleAuthOptions: federated && { credentials: federated },
});

const firestore = new Firestore({
  projectId: PROJECT,
  ...(federated && { authClient: ExternalAccountClient.fromJSON(federated) }),
});
const advisories = firestore.collection("advisories");

const ALREADY_EXISTS = 6; // gRPC status code

/** Write a document once; a concurrent or repeated write of the same id is a no-op (first writer wins). */
async function createOnce(ref: FirebaseFirestore.DocumentReference, data: object): Promise<void> {
  try {
    await ref.create(data);
  } catch (error) {
    if ((error as { code?: number }).code !== ALREADY_EXISTS) throw error;
  }
}

export interface AdvisoryRecord {
  status: AdvisorySummary["status"];
  scenarioId: string;
  /** "best-track" or the forecast key the officer was replaying. */
  replay: string;
  advisory: Advisory;
  capXml: string | null;
  reason: string | null;
  decidedAt: string;
}

/**
 * Append an officer's decision to the audit log, keyed by the tool call it answers. The log is append-only: a
 * decision is written once, and replays of the same conversation (the client resends history) are no-ops.
 */
export async function recordDecision(toolCallId: string, record: AdvisoryRecord): Promise<void> {
  await createOnce(advisories.doc(toolCallId), record);
}

const inflight = new Map<string, Promise<unknown>>();

/**
 * A Gemini reading of a fixed source (an IMD PDF, a pair of satellite images), made once and cached in Firestore.
 * The sources never change, so the first reading is kept; concurrent first requests share one read.
 *
 * @param collection Firestore collection holding this kind of reading.
 * @param id Document id, e.g. the scenario id.
 * @param read Makes the reading; resolves to null when there is nothing to read.
 * @returns The cached or fresh reading, or null.
 */
export function cachedReading<T extends object>(
  collection: "bulletins" | "evidence",
  id: string,
  read: () => Promise<T | null>,
): Promise<T | null> {
  const key = `${collection}/${id}`;
  const pending =
    (inflight.get(key) as Promise<T | null> | undefined) ??
    (async () => {
      const ref = firestore.collection(collection).doc(id);
      const snapshot = await ref.get();
      if (snapshot.exists) return snapshot.data() as T;
      const fresh = await read();
      if (fresh) await createOnce(ref, fresh);
      return fresh;
    })().finally(() => inflight.delete(key));
  inflight.set(key, pending);
  return pending;
}

const SCAN_LIMIT = 100;

/**
 * The latest decisions for one scenario, newest first. Filters on the scenario alone (served by Firestore's automatic
 * single-field index) and sorts the small result here, so no composite index is needed.
 */
export async function listAdvisories(scenarioId: string, limit: number): Promise<AdvisorySummary[]> {
  const snapshot = await advisories.where("scenarioId", "==", scenarioId).limit(SCAN_LIMIT).get();
  return snapshot.docs
    .map((doc) => {
      const record = doc.data() as AdvisoryRecord;
      const info = record.advisory.infos.find((i) => i.language === "en") ?? record.advisory.infos[0];
      return {
        id: doc.id,
        status: record.status,
        replay: record.replay,
        headline: info.headline,
        decidedAt: record.decidedAt,
      };
    })
    .sort((a, b) => b.decidedAt.localeCompare(a.decidedAt))
    .slice(0, limit);
}

/** An audited advisory by id, or null when there is none. */
export async function getAdvisory(id: string): Promise<AdvisoryRecord | null> {
  const snapshot = await advisories.doc(id).get();
  return snapshot.exists ? (snapshot.data() as AdvisoryRecord) : null;
}
