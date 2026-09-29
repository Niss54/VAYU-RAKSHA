/** Formatting, colour and encoding helpers shared by the console's panels and map layers. */

import type { Asset, ForecastAsset } from "./types";

export type Rgb = [number, number, number];

/**
 * What the map and list encode: outage risk, ensemble gale chance, modelled wind at the scrubber time, or modelled
 * surge water or storm rain at the site.
 */
export type ColorBy = "risk" | "gales" | "wind" | "flood" | "rain";

/** Water depth that saturates the flood encoding. */
export const FLOOD_FULL_M = 2;
/** Storm rain that saturates the rain encoding. */
export const RAIN_FULL_MM = 300;
/** Surge height that saturates the coastal surge band. */
export const SURGE_FULL_M = 4;

export const KIND_LABELS: Record<string, string> = {
  hospital: "Hospital",
  cyclone_shelter: "Cyclone shelter",
  health_centre: "Health centre",
  substation: "Substation",
  power_plant: "Power plant",
  clinic: "Clinic",
  water_works: "Water works",
  fire_station: "Fire station",
  police: "Police",
  school: "School",
};

const MS_PER_HOUR = 3_600_000;
const IST_OFFSET_MS = 5.5 * MS_PER_HOUR;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function kindLabel(kind: string): string {
  return KIND_LABELS[kind] ?? kind.replaceAll("_", " ");
}

/** An asset's display name, falling back to its kind for unnamed OSM features ("Unnamed hospital"). */
export function assetName(asset: Pick<Asset, "name" | "kind">): string {
  return asset.name ?? `Unnamed ${kindLabel(asset.kind).toLowerCase()}`;
}

export function percent(value: number | null | undefined, digits = 0): string {
  return value == null || Number.isNaN(value) ? "–" : `${(value * 100).toFixed(digits)}%`;
}

export function knots(value: number | null | undefined): string {
  return value == null || Number.isNaN(value) ? "–" : `${Math.round(value)} kt`;
}

export function compactNumber(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "–";
  return new Intl.NumberFormat("en-IN", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

/** "24 Oct 05:15" for a UTC instant shifted by `offsetMs` (deterministic: no locale or timezone dependence). */
function stamp(ms: number, offsetMs: number): string {
  const d = new Date(ms + offsetMs);
  const hh = String(d.getUTCHours()).padStart(2, "0");
  const mm = String(d.getUTCMinutes()).padStart(2, "0");
  return `${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]} ${hh}:${mm}`;
}

/**
 * Format an ISO instant as UTC and IST, e.g. "24 Oct 05:15 UTC · 10:45 IST". The IST date is repeated only when it
 * differs from the UTC date ("24 Oct 20:00 UTC · 25 Oct 01:30 IST").
 */
export function utcAndIst(iso: string | null | undefined): string {
  if (!iso) return "–";
  const ms = Date.parse(iso);
  if (Number.isNaN(ms)) return "–";
  const utc = stamp(ms, 0);
  const ist = stamp(ms, IST_OFFSET_MS);
  const sameDay = utc.split(" ").slice(0, 2).join(" ") === ist.split(" ").slice(0, 2).join(" ");
  return `${utc} UTC · ${sameDay ? ist.split(" ")[2] : ist} IST`;
}

/** An ISO instant in IST with its date, e.g. "3 May 08:45 IST" (or "–" when missing). */
export function istStamp(iso: string | null | undefined): string {
  const ms = iso ? Date.parse(iso) : Number.NaN;
  return Number.isNaN(ms) ? "–" : `${stamp(ms, IST_OFFSET_MS)} IST`;
}

/** Signed hours from `iso` to `reference`, e.g. "T−15 h" before landfall or "T+3 h" after. */
export function leadLabel(iso: string, reference: string): string {
  const hours = Math.round((Date.parse(reference) - Date.parse(iso)) / MS_PER_HOUR);
  return hours >= 0 ? `T−${hours} h` : `T+${-hours} h`;
}

/** OKLCH → sRGB (0-255), with gamut clipping. */
export function oklchToRgb(l: number, c: number, hueDegrees: number): Rgb {
  const h = (hueDegrees * Math.PI) / 180;
  const a = c * Math.cos(h);
  const b = c * Math.sin(h);
  const l_ = (l + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m_ = (l - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s_ = (l - 0.0894841775 * a - 1.291485548 * b) ** 3;
  const linear = [
    4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
    -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
    -0.0041960863 * l_ - 0.7034186147 * m_ + 1.707614701 * s_,
  ];
  return linear.map((v) => {
    const clipped = Math.min(1, Math.max(0, v));
    const gamma = clipped <= 0.0031308 ? 12.92 * clipped : 1.055 * clipped ** (1 / 2.4) - 0.055;
    return Math.round(gamma * 255);
  }) as Rgb;
}

/**
 * Sequential single-hue ramp on the dark map: low values recede toward the surface (dark, low chroma), high values
 * are bright. Lightness rises monotonically so magnitude reads without relying on hue. Wind and risk share the amber
 * signal; water is blue.
 */
export function rampColor(value: number, colorBy: ColorBy = "risk"): Rgb {
  const t = Math.min(1, Math.max(0, value));
  return oklchToRgb(0.34 + 0.52 * t, 0.03 + 0.15 * t, colorBy === "flood" || colorBy === "rain" ? 245 : 48);
}

export function rgbCss([r, g, b]: Rgb, alpha = 1): string {
  return alpha === 1 ? `rgb(${r} ${g} ${b})` : `rgb(${r} ${g} ${b} / ${alpha})`;
}

/** Value in [0, 1] that drives an asset's colour and size under the chosen encoding. */
export function assetValue(
  asset: Asset | ForecastAsset,
  colorBy: ColorBy,
  windById: ReadonlyMap<string, number> | null,
): number {
  if (colorBy === "gales") return "p34" in asset ? asset.p34 : 0;
  if (colorBy === "wind") return Math.min(1, (windById?.get(asset.asset_id) ?? 0) / 120);
  if (colorBy === "flood") return Math.min(1, (asset.flood_m ?? 0) / FLOOD_FULL_M);
  if (colorBy === "rain") return Math.min(1, (asset.rain_mm ?? 0) / RAIN_FULL_MM);
  return asset.p_outage;
}
