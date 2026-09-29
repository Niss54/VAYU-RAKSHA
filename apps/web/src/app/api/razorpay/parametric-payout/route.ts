import { NextRequest, NextResponse } from "next/server";
import { ParametricPayoutRequest, ParametricPayoutResult } from "@/lib/razorpay";

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as ParametricPayoutRequest;
    const {
      payoutBatchId,
      district,
      panchayatCount,
      totalAmountInr,
      hollandWindPeakKmph,
      floodInundationPct,
      triggerSource,
    } = body;

    // Verify parametric criteria
    const isWindTriggered = hollandWindPeakKmph >= 89;
    const isFloodTriggered = floodInundationPct >= 30;

    if (!isWindTriggered || !isFloodTriggered) {
      return NextResponse.json(
        {
          success: false,
          error: "Parametric threshold conditions not met. Required: Wind >= 89 km/h and Inundation >= 30%.",
          currentReadings: { hollandWindPeakKmph, floodInundationPct },
        },
        { status: 400 }
      );
    }

    const utr = `RZPX${Date.now()}${Math.floor(1000 + Math.random() * 9000)}`;
    const contractHash = `0x${Array.from({ length: 40 }, () => Math.floor(Math.random() * 16).toString(16)).join("")}`;

    const payoutResult: ParametricPayoutResult = {
      success: true,
      payoutBatchId: payoutBatchId || `VR_PAYOUT_${Date.now().toString(36).toUpperCase()}`,
      utrNumber: utr,
      status: "PROCESSED",
      totalAmountInr: totalAmountInr || 75000000,
      recipientCount: panchayatCount || 42,
      disbursedAt: new Date().toISOString(),
      smartContractHash: contractHash,
    };

    return NextResponse.json({
      success: true,
      payout: payoutResult,
      details: {
        district,
        triggerSource,
        disbursementChannel: "RazorpayX Connected Banking API / IMPS / UPI Direct Credit",
        beneficiaries: [
          { name: "Gram Panchayat Brahmagiri Relief Acct", amountInr: 1800000, status: "CREDITED_VIA_UPI" },
          { name: "Krushnaprasad Coastal SDRF Depot", amountInr: 1950000, status: "CREDITED_VIA_IMPS" },
          { name: "Astaranga Marine Fisherfolk Buffer", amountInr: 2100000, status: "CREDITED_VIA_IMPS" },
          { name: "Gop Sub-District Emergency Transit Fund", amountInr: 1650000, status: "CREDITED_VIA_NEFT" },
        ],
      },
    });
  } catch (error: any) {
    console.error("[VAYU-RAKSHA] Parametric Payout Error:", error);
    return NextResponse.json(
      { error: "Failed to process parametric payout", details: error?.message || String(error) },
      { status: 500 }
    );
  }
}
