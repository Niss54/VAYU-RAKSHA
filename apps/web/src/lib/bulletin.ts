/**
 * What Gemini reads out of an official IMD cyclone bulletin (or, where no bulletin is archived, IMD's report). The
 * schema is Gemini's structured-output contract, so every reading is validated before it is cached or shown. IMD stays
 * the authority: ShadowCast only puts the official numbers next to its own.
 */
import { z } from "zod";

const range = z.object({ low: z.number(), high: z.number() });

export const bulletinSchema = z.object({
  title: z.string().max(160).describe("Document title, e.g. 'National Bulletin No. 44'"),
  issued: z.string().max(40).describe("Issue time as ISO 8601 with its offset (IST is +05:30), or the document date"),
  system: z.string().max(120).describe("Storm category and name, e.g. 'Extremely Severe Cyclonic Storm FANI'"),
  position: z
    .object({ lat: z.number(), lon: z.number(), description: z.string().max(200) })
    .nullable()
    .describe("Storm centre at issue time, with the stated distances from coastal towns"),
  windKmh: range.nullable().describe("Maximum sustained wind at landfall (forecast or observed), km/h"),
  gustKmh: z.number().nullable().describe("Gusts at landfall, km/h"),
  landfall: z
    .object({ place: z.string().max(200), time: z.string().max(120) })
    .nullable()
    .describe("Where and when the storm crosses the coast, as stated"),
  surge: z
    .object({ low: z.number(), high: z.number(), areas: z.array(z.string().max(80)).max(12) })
    .nullable()
    .describe("Storm surge above astronomical tide in metres, and the districts it will inundate"),
  rainfall: z.string().max(400).nullable().describe("The heavy-rainfall warning, summarised"),
  damage: z.array(z.string().max(160)).max(8).describe("Damage expected (bulletin) or reported (report)"),
  actions: z.array(z.string().max(160)).max(8).describe("Actions IMD suggests"),
  summary: z.string().max(500).describe("Two plain sentences for a district emergency officer"),
});

export type BulletinReading = z.infer<typeof bulletinSchema>;

/** A reading as the console receives it: the document it came from and when Gemini read it. */
export interface Bulletin {
  reading: BulletinReading;
  kind: "bulletin" | "report";
  source: string;
  readAt: string;
  model: string;
}
