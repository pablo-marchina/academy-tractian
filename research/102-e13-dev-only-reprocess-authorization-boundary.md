# E13 DEV-only Reprocess Authorization Boundary

**Status:** E13_DEV_ONLY_REPROCESS_AUTHORIZATION_BOUNDARY_READY  
**Date:** 2026-08-16  
**Scope:** DEV only  
**Demo:** false  
**Integration:** false  
**New product:** false  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Purpose

E13 implements only the root-cause-specific change preregistered after E12.

E12 showed that E11 did not fail because the policy was missing or partially applied. The independent action-authorization policy ran on the full DEV+VALIDATION capture, checked all 12 outputs, covered both DEV and VALIDATION, changed 0 outputs, and authorized every output as an autonomous state-changing reprocess action.

The E12 root-cause class was:

```text
policy_executed_but_over_permissive_or_wrong_authorization_class
```

E13 directly targets that class.

## Candidate change

```text
reprocess_specific_authorization_boundary
```

Target endpoint:

```text
POST /analyses/{analysis_id}/reprocess
```

Target failure mode:

```text
over_permissive_authorization_of_autonomous_reprocess_actions
```

## Rule implemented

E13 does not authorize autonomous reprocess from generic evidence-family counts or generic human-review markers.

A `POST /analyses/{analysis_id}/reprocess` action is authorized only when visible, endpoint-specific evidence indicates that the current analysis itself is one of:

- failed or errored;
- invalid or unreliable;
- stale or outdated;
- incomplete or missing required data;
- blocked by data-quality failure;
- unsafe to rely on without recomputation.

If that endpoint-specific defect evidence is missing, E13 downgrades immediate reprocess to investigation or human handoff.

## Boundary

E13 is a DEV-only candidate. It is not demo, integration, a new product, a full rerun, or architecture freeze.

The runner must not use:

- VALIDATION tuning;
- private expected paths;
- private oracle values;
- raw scorer rows;
- validation feedback;
- evaluator labels;
- reference trajectories;
- `eval/expected-paths.json` in the model/policy;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST.

Private expected paths may only be used later by the local E9 v3 scorer after E13 outputs are fixed.

## Files

- `research/experiments/e13-dev-only-reprocess-authorization-boundary-manifest.json`
- `scripts/research/e13_dev_only_reprocess_authorization_boundary.py`
- `research/102-e13-dev-only-reprocess-authorization-boundary.md`
- `.github/workflows/research-e13.yml`

## Local run

```powershell
git pull
$env:PYTHONPATH = "."

$TRACTIAN_PACKAGE = "C:\Users\Inteli\Documents\Projetos\academy-tractian\inteli-tractian-project\inteli-tractian-project"

$env:GROQ_API_KEY = "SUA_CHAVE_GROQ_AQUI"
$env:E8_ENABLE_GROQ = "1"
$env:E8_CONFIRM_ZERO_COST = "1"
$env:E8_GROQ_MODEL = "llama-3.1-8b-instant"
$env:E8_MODEL_TEMPERATURE = "0"
$env:E8_MAX_OUTPUT_TOKENS = "800"
$env:E8_PROVIDER_MAX_ATTEMPTS = "5"
$env:E8_PROVIDER_RETRY_BASE_SECONDS = "5"
$env:E8_BETWEEN_CALL_DELAY_SECONDS = "8"
$env:E8_HTTP_USER_AGENT = "academy-tractian-e13-reprocess-boundary/1.0"

$E13_CAPTURE = "$env:TEMP\e13-dev-only-reprocess-boundary-capture.json"

python scripts/research/e13_dev_only_reprocess_authorization_boundary.py `
  --manifest research/experiments/e13-dev-only-reprocess-authorization-boundary-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out $E13_CAPTURE

Test-Path $E13_CAPTURE
```

## Private scoring after fixed outputs exist

```powershell
$E13_SCORE = "$env:TEMP\e13-dev-only-e9-private-score.json"

python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file $E13_CAPTURE `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out $E13_SCORE `
  --include-rows

Get-Content $E13_SCORE
```

Do not commit the non-dry-run capture, private score rows, output hashes, private paths, or oracle values.

## Acceptance before any full remeasurement

E13 must pass DEV-only before any full DEV+VALIDATION run is prepared.

Required:

- `premature_action_rate = 0.0` on DEV;
- `unsupported_final_claim_rate = 0.0` on DEV;
- `real_task_quality >= 0.8571` on DEV;
- `decision_correctness >= 0.75` on DEV;
- `action_correctness >= 0.75` on DEV;
- `evidence_correctness = 1.0` on DEV;
- `escalation_correctness = 1.0` on DEV;
- LOCKED_TEST remains blocked;
- no raw private or fixed-output material is committed.

## Gate decision

No integration.  
No demo.  
No final architecture freeze.  
No full DEV+VALIDATION rerun unless E13 passes DEV-only first.
