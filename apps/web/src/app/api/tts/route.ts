import { NextRequest, NextResponse } from "next/server";

// Mapping from internal VAYU-RAKSHA language codes to Sarvam AI target_language_code
const SARVAM_LANGUAGE_MAP: Record<string, string> = {
  or: "od-IN", // Odia
  hi: "hi-IN", // Hindi
  bn: "bn-IN", // Bengali
  te: "te-IN", // Telugu
  ta: "ta-IN", // Tamil
  en: "en-IN", // Indian English
  gu: "gu-IN", // Gujarati
  kn: "kn-IN", // Kannada
  ml: "ml-IN", // Malayalam
  mr: "mr-IN", // Marathi
  pa: "pa-IN", // Punjabi
};

export async function GET() {
  const isConfigured = Boolean(process.env.SARVAM_API_KEY && !process.env.SARVAM_API_KEY.includes("REPLACE_THIS"));
  return NextResponse.json({
    provider: "sarvam_ai",
    configured: isConfigured,
    model: "bulbul:v1",
    supportedLanguages: Object.keys(SARVAM_LANGUAGE_MAP),
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { text, languageCode = "hi", speaker = "meera" } = body;

    if (!text || typeof text !== "string") {
      return NextResponse.json({ error: "Missing or invalid 'text' field" }, { status: 400 });
    }

    const apiKey = process.env.SARVAM_API_KEY;

    if (!apiKey || apiKey.includes("REPLACE_THIS") || apiKey.trim() === "") {
      return NextResponse.json(
        {
          success: false,
          fallbackToBrowser: true,
          error: "SARVAM_API_KEY is not configured yet. Falling back to browser speech synthesis.",
        },
        { status: 200 }
      );
    }

    const targetLang = SARVAM_LANGUAGE_MAP[languageCode] || "hi-IN";

    // Clean text of markdown characters or prompt artifacts before sending to Sarvam TTS
    const cleanText = text
      .replace(/[#*_`~[\]()]/g, "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 500); // Sarvam optimal batch length

    const sarvamRes = await fetch("https://api.sarvam.ai/text-to-speech", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "api-subscription-key": apiKey.trim(),
      },
      body: JSON.stringify({
        inputs: [cleanText],
        target_language_code: targetLang,
        speaker: speaker,
        pitch: 0,
        pace: 1.0,
        loudness: 1.5,
        speech_sample_rate: 22050,
        enable_preprocessing: true,
        model: "bulbul:v1",
      }),
    });

    if (!sarvamRes.ok) {
      const errText = await sarvamRes.text();
      console.warn(`[VAYU-RAKSHA] Sarvam AI API returned ${sarvamRes.status}:`, errText);
      return NextResponse.json(
        {
          success: false,
          fallbackToBrowser: true,
          error: `Sarvam AI API Error (${sarvamRes.status}): ${errText}`,
        },
        { status: 200 }
      );
    }

    const sarvamData = await sarvamRes.json();
    const audioBase64 = sarvamData?.audios?.[0];

    if (!audioBase64) {
      return NextResponse.json(
        {
          success: false,
          fallbackToBrowser: true,
          error: "No audio returned from Sarvam AI TTS service.",
        },
        { status: 200 }
      );
    }

    return NextResponse.json({
      success: true,
      provider: "sarvam_ai",
      model: "bulbul:v1",
      audioBase64,
      targetLanguage: targetLang,
      speaker,
    });
  } catch (error: any) {
    console.error("[VAYU-RAKSHA] TTS route handler exception:", error);
    return NextResponse.json(
      {
        success: false,
        fallbackToBrowser: true,
        error: error?.message || "Internal server error during TTS generation",
      },
      { status: 200 }
    );
  }
}
