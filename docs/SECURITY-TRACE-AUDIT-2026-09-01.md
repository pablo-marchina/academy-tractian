# Security / Trace / Failure-Containment Audit — 2026-09-01

**Baseline:** `main@3e0dbac5af413859b53011f6e43e8c0107b2fae3`  
**Provider calls:** `0`  
**Credential/account probes:** `0`

## Executive result

No new provider-independent security blocker was found. The current runtime has strong deterministic isolation and fail-closed behavior. The only newly identified provider-free delivery gap is escalation-handoff completeness (PFG-01), which is a quality/continuity gap rather than an authorization bypass.

## Audit matrix

| Control | Status | Evidence / reasoning |
|---|---|---|
| Requester identity outside model control | PROVED | `ProductionRequest` owns identity/user; `ControllerContext` exposes only request text, turn/tool counts and observations. Tests assert `user_id` / `identity_id` are absent from model-visible context. |
| Evaluation seed outside model control | PROVED | seed is runner-bound, absent from `ControllerContext` and provider-visible request; forbidden model-controlled seed fields are rejected. |
| Authorization outside model control | PROVED | production action context is runtime-owned, `actions_enabled` is literal false in the base runtime, permissions are not model-visible, and every canonical action is denied before transport in the default slice. |
| HarnessRunner sole real tool-execution boundary | PROVED | `ProductionRuntime` constructs `HarnessRunner`; `AgentController` delegates proposals to `runner.execute_tool()` and provider-native tool execution is not used. |
| Argument/schema validation before transport | PROVED | strict B1 argument validation blocks invalid proposals before transport; model-controlled binding fields are rejected. |
| Permission/project policy separation | PROVED | tool binding/argument checks and B2 production action policy are separate traceable stages. |
| Consequential-action idempotency / duplicate containment | PROVED_BOUNDED | controlled action path uses durable pre-transport claim and no-replay uncertainty semantics; blanket production mutation remains intentionally disabled. |
| Model-call provenance sanitization | PROVED | controller accepts only a fixed scalar allowlist for model-call audit metadata; raw requests/responses/exceptions and nested arbitrary metadata are not canonical trace payloads. |
| Evaluator-private/gold isolation | PROVED | provider request tests explicitly exclude `gold`, `oracle`, private evaluator modules and benchmark scenario material; runtime adapter imports no private evaluator stack. |
| Trace lifecycle integrity | PROVED | lifecycle validators require one final response / run finished ordering and execution-chain proposal→call→result→observation integrity. |
| Policy-denial containment | PROVED | denied actions emit contained policy events and controller-generated blocked observations; no denied action reaches transport. |
| Transport failure containment | PROVED | exploding transport yields safe `ABSTAIN / TOOL_BOUNDARY_FAILURE`; internal exception detail is absent from serialized trace. |
| Provider failure containment | PROVED | malformed provider output or provider exception yields `ABSTAIN / DECISION_SOURCE_FAILURE`; no tool transport occurs and backend secret text is excluded. |
| Bounded execution | PROVED | explicit max-turn and max-tool-call limits; budget exhaustion terminates via safe abstention. |
| Hidden retry/fallback behavior | PROVED for current governed paths | provider-free campaigns and governed Cloudflare path freeze zero automatic retries/fallbacks/replay. |
| Secrets/private material in traces | PROVED_BOUNDED | leakage campaigns and Cloudflare entrypoint tests prevent token/account/private raw material persistence; real credentials have not been provisioned. |
| Customer-safe failure response | PROVED | EV-011 rejects raw exception/internal provider disclosure and unsupported success claims. |
| Escalation handoff completeness | **MISSING / PFG-01** | current `C10_ESCALATION_HAS_SAFE_HANDOFF` checks only non-empty message + supported reason + human/review wording, not evidence/unresolved uncertainty/continuation context. |

## PFG-01 security-safe closure constraints

Any escalation-handoff improvement must preserve:

```text
no identity/seed/auth leakage
no raw provider/tool exception material
no private evaluator data
no fabricated evidence
no new tool execution
no provider prompt/packet change before D01
no retry/fallback behavior
```

A handoff may summarize only observations already present in the runtime trace/context. If no collected evidence exists, it must explicitly state that no evidence was collected rather than fabricate an evidence list.

## No-change conclusions

The audit does **not** justify:

- LangGraph or a new orchestration runtime;
- persistent memory/state store;
- MCP migration;
- RAG/vector/reranking;
- external observability SaaS;
- new auth framework;
- changes to ADR-018→023 provider packet/custody/client/launcher.

Those components would add surface area without closing a measured security gap.

## Regression obligations

After any PFG-01 change, preserve all of the following:

1. default actions cannot reach transport;
2. forbidden model-controlled identity/seed fields fail closed;
3. malformed provider output fails closed;
4. provider/transport exception detail never reaches the canonical trace/final message;
5. trace lifecycle remains valid;
6. model-call audit allowlist remains strict;
7. controlled-action idempotency/no-replay tests remain green;
8. Cloudflare governed entrypoint provider-free tests remain green;
9. standalone wheel smoke remains green;
10. provider calls and credential probes remain zero.