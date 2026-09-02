import { describe, expect, it } from "vitest";

import type { SafeEvent } from "../api/types";
import {
  deriveRunEventMetrics,
  isRunFinished,
  mergeSafeEvent,
} from "./runEvents";

function event(overrides: Partial<SafeEvent> = {}): SafeEvent {
  return {
    event_id: "run_abc:0",
    run_id: "run_abc",
    sequence: 0,
    event_type: "run_started",
    origin: "system",
    timestamp: null,
    tool_name: null,
    decision_kind: null,
    provider_id: null,
    model_id: null,
    route_id: null,
    live_call: null,
    outcome: null,
    failure_code: null,
    latency_ms: null,
    turn_index: null,
    tool_call_count: null,
    argument_names: "",
    method: null,
    path_template: null,
    tool_kind: null,
    status_code: null,
    policy_stage: null,
    policy_allowed: null,
    policy_contained: null,
    policy_violation: null,
    evidence_id: null,
    reason_code: null,
    response_mode: null,
    message: null,
    ...overrides,
  };
}

describe("mergeSafeEvent", () => {
  it("orders out-of-order deliveries by canonical sequence", () => {
    const second = event({ event_id: "run_abc:1", sequence: 1, event_type: "decision" });
    const first = event();
    expect(mergeSafeEvent([second], first).map((item) => item.sequence)).toEqual([0, 1]);
  });

  it("deduplicates transport replay by event id", () => {
    const first = event();
    const merged = mergeSafeEvent([first], { ...first });
    expect(merged).toHaveLength(1);
    expect(merged[0]).toEqual(first);
  });

  it("does not rewrite history when the same event id arrives with conflicting semantics", () => {
    const first = event();
    const conflict = event({ event_type: "tool_call", tool_name: "get_asset" });
    const merged = mergeSafeEvent([first], conflict);
    expect(merged).toHaveLength(1);
    expect(merged[0].event_type).toBe("run_started");
  });
});

describe("derived live metrics", () => {
  it("counts only real safe event semantics", () => {
    const events = [
      event(),
      event({ event_id: "run_abc:1", sequence: 1, event_type: "model_call" }),
      event({ event_id: "run_abc:2", sequence: 2, event_type: "tool_proposal", tool_name: "get_asset" }),
      event({ event_id: "run_abc:3", sequence: 3, event_type: "policy_check", policy_allowed: false }),
      event({ event_id: "run_abc:4", sequence: 4, event_type: "tool_call", tool_name: "get_asset" }),
      event({ event_id: "run_abc:5", sequence: 5, event_type: "observation", evidence_id: "EV-1" }),
      event({ event_id: "run_abc:6", sequence: 6, event_type: "error", failure_code: "CLIENT_FAILURE" }),
    ];

    expect(deriveRunEventMetrics(events)).toEqual({
      events: 7,
      modelCalls: 1,
      toolProposals: 1,
      toolCalls: 1,
      policyBlocks: 1,
      errors: 1,
      evidenceRefs: 1,
    });
  });

  it("marks terminal state only from a real run_finished event", () => {
    expect(isRunFinished([event({ event_type: "final_response" })])).toBe(false);
    expect(
      isRunFinished([
        event(),
        event({ event_id: "run_abc:1", sequence: 1, event_type: "run_finished" }),
      ]),
    ).toBe(true);
  });
});
