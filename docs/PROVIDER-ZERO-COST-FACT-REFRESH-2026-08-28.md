# Academy × TRACTIAN — Zero-Cost Provider/Model Fact Refresh

**Status:** COMPLETE / external-fact refresh only  
**Date:** 2026-08-28  
**Evidence policy:** primary-source documentation only  
**Provider/model inference calls:** 0  
**Credential/account probes:** 0  
**Scientific state changed:** no  
**Purpose:** update current USD-0 eligibility/capability facts before deciding whether any new provider comparison is still necessary.

## 1. Scope and method

This refresh implements the next step authorized by the historical evidence audit. It does **not** evaluate model quality, run a benchmark, inspect credentials, call provider model endpoints or change any frozen scientific artifact.

The repository evidence from E8/E14/P12/ADR-001→011 remains the historical baseline. This document updates only facts that can change externally over time:

- current free-tier/free-endpoint eligibility;
- model lifecycle state (GA/stable/preview/deprecated);
- structured-output and function/tool-call support;
- published free quota/capacity semantics;
- paid-spillover behavior and fail-closed properties;
- provider terms that affect production eligibility.

Primary sources were checked on 2026-08-28. No community benchmark, secondary comparison site or provider inference output is used as evidence here.

## 2. Current factual screening

| Provider/path | Current relevant free model/path | USD-0 status | Contract-relevant capability | Material constraint | Current screening disposition |
|---|---|---|---|---|---|
| Google Gemini Developer API | `gemini-3.7-flash` | Free tier exists; input/output free on Free Tier | GA/stable; function calling; structured outputs; thinking; 1M input / 64k output | Free-tier content is used to improve Google products; exact active rate limits are project/account-specific in AI Studio and were not probed | `CONDITIONAL_ELIGIBLE` — strong capability frontier, but privacy/data-use fit must be acceptable before live use |
| Groq Free | `openai/gpt-oss-120b`, `openai/gpt-oss-20b`; preview `qwen/qwen3.8-27b` | Free-plan published quotas; no paid tier required for Free use | GPT-OSS 20B/120B support strict structured outputs; all hosted Groq models support tool use | strict Structured Outputs cannot be combined with tool use in the same request; qwen3.8 is Preview; GPT-OSS 120B has preserved negative historical task-quality/capacity evidence | `ELIGIBLE_WITH_HISTORICAL_PENALTY` — retain as zero-cost baseline/control, not a blank-slate frontier candidate |
| Cloudflare Workers AI Free | `@cf/zai-org/glm-4.7-flash`, `@cf/google/gemma-4-26b-a4b-it`, `@cf/nvidia/nemotron-3-120b-a12b` | 10,000 neurons/day free; on Workers Free, exceeding allocation fails instead of billing | model pages expose function calling; OpenAI-compatible parameters include `response_format`, `tools`, `tool_choice`, `seed`; reasoning on screened models | neuron budget varies heavily by model; several newer frontier models require Paid plan and are excluded | `ELIGIBLE` — strongest newly refreshed alternative because zero-cost boundary is explicitly fail-closed on Free plan |
| OpenRouter Free | fixed `:free` variants and `openrouter/free` router | Free plan / free model variants; published free-plan cap 50 requests/day | OpenAI-compatible tool calling and structured outputs on compatible endpoints | `openrouter/free` selects models at random; endpoint support varies; provider-side fallback routing can retry other providers; current fixed free catalog is volatile | `CONDITIONAL_ELIGIBLE_FIXED_MODEL_ONLY` — router itself is unsuitable for controlled evaluation; any future use must pin exact model/provider behavior and disable uncontrolled fallbacks |
| Ollama local | local tool-capable models such as Qwen-family models | No external API charge; local compute only | local tool calling; multi-turn tool loops; JSON-schema structured outputs | quality/latency depend on actual local model and hardware; no current hardware/model qualification performed in this refresh | `ELIGIBLE_LOCAL_BASELINE` — credible zero-external-cost baseline, subject to separate hardware-feasibility facts if needed |
| Hugging Face Inference Providers | free-user monthly inference credits | Free users receive $0.10/month credits; additional routed use requires purchased credits | multi-provider OpenAI-compatible inference; model/provider metadata can expose tools/structured-output support | free allowance is very small and provider routing/billing abstraction adds another layer | `BOUNDED_EXPERIMENT_ONLY` — not a credible default production path without demonstrating workload fits permanently inside the tiny free allowance |
| Cerebras Inference | Free Trial | $5 free credits after account creation | access to Cerebras-powered models | trial credit is bounded rather than a durable recurring free production tier | `NOT_PRIMARY_PRODUCTION_CANDIDATE` — retain historical serving evidence; do not prioritize for final zero-cost production selection |
| NVIDIA hosted NIM/API Catalog | Free endpoints / Developer Program access | free hosted endpoints for prototyping/development/testing | many current agentic/tool-use models exposed as Free Endpoint | NVIDIA explicitly positions hosted free endpoints for development/testing; production requires an enterprise/production path | `INELIGIBLE_FOR_FINAL_HOSTED_PRODUCTION` — preserve historical compatibility evidence; no new hosted-NVIDIA benchmark justified for production selection |

