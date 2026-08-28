# ADR-007 — P0 model-call trace provenance and provider-comparison preregistration

Status: `ACCEPTED`
Date: 2026-08-27
Decision state: `FROZEN_FOR_P0_MODEL_CALL_PROVENANCE_CONTRACT`
Issue: #29
PR: #30
Validated implementation head: `12cd09a83c533bf35170520554b209c361d8d903`
Primary validation: `production-runtime` run `#12` / Actions run `33137347455`, `completed / success`
Root production tests: `80/80 PASS`
ADR-004 controller regression: `12/12 PASS`
Triggered workflows on validated implementation head: `12/12 success`
E2–E8 regression: run `#891` / Actions run `33137347432`, `completed / success`
Scientific state changed: `NO`
Provider/model calls for this decision: `0`
Production provider/model selected: `NO`
Production mutating actions enabled: `NO`
Evaluator/private/gold access: `0`

## Context

ADR-004 froze application-owned orchestration: `AgentController` owns the bounded decision/tool loop and `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary. ADR-005 froze consequential-action authorization while keeping production actions disabled. ADR-006 then froze a provider-neutral `ProviderDecisionSource` adapter without selecting or calling a real provider/model.

The canonical `RunTrace` already reserved `event_type="model_call"`, but the production path had no accepted contract for what such an event must contain, how it is inserted, how failures are represented, or how a deterministic evaluator distinguishes an auditable provider call from unsafe/raw logging.

That gap matters before the first live production-provider comparison. A provider call that is not traceable cannot support reliability, latency, failure-continuity or selection evidence; a provider call logged with raw prompt/response material can violate the project's context-isolation and customer/privacy boundaries.

Issue #29 therefore asks: **what is the smallest provider-neutral provenance contract that makes future model calls auditable without changing ADR-004 decision/tool ownership or recording sensitive provider payloads?**

This ADR is provider-free. It freezes provenance and comparison requirements only. It does not authorize a live request and does not select a provider/model.

## Requirements affected

- P0 — complete trustworthy production Agent + Evaluator plumbing required by `REQ-017`.
- P0/P1 — inspectable process, safe failure continuity, deterministic trace integrity and provider portability.
- Reliability — make later provider failure/latency evidence attributable to individual invocations.
- Security/privacy — prevent credentials, raw prompts/responses, runtime identity/seed/action state and evaluator-private truth from entering model-call telemetry.
- Governance — require provider/model comparison metrics and candidate classes to be preregistered before any live selection experiment.

## Hard constraints

1. `DecisionSource.decide(ControllerContext) -> ControllerDecision` remains unchanged.
2. `AgentController` remains the owner of decision-loop sequencing.
3. `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary.
4. The model-call audit hook cannot emit tool calls, policy checks, observations or terminal events; it can only supply a sanitized `model_call` record that the controller appends to the canonical trace.
5. Existing non-audited `DecisionSource` implementations remain backward compatible and produce no new trace events.
6. Audit metadata is validated **before trace insertion** against a flat scalar allowlist; arbitrary/nested/raw payloads fail closed as `DECISION_SOURCE_AUDIT_FAILURE`.
7. The provider adapter records at most one audit record for each actual `ProviderDecisionClient.complete(...)` invocation.
8. A successful provider invocation records a `model_call` before the corresponding controller `decision`.
9. A failed provider/parsing/proposal invocation records a sanitized failure `model_call` before terminal `DECISION_SOURCE_FAILURE`; it has no corresponding controller decision.
10. The trace stores hashes and non-secret route identity, never raw provider request/response, credentials or exception text.
11. Runtime `user_id`, `x-user-id`, identity binding, seed, action authorization/scope/confirmation/idempotency and evaluator-private/gold state cannot be serialized through the audit hook.
12. Adapter retry count remains `0` and adapter fallback remains `false` unless a future prospective ADR/amendment changes those semantics.
13. Provider-free production evaluation remains the default and requires zero `model_call` events.
14. Traced-provider evaluation is explicit and structural only; enabling that evaluator mode does not authorize a live provider call.
15. B1 canonical ToolSpec argument validation and ADR-005/B2 action authorization remain unchanged.
16. No provider/orchestration SDK is added to the neutral provenance/evaluator contract.
17. Real provider/model calls remain `0` until a separate live-comparison authorization freezes exact candidate/model/route identifiers and the allowed development population.

