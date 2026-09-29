import { Resend } from "resend";

/**
 * Global singleton reference for Resend client to avoid duplicate instances
 * across hot-reloading in development.
 */
const globalForResend = globalThis as unknown as {
  resendClient?: Resend;
};

/**
 * Validates and retrieves the configured Resend instance.
 * Throws a clear error if required environment variables are absent.
 * NEVER logs or exposes the API key.
 */
export function getResendClient(): Resend {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey || apiKey === "[REPLACE_THIS]" || apiKey.trim() === "") {
    throw new Error(
      "[Resend Configuration Error] RESEND_API_KEY is not configured in environment variables. Please provide a valid Resend API key."
    );
  }

  if (!globalForResend.resendClient) {
    globalForResend.resendClient = new Resend(apiKey);
  }

  return globalForResend.resendClient;
}

/**
 * Validates and formats the sender and reply-to addresses.
 */
export function getSenderConfig(): { from: string; replyTo?: string } {
  const fromAddress = process.env.EMAIL_FROM_ADDRESS;
  if (!fromAddress || fromAddress === "[REPLACE_THIS]" || fromAddress.trim() === "") {
    throw new Error(
      "[Resend Configuration Error] EMAIL_FROM_ADDRESS is not configured in environment variables."
    );
  }

  const fromName = process.env.EMAIL_FROM_NAME?.trim() || "VAYU-RAKSHA Emergency Operations";
  const from = `${fromName} <${fromAddress.trim()}>`;
  const replyTo = process.env.EMAIL_REPLY_TO?.trim() || undefined;

  return { from, replyTo };
}

export interface SendEmailOptions {
  to: string | string[];
  subject: string;
  html: string;
  text?: string;
  replyTo?: string;
  headers?: Record<string, string>;
  tags?: { name: string; value: string }[];
}

export interface SendEmailResult {
  success: boolean;
  messageId?: string;
  error?: string;
}

/**
 * Primary transactional email dispatch function using Resend SDK.
 */
export async function sendEmail(options: SendEmailOptions): Promise<SendEmailResult> {
  try {
    const resend = getResendClient();
    const { from, replyTo: defaultReplyTo } = getSenderConfig();

    const response = await resend.emails.send({
      from,
      to: options.to,
      subject: options.subject,
      html: options.html,
      text: options.text,
      replyTo: options.replyTo || defaultReplyTo,
      headers: options.headers,
      tags: options.tags,
    });

    if (response.error) {
      console.error("[Resend Error] Delivery failed:", response.error.message);
      return {
        success: false,
        error: response.error.message,
      };
    }

    return {
      success: true,
      messageId: response.data?.id,
    };
  } catch (err: unknown) {
    const error = err as Error;
    console.error("[Resend Exception] Failed to send email:", error.message);
    return {
      success: false,
      error: error.message || "An unexpected error occurred while sending email via Resend",
    };
  }
}

// ─── TRANSACTIONAL EMAIL FLOWS ────────────────────────────────────────────────

/**
 * 1. Email Verification Flow
 */
