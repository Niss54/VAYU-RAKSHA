import { v2 as cloudinary, type UploadApiResponse, type ResourceApiResponse } from "cloudinary";

/**
 * Cloudinary Storage Implementation for VAYU-RAKSHA.
 * Replaces legacy AWS S3 and Cloudflare R2 storage.
 *
 * Security: Credentials are read exclusively on the server and never exposed to the client.
 */

export interface CloudinaryConfig {
  cloudName: string;
  apiKey: string;
  apiSecret: string;
  secure: boolean;
}

export interface UploadOptions {
  folder?: string;
  publicId?: string;
  resourceType?: "auto" | "image" | "video" | "raw";
  tags?: string[];
  filename?: string;
  mimeType?: string;
}

export interface UploadResult {
  url: string;
  secure_url: string;
  public_id: string;
  format: string;
  resource_type: string;
  bytes: number;
  created_at: string;
  original_filename?: string;
  width?: number;
  height?: number;
  duration?: number;
}

export const DEFAULT_ALLOWED_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/gif",
  "image/svg+xml",
  "application/pdf",
  "audio/wav",
  "audio/webm",
  "audio/mp3",
  "audio/mpeg",
  "audio/ogg",
];

export const DEFAULT_MAX_SIZE_MB = 10;

/**
 * Parse and sanitize the Cloudinary API secret.
 * Handles both plain secret strings and full connection strings
 * (e.g. "CLOUDINARY_URL=cloudinary://<key>:<secret>@<cloud_name>" or "cloudinary://...").
 */
export function parseCloudinarySecret(rawSecret?: string): string {
  if (!rawSecret) return "";
  let secret = rawSecret.trim();

  // Strip leading CLOUDINARY_URL= if present
  if (secret.startsWith("CLOUDINARY_URL=")) {
    secret = secret.replace(/^CLOUDINARY_URL=/, "").trim();
  }

  // Extract secret component from cloudinary://<key>:<secret>@<cloud_name>
  const urlMatch = secret.match(/cloudinary:\/\/[^:]+:([^@]+)@/);
  if (urlMatch) {
    return urlMatch[1];
  }

  return secret;
}

/**
 * Read and validate server-side Cloudinary credentials.
 * Throws if required configuration is missing.
 */
export function getCloudinaryConfig(): CloudinaryConfig {
  const rawUrl = process.env.CLOUDINARY_URL;
  let cloudName = process.env.CLOUDINARY_CLOUD_NAME;
  let apiKey = process.env.CLOUDINARY_API_KEY;
  let rawSecret = process.env.CLOUDINARY_API_SECRET;

  // If a full CLOUDINARY_URL connection string is provided, extract fallback values
  if (rawUrl) {
    const urlMatch = rawUrl.trim().replace(/^CLOUDINARY_URL=/, "").match(/cloudinary:\/\/([^:]+):([^@]+)@(.+)/);
    if (urlMatch) {
      apiKey = apiKey || urlMatch[1];
      rawSecret = rawSecret || urlMatch[2];
      cloudName = cloudName || urlMatch[3];
    }
  }

  // Also extract cloud name or api key from rawSecret if rawSecret itself was a CLOUDINARY_URL
  if (rawSecret && rawSecret.includes("cloudinary://")) {
    const fullMatch = rawSecret.trim().replace(/^CLOUDINARY_URL=/, "").match(/cloudinary:\/\/([^:]+):([^@]+)@(.+)/);
    if (fullMatch) {
      apiKey = apiKey || fullMatch[1];
      cloudName = cloudName || fullMatch[3];
    }
  }

  const apiSecret = parseCloudinarySecret(rawSecret);

  if (!cloudName || !apiKey || !apiSecret) {
    throw new Error(
      "Missing Cloudinary credentials. Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET environment variables.",
    );
  }

  return {
    cloudName,
    apiKey,
    apiSecret,
    secure: true,
  };
}

/**
 * Configure and return the Cloudinary v2 SDK client.
 */
export function configureCloudinary(): typeof cloudinary {
  const config = getCloudinaryConfig();

  // On Node.js, ensure IPv4 network connectivity is prioritized
  try {
    const https = require("https");
    if (https && https.globalAgent && https.globalAgent.options) {
      https.globalAgent.options.family = 4;
    }
  } catch {
    // Non-fatal if running in edge/browser environment
  }

  cloudinary.config({
    cloud_name: config.cloudName,
    api_key: config.apiKey,
    api_secret: config.apiSecret,
    secure: config.secure,
  });
  return cloudinary;
}


/**
 * Returns the list of permitted MIME types from environment or defaults.
 */
export function getAllowedFileTypes(): string[] {
  const envTypes = process.env.ALLOWED_FILE_TYPES;
  if (!envTypes) return DEFAULT_ALLOWED_TYPES;
  return envTypes
    .split(",")
    .map((t) => t.trim().toLowerCase())
    .filter(Boolean);
}

/**
 * Returns maximum allowed file size in bytes from environment or defaults.
 */
