# Production provider/model live-comparison preregistration — 2026-08-27

Status: `PREREGISTERED / PROVIDER_FREE_ONLY`
Issue: #29
ADR: ADR-007
Scientific state changed: `NO`
Provider/model calls authorized by this document: `0`
Production provider/model selected: `NO`
Production actions enabled: `NO`

## Purpose

Freeze the evidence contract that must be satisfied **before** any production provider/model comparison can make a selection claim. This document does not authorize or execute a live request and does not rank candidate models.

ADR-004 owns the application-side agent loop. ADR-006 owns the provider-neutral `DecisionSource` adapter. ADR-007 freezes the sanitized model-call provenance contract and accepts this preregistration. This document governs only a later serving-route/model comparison behind that adapter.

## Hard boundaries

The later comparison must preserve all of the following:

- `AgentController` owns the bounded decision/tool loop;
- `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary;
- B1 remains the sole canonical known-tool argument-validation owner;
- ADR-005/B2 remains the sole consequential-action authorization owner;
- production mutating actions remain disabled unless a separate future decision explicitly enables them;
- provider-visible context contains no runtime identity, seed, action authorization/idempotency/scope state, config hash or evaluator-private/gold truth;
- exactly one provider-client invocation per `DecisionSource.decide()` call under the default comparison contract;
- automatic retries: `0` unless prospectively amended before execution;
- provider/model fallback: `0` unless prospectively amended before execution;
- every attempted provider invocation must produce one sanitized `model_call` provenance event before its corresponding controller decision or fail-closed terminal state;
- no raw provider request/response, credential, exception text or private evaluator material may be serialized into `RunTrace` or evaluation reports.

## Candidate-set rule

Immediately before any live authorization, freeze exact current identifiers and serving routes for at least:

1. **provider-free scripted/null baseline** — deterministic contract lower bound; no live model inference;
2. **quality-frontier candidate** — a currently available strong general reasoning/tool-use model suitable for the task;
3. **lower-cost/local/open candidate** — a feasible alternative representing materially lower resource/cost or self-hostability;
4. **additional candidate only when it represents a distinct credible Pareto trade-off** not already covered above.

Historical C4 provider qualification is not a production-provider prior and cannot bypass this candidate-set rule.

No concrete live candidate/model ID is frozen in this task because provider calls remain unauthorized and time-sensitive provider facts must be refreshed from official sources immediately before a future authorization.

## Exact route identity to freeze before execution

For every live candidate, record before the first call:

- provider identifier;
- exact model identifier/version exposed by the serving route;
- route/API identifier;
- hosting class: hosted API, local, or self-hosted;
- relevant structured-output/tool-use capability relied upon;
- context/output limits relevant to the frozen request contract;
- pricing/resource basis used for accounting, when applicable;
- known availability/region/account constraints;
- exact client implementation commit;
- retry/fallback policy;
- whether the call is marked `live_call=true` in trace provenance.

Any material route/model change after execution begins is a new candidate or requires a prospective amendment; it must not be silently pooled.

## Evaluation population

A later task must freeze an **allowed development-only population** before live execution. It must not include FRESH_BLIND, LEGACY_LOCKED_TEST or private/gold evaluator content unless a separate scientific gate explicitly authorizes such access.

The population freeze must record:

- exact public/development input identities and hashes;
- scenario/task categories covered;
- number of independent units;
- deterministic ordering or randomized order + seed;
- maximum provider calls per unit;
- stop conditions and terminal operational-failure rules;
- explicit exclusions.

## Primary measurements

All formulas, denominators and pass/fail thresholds must be frozen before the first live request.

### M1 — Structured-decision adherence

Denominator: all provider invocations.

Pass event: response is accepted by `ProviderDecisionPayload` and maps to exactly one existing `ControllerDecision` without adapter repair.

Report:

- accepted / attempted;
- malformed JSON;
- duplicate-key/non-object JSON;
- payload-shape invalid;
- unknown-tool output;
- proposal rejected by model-binding guard.

### M2 — Known-tool selection validity

Denominator: provider decisions with `kind=TOOL`.

Pass event: selected `tool_name` exists in the frozen canonical 18-operation registry.

Unknown tools remain fail-closed; no alias repair is allowed during the frozen comparison.

### M3 — Canonical argument validity / B1 containment

Denominator: known-tool proposals.

Report separately:

- proposals passing canonical B1 argument validation;
- proposals contained as `ARGUMENT_INVALID`;
- identity/seed-control attempts rejected before tool execution.

Do not duplicate or weaken B1 validation in provider-specific code.

### M4 — Allowed-development task quality

The future authorization must freeze deterministic/public or otherwise explicitly permitted task-quality measures before execution. Semantic/judge scoring is not implicitly authorized by this preregistration.

If semantic judging is later proposed, it requires its own custody, reliability and authorization evidence before use.

### M5 — Safe failure behavior

Denominator: provider/client/parsing failures plus deliberately injected failure cases.

Pass conditions must include:

- no unauthorized tool transport;
- `DECISION_SOURCE_FAILURE` safe abstention for provider/source failures;
- sanitized `model_call` failure provenance before terminal abstention;
- no exception/request/response leakage in trace or final response;
- no hidden retry/fallback.

### M6 — Latency

Record per invocation using the adapter-owned elapsed timer and report at minimum:

- count;
- median;
- p90;
- p95;
- maximum;
- failures separately from successes.

Warm-up policy must be frozen in advance; hidden warm-up calls are forbidden.

### M7 — Reliability

Report exact attempted/success/failure counts and provider-visible failure families. Do not delete failed attempts from denominators.

Repeated-run stability, if measured, must preregister repetitions and seeds before execution.

### M8 — Usage/resource/cost

Where the serving route exposes reliable accounting, record provider-reported usage or local measured resource evidence in a separate sanitized artifact linked by call ID. Do not infer missing token/cost numbers.

Report zero/unknown explicitly rather than fabricating estimates.

### M9 — Portability / operational constraints

Record qualitative but evidence-backed constraints including:

- provider SDK dependency or HTTP portability;
- credential/account requirements;
- hosting requirements;
- rate/capacity constraints observed during the run;
- reproducibility limitations;
- local/self-hosted hardware burden where applicable.

### M10 — Trace integrity

Every attempted invocation must have exactly one valid `provider-model-call-v1` event with:

- deterministic canonical `call_id`;
- provider/model/route identifiers;
- request SHA-256;
- response SHA-256 when a string response exists;
- turn/tool-call counters;
- outcome or sanitized failure code;
- measured latency;
- client invocation count = 1;
- retry count = 0;
- fallback = false;
- raw request/response/exception recording flags = false.

The event must precede its matching controller `decision`; a failed event must precede terminal `DECISION_SOURCE_FAILURE` and have no matching controller decision.

## Selection rule to freeze later

No winner rule is frozen yet because the exact candidate set and allowed-development task-quality metric are not authorized here. Before live execution, the comparison task must freeze a deterministic selection rule that:

- treats hard safety/trace-contract violations as disqualifying rather than compensable by quality;
- does not silently drop operational failures;
- distinguishes quality-frontier and cost/resource trade-offs;
- defines tie/indifference handling;
- permits `NO_SELECTION` when evidence is insufficient or all candidates violate hard requirements.

A live comparison must not retroactively choose thresholds after seeing candidate results.

## Stopping / amendment rules

Stop and freeze an operational failure without ranking if:

- required provenance cannot be recorded safely;
- provider behavior would require hidden retry/fallback or contract repair not preregistered;
- custody boundaries are violated;
- the serving model/route changes materially mid-run;
- the allowed call budget is exhausted before the preregistered evidence packet completes.

Any change to candidate set, retry/fallback policy, evaluation population, hard gate or selection rule after the first live call requires a prospective amendment preserving the already-consumed evidence.

## Current non-authorization

As of this preregistration:

```text
real provider/model calls                  0
provider/model selected                    NO
live candidate identifiers frozen          NO
production mutating actions enabled        NO
scientific gate changed                    NO
semantic evaluation authorized             NO
FRESH_BLIND access authorized              NO
LEGACY_LOCKED_TEST access authorized       NO
production-readiness claim                 NO
global architecture freeze                 NO
```

ADR-007 freezes this preregistration and the model-call provenance contract. The next admissible provider-comparison step is a **separate future governed task** that refreshes official current provider/model facts, freezes exact candidates, allowed development population, hard gates and the deterministic selection rule, and obtains explicit authorization before the first live request.
