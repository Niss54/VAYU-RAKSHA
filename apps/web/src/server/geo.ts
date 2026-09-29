/** Server-side access to the geo API (page rendering and agent tools; the browser goes through the /api/geo rewrite). */

export const GEO_API_URL = process.env.GEO_API_URL ?? "https://shadowcast-geo-489356738785.asia-south1.run.app";

const TIMEOUT_MS = 10_000;

/** GET a geo API path, raising with the status and server message on non-2xx responses or after 10 s. */
export async function geoResponse(path: string): Promise<Response> {
  const response = await fetch(`${GEO_API_URL}${path}`, { cache: "no-store", signal: AbortSignal.timeout(TIMEOUT_MS) });
  if (!response.ok) throw new Error(`geo API ${response.status} for ${path}: ${await response.text()}`);
  return response;
}

/** GET a geo API path as JSON (see {@link geoResponse}). */
export async function geoFetch<T>(path: string): Promise<T> {
  return (await (await geoResponse(path)).json()) as T;
}
