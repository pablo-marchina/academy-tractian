import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import { submitRun } from "../api/client";
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
  const url = new URL(run.stream_path, window.location.origin);
  url.searchParams.set("after_sequence", String(afterSequence));
  return `${url.pathname}${url.search}`;
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
  const sourceRef = useRef<EventSource | null>(null);
  const lastSequenceRef = useRef(-1);
  const [accepted, setAccepted] = useState<RunAccepted | null>(null);
  const [events, setEvents] = useState<SafeEvent[]>([]);
  const [connection, setConnection] = useState<StreamConnectionState>("idle");
  const [error, setError] = useState<string | null>(null);

  const closeSource = useCallback(() => {
    sourceRef.current?.close();
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
      const source = new EventSource(
        resume ? resumedStreamPath(run, lastSequenceRef.current) : run.stream_path,
      );
      sourceRef.current = source;

      source.onopen = () => {
        setError(null);
        setConnection((current) => (current === "reconnecting" ? current : "live"));
      };

      source.addEventListener("stream_state", (message) => {
        try {
          const state = parseStreamState((message as MessageEvent<string>).data);
          if (state.run_id !== run.run_id) throw new Error("cross_run_stream_state_rejected");
          if (state.after_sequence < lastSequenceRef.current) {
            throw new Error("stream_cursor_regression_rejected");
          }
          lastSequenceRef.current = state.after_sequence;
          setConnection("caught_up");
        } catch (cause) {
          source.close();
          if (sourceRef.current === source) sourceRef.current = null;
          setConnection("failed");
          setError(cause instanceof Error ? cause.message : "invalid_stream_state");
        }
      });

      source.addEventListener("trace_event", (message) => {
        try {
          const incoming = parseSafeEvent((message as MessageEvent<string>).data);
          if (incoming.run_id !== run.run_id) throw new Error("cross_run_event_rejected");
          lastSequenceRef.current = Math.max(lastSequenceRef.current, incoming.sequence);
          setConnection((current) => (current === "caught_up" ? "live" : current));
          setEvents((current) => {
            const next = mergeSafeEvent(current, incoming);
            if (isRunFinished(next)) {
              source.close();
              if (sourceRef.current === source) sourceRef.current = null;
              setConnection("completed");
              void refreshTerminalState(run);
            }
            return next;
          });
        } catch (cause) {
          source.close();
          if (sourceRef.current === source) sourceRef.current = null;
          setConnection("failed");
          setError(cause instanceof Error ? cause.message : "invalid_stream_event");
        }
      });

      source.onerror = () => {
        if (sourceRef.current === source) {
          setConnection((current) => (current === "completed" ? current : "reconnecting"));
        }
      };
    },
    [closeSource, refreshTerminalState],
  );

  const follow = useCallback(
    (run: RunAccepted) => {
      closeSource();
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
    lastSequenceRef.current = -1;
    setAccepted(null);
    setEvents([]);
    setConnection("idle");
    setError(null);
  }, [closeSource]);

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