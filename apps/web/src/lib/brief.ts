/**
 * The duty brief at the timeline's current moment: the situation in a few sentences, the exceptions that need
 * attention, and recommended actions per agency, each due before gales reach the group's first site (crews and
 * generators cannot be moved safely in gales). Sites the modelled storm surge would flood get their own evacuation
 * action. Pure and deterministic: every number comes from the ranked assets, never from Gemini.
 */
import { assetName } from "./format";
import type { Asset, ForecastAsset, RoadCollection } from "./types";

export type Hazard = "lose power" | "get gales";

export interface BriefAction {
  agency: string;
  task: string;
  sites: number;
  /** The group's highest-priority named site, opened when the action is clicked (null for roads). */
  leadId: string | null;
  leadName: string;
  /** When gales first reach one of the group's sites (ISO), or null when they never do. */
  deadline: string | null;
  /** Gales have already reached the group's first site. */
  late: boolean;
  /** Whole hours between now and the deadline (at least 1 while it is ahead), or null without a deadline. */
  hours: number | null;
}

export interface Brief {
  summary: string;
  hazard: Hazard;
  /** Sites at or above the likelihood threshold for the hazard. */
  likely: number;
  /** How many of those gales have already reached. */
  reached: number;
  /** The next likely site gales will reach. */
  next: { assetId: string; name: string; hours: number } | null;
  /** Sites with at least ``FLOOD_M`` of modelled surge water; null without a surge model (forecast replays). */
  flooded: number | null;
  actions: BriefAction[];
}

interface BriefInput {
  /** Assets in rank order, from either replay. */
  assets: (Asset | ForecastAsset)[];
  timeMs: number;
  storm: string;
  region: string;
  landfall: string;
  /** Arterial roads with their status (best track); omitted in forecast replays. */
  roads?: RoadCollection;
}

const HOUR_MS = 3_600_000;
const LIKELY = 0.5;
const LANDFALL_WINDOW_H = 1;
const FLOOD_M = 0.3; // ankle-deep: enough to stop vehicles and wet equipment
const EXTREME_RAIN_MM = 204.5; // IMD's "extremely heavy" threshold
const PEOPLE_SITES = ["cyclone_shelter", "school", "hospital", "health_centre", "clinic"];
/**
 * Who acts for which kinds of site, and what they do before gales arrive. The first group is chosen by modelled surge
 * water rather than outage likelihood; together the rest cover every asset kind the geo API emits.
 */
const AGENCIES: { agency: string; kinds: string[]; task: string; flood?: true }[] = [
  {
    agency: "Evacuation",
    kinds: PEOPLE_SITES,
    task: "Move people and patients out of sites the surge will flood",
    flood: true,
  },
  {
    agency: "Health",
    kinds: ["hospital", "health_centre", "clinic"],
    task: "Move back-up generators and 72 h of fuel",
  },
  { agency: "Power utility", kinds: ["substation", "power_plant"], task: "Stage line crews and spares nearby" },
  {
    agency: "District administration",
    kinds: ["cyclone_shelter", "school"],
    task: "Open, stock and test back-up power",
  },
  { agency: "Water supply", kinds: ["water_works"], task: "Fill storage and put tankers on standby" },
  { agency: "Police and fire", kinds: ["police", "fire_station"], task: "Pre-position rescue teams and generators" },
];

/** Open actions first (soonest deadline first), then those gales have overtaken (most recent first), then the rest. */
function urgency(action: BriefAction): [number, number] {
  if (action.deadline == null) return [2, 0];
  const ms = Date.parse(action.deadline);
  return action.late ? [1, -ms] : [0, ms];
}

/**
 * Build the brief for ``timeMs``. In a forecast replay "likely" means most ensemble members bring gales; in the best
 * track it means a grid-outage probability of at least 50%.
 *
 * @returns The situation summary, exception counts and recommended actions, most urgent first.
 */