## 3. Provider details

### 3.1 Google Gemini — materially stronger current candidate than the historical packet

Current first-party docs state that Gemini 3.7 Flash (`gemini-3.7-flash`) is GA/stable and intended for agentic workflows and reliable multi-step execution. The model supports function calling, structured outputs, thinking, a 1,048,576-token input window and 65,536 output tokens.

The Gemini pricing page currently lists Free Tier input and output for Gemini 3.7 Flash as free of charge. The Free usage tier has no spend-based rate limit because it has no billed spend; active RPM/TPM/RPD limits are project/model dependent and are shown in AI Studio. This refresh deliberately did not inspect the account.

The important production constraint is data policy: the pricing table states Free Tier content is used to improve Google products, while Paid Tier content is not. Therefore Gemini 3.7 Flash is technically the strongest refreshed hosted candidate, but it remains `CONDITIONAL_ELIGIBLE` until the project confirms that the exact production/evaluation payload is acceptable under that Free Tier data-use policy.

This is a meaningful change from the historical ADR-008 packet: the relevant current Gemini candidate is now **3.7 Flash**, not the older frozen 3.7/3.6 assumptions in prior planning, and it has a current free tier.

Primary sources:

- https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash
- https://ai.google.dev/gemini-api/docs/latest-model
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits
- https://ai.google.dev/gemini-api/docs/function-calling
- https://ai.google.dev/gemini-api/docs/structured-output

### 3.2 Groq Free — viable baseline, but historical negative evidence must remain binding

Groq's current Free Plan publishes, among other entries:

- `openai/gpt-oss-120b`: 30 RPM / 1K RPD / 8K TPM / 200K TPD;
- `openai/gpt-oss-20b`: 30 RPM / 1K RPD / 8K TPM / 200K TPD;
- `qwen/qwen3.6-27b`: 30 RPM / 1K RPD / 8K TPM / 200K TPD;
- `qwen/qwen3.8-27b`: 30 RPM / 1K RPD / 8K TPM / 2M TPD.

Groq documents strict Structured Outputs for GPT-OSS 20B, GPT-OSS 120B and Qwen 3.8 27B. It also documents tool use for hosted models. However, Structured Outputs and tool use are currently not supported together in a single Structured Outputs request. That does not necessarily block this repository because the accepted provider-neutral `DecisionSource` can request a typed decision payload and keep real tool execution in `HarnessRunner`; provider-native TRACTIAN tool execution remains forbidden anyway.

`qwen/qwen3.8-27b` is currently a **Preview** model. Groq explicitly states Preview models are evaluation-only and should not be used for production. It is therefore not a clean final production candidate despite its larger 2M TPD Free quota.

`openai/gpt-oss-120b` remains a production model and a Free-plan route, but E14/P12 already preserve substantial negative evidence: operational completeness was achievable, while task-quality/decision/action/escalation and capacity problems were observed in prior project-specific experiments. Those results must not be erased by treating Groq as a new candidate from scratch.

Primary sources:

- https://console.groq.com/docs/rate-limits
- https://console.groq.com/docs/models
- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/tool-use/overview
- https://console.groq.com/docs/billing-faqs

### 3.3 Cloudflare Workers AI — newly strong fail-closed zero-cost route

Workers AI is available on the Workers Free plan. Cloudflare currently grants **10,000 neurons/day free**. On Workers Free, usage above that allocation does not become billable: further operations fail. The Paid plan is a separate upgrade path. This is a strong match for the project's `USD 0` hard boundary because overage is fail-closed rather than silent paid spillover.

Current Free-plan-accessible, agent-relevant models include:

- `@cf/zai-org/glm-4.7-flash` — 131,072 context, function calling, reasoning, multi-turn tool use;
- `@cf/google/gemma-4-26b-a4b-it` — 256,000 context, function calling, reasoning, vision;
- `@cf/nvidia/nemotron-3-120b-a12b` — 256,000 context, function calling, reasoning.

