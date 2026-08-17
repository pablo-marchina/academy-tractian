# E14 DEV-only Provider Deprecation Recovery

**Status:** E14_PROVIDER_DEPRECATION_RECOVERY_PREREGISTERED  
**Date:** 2026-08-17  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**E14 policy changed:** false  
**E14 acceptance thresholds changed:** false  
**Final architecture frozen:** false

## Why the first real E14 attempt is invalid

The first non-dry-run E14 attempt produced 6 fixed calls, 0 parsed outputs and 0 scoreable calls, with 12 wrapper retries. No selective-reprocess decision was reached.

This is an infrastructure/provider invalidation, not evidence that the E14 policy failed.

Groq officially shut down `llama-3.1-8b-instant` for Free and Developer usage on 2026-08-16. Groq's published replacement for this model is `openai/gpt-oss-20b`.

The failed attempt must therefore be classified as:

```text
external_provider_model_shutdown_before_model_output
```

Do not include this run in E14 quality comparisons.

## Recovery model

Use:

```text
openai/gpt-oss-20b
```

The replacement is operational, not a DEV-quality tuning choice. It is selected from Groq's official deprecation guidance after the previously configured model became unavailable.

The replacement currently supports JSON Object Mode and is listed under Groq Free Plan rate limits.

## Methodological boundary

The E14 candidate itself remains unchanged:

```text
completeness_preserving_selective_reprocess_authorization
```

The following remain unchanged:

- DEV groups: `asset_G501`, `asset_C710`, `asset_S420`;
- 2 repeats per DEV group;
- 6 fixed calls;
- syntax-only JSON repair;
- retry only failed model calls or parse failures;
- no semantic field invention;
- selective reprocess authorization requirements;
- E9 v3 private scorer;
- all E14 acceptance thresholds;
- no VALIDATION tuning;
- no LOCKED_TEST.

## Historical-comparison rule

Do not interpret a score difference between historical E13 on `llama-3.1-8b-instant` and recovered E14 on `openai/gpt-oss-20b` as a causal policy delta.

If a causal E13-versus-E14 comparison is later needed, remeasure both candidates DEV-only on the same replacement model before making a delta claim. This paired rebaseline is measurement, not tuning, and must still exclude VALIDATION feedback.

The absolute E14 gate may still be evaluated on the replacement model because the project has not frozen the model/provider and the already-preregistered E14 gate is absolute rather than a required E13 delta.

## Safe provider preflight

Before spending any of the six fixed calls, run:

```powershell
$env:E8_ENABLE_GROQ = "1"
$env:E8_CONFIRM_ZERO_COST = "1"
$env:E8_GROQ_MODEL = "openai/gpt-oss-20b"
$env:E8_HTTP_USER_AGENT = "academy-tractian-e14-recovery/1.0"

python scripts/research/e14_provider_preflight.py
```

Expected:

```text
E14_GROQ_PROVIDER_PREFLIGHT_PASS
```

The preflight makes no model inference and does not print the API key.

## Recovered E14 real DEV-only run

```powershell
$env:PYTHONPATH = "."
$TRACTIAN_PACKAGE = "C:\Users\Inteli\Documents\Projetos\academy-tractian\inteli-tractian-project\inteli-tractian-project"

$env:E8_ENABLE_GROQ = "1"
$env:E8_CONFIRM_ZERO_COST = "1"
$env:E8_GROQ_MODEL = "openai/gpt-oss-20b"
$env:E8_MODEL_TEMPERATURE = "0"
$env:E8_MAX_OUTPUT_TOKENS = "800"
$env:E8_PROVIDER_MAX_ATTEMPTS = "5"
$env:E8_PROVIDER_RETRY_BASE_SECONDS = "5"
$env:E8_BETWEEN_CALL_DELAY_SECONDS = "12"
$env:E14_MAX_RETRIES = "2"
$env:E8_HTTP_USER_AGENT = "academy-tractian-e14-recovery/1.0"

$E14_CAPTURE = "$env:TEMP\e14-dev-only-real-gpt-oss-20b-capture.json"
$E14_SCORE = "$env:TEMP\e14-dev-only-gpt-oss-20b-e9-private-score.json"

python scripts/research/e14_dev_only_completeness_selective_reprocess.py `
  --manifest research/experiments/e14-dev-only-completeness-selective-reprocess-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out $E14_CAPTURE
```

Only if E14 produces 6 parsed and scoreable fixed outputs, run E9 v3:

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file $E14_CAPTURE `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out $E14_SCORE `
  --include-rows

Get-Content $E14_SCORE
```

Do not commit the capture, private score rows, output hashes, oracle values, private paths or API key.

## Acceptance remains unchanged

Required before any DEV+VALIDATION measurement-only rerun:

- parsed outputs = 6;
- scoreable calls = 6;
- premature action rate = 0.0;
- unsupported final-claim rate = 0.0;
- real task quality >= 0.8571;
- decision correctness >= 0.75;
- action correctness >= 0.75;
- evidence correctness = 1.0;
- escalation correctness = 1.0;
- LOCKED_TEST remains blocked.

No integration, demo, UI/final-architecture progression or final architecture freeze occurs before this gate passes.