## Decision criteria

| Criterion | Required interpretation |
|---|---|
| Ownership preservation | Provenance observes a source call; it never owns the loop or tool execution. |
| Pre-insertion redaction | Unsafe metadata is rejected before entering `RunTrace`, not merely flagged afterward. |
| One-call accountability | One client invocation maps to one model-call record; hidden retries/fallbacks are disallowed. |
| Deterministic identity | Equivalent canonical non-secret call inputs produce the same self-verifying call ID. |
| Failure continuity | Client/parser/proposal failures remain visible without exception/body leakage and end fail-closed. |
| Trace ordering | Successful model call precedes exactly one matching controller decision; failed calls are terminal. |
| Tamper detection | Invalid call IDs, duplicated IDs, malformed records and ordering inconsistencies fail structural evaluation. |
| Backward compatibility | Existing provider-free/scripted traces are unchanged. |
| Minimal disclosure | Route identity, hashes, counters, outcome/failure code and latency are enough; bodies are not needed. |
| Selection governance | A later provider comparison cannot retroactively invent metrics or thresholds after results are seen. |

## Alternatives considered

### A — Keep `model_call` unused

Continue evaluating only tool/controller trace events and rely on external provider logs later.

**Advantages**

- No new trace surface.
- Zero additional metadata.

**Risks / costs**

- Provider failures/latency cannot be deterministically linked to a production run.
- External logs may not preserve the same run/call identity or retention semantics.
- A provider-selection experiment would lack canonical trace-integrity evidence.

**Decision:** `REJECTED_AS_INSUFFICIENT_FOR_LIVE_PROVIDER_EVIDENCE`.

### B — Record raw provider request/response in `RunTrace`

Serialize the provider-visible prompt/request and raw response alongside call metadata.

**Advantages**

- Maximum debugging detail.
- Easy offline replay of exact provider payloads.

**Risks / costs**

- Duplicates customer/tool-result content into a broader trace surface.
- Increases credential/privacy/evaluator-boundary leakage risk.
- Makes future retention/export controls substantially harder.
- Not required to verify call identity, failure family, ordering or latency.

**Decision:** `REJECTED`; raw request/response recording is explicitly forbidden by the accepted contract.

### C — Provider/client-owned telemetry only

Require each concrete provider client to log whatever its SDK exposes, outside the controller trace.

**Advantages**

- Can exploit provider-native usage/latency fields.
- Keeps controller code smaller.

**Risks / costs**

- Provider-specific semantics fragment evidence.
- Switching providers changes audit shape.
- External logs can silently include sensitive payloads or retries.
- Canonical evaluator cannot deterministically validate one-call/one-decision ordering.

**Decision:** provider-native telemetry may later supplement evidence, but `REJECTED_AS_CANONICAL_PROVENANCE`.

### D — Sanitized controller-owned `model_call` envelope

An auditable `DecisionSource` exposes a drain hook containing only an accepted model-call envelope. The controller validates the envelope and appends it to `RunTrace`; `ProviderDecisionSource` generates a self-verifying versioned record around exactly one client invocation.

**Advantages**

- Preserves ADR-004 ownership.
- Provider-neutral and SDK-independent.
- Failures are captured before source exceptions become safe abstention.
- Raw/nested metadata is blocked before trace insertion.
- Deterministic evaluator can validate integrity without provider access.
- Existing non-audited DecisionSources remain unchanged.

**Risks / costs**

