/**
 * Gemini as a satellite analyst: it looks at the region's VIIRS night lights before and after the storm (two images
 * rendered by the geo build on one brightness scale) and says where the lights went out, next to where ShadowCast
 * expected outages. Read once per scenario and cached in Firestore.
 */
import { generateText, Output } from "ai";

import { type Evidence, evidenceSchema } from "@/lib/evidence";
import type { ScenarioDetail } from "@/lib/types";
import { geoFetch, geoResponse } from "@/server/geo";
import { cachedReading, GEMINI_MODEL, vertex } from "@/server/google";

const IMAGES = ["night-lights-pre", "night-lights-post"] as const;
const DISTRICTS_LISTED = 25;

async function read(scenarioId: string): Promise<Evidence> {
  const scenario = await geoFetch<ScenarioDetail>(`/scenarios/${scenarioId}`);
  const [before, after] = await Promise.all(
    IMAGES.map(async (name) => {
      const image = await geoResponse(`/scenarios/${scenarioId}/evidence/${name}.png`);
      return new Uint8Array(await image.arrayBuffer());
    }),
  );
  const [south, west, north, east] = scenario.region.bbox;
  const districts = scenario.insurance.districts
    .slice(0, DISTRICTS_LISTED)
    .map((d) => `${d.district} (${d.lat.toFixed(2)}N ${d.lon.toFixed(2)}E): wind index ${Math.round(d.index_kt)} kt`)
    .join("; ");
  const prompt =
    `Two NASA VIIRS night-light images of the ${scenario.region.name}, India: the first is the median of the nights ` +
    `before Cyclone ${scenario.storm} (${scenario.season}), the second the nights just after landfall. Both are ` +
    `north-up, span ${south}-${north}N and ${west}-${east}E, and use the same brightness scale (dark = no light). ` +
    `Districts in view, with their centres and ShadowCast's modelled wind index (the higher, the more outages ` +
    `expected; 64 kt and above means hurricane force): ${districts}. Compare the two images and report only what is ` +
    `visible: where lights went out and how badly, what stayed lit, and whether that matches the high-index ` +
    `districts. Use the listed district names to say where; do not invent towns.`;

  const { output } = await generateText({
    model: vertex(GEMINI_MODEL),
    output: Output.object({ schema: evidenceSchema }),
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "Before the storm:" },
          { type: "file", mediaType: "image/png", data: before },
          { type: "text", text: "After landfall:" },
          { type: "file", mediaType: "image/png", data: after },
          { type: "text", text: prompt },
        ],
      },
    ],
    maxRetries: 3,
    abortSignal: AbortSignal.timeout(100_000),
  });
  return { reading: output, readAt: new Date().toISOString(), model: GEMINI_MODEL };
}

/** Gemini's reading of a scenario's before/after night lights, from the cache or read now. */
export function satelliteEvidence(scenarioId: string): Promise<Evidence | null> {
  return cachedReading("evidence", scenarioId, () => read(scenarioId));
}
