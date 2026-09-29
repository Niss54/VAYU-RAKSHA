/**
 * Live alerts for the replay: what a duty officer would be told at the timeline's current moment. Derived purely from
 * the ranked priority assets (when gales and hurricane-force winds reach them) and the storm's landfall, so every
 * alert carries the model's own numbers.
 */
import { assetName, kindLabel, percent } from "./format";
import type { Asset, ForecastAsset } from "./types";

type Hazard = "gales" | "hurricane";
export type AlertKind = "landfall" | `${Hazard}-${"now" | "soon"}`;

export interface LiveAlert {
  id: string;
  kind: AlertKind;
  /** Moment the alert refers to (ISO), shown as its time stamp. */
  at: string;
  title: string;
  detail: string;
  /** Asset to open when the alert is clicked (the group's highest-priority asset), if any. */
  assetId: string | null;
}

interface AlertInput {
  assets: (Asset | ForecastAsset)[];
  timeMs: number;
  landfall: string;
  storm: string;
  stormVmaxKt: number | null;
  limit?: number;
}

interface Group {
  ms: number;
  hazard: Hazard;
  members: (Asset | ForecastAsset)[];
}

const HOUR_MS = 3_600_000;
const NOW_WINDOW_MS = 3 * HOUR_MS;
const SOON_WINDOW_MS = 24 * HOUR_MS;
const LANDFALL_WINDOW_MS = 2 * HOUR_MS;
const MAX_NOW = 2; // leave room for what is coming next
const PRIORITY_RANKS = 250; // alerts speak for the assets an officer would act on, not every school on the map
const HAZARD_WORDS: Record<Hazard, string> = { gales: "Gales", hurricane: "Hurricane-force winds" };

/**
 * Priority assets reaching gales, or entering the 64-kt wind radius, at the same moment: one group per hazard and
 * moment, members in rank order, groups in time order.
 */
function arrivalGroups(assets: (Asset | ForecastAsset)[]): Group[] {
  const groups = new Map<string, Group>();
  const add = (hazard: Hazard, iso: string, asset: Asset | ForecastAsset) => {
    const ms = Date.parse(iso);
    const group = groups.get(`${hazard}:${ms}`) ?? { ms, hazard, members: [] };
    group.members.push(asset);
    groups.set(`${hazard}:${ms}`, group);
  };
  for (const asset of assets) {
    if (asset.rank > PRIORITY_RANKS) continue;
    if (asset.gale_arrival) add("gales", asset.gale_arrival, asset);
    if (asset.band_kt === 64 && asset.band_entry) add("hurricane", asset.band_entry, asset);
  }
  return [...groups.values()]
    .map((g) => ({ ...g, members: g.members.sort((a, b) => a.rank - b.rank) }))
    .sort((a, b) => a.ms - b.ms);
}

function describe({ ms, hazard, members }: Group, timeMs: number): LiveAlert {
  const lead = members.find((a) => a.name) ?? members[0];
  const name = `${assetName(lead)}${members.length > 1 ? ` + ${members.length - 1} more` : ""}`;
  const now = ms <= timeMs;
  const hours = Math.max(1, Math.round((ms - timeMs) / HOUR_MS));
  return {
    id: `${hazard}:${ms}`,
    kind: `${hazard}-${now ? "now" : "soon"}`,
    at: new Date(ms).toISOString(),
    title: now ? `${HAZARD_WORDS[hazard]} now at ${name}` : `${HAZARD_WORDS[hazard]} reach ${name} in ${hours} h`,
    detail:
      "p34" in lead
        ? `${kindLabel(lead.kind)} · ${percent((lead as ForecastAsset).p34)} of ensemble members agree`
        : `${kindLabel(lead.kind)} · ${percent(lead.p_outage)} chance of losing power`,
    assetId: lead.asset_id,
  };
}

/**
 * Alerts at ``timeMs``: landfall (within two hours of it), then up to two winds that reached priority assets in the
 * last three hours (latest first), then winds due in the next day (soonest first).
 *
 * @returns At most ``limit`` alerts, most urgent first.
 */
export function liveAlerts({ assets, timeMs, landfall, storm, stormVmaxKt, limit = 3 }: AlertInput): LiveAlert[] {
  const alerts: LiveAlert[] = [];
  const landfallMs = Date.parse(landfall);
  if (Math.abs(timeMs - landfallMs) <= LANDFALL_WINDOW_MS) {
    alerts.push({
      id: "landfall",
      kind: "landfall",
      at: landfall,
      title: timeMs < landfallMs ? `${storm} is about to make landfall` : `${storm} is crossing the coast`,
      detail: stormVmaxKt == null ? "Official landfall time" : `Storm intensity ${Math.round(stormVmaxKt)} kt`,
      assetId: null,
    });
  }
  const groups = arrivalGroups(assets);
  const now = groups.filter((g) => g.ms <= timeMs && g.ms > timeMs - NOW_WINDOW_MS).reverse();
  const soon = groups.filter((g) => g.ms > timeMs && g.ms <= timeMs + SOON_WINDOW_MS);
  alerts.push(...[...now.slice(0, MAX_NOW), ...soon].map((g) => describe(g, timeMs)));
  return alerts.slice(0, limit);
}