export async function sendVerificationEmail(
  to: string,
  name: string,
  verificationUrl: string
): Promise<SendEmailResult> {
  const subject = "Verify your VAYU-RAKSHA Emergency Response account";
  const html = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background-color: #0d1117; color: #e6edf3; border-radius: 8px; overflow: hidden; border: 1px solid #30363d;">
      <div style="background: linear-gradient(135deg, #0969da, #1f6feb); padding: 24px; text-align: center;">
        <h1 style="margin: 0; color: #ffffff; font-size: 24px; letter-spacing: 1px;">VAYU-RAKSHA</h1>
        <p style="margin: 4px 0 0 0; color: #d0d7de; font-size: 13px;">Anticipatory Cyclone & Infrastructure Cascade Intelligence</p>
      </div>
      <div style="padding: 32px 24px;">
        <h2 style="color: #ffffff; font-size: 18px; margin-top: 0;">Welcome, ${name}!</h2>
        <p style="line-height: 1.6; color: #8b949e;">Please verify your official disaster monitoring email address to activate your access to real-time cyclone telemetry and evacuation protocols.</p>
        <div style="text-align: center; margin: 32px 0;">
          <a href="${verificationUrl}" style="background-color: #238636; color: #ffffff; padding: 12px 28px; font-weight: 600; text-decoration: none; border-radius: 6px; display: inline-block;">Verify Email Address</a>
        </div>
        <p style="font-size: 12px; color: #6e7681; word-break: break-all;">If the button does not work, copy and paste this link in your browser:<br/><a href="${verificationUrl}" style="color: #58a6ff;">${verificationUrl}</a></p>
      </div>
      <div style="border-top: 1px solid #21262d; padding: 16px 24px; text-align: center; font-size: 12px; color: #6e7681;">
        VAYU-RAKSHA Emergency Relief & SDRF Response Coordination.
      </div>
    </div>
  `;
  const text = `Welcome ${name},\n\nPlease verify your email for VAYU-RAKSHA by opening the following link:\n${verificationUrl}\n\nThank you,\nVAYU-RAKSHA Emergency Operations`;
  return sendEmail({ to, subject, html, text });
}

/**
 * 2. OTP / 2FA Verification Flow
 */
export async function sendOtpEmail(
  to: string,
  otpCode: string,
  purpose: string = "Account Login Verification"
): Promise<SendEmailResult> {
  const subject = `Your VAYU-RAKSHA Security Code: ${otpCode}`;
  const html = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 500px; margin: 0 auto; background-color: #0d1117; color: #e6edf3; border-radius: 8px; overflow: hidden; border: 1px solid #30363d;">
      <div style="background-color: #161b22; padding: 20px; text-align: center; border-bottom: 1px solid #30363d;">
        <h2 style="margin: 0; color: #58a6ff; font-size: 20px;">VAYU-RAKSHA Secure Auth</h2>
      </div>
      <div style="padding: 28px 24px; text-align: center;">
        <p style="color: #8b949e; margin-top: 0;">Use the one-time security code below for <strong>${purpose}</strong>:</p>
        <div style="background-color: #1f242c; border: 1px dashed #388bfd; border-radius: 8px; padding: 16px; margin: 24px auto; max-width: 240px;">
          <span style="font-size: 32px; font-weight: 700; letter-spacing: 6px; color: #ffffff; font-family: monospace;">${otpCode}</span>
        </div>
        <p style="font-size: 13px; color: #f85149; margin-bottom: 0;">This code will expire in 10 minutes. Do not share it with anyone.</p>
      </div>
    </div>
  `;
  const text = `Your VAYU-RAKSHA security code for ${purpose} is: ${otpCode}\nValid for 10 minutes.`;
  return sendEmail({ to, subject, html, text });
}

/**
 * 3. Password Reset Flow
 */
