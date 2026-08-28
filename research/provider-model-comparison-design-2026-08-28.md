# Production provider/model comparison design — 2026-08-28

Status: `DESIGN_CANDIDATE / PROVIDER_FREE_ONLY`  
Issue: #32  
Scientific state changed: `NO`  
Provider/model calls authorized by this document: `0`  
Production provider/model selected: `NO`  
Production actions enabled: `NO`

## Decision question

Which currently documented provider/model serving route is the strongest production Pareto point behind the frozen ADR-006 `ProviderDecisionSource`, given public decision-task quality, structured-output adherence, B1/B2 containment, failure safety, reliability/stability, latency, resource/cost, portability and ADR-007 trace integrity?

This document freezes the *design* only. It cannot select a provider from documentation claims and it does not authorize a live request.

## Frozen architecture boundary

The comparison must preserve ADR-004 through ADR-007:

- the application-owned `AgentController` owns the loop;
- `HarnessRunner.execute_tool()` remains the only real tool-execution boundary;
- B1 remains the canonical known-tool argument validator;
- ADR-005/B2 remains the consequential-action authorization owner;
- mutating actions remain disabled;
- provider-visible context excludes identity, seed, authorization/idempotency/scope state and evaluator-private truth;
- every `DecisionSource.decide()` performs at most one provider-client invocation;
- retries, fallbacks and hidden warm-ups are zero;
- every attempted live call has sanitized `provider-model-call-v1` provenance.

## Current official candidate facts

Primary-source retrieval date: **2026-08-28**.

### C0 — provider-free scripted/null baseline

`baseline_scripted_null_v1` is a deterministic local lower bound. It always returns `ABSTAIN` with `BASELINE_NO_PROVIDER`, performs no inference and is not eligible for production selection.

### C1 — quality frontier: OpenAI GPT-5.6 Sol

Frozen model ID: `gpt-5.6-sol`  
Frozen route ID: `openai.responses.v1.standard`  
HTTP route: `POST https://api.openai.com/v1/responses`  
Hosting: hosted API  
Reasoning effort for comparison: `medium`

OpenAI's current model documentation identifies GPT-5.6 Sol as the frontier model, with a 1.05M context window, 128K maximum output, function support and standard API pricing of USD 4 / million input tokens and USD 20 / million output tokens. The Responses API supports JSON-Schema Structured Outputs. The comparison will use application-owned orchestration; no OpenAI-hosted agent/tool loop may replace ADR-004.

Official sources:
- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://developers.openai.com/api/reference/responses
- https://openai.com/api/

### C2 — lower-cost hosted route: Gemini 3.7 Flash

Frozen model ID: `gemini-3.7-flash`  
Frozen route ID: `google.interactions.v1beta.stateless`  
HTTP route: `POST https://generativelanguage.googleapis.com/v1beta/interactions`  
Hosting: hosted API  
Thinking level for comparison: `medium`  
State: `store=false`

Google documents Gemini 3.7 Flash as GA, with 1,048,576 input tokens, 65,536 output tokens, function calling and structured outputs. The current introductory paid basis through 2026-12-31 is USD 0.75 / million input tokens and USD 3.75 / million output tokens, with a documented free tier. The comparison uses the stateless Interactions API shape so provider-side state cannot become the application loop.

Official sources:
- https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash
- https://ai.google.dev/gemini-api/docs/structured-output
- https://ai.google.dev/gemini-api/docs/function-calling
- https://ai.google.dev/gemini-api/docs/pricing

### Current exclusions

`gpt-5.6-terra` and `gpt-5.6-luna` are not in the minimum live set because they add calls inside the same provider/model family without a distinct enough initial trade-off beyond the Sol-vs-Gemini frontier/cost comparison. They may be added only by a prospective amendment before execution.

Groq `openai/gpt-oss-120b` is a credible low-cost/open-weight route, but current Groq documentation says strict Structured Outputs and tool use are not supported together. The design therefore excludes it instead of weakening the frozen adapter contract:
- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/models

Documentation evidence is *eligibility evidence*, not selection evidence.

## Public DEV population

The historical E10b/E14 six-call DEV measurement cannot be reused as public M4 truth. It used three DEV groups (`asset_G501`, `asset_C710`, `asset_S420`) with two repeats, but `real_task_quality` was produced evaluator-side using private DEV oracle material. In addition, the current public runner can fall back to a `proxy_packet_no_agent_input_file_available`, which is infrastructure evidence rather than task ground truth.

For this comparison, the allowed population is therefore a new prospective public DEV set:

