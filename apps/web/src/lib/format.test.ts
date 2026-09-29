import { describe, expect, it } from "vitest";

import {
  assetName,
  assetValue,
  compactNumber,
  istStamp,
  kindLabel,
  knots,
  leadLabel,
  oklchToRgb,
  percent,
  rgbCss,
  rampColor,
  utcAndIst,
} from "./format";
import type { Asset, ForecastAsset } from "./types";

const asset = { asset_id: "osm:node/1", p_outage: 0.42 } as Asset;
const forecastAsset = { ...asset, p34: 0.8 } as ForecastAsset;

describe("labels and numbers", () => {
  it.each([
    ["cyclone_shelter", "Cyclone shelter"],
    ["new_kind", "new kind"],
  ])("kindLabel(%s)", (kind, expected) => {
    expect(kindLabel(kind)).toBe(expected);
  });

  it("names assets, falling back to their kind", () => {
    expect(assetName({ name: "Puri 132 kV", kind: "substation" })).toBe("Puri 132 kV");
    expect(assetName({ name: null, kind: "health_centre" })).toBe("Unnamed health centre");
  });

  it("formats percent, knots and compact numbers, with a dash for missing values", () => {
    expect(percent(0.4213)).toBe("42%");
    expect(percent(0.4213, 1)).toBe("42.1%");
    expect(percent(null)).toBe("–");
    expect(knots(116.9)).toBe("117 kt");
    expect(knots(Number.NaN)).toBe("–");
    expect(compactNumber(4521)).toBe("4.5K");
    expect(compactNumber(undefined)).toBe("–");
  });
});

describe("time", () => {
  it.each([
    ["2024-10-24T05:15:00Z", "24 Oct 05:15 UTC · 10:45 IST"],
    ["2024-10-24T20:00:00Z", "24 Oct 20:00 UTC · 25 Oct 01:30 IST"],
    [null, "–"],
    ["not a date", "–"],
  ])("utcAndIst(%s)", (iso, expected) => {
    expect(utcAndIst(iso)).toBe(expected);
  });

  it("labels lead time before and after landfall", () => {
    expect(leadLabel("2024-10-23T00:00:00Z", "2024-10-24T20:00:00Z")).toBe("T−44 h");
    expect(leadLabel("2024-10-24T23:00:00Z", "2024-10-24T20:00:00Z")).toBe("T+3 h");
  });
});

describe("colour", () => {
  it("converts OKLCH endpoints to sRGB", () => {
    expect(oklchToRgb(1, 0, 0)).toEqual([255, 255, 255]);
    expect(oklchToRgb(0, 0, 0)).toEqual([0, 0, 0]);
  });

  it("ramps get monotonically lighter, clamp out-of-range input, and turn blue for water", () => {
    const luminance = (p: number) => rampColor(p).reduce((sum, channel) => sum + channel, 0);
    expect(luminance(0.25)).toBeGreaterThan(luminance(0));
    expect(luminance(1)).toBeGreaterThan(luminance(0.75));
    expect(rampColor(-1)).toEqual(rampColor(0));
    expect(rampColor(2)).toEqual(rampColor(1));
    const [red, , blue] = rampColor(1, "flood");
    expect(blue).toBeGreaterThan(red);
  });

  it("renders CSS colours", () => {
    expect(rgbCss([1, 2, 3])).toBe("rgb(1 2 3)");
    expect(rgbCss([1, 2, 3], 0.5)).toBe("rgb(1 2 3 / 0.5)");
  });
});

describe("assetValue", () => {
  it.each([
    ["risk", asset, null, 0.42],
    ["gales", forecastAsset, null, 0.8],
    ["gales", asset, null, 0],
    ["wind", asset, new Map([["osm:node/1", 60]]), 0.5],
    ["wind", asset, new Map([["osm:node/1", 300]]), 1],
    ["wind", asset, null, 0],
    ["flood", { ...asset, flood_m: 1 }, null, 0.5],
    ["flood", asset, null, 0],
    ["rain", { ...asset, rain_mm: 150 }, null, 0.5],
    ["rain", asset, null, 0],
  ] as const)("colorBy=%s", (colorBy, item, wind, expected) => {
    expect(assetValue(item, colorBy, wind)).toBe(expected);
  });
});

describe("istStamp", () => {
  it.each([
    ["2019-05-03T03:15:00Z", "3 May 08:45 IST"],
    ["2024-10-24T20:00:00Z", "25 Oct 01:30 IST"],
    [null, "–"],
    ["not a time", "–"],
  ])("istStamp(%s)", (iso, expected) => {
    expect(istStamp(iso)).toBe(expected);
  });
});
