# E8 Free-Anywhere Real Candidate Run Instructions

**Status:** READY_FOR_USER_KEYED_RUN  
**Date:** 2026-08-16  
**Budget:** USD 0 only  
**Scope:** Groq/Gemini remote free APIs first; OpenAI/Anthropic disabled  
**LOCKED_TEST:** blocked

## Key handling rule

Do not commit API keys and do not paste them into issues, PR descriptions or markdown files. Set them only as local environment variables or as repository secrets if a later controlled CI run is approved.

## Preferred order

1. Groq free API first.
2. Gemini free API second.
3. OpenRouter free router only if Groq/Gemini are unavailable or weak.
4. Hugging Face free inference credits only with tighter billing guard.
5. Ollama remains a fallback, not a requirement.

## Why Groq/Gemini first

The user has Groq and Gemini keys available, so no additional key is needed for the first model-quality pilot. The run should start with Groq because it uses an OpenAI-compatible API surface and tends to be simple to integrate, then repeat with Gemini for comparison.

## Required local setup

Use the supplied TRACTIAN API and `agent-input/cases.json` when available. The model prompt must receive only agent-visible cases. It must not receive `eval/`, `docs/test-scenarios.md`, `data/cases.parquet`, expected answers, or scorer-only oracles.

## Groq command — PowerShell

```powershell
cd "C:\Users\Inteli\Documents\Projetos\academy-tractian"
git checkout research/systematic-foundation
git pull
$env:PYTHONPATH = "."

$TRACTIAN_PACKAGE = "C:\Users\Inteli\Documents\Projetos\academy-tractian\inteli-tractian-project\inteli-tractian-project"

$env:GROQ_API_KEY = "COLE_SUA_CHAVE_AQUI_SOMENTE_NO_TERMINAL"
$env:E8_ENABLE_GROQ = "1"
$env:E8_CONFIRM_ZERO_COST = "1"
$env:E8_GROQ_MODEL = "llama-3.1-8b-instant"

python scripts/research/e8_free_anywhere_model_runner.py `
  --provider groq `
  --manifest research/experiments/e8-free-anywhere-real-candidate-run-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --out "$env:TEMP\e8-groq-free-anywhere-model-run-summary.json"

Get-Content "$env:TEMP\e8-groq-free-anywhere-model-run-summary.json"
```

## Gemini command — PowerShell

```powershell
cd "C:\Users\Inteli\Documents\Projetos\academy-tractian"
git checkout research/systematic-foundation
git pull
$env:PYTHONPATH = "."

$TRACTIAN_PACKAGE = "C:\Users\Inteli\Documents\Projetos\academy-tractian\inteli-tractian-project\inteli-tractian-project"

$env:GEMINI_API_KEY = "COLE_SUA_CHAVE_AQUI_SOMENTE_NO_TERMINAL"
$env:E8_ENABLE_GEMINI = "1"
$env:E8_CONFIRM_ZERO_COST = "1"
$env:E8_GEMINI_MODEL = "gemini-2.5-flash-lite"

python scripts/research/e8_free_anywhere_model_runner.py `
  --provider gemini `
  --manifest research/experiments/e8-free-anywhere-real-candidate-run-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --out "$env:TEMP\e8-gemini-free-anywhere-model-run-summary.json"

Get-Content "$env:TEMP\e8-gemini-free-anywhere-model-run-summary.json"
```

## Expected successful status

A successful provider run should end with:

```json
{
  "status": "E8_FREE_ANYWHERE_MODEL_RUN_PASS"
}
```

A `NEEDS_REVIEW` result is not necessarily bad. It means the provider response was not fully schema-compliant, failed the DEV smoke gate, returned an API error, or the output suggested unsafe/unsupported behavior.

## What the summary measures

- provider availability;
- external call success rate;
- JSON/schema compliance;
- no LOCKED_TEST leakage;
- evidence-plan completeness proxy;
- action/escalation policy self-check proxy;
- trace completeness;
- latency average and p95;
- reported token usage when provider returns it;
- cost recorded as USD 0 only under explicit `E8_CONFIRM_ZERO_COST=1`.

## Interpretation limit

This is real model-output evidence from a free candidate, but it still avoids evaluator-only gold in prompts. Therefore, task-success remains a proxy until a later scorer maps outputs to private oracles outside the model prompt.

No model/provider or final architecture is frozen by this run.
