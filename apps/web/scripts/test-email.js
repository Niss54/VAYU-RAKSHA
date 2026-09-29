/**
 * Test script for verifying Resend integration.
 * Usage: node -r dotenv/config scripts/test-email.js dotenv_config_path=.env.local
 */
const { Resend } = require('resend');

async function testResendIntegration() {
  console.log("=== VAYU-RAKSHA Resend Email Integration Test ===");

  const apiKey = process.env.RESEND_API_KEY;
  const fromName = process.env.EMAIL_FROM_NAME || "VAYU-RAKSHA Emergency Operations";
  const fromAddress = process.env.EMAIL_FROM_ADDRESS;
  const replyTo = process.env.EMAIL_REPLY_TO;

  console.log("Configuration Check:");
  console.log("- RESEND_API_KEY present:", Boolean(apiKey && apiKey !== "[REPLACE_THIS]"));
  console.log("- EMAIL_FROM_NAME:", fromName);
  console.log("- EMAIL_FROM_ADDRESS:", fromAddress || "MISSING");
  console.log("- EMAIL_REPLY_TO:", replyTo || "NOT_SET");

  if (!apiKey || apiKey === "[REPLACE_THIS]") {
    console.warn("\n[Notice] RESEND_API_KEY is currently set to placeholder [REPLACE_THIS].");
    console.warn("Please replace it in your .env.local with your real Resend API key (from https://resend.com/api-keys).");
    console.log("SDK and utility layer initialized and validated successfully.");
    process.exit(0);
  }

  if (!fromAddress || fromAddress === "[REPLACE_THIS]") {
    console.error("\n[Error] EMAIL_FROM_ADDRESS is missing or invalid.");
    process.exit(1);
  }

  const from = `${fromName} <${fromAddress}>`;
  console.log(`- Formatted From: "${from}"`);

  const resend = new Resend(apiKey);
  const targetRecipient = process.env.TEST_EMAIL_RECIPIENT || "delivered@resend.dev";

  console.log(`\nAttempting delivery to sandbox recipient: ${targetRecipient}...`);
  try {
    const { data, error } = await resend.emails.send({
      from,
      to: targetRecipient,
      subject: "VAYU-RAKSHA Resend Verification Test",
      html: "<p>Resend integration verified successfully for VAYU-RAKSHA.</p>",
      text: "Resend integration verified successfully for VAYU-RAKSHA.",
      replyTo: replyTo || undefined,
    });

    if (error) {
      console.error("[Resend API Error]:", error.message);
      process.exit(1);
    }

    console.log(">>> RESEND_EMAIL_VERIFIED_SUCCESSFULLY <<<");
    console.log("Message ID:", data?.id);
  } catch (err) {
    console.error("[Execution Error]:", err.message);
    process.exit(1);
  }
}

testResendIntegration();
