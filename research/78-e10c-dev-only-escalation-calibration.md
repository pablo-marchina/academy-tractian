# E10c DEV-only Escalation Calibration

**Status:** READY_FOR_LOCAL_DEV_ONLY_CAPTURE  
**Date:** 2026-08-16  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why E10c exists

E10b strongly improved DEV-only private scoring, but escalation correctness remained 0.0.

Comparable DEV-only result:

| Metric | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only |
|---|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | 0.8571 |
| Decision correctness | 0.3333 | 0.3333 | 1.0 |
| Evidence correctness | 0.0 | 1.0 | 1.0 |
| Action correctness | 0.0 | 0.0 | 1.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 |

E10c keeps E10b's decision/evidence/action rules and focuses only on escalation calibration.

## DEV-only boundary

E10c may use only these DEV groups:

- `asset_G501`
- `asset_C710`
- `asset_S420`

E10c must not use VALIDATION for tuning and must not access LOCKED_TEST. Private expected paths stay scorer-only after outputs are fixed.

## Candidate policy change

E10c makes the human-escalation rule more explicit:

- human escalation is not mutually exclusive with action;
- `requires_human_escalation=true` is appropriate when an action must proceed through specialist/human handling;
- request-specialist and case-escalate endpoints imply human escalation;
- high-impact maintenance, safety/severity judgment, permission-sensitive execution, engineering approval or specialist review imply human escalation;
- generic uncertainty alone is still not enough for escalation.

## Acceptance target before full remeasurement

Do not promote E10c to full DEV+VALIDATION unless a DEV-only private scorer run shows all of the following:

- evidence correctness remains materially above the E9 DEV baseline;
- action correctness remains above 0.0;
- escalation correctness improves above 0.0;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible;
- no raw private oracles or fixed parsed outputs are committed.

## Local command

```powershell
python scripts/research/e10c_dev_only_escalation_capture.py `
  --manifest research/experiments/e10c-dev-only-escalation-calibration-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10c-dev-only-escalation-capture.json"
```

Then score it with the existing private scorer:

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10c-dev-only-escalation-capture.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e10c-dev-only-e9-private-score.json" `
  --include-rows
```

Do not commit the non-dry-run fixed outputs or private scorer rows.
