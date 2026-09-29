import { NextRequest, NextResponse } from "next/server";
import { getRazorpayServerClient, RazorpayOrderPayload } from "@/lib/razorpay";

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as RazorpayOrderPayload;
    const { amount, currency = "INR", campaignId, donorName, donorEmail, donorPhone, district } = body;

    if (!amount || amount <= 0) {
      return NextResponse.json({ error: "Invalid donation or payout amount." }, { status: 400 });
    }

    const amountInPaise = Math.round(amount * 100);
    const receipt = `vayu_rcpt_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 6)}`;

    const razorpay = await getRazorpayServerClient();

    if (razorpay) {
      // Live / Test Mode with Razorpay SDK
      const order = await razorpay.orders.create({
        amount: amountInPaise,
        currency,
        receipt,
        notes: {
          platform: "VAYU-RAKSHA",
          campaignId: campaignId || "general_disaster_relief",
          district: district || "Coastal_Odisha",
          donorName: donorName || "Anonymous Donor",
          taxExemption: "80G_Eligible",
        },
      });

      return NextResponse.json({
        success: true,
        orderId: order.id,
        amount: order.amount,
        currency: order.currency,
        receipt: order.receipt,
        isLiveRazorpay: true,
        keyId: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || process.env.RAZORPAY_KEY_ID,
      });
    } else {
      // High-Fidelity Simulation / Demo Mode (Ensures zero-friction hackathon demos without active gateway failure)
      const mockOrderId = `order_sim_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 8)}`;

      return NextResponse.json({
        success: true,
        orderId: mockOrderId,
        amount: amountInPaise,
        currency,
        receipt,
        isLiveRazorpay: false,
        keyId: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "rzp_test_vayuRaksha2026",
        notes: {
          mode: "SIMULATION_FALLBACK",
          message: "Razorpay order initialized in tactical simulation mode.",
        },
      });
    }
  } catch (error: any) {
    console.error("[VAYU-RAKSHA] Razorpay Order Creation Failed:", error);
    return NextResponse.json(
      { error: "Failed to generate Razorpay payment order", details: error?.message || String(error) },
      { status: 500 }
    );
  }
}
