# E10d Full DEV+VALIDATION Remeasurement

**Status:** READY_FOR_LOCAL_FULL_CAPTURE  
**Date:** 2026-08-16  
**Scope:** DEV + VALIDATION measurement  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why this gate exists

E10d passed the DEV-only private scorer target:

| Metric | E10d DEV-only |
|---|---:|
| Real task quality | 1.0 |
| Decision correctness | 1.0 |
| Evidence correctness | 1.0 |
| Action correctness | 1.0 |
| Escalation correctness | 1.0 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| Proxy-vs-real disagreement rate | 0.0 |

That allows a full DEV+VALIDATION remeasurement of the same candidate. It does not freeze the model, provider or architecture.

## Boundary

The full remeasurement may run DEV and VALIDATION, but VALIDATION is measurement-only. No tuning or prompt/policy adjustment may be made from VALIDATION results.

LOCKED_TEST remains forbidden.

The model and visible-output guard must not receive:

- private expected paths;
- evaluator labels;
- reference trajectories;
- validation feedback;
- locked-test material;
- raw private oracle rows.

The guard operates only on parsed visible model output and visible consistency policy.

## Remeasurement split groups

DEV:

- `asset_G501`
- `asset_C710`
- `asset_S420`

VALIDATION:

- `asset_B204`
- `asset_M102`

Default repeats preserve the original E8/E9 full measurement shape:

- DEV: 2 repeats per group;
- VALIDATION: 3 repeats per group.

## Local capture command

```powershell
python scripts/research/e10d_full_dev_validation_capture.py `
  --manifest research/experiments/e10d-full-dev-validation-remeasurement-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10d-full-dev-validation-capture.json"
```

## Private scorer command

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10d-full-dev-validation-capture.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e10d-full-dev-validation-e9-private-score.json" `
  --include-rows
```

Do not commit the non-dry-run fixed outputs, score rows, raw private oracles, output hashes or expected-path values.

## Acceptance target

E10d may move to later integration gates only if full DEV+VALIDATION private scoring shows:

- real task quality above the original E9 full baseline of 0.631;
- evidence correctness above the original E9 full baseline of 0.0;
- action correctness above the original E9 full baseline of 0.25;
- escalation correctness above the original E9 full baseline of 0.5;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible;
- no final architecture/model/provider freeze is claimed.
