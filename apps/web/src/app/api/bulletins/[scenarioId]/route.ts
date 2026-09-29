import { agentContextSchema } from "@/server/agent";
import { officialBulletin } from "@/server/bulletins";

export const maxDuration = 120;

/** Gemini's reading of the scenario's official IMD bulletin (read once from the PDF, then cached). */
export async function GET(_request: Request, ctx: RouteContext<"/api/bulletins/[scenarioId]">) {
  const scenarioId = agentContextSchema.shape.scenarioId.safeParse((await ctx.params).scenarioId);
  if (!scenarioId.success) return Response.json({ error: "unknown scenario" }, { status: 400 });
  const bulletin = await officialBulletin(scenarioId.data);
  if (!bulletin) return Response.json({ error: "no archived IMD bulletin for this storm" }, { status: 404 });
  return Response.json(bulletin, { headers: { "Cache-Control": "public, s-maxage=86400" } });
}
