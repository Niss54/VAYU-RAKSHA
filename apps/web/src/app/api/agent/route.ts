import { createAgentUIStreamResponse, RetryError, validateUIMessages } from "ai";
import { z } from "zod";

import type { ScenarioDetail } from "@/lib/types";
import { agentContextSchema, createAgent, type ShadowCastMessage } from "@/server/agent";
import { geoFetch } from "@/server/geo";
import { recordDecision } from "@/server/google";

export const maxDuration = 60;

const bodySchema = agentContextSchema.extend({ messages: z.array(z.unknown()).min(1).max(60) });

/** Stream the duty analyst's reply; officer decisions on advisories arrive as tool-approval responses in `messages`. */
export async function POST(request: Request) {
  const body = bodySchema.safeParse(await request.json().catch(() => null));
  if (!body.success) return Response.json({ error: z.prettifyError(body.error) }, { status: 400 });
  const { messages: rawMessages, ...context } = body.data;

  const scenario = await geoFetch<ScenarioDetail>(`/scenarios/${context.scenarioId}`);
  if (context.forecastKey && !scenario.forecasts.some((f) => f.key === context.forecastKey)) {
    return Response.json({ error: `unknown forecast ${context.forecastKey}` }, { status: 400 });
  }
  const agent = createAgent(scenario, context);
  let messages: ShadowCastMessage[];
  try {
    messages = await validateUIMessages<ShadowCastMessage>({ messages: rawMessages, tools: agent.tools });
  } catch (error) {
    return Response.json({ error: error instanceof Error ? error.message : "invalid messages" }, { status: 400 });
  }

  // Approvals are audited when the tool executes; rejections never reach a tool, so audit them here.
  for (const part of messages.at(-1)?.parts ?? []) {
    if (part.type === "tool-issueAdvisory" && part.state === "approval-responded" && !part.approval.approved) {
      await recordDecision(part.toolCallId, {
        status: "rejected",
        scenarioId: scenario.id,
        replay: context.forecastKey ?? "best-track",
        advisory: part.input,
        capXml: null,
        reason: part.approval.reason ?? null,
        decidedAt: new Date().toISOString(),
      });
    }
  }

  return createAgentUIStreamResponse({
    agent,
    uiMessages: messages,
    onError: (error) =>
      RetryError.isInstance(error) && (error.lastError as { statusCode?: number }).statusCode === 429
        ? "Gemini is busy right now (Vertex AI capacity). Please try again in a minute."
        : "The duty analyst hit an error. Please try again.",
  });
}
