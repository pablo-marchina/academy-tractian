# E8 Optional Free-Provider Comparators

**Status:** E8_OPTIONAL_FREE_PROVIDER_COMPARATORS_REGISTERED  
**Date:** 2026-08-16  
**Budget:** USD 0 only  
**Leading candidate:** Groq `llama-3.1-8b-instant`  
**LOCKED_TEST accessed:** false

## Decision

Groq remains the leading free-provider candidate after passing the E8 real free-anywhere model run on DEV and VALIDATION.

Optional comparators are allowed, but they must not delay E9. Their purpose is provider redundancy and benchmark context, not blocking architecture progress.

## Comparator priority

1. **OpenRouter free comparator**
   - Add as the next optional remote comparator.
   - Use only `openrouter/free` or a specific model ending in `:free`.
   - Block `openrouter/auto` and `openrouter/auto:free` because they are not strict enough for reproducible zero-cost benchmarking.
   - Required env: `OPENROUTER_API_KEY`, `E8_ENABLE_OPENROUTER_FREE=1`, `E8_CONFIRM_ZERO_COST=1`.
   - Documentation basis: OpenRouter documents `openrouter/free`, free `:free` model variants and warns that `openrouter/auto:free` or `auto` can still result in charges; this repo therefore requires the strict free router or a specific `:free` model.

2. **Gemini key-visible model comparator**
   - Retry only after listing models visible to the key.
   - Use only a model returned by `models.list` that supports `generateContent`.
   - Gemini must not block E9 because the first attempts failed due model availability and connection errors, not project logic.

3. **Hugging Face free-credit comparator**
   - Low priority.
   - Only valid if the account/free-credit state can be bounded to USD 0.
   - Do not run if there is any risk of billing after free credits are exhausted.

4. **Ollama local optional fallback**
   - Still allowed as no-token-cost fallback.
   - Not required because the project is free-anywhere, not local-only.

## Implementation update

Added:

- `scripts/research/e8_free_anywhere_model_runner_v3.py`
- `research/experiments/e8-optional-free-provider-comparators-manifest.json`

The v3 runner extends the v2 scoring/retry runner and adds OpenRouter support while preserving:

- zero-cost opt-in;
- OpenAI/Anthropic disabled;
- DEV before VALIDATION;
- LOCKED_TEST blocked;
- no evaluator-only gold in prompts;
- native ToolSpec internal default;
- MCP-compatible adapter as optional external surface.

## OpenRouter command

```powershell
$env:OPENROUTER_API_KEY = "COLE_SUA_CHAVE_AQUI_SOMENTE_NO_TERMINAL"
$env:E8_ENABLE_OPENROUTER_FREE = "1"
$env:E8_CONFIRM_ZERO_COST = "1"
$env:E8_OPENROUTER_MODEL = "openrouter/free"
# Prefer a specific :free model if selected from the OpenRouter free catalog:
# $env:E8_OPENROUTER_MODEL = "provider/model-name:free"

python scripts/research/e8_free_anywhere_model_runner_v3.py `
  --provider openrouter `
  --manifest research/experiments/e8-free-anywhere-real-candidate-run-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e8-openrouter-free-anywhere-model-run-summary-v3.json"
```

## Non-blocking rule

E9 proceeds regardless of optional comparator availability because E8 already has one passing real zero-cost remote model candidate.

## Next gate

E9 evaluator-side task-quality scorer:

- map model outputs to private oracles outside model prompts;
- separate proxy success from real task-quality evidence;
- measure evidence correctness;
- measure action/escalation correctness;
- keep LOCKED_TEST blocked until final evaluation;
- do not freeze the final architecture yet.
