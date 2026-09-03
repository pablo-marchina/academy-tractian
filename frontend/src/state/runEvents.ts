import type { SafeEvent } from "../api/types";

export type StreamConnectionState =
  | "idle"
  | "connecting"
  | "live"
  | "reconnecting"
  | "caught_up"
  | "completed"
  | "failed";

export interface RunEventMetrics {
  events: number;
  modelCalls: number;
  toolProposals: number;
  toolCalls: number;
  policyBlocks: number;
  errors: number;
  evidenceRefs: number;
}

export function mergeSafeEvent(events: readonly SafeEvent[], incoming: SafeEvent): SafeEvent[] {
  const existingIndex = events.findIndex((event) => event.event_id === incoming.event_id);
  if (existingIndex >= 0) {
    const existing = events[existingIndex];
    if (existing.sequence === incoming.sequence && existing.event_type === incoming.event_type) {
      return [...events];
    }
    // A conflicting payload under the same event id is an integrity anomaly. Keep the first
    // observed event rather than mutating already-rendered history with contradictory data.
    return [...events];
  }

  return [...events, incoming].sort(
    (left, right) => left.sequence - right.sequence || left.event_id.localeCompare(right.event_id),
  );
}

export function deriveRunEventMetrics(events: readonly SafeEvent[]): RunEventMetrics {
  return events.reduce<RunEventMetrics>(
    (metrics, event) => {
      metrics.events += 1;
      if (event.event_type === "model_call") metrics.modelCalls += 1;
      if (event.event_type === "tool_proposal") metrics.toolProposals += 1;
      if (event.event_type === "tool_call") metrics.toolCalls += 1;
      if (event.event_type === "policy_check" && event.policy_allowed === false) {
        metrics.policyBlocks += 1;
      }
      if (event.event_type === "error" || event.failure_code) metrics.errors += 1;
      if (event.evidence_id) metrics.evidenceRefs += 1;
      return metrics;
    },
    {
      events: 0,
      modelCalls: 0,
      toolProposals: 0,
      toolCalls: 0,
      policyBlocks: 0,
      errors: 0,
      evidenceRefs: 0,
    },
  );
}

export function isRunFinished(events: readonly SafeEvent[]): boolean {
  return events.some((event) => event.event_type === "run_finished");
}

export function eventDisplayLabel(event: SafeEvent): string {
  if (event.event_type === "model_call") {
    return event.outcome ? `Model ${event.outcome}` : "Model call";
  }
  if (event.event_type === "decision") {
    return event.decision_kind ? `Decision · ${event.decision_kind}` : "Decision";
  }
  if (event.event_type === "tool_proposal") {
    return event.tool_name ? `Propose · ${event.tool_name}` : "Tool proposal";
  }
  if (event.event_type === "tool_call") {
    return event.tool_name ? `Execute · ${event.tool_name}` : "Tool call";
  }
  if (event.event_type === "policy_check") {
    const disposition = event.policy_allowed === false ? "Blocked" : "Allowed";
    return `${disposition}${event.policy_stage ? ` · ${event.policy_stage}` : ""}`;
  }
  if (event.event_type === "observation") {
    return event.evidence_id ? `Evidence · ${event.evidence_id}` : "Observation";
  }
  if (event.event_type === "final_response") {
    return event.response_mode ? `Final · ${event.response_mode}` : "Final response";
  }
  if (event.event_type === "run_finished") return "Run finished";
  return event.event_type.replaceAll("_", " ");
}
