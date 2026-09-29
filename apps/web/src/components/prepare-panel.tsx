"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, type FileUIPart, lastAssistantMessageIsCompleteWithApprovalResponses } from "ai";
import { clsx } from "clsx";
import { ArrowUp, FileText, Landmark, LoaderCircle, Mic, Paperclip, Search, Square, X } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";

import { AdvisoryCard } from "@/components/advisory-card";
import {
  ATTACHMENT_TYPES,
  blobToDataUrl,
  MAX_ATTACHMENT_BYTES,
  MAX_VOICE_SECONDS,
  recordingToWavUrl,
} from "@/lib/media";
import type { AgentContext, ShadowCastMessage } from "@/server/agent";

const VOICE_PROMPT = "(Voice question: answer in the language I spoke.)";

interface PreparePanelProps {
  context: AgentContext;
  suggestions: string[];
  onSelectAsset: (assetId: string) => void;
}

/**
 * The Gemini duty analyst: explains the ranking and drafts advisories that the officer approves or rejects. The
 * officer can type, speak (a voice note Gemini hears directly) or attach photos, PDFs and audio for Gemini to read.
 */
export function PreparePanel({ context, suggestions, onSelectAsset }: PreparePanelProps) {
  // One conversation per replay (the parent keys this panel by it); the map selection travels with each message.
  const [transport] = useState(
    () =>
      new DefaultChatTransport<ShadowCastMessage>({
        api: "/api/agent",
        body: { scenarioId: context.scenarioId, forecastKey: context.forecastKey },
      }),
  );
  const { messages, sendMessage, status, error, stop, addToolApprovalResponse } = useChat<ShadowCastMessage>({
    transport,
    sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithApprovalResponses,
  });
  const [input, setInput] = useState("");
  const [files, setFiles] = useState<FileUIPart[]>([]);
  const [recorder, setRecorder] = useState<MediaRecorder | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const picker = useRef<HTMLInputElement>(null);
  const busy = status === "submitted" || status === "streaming";

  const end = useRef<HTMLDivElement>(null);
  useEffect(() => {
    end.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  const send = (text: string, attachments: FileUIPart[] = files) => {
    if ((!text.trim() && attachments.length === 0) || busy) return;
    void sendMessage(
      { text: text.trim() || "(See the attachment.)", files: attachments },
      { body: { selectedAssetId: context.selectedAssetId } },
    );
    setInput("");
    setFiles([]);
  };

  const attach = async (list: FileList | null) => {
    const accepted = [...(list ?? [])].filter(
      (file) => ATTACHMENT_TYPES.some((type) => file.type.startsWith(type)) && file.size <= MAX_ATTACHMENT_BYTES,
    );
    setNotice(accepted.length < (list?.length ?? 0) ? "Photos, PDFs and audio up to 8 MB only." : null);
    const parts = await Promise.all(
      accepted.map(async (file): Promise<FileUIPart> => ({
        type: "file",
        mediaType: file.type,
        filename: file.name,
        url: await blobToDataUrl(file),
      })),
    );
    setFiles((current) => [...current, ...parts]);
    if (picker.current) picker.current.value = "";
  };

  // Record until the officer taps again (or MAX_VOICE_SECONDS), then send the note: Gemini hears it directly.
  const toggleVoice = async () => {
    if (recorder) {
      recorder.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const next = new MediaRecorder(stream);
      const chunks: Blob[] = [];
      next.ondataavailable = (event) => chunks.push(event.data);
      next.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        setRecorder(null);
        const url = await recordingToWavUrl(new Blob(chunks, { type: next.mimeType }));
        send(VOICE_PROMPT, [{ type: "file", mediaType: "audio/wav", filename: "voice-question.wav", url }]);
      };
      next.start();
      setRecorder(next);
      setNotice(null);
      setTimeout(() => next.state === "recording" && next.stop(), MAX_VOICE_SECONDS * 1000);
    } catch {
      setNotice("Microphone unavailable: allow access in the browser to ask by voice.");
    }
  };
  const submit = (event: FormEvent) => {
    event.preventDefault();
    send(input);
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto px-4 pb-3" aria-live="polite">
        {messages.length === 0 && (
          <div className="space-y-3 pt-1">
            <div className="label">Duty analyst · Gemini 3.8 Flash</div>
            <p className="text-sm leading-relaxed text-[var(--text-secondary)]">
              Ask why an asset is at risk, or have Gemini draft an advisory with officer actions and a public message in
              English, Hindi and the local language. Type, tap the microphone to ask by voice in any language, or attach
              a field photo or an IMD bulletin. Nothing is issued until you approve it.
            </p>
            <div className="flex flex-col items-start gap-2">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => send(suggestion)}
                  className="rounded-2xl border border-[var(--line)] bg-[var(--surface-2)] px-3.5 py-2.5 text-left text-sm text-[var(--text-primary)] transition-colors hover:border-[var(--line-strong)] hover:bg-[var(--surface-3)]"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={clsx(
              "flex flex-col gap-2 text-sm",
              message.role === "user" && "ml-10 self-end rounded-2xl rounded-br-md bg-[var(--surface-3)] px-3.5 py-2.5",
            )}
          >
            {message.parts.map((part, index) => {
              switch (part.type) {
                case "text":
                  return part.text === VOICE_PROMPT ? null : (
                    <p key={index} className="whitespace-pre-wrap leading-relaxed text-[var(--text-primary)]">
                      {part.text}
                    </p>
                  );
                case "file":
                  return part.mediaType.startsWith("image/") ? (
                    // A data URL chosen by the officer: next/image cannot optimise it.
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      key={index}
                      src={part.url}
                      alt={part.filename ?? "Attached photo"}
                      className="max-h-48 rounded-xl"
                    />
                  ) : part.mediaType.startsWith("audio/") ? (
                    <audio
                      key={index}
                      controls
                      src={part.url}
                      className="h-9 w-56"
                      aria-label={part.filename ?? "Voice note"}
                    />
                  ) : (
                    <span key={index} className="flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
                      <FileText className="size-3.5" /> {part.filename ?? "Document"}
                    </span>
                  );
                case "tool-officialBulletin":
                  return (
                    <p key={part.toolCallId} className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                      <Landmark className="size-3.5" />
                      {part.state === "output-available"
                        ? "Checked IMD's official bulletin"
                        : part.state === "output-error"
                          ? `IMD bulletin unavailable: ${part.errorText}`
                          : "Reading IMD's bulletin…"}
                    </p>
                  );
                case "tool-searchAssets":
                  return (
                    <p key={part.toolCallId} className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                      <Search className="size-3.5" />
                      {part.state === "output-available"
                        ? `Looked up ${part.output.total} matching assets${part.input.query ? ` for "${part.input.query}"` : ""}`
                        : part.state === "output-error"
                          ? `Asset lookup failed: ${part.errorText}`
                          : "Looking up assets…"}
                    </p>
                  );
                case "tool-issueAdvisory":
                  if (part.state === "input-streaming" || part.state === "input-available") {
                    return (
                      <p key={part.toolCallId} className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                        <LoaderCircle className="size-3.5 animate-spin" /> Drafting advisory…
                      </p>
                    );
                  }
                  if (part.state === "output-error") {
                    return (
                      <p key={part.toolCallId} className="text-xs text-red-300">
                        Issuing failed: {part.errorText}
                      </p>
                    );
                  }
                  return (
                    <AdvisoryCard
                      key={part.toolCallId}
                      advisory={part.input}
                      onSelectAsset={onSelectAsset}
                      decision={
                        part.state === "approval-requested"
                          ? {
                              state: "pending",
                              onDecide: (approved) =>
                                addToolApprovalResponse({
                                  id: part.approval.id,
                                  approved,
                                  reason: approved ? undefined : "Rejected by the officer",
                                }),
                            }
                          : part.state === "output-available"
                            ? { state: "issued", issued: part.output }
                            : part.state === "output-denied"
                              ? { state: "rejected" }
                              : { state: "deciding" }
                      }
                    />
                  );
                default:
                  return null;
              }
            })}
          </div>
        ))}
        {status === "submitted" && (
          <LoaderCircle className="size-4 animate-spin text-[var(--text-muted)]" aria-label="Thinking" />
        )}
        {error && <p className="text-xs text-red-300">Something went wrong: {error.message}</p>}
        <div ref={end} />
      </div>

      <form onSubmit={submit} className="flex flex-col gap-2 border-t border-[var(--line)] p-3">
        {(files.length > 0 || notice) && (
          <div className="flex flex-wrap items-center gap-1.5">
            {files.map((file, i) => (
              <span
                key={`${file.filename}-${i}`}
                className="flex items-center gap-1 rounded-full border border-[var(--line-strong)] py-0.5 pr-1 pl-2.5 text-xs text-[var(--text-secondary)]"
              >
                {file.filename}
                <button
                  type="button"
                  onClick={() => setFiles((current) => current.filter((_, j) => j !== i))}
                  aria-label={`Remove ${file.filename}`}
                  className="rounded-full p-0.5 hover:bg-[var(--surface-3)]"
                >
                  <X className="size-3" />
                </button>
              </span>
            ))}
            {notice && <span className="text-xs text-[var(--text-muted)]">{notice}</span>}
          </div>
        )}
        <div className="flex items-end gap-2">
          <input
            ref={picker}
            type="file"
            multiple
            accept="image/*,application/pdf,audio/*"
            onChange={(event) => void attach(event.target.files)}
            className="hidden"
          />
          <div className="flex flex-col gap-1">
            <button
              type="button"
              onClick={() => picker.current?.click()}
              disabled={busy}
              aria-label="Attach a photo, PDF or audio"
              className="btn-ghost grid size-9 place-items-center disabled:opacity-40"
            >
              <Paperclip className="size-4" />
            </button>
            <button
              type="button"
              onClick={() => void toggleVoice()}
              disabled={busy}
              aria-label={recorder ? "Stop and send the voice question" : "Ask by voice"}
              aria-pressed={recorder != null}
              className={clsx(
                "grid size-9 place-items-center disabled:opacity-40",
                recorder ? "btn-primary animate-pulse" : "btn-ghost",
              )}
            >
              <Mic className="size-4" />
            </button>
          </div>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) submit(event);
            }}
            rows={2}
            maxLength={2000}
            placeholder="Ask the duty analyst…"
            aria-label="Message the duty analyst"
            className="min-h-0 flex-1 resize-none rounded-2xl border border-[var(--line-strong)] bg-[var(--surface-2)] px-3.5 py-2.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none"
          />
          {busy ? (
            <button
              type="button"
              onClick={() => void stop()}
              aria-label="Stop"
              className="btn-ghost grid size-10 place-items-center"
            >
              <Square className="size-3.5" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim() && files.length === 0}
              aria-label="Send"
              className="btn-primary grid size-10 place-items-center disabled:opacity-40"
            >
              <ArrowUp className="size-4" />
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
