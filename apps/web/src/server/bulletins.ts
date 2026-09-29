/**
 * The official IMD bulletin for each scenario, read by Gemini straight from the PDF (multimodal document input with a
 * validated structured output) and cached in Firestore, so each document is read once.
 */
import { generateText, Output } from "ai";

import { type Bulletin, bulletinSchema } from "@/lib/bulletin";
import { cachedReading, GEMINI_MODEL, vertex } from "@/server/google";

const RSMC = "https://rsmcnewdelhi.imd.gov.in/uploads";

/**
 * The last archived national bulletin before landfall for each storm. IMD's 2014 bulletins are not archived, so
 * Hudhud falls back to IMD's report on the storm.
 */
const SOURCES: Record<string, { kind: Bulletin["kind"]; url: string }> = {
  "fani-2019": {
    kind: "bulletin", // National Bulletin No. 44, 05:30 IST 2 May 2019, via the Internet Archive
    url: "https://web.archive.org/web/20190502010655id_/http://www.rsmcnewdelhi.imd.gov.in/images/bulletin/indian.pdf",
  },
  "amphan-2020": {
    kind: "bulletin",
    url: `${RSMC}/archive/1/1_868561_31.National%20Bulletin%2020200519_1800UTC.pdf`,
  },
  "dana-2024": {
    kind: "bulletin",
    url: `${RSMC}/archive/1/1_4c1a3c_9.National%20Bulletin%20No%209-23Oct2024_1430IST.pdf`,
  },
  "hudhud-2014": { kind: "report", url: `${RSMC}/report/26/26_fac6af_hud.pdf` },
};

const PROMPT: Record<Bulletin["kind"], string> = {
  bulletin:
    "This is an official India Meteorological Department (IMD) cyclone bulletin. Extract exactly what it states for " +
    "the storm threatening the Indian coast: nothing inferred, nothing added. Give times as ISO 8601 with the +05:30 " +
    "offset when IST is stated. Wind in km/h as stated; storm surge in metres above astronomical tide. Use null for " +
    "anything the bulletin does not state.",
  report:
    "This is the India Meteorological Department report on a past cyclone. Extract what it states about the storm " +
    "at landfall (position, wind, landfall place and time, observed storm surge, rainfall, damage): nothing inferred, " +
    "nothing added. Use the landfall time as the issue time. Use null for anything the report does not state.",
};

async function read(scenarioId: string): Promise<Bulletin | null> {
  const source = SOURCES[scenarioId];
  if (!source) return null;

  const pdf = await fetch(source.url, { signal: AbortSignal.timeout(30_000) });
  if (!pdf.ok) throw new Error(`IMD document unavailable (${pdf.status})`);
  const { output } = await generateText({
    model: vertex(GEMINI_MODEL),
    output: Output.object({ schema: bulletinSchema }),
    messages: [
      {
        role: "user",
        content: [
          { type: "file", mediaType: "application/pdf", data: new Uint8Array(await pdf.arrayBuffer()) },
          { type: "text", text: PROMPT[source.kind] },
        ],
      },
    ],
    maxRetries: 3,
    abortSignal: AbortSignal.timeout(100_000),
  });
  return {
    reading: output,
    kind: source.kind,
    source: source.url,
    readAt: new Date().toISOString(),
    model: GEMINI_MODEL,
  };
}

/**
 * Gemini's reading of a scenario's IMD bulletin, from the cache or read now.
 *
 * @returns The reading, or null when the scenario has no archived IMD document.
 */
export function officialBulletin(scenarioId: string): Promise<Bulletin | null> {
  return cachedReading("bulletins", scenarioId, () => read(scenarioId));
}
