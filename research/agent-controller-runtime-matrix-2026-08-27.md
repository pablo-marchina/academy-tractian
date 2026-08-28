# Agent Controller runtime decision matrix — 2026-08-27

**Issue:** #15  
**Class:** C — material architecture/runtime decision  
**Priority:** P0  
**Decision scope:** single-agent controller for the final vertical slice  
**Scientific state changed:** no  
**Provider/model calls:** 0  
**Evaluator/private/gold access:** 0  
**LOCKED_TEST access:** 0  
**Validation state:** `PENDING_PR_CI` — ADR/merge is forbidden until the provider-free controller tests pass on the repository CI boundary.

## 1. Decision question

Choose the smallest runtime/orchestration layer that can close the current P0 Agent Controller gap while preserving the already-proven E2 boundary:

```text
request
  -> typed controller decision
  -> optional tool proposal
  -> HarnessRunner.execute_tool()  [exclusive execution boundary]
  -> deterministic B1/B2/B3 + runner-owned identity/seed + trace
  -> normalized observation
  -> next bounded controller turn or terminal decision
  -> final / clarify / escalate / abstain
```

This decision does **not** select or freeze a model/provider, MCP topology, RAG/vector store, multi-agent decomposition, persistent-memory backend, observability backend, UI, semantic evaluator, FRESH_BLIND, or LEGACY_LOCKED_TEST path.

## 2. Constants that must not move

The current implementation evidence makes the following constraints non-negotiable for this P0 decision:

1. `HarnessRunner` remains the exclusive path for real tool execution.
2. `x-user-id` and seed remain runner-bound and must never appear as model-controlled tool arguments.
3. B1 argument validation, B2 permission/resource policy, and B3 evidence-aware action gating stay deterministic and outside model/runtime control.
4. Proposal, executed call, result, observation, terminal decision and final response remain separately inspectable in `RunTrace`.
5. The runtime must fail closed on malformed decisions, exhausted budgets, decision-source failure, or execution-boundary failure.
6. The runtime must support explicit `FINAL`, `CLARIFY`, `ESCALATE`, and `ABSTAIN` termination without forcing a tool call.
7. Provider/model integration must remain replaceable above the controller protocol.

## 3. What historical E6 actually established

E6 is valuable evidence, but it is not a final architecture freeze.

| Evidence | What it established | What it did not establish |
|---|---|---|
| E6 scorecard (`research/50-e6-runtime-spike-results-adr.md`) | LangGraph ranked first at `4.404`, narrowly ahead of Pydantic AI/Graph `4.328` and OpenAI Agents SDK `4.188`; the strongest weights favored replay/checkpointing and pause/resume/HITL. | That checkpointing/HITL must be on the final P0 critical path. |
| Adaptive ToolSpec spike (`research/54-e6-real-toolspec-langgraph-results.md`) | LangGraph preserved the 18-tool registry, `HarnessRunner`, B3, evidence stopping, deterministic replay and checkpoint pause/resume over DEV + VALIDATION. | That this orchestration layer is free: direct HarnessRunner averaged `1.3582 ms` vs LangGraph `20.3439 ms` (`14.979x` orchestration ratio in that spike). |
| Live API integration (`research/56-e6-live-api-integration-live-results.md`) | LangGraph + `HarnessRunner` + `HttpxTransport` successfully exercised the supplied API: `37/37` live requests and `4/4` accepted action proxies over 8 DEV + VALIDATION representative cases. | That LangGraph is necessary once the delivery gap is reframed around a minimal single-agent controller. |
| Delivery-gap inventory (`research/delivery-gap-inventory-2026-08-27.md`) | The current P0 blocker is the missing controller above E2; persistent memory remains `BLOCKED_BY_DECISION`/P2 unless evidence requires it. | Authorization to promote the entire historical research architecture wholesale. |

Therefore E6 proves that **LangGraph is a viable and already-integrated upgrade path**. It does not prove that it is the minimum justified dependency for the P0 vertical slice.

## 4. Current alternatives against the actual P0 boundary

The matrix below deliberately distinguishes repository-specific empirical evidence from current framework capabilities. `DIRECT` means the requirement is satisfied without another orchestration layer. `ADAPTER` means the framework can preserve the boundary, but only through an explicit integration adapter. `OWNED` means the framework normally owns behavior that this project currently needs to keep in E2/application control.

