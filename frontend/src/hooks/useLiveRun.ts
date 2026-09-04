import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import { apiUrl } from "../api/baseUrl";
import { submitRun } from "../api/client";
import { SseHttpError, streamSse, type SseMessage } from "../api/sse";
import type { RunAccepted, SafeEvent } from "../api/types";
import {
  isRunFinished,
  mergeSafeEvent,
  type StreamConnectionState,
} from "../state/runEvents";

interface StreamStateMessage {
  run_id: string;
  state: "caught_up";
  after_sequence: number;
}

function parseStreamState(value: string): StreamStateMessage {
  const parsed = JSON.parse(value) as Partial<StreamStateMessage>;
  if (
    typeof parsed.run_id !== "string" ||
    parsed.state !== "caught_up" ||
    typeof parsed.after_sequence !== "number"
  ) {
    throw new Error("invalid_stream_state");
  }
  return parsed as StreamStateMessage;
}

function parseSafeEvent(value: string): SafeEvent {
  const parsed = JSON.parse(value) as Partial<SafeEvent>;
  if (
    typeof parsed.event_id !== "string" ||
    typeof parsed.run_id !== "string" ||
    typeof parsed.sequence !== "number" ||
    typeof parsed.event_type !== "string" ||
    typeof parsed.origin !== "string"
  ) {
    throw new Error("invalid_safe_event");
  }
  return parsed as SafeEvent;
}

function resumedStreamPath(run: RunAccepted, afterSequence: number): string {
  const url = new URL(apiUrl(run.stream_path), window.location.origin);
  url.searchParams.set("after_sequence", String(afterSequence));
  return url.toString();
}

function isAbortError(cause: unknown): boolean {
  return cause instanceof Error && cause.name === "AbortError";
}

function isTerminalStreamFailure(cause: unknown): boolean {
  if (cause instanceof SseHttpError) return [400, 401, 403, 404].includes(cause.status);
  return cause instanceof Error && [
    "invalid_sse_content_type",
    "sse_body_unavailable",
    "truncated_sse_frame",
  ].includes(cause.message);
}

export interface LiveRunState {
  accepted: RunAccepted | null;
  events: SafeEvent[];
  connection: StreamConnectionState;
  error: string | null;
  submitting: boolean;
  submit: (userRequest: string) => Promise<void>;
  follow: (run: RunAccepted) => void;
  clear: () => void;
}

