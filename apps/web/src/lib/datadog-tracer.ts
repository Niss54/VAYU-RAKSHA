/**
 * Datadog APM & Infrastructure Tracer Initialization
 * Service Name: VAYU-RAKSHA
 */
import tracer from "dd-trace";

let isInitialized = false;

export function initDatadog(): typeof tracer | null {
  if (isInitialized) return tracer;

  // Only initialize on Node.js server runtime
  if (typeof window !== "undefined") return null;

  try {
    const service = "VAYU-RAKSHA"; // Strictly enforced per requirement 8
    const env = process.env.DD_ENV || process.env.NODE_ENV || "development";
    const version = process.env.DD_VERSION || "2.0.0";
    const site = process.env.DD_SITE || "datadoghq.com";

    // Set environment defaults for dd-trace
    process.env.DD_SERVICE = service;
    process.env.DD_ENV = env;
    process.env.DD_VERSION = version;
    process.env.DD_SITE = site;

    tracer.init({
      service,
      env,
      version,
      // Collect process metrics: CPU, Heap Memory, Event Loop Latency, GC
      runtimeMetrics: true,
      logInjection: true,
      // Non-blocking & graceful fallback if Datadog Agent is not running locally
      startupLogs: false,
    });

    isInitialized = true;
    return tracer;
  } catch (err: unknown) {
    const error = err as Error;
    // Production-safe: never crash the application if Datadog fails to start
    console.warn("[Datadog APM] Tracer initialization bypassed:", error.message);
    return null;
  }
}

export { tracer };
