import { NextRequest, NextResponse } from "next/server";
import { runVayuRakshaSimulation } from "@/lib/vayu-engine";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const scenario = body.scenario === "dana" ? "dana" : "fani";
    const hardenedNodes = Array.isArray(body.hardenedNodeIds) ? body.hardenedNodeIds : [];

    const simulationResult = runVayuRakshaSimulation(scenario, hardenedNodes);

    return NextResponse.json({
      success: true,
      data: simulationResult,
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Simulation execution failure",
      },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const scenario = searchParams.get("scenario") === "dana" ? "dana" : "fani";

  const simulationResult = runVayuRakshaSimulation(scenario);

  return NextResponse.json({
    success: true,
    data: simulationResult,
  });
}
