import { NextRequest, NextResponse } from "next/server";
import { verifyRazorpayWebhook } from "@/lib/razorpay";

export async function POST(req: NextRequest) {
  try {
    const rawBody = await req.text();
    const signature = req.headers.get("x-razorpay-signature") || "";
    const webhookSecret = process.env.RAZORPAY_WEBHOOK_SECRET || "";

    const isValid = verifyRazorpayWebhook(rawBody, signature, webhookSecret);

    if (!isValid) {
      console.warn("[VAYU-RAKSHA] Invalid webhook signature received.");
      return NextResponse.json({ error: "Invalid webhook signature" }, { status: 400 });
    }

    const event = JSON.parse(rawBody);
    const eventType = event.event;

    console.log(`[VAYU-RAKSHA Razorpay Webhook] Event received: ${eventType}`);

    switch (eventType) {
      case "payment.captured":
        // Immediate relief donation captured
        const payment = event.payload.payment.entity;
        console.log(`[VAYU-RAKSHA] Payment Captured: ID=${payment.id}, Amount=₹${payment.amount / 100}`);
        break;

      case "order.paid":
        const order = event.payload.order.entity;
        console.log(`[VAYU-RAKSHA] Order Paid: ID=${order.id}, Receipt=${order.receipt}`);
        break;

      case "payout.processed":
        // RazorpayX parametric emergency payout processed
        const payout = event.payload.payout.entity;
        console.log(`[VAYU-RAKSHA] Parametric Relief Payout Disbursed: ID=${payout.id}, Amount=₹${payout.amount / 100}, UTR=${payout.utr}`);
        break;

      default:
        console.log(`[VAYU-RAKSHA] Unhandled webhook event type: ${eventType}`);
        break;
    }

    return NextResponse.json({ status: "ok", received: true, event: eventType });
  } catch (error: any) {
    console.error("[VAYU-RAKSHA] Razorpay Webhook Handling Error:", error);
    return NextResponse.json({ error: "Webhook processing error" }, { status: 500 });
  }
}
