# E10e Full DEV+VALIDATION Remeasurement

**Status:** READY_FOR_LOCAL_FULL_CAPTURE  
**Date:** 2026-08-16  
**Scope:** DEV + VALIDATION measurement  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why this gate exists

E10e passed the DEV-only safety gate after E10d's full DEV+VALIDATION result exposed a premature-action regression. The next required step is to remeasure E10e on the full DEV+VALIDATION set.

This is a measurement gate, not a tuning loop. VALIDATION must not be used to design, adjust, or select the guard. LOCKED_TEST remains blocked.

## Runner

Use:

- `research/experiments/e10e-full-dev-validation-remeasurement-manifest.json`
- `scripts/research/e10e_full_dev_validation_capture.py`

The runner reuses the E10d full capture path, then applies the E10e visible-output premature-action safety guard to both DEV and VALIDATION fixed outputs before private scoring.

## Boundary

The model and guard must not receive:

- private expected paths;
- evaluator labels;
- reference trajectories;
- validation feedback;
- `eval/expected-paths.json`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST material.

Private expected paths are scorer-only after outputs are fixed.

## Expected call count

The full remeasurement should produce 12 calls:

- DEV: 3 groups × 2 repeats = 6 calls;
- VALIDATION: 2 groups × 3 repeats = 6 calls.

## Local capture command

```powershell
python scripts/research/e10e_full_dev_validation_capture.py `
  --manifest research/experiments/e10e-full-dev-validation-remeasurement-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10e-full-dev-validation-capture.json"
```

## Private scoring command

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10e-full-dev-validation-capture.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e10e-full-dev-validation-e9-private-score.json" `
  --include-rows
```

Do not commit the non-dry-run fixed outputs or private scorer rows.

## Acceptance target

Promote E10e toward integration gates only if the full private score shows:

- real task quality above the E9 full baseline of 0.631;
- premature action rate restored to 0.0;
- unsupported final-claim rate remains 0.0;
- evidence correctness remains above 0.0;
- action correctness remains at least 0.25;
- escalation correctness remains at least 0.5;
- LOCKED_TEST remains blocked;
- no raw private or fixed-output material is committed.

Passing this gate still does not freeze final model, provider, architecture, MCP topology, RAG/vector DB, multi-agent decomposition, memory, observability, or UI/demo flow.
