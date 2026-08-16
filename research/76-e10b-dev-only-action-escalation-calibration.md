# E10b DEV-only Action/Escalation Calibration

**Status:** READY_FOR_LOCAL_DEV_ONLY_CAPTURE  
**Date:** 2026-08-16  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why E10b exists

E9 showed that the E8 proxy/schema success was over-optimistic. E10 then improved the first bottleneck, evidence grounding, but did not improve action or escalation calibration.

Comparable DEV-only result:

| Metric | E9 DEV-only baseline | E10 DEV-only | Delta |
|---|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | +0.1428 |
| Decision correctness | 0.3333 | 0.3333 | 0.0 |
| Evidence correctness | 0.0 | 1.0 | +1.0 |
| Action correctness | 0.0 | 0.0 | 0.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 |

E10b therefore keeps the evidence-first prompt policy and adds explicit action/escalation calibration rules.

## DEV-only boundary

E10b may use only these DEV groups:

- `asset_G501`
- `asset_C710`
- `asset_S420`

E10b must not use VALIDATION for tuning and must not access LOCKED_TEST. Private expected paths stay scorer-only after outputs are fixed.

## Candidate policy change

The E10b capture runner adds an explicit `action_escalation_rubric` to the model output:

- `needs_more_evidence`
- `safe_to_act`
- `action_endpoint`
- `needs_human_escalation`
- `calibration_reason`

The model must fill this rubric before setting:

- `decision_class`
- `should_take_action_now`
- `requires_human_escalation`

The rubric is not private-oracle-derived. It is a general visible-evidence decision discipline.

## Action calibration

The runner asks the model to set `should_take_action_now=true` only when the visible packet supports a concrete safe endpoint:

- `POST /analyses/{analysis_id}/reprocess`
- `POST /analyses/{analysis_id}/request-specialist`
- `POST /models/{model_id}/request-retraining`
- `PATCH /assets/{asset_id}`
- `POST /cases/{case_id}/escalate`

The runner also warns against leaving all actions false merely because more evidence would be nice. The goal is to distinguish genuinely missing evidence from a supported next action.

## Escalation calibration

The runner asks the model to set `requires_human_escalation=true` when visible evidence indicates:

- safety risk;
- severe fault;
- specialist-needed diagnosis;
- ambiguous but high-impact condition;
- missing permission for a needed action;
- request-specialist/escalate as the best endpoint.

Generic uncertainty alone should not trigger escalation.

## Acceptance target before full remeasurement

Do not promote E10b to full DEV+VALIDATION unless a DEV-only private scorer run shows all of the following:

- evidence correctness remains materially above the E9 DEV baseline;
- action correctness improves above 0.0;
- escalation correctness improves above 0.0;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible;
- no raw private oracles or fixed parsed outputs are committed.

## Local command

```powershell
python scripts/research/e10b_dev_only_action_escalation_capture.py `
  --manifest research/experiments/e10b-dev-only-action-escalation-calibration-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10b-dev-only-action-escalation-capture.json"
```

Then score it with the existing private scorer:

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10b-dev-only-action-escalation-capture.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e10b-dev-only-e9-private-score.json" `
  --include-rows
```

Do not commit the non-dry-run fixed outputs or private scorer rows.