- Deliberately omits raw payloads, so deep provider debugging needs separately governed diagnostics.
- `live_call` and provider/model/route identifiers must be supplied truthfully by a future concrete client configuration.
- Latency is diagnostic and environment-dependent; it is not part of deterministic call identity.
- Provider-reported token/cost usage is not yet part of the canonical record because no provider-neutral trustworthy source exists in this task.

**Decision:** `SELECTED`.

## Accepted provenance contract

### Controller audit boundary

`DecisionSourceAuditRecord` is additive and optional. The controller checks:

- event type is exactly `model_call`;
- `call_id` is a 64-character lowercase SHA-256 hex string;
- metadata keys belong to the frozen allowlist;
- metadata values are flat scalar values only;
- oversized arbitrary strings/nested payloads are rejected before trace insertion.

If audit-drain validation fails, the controller performs a safe abstention with `DECISION_SOURCE_AUDIT_FAILURE`; no malformed audit event is appended and no tool is executed after the audit failure.

### Provider model-call record

`ProviderModelCallRecord` version `provider-model-call-v1` records:

- adapter version;
- deterministic `call_id`;
- non-secret `provider_id`, `model_id`, `route_id`;
- `live_call` boolean;
- canonical provider-request SHA-256;
- raw-response SHA-256 only when the client returned a string;
- bounded `turn_index` and `tool_call_count`;
- `success` or `failure` outcome;
- decision kind on success;
- sanitized failure code on failure;
- elapsed latency in milliseconds;
- adapter client invocation count fixed at `1`;
- adapter retry count fixed at `0`;
- adapter fallback flag fixed at `false`;
- explicit `raw_request_recorded=false`, `raw_response_recorded=false`, `exception_text_recorded=false` flags.

The canonical `call_id` is SHA-256 over only:

```text
provider-model-call-v1
provider-decision-adapter-v1
provider_id
model_id
route_id
live_call
request_sha256
turn_index
tool_call_count
```

The record recomputes this value during validation; a tampered call ID is invalid even when syntactically well formed.

Latency, response hash and outcome are intentionally **not** part of call identity: they are observations about the invocation, not inputs defining which canonical invocation was attempted.

### Failure codes

The frozen provider-neutral adapter failure families are:

- `CLIENT_FAILURE`;
- `RESPONSE_TYPE_INVALID`;
- `RESPONSE_JSON_INVALID`;
- `RESPONSE_PAYLOAD_INVALID`;
- `UNKNOWN_TOOL`;
- `PROPOSAL_REJECTED`.

Exception text is never copied into the model-call record or final response.

## Accepted evaluation modes

`ProductionEvaluationPolicy` now makes the provider mode explicit:

### Default provider-free mode

```text
provider_free = true
require_model_call_provenance = false
```

A trace containing any `model_call` fails the provider-free check. This preserves the meaning of existing provider-free production evidence.

### Explicit traced-provider structural mode

```text
provider_free = false
require_model_call_provenance = true
```

The evaluator requires at least one model-call event and checks:

- every event validates as `ProviderModelCallRecord`;
- event payload fields such as `tool_name`, `arguments` and `result` remain empty;
- call IDs are unique;
- successful records have exactly one subsequent matching controller decision before the next model call;
- decision kind, turn index and prior tool-call count match;
- failed records have no controller decision and are terminal among model calls;
- a failure record is followed by final `DECISION_SOURCE_FAILURE`.

Evaluation reports expose sanitized summaries only. They do not copy request/response hashes into the per-call summary and never copy raw provider payloads.

This mode proves structural provenance, not semantic model quality and not authorization to call a provider.

## Provider-comparison preregistration

The accepted prospective evidence contract is:

`research/provider-model-live-comparison-preregistration-2026-08-27.md`

A later live comparison must freeze exact current candidate/model/route identities **before** the first live request and include at minimum:

1. provider-free scripted/null baseline;
2. one strong quality-frontier provider/model candidate;
3. one feasible lower-cost/local/open candidate;
4. any additional candidate only for a distinct credible Pareto trade-off.

