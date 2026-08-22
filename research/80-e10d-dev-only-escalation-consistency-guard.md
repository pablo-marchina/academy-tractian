# E10d DEV-only Visible-output Escalation Consistency Guard

**Status:** READY_FOR_LOCAL_DEV_ONLY_CAPTURE  
**Date:** 2026-08-16  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why E10d exists

E10b and E10c both preserved strong DEV-only decision/evidence/action quality, but escalation correctness remained 0.0.

Comparable DEV-only result:

| Metric | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only | E10c DEV-only |
|---|---:|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | 0.8571 | 0.8571 |
| Decision correctness | 0.3333 | 0.3333 | 1.0 | 1.0 |
| Evidence correctness | 0.0 | 1.0 | 1.0 | 1.0 |
| Action correctness | 0.0 | 0.0 | 1.0 | 1.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 |

E10d changes the approach: instead of another prompt-only escalation instruction, it adds a deterministic visible-output guard after model generation and before private scoring.

## DEV-only boundary

E10d may use only these DEV groups:

- `asset_G501`
- `asset_C710`
- `asset_S420`

E10d must not use VALIDATION for tuning and must not access LOCKED_TEST. Private expected paths stay scorer-only after outputs are fixed.

## Guard rule

The guard uses only the parsed model output. It does not read:

- private expected paths;
- reference trajectories;
- evaluator-only labels;
- VALIDATION feedback;
- LOCKED_TEST material.

The guard sets `requires_human_escalation=true` only when the visible output itself indicates one of these conditions:

- `action_escalation_rubric.needs_human_escalation=true`;
- `decision_class=escalation_candidate`;
- specialist/case-escalate endpoint selected;
- visible text mentions human/specialist/safety/severity/permission/high-impact/risk/engineering-review rationale;
- `should_take_action_now=true` with a state-changing maintenance endpoint that should be protected by a human-in-the-loop guard.

The guard preserves:

- `decision_class`;
- `evidence_plan`;
- `should_take_action_now`;
- `proposed_next_step`.

## Acceptance target before full remeasurement

Do not promote E10d to full DEV+VALIDATION unless a DEV-only private scorer run shows all of the following:

- evidence correctness remains materially above the E9 DEV baseline;
- action correctness remains above 0.0;
- escalation correctness improves above 0.0;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible;
- no raw private oracles or fixed parsed outputs are committed.

## Local command

```powershell
python scripts/research/e10d_dev_only_escalation_consistency_guard.py `
  --manifest research/experiments/e10d-dev-only-escalation-consistency-guard-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10d-dev-only-escalation-guard-capture.json"
```

Then score it with the existing private scorer:

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10d-dev-only-escalation-guard-capture.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e10d-dev-only-e9-private-score.json" `
  --include-rows
```

Do not commit the non-dry-run fixed outputs or private scorer rows.
