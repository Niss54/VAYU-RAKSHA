import { generateSpeech } from "ai";
import type { NextRequest } from "next/server";

import { getAdvisory, vertex } from "@/server/google";

export const maxDuration = 60;

const TTS_MODEL = "gemini-2.5-flash-tts";
const ADVISORY_ID = /^[\w-]{1,100}$/;

/**
 * Speak one language of an issued advisory with Gemini-TTS (Cloud Text-to-Speech has no Odia voice). Only audited,
 * approved advisories can be spoken, and they never change, so the audio is cached indefinitely.
 */
export async function GET(request: NextRequest, ctx: RouteContext<"/api/advisories/[id]/audio">) {
  const { id } = await ctx.params;
  const language = request.nextUrl.searchParams.get("lang");
  const record = ADVISORY_ID.test(id) ? await getAdvisory(id) : null;
  const info = record?.status === "issued" ? record.advisory.infos.find((i) => i.language === language) : undefined;
  if (!info) return new Response("No issued advisory in that language", { status: 404 });

  const { audio } = await generateSpeech({
    model: vertex.speech(TTS_MODEL),
    text: `${info.headline}. ${info.description} ${info.instruction}`,
    voice: "Kore",
    instructions:
      "Read this cyclone advisory calmly and clearly, at a measured pace, like a public safety announcement.",
    abortSignal: AbortSignal.timeout(50_000),
  });
  return new Response(Buffer.from(audio.uint8Array), {
    headers: { "Content-Type": audio.mediaType, "Cache-Control": "public, max-age=31536000, immutable" },
  });
}