The allowed development-only population must be frozen prospectively. Historical C4 serving-route qualification is not production-provider selection and cannot bypass this requirement.

Measurements to freeze before execution include:

- structured-decision adherence;
- known-tool selection validity;
- canonical argument validity / B1 containment;
- allowed-development task quality under separately authorized measures;
- safe failure behavior;
- latency distribution;
- reliability/error families;
- usage/resource/cost where reliably observable;
- portability/operational constraints;
- trace integrity.

Default automatic retries are `0`; default provider/model fallbacks are `0`. Failed attempts remain in denominators. Selection must permit `NO_SELECTION` when hard requirements fail or evidence is insufficient.

No concrete live model identifier is frozen by ADR-007 because current provider facts are time-sensitive and live calls are not authorized here.

## Validation evidence

The implementation was validated entirely provider-free.

First complete implementation head before the explicit valid-duplicate attack test:

`80131bcfafc7f8498edfb16448712aa2f70d2229`

Validation:

```text
production-runtime run        33137274889 / #11
root production tests         79 / 79 PASS
ADR-004 controller tests      12 / 12 PASS
triggered workflows           12 / 12 success
provider/model calls          0
```

Before ADR acceptance, an explicit regression was added for a duplicated **otherwise valid** `call_id`, rather than relying only on malformed-metadata coverage. That strengthened pre-ADR implementation head is:

`12cd09a83c533bf35170520554b209c361d8d903`

Final pre-ADR implementation validation:

```text
production-runtime run        33137347455 / #12
root production tests         80 / 80 PASS
ADR-004 controller tests      12 / 12 PASS
E2–E8 run                     33137347432 / #891 success
triggered workflows           12 / 12 success
provider/model calls          0
production action calls       0
```

Negative-path evidence covers:

- malicious nested/raw audit metadata rejected before trace insertion;
- valid audited calls ordered before decisions;
- deterministic/self-verifying call IDs;
- client exception with secret text retained nowhere in trace;
- malformed provider response represented only by response hash + sanitized failure code;
- default provider-free evaluator rejecting traces with model calls;
- explicit traced-provider evaluator accepting valid fake/provider-free provenance;
- tampered call ID rejection;
- duplicated valid call ID rejection;
- invalid/extra provenance metadata rejection;
- multi-turn one-call/one-decision matching;
- existing non-audited provider adapter trace shape preserved.

No live inference occurred in any test.

## Decision

Freeze the **sanitized controller-owned model-call provenance contract and the provider/model live-comparison preregistration for the P0 production scope**.

Accepted future path:

```text
ControllerContext
  -> ProviderDecisionSource
  -> build deterministic ProviderDecisionRequest
  -> ProviderDecisionClient.complete(request)       [future separately authorized live client]
  -> sanitized ProviderModelCallRecord
  -> DecisionSourceAuditRecord drain
  -> AgentController validates + appends model_call
  -> controller decision OR fail-closed source failure
  -> HarnessRunner / B1 / ADR-005 B2 / transport
  -> RunTrace
  -> ProductionEvaluator structural provenance checks
```

The provenance event observes and identifies the client invocation; it does not change the returned `ControllerDecision`, perform a retry, dispatch a tool or authorize an action.

## Explicit non-authorization

ADR-007 does **not**:

- authorize a real provider/model/API call;
- select, rank, qualify or prefer a production provider/model;
- freeze a concrete current live candidate set;
- authorize provider retries/fallbacks;
- enable production actions;
- change ADR-005 action authorization;
- change B1 canonical argument validation;
- authorize semantic/judge evaluation;
- authorize FRESH_BLIND or LEGACY_LOCKED_TEST access;
- alter or recompute any frozen C4 artifact/score;
- authorize survivor/PREFERRED inference;
- change the scientific gate;
- freeze global architecture;
- claim production readiness.

The scientific gate remains independently `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` and provider/model calls authorized now remain `0`.

