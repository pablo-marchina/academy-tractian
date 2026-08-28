# ADR-004 — P0 Agent Controller runtime and orchestration boundary

Status: `ACCEPTED`
Date: 2026-08-27
Decision state: `FROZEN_FOR_P0_CONTROLLER_SCOPE`
Issue: #15
Validation evidence: PR CI run `#887` / Actions run `33130472742`, `completed / success` at `0cc498342716a8ee631e305d255cfe92725494f6`
Scientific state changed: `NO`
Provider/model calls for this decision: `0`
Evaluator/private/gold access: `0`
`LOCKED_TEST` access: `0`

## Context

The canonical E2 `HarnessRunner` already owns deterministic tool execution: typed ToolSpec resolution, runner-bound identity/seed, B1/B2/B3 guards, transport, evidence-aware action gating, and normalized trace events. It intentionally does not own agent reasoning or the iterative decision loop.

Issue #15 therefore asks a narrower architecture question than the historical E6 runtime research: what is the smallest single-agent controller/runtime layer that closes the current P0 delivery gap **without moving the proven E2 execution boundary**?

Historical E6 established that LangGraph is a viable orchestration path. Its strongest evidence includes preservation of the E2 boundary, deterministic replay/checkpoint behavior, and a live integration that completed `37/37` supplied-API requests and `4/4` accepted action proxies on representative DEV + VALIDATION cases. That evidence establishes feasibility, not necessity for the current P0 scope.

The current delivery-gap inventory does not make persistent cross-process memory, durable checkpointing, durable HITL, multi-agent orchestration, RAG, vector search, or MCP a baseline P0 requirement. Adding those capabilities to the critical path without a demonstrated requirement would increase runtime ownership and dependency complexity before the final vertical slice exists.

## Requirements affected

- P0 — `REQ-017`: operational Agent + integrated evaluation framework.
- P0 — `REQ-005..013` / `AG-003..AG-013`: contextualize, investigate, plan/stop, clarify/abstain, act, escalate, handle degraded evidence, ground responses, and fail safely.
- P1 — technical coherence, traceability, failure continuity, reproducibility, rollback, and latency/resource control.

This ADR does **not** change the scientific authorization state or select a model/provider.

## Hard constraints

1. `HarnessRunner.execute_tool()` remains the exclusive path for real tool execution.
2. `x-user-id` and seed remain runner-owned and outside model/controller tool arguments.
3. B1 argument validation, B2 permission/resource policy, and B3 evidence-aware action gating remain deterministic and outside model/runtime control.
4. Proposal, executed call, result, normalized observation, terminal decision, and final response remain separately inspectable in `RunTrace`.
5. Malformed decisions, exhausted budgets, decision-source failure, and execution-boundary failure fail closed.
6. `FINAL`, `CLARIFY`, `ESCALATE`, and `ABSTAIN` may terminate without a tool call.
7. Provider/model integration stays replaceable above a provider-free controller protocol.
8. No private evaluator/gold/`LOCKED_TEST` state may enter controller runtime state.

## Decision criteria

| Criterion | Required interpretation |
|---|---|
| P0 functional coverage | Bounded single-agent iterative tool loop plus final/clarify/escalate/abstain. |
| E2 compatibility | Preserve `HarnessRunner` as the only real execution boundary and preserve runner-owned identity/seed. |
| Fail-closed behavior | Contain malformed decisions, source failures, budget exhaustion, blocked tools, and transport/boundary failures. |
| Traceability | Preserve separate proposal/call/result/observation/terminal trace semantics. |
| Provider neutrality | Controller protocol must not depend on a provider SDK or provider-owned runtime. |
| Deterministic testability | Core controller behavior must be testable with zero provider/model calls. |
| Complexity proportionality | Prefer the simplest runtime that satisfies current P0/P1 requirements without measurable required loss. |
| Reversibility | Preserve a clear migration path if durable orchestration becomes a demonstrated requirement. |

## Alternatives considered

### A — Explicit provider-free single-agent controller

