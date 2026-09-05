import { authorizationHeaders } from "./auth";

export interface SseMessage {
  event: string;
  id: string | null;
  data: string;
}

export class SseHttpError extends Error {
  readonly status: number;

  constructor(status: number) {
    super(`sse_http_${status}`);
    this.name = "SseHttpError";
    this.status = status;
  }
}

export class SseFrameDecoder {
  private buffer = "";
  private eventName = "message";
  private eventId: string | null = null;
  private dataLines: string[] = [];
  private readonly emit: (message: SseMessage) => void;

  constructor(emit: (message: SseMessage) => void) {
    this.emit = emit;
  }

  push(chunk: string): void {
    this.buffer += chunk;
    while (true) {
      const newline = this.buffer.indexOf("\n");
      if (newline < 0) return;
      const rawLine = this.buffer.slice(0, newline);
      this.buffer = this.buffer.slice(newline + 1);
      this.handleLine(rawLine.endsWith("\r") ? rawLine.slice(0, -1) : rawLine);
    }
  }

  finish(): void {
    if (this.buffer.length > 0 || this.dataLines.length > 0) {
      throw new Error("truncated_sse_frame");
    }
  }

  private handleLine(line: string): void {
    if (line === "") {
      this.dispatch();
      return;
    }
    if (line.startsWith(":")) return;

    const separator = line.indexOf(":");
    const field = separator < 0 ? line : line.slice(0, separator);
    let value = separator < 0 ? "" : line.slice(separator + 1);
    if (value.startsWith(" ")) value = value.slice(1);

    if (field === "event") {
      this.eventName = value || "message";
    } else if (field === "data") {
      this.dataLines.push(value);
    } else if (field === "id" && !value.includes("\0")) {
      this.eventId = value;
    }
  }

  private dispatch(): void {
    if (this.dataLines.length > 0) {
      this.emit({
        event: this.eventName,
        id: this.eventId,
        data: this.dataLines.join("\n"),
      });
    }
    this.eventName = "message";
    this.eventId = null;
    this.dataLines = [];
  }
}

export interface StreamSseOptions {
  signal: AbortSignal;
  onOpen?: () => void;
  onMessage: (message: SseMessage) => void;
}

export async function streamSse(url: string, options: StreamSseOptions): Promise<void> {
  const authHeaders = await authorizationHeaders();
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "text/event-stream",
      "Cache-Control": "no-cache",
      ...authHeaders,
    },
    cache: "no-store",
    credentials: "omit",
    signal: options.signal,
  });

  if (!response.ok) throw new SseHttpError(response.status);
  const contentType = response.headers.get("content-type")?.toLowerCase() ?? "";
  if (!contentType.includes("text/event-stream")) {
    throw new Error("invalid_sse_content_type");
  }
  if (response.body === null) throw new Error("sse_body_unavailable");

  options.onOpen?.();
  const reader = response.body.getReader();
  const textDecoder = new TextDecoder("utf-8", { fatal: true });
  const frameDecoder = new SseFrameDecoder(options.onMessage);

  while (true) {
    const result = await reader.read();
    if (result.done) break;
    frameDecoder.push(textDecoder.decode(result.value, { stream: true }));
  }
  const tail = textDecoder.decode();
  if (tail) frameDecoder.push(tail);
  frameDecoder.finish();
}
