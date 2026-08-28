# Decision Revalidation Addendum 004 — Provider Pre-Benchmark Gates

**Date:** 2026-08-28
**Status:** ACCEPTED FOR PLANNING SCOPE
**Provider/model inference calls:** 0

## Decision

The four factual gates left after Addendum 003 are closed:

1. **Gemini 3.7 Flash Free Tier** — the frozen public/synthetic probe population is acceptable for public evaluation use, but the general production provider request can contain verbatim user text and raw tool observation bodies. Under the current Free Tier data-use terms, Gemini is `PUBLIC_SYNTHETIC_EVAL_ELIGIBLE` but `PRODUCTION_PAYLOAD_INELIGIBLE_BY_DEFAULT`.
2. **Cloudflare Workers AI Free** — the minimum retained set is `@cf/zai-org/glm-4.7-flash` plus `@cf/nvidia/nemotron-3-120b-a12b`. `@cf/google/gemma-4-26b-a4b-it` is excluded from the minimum first comparison because its currently distinct context/output-cost advantages do not map to a demonstrated requirement in the compact public DecisionSource workload.
3. **Groq Free** — next role is `HISTORICAL_CONTROL_ONLY`. E8/E14/P12 already provide operational, negative task-quality and capacity evidence, while current GPT-OSS-120B Free limits do not create a reversal trigger. Qwen 3.8 is Preview.
4. **Ollama local** — `qwen3:4b` is a `SPEC_FEASIBLE_LOCAL_BASELINE` from current model/runtime specifications. Exact host performance is not proven and must be checked using host metadata before inclusion in a frozen comparison.

## D01 conclusion

A narrow material evidence gap remains: the repository cannot currently select between the retained production-eligible Cloudflare models on project-specific decision quality, reliability and latency.

Therefore a **minimum prospective provider/model comparison is justified**, but only its planning/preregistration may start now. No inference is authorized by this addendum.

Core candidates for that future preregistration:

- `@cf/zai-org/glm-4.7-flash`
- `@cf/nvidia/nemotron-3-120b-a12b`

Conditional local baseline:

- `qwen3:4b`, only if a no-inference host inventory passes before freeze.

Historical control:

- Groq/GPT-OSS evidence only; no freshness rerun.

Gemini is outside final production selection under the current Free Tier data-use boundary.

## Boundaries

The old ADR-008 candidate packet remains historical and must not execute as-is. Existing public probes and measurement definitions should be reused where still valid. The new prospective packet must freeze exact candidates, routes, call budget, repetitions, neuron upper bound, no-retry/no-fallback behavior, output custody and zero-cost containment before attempt 1. C4 is unchanged.