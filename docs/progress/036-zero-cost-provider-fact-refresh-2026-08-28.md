# Progress 036 — Zero-cost provider/model fact refresh

**Date:** 2026-08-28  
**Type:** external fact refresh / no inference  
**Provider/model inference calls:** 0  
**Credential/account probes:** 0  
**Real customer mutations:** 0

## Purpose

Execute the evidence-first next step for D01/D02: refresh only current first-party provider/model facts that can change over time, then reconcile them with existing E8/E14/P12/ADR evidence before deciding whether a new live comparison is still necessary.

## Completed

- reviewed current primary-source documentation for Gemini Developer API, Groq Free, Cloudflare Workers AI Free, OpenRouter Free, Ollama, Hugging Face Inference Providers, Cerebras and NVIDIA hosted NIM/API Catalog;
- recorded current free-tier/free-endpoint eligibility, lifecycle, structured-output/tool capabilities, public quota/capacity semantics, paid-spillover behavior and production-use constraints;
- created `docs/PROVIDER-ZERO-COST-FACT-REFRESH-2026-08-28.md`;
- created machine-readable `research/results/provider-zero-cost-fact-refresh-2026-08-28.json`;
- made zero model inference calls and zero credential/account probes.

## Current screening result

Primary hosted feasible set:

1. Gemini 3.7 Flash — conditional on Free Tier data-use/privacy acceptability for the exact payload;
2. Cloudflare Workers AI Free — pinned model only; strong fail-closed USD-0 boundary through the Workers Free allocation;
3. Groq Free — retain as historical/control route with prior project-specific negative quality/capacity evidence preserved.

Conditional baselines:

- Ollama local;
- fixed OpenRouter `:free` model only, never the generic random free router.

Not primary final hosted production candidates:

- NVIDIA free hosted NIM — development/testing positioning;
- Cerebras Free Trial — bounded trial;
- Hugging Face routed free credit — allowance too small for default production use without proving ultra-low volume;
- Groq Qwen 3.8 Preview — preview/evaluation-only lifecycle.

## Decision effect

D01 remains `PARTIALLY_ASSESSED`, but the next gap is narrower and no longer justifies open-ended provider discovery.

No benchmark is authorized by this refresh. Before any provider call, the project must resolve the Gemini Free Tier data-use eligibility question, select the minimum materially distinct Cloudflare representative(s), decide Groq's exact control role, and determine whether an Ollama hardware/model baseline is realistically feasible without inference.

C4 remains unchanged and separate.
