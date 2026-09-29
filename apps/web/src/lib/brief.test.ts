import { describe, expect, it } from "vitest";

import { dutyBrief } from "./brief";
import type { Asset, ForecastAsset } from "./types";

const LANDFALL = "2019-05-03T03:30:00Z";
const at = (iso: string) => Date.parse(iso);

function asset(
  rank: number,
  kind: string,
  galeArrival: string | null,
  pOutage = 0.9,
  name: string | null = `Site ${rank}`,
) {
  return { asset_id: `osm:node/${rank}`, rank, kind, name, gale_arrival: galeArrival, p_outage: pOutage } as Asset;
}

const assets = [
  asset(1, "cyclone_shelter", "2019-05-02T11:00:00Z", 0.99, null),
  asset(2, "cyclone_shelter", "2019-05-02T11:00:00Z"),
  asset(3, "hospital", "2019-05-02T15:00:00Z"),
  asset(4, "substation", "2019-05-02T20:00:00Z"),
  asset(5, "water_works", null, 0.9, null), // unnamed and never reached by gales
  asset(6, "school", "2019-05-02T09:00:00Z", 0.2), // not likely: excluded everywhere
];
const fani = { storm: "Fani", region: "Odisha coast", landfall: LANDFALL };

describe("dutyBrief", () => {
  it("summarises the situation and orders actions by the time gales reach each agency's first site", () => {
    const brief = dutyBrief({ ...fani, assets, timeMs: at("2019-05-02T13:00:00Z") });

    expect(brief.summary).toBe(
      "Fani is 15 h from landfall on the Odisha coast. 5 sites are likely to lose power; gales have reached 2 of them.",
    );
    expect(brief).toMatchObject({ hazard: "lose power", likely: 5, reached: 2 });
    expect(brief.next).toEqual({ assetId: "osm:node/3", name: "Site 3", hours: 2 });
    expect(brief.actions.map((a) => [a.agency, a.sites, a.leadName, a.late, a.hours])).toEqual([
      ["Health", 1, "Site 3", false, 2],
      ["Power utility", 1, "Site 4", false, 7],
      ["District administration", 2, "Site 2", true, 2], // led by the highest-priority named shelter
      ["Water supply", 1, "Unnamed water works", false, null],
    ]);
    expect(brief.actions[0].deadline).toBe("2019-05-02T15:00:00.000Z");
  });

  it("puts the most recently overtaken action first among late ones", () => {
    const brief = dutyBrief({ ...fani, assets, timeMs: at("2019-05-02T21:00:00Z") });

    expect(brief.actions.map((a) => a.agency)).toEqual([
      "Power utility",
      "Health",
      "District administration",
      "Water supply",
    ]);
    expect(brief.next).toBeNull();
  });

  it.each([
    ["2019-05-03T04:00:00Z", "Fani is making landfall on the Odisha coast."],
    ["2019-05-03T09:30:00Z", "Fani made landfall on the Odisha coast 6 h ago."],
  ])("describes the storm at %s", (time, sentence) => {
    expect(dutyBrief({ ...fani, assets, timeMs: at(time) }).summary.startsWith(sentence)).toBe(true);
  });

  it("uses ensemble gale agreement in a forecast replay", () => {
    const forecast = [
      { ...asset(1, "hospital", "2024-10-24T06:00:00Z", 0), p34: 0.94 } as ForecastAsset,
      { ...asset(2, "hospital", "2024-10-24T06:00:00Z", 0), p34: 0.3 } as ForecastAsset,
    ];

    const brief = dutyBrief({
      assets: forecast,
      timeMs: at("2024-10-22T00:00:00Z"),
      storm: "Dana",
      region: "Odisha coast",
      landfall: "2024-10-24T20:00:00Z",
    });

    expect(brief.summary).toBe(
      "Dana is 68 h from landfall on the Odisha coast. 1 site is likely to get gales; gales have reached 0 of them.",
    );
    expect(brief.actions).toHaveLength(1);
  });

  it("adds an evacuation action for sites the surge will flood, first when it is due soonest", () => {
    const surged = [
      { ...asset(7, "cyclone_shelter", "2019-05-02T14:00:00Z", 0.1, "Low shelter"), flood_m: 0.8 },
      { ...asset(8, "substation", "2019-05-02T14:00:00Z", 0.1), flood_m: 1.2 }, // floods, but not a people site
      { ...asset(9, "hospital", null, 0.1), flood_m: 0 },
    ];

    const brief = dutyBrief({ ...fani, assets: surged, timeMs: at("2019-05-02T13:00:00Z") });

    expect(brief.flooded).toBe(2);
    expect(brief.summary.endsWith("The storm surge could flood 2 sites.")).toBe(true);
    expect(brief.actions).toEqual([
      expect.objectContaining({ agency: "Evacuation", sites: 1, leadName: "Low shelter", hours: 1 }),
    ]);
    const one = dutyBrief({ ...fani, assets: surged.slice(0, 1), timeMs: at("2019-05-02T13:00:00Z") });
    expect(one.summary.endsWith("The storm surge could flood 1 site.")).toBe(true);
    const wet = (n: number) =>
      dutyBrief({
        ...fani,
        assets: surged.slice(0, n).map((a) => ({ ...a, rain_mm: 250 })),
        timeMs: at("2019-05-02T13:00:00Z"),
      });
    expect(wet(1).summary.endsWith("Extremely heavy rain (204.5 mm or more) is modelled at 1 site.")).toBe(true);
    expect(wet(2).summary.endsWith("is modelled at 2 sites.")).toBe(true);
  });

  it("adds a public-works action for the arterial roads that will be cut", () => {
    const road = (name: string | null, ref: string | null, status: string, closes: string | null, km: number) => ({
      type: "Feature" as const,
      geometry: { type: "LineString" as const, coordinates: [] },
      properties: {
        road_id: `osm:way/${km}`,
        name,
        ref,
        highway: "trunk",
        length_km: km,
        peak_wind_kt: 90,
        flood_m: 0,
        rain_mm: 0,
        status,
        causes: [],
        closes_at: closes,
      },
    }); // fmt: skip
    const roads = {
      type: "FeatureCollection" as const,
      features: [
        road("NH-316", null, "cut", "2019-05-02T22:00:00Z", 12.4),
        road(null, "SH13", "cut", "2019-05-02T20:00:00Z", 5),
        road(null, null, "cut", null, 3),
        road("Open road", null, "open", null, 40),
      ],
    } as Parameters<typeof dutyBrief>[0]["roads"];

    const brief = dutyBrief({ ...fani, assets: [], timeMs: at("2019-05-02T13:00:00Z"), roads });

    expect(brief.summary.endsWith("About 20 km of arterial road is likely to be cut; SH13 closes first.")).toBe(true);
    expect(brief.actions).toEqual([
      expect.objectContaining({ agency: "Public works", sites: 3, leadId: null, leadName: "SH13", hours: 7 }),
    ]);
    const unnamed = dutyBrief({
      ...fani,
      assets: [],
      timeMs: at("2019-05-02T13:00:00Z"),
      roads: { ...roads!, features: [roads!.features[2]] },
    });
    expect(unnamed.actions[0]).toMatchObject({ leadName: "an unnamed road", deadline: null });
  });

  it("is all clear when no site is likely to be hit", () => {
    const brief = dutyBrief({ ...fani, assets: [assets[5]], timeMs: at("2019-05-02T13:00:00Z") });

    expect(brief.summary.endsWith("No site is likely to lose power: all clear.")).toBe(true);
    expect(brief).toMatchObject({ likely: 0, reached: 0, next: null, flooded: null, actions: [] });
  });
});
