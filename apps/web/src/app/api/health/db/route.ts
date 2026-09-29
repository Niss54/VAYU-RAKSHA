import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const startTime = Date.now();
    // Execute live health check query on Neon PostgreSQL
    const rawResult = await prisma.$queryRaw`SELECT 1 as connected, NOW() as server_time, version() as pg_version;`;
    const latencyMs = Date.now() - startTime;

    return NextResponse.json({
      status: "healthy",
      database: "Neon PostgreSQL",
      connected: true,
      latencyMs,
      neonAuthUrl: process.env.NEON_AUTH_URL ? "Configured" : "Not Set",
      dataApiUrl: process.env.DATA_API_URL ? "Configured" : "Not Set",
      result: rawResult,
      timestamp: new Date().toISOString(),
    });
  } catch (error: unknown) {
    const err = error as Error;
    return NextResponse.json(
      {
        status: "unhealthy",
        database: "Neon PostgreSQL",
        connected: false,
        error: err.message || "Failed to connect to Neon database",
      },
      { status: 500 }
    );
  }
}
