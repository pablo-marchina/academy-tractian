# E8 Free-Anywhere Candidate Discovery

**Status:** E8_FREE_ANYWHERE_CANDIDATE_DISCOVERY_PASS  
**Date:** 2026-08-16  
**Budget:** completely free / USD 0  
**Scope:** free remote APIs, free hosted systems and local systems  
**LOCKED_TEST accessed:** false

## Correction to scope

E8 is not limited to local candidates. The project may use any API, hosted service or local system if and only if it can be executed with total project cost USD 0.

This means the candidate universe is:

- free hosted API tiers;
- free model routers;
- provider monthly free credits, only when they can be bounded at USD 0;
- local/no-token-cost models;
- the no-model policy baseline as the always-free instrumentation anchor.

It explicitly excludes paid OpenAI/Anthropic reference runs and any provider configuration that can silently charge money after a free allowance is exhausted.

## Current free-anywhere candidate slots

| Slot | Type | Default status | Required local opt-in | Cost rule |
|---|---|---|---|---|
| `no_model_policy_baseline` | built-in baseline | available | none | always USD 0 |
| `groq_free_api` | remote hosted API | disabled until key/opt-in | `GROQ_API_KEY`, `E8_ENABLE_GROQ=1`, `E8_CONFIRM_ZERO_COST=1` | free tier only |
| `gemini_free_api` | remote hosted API | disabled until key/opt-in | `GEMINI_API_KEY` or `GOOGLE_API_KEY`, `E8_ENABLE_GEMINI=1`, `E8_CONFIRM_ZERO_COST=1` | free tier only |
| `openrouter_free_router` | remote free-model router | disabled until key/opt-in | `OPENROUTER_API_KEY`, `E8_ENABLE_OPENROUTER_FREE=1`, `E8_CONFIRM_ZERO_COST=1` | free models only |
| `huggingface_free_inference` | remote inference provider credits | disabled until key/opt-in | `HF_TOKEN`, `E8_ENABLE_HUGGINGFACE=1`, `E8_CONFIRM_ZERO_COST=1` | monthly free credits only; blocked if billing risk cannot be bounded |
| `ollama_local_optional` | local runtime | disabled until opt-in | `OLLAMA_HOST`, `E8_ENABLE_OLLAMA=1` | local compute only |
| `openai_reference_optional` | paid reference | disabled | not allowed under current project constraint | blocked |
| `anthropic_reference_optional` | paid reference | disabled | not allowed under current project constraint | blocked |

## Why these candidates are allowed to be considered

- Groq is allowed as a candidate because GroqCloud exposes a Free tier and a separate Developer tier requiring billing setup.
- Gemini is allowed as a candidate because Gemini Developer API and AI Studio expose free-tier/free-of-charge usage with model-specific limits.
- OpenRouter is allowed as a candidate because it exposes free models and an `openrouter/free` router for free-model selection.
- Hugging Face is allowed as a candidate because Inference Providers include monthly credits/free-tier usage; however, it must be guarded more strictly because usage past free credits can become paid.
- Ollama remains allowed as a local fallback, but locality is not required.

## Non-negotiable zero-cost guard

A remote candidate is considered executable only when all of the following are true:

1. provider API key is present;
2. candidate-specific opt-in flag is set;
3. `E8_CONFIRM_ZERO_COST=1` is set;
4. OpenAI/Anthropic paid references remain disabled;
5. CI/default execution makes no external model calls;
6. the summary records cost as USD 0 or marks the candidate blocked.

## Execution policy

Default CI may discover candidates and execute the no-model baseline, but must not call external APIs because secrets and free-tier state are user-specific.

Actual model-quality evidence requires a user-controlled run with one or more free remote/local candidates enabled, still with cost USD 0.

The run order remains:

1. DEV smoke first;
2. VALIDATION only after DEV smoke passes;
3. LOCKED_TEST blocked.

## What changed

The next E8 task is no longer "free/local candidate run". It is now:

**E8 free-anywhere candidate run** — use any remote API, hosted service or local system that can be proven/guarded as fully free.

## Interpretation limits

This gate broadens and guards the candidate universe. It does not claim that Groq, Gemini, OpenRouter, Hugging Face or Ollama have already produced model-quality benchmark results in this repo.

The next evidence-producing step is to run the E8 runner with an actually available free candidate and then compare task success, action/escalation correctness, evidence coverage, trace completeness, latency and cost.
