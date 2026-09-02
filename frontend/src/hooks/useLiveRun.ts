import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import { submitRun } from "../api/client";
import type { RunAccepted, SafeEvent } from "../api/types";
import {
  isRunFinished,
  mergeSafeEvent,
  type StreamConnectionState,
} from "../state/runEvents";

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

export interface LiveRunState {
  accepted: RunAccepted | null;
  events: SafeEvent[];
  connection: StreamConnectionState;
  error: string | null;
  submitting: boolean;
  submit: (userRequest: string) => Promise<void>;
  clear: () => void;
}

export function useLiveRun(): LiveRunState {
  const queryClient = useQueryClient();
  const sourceRef = useRef<EventSource | null>(null);
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
    (run: RunAccepted) => {
      closeSource();
      setConnection("connecting");
      const source = new EventSource(run.stream_path);
      sourceRef.current = source;

      source.onopen = () => {
        setError(null);
        setConnection("live");
      };

      source.addEventListener("trace_event", (message) => {
        try {
          const incoming = parseSafeEvent((message as MessageEvent<string>).data);
          if (incoming.run_id !== run.run_id) {
            throw new Error("cross_run_event_rejected");
          }
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
        // EventSource reconnects automatically and carries Last-Event-ID. Do not synthesize
        // progress while disconnected; the persisted server cursor will catch up real events.
        if (sourceRef.current === source) {
          setConnection((current) => (current === "completed" ? current : "reconnecting"));
        }
      };
    },
    [closeSource, refreshTerminalState],
  );

  const mutation = useMutation({
    mutationFn: submitRun,
    onSuccess: (run) => {
      setAccepted(run);
      setEvents([]);
      setError(null);
      connect(run);
    },
    onError: (cause) => {
      setConnection("failed");
      setError(cause instanceof Error ? cause.message : "run_submission_failed");
    },
  });

  const submit = useCallback(
    async (userRequest: string) => {
      closeSource();
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
    setAccepted(null);
    setEvents([]);
    setConnection("idle");
    setError(null);
  }, [closeSource]);

  useEffect(() => closeSource, [closeSource]);

  return {
    accepted,
    events,
    connection,
    error,
    submitting: mutation.isPending,
    submit,
    clear,
  };
}
