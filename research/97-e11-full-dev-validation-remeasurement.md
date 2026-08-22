# E11 Full DEV+VALIDATION Remeasurement

**Status:** E11_FULL_DEV_VALIDATION_REMEASUREMENT_READY  
**Date:** 2026-08-16  
**Scope:** DEV + VALIDATION measurement only  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why this exists

E11 passed the DEV-only independent action-authorization gate after E10h identified the blocker: model self-attested action safety was being treated as sufficient authorization.

This full remeasurement checks whether E11 generalizes to DEV + VALIDATION and restores the full `premature_action_rate` from `0.25` to `0.0` without using VALIDATION for tuning.

## Boundary

The full runner measures DEV + VALIDATION only.

It must not expose the following to the model or policy:

- private expected paths;
- evaluator labels;
- reference trajectories;
- validation feedback;
- raw scorer rows;
- `eval/expected-paths.json`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST material.

Private expected paths may be read only by the local E9 v3 scorer after fixed outputs exist.

## Candidate under remeasurement

E11 applies independent action authorization after the E10g full capture path. The policy does not trust `safe_to_act=true` as sufficient authorization. It checks:

- supported endpoint classification;
- human handoff/review path vs autonomous state-changing maintenance;
- required endpoint identifiers;
- endpoint-specific evidence-family sufficiency;
- human review/escalation support for autonomous state-changing actions;
- policy explanation for action authorization.

## Expected local capture

The full run should execute 12 calls:

- DEV: 3 representative groups × 2 repeats = 6 calls;
- VALIDATION: 2 representative groups × 3 repeats = 6 calls.

The capture file is private working output and must not be committed.

## How to run locally

```powershell
$E11_FULL_CAPTURE = "$env:TEMP\e11-full-dev-validation-capture.json"

python scripts/research/e11_full_dev_validation_capture.py `
  --manifest research/experiments/e11-full-dev-validation-remeasurement-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out $E11_FULL_CAPTURE

Test-Path $E11_FULL_CAPTURE
```

Then score after outputs are fixed:

```powershell
$E11_FULL_SCORE = "$env:TEMP\e11-full-dev-validation-e9-private-score.json"

python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file $E11_FULL_CAPTURE `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out $E11_FULL_SCORE `
  --include-rows

Get-Content $E11_FULL_SCORE
```

## Required comparison

Compare full E11 against:

- E9 full baseline;
- E10d full;
- E10e full;
- E10g full;
- E11 DEV-only.

Known full baseline context:

```text
E9 full baseline → E10d full → E10e full → E10g full
real_task_quality:       0.631  → 0.8214 → 0.8214 → 0.8214
decision_correctness:    0.6667 → 0.75   → 0.75   → 0.75
evidence_correctness:    0.0    → 0.75   → 0.75   → 0.75
action_correctness:      0.25   → 0.75   → 0.75   → 0.75
escalation_correctness:  0.5    → 0.5    → 0.5    → 0.5
premature_action_rate:   0.0    → 0.25   → 0.25   → 0.25
unsupported_claim_rate:  0.0    → 0.0    → 0.0    → 0.0
proxy_disagreement_rate: 1.0    → 0.5    → 0.5    → 0.5
```

## Acceptance target

Only consider integration if full E11 meets all of the following:

- `real_task_quality > 0.631`;
- `premature_action_rate = 0.0`;
- `unsupported_final_claim_rate = 0.0`;
- `evidence_correctness > 0.0`;
- `action_correctness >= 0.25`;
- `escalation_correctness >= 0.5`;
- LOCKED_TEST remains blocked;
- no raw private or fixed-output material is committed.

## Gate decision pending

E11 full is ready to run locally, but it has not yet produced a real full private score.

Do not promote to integration until the full measurement is scored and passes the safety gate.
