/**
 * What Gemini sees when it compares the satellite night lights before and after a storm: which places went dark and
 * whether that matches ShadowCast's forecast. The schema is Gemini's structured-output contract.
 */
import { z } from "zod";

export const evidenceSchema = z.object({
  summary: z.string().max(500).describe("Two or three plain sentences on what changed between the two images"),
  darkened: z
    .array(
      z.object({
        place: z.string().max(80).describe("Nearest listed district, or a direction and distance from one"),
        severity: z.enum(["total", "partial", "slight"]),
        note: z.string().max(200),
      }),
    )
    .max(10)
    .describe("Areas visibly darker after the storm, most severe first"),
  stillLit: z.array(z.string().max(80)).max(8).describe("Places that stayed lit"),
  agreement: z
    .enum(["agrees", "partly agrees", "disagrees"])
    .describe("How the darkening matches the districts ShadowCast expected to lose power"),
  caveats: z.array(z.string().max(160)).max(4).describe("What the images cannot show (clouds, moonlight, scale)"),
});

export type EvidenceReading = z.infer<typeof evidenceSchema>;

export interface Evidence {
  reading: EvidenceReading;
  readAt: string;
  model: string;
}