| Criterion | Explicit provider-free controller | LangGraph | Pydantic AI | OpenAI Agents SDK |
|---|---|---|---|---|
| Exclusive `HarnessRunner` tool execution | **DIRECT** | **ADAPTER, proven in E6** | **ADAPTER** via external/deferred tools | **OWNED by SDK by default**; custom boundary required |
| Runner-owned identity/seed preserved | **DIRECT** | **Proven in E6** | **ADAPTER** | **ADAPTER** |
| Typed tool/terminal decisions | **DIRECT** with Pydantic protocol | Supported with app-owned schema/state | Strong typed/schema fit | Structured output supported, but inside SDK runner model |
| Explicit turn + tool-call budgets | **DIRECT** | Supported | Supported by app/agent control | Turn budget built in; tool execution remains SDK-managed by default |
| Clarify/escalate/abstain without tool execution | **DIRECT** | Supported as graph/state branches | Supported as output/deferred control | Supported through outputs/handoffs/runner behavior |
| Deterministic fail-closed around E2 boundary | **DIRECT and testable** | **Proven compatible in E6** | Requires adapter around external tool resolution | Requires adapter because SDK runner executes local tools by default |
| Replay/checkpoint/pause-resume | In-process bounded state only | **Strong; empirically proven in E6** | Strong durable/deferred capabilities | Strong sessions/run-state/HITL capabilities |
| Persistent cross-process state required by current P0? | **No extra infrastructure** | Feature-rich but not currently required | Feature-rich but not currently required | Feature-rich but not currently required |
| New runtime dependency for P0 | **None** beyond existing Pydantic/E2 | `langgraph` | `pydantic-ai` (+ optional durability stack) | `openai-agents` |
| Repository-specific end-to-end runtime evidence | **This #15 provider-free test gate** | **Strong historical E6 evidence** | Historical scorecard only; no equivalent current E2 integration | Historical scorecard only; no equivalent current E2 integration |
| Provider neutrality of controller protocol | **Maximal** | High | High | Lower by default; SDK is OpenAI-first although model adapters exist |
| Complexity proportional to current delivery gap | **Best fit** | Higher than current minimum | Higher than current minimum | Mismatched ownership for current execution boundary |

### Current documentation check — 2026-08-27

- LangGraph's Functional API is explicitly aimed at adding persistence/memory, human-in-the-loop and streaming while keeping imperative control flow. Those are valuable upgrade features, but they are not current P0 requirements.
- Pydantic AI supports `ExternalToolset` / deferred calls whose execution is handed back to an outer application, so it can preserve `HarnessRunner` ownership. Its durable-execution stack is also strong, but not required for this P0 slice.
- OpenAI Agents SDK's `Runner` owns the agent loop and executes tool calls. Its own guidance recommends using the lower-level Responses path when the application wants to own the loop, tool dispatch and state handling. That ownership mismatch is decisive here because E2 must remain the execution boundary.

Documentation anchors:

- https://docs.langchain.com/oss/python/langgraph/functional-api
- https://docs.langchain.com/oss/python/releases/langgraph-v1
- https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/
- https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/
- https://openai.github.io/openai-agents-python/
- https://openai.github.io/openai-agents-python/running_agents/

## 5. Decision

**Select the explicit provider-free `AgentController` as the P0 single-agent orchestration layer, conditional only on repository CI passing before ADR/merge.**

The controller is intentionally small:

- provider-free `DecisionSource` protocol;
- Pydantic-validated `ControllerDecision` / `ToolProposal` / observation/context models;
- `TOOL`, `FINAL`, `CLARIFY`, `ESCALATE`, `ABSTAIN` decisions;
- explicit `max_turns` and `max_tool_calls`;
- zero direct transport/tool-registry execution;
- all real tools routed through `HarnessRunner.execute_tool()`;
- safe abstention on decision-source failure, tool-boundary failure and exhausted budgets;
- no binding, seed, private evaluator state or gold in `ControllerContext`;
- no model/provider/framework SDK imports.

This is a **P0 vertical-slice runtime decision**, not a universal/final architecture freeze for every future requirement.

## 6. Why LangGraph is retained, not rejected

LangGraph remains the first proven upgrade candidate. Re-open the runtime decision if at least one of the following becomes an actual release requirement rather than a hypothetical capability:

1. cross-process durable pause/resume;
2. checkpoint persistence across worker/process failure;
3. first-class human-in-the-loop interruption/resumption across long-running runs;
4. controller branching/state complexity that makes the explicit loop materially harder to verify or maintain;
5. a measured reliability or developer-productivity gain that outweighs the extra orchestration dependency while preserving E2 invariants.

At that point, the historical E6 path provides a concrete migration route rather than requiring a greenfield rewrite.

Pydantic AI should be revisited if typed provider integration plus external/deferred tool execution becomes the dominant need. OpenAI Agents SDK should be revisited only if the project deliberately changes the current ownership rule and allows a framework runner to own the agent loop/tool dispatch instead of E2/application code.

## 7. Validation gate before ADR

The decision is not allowed to become an ADR or merge until CI proves the implementation invariants on the actual branch. Required tests include:

- one successful tool turn followed by final response, with exactly one transport call through the real `HarnessRunner` path;
- external `x-user-id` and seed binding preserved;
- model-controlled identity/seed rejected at proposal validation;
- second tool call blocked once `max_tool_calls` is exhausted;
- turn budget exhaustion terminates safely;
- B1-blocked proposal returned to the controller as a contained observation with zero transport bypass;
- decision-source exception terminates in safe abstention without leaking exception text;
- transport/boundary exception terminates in safe abstention without leaking exception text;
- `CLARIFY`, `ESCALATE`, and `ABSTAIN` execute zero tools;
- controller source imports no provider/runtime orchestration SDK;
- malformed controller decision shapes fail validation.

After these checks pass in the repository CI, this matrix can be marked `VALIDATED`, the ADR can record the decision, and only then may the Class C PR be merged.