A small application-owned controller loop with typed `ControllerDecision`, `ToolProposal`, observation/context models, explicit turn/tool budgets, and a provider-free `DecisionSource` protocol. Every real tool proposal is delegated to `HarnessRunner.execute_tool()`.

**Evidence**

- Implemented in `research/e2/controller.py`.
- Deterministic compatibility/regression coverage in `research/e2/tests/test_controller.py`.
- Repository CI run #887 completed successfully at `0cc498342716a8ee631e305d255cfe92725494f6` after the implementation/test correction cycle.
- No provider/model calls, private evaluator access, gold access, or `LOCKED_TEST` access were required.

**Advantages**

- Direct ownership match with the existing E2 boundary.
- No new orchestration runtime dependency.
- Provider-neutral decision source.
- Small state surface and explicit budgets/fallbacks.
- Straightforward deterministic replay/regression tests.

**Costs / risks**

- Durable cross-process checkpointing, durable HITL, and complex graph orchestration are not provided automatically.
- Application code owns the controller loop and must keep its invariants tested as functionality grows.

**Decision:** `SELECTED` for the P0 controller scope.

### B — LangGraph

LangGraph can preserve the E2 boundary through an adapter and has the strongest repository-specific framework evidence from E6, including checkpoint/pause-resume experiments and successful supplied-API integration.

**Advantages**

- Proven repository compatibility.
- Strong persistence/checkpoint/HITL and explicit state/branching capabilities.
- Concrete migration route already exists from E6.

**Costs / risks**

- Adds a runtime dependency and orchestration semantics not required by the current P0 gap.
- Historical E6 measured non-zero orchestration overhead relative to direct `HarnessRunner` execution.

**Decision:** `QUALIFIED_UPGRADE_PATH`, not required on the P0 critical path.

### C — Pydantic AI runtime

Provides strong typed agent/output integration and can hand external/deferred tool execution back to application code.

**Advantages**

- Strong typed/schema fit.
- Can preserve application-owned execution through adapter/deferred-tool patterns.
- Durable execution capabilities are available if later required.

**Costs / risks**

- Adds runtime/dependency surface before a current P0 requirement justifies it.
- No equivalent repository-specific current E2 integration evidence to displace the simpler baseline.

**Decision:** `DEFERRED`; revisit if typed provider integration plus external/deferred execution becomes the dominant requirement.

### D — OpenAI Agents SDK

Provides a full agent runner, structured outputs, session/run-state, tools, and HITL capabilities.

**Advantages**

- Mature agent-loop feature set.
- Strong built-in run/session abstractions.

**Costs / risks**

- Default runner ownership overlaps the exact loop/tool-dispatch ownership this project currently keeps in application/E2 code.
- Requires an additional adapter/ownership decision and is OpenAI-first at the runtime layer.

**Decision:** `DEFERRED`; reconsider only if the project deliberately changes the E2/application ownership rule.

## Validation experiment

The selected baseline was not accepted from design preference alone. The branch implemented a provider-free prototype and required the existing repository PR workflow to exercise E2 and the downstream research regression suite.

Validation evidence:

- pre-ADR implementation head: `0cc498342716a8ee631e305d255cfe92725494f6`;
- workflow run: `#887` / Actions run `33130472742`;
- final workflow state: `completed`;
- final workflow conclusion: `success`;
- provider/model calls: `0`;
- scientific-state changes: `0`.

The controller tests cover the material boundary conditions required by #15: successful tool-to-final routing through `HarnessRunner`, runner-owned identity/seed, rejection of model-controlled identity/seed, turn and tool-call budgets, blocked proposals without transport bypass, decision-source failure, transport/boundary failure, terminal no-tool decisions, provider/runtime import isolation, and malformed decision shapes.

A first PR CI run failed on a test assertion typo (`transport.cals` instead of `transport.calls`). The typo was corrected without changing controller runtime behavior; run #887 then passed. This failure is retained as provenance rather than hidden.

## Decision

Freeze the **explicit provider-free `AgentController` pattern for the P0 single-agent controller scope**.

The accepted runtime boundary is:

