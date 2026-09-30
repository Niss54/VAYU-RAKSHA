/**
 * Integration test script for verifying Cloudinary file storage, upload, retrieval, and cleanup flow.
 * Usage: node -r dotenv/config scripts/test-cloudinary.js dotenv_config_path=.env.local
 */

const https = require("https");
https.globalAgent = new https.Agent({ family: 4, keepAlive: true });
const dns = require("dns");
if (dns.setDefaultResultOrder) {
  dns.setDefaultResultOrder("ipv4first");
}
const { v2: cloudinary } = require("cloudinary");


function parseSecret(rawSecret) {
  if (!rawSecret) return "";
  let secret = rawSecret.trim();
  if (secret.startsWith("CLOUDINARY_URL=")) {
    secret = secret.replace(/^CLOUDINARY_URL=/, "").trim();
  }
  const match = secret.match(/cloudinary:\/\/[^:]+:([^@]+)@/);
  if (match) return match[1];
  return secret;
}

async function testCloudinaryFlow() {
  console.log("=== VAYU-RAKSHA Cloudinary Storage Integration Test ===");

  const cloudName = process.env.CLOUDINARY_CLOUD_NAME;
  const apiKey = process.env.CLOUDINARY_API_KEY;
  const rawSecret = process.env.CLOUDINARY_API_SECRET;
  const apiSecret = parseSecret(rawSecret);

  console.log("\n1. Configuration Check:");
  console.log("   - CLOUDINARY_CLOUD_NAME:", cloudName);
  console.log("   - CLOUDINARY_API_KEY:", apiKey ? `${apiKey.substring(0, 6)}...` : "missing");
  console.log("   - CLOUDINARY_API_SECRET set:", Boolean(apiSecret));
  console.log("   - Raw secret had CLOUDINARY_URL prefix:", rawSecret && rawSecret.startsWith("CLOUDINARY_URL="));

  if (!cloudName || !apiKey || !apiSecret) {
    console.error("❌ Missing required Cloudinary credentials in environment!");
    process.exit(1);
  }

  cloudinary.config({
    cloud_name: cloudName,
    api_key: apiKey,
    api_secret: apiSecret,
    secure: true,
  });

  // Step 2: Ping Cloudinary API
  console.log("\n2. Pinging Cloudinary API...");
  try {
    const pingResult = await cloudinary.api.ping();
    console.log("   ✓ Ping successful:", pingResult);
  } catch (err) {
    console.error("❌ Failed to connect to Cloudinary:", err.message || err.error?.message || JSON.stringify(err));
    process.exit(1);
  }

  // Step 3: Test Uploading an Image Asset
  console.log("\n3. Testing Asset Upload (Sample 1x1 PNG data URI)...");
  // 1x1 transparent PNG data URL
  const samplePngDataUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAEDktHR9MAAAAASUVORK5CYII=";
  
  let uploadedPublicId = null;
  let secureUrl = null;

  const testAssets = [
    {
      name: "Image (PNG)",
      dataUrl: samplePngDataUrl,
      folder: "vayu-raksha/test/images",
      resourceType: "image",
    },
    {
      name: "Document (PDF)",
      dataUrl: "data:application/pdf;base64,JVBERi0xLjQKMSAwIG9iajw8L1R5cGUvQ2F0YWxvZy9QYWdlcyAyIDAgUj4+ZW5kb2JqCjIgMCBvYmo8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PmVuZG9iagozIDAgb2JqPDwvVHlwZS9QYWdlL01lZGlhQm94WzAgMCAzIDNdL1BhcmVudCAyIDAgUj4+ZW5kb2JqCnhyZWYKMCA0CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAwMDAwMDUzIDAwMDAwIG4gCjAwMDAwMDAxMDIgMDAwMDAgbiAKdHJhaWxlcjw8L1NpemUgNC9Sb290IDEgMCBSPj4Kc3RhcnR4cmVmCjE3OAolJUVPRg==",
      folder: "vayu-raksha/test/docs",
      resourceType: "image", // Cloudinary processes PDFs under image or raw
    },
    {
      name: "Audio Note (WAV)",
      dataUrl: "data:audio/wav;base64,UklGRiwAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YQgAAAAAAAAAAAAAAA==",
      folder: "vayu-raksha/test/audio",
      resourceType: "video", // Cloudinary processes audio under video
    },
  ];

  const uploadedRecords = [];

  for (const asset of testAssets) {
    console.log(`\n3. Testing Asset Upload: ${asset.name}...`);
    try {
      const uploadResult = await cloudinary.uploader.upload(asset.dataUrl, {
        folder: asset.folder,
        resource_type: "auto",
        tags: ["vayu-raksha", "automated-test"],
      });

      console.log("   ✓ Upload successful!");
      console.log("   - Public ID:", uploadResult.public_id);
      console.log("   - Secure URL (HTTPS):", uploadResult.secure_url);
      console.log("   - Format:", uploadResult.format);
      console.log("   - Bytes:", uploadResult.bytes);
      console.log("   - Resource Type:", uploadResult.resource_type);

      if (!uploadResult.secure_url || !uploadResult.secure_url.startsWith("https://")) {
        throw new Error("Upload did not return a valid HTTPS secure_url");
      }

      uploadedRecords.push({
        name: asset.name,
        publicId: uploadResult.public_id,
        secureUrl: uploadResult.secure_url,
        resourceType: uploadResult.resource_type,
      });
    } catch (err) {
      console.error(`❌ Upload test failed for ${asset.name}:`, err.message || err);
      process.exit(1);
    }
  }

  // Step 4: Test Asset Retrieval via API for all uploaded assets
  console.log("\n4. Testing Asset Retrieval via Cloudinary API...");
  for (const record of uploadedRecords) {
    try {
      const resource = await cloudinary.api.resource(record.publicId, {
        resource_type: record.resourceType,
      });
      console.log(`   ✓ Retrieved ${record.name} details successfully!`);
      console.log("   - Public ID verified:", resource.public_id === record.publicId);
      console.log("   - Secure URL verified:", resource.secure_url === record.secureUrl);
    } catch (err) {
      console.error(`❌ Asset retrieval failed for ${record.name}:`, err.message || err);
      process.exit(1);
    }
  }

  // Step 5: Test Asset Cleanup (Deletion)
  console.log("\n5. Cleaning up test assets...");
  for (const record of uploadedRecords) {
    try {
      const deleteResult = await cloudinary.uploader.destroy(record.publicId, {
        resource_type: record.resourceType,
      });
      console.log(`   ✓ Cleanup for ${record.name}:`, deleteResult.result || deleteResult);
    } catch (err) {
      console.warn(`   ⚠️ Cleanup warning for ${record.name}:`, err.message || err);
    }
  }

  console.log("\n🎉 ALL CLOUDINARY STORAGE TESTS (IMAGES, DOCS, AUDIO) PASSED SUCCESSFULLY!\n");
}

testCloudinaryFlow().catch((err) => {
  console.error("Unhandled error:", err);
  process.exit(1);
});
