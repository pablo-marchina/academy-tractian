# E10e DEV-only Premature-action Safety Guard

**Status:** READY_FOR_LOCAL_DEV_ONLY_CAPTURE  
**Date:** 2026-08-16  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why E10e exists

E10d passed DEV-only private scoring and then improved full DEV+VALIDATION aggregate task quality. However, the full remeasurement revealed a safety regression: `premature_action_rate` increased from `0.0` to `0.25`.

That blocks promotion even though average quality improved. E10e therefore targets premature-action safety before any new full remeasurement.

## Boundary

E10e is DEV-only. It may use only:

- `asset_G501`
- `asset_C710`
- `asset_S420`

VALIDATION is protected from tuning. LOCKED_TEST remains forbidden. Private expected paths remain scorer-only after outputs are fixed.

The E10e guard is not an oracle adapter. It uses only visible parsed model output and general safety invariants.

## Guard strategy

E10e keeps the E10d visible-output escalation guard and adds a second visible-output safety guard.

The safety guard blocks or downgrades `should_take_action_now=true` when the model's own visible output indicates one of these unsafe conditions:

- the visible rubric says `needs_more_evidence=true`;
- the visible rubric says `safe_to_act=false`;
- no supported state-changing endpoint is visible;
- the visible endpoint is unsupported;
- the output text itself says evidence is insufficient, missing, low-confidence or inconclusive;
- the evidence plan is too sparse for a state-changing maintenance action;
- the decision class conflicts with immediate state-changing action.

When the guard triggers, it sets `should_take_action_now=false`, may downgrade `decision_class` from `action_candidate` to `investigate_only`, preserves the evidence plan, and preserves human escalation if review is still needed.

## What E10e must not do

E10e must not:

- use VALIDATION rows for tuning;
- use private expected paths in the guard/model;
- use evaluator labels;
- use reference trajectories;
- access LOCKED_TEST;
- commit raw fixed parsed outputs, score rows, output hashes or private oracle material.

## Acceptance target before another full remeasurement

Do not run another full DEV+VALIDATION remeasurement unless DEV-only E10e scoring shows:

- `premature_action_rate = 0.0`;
- `unsupported_final_claim_rate = 0.0`;
- evidence correctness remains above the E9 DEV baseline;
- action correctness remains above the E9 DEV baseline;
- escalation correctness remains at least comparable to the E9 full baseline;
- real task quality does not collapse;
- LOCKED_TEST remains blocked;
- no raw private or fixed-output material is committed.

## Local command

```powershell
python scripts/research/e10e_dev_only_premature_action_guard.py `
  --manifest research/experiments/e10e-dev-only-premature-action-safety-guard-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10e-dev-only-premature-action-guard-capture.json"
```

Then score it with the existing private scorer:

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10e-dev-only-premature-action-guard-capture.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e10e-dev-only-e9-private-score.json" `
  --include-rows
```

Do not commit the non-dry-run fixed outputs or private scorer rows.
