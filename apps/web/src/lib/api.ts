"use client";

/**
 * Data hooks for the geo API and the advisory audit log. Geo requests go through the `/api/geo` rewrite (see
 * next.config.ts), so the browser only talks to this origin and the API location stays server-side configuration.
 */
import useSWR, { type SWRConfiguration } from "swr";

import type { AdvisorySummary } from "./advisory";
import type { Bulletin } from "./bulletin";
import type { Evidence } from "./evidence";
import type {
  Asset,
  AssetDetail,
  Backtest,
  ForecastAsset,
  HazardSnapshot,
  LiveFeed,
  Page,
  ReplayMode,
  RoadCollection,
  ScenarioDetail,
  SurgePoint,
  TrackFeatureCollection,
} from "./types";

export const GEO_PREFIX = "/api/geo";

/** Fetch JSON from this origin, raising with the server's message on non-2xx responses. */
export async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${await response.text()}`);
  }
  return (await response.json()) as T;
}

const STATIC: SWRConfiguration = { revalidateOnFocus: false, revalidateIfStale: false, dedupingInterval: 60_000 };

export function useScenario(id: string) {
  return useSWR<ScenarioDetail>(`${GEO_PREFIX}/scenarios/${id}`, fetchJson, STATIC);
}

export function useTrack(id: string) {
  return useSWR<TrackFeatureCollection>(`${GEO_PREFIX}/scenarios/${id}/track`, fetchJson, STATIC);
}

/** Every asset in rank order for the selected replay (the full list feeds the map; ~250 kB gzipped). */
export function useAssets(id: string, mode: ReplayMode) {
  const path = `${GEO_PREFIX}/scenarios/${id}${mode.kind === "forecast" ? `/forecasts/${mode.key}` : ""}/assets`;
  return useSWR<Page<Asset | ForecastAsset>>(`${path}?limit=5000`, fetchJson, { ...STATIC, keepPreviousData: true });
}

export function useForecastTracks(id: string, mode: ReplayMode) {
  const key = mode.kind === "forecast" ? `${GEO_PREFIX}/scenarios/${id}/forecasts/${mode.key}/tracks` : null;
  return useSWR<TrackFeatureCollection>(key, fetchJson, STATIC);
}

export function useAssetDetail(id: string, assetId: string | null) {
  return useSWR<AssetDetail>(assetId ? `${GEO_PREFIX}/scenarios/${id}/assets/${assetId}` : null, fetchJson, STATIC);
}

/** Peak modelled surge along the open coast; best-track replays only (a forecast must not show hindsight). */
export function useSurge(id: string, mode: ReplayMode) {
  return useSWR<SurgePoint[]>(
    mode.kind === "best-track" ? `${GEO_PREFIX}/scenarios/${id}/surge` : null,
    fetchJson,
    STATIC,
  );
}

/** Arterial roads with their status and closing time; best-track replays only. */
export function useRoads(id: string, mode: ReplayMode) {
  return useSWR<RoadCollection>(
    mode.kind === "best-track" ? `${GEO_PREFIX}/scenarios/${id}/roads` : null,
    fetchJson,
    STATIC,
  );
}

export function useBacktest(id: string) {
  return useSWR<Backtest>(`${GEO_PREFIX}/scenarios/${id}/backtest`, fetchJson, STATIC);
}

/** Wind at every asset at one moment; `at` should be quantised by the caller so scrubbing reuses cached snapshots. */
export function useHazard(id: string, at: string | null) {
  return useSWR<HazardSnapshot>(
    at ? `${GEO_PREFIX}/scenarios/${id}/hazard?at=${encodeURIComponent(at)}` : null,
    fetchJson,
    {
      ...STATIC,
      keepPreviousData: true,
    },
  );
}

/** The latest officer decisions for a scenario; revalidated whenever the brief mounts, so a new decision shows up. */
export function useAdvisories(scenarioId: string) {
  return useSWR<AdvisorySummary[]>(`/api/advisories?scenario=${scenarioId}`, fetchJson);
}

/** Gemini's reading of the scenario's official IMD bulletin; the first request may take a while (Gemini reads the PDF). */
export function useBulletin(scenarioId: string) {
  return useSWR<Bulletin>(`/api/bulletins/${scenarioId}`, fetchJson, { ...STATIC, shouldRetryOnError: false });
}

/** Gemini's reading of the before/after satellite night lights (the first request waits for Gemini). */
export function useEvidence(scenarioId: string) {
  return useSWR<Evidence>(`/api/evidence/${scenarioId}`, fetchJson, { ...STATIC, shouldRetryOnError: false });
}

/** The live picture from the feed archiver's newest run; refreshed every 15 minutes while the console is open. */
export function useLive() {
  return useSWR<LiveFeed>(`${GEO_PREFIX}/live`, fetchJson, { refreshInterval: 15 * 60_000, shouldRetryOnError: false });
}
