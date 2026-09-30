import { NextRequest, NextResponse } from "next/server";
import {
  uploadBuffer,
  uploadBase64,
  getFile,
  deleteFile,
  validateFileType,
  validateFileSize,
  getAllowedFileTypes,
  getMaxFileSizeBytes,
  getCloudinaryConfig,
} from "@/lib/storage";

export const maxDuration = 60;

/**
 * GET /api/upload
 * - If ?public_id is provided: retrieves the asset details from Cloudinary.
 * - Otherwise: returns storage health, configuration, and constraints (no secrets exposed).
 */
export async function GET(request: NextRequest) {
  try {
    const publicId = request.nextUrl.searchParams.get("public_id");
    const resourceType = (request.nextUrl.searchParams.get("resource_type") || "image") as
      | "image"
      | "video"
      | "raw";

    if (publicId) {
      const file = await getFile(publicId, resourceType);
      return NextResponse.json({
        success: true,
        file: {
          public_id: file.public_id,
          format: file.format,
          bytes: file.bytes,
          secure_url: file.secure_url,
          url: file.secure_url,
          resource_type: file.resource_type,
          created_at: file.created_at,
        },
      });
    }

    const config = getCloudinaryConfig();
    return NextResponse.json({
      status: "ok",
      provider: "cloudinary",
      cloud_name: config.cloudName,
      allowed_types: getAllowedFileTypes(),
      max_size_mb: getMaxFileSizeBytes() / (1024 * 1024),
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to retrieve storage status";
    return NextResponse.json({ success: false, error: message }, { status: 400 });
  }
}

/**
 * POST /api/upload
 * Accepts either:
 * 1. multipart/form-data with a `file` or `files` field.
 * 2. application/json with `{ file: "<data_url_or_base64>", filename?: string, mimeType?: string, folder?: string }`.
 *
 * Always returns `secure_url` on success.
 */
export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get("content-type") || "";

    // 1. Handle multipart/form-data
    if (contentType.includes("multipart/form-data")) {
      const formData = await request.formData();
      const files = formData.getAll("files") as File[];
      const singleFile = formData.get("file") as File | null;
      const folder = (formData.get("folder") as string) || undefined;

      const uploadList: File[] = files.length > 0 ? files : singleFile ? [singleFile] : [];

      if (uploadList.length === 0) {
        return NextResponse.json(
          { success: false, error: "No file provided in form data ('file' or 'files' field required)" },
          { status: 400 },
        );
      }

      // Validate all files before uploading
      for (const file of uploadList) {
        if (!validateFileType(file.type)) {
          return NextResponse.json(
            {
              success: false,
              error: `Unsupported file type '${file.type}' for file '${file.name}'. Allowed types: ${getAllowedFileTypes().join(", ")}`,
            },
            { status: 400 },
          );
        }
        if (!validateFileSize(file.size)) {
          return NextResponse.json(
            {
              success: false,
              error: `File '${file.name}' (${(file.size / (1024 * 1024)).toFixed(2)} MB) exceeds size limit of ${getMaxFileSizeBytes() / (1024 * 1024)} MB`,
            },
            { status: 400 },
          );
        }
      }

      const results = await Promise.all(
        uploadList.map(async (file) => {
          const buffer = Buffer.from(await file.arrayBuffer());
          return uploadBuffer(buffer, {
            filename: file.name,
            mimeType: file.type,
            folder,
          });
        }),
      );

      if (results.length === 1) {
        return NextResponse.json({
          success: true,
          url: results[0].secure_url,
          secure_url: results[0].secure_url,
          file: results[0],
        });
      }

      return NextResponse.json({
        success: true,
        files: results,
      });
    }

    // 2. Handle JSON payload (base64 / data URL)
    if (contentType.includes("application/json")) {
      const body = await request.json().catch(() => null);
      if (!body || !body.file) {
        return NextResponse.json(
          { success: false, error: "Invalid JSON. 'file' field (base64 string or data URL) is required" },
          { status: 400 },
        );
      }

      const result = await uploadBase64(body.file, {
        filename: body.filename,
        mimeType: body.mimeType,
        folder: body.folder,
      });

      return NextResponse.json({
        success: true,
        url: result.secure_url,
        secure_url: result.secure_url,
        file: result,
      });
    }

    return NextResponse.json(
      {
        success: false,
        error: "Unsupported Content-Type. Please use multipart/form-data or application/json",
      },
      { status: 415 },
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : "File upload failed";
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}

/**
 * DELETE /api/upload
 * Deletes an uploaded asset from Cloudinary by public ID.
 */
export async function DELETE(request: NextRequest) {
  try {
    let publicId = request.nextUrl.searchParams.get("public_id");
    let resourceType = (request.nextUrl.searchParams.get("resource_type") || "image") as
      | "image"
      | "video"
      | "raw";

    if (!publicId && request.headers.get("content-type")?.includes("application/json")) {
      const body = await request.json().catch(() => null);
      if (body?.public_id) {
        publicId = body.public_id;
        if (body.resource_type) resourceType = body.resource_type;
      }
    }

    if (!publicId) {
      return NextResponse.json(
        { success: false, error: "Missing 'public_id' parameter" },
        { status: 400 },
      );
    }

    const result = await deleteFile(publicId, resourceType);
    return NextResponse.json({ success: true, result });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Deletion failed";
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
