import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs/config";

import { GEO_API_URL } from "./src/server/geo";

const nextConfig: NextConfig = {
  // The browser calls /api/geo/*; Next.js forwards to the geo API so its location stays server-side configuration.
  async rewrites() {
    const destinationBase = GEO_API_URL.startsWith("http") ? GEO_API_URL : `https://${GEO_API_URL}`;
    return [{ source: "/api/geo/:path*", destination: `${destinationBase}/:path*` }];
  },
  // gRPC-based client & APM tracer: load from node_modules at runtime rather than bundling.
  serverExternalPackages: ["@google-cloud/firestore", "dd-trace"],
};

export default withSentryConfig(nextConfig, {
  silent: !process.env.CI,
  telemetry: false,
});