Their current neuron costs differ materially:

- GLM-4.7-Flash: 5,500 neurons / M input; 36,400 / M output;
- Gemma 4 26B A4B: 9,091 / M input; 27,273 / M output;
- Nemotron 3 120B A12B: 45,455 / M input; 136,364 / M output.

Cloudflare's OpenAI-compatible model schemas expose `response_format`, `tools`, `tool_choice`, `seed` (best-effort deterministic), and standard completion controls. This makes Workers AI a credible current comparison candidate without changing the project's model-neutral DecisionSource or HarnessRunner execution boundary.

Some more expensive frontier models now explicitly require the Workers Paid plan and are therefore excluded from the zero-cost feasible set.

Primary sources:

- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://developers.cloudflare.com/workers-ai/
- https://developers.cloudflare.com/workers-ai/features/json-mode/
- https://developers.cloudflare.com/workers-ai/features/function-calling/
- https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/
- https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/
- https://developers.cloudflare.com/workers-ai/models/nemotron-3-120b-a12b/
- https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/

### 3.4 OpenRouter Free — useful interoperability route, weak controlled-experiment default

OpenRouter currently exposes 25+ free models on its Free plan and publishes a 50 requests/day plan cap. It supports structured outputs on compatible endpoints and standardizes client-side tool calling.

Two facts matter for this project:

1. `openrouter/free` intentionally selects a free model **at random** among models satisfying the requested features. That violates the controlled-comparison requirement for stable model identity.
2. OpenRouter documents provider-side fallback routing: if an upstream provider rate-limits or is unavailable, another provider may be retried before the error reaches the client. This behavior is useful operationally, but it is not acceptable in a controlled provider/model comparison unless explicitly pinned/disabled prospectively.

Therefore the generic free router is excluded. A specific fixed `:free` model could remain eligible only if exact model identity, endpoint/provider routing, required parameters and no-paid-spillover behavior are pinned prospectively.

Primary sources:

- https://openrouter.ai/pricing
- https://openrouter.ai/openrouter/free/
- https://openrouter.ai/docs/api_reference/limits
- https://openrouter.ai/docs/guides/features/structured-outputs
- https://openrouter.ai/collections/tool-calling-models

### 3.5 Ollama local — valid zero-external-cost baseline, not yet hardware-qualified

Ollama supports local function/tool calling, parallel and multi-turn tool loops, and structured outputs using JSON Schema. The local API defaults to `http://localhost:11434/api`.

This makes an Ollama-served open-weight model a valid architecture/provider baseline because it has no external inference charge and does not require provider-side routing. However, this refresh intentionally did not choose a specific local model or execute it. Model quality, memory footprint, latency and hardware feasibility remain separate facts that should be checked only if a local baseline is required in the minimum future comparison.

Primary sources:

- https://docs.ollama.com/capabilities/tool-calling
- https://docs.ollama.com/capabilities/structured-outputs
- https://docs.ollama.com/api/introduction

### 3.6 Hugging Face Inference Providers — free but too small for default production selection

Current Hugging Face documentation gives Free users **$0.10/month** of Inference Providers credits, subject to change. The routed service can access many providers and supports model/provider metadata including tool and structured-output capability flags.

The allowance is real, but extremely small. Additional routed usage requires purchased credits. Therefore the path can be fail-closed at USD 0 if no credits are purchased, but it is not a credible default production route unless a measured workload is permanently bounded below that tiny allowance. It remains useful only as a bounded experiment/interoperability route, not a first-line final provider candidate.

Primary sources:

- https://huggingface.co/docs/inference-providers/pricing
- https://huggingface.co/docs/inference-providers/index
- https://huggingface.co/docs/inference-providers/hub-api

### 3.7 Cerebras — retain historical serving evidence, do not prioritize

Cerebras currently describes its entry path as a **Free Trial** with $5 in free credits after account creation. This is useful for bounded evaluation, but it is not equivalent to a durable recurring free production tier.

The repository already contains ADR-001 and P12 serving-path evidence for Cerebras. No new Cerebras experiment is justified by this refresh.

Primary source:

- https://www.cerebras.ai/pricing

### 3.8 NVIDIA hosted NIM — free development endpoint, not final hosted production route

NVIDIA currently advertises free NIM API endpoints and a broad catalog of current agentic models. However, NVIDIA's own developer guidance frames the hosted free access as **prototyping/development/testing**. The production path is NVIDIA AI Enterprise or another production-grade deployment route.

