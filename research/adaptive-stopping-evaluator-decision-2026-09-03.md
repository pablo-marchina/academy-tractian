# Adaptive evidence/stopping evaluator decision — 2026-09-03

## Decision

Add a **DEV-only, evaluator-only replay diagnostic** that measures observed evidence-stopping headroom without changing the production runtime. This slice is allowed to identify the earliest tool-call prefix at which the frozen evidence oracle was satisfied, compare that prefix with the actually observed trace length, and report action-before-evidence violations. It is explicitly **not** allowed to authorize a stopping-policy promotion.

## Why evaluator-only first

The benchmark already contains `EvidenceOracle.required_groups`, per-group `minimum_satisfied`, free-text evidence predicates, `required_before_action`, and a `TrajectoryOracle` whose efficiency signal is diagnostic. Those contracts are sufficient to measure whether historical traces contain post-sufficiency calls, but they do not define a deployable runtime confidence score or stopping threshold.

A direct runtime change would therefore skip the required experiment boundary. The first question is narrower: **does measured headroom exist at all, and where?** Only after that result is frozen should a runtime-safe challenger be designed and compared against the current baseline.

## Predicate semantics

`EvidenceRequirement.predicate` is arbitrary evaluator text. The replay must never infer predicate satisfaction merely because a named tool appeared or returned a payload.

For every oracle requirement, an evaluator-private `EvidenceRequirementJudgment` explicitly records:

- group ID and requirement index;
- the exact `source` and `predicate` from the oracle;
- `SATISFIED`, `NOT_SATISFIED`, or `NOT_ASSESSABLE`;
- when satisfied, the **1-based ordinal of the tool call at which the predicate first became true**.

The judgment packet is frozen and SHA-256-bound to both the complete `RunTrace` and the scenario's evidence oracle. Missing requirements, altered predicates, changed traces, changed oracles, duplicate judgments, or impossible ordinals fail closed.

## Group sufficiency rule

Sufficiency is computed per required evidence group.

- If `minimum_satisfied` is an integer, the group becomes sufficient when that many requirements are satisfied.
- If `minimum_satisfied` is `None`, all requirements in the group are required. This is the conservative interpretation; `None` is never treated as zero or one.
- An empty required group or a minimum greater than its requirement count is invalid and fails closed.
- `NOT_ASSESSABLE` does not automatically block a group if enough other requirements already satisfy the group's minimum. It blocks a sufficiency conclusion only when the minimum cannot otherwise be established.

The globally sufficient prefix is the maximum of the first sufficient ordinal for every required group. A scenario with no required evidence groups is `NOT_ASSESSABLE`, not a zero-headroom success.

## Headroom estimand

For a case where a sufficient prefix is observed:

`post_sufficiency_tool_calls = observed_tool_call_count - earliest_sufficient_tool_call_ordinal`

and:

`headroom_fraction = post_sufficiency_tool_calls / observed_tool_call_count`

These are replay diagnostics only. Calls after evidence sufficiency are **not automatically labeled waste**: they may serve policy, action execution, confirmation, communication, or other runtime obligations that the evidence oracle does not encode.

The aggregate report therefore uses the language `HEADROOM_OBSERVED`, never `optimization_proven` or equivalent.

## Action guard diagnostic

For requirements marked `required_before_action=true`, the evaluator separately identifies the first action `tool_call` using the frozen 18-operation tool registry.

A violation is counted when the requirement is not established strictly before that first action. This is a diagnostic guard signal; this slice does not invent a new production policy from it.

Unknown tools or malformed `tool_call` events fail closed rather than being silently classified.

## Split and freeze boundary

The experiment is **DEV-only**.

- the benchmark split manifest must have `status=FROZEN`;
- the exact scenario selection is separately frozen and hash-bound;
- replay cases must match that selection exactly;
- VALIDATION and LOCKED_TEST scenarios are rejected;
- LOCKED_TEST remains unavailable for stopping-policy, threshold, prompt, model, architecture, or evaluator tuning.

The hashes provide integrity and reproducibility of the supplied artifacts. They do **not** prove when a human froze the files. Operational procedure must still freeze selection and judgments before using the diagnostic result to motivate a challenger.

## Output boundary

`scripts/adaptive_stopping_report.py` is a trusted/offline CLI. Its input bundle may contain evaluator-private scenarios, traces, and predicate judgments. Its persisted output contains only aggregate diagnostics and case indices; it does not copy scenario IDs, predicates, raw tool results, provider payloads, private truth, or chain-of-thought.

The result always carries:

- `promotion_ready=false`;
- `runtime_policy_change_authorized=false`;
- `business_claim_ready=false`;
- `requires_runtime_challenger_experiment=true`.

Thus even a `HEADROOM_OBSERVED` result is only evidence that a runtime challenger may be worth testing.

## Status interpretation

- `NOT_READY`: no selected case has an observed sufficient prefix.
- `PARTIAL_DIAGNOSTIC`: at least one selected case has a sufficient prefix, but at least one other case is insufficient or not assessable.
- `HEADROOM_OBSERVED`: every selected case has a sufficient prefix and at least one post-sufficiency tool call is observed.
- `NO_HEADROOM_OBSERVED`: every selected case has a sufficient prefix and no post-sufficiency tool call is observed.

No threshold for "enough headroom" is introduced in this slice.

## What must happen before any runtime promotion

A later experiment must define a deployable, oracle-free stopping signal available at runtime and compare it against the unchanged baseline on paired DEV runs. Promotion may proceed only if the challenger reduces calls/latency materially **without** regressing operational conclusion correctness, evidence correctness/sufficiency, escalation behavior, action safety, authorization, duplicate-action safety, tenant isolation, or communication safety. VALIDATION is then used only after the challenger and promotion rule are frozen; LOCKED_TEST remains untouched until the final locked evaluation.

## Current evidence state

The contract, synthetic tests, trusted CLI and CI gate in this slice are engineering instrumentation only. **No real stopping headroom measurement, runtime efficiency improvement, or production-policy claim is asserted by this repository change.**
