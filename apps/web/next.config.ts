import type { NextConfig } from "next";

import { GEO_API_URL } from "./src/server/geo";

const nextConfig: NextConfig = {
  // The browser calls /api/geo/*; Next.js forwards to the geo API so its location stays server-side configuration.
  async rewrites() {
    return [{ source: "/api/geo/:path*", destination: `${GEO_API_URL}/:path*` }];
  },
  // gRPC-based client: load it from node_modules at runtime rather than bundling it.
  serverExternalPackages: ["@google-cloud/firestore"],
};

export default nextConfig;
