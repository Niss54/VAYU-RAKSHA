/**
 * Datadog Infrastructure Monitoring & Telemetry Client
 * Service Name: VAYU-RAKSHA
 * Sends metrics, events, and structured logs to Datadog via HTTPS API.
 */
import os from "os";

export interface DatadogConfig {
  apiKey: string;
  appKey?: string;
  site: string;
  service: string;
}

export function getDatadogConfig(): DatadogConfig {
  const apiKey = process.env.DD_API_KEY?.trim() || "";
  const appKey = process.env.DD_APP_KEY?.trim() || "";
  const site = process.env.DD_SITE?.trim() || "datadoghq.com";
  const service = "VAYU-RAKSHA"; // Strictly enforced per requirement 8

  return { apiKey, appKey, site, service };
}

export interface MetricPayload {
  metric: string;
  value: number;
  type?: "count" | "gauge" | "rate";
  tags?: string[];
}

export interface LogPayload {
  message: string;
  level?: "info" | "warn" | "error" | "debug";
  tags?: string[];
  attributes?: Record<string, unknown>;
}

export interface EventPayload {
  title: string;
  text: string;
  alertType?: "info" | "warning" | "error" | "success";
  tags?: string[];
}

/**
 * Send custom infrastructure metric to Datadog (V2 Series API)
 */
export async function sendDatadogMetric(metric: MetricPayload): Promise<{ success: boolean; error?: string }> {
  const { apiKey, site, service } = getDatadogConfig();

  if (!apiKey || apiKey === "[REPLACE_THIS]") {
    return { success: false, error: "DD_API_KEY is not configured" };
  }

  const timestamp = Math.floor(Date.now() / 1000);
  const tags = [`service:${service}`, `env:${process.env.NODE_ENV || "development"}`, ...(metric.tags || [])];

  const payload = {
    series: [
      {
        metric: metric.metric,
        type: metric.type === "count" ? 1 : 2, // 1: count, 2: gauge
        points: [
          {
            timestamp,
            value: metric.value,
          },
        ],
        tags,
      },
    ],
  };

  try {
    const res = await fetch(`https://api.${site}/api/v2/series`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "DD-API-KEY": apiKey,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      return { success: false, error: `Datadog API returned status ${res.status}: ${errText}` };
    }

    return { success: true };
  } catch (err: unknown) {
    const error = err as Error;
    return { success: false, error: error.message };
  }
}

/**
 * Collect and send system infrastructure metrics (CPU, Memory, Process Uptime)
 */
export async function sendSystemMetrics(): Promise<{ success: boolean; metricsCount: number; error?: string }> {
  const { apiKey, site, service } = getDatadogConfig();

  if (!apiKey || apiKey === "[REPLACE_THIS]") {
    return { success: false, metricsCount: 0, error: "DD_API_KEY is not configured" };
  }

  const timestamp = Math.floor(Date.now() / 1000);
  const mem = process.memoryUsage();
  const cpu = process.cpuUsage();
  const env = process.env.NODE_ENV || "development";
  const tags = [`service:${service}`, `env:${env}`, `host:${os.hostname()}`];

  const series = [
    { metric: "vayu_raksha.process.memory.heap_used_bytes", points: [{ timestamp, value: mem.heapUsed }], type: 2, tags },
    { metric: "vayu_raksha.process.memory.heap_total_bytes", points: [{ timestamp, value: mem.heapTotal }], type: 2, tags },
    { metric: "vayu_raksha.process.memory.rss_bytes", points: [{ timestamp, value: mem.rss }], type: 2, tags },
    { metric: "vayu_raksha.process.cpu.user_ms", points: [{ timestamp, value: Math.round(cpu.user / 1000) }], type: 2, tags },
    { metric: "vayu_raksha.process.cpu.system_ms", points: [{ timestamp, value: Math.round(cpu.system / 1000) }], type: 2, tags },
    { metric: "vayu_raksha.process.uptime_seconds", points: [{ timestamp, value: Math.round(process.uptime()) }], type: 2, tags },
    { metric: "vayu_raksha.system.memory.free_bytes", points: [{ timestamp, value: os.freemem() }], type: 2, tags },
    { metric: "vayu_raksha.system.memory.total_bytes", points: [{ timestamp, value: os.totalmem() }], type: 2, tags },
  ];

  try {
    const res = await fetch(`https://api.${site}/api/v2/series`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "DD-API-KEY": apiKey,
      },
      body: JSON.stringify({ series }),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      return { success: false, metricsCount: 0, error: `Datadog API returned status ${res.status}: ${errText}` };
    }

    return { success: true, metricsCount: series.length };
  } catch (err: unknown) {
    const error = err as Error;
    return { success: false, metricsCount: 0, error: error.message };
  }
}

/**
 * Ship a structured log event to Datadog Logs HTTP Intake
 */
export async function sendDatadogLog(log: LogPayload): Promise<{ success: boolean; error?: string }> {
  const { apiKey, site, service } = getDatadogConfig();

  if (!apiKey || apiKey === "[REPLACE_THIS]") {
    return { success: false, error: "DD_API_KEY is not configured" };
  }

  const payload = [
    {
      ddsource: "nodejs",
      service,
      status: log.level || "info",
      message: log.message,
      ddtags: [`env:${process.env.NODE_ENV || "development"}`, ...(log.tags || [])].join(","),
      timestamp: new Date().toISOString(),
      ...log.attributes,
    },
  ];

  try {
    const res = await fetch(`https://http-intake.logs.${site}/api/v2/logs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "DD-API-KEY": apiKey,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      return { success: false, error: `Datadog Logs API returned status ${res.status}: ${errText}` };
    }

    return { success: true };
  } catch (err: unknown) {
    const error = err as Error;
    return { success: false, error: error.message };
  }
}

/**
 * Post an event to Datadog Events Stream
 */
export async function sendDatadogEvent(event: EventPayload): Promise<{ success: boolean; error?: string }> {
  const { apiKey, site, service } = getDatadogConfig();

  if (!apiKey || apiKey === "[REPLACE_THIS]") {
    return { success: false, error: "DD_API_KEY is not configured" };
  }

  const payload = {
    title: event.title,
    text: event.text,
    alert_type: event.alertType || "info",
    tags: [`service:${service}`, `env:${process.env.NODE_ENV || "development"}`, ...(event.tags || [])],
  };

  try {
    const res = await fetch(`https://api.${site}/api/v1/events`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "DD-API-KEY": apiKey,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      return { success: false, error: `Datadog Events API returned status ${res.status}: ${errText}` };
    }

    return { success: true };
  } catch (err: unknown) {
    const error = err as Error;
    return { success: false, error: error.message };
  }
}

/**
 * Track execution latency of an async operation and ship metric to Datadog
 */
export async function trackLatency<T>(operation: string, fn: () => Promise<T>): Promise<T> {
  const start = Date.now();
  try {
    const result = await fn();
    const durationMs = Date.now() - start;
    sendDatadogMetric({
      metric: "vayu_raksha.operation.latency_ms",
      value: durationMs,
      type: "gauge",
      tags: [`operation:${operation}`, "status:success"],
    }).catch(() => {});
    return result;
  } catch (error) {
    const durationMs = Date.now() - start;
    sendDatadogMetric({
      metric: "vayu_raksha.operation.latency_ms",
      value: durationMs,
      type: "gauge",
      tags: [`operation:${operation}`, "status:error"],
    }).catch(() => {});
    throw error;
  }
}
