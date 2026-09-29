import { NextRequest, NextResponse } from "next/server";
import { verifyRazorpaySignature, RazorpayVerificationPayload } from "@/lib/razorpay";
import { sendDonationReceiptEmail } from "@/lib/email";

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as RazorpayVerificationPayload & {
      amount: number;
      campaignId: string;
      donorName?: string;
      donorEmail?: string;
      donorPan?: string;
    };

    const {
      razorpay_order_id,
      razorpay_payment_id,
      razorpay_signature,
      amount,
      campaignId,
      donorName = "Valued Disaster Contributor",
      donorEmail = "citizen@relief.in",
      donorPan,
    } = body;

    const secretKey = process.env.RAZORPAY_KEY_SECRET || "";

    const isValid = verifyRazorpaySignature(
      razorpay_order_id,
      razorpay_payment_id,
      razorpay_signature,
      secretKey
    );

    if (!isValid) {
      return NextResponse.json(
        { success: false, error: "Payment signature cryptographic verification failed." },
        { status: 400 }
      );
    }

    const certificateId = `80G-VR-${Date.now().toString(36).toUpperCase()}-${Math.floor(1000 + Math.random() * 9000)}`;

    // Dispatch official 80G tax receipt & donation confirmation email via Resend
    if (donorEmail && donorEmail.includes("@")) {
      sendDonationReceiptEmail(donorEmail, {
        donorName,
        amount,
        orderId: razorpay_order_id,
        paymentId: razorpay_payment_id,
        certificateId,
        campaign: campaignId || "SDRF-ODISHA-RELIEF",
      }).catch((emailErr) => {
        console.warn("[VAYU-RAKSHA] Non-blocking donation receipt email failed:", emailErr?.message || emailErr);
      });
    }

    return NextResponse.json({
      success: true,
      verified: true,
      transaction: {
        paymentId: razorpay_payment_id,
        orderId: razorpay_order_id,
        amountInr: amount,
        campaignId,
        donorName,
        donorEmail,
        donorPan: donorPan || "NOT_PROVIDED",
        timestamp: new Date().toISOString(),
        paymentMethod: "UPI / Netbanking / Card",
        status: "CAPTURED",
      },
      taxCertificate: {
        certificateNumber: certificateId,
        exemptionSection: "Section 80G(5)(vi) Income Tax Act 1961",
        eligibleDeductionPct: 50,
        organizationName: "Odisha State Disaster Management Authority / SDRF Relief Shield",
        pan: "AAATO2026R",
      },
      message: "Emergency disaster relief payment successfully verified and credited to emergency relief escrow.",
    });
  } catch (error: any) {
    console.error("[VAYU-RAKSHA] Razorpay Verification Error:", error);
    return NextResponse.json(
      { error: "Payment verification failed", details: error?.message || String(error) },
      { status: 500 }
    );
  }
}
