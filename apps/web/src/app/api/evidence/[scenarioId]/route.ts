import { agentContextSchema } from "@/server/agent";
import { satelliteEvidence } from "@/server/evidence";

export const maxDuration = 120;

/** Gemini's reading of the before/after satellite night lights (read once, then cached). */
export async function GET(_request: Request, ctx: RouteContext<"/api/evidence/[scenarioId]">) {
  const scenarioId = agentContextSchema.shape.scenarioId.safeParse((await ctx.params).scenarioId);
  if (!scenarioId.success) return Response.json({ error: "unknown scenario" }, { status: 400 });
  const evidence = await satelliteEvidence(scenarioId.data);
  if (!evidence) return Response.json({ error: "no satellite evidence for this storm" }, { status: 404 });
  return Response.json(evidence, { headers: { "Cache-Control": "public, s-maxage=86400" } });
}
