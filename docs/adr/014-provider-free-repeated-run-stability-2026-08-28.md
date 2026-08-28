# ADR-014 — Provider-free repeated-run stability

**Date:** 2026-08-28  
**Status:** FROZEN FOR EV-008 PROVIDER-FREE STABILITY SCOPE  
**Tracks:** #51 / PR #52  
**Supersedes:** nothing

## Decision

Freeze EV-008 as a deterministic provider-free repeated-run stability campaign over the accepted production/controller/action/evaluator boundaries.

The frozen geometry is:

```text
stability units              6
repetitions per unit         5
provider-free runs          30
stability dimensions        11
unit × dimension checks     66
provider calls               0
real customer mutations      0
```

The exact campaign version is `ev008-provider-free-stability-campaign-v1`.

## Frozen population

The population was preregistered before interpretation:

1. `STAB-01` — read/investigate: canonical `get_asset` call followed by `ORIENT`;
2. `STAB-02` — clarification: `ASK_CLARIFICATION / MISSING_CONTEXT`;
3. `STAB-03` — safe abstention: `ABSTAIN / NO_SAFE_PATH`;
4. `STAB-04` — human escalation: `ESCALATE_HUMAN / HUMAN_REVIEW_REQUIRED`;
5. `STAB-05` — one fully authorized `reprocess_analysis` action with deterministic supplied `202 {"accepted": true}` transport;
6. `STAB-06` — deterministic read-transport exception contained as `ABSTAIN / TOOL_BOUNDARY_FAILURE`.

Every unit runs exactly five times.

For `STAB-05`, each repetition receives a fresh durable claim root. The action arguments, action fingerprint, authorization semantics and raw idempotency key remain equivalent across repetitions. This isolates per-run custody so a prior repetition cannot turn the next repetition into a duplicate-action test.

## Frozen dimensions

Each unit compares all repetitions independently on:

1. terminal signature;
2. ordered tool selection;
3. canonical arguments;
4. action fingerprint;
5. ordered policy outcomes;
6. evaluator pass/fail classification;
7. terminal/failure reason code;
8. normalized behavioral trace;
9. final response;
10. sensitive leak count;
11. retry/replay count.

No weighted aggregate score is introduced.

## Normalization boundary

The normalized behavioral trace excludes only top-level per-execution `run_id` / `scenario_id` identity by constructing its signature from stable trace fields and the full event sequence.

It does **not** normalize away:

- tool selection;
- canonical arguments;
- action fingerprint;
- B1/B2 policy outcomes;
- terminal decision/reason;
- evaluator classification;
- final response content;
- executed trace events.

The test suite deliberately alters terminal, tool, argument, evaluator and final-response signatures and requires the unit summary to detect instability.

## Exact provider-free result

The dedicated validator reproduced:

```text
EV008_VALIDATION                      PASS
report SHA-256                        1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
runs                                  30 / 30
stable units                           6 / 6
stable dimension checks              66 / 66
contract expectations                30 / 30
raw sensitive leaks                    0
automatic retries                      0
replays                                0
provider calls                         0
real customer mutations                0
```

The compact immutable result manifest is:

`research/results/ev008-provider-free-stability-campaign-result-2026-08-28.json`

It records the global report SHA plus all six unit spec/summary hashes. The freeze self-check reruns the complete 30-run campaign and requires exact reproduction of the global report SHA and all six summary hashes.

## Validation history

Initial implementation head `80e74a99ab68cc9d2a33f586360e0eae6bf180ec` passed:

- 195 production tests;
- 12 ADR-004 controller regressions;
- 11/11 triggered workflows.

The first dedicated-validator head `a404cd9efca635c8d4740a5a7479ca610e4bf24c` failed before campaign execution because direct `python scripts/...` execution did not place the repository root on `sys.path`, so `research.e2` could not be imported. This was an operational validator defect, not a stability result.

The validator was corrected by applying the same checkout-executable root bootstrap already used by the frozen EV-007 validator. No stability unit, repetition count, expected behavior or metric changed.

Corrected head `a88b98e53e2767a5f85290082896f3c9b4d93cd4` passed:

- `ev008-repeated-run-stability #2` — PASS;
- report SHA exactly `1542a7cb...`;
- production-runtime #63 — 195 passed;
- ADR-004 regression — 12 passed;
- 12/12 triggered workflows — success.

## Preserved boundaries

ADR-014 does not change ADR-004, ADR-005, ADR-006, ADR-007, ADR-012 or ADR-013 semantics.

It does not authorize:

- any ADR-009 live call;
- credential/account probing;
- provider/model selection;
- real customer mutation;
- default `ProductionRuntime` action enablement;
- C4 reconstruction/rescoring or scientific-gate advancement;
- semantic/private/blind evaluation;
- a production-readiness claim.

The default `ProductionRuntime` remains action-disabled. `STAB-05` is capability evidence through `ControlledActionRuntime` and deterministic supplied/test transport only.

## Interpretation

This result establishes deterministic reproducibility of the provider-free runtime/harness/evaluator boundary for the frozen scenarios. It does **not** establish live-model behavioral stability or live provider quality.

The same metric definitions should be reused later against a governed selected provider without changing them after observing live results.

## Change rule

Any change to the six-unit population, five-repetition geometry, normalization boundary, metric definitions or expected semantics after this freeze requires a prospective ADR/amendment and new evidence identity. Historical ADR-014 evidence remains immutable.