export function useLiveRun(): LiveRunState {
  const queryClient = useQueryClient();
  const sourceRef = useRef<AbortController | null>(null);
  const completedRef = useRef(false);
  const lastSequenceRef = useRef(-1);
  const [accepted, setAccepted] = useState<RunAccepted | null>(null);
  const [events, setEvents] = useState<SafeEvent[]>([]);
  const [connection, setConnection] = useState<StreamConnectionState>("idle");
  const [error, setError] = useState<string | null>(null);

  const closeSource = useCallback(() => {
    sourceRef.current?.abort();
    sourceRef.current = null;
  }, []);

  const refreshTerminalState = useCallback(
    async (run: RunAccepted) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["run", run.run_id] }),
        queryClient.invalidateQueries({ queryKey: ["execution", run.run_id] }),
        queryClient.invalidateQueries({ queryKey: ["evaluation", run.run_id] }),
      ]);
    },
    [queryClient],
  );

  const connect = useCallback(
    (run: RunAccepted, resume = false) => {
      closeSource();
      setConnection(resume ? "reconnecting" : "connecting");
      const controller = new AbortController();
      sourceRef.current = controller;
      const target = resume
        ? resumedStreamPath(run, lastSequenceRef.current)
        : apiUrl(run.stream_path);

      const failIntegrity = (cause: unknown) => {
        controller.abort();
        if (sourceRef.current === controller) sourceRef.current = null;
        setConnection("failed");
        setError(cause instanceof Error ? cause.message : "invalid_stream_event");
      };

      const onMessage = (message: SseMessage) => {
        try {
          if (message.event === "stream_state") {
            if (message.id !== null) throw new Error("stream_state_id_forbidden");
            const state = parseStreamState(message.data);
            if (state.run_id !== run.run_id) throw new Error("cross_run_stream_state_rejected");
            if (state.after_sequence < lastSequenceRef.current) {
              throw new Error("stream_cursor_regression_rejected");
            }
            lastSequenceRef.current = state.after_sequence;
            setConnection("caught_up");
            return;
          }

          if (message.event !== "trace_event") {
            throw new Error("unknown_sse_event_rejected");
          }
          const incoming = parseSafeEvent(message.data);
          if (incoming.run_id !== run.run_id) throw new Error("cross_run_event_rejected");
          if (message.id !== null && message.id !== incoming.event_id) {
            throw new Error("sse_event_id_mismatch");
          }
          lastSequenceRef.current = Math.max(lastSequenceRef.current, incoming.sequence);
          setConnection((current) => (current === "caught_up" ? "live" : current));
          setEvents((current) => {
            const next = mergeSafeEvent(current, incoming);
            if (isRunFinished(next)) {
              completedRef.current = true;
              controller.abort();
              if (sourceRef.current === controller) sourceRef.current = null;
              setConnection("completed");
              void refreshTerminalState(run);
            }
            return next;
          });
        } catch (cause) {
          failIntegrity(cause);
        }
      };

      void streamSse(target, {
        signal: controller.signal,
        onOpen: () => {
          if (sourceRef.current !== controller) return;
          setError(null);
          setConnection((current) => (current === "reconnecting" ? current : "live"));
        },
        onMessage,
      })
        .then(() => {
          if (sourceRef.current !== controller) return;
          sourceRef.current = null;
          if (!completedRef.current) setConnection("reconnecting");
        })
        .catch((cause: unknown) => {
          if (isAbortError(cause) || sourceRef.current !== controller) return;
          sourceRef.current = null;
          if (isTerminalStreamFailure(cause)) {
            setConnection("failed");
            setError(cause instanceof Error ? cause.message : "stream_failed");
            return;
          }
          if (!completedRef.current) setConnection("reconnecting");
        });
    },
    [closeSource, refreshTerminalState],
  );

  const follow = useCallback(
    (run: RunAccepted) => {
      closeSource();
      completedRef.current = false;
      lastSequenceRef.current = -1;
      setAccepted(run);
      setEvents([]);
      setError(null);
      connect(run);
    },
    [closeSource, connect],
  );

  const mutation = useMutation({
    mutationFn: submitRun,
    onSuccess: follow,
    onError: (cause) => {
      setConnection("failed");
      setError(cause instanceof Error ? cause.message : "run_submission_failed");
    },
  });

  const submit = useCallback(
    async (userRequest: string) => {
      closeSource();
      completedRef.current = false;
      lastSequenceRef.current = -1;
      setAccepted(null);
      setEvents([]);
      setError(null);
      setConnection("connecting");
      await mutation.mutateAsync(userRequest);
    },
    [closeSource, mutation],
  );

  const clear = useCallback(() => {
    closeSource();
    completedRef.current = false;
    lastSequenceRef.current = -1;
    setAccepted(null);
    setEvents([]);
    setConnection("idle");
    setError(null);
  }, [closeSource]);

  useEffect(() => {
    if (
      !accepted ||
      connection !== "reconnecting" ||
      sourceRef.current !== null ||
      !navigator.onLine
    ) {
      return;
    }
    const timer = window.setTimeout(() => connect(accepted, true), 350);
    return () => window.clearTimeout(timer);
  }, [accepted, connect, connection]);

  useEffect(() => {
    const handleOffline = () => {
      if (!accepted || connection === "completed" || connection === "failed") return;
      closeSource();
      setConnection("reconnecting");
    };
    const handleOnline = () => {
      if (!accepted || connection !== "reconnecting" || sourceRef.current !== null) return;
      connect(accepted, true);
    };

    window.addEventListener("offline", handleOffline);
    window.addEventListener("online", handleOnline);
    return () => {
      window.removeEventListener("offline", handleOffline);
      window.removeEventListener("online", handleOnline);
    };
  }, [accepted, closeSource, connect, connection]);

  useEffect(() => closeSource, [closeSource]);

  return {
    accepted,
    events,
    connection,
    error,
    submitting: mutation.isPending,
    submit,
    follow,
    clear,
  };
}
