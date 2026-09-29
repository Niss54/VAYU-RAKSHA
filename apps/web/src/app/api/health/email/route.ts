import { NextRequest, NextResponse } from "next/server";
import { sendTestEmail, getSenderConfig } from "@/lib/email";

export const dynamic = "force-dynamic";

/**
 * GET /api/health/email
 * Diagnostic endpoint to verify Resend configuration status safely
 * (never exposes API keys or secrets).
 */
export async function GET() {
  const hasApiKey = Boolean(
    process.env.RESEND_API_KEY &&
      process.env.RESEND_API_KEY !== "[REPLACE_THIS]" &&
      process.env.RESEND_API_KEY.trim().length > 0
  );

  let senderInfo = { from: "Not configured", replyTo: "Not configured" };
  let error: string | null = null;

  try {
    const config = getSenderConfig();
    senderInfo = {
      from: config.from,
      replyTo: config.replyTo || "Default",
    };
  } catch (err: unknown) {
    error = (err as Error).message;
  }

  return NextResponse.json({
    status: hasApiKey && !error ? "configured" : "incomplete_configuration",
    provider: "Resend",
    hasApiKey,
    sender: senderInfo,
    error,
    timestamp: new Date().toISOString(),
  });
}

/**
 * POST /api/health/email
 * Send a verification / test email to a given address.
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const to = body.to || process.env.EMAIL_REPLY_TO || "onboarding@resend.dev";

    if (!to || typeof to !== "string" || !to.includes("@")) {
      return NextResponse.json(
        { success: false, error: "Valid recipient 'to' email address is required." },
        { status: 400 }
      );
    }

    const result = await sendTestEmail(to);

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          error: result.error,
          message: "Failed to send test email via Resend. Check API key and recipient permissions.",
        },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      messageId: result.messageId,
      recipient: to,
      message: "Test email dispatched successfully through Resend.",
    });
  } catch (err: unknown) {
    const error = err as Error;
    return NextResponse.json(
      {
        success: false,
        error: error.message || "Unexpected failure while attempting to send test email.",
      },
      { status: 500 }
    );
  }
}
