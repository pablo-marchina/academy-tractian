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

## Provider connectivity notes after first attempt

The first keyed attempt reached the providers but did not produce model-quality evidence:

- Groq returned HTTP 403 / code 1010 and intermittent connection resets. The runner now sends an explicit `User-Agent` header because bare `urllib` clients can be blocked by Groq/Cloudflare.
- Gemini returned HTTP 404 for `gemini-2.5-flash-lite` because that model was unavailable to the current user/account. The default was changed to `gemini-2.5-flash`; override with `E8_GEMINI_MODEL` if `models.list` shows a different available free model.

These are provider/connectivity issues, not model-quality failures.

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
$env:E8_HTTP_USER_AGENT = "academy-tractian-e8-free-anywhere-runner/1.1"

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
$env:E8_GEMINI_MODEL = "gemini-2.5-flash"

python scripts/research/e8_free_anywhere_model_runner.py `
  --provider gemini `
  --manifest research/experiments/e8-free-anywhere-real-candidate-run-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --out "$env:TEMP\e8-gemini-free-anywhere-model-run-summary.json"

Get-Content "$env:TEMP\e8-gemini-free-anywhere-model-run-summary.json"
```

## Quick Gemini model probe

If Gemini returns `NOT_FOUND`, list the models available to the key and choose one that supports `generateContent`:

```powershell
$headers = @{ "x-goog-api-key" = $env:GEMINI_API_KEY }
Invoke-RestMethod -Uri "https://generativelanguage.googleapis.com/v1beta/models" -Headers $headers |
  ConvertTo-Json -Depth 8
```

Then rerun with the model name without the `models/` prefix, for example:

```powershell
$env:E8_GEMINI_MODEL = "gemini-2.5-flash"
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