export function dutyBrief({ assets, timeMs, storm, region, landfall, roads }: BriefInput): Brief {
  const hazard: Hazard = assets.some((a) => "p34" in a) ? "get gales" : "lose power";
  const likely = assets.filter((a) => ("p34" in a ? (a as ForecastAsset).p34 : a.p_outage) >= LIKELY);
  const galeMs = (a: Asset) => (a.gale_arrival ? Date.parse(a.gale_arrival) : Number.POSITIVE_INFINITY);
  const hoursTo = (ms: number) => Math.round((ms - timeMs) / HOUR_MS);
  const reached = likely.filter((a) => galeMs(a) <= timeMs).length;
  // Stable sort keeps rank order among sites that gales reach at the same moment.
  const next = likely.filter((a) => a.gale_arrival && galeMs(a) > timeMs).sort((a, b) => galeMs(a) - galeMs(b))[0];

  const surgeModelled = assets.some((a) => a.flood_m != null);
  const flooded = assets.filter((a) => (a.flood_m ?? 0) >= FLOOD_M);

  const action = (
    agency: string,
    task: string,
    sites: number,
    lead: { id: string | null; name: string },
    first: number,
  ): BriefAction => {
    const deadline = Number.isFinite(first) ? new Date(first).toISOString() : null;
    return {
      agency,
      task,
      sites,
      leadId: lead.id,
      leadName: lead.name,
      deadline,
      late: first <= timeMs,
      hours: deadline == null ? null : first <= timeMs ? -hoursTo(first) : Math.max(1, hoursTo(first)),
    };
  };
  const cut = (roads?.features ?? []).filter((f) => f.properties.status === "cut");
  const closeMs = (f: (typeof cut)[number]) =>
    f.properties.closes_at ? Date.parse(f.properties.closes_at) : Number.POSITIVE_INFINITY;
  const firstRoad = [...cut].sort((a, b) => closeMs(a) - closeMs(b))[0];
  const roadName = (f: (typeof cut)[number]) => f.properties.name ?? f.properties.ref ?? "an unnamed road";

  const actions = [
    ...AGENCIES.flatMap(({ agency, kinds, task, flood }): BriefAction[] => {
      const group = (flood ? flooded : likely).filter((a) => kinds.includes(a.kind));
      if (group.length === 0) return [];
      const lead = group.find((a) => a.name) ?? group[0];
      return [
        action(
          agency,
          task,
          group.length,
          { id: lead.asset_id, name: assetName(lead) },
          Math.min(...group.map(galeMs)),
        ),
      ];
    }),
    ...(firstRoad
      ? [
          action(
            "Public works",
            "Stage tree-cutting and earth-moving crews on arterial roads",
            cut.length,
            { id: null, name: roadName(firstRoad) },
            closeMs(firstRoad),
          ),
        ]
      : []),
  ].sort((a, b) => {
    const [groupA, keyA] = urgency(a);
    const [groupB, keyB] = urgency(b);
    return groupA - groupB || keyA - keyB;
  });

  const toLandfall = hoursTo(Date.parse(landfall));
  const when =
    Math.abs(toLandfall) <= LANDFALL_WINDOW_H
      ? `${storm} is making landfall on the ${region}.`
      : toLandfall > 0
        ? `${storm} is ${toLandfall} h from landfall on the ${region}.`
        : `${storm} made landfall on the ${region} ${-toLandfall} h ago.`;
  const count = likely.length.toLocaleString("en-IN");
  const impact =
    likely.length === 0
      ? `No site is likely to ${hazard}: all clear.`
      : `${count} ${likely.length === 1 ? "site is" : "sites are"} likely to ${hazard}; gales have reached ${reached} of them.`;
  const drenched = assets.filter((a) => (a.rain_mm ?? 0) >= EXTREME_RAIN_MM).length;
  const rain =
    drenched > 0
      ? ` Extremely heavy rain (204.5 mm or more) is modelled at ${drenched.toLocaleString("en-IN")} ${drenched === 1 ? "site" : "sites"}.`
      : "";
  const kmCut = Math.round(cut.reduce((sum, f) => sum + f.properties.length_km, 0));
  const roadsLine = firstRoad
    ? ` About ${kmCut.toLocaleString("en-IN")} km of arterial road is likely to be cut; ${roadName(firstRoad)} closes first.`
    : "";
  const surge =
    flooded.length > 0
      ? ` The storm surge could flood ${flooded.length.toLocaleString("en-IN")} ${flooded.length === 1 ? "site" : "sites"}.`
      : "";

  return {
    summary: `${when} ${impact}${surge}${rain}${roadsLine}`,
    hazard,
    likely: likely.length,
    reached,
    next: next ? { assetId: next.asset_id, name: assetName(next), hours: Math.max(1, hoursTo(galeMs(next))) } : null,
    flooded: surgeModelled ? flooded.length : null,
    actions,
  };
}
