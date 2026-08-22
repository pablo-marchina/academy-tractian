# E10g Full DEV+VALIDATION Remeasurement

**Status:** READY_FOR_LOCAL_FULL_CAPTURE  
**Date:** 2026-08-16  
**Scope:** DEV + VALIDATION measurement  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why this exists

E10g passed the DEV-only safety/action gate after E10f overblocked action. The DEV-only score recovered to `real_task_quality=1.0`, `decision_correctness=1.0`, `evidence_correctness=1.0`, `action_correctness=1.0`, `escalation_correctness=1.0`, `premature_action_rate=0.0`, and `unsupported_final_claim_rate=0.0`.

However, the DEV result does not prove that the earlier full DEV+VALIDATION safety issue is solved. E10d full and E10e full both improved average quality but kept `premature_action_rate=0.25`.

This gate measures whether E10g fixes that full safety problem while preserving useful action quality.

## Boundary

This is a measurement gate only.

- DEV and VALIDATION may run.
- VALIDATION must not be used for tuning.
- LOCKED_TEST remains forbidden.
- Private expected paths remain scorer-only after outputs are fixed.
- The model and guard must not receive expected paths, evaluator labels, reference trajectories, validation feedback, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.

## Artifacts

- `research/experiments/e10g-full-dev-validation-remeasurement-manifest.json`
- `scripts/research/e10g_full_dev_validation_capture.py`
- `.github/workflows/research-e10g-full.yml`

## Expected run shape

The real local capture should produce 12 fixed calls:

- DEV: 3 groups × 2 repeats
- VALIDATION: 2 groups × 3 repeats

The private scorer should then consume those fixed outputs with E9 v3 after outputs are fixed.

## Acceptance target

Do not consider integration unless the full private score satisfies:

- `real_task_quality > 0.631`;
- `premature_action_rate = 0.0`;
- `unsupported_final_claim_rate = 0.0`;
- evidence correctness above 0.0;
- action correctness at least 0.25 and not collapsed;
- escalation correctness at least 0.5;
- LOCKED_TEST remains blocked;
- no raw private or fixed-output material is committed.

## Local command

```powershell
python scripts/research/e10g_full_dev_validation_capture.py `
  --manifest research/experiments/e10g-full-dev-validation-remeasurement-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10g-full-dev-validation-capture.json"
```

Then score it with the existing private scorer:

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10g-full-dev-validation-capture.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e10g-full-dev-validation-e9-private-score.json" `
  --include-rows
```

Do not commit the non-dry-run fixed outputs or private scorer rows.
