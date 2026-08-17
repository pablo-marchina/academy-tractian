# E14 Preregistered Completeness-Preserving Selective Reprocess Boundary

**Status:** E14_PREREGISTERED_COMPLETENESS_SELECTIVE_REPROCESS_BOUNDARY  
**Date:** 2026-08-16  
**Scope:** preregistration only  
**Implementation:** false  
**Demo:** false  
**Integration:** false  
**Full rerun:** false  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Purpose

E14 preregisters the only next candidate class allowed after the E13 blocker audit.

E13 implemented the reprocess-specific authorization boundary, but it failed DEV-only acceptance. The E13 blocker audit found two simultaneous DEV blockers:

1. **Completeness blocker:** one DEV call lacked a parsed output.
2. **Selectivity blocker:** the boundary changed every parsed target reprocess action, causing action collapse and decision regression.

E14 does not implement anything yet. It only preregisters a later candidate that must address both blockers at the same time, without VALIDATION tuning.

## E13 blocker audit basis

The E13 blocker audit identified these root-cause classes:

```text
parsed_output_missing_in_dev_capture
boundary_changed_all_target_reprocess_actions
action_collapse_consistent_with_overblocking_reprocess_boundary
decision_regression_after_reprocess_downgrade
```

Observed sanitized facts:

| Finding | Value |
|---|---:|
| DEV calls observed | 6 |
| Parsed DEV outputs | 5 |
| Missing parsed outputs | 1 |
| Target reprocess rows | 5 |
| Changed rows | 5 |
| Authorized rows | 0 |
| VALIDATION calls read | 0 |
| LOCKED_TEST accessed | false |

Dominant boundary reason:

```text
missing_endpoint_specific_reprocess_defect_evidence=5
```

## Preregistered change

```text
completeness_preserving_selective_reprocess_authorization
```

This change must address both blockers:

```text
1. Completeness: guarantee 6/6 parsed DEV outputs before DEV acceptance.
2. Selectivity: do not block every correct reprocess action; preserve action when visible support is sufficient while keeping premature_action_rate = 0.0.
```

## Completeness rule

A later E14 DEV-only candidate must produce:

```text
fixed_calls_consumed = 6
parsed_model_outputs_available = 6
scoreable_calls = 6
```

Allowed mechanisms:

- retry only failed model calls or parse failures inside the fixed DEV run;
- deterministic JSON/schema repair only when no semantic field is invented;
- sanitized retry/repair counters in the capture;
- fail closed if 6/6 parsed outputs are not achieved.

Forbidden mechanisms:

- using private oracle values to repair or complete outputs;
- using VALIDATION examples or feedback;
- using LOCKED_TEST material;
- committing raw fixed outputs, output hashes, score rows or local private paths.

## Selectivity rule

E13 was too strict because it required endpoint-specific defect phrases and therefore blocked all parsed DEV target reprocess actions.

E14 must not authorize reprocess from generic evidence-family counts or generic human-review markers alone. However, E14 may authorize `POST /analyses/{analysis_id}/reprocess` when visible public/runtime evidence contains concrete support anchors for that exact reprocess action.

### Required support for reprocess authorization

All of these must be present:

- exact endpoint: `POST /analyses/{analysis_id}/reprocess`;
- visible analysis identifier or analysis resource reference;
- visible asset or case identifier;
- proposed action limited to reprocess, without `PATCH /assets/{asset_id}`, model retraining or other higher-risk mutation;
- human-readable reason linking visible evidence to reprocess, not merely naming the endpoint.

At least two of these must also be present:

- concrete sensor/RMS/spectrum/baseline/data-quality observation;
- explicit uncertainty or incompleteness about the current diagnosis that reprocess can resolve;
- stale, failed, unreliable or incomplete analysis signal;
- mismatch between current evidence and the existing analysis conclusion;
- case/user request context asking for updated or recomputed analysis;
- knowledge or model context indicating reprocess is the low-risk next diagnostic action.

### Block conditions

E14 must still block or downgrade reprocess when any of these is true:

- parsed output missing;
- exact reprocess endpoint missing;
- visible analysis/resource identifier missing;
- only generic evidence-family count is present;
- only generic human-review language is present;
- the action includes higher-risk endpoints or asset/model mutation;
- the output cannot explain why reprocess is the next action from visible evidence.

## Acceptance before any full rerun

A later E14 candidate must pass DEV-only before any full DEV+VALIDATION measurement is prepared:

| Target | Required |
|---|---:|
| Parsed outputs | 6 |
| Scoreable calls | 6 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| Real task quality | >= 0.8571 |
| Decision correctness | >= 0.75 |
| Action correctness | >= 0.75 |
| Evidence correctness | 1.0 |
| Escalation correctness | 1.0 |
| LOCKED_TEST accessed | false |

## Boundary

E14 is preregistration only. It does not authorize integration, demo, a full rerun, a new product, final architecture freeze or implementation outside the described candidate class.

The next allowed step is to implement only this preregistered DEV-only candidate.

No VALIDATION tuning. No private expected paths in model or policy. No raw fixed outputs, score rows, output hashes, private local paths, validation feedback, evaluator labels, reference trajectories, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet` or LOCKED_TEST.