export async function sendPasswordResetEmail(
  to: string,
  name: string,
  resetUrl: string
): Promise<SendEmailResult> {
  const subject = "Reset your VAYU-RAKSHA password";
  const html = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background-color: #0d1117; color: #e6edf3; border-radius: 8px; overflow: hidden; border: 1px solid #30363d;">
      <div style="background-color: #161b22; padding: 20px; text-align: center; border-bottom: 1px solid #30363d;">
        <h2 style="margin: 0; color: #d29922; font-size: 20px;">Password Reset Request</h2>
      </div>
      <div style="padding: 32px 24px;">
        <p style="color: #e6edf3;">Hello ${name},</p>
        <p style="color: #8b949e; line-height: 1.6;">We received a request to reset your password for VAYU-RAKSHA Emergency Platform. Click the button below to choose a new password:</p>
        <div style="text-align: center; margin: 32px 0;">
          <a href="${resetUrl}" style="background-color: #1f6feb; color: #ffffff; padding: 12px 24px; font-weight: 600; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
        </div>
        <p style="font-size: 12px; color: #6e7681;">If you did not request this change, you can safely ignore this email.</p>
      </div>
    </div>
  `;
  const text = `Hello ${name},\n\nClick this link to reset your password:\n${resetUrl}\n\nIf you did not request this, please ignore.`;
  return sendEmail({ to, subject, html, text });
}

/**
 * 4. Cyclone Alert / Early Warning Notification
 */
export async function sendCycloneAlertEmail(
  to: string | string[],
  alert: {
    cycloneName: string;
    district: string;
    severity: string;
    windSpeedKmH: number;
    evacuationInstructions: string;
    timestamp?: string;
  }
): Promise<SendEmailResult> {
  const subject = `⚠️ URGENT CYCLONE ALERT: ${alert.cycloneName} — District ${alert.district} (${alert.severity})`;
  const html = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background-color: #0d1117; color: #e6edf3; border-radius: 8px; overflow: hidden; border: 2px solid #da3633;">
      <div style="background-color: #b62324; padding: 20px; text-align: center; color: #ffffff;">
        <h1 style="margin: 0; font-size: 20px; letter-spacing: 1px;">🚨 EMERGENCY DISASTER ADVISORY</h1>
        <p style="margin: 4px 0 0 0; font-size: 13px;">Special Relief Commissioner & SDRF Command Center</p>
      </div>
      <div style="padding: 24px;">
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <tr>
            <td style="padding: 8px; color: #8b949e; border-bottom: 1px solid #21262d;">Cyclone System:</td>
            <td style="padding: 8px; color: #ffffff; font-weight: 700; border-bottom: 1px solid #21262d;">${alert.cycloneName}</td>
          </tr>
          <tr>
            <td style="padding: 8px; color: #8b949e; border-bottom: 1px solid #21262d;">Target District:</td>
            <td style="padding: 8px; color: #58a6ff; font-weight: 700; border-bottom: 1px solid #21262d;">${alert.district}</td>
          </tr>
          <tr>
            <td style="padding: 8px; color: #8b949e; border-bottom: 1px solid #21262d;">Severity Level:</td>
            <td style="padding: 8px; color: #f85149; font-weight: 700; border-bottom: 1px solid #21262d;">${alert.severity}</td>
          </tr>
          <tr>
            <td style="padding: 8px; color: #8b949e; border-bottom: 1px solid #21262d;">Projected Sustained Winds:</td>
            <td style="padding: 8px; color: #e6edf3; font-weight: 700; border-bottom: 1px solid #21262d;">${alert.windSpeedKmH} km/h</td>
          </tr>
        </table>
        <div style="background-color: #161b22; border-left: 4px solid #da3633; padding: 16px; border-radius: 0 4px 4px 0;">
          <h4 style="margin: 0 0 8px 0; color: #f85149;">Direct Action Protocol:</h4>
          <p style="margin: 0; line-height: 1.5; color: #d0d7de;">${alert.evacuationInstructions}</p>
        </div>
      </div>
    </div>
  `;
  const text = `URGENT CYCLONE ALERT: ${alert.cycloneName}\nDistrict: ${alert.district}\nSeverity: ${alert.severity}\nWind Speed: ${alert.windSpeedKmH} km/h\nInstructions: ${alert.evacuationInstructions}`;
  return sendEmail({ to, subject, html, text });
}

/**
 * 5. Disaster Relief Donation & 80G Tax Exemption Receipt Flow
 */
