# E8 Groq Free-Anywhere Model Run Results

**Status:** E8_FREE_ANYWHERE_MODEL_RUN_PASS  
**Date:** 2026-08-16  
**Provider:** Groq  
**Model:** `llama-3.1-8b-instant`  
**Runner:** `scripts/research/e8_free_anywhere_model_runner_v2.py`  
**Budget:** USD 0  
**LOCKED_TEST accessed:** false

## Result

The Groq free-anywhere keyed run passed both DEV smoke and VALIDATION after the v2 scoring/retry fix.

| Metric | DEV | VALIDATION | Aggregate |
|---|---:|---:|---:|
| Groups | `asset_G501`, `asset_C710`, `asset_S420` | `asset_B204`, `asset_M102` | DEV + VALIDATION |
| Total calls | 6 | 6 | 12 |
| Successful calls | 6 | 6 | 12 |
| Passed | true | true | true |
| Task-success proxy | 1.0 | 1.0 | 1.0 |
| Schema-valid rate | 1.0 | 1.0 | 1.0 |
| No LOCKED_TEST claim rate | 1.0 | 1.0 | 1.0 |
| Trace completeness | true | true | true |
| Average latency ms | 8974.732 | 9766.9 | 9370.816 |
| P95 latency ms | 30724.136 | 50841.424 | 50841.424 |
| Cost USD | 0.0 | 0.0 | 0.0 |

## Integrity checks

- The run used agent-visible cases.
- The run stayed inside DEV + VALIDATION.
- LOCKED_TEST remained blocked.
- OpenAI/Anthropic paid candidates remained disabled.
- `E8_CONFIRM_ZERO_COST=1` was required for the keyed run.
- The result did not freeze model/provider or final architecture.

## Interpretation

This is the first successful real free-provider model-output evidence for E8. It validates the zero-cost remote-provider path, JSON/schema compliance, trace proxy, no-locked-test/no-gold self-checks and DEV-before-VALIDATION gating.

It is still not final task-quality evidence against private evaluator oracles. Task success remains a proxy until a later scorer maps model outputs to private oracles outside the model prompt.

## Decision implication

Groq becomes the current leading free-provider candidate for the statistical/model benchmark path. Gemini remains unresolved due provider/model availability and connection issues. No final architecture or provider choice is frozen at this gate.