```text
request
  -> provider-free typed controller decision
  -> optional ToolProposal
  -> HarnessRunner.execute_tool()  [exclusive real execution boundary]
  -> deterministic E2 guards/binding/transport/trace
  -> normalized observation
  -> next bounded controller turn OR terminal decision
  -> final / clarify / escalate / abstain
```

The controller owns bounded orchestration only. `HarnessRunner` continues to own actual tool execution and external identity/seed binding. Provider/model code, when added under a separately authorized task, must implement the `DecisionSource` side of this boundary rather than bypassing it.

This decision is **frozen only for the P0 controller/runtime pattern**. It is not a claim that the final production architecture is globally frozen.

## Non-inferences and authorization boundary

This ADR does not:

- select or freeze a model or provider;
- authorize provider/model calls under the current C4 scientific gate;
- authorize semantic evaluation, survivor/PREFERRED inference, FRESH_BLIND, or LEGACY_LOCKED_TEST;
- introduce private evaluator/gold data into runtime;
- freeze persistent memory, RAG/vector DB, MCP, multi-agent topology, observability backend, or UI;
- claim production readiness;
- modify any frozen C4 artifact.

The scientific gate remains independently governed; at the time of this ADR, `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` remains separate from this architecture decision.

## Consequences

- **Positive:** closes the P0 controller gap with the smallest currently sufficient runtime surface and preserves all E2 execution invariants.
- **Positive:** keeps provider/model integration replaceable and testable above a stable provider-free protocol.
- **Positive:** retains the historical LangGraph path as a proven upgrade instead of discarding prior E6 work.
- **Negative:** application code must own and maintain the bounded loop and regression obligations.
- **Negative:** durable checkpoint/HITL/cross-process state is deliberately absent from the P0 baseline.
- **Operational:** every future controller change must preserve exclusive `HarnessRunner.execute_tool()` routing, external binding ownership, fail-closed budgets/fallbacks, and normalized trace semantics.
- **Evaluation:** provider-free deterministic controller tests remain a regression gate; semantic/private/blind evaluation stays outside this decision.

## Reversal triggers

Reopen ADR-004 if any of the following becomes a demonstrated release requirement or measured problem:

1. durable pause/resume across process or worker failure;
2. persistent checkpoint recovery across runs;
3. first-class long-running human-in-the-loop interruption/resumption;
4. controller branching/state complexity that materially reduces verifiability or maintainability of the explicit loop;
5. measured reliability, latency, or developer-productivity evidence showing a framework provides net benefit while preserving all E2 invariants;
6. a deliberate architecture decision moves tool-loop ownership away from E2/application code.

If reopened for durable orchestration, LangGraph is the first qualified candidate because E6 already demonstrated compatibility with the repository boundary. Pydantic AI and OpenAI Agents SDK remain alternatives under the conditions recorded in the decision matrix.

## Regression obligations

Any implementation derived from this ADR must continue to prove:

- all real tool execution goes through `HarnessRunner.execute_tool()`;
- controller proposals cannot set runner-owned identity/seed;
- deterministic B1/B2/B3 behavior remains outside provider/runtime control;
- explicit turn/tool budgets fail closed;
- decision-source and tool-boundary failures terminate safely without leaking exception internals;
- `FINAL`, `CLARIFY`, `ESCALATE`, and `ABSTAIN` can terminate with zero tool execution;
- controller runtime remains free of private evaluator/gold/`LOCKED_TEST` state;
- provider/runtime additions do not silently bypass E2 trace semantics.

## Sources

Repository evidence:

- `research/agent-controller-runtime-matrix-2026-08-27.md`
- `research/e2/controller.py`
- `research/e2/tests/test_controller.py`
- `research/50-e6-runtime-spike-results-adr.md`
- `research/54-e6-real-toolspec-langgraph-results.md`
- `research/56-e6-live-api-integration-live-results.md`
- `research/delivery-gap-inventory-2026-08-27.md`
- issue #15
- PR #16
- Actions run #887 / `33130472742`

Primary framework documentation reviewed by the dated decision matrix remains the capability reference; repository-specific selection is based on the controlled E2 compatibility evidence above.