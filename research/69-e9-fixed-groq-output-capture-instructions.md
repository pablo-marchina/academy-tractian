# E9 Fixed Groq Output Capture Instructions

**Status:** READY_FOR_LOCAL_PRIVATE_CAPTURE  
**Date:** 2026-08-16  
**Purpose:** produce fixed parsed Groq outputs for the E9 private scorer  
**Budget:** USD 0  
**LOCKED_TEST:** blocked  
**Commit generated output file:** no

## Why `fixed_calls_consumed = 0` happened

The E9 scorer is behaving correctly when it reports:

```json
{
  "status": "E9_SCORER_CONTRACT_PASS_PRIVATE_ORACLE_OR_OUTPUTS_REQUIRED",
  "fixed_calls_consumed": 0,
  "real_score_available": false
}
```

That means it was pointed at the public sanitized E8 summary, which contains aggregate metrics and/or hashes but not scorer-consumable `calls[*].parsed_output` records. E9 cannot infer semantic task quality from hashes alone.

## Required E9 input chain

```text
Groq model run -> fixed parsed output file -> private scorer reads DEV/VALIDATION oracle -> sanitized aggregate result
```

The model still must never receive:

- expected answers;
- reference trajectories;
- private scoring labels;
- evaluator-only gold;
- `eval/expected-paths.json`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST cases or labels.

## Capture fixed parsed Groq outputs

Run this locally. Do not commit the output file.

```powershell
cd "C:\Users\Inteli\Documents\Projetos\academy-tractian"
git checkout research/systematic-foundation
git pull
$env:PYTHONPATH = "."

$TRACTIAN_PACKAGE = "C:\Users\Inteli\Documents\Projetos\academy-tractian\inteli-tractian-project\inteli-tractian-project"

$env:GROQ_API_KEY = "SUA_CHAVE_GROQ_AQUI"
$env:E8_ENABLE_GROQ = "1"
$env:E8_CONFIRM_ZERO_COST = "1"
$env:E8_GROQ_MODEL = "llama-3.1-8b-instant"
$env:E8_MODEL_TEMPERATURE = "0"
$env:E8_MAX_OUTPUT_TOKENS = "350"
$env:E8_PROVIDER_MAX_ATTEMPTS = "5"
$env:E8_PROVIDER_RETRY_BASE_SECONDS = "5"
$env:E8_BETWEEN_CALL_DELAY_SECONDS = "8"
$env:E8_HTTP_USER_AGENT = "academy-tractian-e8-fixed-groq-capture/1.0"

python scripts/research/e8_capture_fixed_groq_outputs.py `
  --manifest research/experiments/e8-free-anywhere-real-candidate-run-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json"

Get-Content "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json"
```

Expected capture status:

```json
{
  "status": "E8_FIXED_GROQ_OUTPUT_CAPTURE_PASS",
  "parsed_model_outputs_available": 12
}
```

`parsed_model_outputs_available` should be greater than zero. If it is zero, E9 will remain in contract mode.

## Run E9 private scorer

After the fixed parsed output file exists, run the scorer with the private DEV/VALIDATION oracle file:

```powershell
python scripts/research/e9_evaluator_side_scorer.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --fixed-output-file "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json" `
  --oracle-file "<private-dev-validation-oracle.json>" `
  --out "$env:TEMP\e9-private-task-quality-summary.json" `
  --include-rows

Get-Content "$env:TEMP\e9-private-task-quality-summary.json"
```

Expected scorer status after a valid private oracle is supplied:

```text
E9_TASK_QUALITY_SCORER_PASS
```

## What may be committed afterwards

Commit only a sanitized aggregate summary, for example:

- scoreable call count;
- real task-quality aggregate;
- decision correctness;
- evidence correctness;
- action correctness;
- escalation correctness;
- premature action rate;
- unsupported final-claim rate;
- proxy-vs-real disagreement rate;
- LOCKED_TEST access flag = false;
- final architecture freeze = false.

Do not commit:

- private oracle rows;
- evaluator-only gold;
- expected answers;
- raw private trajectories;
- secrets/API keys;
- LOCKED_TEST cases or labels.

## CI mode

CI validates the capture/scorer contract with dry runs only. Real E9 quality scoring remains a local/private step because the required oracles should not be in the public repository.
