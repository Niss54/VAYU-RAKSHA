import { fileURLToPath } from "node:url";

import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  test: {
    include: ["src/**/*.test.ts"],
    coverage: {
      include: [
        "src/lib/format.ts",
        "src/lib/advisory.ts",
        "src/lib/alerts.ts",
        "src/lib/brief.ts",
        "src/lib/media.ts",
      ],
      thresholds: { lines: 90, branches: 90 },
    },
  },
});