export function getMaxFileSizeBytes(): number {
  const envMb = parseFloat(process.env.MAX_FILE_SIZE_MB || "");
  const mb = !isNaN(envMb) && envMb > 0 ? envMb : DEFAULT_MAX_SIZE_MB;
  return mb * 1024 * 1024;
}

/**
 * Validate that a file's MIME type is in the allowed whitelist.
 * Supports wildcards like "image/*" or "audio/*" as well as exact MIME types.
 */
export function validateFileType(mimeType: string): boolean {
  if (!mimeType) return false;
  const normalized = mimeType.toLowerCase().trim();
  const allowed = getAllowedFileTypes();
  return allowed.some((type) => {
    if (type.endsWith("/*")) {
      const prefix = type.slice(0, -1);
      return normalized.startsWith(prefix);
    }
    if (type.endsWith("/")) {
      return normalized.startsWith(type);
    }
    return normalized === type;
  });
}

/**
 * Validate that file size does not exceed the allowed maximum limit.
 */
export function validateFileSize(bytes: number): boolean {
  return bytes > 0 && bytes <= getMaxFileSizeBytes();
}

/**
 * Format Cloudinary upload response to a clean, standardized UploadResult.
 * Always ensures secure_url (HTTPS) is populated.
 */
function formatUploadResponse(res: UploadApiResponse, filename?: string): UploadResult {
  return {
    url: res.secure_url,
    secure_url: res.secure_url,
    public_id: res.public_id,
    format: res.format,
    resource_type: res.resource_type,
    bytes: res.bytes,
    created_at: res.created_at,
    original_filename: filename || res.original_filename,
    width: res.width,
    height: res.height,
    duration: res.duration,
  };
}

/**
 * Upload a binary buffer to Cloudinary.
 * Used for server-side file uploads, multipart form processing, and generated assets.
 */
export async function uploadBuffer(
  buffer: Buffer | Uint8Array,
  options: UploadOptions = {},
): Promise<UploadResult> {
  const client = configureCloudinary();
  const size = buffer.byteLength;

  if (!validateFileSize(size)) {
    throw new Error(
      `File size (${(size / (1024 * 1024)).toFixed(2)} MB) exceeds allowed limit of ${getMaxFileSizeBytes() / (1024 * 1024)} MB`,
    );
  }

  if (options.mimeType && !validateFileType(options.mimeType)) {
    throw new Error(
      `File type '${options.mimeType}' is not supported. Allowed types: ${getAllowedFileTypes().join(", ")}`,
    );
  }

  return new Promise((resolve, reject) => {
    const uploadStream = client.uploader.upload_stream(
      {
        folder: options.folder || "vayu-raksha/uploads",
        public_id: options.publicId,
        resource_type: options.resourceType || "auto",
        tags: options.tags || ["vayu-raksha"],
        filename_override: options.filename,
      },
      (error, result) => {
        if (error || !result) {
          return reject(error || new Error("Cloudinary upload failed with no result"));
        }
        resolve(formatUploadResponse(result, options.filename));
      },
    );

    const buf = Buffer.isBuffer(buffer) ? buffer : Buffer.from(buffer);
    uploadStream.end(buf);
  });
}

/**
 * Upload a Base64 string or Data URI to Cloudinary.
 * Used for client attachments, canvas exports, or audio wav data URLs.
 */
export async function uploadBase64(
  dataUriOrBase64: string,
  options: UploadOptions = {},
): Promise<UploadResult> {
  const client = configureCloudinary();

  let mimeType = options.mimeType;
  if (!mimeType && dataUriOrBase64.startsWith("data:")) {
    const match = dataUriOrBase64.match(/^data:([^;]+);/);
    if (match) mimeType = match[1];
  }

  if (mimeType && !validateFileType(mimeType)) {
    throw new Error(
      `File type '${mimeType}' is not supported. Allowed types: ${getAllowedFileTypes().join(", ")}`,
    );
  }

  const result = await client.uploader.upload(dataUriOrBase64, {
    folder: options.folder || "vayu-raksha/uploads",
    public_id: options.publicId,
    resource_type: options.resourceType || "auto",
    tags: options.tags || ["vayu-raksha"],
    filename_override: options.filename,
  });

  return formatUploadResponse(result, options.filename);
}

export interface CloudinaryResource {
  public_id: string;
  format: string;
  bytes: number;
  secure_url: string;
  url?: string;
  resource_type: string;
  created_at: string;
  [key: string]: any;
}

/**
 * Retrieve resource details from Cloudinary by public ID.
 */
export async function getFile(
  publicId: string,
  resourceType: "image" | "video" | "raw" = "image",
): Promise<CloudinaryResource> {
  const client = configureCloudinary();
  const res = await client.api.resource(publicId, { resource_type: resourceType });
  return res as CloudinaryResource;
}


/**
 * Delete a resource from Cloudinary by public ID.
 */
export async function deleteFile(
  publicId: string,
  resourceType: "image" | "video" | "raw" = "image",
): Promise<{ result: string }> {
  const client = configureCloudinary();
  return client.uploader.destroy(publicId, { resource_type: resourceType });
}
