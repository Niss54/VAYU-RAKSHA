import { describe, expect, it } from "vitest";

import { liveAlerts } from "./alerts";
import type { Asset, ForecastAsset } from "./types";

const LANDFALL = "2019-05-03T03:30:00Z";
const at = (iso: string) => Date.parse(iso);

function asset(rank: number, galeArrival: string | null, name: string | null = `Asset ${rank}`, band = 34): Asset {
  return {
    asset_id: `osm:node/${rank}`,
    rank,
    kind: "hospital",
    name,
    gale_arrival: galeArrival,
    band_kt: band,
    band_entry: band === 64 ? "2019-05-03T02:00:00Z" : null,
    p_outage: 0.9,
  } as Asset;
}

const assets = [
  asset(3, "2019-05-02T12:00:00Z"),
  asset(1, "2019-05-02T12:00:00Z", null),
  asset(2, "2019-05-02T12:00:00Z"),
  asset(4, "2019-05-02T18:00:00Z"),
  asset(5, "2019-05-01T00:00:00Z"),
  asset(6, null),
  asset(900, "2019-05-02T12:00:00Z", "Low-priority school"),
];

describe("liveAlerts", () => {
  it("groups priority assets reaching gales together, under the highest-priority named asset", () => {
    const [alert] = liveAlerts({
      assets,
      timeMs: at("2019-05-02T13:00:00Z"),
      landfall: LANDFALL,
      storm: "Fani",
      stormVmaxKt: 110,
    });

    expect(alert).toMatchObject({
      kind: "gales-now",
      title: "Gales now at Asset 2 + 2 more", // the rank-900 school is not a priority asset
      assetId: "osm:node/2",
      detail: "Hospital · 90% chance of losing power",
      at: "2019-05-02T12:00:00.000Z",
    });
  });

  it("lists upcoming winds soonest first, with hours to go", () => {
    const alerts = liveAlerts({
      assets,
      timeMs: at("2019-05-02T09:00:00Z"),
      landfall: LANDFALL,
      storm: "Fani",
      stormVmaxKt: null,
    });

    expect(alerts.map((a) => a.title)).toEqual(["Gales reach Asset 2 + 2 more in 3 h", "Gales reach Asset 4 in 9 h"]);
  });

  it("alerts when priority assets enter the hurricane-force radius", () => {
    const alerts = liveAlerts({
      assets: [asset(7, null, "Puri 132 kV", 64)],
      timeMs: at("2019-05-02T20:00:00Z"),
      landfall: LANDFALL,
      storm: "Fani",
      stormVmaxKt: null,
    });

    expect(alerts).toEqual([
      expect.objectContaining({ kind: "hurricane-soon", title: "Hurricane-force winds reach Puri 132 kV in 6 h" }),
    ]);
  });

  it("leads with landfall near the landfall time, and respects the limit", () => {
    const before = liveAlerts({
      assets,
      timeMs: at("2019-05-03T02:00:00Z"),
      landfall: LANDFALL,
      storm: "Fani",
      stormVmaxKt: 115.4,
      limit: 1,
    });
    const after = liveAlerts({
      assets: [],
      timeMs: at("2019-05-03T04:00:00Z"),
      landfall: LANDFALL,
      storm: "Fani",
      stormVmaxKt: null,
    });

    expect(before).toEqual([
      expect.objectContaining({
        kind: "landfall",
        title: "Fani is about to make landfall",
        detail: "Storm intensity 115 kt",
      }),
    ]);
    expect(after).toEqual([
      expect.objectContaining({ title: "Fani is crossing the coast", detail: "Official landfall time" }),
    ]);
  });

  it("describes forecast assets by ensemble agreement and names unnamed ones by kind", () => {
    const forecast = { ...asset(1, "2024-10-24T06:00:00Z", null), p34: 0.94 } as ForecastAsset;

    const [alert] = liveAlerts({
      assets: [forecast],
      timeMs: at("2024-10-24T05:00:00Z"),
      landfall: "2024-10-24T20:00:00Z",
      storm: "Dana",
      stormVmaxKt: null,
    });

    expect(alert.title).toBe("Gales reach Unnamed hospital in 1 h");
    expect(alert.detail).toBe("Hospital · 94% of ensemble members agree");
  });

  it("caps current alerts at two so the next incoming one still shows", () => {
    const busy = [
      asset(1, "2019-05-02T12:00:00Z"),
      asset(2, "2019-05-02T12:15:00Z"),
      asset(3, "2019-05-02T12:30:00Z"),
      asset(4, "2019-05-02T20:00:00Z"),
    ];

    const alerts = liveAlerts({
      assets: busy,
      timeMs: at("2019-05-02T13:00:00Z"),
      landfall: LANDFALL,
      storm: "Fani",
      stormVmaxKt: null,
    });

    expect(alerts.map((a) => a.kind)).toEqual(["gales-now", "gales-now", "gales-soon"]);
  });

  it("is empty when nothing is near", () => {
    expect(
      liveAlerts({ assets, timeMs: at("2019-06-01T00:00:00Z"), landfall: LANDFALL, storm: "Fani", stormVmaxKt: null }),
    ).toEqual([]);
  });
});
