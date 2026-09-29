/**
 * Voice notes and attachments for the duty analyst. Browsers record WebM/Opus, which Gemini does not accept, so a
 * recording is decoded and re-encoded as 16 kHz mono 16-bit PCM WAV: small (32 kB/s) and understood by every speech
 * model. Photos, PDFs and audio files travel as data URLs in chat file parts.
 */

export const ATTACHMENT_TYPES = ["image/", "application/pdf", "audio/"];
export const MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024;
export const VOICE_SAMPLE_RATE = 16_000;
export const MAX_VOICE_SECONDS = 60;

/**
 * Encode mono samples in [-1, 1] as a PCM WAV file.
 *
 * @param samples Audio samples, clipped to [-1, 1].
 * @param sampleRate Samples per second.
 * @returns The WAV file bytes (44-byte RIFF header plus 16-bit little-endian samples).
 */
export function encodeWav(samples: Float32Array, sampleRate: number): ArrayBuffer {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);
  const text = (offset: number, value: string) =>
    [...value].forEach((c, i) => view.setUint8(offset + i, c.charCodeAt(0)));
  text(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  text(8, "WAVE");
  text(12, "fmt ");
  view.setUint32(16, 16, true); // PCM chunk size
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true); // byte rate
  view.setUint16(32, 2, true); // block align
  view.setUint16(34, 16, true); // bits per sample
  text(36, "data");
  view.setUint32(40, samples.length * 2, true);
  samples.forEach((sample, i) => {
    const s = Math.max(-1, Math.min(1, sample));
    view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  });
  return buffer;
}

/**
 * Turn a browser recording into a WAV data URL that can travel as a chat file part.
 *
 * @param recording The MediaRecorder output (any format the browser can decode).
 * @returns A ``data:audio/wav;base64,...`` URL.
 */
export async function recordingToWavUrl(recording: Blob): Promise<string> {
  const context = new AudioContext({ sampleRate: VOICE_SAMPLE_RATE });
  try {
    const decoded = await context.decodeAudioData(await recording.arrayBuffer());
    return await blobToDataUrl(
      new Blob([encodeWav(decoded.getChannelData(0), VOICE_SAMPLE_RATE)], { type: "audio/wav" }),
    );
  } finally {
    void context.close();
  }
}

/**
 * Read a file or blob as a data URL.
 *
 * @param blob The file.
 * @returns A ``data:<type>;base64,...`` URL.
 */
export function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });
}