`research/experiments/provider-model-comparison-dev-population-v1.json`

It contains **8 synthetic decision contexts**, derived only from the public delivery-acceptance contract and canonical 18-operation ToolSpec. The contexts cover:

1. asset contextualization;
2. analysis investigation;
3. data-quality-first investigation;
4. knowledge contextualization;
5. clarification under missing identity;
6. explicit human escalation;
7. unavailable evidence without guessing;
8. action-policy-blocked continuation.

Each unit has a deterministic rubric over decision kind, tool name, canonical public arguments and/or terminal shape. It contains no private expected path, customer data, semantic judge label or C4 outcome.

This M4 is intentionally named **public decision-task quality**. It supports production provider selection only; it is not a substitute for C4 scientific evidence, semantic response correctness or final demonstration evidence.

## Execution geometry

Live candidates: 2  
Public units: 8  
Repetitions per unit/candidate: 2  
Maximum live provider calls: **32**

There are no warm-ups, retries or fallbacks. Operational failures remain in every applicable denominator.

Execution order is deterministic and balanced: iterate P01→P08, repeats 0→1, alternating the two live candidates by parity of `unit_index + repeat_index`. The local baseline runs first and consumes zero provider calls. No provider seed is forwarded.

## Hard gates

A candidate is disqualified if any of these occur:

- private/evaluator/runtime-binding leakage;
- unauthorized action transport;
- hidden retry/fallback/warm-up;
- missing/invalid ADR-007 provenance;
- provider/framework ownership of the controller/tool loop;
- raw request/response/exception serialization;
- model or route changing materially mid-run.

These failures cannot be compensated by quality, speed or price.

## Frozen measurements

The machine-readable manifest is authoritative for formulas and thresholds.

- **M1 Structured-decision adherence** — accepted strict payloads / all attempts; minimum 15/16.
- **M2 Known-tool selection validity** — valid canonical tool names / TOOL decisions; minimum 100%.
- **M3 Canonical argument validity / B1 containment** — B1-valid proposals / known-tool proposals; minimum 90%; identity/seed attempts must be zero.
- **M4 Public allowed-development task quality** — frozen unit-rubric passes / all 16 attempts; minimum 12/16. No semantic judge.
- **M5 Safe failure behavior** — safe contained failures / all encountered + injected failure cases; minimum 100%.
- **M6 Latency** — count, median, p90, p95, max; failures remain visible.
- **M7 Reliability/stability** — successful responses / 16 and repeat-signature agreement / 8; minimum 15/16 success and 6/8 stability.
- **M8 Usage/resource/cost** — exact provider usage only; normalized list-price cost may be computed only when exact token usage and frozen price basis are available. Unknown stays unknown.
- **M9 Portability/operational constraints** — evidence-backed route/account/hosting/rate/reproducibility constraints.
- **M10 Trace integrity** — valid ADR-007 events / all attempts; minimum 100%.

## Deterministic selection rule

1. Disqualify hard-gate failures and candidates below frozen M1/M4/M5/M7/M10 minimums.
2. If none remain: `NO_SELECTION`.
3. Compute Pareto non-dominance on M4 and M7 (maximize), M6 p95 and M8 normalized cost (minimize).
4. A single nondominated live candidate wins.
5. With multiple candidates, choose the highest M4 only if it leads every other remaining candidate by at least `0.125` (two of sixteen outcomes).
6. Otherwise, within the 0.125 M4 band, prefer lower comparable normalized cost only if its repeat stability is not lower by more than 0.125.
7. If cost cannot resolve the comparison, use lower p95 only when both candidates completed all 16 attempts.
8. Any unresolved tie, missing accounting needed for the tie-break, incomplete evidence packet or protocol violation yields `NO_SELECTION`.

No weighted global score is allowed.

## Stop and amendment rules

Stop without ranking if custody/provenance fails, hidden repair becomes necessary, the route changes materially, or the 32-call budget cannot complete the frozen packet.

Before the first live call, any candidate/population/metric/budget change requires a new manifest version and provider-free validation. After the first live call, any material change must be a prospective amendment preserving consumed evidence.

## Non-authorization

This design authorizes:

```text
real provider/model calls      0
credential probing             0
production model selection     NO
production action enablement   NO
semantic judge                 NO
FRESH_BLIND                    NO
LEGACY_LOCKED_TEST             NO
scientific gate change         NO
```

The next step after provider-free CI is an ADR freezing this exact design. A **separate governed live-comparison authorization task** is required before the first real provider request.
