import { NextRequest, NextResponse } from "next/server";
import { getDatadogConfig, sendDatadogLog, sendDatadogMetric, sendSystemMetrics } from "@/lib/datadog";

export const dynamic = "force-dynamic";

/**
 * GET /api/health/datadog
 * Diagnostic endpoint to check Datadog integration configuration
 */
export async function GET() {
  const config = getDatadogConfig();
  const hasApiKey = Boolean(config.apiKey && config.apiKey !== "[REPLACE_THIS]");
  const hasAppKey = Boolean(config.appKey && config.appKey !== "[REPLACE_THIS]");

  return NextResponse.json({
    status: hasApiKey ? "configured" : "incomplete_configuration",
    provider: "Datadog",
    service: config.service,
    site: config.site,
    hasApiKey,
    hasAppKey,
    timestamp: new Date().toISOString(),
  });
}

/**
 * POST /api/health/datadog
 * Dispatches heartbeat telemetry, infrastructure CPU/memory metrics, and logs to Datadog
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const message = body.message || "VAYU-RAKSHA Datadog Heartbeat Check";

    const logResult = await sendDatadogLog({
      message,
      level: "info",
      tags: ["type:healthcheck", "component:api"],
      attributes: {
        nodeVersion: process.version,
        platform: "Next.js App Router",
      },
    });

    const metricResult = await sendDatadogMetric({
      metric: "vayu_raksha.infrastructure.heartbeat",
      value: 1,
      type: "count",
      tags: ["status:healthy"],
    });

    const systemMetricsResult = await sendSystemMetrics();

    return NextResponse.json({
      success: logResult.success || metricResult.success || systemMetricsResult.success,
      logDelivery: logResult,
      metricDelivery: metricResult,
      systemMetricsDelivery: systemMetricsResult,
      message: "Datadog telemetry and infrastructure metrics dispatched.",
    });
  } catch (err: unknown) {
    const error = err as Error;
    return NextResponse.json(
      {
        success: false,
        error: error.message || "Unexpected failure while dispatching Datadog telemetry.",
      },
      { status: 500 }
    );
  }
}
