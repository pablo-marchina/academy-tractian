import { describe, expect, it } from "vitest";

import { SseFrameDecoder, type SseMessage } from "./sse";

describe("fetch SSE frame decoder", () => {
  it("decodes CRLF, comments, ids and multi-line data across chunks", () => {
    const messages: SseMessage[] = [];
    const decoder = new SseFrameDecoder((message) => messages.push(message));

    decoder.push(": keepalive\r\n");
    decoder.push("id: run_abc:1\r\nevent: trace_event\r\ndata: {\"a\":1}\r\n");
    decoder.push("data: {\"b\":2}\r\n\r\n");
    decoder.finish();

    expect(messages).toEqual([
      {
        event: "trace_event",
        id: "run_abc:1",
        data: '{"a":1}\n{"b":2}',
      },
    ]);
  });

  it("defaults to message events and ignores unsupported SSE fields", () => {
    const messages: SseMessage[] = [];
    const decoder = new SseFrameDecoder((message) => messages.push(message));
    decoder.push("retry: 1000\ndata: payload\n\n");
    decoder.finish();
    expect(messages).toEqual([{ event: "message", id: null, data: "payload" }]);
  });

  it("rejects a stream that ends with an unterminated frame", () => {
    const decoder = new SseFrameDecoder(() => undefined);
    decoder.push("event: trace_event\ndata: partial");
    expect(() => decoder.finish()).toThrow("truncated_sse_frame");
  });

  it("does not dispatch comment-only frames", () => {
    const messages: SseMessage[] = [];
    const decoder = new SseFrameDecoder((message) => messages.push(message));
    decoder.push(": keepalive\n\n");
    decoder.finish();
    expect(messages).toEqual([]);
  });
});
