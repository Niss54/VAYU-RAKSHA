import type { NextRequest } from "next/server";

import { agentContextSchema } from "@/server/agent";
import { listAdvisories } from "@/server/google";

const LIMIT = 5;

/** The latest officer decisions for one scenario, from the append-only audit log (never cached: it changes). */
export async function GET(request: NextRequest) {
  const scenarioId = agentContextSchema.shape.scenarioId.safeParse(request.nextUrl.searchParams.get("scenario"));
  if (!scenarioId.success) return Response.json({ error: "scenario must be a scenario id" }, { status: 400 });
  return Response.json(await listAdvisories(scenarioId.data, LIMIT), { headers: { "Cache-Control": "no-store" } });
}
