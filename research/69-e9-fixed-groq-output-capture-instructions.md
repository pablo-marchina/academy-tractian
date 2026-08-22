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

## Why `fixed_calls_consumed = 12` can still be contract mode

This result means the fixed Groq capture file is correct, but the scorer still does not have a real private oracle file:

```json
{
  "status": "E9_SCORER_CONTRACT_PASS_PRIVATE_ORACLE_OR_OUTPUTS_REQUIRED",
  "fixed_calls_consumed": 12,
  "parsed_model_outputs_available": 12,
  "private_oracle_file_provided": false,
  "private_oracles_loaded": 0,
  "real_score_available": false
}
```

Do not pass the literal placeholder string `<private-dev-validation-oracle.json>`. Replace it with the real local path to a DEV/VALIDATION-only oracle JSON file. If the path does not exist, the scorer must stay in contract mode.

Older scorer output could print `real_score_available: true` when aggregate proxy metrics existed without a private oracle. That was confusing and has been corrected: a real score now requires both parsed fixed outputs and matching private oracles.

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

## Private oracle file format

The oracle file may use a flexible shape, but it must include DEV/VALIDATION group IDs such as `asset_G501`, `asset_C710`, `asset_S420`, `asset_B204`, or `asset_M102` and expected fields. Minimal example:

```json
{
  "oracles": {
    "asset_G501": {
      "expected_decision_class": "investigate_only",
      "required_evidence_terms": ["analysis", "baseline"],
      "expected_should_take_action_now": false,
      "expected_requires_human_escalation": false
    }
  }
}
```

Supported oracle fields include:

- `expected_decision_class` or `allowed_decision_classes`;
- `required_evidence_terms` or `expected_evidence`;
- `expected_should_take_action_now`;
- `expected_requires_human_escalation`;
- `forbidden_claim_terms`.

The scorer rejects LOCKED_TEST groups if they appear in the oracle file before final evaluation.

## Run E9 private scorer

After the fixed parsed output file exists, run the scorer with the real local private DEV/VALIDATION oracle file. Replace the path below; do not leave the placeholder.

```powershell
$PRIVATE_ORACLE = "C:\path\to\private-dev-validation-oracle.json"
Test-Path $PRIVATE_ORACLE

python scripts/research/e9_evaluator_side_scorer.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json" `
  --oracle-file $PRIVATE_ORACLE `
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