export async function sendDonationReceiptEmail(
  to: string,
  receipt: {
    donorName: string;
    amount: number;
    currency?: string;
    orderId: string;
    paymentId: string;
    certificateId: string;
    campaign: string;
  }
): Promise<SendEmailResult> {
  const currency = receipt.currency || "INR";
  const subject = `Official Donation Receipt & 80G Certificate — VAYU-RAKSHA (${currency} ${receipt.amount})`;
  const html = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background-color: #0d1117; color: #e6edf3; border-radius: 8px; overflow: hidden; border: 1px solid #30363d;">
      <div style="background: linear-gradient(135deg, #1f6feb, #238636); padding: 24px; text-align: center; color: #ffffff;">
        <h2 style="margin: 0; font-size: 22px;">Emergency Relief Contribution</h2>
        <p style="margin: 4px 0 0 0; font-size: 13px; color: #e6edf3;">State Disaster Response Fund (SDRF) / VAYU-RAKSHA Shield</p>
      </div>
      <div style="padding: 28px 24px;">
        <p style="margin-top: 0; font-size: 16px;">Dear <strong>${receipt.donorName}</strong>,</p>
        <p style="color: #8b949e; line-height: 1.6;">Thank you for your generous emergency disaster contribution. Your payment has been verified and deposited into the immediate disaster response escrow.</p>
        
        <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin: 20px 0;">
          <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
              <td style="padding: 6px 0; color: #8b949e;">Amount Contributed:</td>
              <td style="padding: 6px 0; font-weight: 700; color: #3fb950; text-align: right;">${currency} ${receipt.amount.toLocaleString("en-IN")}</td>
            </tr>
            <tr>
              <td style="padding: 6px 0; color: #8b949e;">Certificate No:</td>
              <td style="padding: 6px 0; font-family: monospace; color: #58a6ff; text-align: right;">${receipt.certificateId}</td>
            </tr>
            <tr>
              <td style="padding: 6px 0; color: #8b949e;">Payment ID:</td>
              <td style="padding: 6px 0; font-family: monospace; color: #e6edf3; text-align: right;">${receipt.paymentId}</td>
            </tr>
            <tr>
              <td style="padding: 6px 0; color: #8b949e;">Campaign:</td>
              <td style="padding: 6px 0; color: #e6edf3; text-align: right;">${receipt.campaign}</td>
            </tr>
          </table>
        </div>

        <div style="background-color: #121d2f; border: 1px solid #1f6feb; border-radius: 6px; padding: 12px; font-size: 12px; color: #79c0ff;">
          <strong>Tax Exemption Note:</strong> Eligible for 50% deduction under Section 80G(5)(vi) of the Income Tax Act, 1961. PAN: AAATO2026R.
        </div>
      </div>
      <div style="border-top: 1px solid #21262d; padding: 16px; text-align: center; font-size: 12px; color: #6e7681;">
        Thank you for standing with cyclone-affected coastal communities.
      </div>
    </div>
  `;
  const text = `Dear ${receipt.donorName},\n\nThank you for contributing ${currency} ${receipt.amount} to ${receipt.campaign}.\nCertificate ID: ${receipt.certificateId}\nPayment ID: ${receipt.paymentId}\nEligible for Section 80G deduction.\n\nVAYU-RAKSHA Relief Operations`;
  return sendEmail({ to, subject, html, text });
}

/**
 * 6. Test Email Flow
 */
export async function sendTestEmail(to: string): Promise<SendEmailResult> {
  const subject = "Resend Integration Verified — VAYU-RAKSHA Emergency Platform";
  const html = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 500px; margin: 0 auto; background-color: #0d1117; color: #e6edf3; border-radius: 8px; padding: 24px; border: 1px solid #30363d; text-align: center;">
      <h2 style="color: #3fb950; margin-top: 0;">✓ Resend Integration Active</h2>
      <p style="color: #8b949e; line-height: 1.6;">This is an official test email confirming that your Resend SDK is configured correctly on the VAYU-RAKSHA platform.</p>
      <div style="background-color: #161b22; border-radius: 6px; padding: 12px; font-size: 12px; color: #58a6ff; font-family: monospace; margin: 16px 0;">
        Timestamp: ${new Date().toISOString()}
      </div>
      <p style="font-size: 12px; color: #6e7681; margin-bottom: 0;">Resend Transactional Email Engine • VAYU-RAKSHA</p>
    </div>
  `;
  const text = `Resend Integration Verified for VAYU-RAKSHA at ${new Date().toISOString()}`;
  return sendEmail({ to, subject, html, text });
}