Because the project's final selected hosted path must be zero-cost and production-defensible, the free hosted NIM/API Catalog is not eligible as the final hosted production provider. Historical ADR-003 compatibility/serving evidence remains useful and should not be rerun.

Primary sources:

- https://developer.nvidia.com/nim
- https://build.nvidia.com/
- https://build.nvidia.com/models
- https://docs.nvidia.com/nim/large-language-models/1.15.0/getting-started.html

## 4. Reconciliation with repository evidence

### What changed versus the historical evidence

- Gemini has a **new GA 3.7 Flash** candidate with a current Free Tier and full contract-relevant capabilities.
- Cloudflare Workers AI is now a materially stronger zero-cost candidate because the Free plan gives a clear daily allocation and fails rather than billing after the allocation.
- Groq's Free catalog has changed; Qwen 3.8 has substantially higher TPD but remains Preview, so its quota improvement does not make it a final production candidate.
- OpenRouter's free router is broader than before but remains unsuitable for controlled model comparison because of random model selection and routing/fallback variability.
- NVIDIA still offers free hosted inference, but first-party guidance keeps it in development/testing rather than final production.

### What did not change

- historical Groq GPT-OSS failures remain negative evidence;
- historical provider capacity failures remain evidence and should not be repeated;
- provider-native tool execution still must not bypass `HarnessRunner.execute_tool()`;
- provider credentials remain operational prerequisites, not evidence;
- no provider/model is selected by this factual refresh;
- no provider benchmark is authorized by this factual refresh.

## 5. Current feasible-set interpretation

After the factual refresh, the provider/model decision is no longer an open-ended search.

### Primary hosted candidates worth carrying forward

1. **Gemini 3.7 Flash** — strongest current stable/free agentic model found, but only if the Free Tier data-use policy is acceptable for the exact payload.
2. **Cloudflare Workers AI** — at least one pinned Free-plan model, with `GLM-4.7-Flash`, `Gemma 4 26B A4B`, and `Nemotron 3 120B A12B` as current capability/capacity trade-off candidates.
3. **Groq Free** — historical/control route; any new use must explicitly account for the prior GPT-OSS quality/capacity evidence rather than restarting evaluation.

### Baseline / conditional routes

- **Ollama local** — credible zero-external-cost baseline if hardware feasibility supports a suitable local model.
- **OpenRouter fixed free variant** — conditional interoperability candidate only; generic `openrouter/free` is excluded from controlled comparison.

### Screened out of the primary production comparison

- NVIDIA hosted free NIM — development/testing, not hosted production.
- Cerebras Free Trial — bounded trial rather than durable primary production path; already historically explored.
- Hugging Face routed free credits — allowance too small to justify default production selection without a measured ultra-low-volume workload.
- Groq Qwen 3.8 Preview — Preview/evaluation-only according to Groq production guidance.

## 6. Decision state after refresh

```text
current external fact refresh              COMPLETE
provider/model inference calls              0
credential/account probes                   0
production provider/model selected          NO
new benchmark authorized                    NO
provider search from zero                   NO LONGER REQUIRED
current primary hosted feasible set         GEMINI 3.7 FLASH / CLOUDFLARE FREE / GROQ FREE-HISTORICAL
conditional baseline routes                 OLLAMA LOCAL / PINNED OPENROUTER :FREE
```

The historical audit classification for D01 remains `PARTIALLY_ASSESSED`, but its next gap is now much narrower:

> determine whether Gemini Free Tier privacy/data-use is acceptable for the exact project payload; choose the minimum pinned Cloudflare representative(s); decide whether existing Groq evidence plus these new candidates leaves a material quality gap requiring a prospective comparison.

That is a **planning/reconciliation step**, not authorization to call any provider.

## 7. Next action

Do not run models yet.

The next provider task is to derive a **minimal prospective comparison candidate set** from this refresh and the historical E8/E14/P12 evidence. Before any inference call, it must:

1. resolve the Gemini Free Tier data-use/privacy eligibility question for the exact intended payload;
2. select no more Cloudflare candidates than are needed to represent materially distinct quality/capacity points;
3. decide whether Groq GPT-OSS should remain only a historical control or one live baseline under the current DecisionSource contract;
4. include a local Ollama baseline only if a no-inference hardware/model feasibility check finds a realistic model;
5. exclude `openrouter/free` router and all preview/development-only paths from final-production claims;
6. preregister exact model IDs, provider routes, case population, call budget, no-fallback/no-retry rules, metrics, hard gates and zero-cost containment;
7. still make zero provider/model inference calls until that prospective packet is frozen.

C4 exact-byte recovery remains separate and unchanged.
