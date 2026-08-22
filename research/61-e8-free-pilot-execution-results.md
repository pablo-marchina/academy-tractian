# E8 Free-Only Pilot Execution Results

**Status:** E8_FREE_PILOT_SMOKE_PASS  
**Date:** 2026-08-16  
**Budget:** completely free / zero paid model calls  
**Scope:** DEV smoke first, then VALIDATION after DEV pass  
**LOCKED_TEST accessed:** false

## What was executed

E8 pilot execution was started in the only mode compatible with the project constraint that the system must be completely free.

The runner performs three things:

1. Detects which free/local candidates are available from the current environment.
2. Keeps OpenAI and Anthropic paid reference candidates disabled.
3. Executes a no-model policy-baseline pilot smoke over DEV first and VALIDATION second, using fixed observation packets and repeated outputs to validate the pilot harness.

This is an execution smoke for the statistical-pilot harness. It is not yet an external model-quality benchmark because no free external API key or local model availability is assumed in CI.

## Candidate availability policy

| Slot | Status in default CI | Reason |
|---|---|---|
| `no_model_policy_baseline` | available/executed | Built-in deterministic free baseline |
| `groq_openai_compatible_free_first` | optional/not executed by default | Requires `GROQ_API_KEY` and `E8_ENABLE_GROQ=1` |
| `google_gemini_free_or_low_cost` | optional/not executed by default | Requires `GEMINI_API_KEY` or `GOOGLE_API_KEY` and `E8_ENABLE_GEMINI=1` |
| `local_ollama_optional` | optional/not executed by default | Requires `OLLAMA_HOST` and `E8_ENABLE_OLLAMA=1` |
| `openai_reference_optional` | disabled | Paid candidate blocked by free-only policy |
| `anthropic_reference_optional` | disabled | Paid candidate blocked by free-only policy |

## Execution order

| Gate | Groups | Repeats | Result |
|---|---|---:|---|
| DEV smoke | `asset_G501`, `asset_C710`, `asset_S420` | 3 per group | pass |
| VALIDATION after DEV pass | `asset_B204`, `asset_M102` | 5 per group | pass |

## Metrics measured

| Metric | Result |
|---|---:|
| Free-only mode | true |
| Paid model calls | 0 |
| External model calls in CI | 0 |
| Cost USD | 0.0 |
| Fixed observation packets used | true |
| Stochastic repeat harness executed | true |
| DEV smoke before VALIDATION | true |
| Task success proxy | 1.0 |
| Action/escalation correctness proxy | 1.0 |
| Evidence coverage proxy | 1.0 |
| RunTrace completeness | true |
| LOCKED_TEST accessed | false |

## Interpretation

The result validates that the E8 pilot execution harness can run in a fully free mode, respects the DEV-before-VALIDATION order, separates fixed observation packets from repeated outputs, and keeps paid providers disabled.

The result does **not** prove external model quality yet. To benchmark Groq, Gemini or a local Ollama model, the same runner must be executed locally with explicit free/local opt-in environment variables and without enabling paid candidates.

## Preserved constants

- B3 guarded boundary.
- Evidence-sufficiency policy.
- Adaptive evidence planning.
- LangGraph runtime candidate.
- HarnessRunner execution boundary.
- `HttpxTransport` live API path.
- Native ToolSpec internal surface.
- Optional MCP-compatible adapter.
- Pydantic AI/Graph and OpenAI Agents SDK retained as comparators.

## Next

Run the same E8 runner locally after checking whether Groq free-tier, Gemini free-tier or local Ollama are actually available. If none are available, continue with the no-model policy baseline and do not claim model-quality evidence.
