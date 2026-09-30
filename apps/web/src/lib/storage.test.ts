import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { v2 as cloudinary } from "cloudinary";
import {
  parseCloudinarySecret,
  getCloudinaryConfig,
  configureCloudinary,
  getAllowedFileTypes,
  getMaxFileSizeBytes,
  validateFileType,
  validateFileSize,
  uploadBuffer,
  uploadBase64,
  getFile,
  deleteFile,
  DEFAULT_ALLOWED_TYPES,
  DEFAULT_MAX_SIZE_MB,
} from "./storage";

describe("Cloudinary Storage Implementation", () => {
  const originalEnv = { ...process.env };

  beforeEach(() => {
    process.env = { ...originalEnv };
    process.env.CLOUDINARY_CLOUD_NAME = "test-cloud";
    process.env.CLOUDINARY_API_KEY = "test-key";
    process.env.CLOUDINARY_API_SECRET = "test-secret";
    delete process.env.CLOUDINARY_URL;
    delete process.env.ALLOWED_FILE_TYPES;
    delete process.env.MAX_FILE_SIZE_MB;
  });

  afterEach(() => {
    process.env = originalEnv;
    vi.restoreAllMocks();
  });

  describe("parseCloudinarySecret", () => {
    it("returns plain secret unchanged", () => {
      expect(parseCloudinarySecret("mySecretKey123")).toBe("mySecretKey123");
    });

    it("extracts secret from CLOUDINARY_URL connection string with prefix", () => {
      const input = "CLOUDINARY_URL=cloudinary://145764614276676:ey_K80B4FsA-4VGG_ICYCQl9hMY@x9sncqcz";
      expect(parseCloudinarySecret(input)).toBe("ey_K80B4FsA-4VGG_ICYCQl9hMY");
    });

    it("extracts secret from cloudinary:// url format without prefix", () => {
      const input = "cloudinary://123456:secret_abc_123@mycloud";
      expect(parseCloudinarySecret(input)).toBe("secret_abc_123");
    });

    it("returns empty string when secret is undefined or empty", () => {
      expect(parseCloudinarySecret(undefined)).toBe("");
      expect(parseCloudinarySecret("")).toBe("");
      expect(parseCloudinarySecret("   ")).toBe("");
    });
  });

  describe("getCloudinaryConfig", () => {
    it("returns config from individual environment variables", () => {
      process.env.CLOUDINARY_CLOUD_NAME = "x9sncqcz";
      process.env.CLOUDINARY_API_KEY = "145764614276676";
      process.env.CLOUDINARY_API_SECRET = "ey_K80B4FsA-4VGG_ICYCQl9hMY";

      const config = getCloudinaryConfig();
      expect(config).toEqual({
        cloudName: "x9sncqcz",
        apiKey: "145764614276676",
        apiSecret: "ey_K80B4FsA-4VGG_ICYCQl9hMY",
        secure: true,
      });
    });

    it("handles CLOUDINARY_API_SECRET provided as CLOUDINARY_URL", () => {
      process.env.CLOUDINARY_CLOUD_NAME = "x9sncqcz";
      process.env.CLOUDINARY_API_KEY = "145764614276676";
      process.env.CLOUDINARY_API_SECRET =
        "CLOUDINARY_URL=cloudinary://145764614276676:ey_K80B4FsA-4VGG_ICYCQl9hMY@x9sncqcz";

      const config = getCloudinaryConfig();
      expect(config).toEqual({
        cloudName: "x9sncqcz",
        apiKey: "145764614276676",
        apiSecret: "ey_K80B4FsA-4VGG_ICYCQl9hMY",
        secure: true,
      });
    });

    it("falls back to CLOUDINARY_URL if separate vars are missing", () => {
      delete process.env.CLOUDINARY_CLOUD_NAME;
      delete process.env.CLOUDINARY_API_KEY;
      delete process.env.CLOUDINARY_API_SECRET;
      process.env.CLOUDINARY_URL = "cloudinary://urlKey:urlSecret@urlCloud";

      const config = getCloudinaryConfig();
      expect(config).toEqual({
        cloudName: "urlCloud",
        apiKey: "urlKey",
        apiSecret: "urlSecret",
        secure: true,
      });
    });

    it("throws an error when required credentials are missing", () => {
      delete process.env.CLOUDINARY_CLOUD_NAME;
      delete process.env.CLOUDINARY_API_KEY;
      delete process.env.CLOUDINARY_API_SECRET;
      delete process.env.CLOUDINARY_URL;

      expect(() => getCloudinaryConfig()).toThrow("Missing Cloudinary credentials");
    });
  });

  describe("configureCloudinary", () => {
    it("calls cloudinary.config with the parsed credentials", () => {
      const spy = vi.spyOn(cloudinary, "config");
      configureCloudinary();
      expect(spy).toHaveBeenCalledWith({
        cloud_name: "test-cloud",
        api_key: "test-key",
        api_secret: "test-secret",
        secure: true,
      });
    });
  });

  describe("File type and size validation", () => {
    it("returns default allowed types when env is unset", () => {
      expect(getAllowedFileTypes()).toEqual(DEFAULT_ALLOWED_TYPES);
    });

    it("parses ALLOWED_FILE_TYPES from environment variable", () => {
      process.env.ALLOWED_FILE_TYPES = "image/png, image/jpeg, application/pdf";
      expect(getAllowedFileTypes()).toEqual(["image/png", "image/jpeg", "application/pdf"]);
    });

    it("validates allowed MIME types accurately", () => {
      expect(validateFileType("image/png")).toBe(true);
      expect(validateFileType("image/jpeg")).toBe(true);
      expect(validateFileType("image/webp")).toBe(true);
      expect(validateFileType("application/pdf")).toBe(true);
      expect(validateFileType("audio/wav")).toBe(true);
      expect(validateFileType("audio/webm")).toBe(true);

      // Disallowed or malformed types
      expect(validateFileType("application/x-msdownload")).toBe(false);
      expect(validateFileType("text/html")).toBe(false);
      expect(validateFileType("")).toBe(false);
    });

    it("supports wildcard and trailing slash prefix type checking", () => {
      process.env.ALLOWED_FILE_TYPES = "image/*, audio/, application/pdf";
      expect(validateFileType("image/png")).toBe(true);
      expect(validateFileType("image/gif")).toBe(true);
      expect(validateFileType("audio/wav")).toBe(true);
      expect(validateFileType("audio/mp3")).toBe(true);
      expect(validateFileType("application/pdf")).toBe(true);
      expect(validateFileType("video/mp4")).toBe(false);
    });

    it("returns default max file size in bytes (10MB)", () => {
      expect(getMaxFileSizeBytes()).toBe(DEFAULT_MAX_SIZE_MB * 1024 * 1024);
    });

    it("parses MAX_FILE_SIZE_MB from environment", () => {
      process.env.MAX_FILE_SIZE_MB = "25";
      expect(getMaxFileSizeBytes()).toBe(25 * 1024 * 1024);
    });

    it("validates file sizes within limit", () => {
      expect(validateFileSize(1024)).toBe(true);
      expect(validateFileSize(10 * 1024 * 1024)).toBe(true);
      expect(validateFileSize(10 * 1024 * 1024 + 1)).toBe(false);
      expect(validateFileSize(0)).toBe(false);
      expect(validateFileSize(-1)).toBe(false);
    });
  });

  describe("uploadBuffer", () => {
    it("uploads buffer stream and returns formatted UploadResult with secure_url", async () => {
      const mockResult = {
        secure_url: "https://res.cloudinary.com/test-cloud/image/upload/v1/sample.png",
        public_id: "vayu-raksha/uploads/sample",
        format: "png",
        resource_type: "image",
        bytes: 1024,
        created_at: "2026-09-30T10:00:00Z",
        original_filename: "test.png",
        width: 400,
        height: 300,
      };

      vi.spyOn(cloudinary.uploader as any, "upload_stream").mockImplementation((...args: any[]) => {
        const callback = typeof args[0] === "function" ? args[0] : args[1];
        return {
          end: (_buf: Buffer) => {
            callback?.(undefined, mockResult);
          },
        };
      });

      const buffer = Buffer.from("dummy-image-content");
      const result = await uploadBuffer(buffer, {
        filename: "test.png",
        mimeType: "image/png",
      });

      expect(result.secure_url).toBe("https://res.cloudinary.com/test-cloud/image/upload/v1/sample.png");
      expect(result.url).toBe("https://res.cloudinary.com/test-cloud/image/upload/v1/sample.png");
      expect(result.public_id).toBe("vayu-raksha/uploads/sample");
      expect(result.format).toBe("png");
      expect(result.bytes).toBe(1024);
    });

    it("rejects buffer exceeding maximum allowed file size", async () => {
      process.env.MAX_FILE_SIZE_MB = "0.001"; // ~1KB
      const largeBuffer = Buffer.alloc(2000);

      await expect(uploadBuffer(largeBuffer)).rejects.toThrow("exceeds allowed limit");
    });

    it("rejects unsupported MIME type", async () => {
      const buffer = Buffer.from("malicious executable");
      await expect(
        uploadBuffer(buffer, { mimeType: "application/x-dosexec" }),
      ).rejects.toThrow("File type 'application/x-dosexec' is not supported");
    });

    it("rejects when upload stream yields error", async () => {
      vi.spyOn(cloudinary.uploader as any, "upload_stream").mockImplementation((...args: any[]) => {
        const callback = typeof args[0] === "function" ? args[0] : args[1];
        return {
          end: () => {
            callback?.(new Error("Cloudinary connection failed"), undefined);
          },
        };
      });

      const buffer = Buffer.from("valid content");
      await expect(uploadBuffer(buffer, { mimeType: "image/png" })).rejects.toThrow("Cloudinary connection failed");
    });
  });

  describe("uploadBase64", () => {
    it("uploads base64 data URI and returns secure_url", async () => {
      const mockResult = {
        secure_url: "https://res.cloudinary.com/test-cloud/image/upload/v1/avatar.jpg",
        public_id: "vayu-raksha/uploads/avatar",
        format: "jpg",
        resource_type: "image",
        bytes: 2048,
        created_at: "2026-09-30T10:00:00Z",
        original_filename: "avatar.jpg",
      };

      vi.spyOn(cloudinary.uploader, "upload").mockResolvedValue(mockResult as any);

      const dataUri = "data:image/jpeg;base64,/9j/4AAQSkZJRg==";
      const result = await uploadBase64(dataUri, { filename: "avatar.jpg" });

      expect(result.secure_url).toBe("https://res.cloudinary.com/test-cloud/image/upload/v1/avatar.jpg");
      expect(result.public_id).toBe("vayu-raksha/uploads/avatar");
    });

    it("rejects data URI with unsupported MIME type", async () => {
      const invalidDataUri = "data:application/x-msdownload;base64,TVqQAAMAAAAEAAAA";
      await expect(uploadBase64(invalidDataUri)).rejects.toThrow("not supported");
    });
  });

  describe("getFile and deleteFile", () => {
    it("calls cloudinary.api.resource for retrieval", async () => {
      const mockResource = {
        public_id: "vayu-raksha/uploads/sample",
        format: "png",
        bytes: 1024,
        secure_url: "https://res.cloudinary.com/test-cloud/image/upload/v1/sample.png",
        url: "https://res.cloudinary.com/test-cloud/image/upload/v1/sample.png",
        resource_type: "image",
        created_at: "2026-09-30T10:00:00Z",
      };
      vi.spyOn(cloudinary.api as any, "resource").mockResolvedValue(mockResource);

      const file = await getFile("vayu-raksha/uploads/sample");
      expect(file.public_id).toBe("vayu-raksha/uploads/sample");
      expect(file.secure_url).toBe("https://res.cloudinary.com/test-cloud/image/upload/v1/sample.png");
    });

    it("calls cloudinary.uploader.destroy for deletion", async () => {
      vi.spyOn(cloudinary.uploader as any, "destroy").mockResolvedValue({ result: "ok" });

      const res = await deleteFile("vayu-raksha/uploads/sample");
      expect(res.result).toBe("ok");
    });
  });
});