## Consequences and trade-offs

- **Positive:** future model/provider calls can be linked deterministically to controller turns without raw payload logging.
- **Positive:** provider failures become auditable while still terminating through the existing safe-abstention path.
- **Positive:** malformed/sensitive audit metadata is blocked before it contaminates the trace.
- **Positive:** provider-free historical/current traces retain their original semantics.
- **Positive:** the deterministic evaluator can detect provenance tampering and ordering defects offline.
- **Positive:** live provider comparison cannot legitimately select a winner without prospectively frozen evidence criteria.
- **Negative:** response/request bodies are unavailable in canonical telemetry; deeper debugging needs a separately governed diagnostic surface.
- **Negative:** the record does not yet standardize provider-native token/usage/cost fields.
- **Negative:** route identity and `live_call` truthfulness ultimately depend on the future concrete client configuration and its own validation evidence.
- **Operational:** latency is measured at the neutral client boundary and may include network/provider variability; it is diagnostic, not deterministic identity.

## Reversal / amendment triggers

Reopen or supersede ADR-007 if:

1. real provider evidence shows the one-invocation/zero-retry contract is operationally inadequate;
2. a justified retry/fallback policy is needed and must become explicit in trace semantics;
3. provider-native usage/cost evidence needs a provider-neutral trustworthy extension;
4. security/privacy review requires stricter hashing, retention or route-identity treatment;
5. a future provider cannot supply truthful stable route/model identity under this contract;
6. ADR-004 orchestration ownership is deliberately superseded;
7. model-call events need cross-process correlation or distributed tracing beyond current `RunTrace` semantics;
8. measured debugging/reliability needs justify a separately protected raw diagnostic store;
9. the live-comparison task requires a material metric/selection-rule change after prospective review.

Changes after the first live comparison call must preserve consumed evidence and be recorded as prospective amendments, never silently backfilled.

## Regression obligations

Any future implementation under ADR-007 must continue to prove:

- non-audited DecisionSources produce no model-call events;
- audit metadata is allowlisted/flat and validated before trace insertion;
- no raw provider request/response, credential or exception text enters model-call telemetry;
- runtime identity/seed/action/evaluator-private state cannot enter audit metadata;
- one client invocation produces exactly one model-call record;
- adapter retry count remains zero and fallback remains false unless prospectively amended;
- call ID recomputation detects tampering;
- duplicate call IDs fail structural evaluation;
- successful model calls precede exactly one matching decision;
- failed model calls precede `DECISION_SOURCE_FAILURE` and have no decision;
- provider-free evaluation rejects any model-call event;
- traced-provider evaluation rejects missing/malformed/duplicate/inconsistent provenance;
- ADR-004 controller/tool ownership remains unchanged;
- B1 and ADR-005/B2 remain authoritative;
- provider/orchestration SDK imports stay outside neutral provenance/evaluator code;
- production runtime + ADR-004 controller regression suites stay green;
- a live comparison cannot begin before exact candidates, allowed population, metrics, hard gates, stopping rules and selection rule are prospectively frozen;
- provider calls remain zero until separately authorized;
- frozen scientific artifacts/gates cannot change as a side effect of provider telemetry.

## Sources

Repository evidence:

- issue #29
- PR #30
- ADR-004
- ADR-005
- ADR-006
- `research/e2/controller.py`
- `research/e2/models.py`
- `src/academy_tractian/decision_source.py`
- `src/academy_tractian/evaluation.py`
- `tests/test_model_call_provenance.py`
- `tests/test_model_call_provenance_duplicate.py`
- `research/provider-model-live-comparison-preregistration-2026-08-27.md`
- `production-runtime` Actions runs `33137274889` and `33137347455`
- E2–E8 Actions run `33137347432`

No external provider/model source is treated as selection evidence in this ADR because no concrete provider/model is selected or called. Current provider facts must be refreshed from official sources in the future separately authorized live-comparison task.
