# E8 Free Provider Connectivity Review

**Status:** E8_FREE_PROVIDER_CONNECTIVITY_NEEDS_RETRY  
**Date:** 2026-08-16  
**Scope:** Groq and Gemini keyed free-anywhere model attempts  
**Budget:** USD 0  
**LOCKED_TEST accessed:** false

## Summary

The first real free-provider keyed run reached both configured providers but did not produce model-quality evidence. Both provider summaries ended as `E8_FREE_ANYWHERE_MODEL_RUN_NEEDS_REVIEW` because every DEV smoke call failed before a schema-valid model output was returned.

This is classified as a provider/connectivity/model-endpoint issue, not as a model-quality failure.

## Gemini attempt

| Metric | Result |
|---|---:|
| Provider | `gemini` |
| External calls made | true |
| Cost USD | 0.0 |
| DEV groups | `asset_G501`, `asset_C710`, `asset_S420` |
| DEV calls | 6 |
| Successful calls | 0 |
| Schema valid rate | 0.0 |
| Trace completeness | false |
| LOCKED_TEST accessed | false |

Observed errors:

- repeated Windows connection resets: `WinError 10054`;
- one HTTP 404 reporting that `models/gemini-2.5-flash-lite` is no longer available to the current user and recommending migration/update.

Remediation applied:

- changed the default Gemini model from `gemini-2.5-flash-lite` to `gemini-2.5-flash`;
- changed Gemini authentication to use the `x-goog-api-key` header instead of putting the key in the query string;
- added instructions to list key-visible Gemini models before retrying if another `NOT_FOUND` occurs.

## Groq attempt

| Metric | Result |
|---|---:|
| Provider | `groq` |
| External calls made | true |
| Cost USD | 0.0 |
| DEV groups | `asset_G501`, `asset_C710`, `asset_S420` |
| DEV calls | 6 |
| Successful calls | 0 |
| Schema valid rate | 0.0 |
| Trace completeness | false |
| LOCKED_TEST accessed | false |

Observed errors:

- HTTP 403 with error code `1010`;
- repeated Windows connection resets: `WinError 10054`.

Remediation applied:

- added an explicit `User-Agent` and `Accept: application/json` header to all provider requests;
- preserved `llama-3.1-8b-instant` as the Groq default model;
- kept Groq behind `GROQ_API_KEY`, `E8_ENABLE_GROQ=1` and `E8_CONFIRM_ZERO_COST=1`.

## Integrity result

- LOCKED_TEST remained blocked.
- No evaluator-only gold was included in prompts.
- Cost remained USD 0.0.
- OpenAI and Anthropic remained disabled.
- DEV did not pass, so VALIDATION correctly did not run.
- No model/provider or final architecture is frozen.

## Next step

Pull the provider-connectivity fix and rerun Groq first, then Gemini. If Gemini still returns `NOT_FOUND`, list models available to the key and rerun with a `generateContent`-capable model returned by the API.
