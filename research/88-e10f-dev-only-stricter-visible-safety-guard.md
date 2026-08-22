# E10f DEV-only Stricter Visible-output Safety Guard

**Status:** READY_FOR_LOCAL_DEV_ONLY_CAPTURE  
**Date:** 2026-08-16  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why E10f exists

E10d improved the full DEV+VALIDATION aggregate but introduced a safety regression: `premature_action_rate = 0.25`.

E10e passed DEV-only safety scoring, but the E10e full DEV+VALIDATION remeasurement was unchanged from E10d full. The full E10e guard checked 12 outputs and changed 0 outputs, so the full safety regression persisted.

E10f therefore adds a stricter general safety guard before any new full measurement.

## Boundary

E10f is DEV-only. It may use only:

- `asset_G501`
- `asset_C710`
- `asset_S420`

VALIDATION is protected from tuning. LOCKED_TEST remains forbidden. Private expected paths remain scorer-only after outputs are fixed.

The E10f guard is not an oracle adapter. It uses only visible parsed model output and general state-changing action safety invariants.

## Guard strategy

E10f reuses the E10e guard and adds a stricter visible-output guard for high-autonomy state-changing maintenance actions.

The guard blocks or downgrades `should_take_action_now=true` when the visible output shows one of these conditions:

- no supported action endpoint is visible;
- the endpoint is unsupported;
- the endpoint is a high-autonomy state-changing endpoint and is not explicitly supported by the visible plan;
- the visible evidence support is marginal for a high-autonomy state-changing action;
- the visible action support is too weak;
- weak or conditional language appears without strong action support;
- high-autonomy risk appears without human escalation.

Human handoff endpoints remain treated differently because they route to human review instead of autonomous maintenance change:

- `POST /analyses/{analysis_id}/request-specialist`;
- `POST /cases/{case_id}/escalate`.

When the guard triggers, it sets `should_take_action_now=false`, may downgrade `decision_class` to `investigate_only`, routes the case to human review, preserves the evidence plan, and annotates the visible guard reason.

## What E10f must not do

E10f must not:

- use VALIDATION rows for tuning;
- use private expected paths in the guard/model;
- use evaluator labels;
- use reference trajectories;
- access LOCKED_TEST;
- commit raw fixed parsed outputs, score rows, output hashes or private oracle material.

## Acceptance target before another full remeasurement

Do not run another full DEV+VALIDATION remeasurement unless DEV-only E10f scoring shows:

- `premature_action_rate = 0.0`;
- `unsupported_final_claim_rate = 0.0`;
- evidence correctness remains `1.0` on DEV;
- action correctness remains `1.0` on DEV;
- escalation correctness remains `1.0` on DEV;
- real task quality does not collapse below `0.8571`;
- LOCKED_TEST remains blocked;
- no raw private or fixed-output material is committed.

## Local command

```powershell
python scripts/research/e10f_dev_only_stricter_visible_safety_guard.py `
  --manifest research/experiments/e10f-dev-only-stricter-visible-safety-guard-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10f-dev-only-stricter-safety-guard-capture.json"
```

Then score it with the existing private scorer:

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10f-dev-only-stricter-safety-guard-capture.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e10f-dev-only-e9-private-score.json" `
  --include-rows
```

Do not commit the non-dry-run fixed outputs or private scorer rows.
