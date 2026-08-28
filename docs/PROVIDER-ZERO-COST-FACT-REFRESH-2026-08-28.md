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
- model lifecycle state;
- structured-output and function/tool-call support;
- published free quota/capacity semantics;
- paid-spillover behavior and fail-closed properties;
- provider terms that affect production eligibility.

Primary sources were checked on 2026-08-28. No community benchmark, secondary comparison site or provider inference output is used as evidence here.

## 2. Current factual screening

| Provider/path | Current relevant free model/path | USD-0 status | Material facts | Screening |
|---|---|---|---|---|
| Google Gemini Developer API | `gemini-3.7-flash` | Free Tier input/output free | GA/stable; function calling; structured outputs; thinking; 1M input / 64k output; Free Tier content is used to improve Google products; exact account limits not probed | `CONDITIONAL_ELIGIBLE` — technically strong, but exact payload must pass the Free Tier data-use/privacy gate |
| Groq Free | `openai/gpt-oss-120b`, `openai/gpt-oss-20b`; preview `qwen/qwen3.8-27b` | published Free Plan quotas | GPT-OSS supports strict structured outputs; hosted models support tool use; strict Structured Outputs + tool use are not supported together; Qwen 3.8 is Preview; GPT-OSS 120B has preserved project-specific negative evidence | `ELIGIBLE_WITH_HISTORICAL_PENALTY` — historical/control route, not a blank-slate frontier candidate |
| Cloudflare Workers AI Free | `@cf/zai-org/glm-4.7-flash`, `@cf/google/gemma-4-26b-a4b-it`, `@cf/nvidia/nemotron-3-120b-a12b` | 10,000 neurons/day on Workers Free | over-allocation on Free requires upgrade rather than silent billing; screened models expose function calling/reasoning; OpenAI-compatible parameters include `response_format`, `tools`, `tool_choice`, `seed` | `ELIGIBLE` — strongest newly surfaced fail-closed hosted USD-0 alternative |
| OpenRouter Free | fixed `:free` variants; generic `openrouter/free` router | Free plan/free variants | 50 requests/day plan cap; generic free router chooses an eligible free model dynamically; provider fallback routing may retry another provider | `CONDITIONAL_ELIGIBLE_FIXED_MODEL_ONLY`; generic router excluded from controlled comparison |
| Ollama local | local tool-capable open-weight models | no external API charge | tool calling; multi-turn tool loops; JSON-schema structured outputs | `ELIGIBLE_LOCAL_BASELINE`, subject to hardware/model feasibility facts |
| Hugging Face Inference Providers | routed free-user credits | $0.10/month for Free users | additional routed use requires purchased credits | `BOUNDED_EXPERIMENT_ONLY`; too small for default production path absent an ultra-low-volume proof |
| Cerebras Inference | Free Trial | $5 free trial credits | bounded trial, not durable recurring free production tier | `NOT_PRIMARY_PRODUCTION_CANDIDATE`; retain historical serving evidence |
| NVIDIA hosted NIM/API Catalog | free hosted endpoints | development/testing access | NVIDIA positions free hosted endpoints for prototyping/development/testing; production uses a production/enterprise path | `INELIGIBLE_FOR_FINAL_HOSTED_PRODUCTION`; preserve historical compatibility evidence |

## 3. Provider details

### 3.1 Google Gemini

Current first-party documentation states that `gemini-3.7-flash` is GA/stable and intended for agentic workflows. It supports function calling, structured outputs, thinking, a 1,048,576-token input window and 65,536 output tokens.

The current pricing table lists Free Tier input and output for Gemini 3.7 Flash as free of charge. Active RPM/TPM/RPD limits depend on project/model and are shown in AI Studio; this refresh deliberately did not inspect the account.

The material constraint is the Free Tier data-use policy: current pricing documentation states Free Tier content is used to improve Google products, while Paid Tier content is not. Gemini therefore remains `CONDITIONAL_ELIGIBLE` until the exact intended project payload is judged acceptable under that policy.

**Historical provenance correction:** ADR-008 already used `gemini-3.7-flash` as its frozen Google candidate. The material change in this refresh is **not** a new Gemini model ID. It is the current confirmation that the same model is GA with a Free Tier, together with the now-explicit Free Tier data-use gate and the changed zero-cost feasible set after the OpenAI candidate became ineligible.

Primary sources:

- https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash
- https://ai.google.dev/gemini-api/docs/latest-model
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits
- https://ai.google.dev/gemini-api/docs/function-calling
- https://ai.google.dev/gemini-api/docs/structured-output

### 3.2 Groq Free

Current Free Plan documentation includes:

- `openai/gpt-oss-120b`: 30 RPM / 1K RPD / 8K TPM / 200K TPD;
- `openai/gpt-oss-20b`: 30 RPM / 1K RPD / 8K TPM / 200K TPD;
- `qwen/qwen3.8-27b`: 30 RPM / 1K RPD / 8K TPM / 2M TPD.

Groq documents strict Structured Outputs for GPT-OSS 20B/120B and Qwen 3.8 27B and tool use for hosted models. It also states that strict Structured Outputs and tool use cannot currently be combined in one Structured Outputs request. The repository can keep real TRACTIAN execution inside `HarnessRunner`, so provider-native tool dispatch is not required.

Qwen 3.8 is currently a **Preview** model; Groq states Preview models are intended for evaluation and should not be used in production. GPT-OSS 120B is a production model, but E14/P12 already preserve negative project-specific quality and capacity evidence. Those failures remain binding evidence and must not be rerun away.

Primary sources:

- https://console.groq.com/docs/rate-limits
- https://console.groq.com/docs/models
- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/tool-use/overview
- https://console.groq.com/docs/billing-faqs

### 3.3 Cloudflare Workers AI Free

Workers AI currently provides **10,000 neurons/day free** on Workers Free. Current pricing documentation makes further usage a plan-upgrade boundary rather than an automatic paid spillover path, which matches the project's fail-closed USD-0 requirement.

Current agent-relevant screened models include:

| Model | Context | Function calling / reasoning | Neurons per M input | Neurons per M output |
|---|---:|---|---:|---:|
| `@cf/zai-org/glm-4.7-flash` | 131,072 | yes / yes | 5,500 | 36,400 |
| `@cf/google/gemma-4-26b-a4b-it` | 256,000 | yes / yes | 9,091 | 27,273 |
| `@cf/nvidia/nemotron-3-120b-a12b` | 256,000 | yes / yes | 45,455 | 136,364 |

Their model/API schemas expose contract-relevant parameters including `response_format`, `tools`, `tool_choice` and a best-effort `seed`. Several newer models explicitly require Workers Paid and are excluded from the zero-cost feasible set.

Primary sources:

- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://developers.cloudflare.com/workers-ai/
- https://developers.cloudflare.com/workers-ai/features/json-mode/
- https://developers.cloudflare.com/workers-ai/features/function-calling/
- https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/
- https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/
- https://developers.cloudflare.com/workers-ai/models/nemotron-3-120b-a12b/
- https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/

### 3.4 OpenRouter Free

OpenRouter currently exposes free models and a Free plan with a published 50 requests/day cap. Structured-output support depends on the selected endpoint and tool calling is standardized at the API surface.

The generic `openrouter/free` route is **not** suitable for a controlled model comparison because it dynamically selects among eligible free models. OpenRouter also documents provider fallback routing that can try another provider before an upstream failure reaches the client. A future controlled use must therefore pin an exact free model/route and explicitly prevent uncontrolled routing/fallback behavior.

Primary sources:

- https://openrouter.ai/pricing
- https://openrouter.ai/openrouter/free/
- https://openrouter.ai/docs/api_reference/limits
- https://openrouter.ai/docs/guides/features/structured-outputs
- https://openrouter.ai/collections/tool-calling-models

### 3.5 Ollama local

Ollama supports local function/tool calling, parallel and multi-turn tool loops, and JSON-schema structured outputs. This makes local open-weight execution a valid zero-external-charge baseline, but this factual refresh intentionally did not choose or execute a model. Hardware fit, memory footprint and latency remain a no-inference feasibility question if the local baseline is carried into a future packet.

Primary sources:

- https://docs.ollama.com/capabilities/tool-calling
- https://docs.ollama.com/capabilities/structured-outputs
- https://docs.ollama.com/api/introduction

### 3.6 Hugging Face Inference Providers

Current first-party pricing gives Free users **$0.10/month** of Inference Providers credits; extra routed usage requires purchased credits. The path is technically free within that tiny bound, but it is not a credible default production route without proving that the intended workload permanently fits inside it.

Primary sources:

- https://huggingface.co/docs/inference-providers/pricing
- https://huggingface.co/docs/inference-providers/index
- https://huggingface.co/docs/inference-providers/hub-api

### 3.7 Cerebras

Cerebras currently describes the entry path as a **Free Trial** with $5 in credits after account creation. This is useful as bounded serving evidence but not equivalent to a durable recurring free production tier. ADR-001/P12 already contain project-specific Cerebras serving work, so no new Cerebras experiment is justified by this refresh.

Primary source:

- https://www.cerebras.ai/pricing

### 3.8 NVIDIA hosted NIM

NVIDIA advertises free NIM/API Catalog access, but current first-party developer guidance frames the hosted free path as prototyping/development/testing and points production to enterprise/production deployment routes. The free hosted endpoint is therefore not eligible as the project's final hosted production provider under the USD-0 production constraint. Historical ADR-003 compatibility evidence remains useful and should not be repeated.

Primary sources:

- https://developer.nvidia.com/nim
- https://build.nvidia.com/
- https://build.nvidia.com/models
- https://docs.nvidia.com/nim/large-language-models/1.15.0/getting-started.html

## 4. Reconciliation with historical repository evidence

### Materially new/current facts

- Gemini 3.7 Flash remains the same historical candidate ID, but is now confirmed current GA/free and carries an explicit Free Tier data-use gate.
- Cloudflare Workers AI is a materially credible new zero-cost candidate because its Free allocation is bounded and the screened agentic models expose the needed contract primitives.
- Groq's Free catalog changed; Qwen 3.8 has larger TPD but is Preview and therefore not a clean production candidate.
- OpenRouter's current generic free router remains unsuitable for controlled model identity because routing is dynamic and fallbacks may hide upstream failures.
- NVIDIA still offers free hosted inference, but its first-party production distinction keeps that endpoint out of the final hosted production feasible set.

### Historical evidence that remains binding

- E8 Groq operational/schema/trace evidence;
- E14 GPT-OSS negative task-quality evidence;
- P12-C2/C3 Groq capacity failures;
- ADR-001 serving-path/capacity comparison;
- ADR-002/003 and later provider-serving probes;
- ADR-006→011 provider-neutral client/executor/custody engineering;
- provider-native TRACTIAN execution remains forbidden outside `HarnessRunner.execute_tool()`.

## 5. Current feasible-set interpretation

The provider decision is no longer an open-ended discovery problem.

### Primary hosted candidates to carry forward

1. **Gemini 3.7 Flash** — only if the exact payload passes the Free Tier data-use/privacy gate.
2. **Cloudflare Workers AI Free** — one or more **pinned** models representing genuinely distinct quality/capacity points; do not carry all three automatically.
3. **Groq Free** — historical/control route; any future live use must incorporate the existing negative evidence rather than restart evaluation.

### Conditional baselines

- **Ollama local** — only if a no-inference hardware/model feasibility check identifies a realistic local model.
- **OpenRouter fixed `:free` variant** — interoperability candidate only if exact model/provider routing and no-fallback behavior can be pinned.

### Screened out of the primary production comparison

- NVIDIA hosted free NIM — development/testing rather than free hosted production;
- Cerebras Free Trial — bounded trial, already historically explored;
- Hugging Face routed free credit — too small for a default production route without ultra-low-volume proof;
- Groq Qwen 3.8 Preview — Preview/evaluation lifecycle, not production.

## 6. Decision state after refresh

```text
external fact refresh                       COMPLETE
provider/model inference calls               0
credential/account probes                    0
production provider/model selected           NO
new benchmark authorized                     NO
provider search from zero                    NO LONGER REQUIRED
primary hosted feasible set                  GEMINI 3.7 FLASH / CLOUDFLARE FREE / GROQ HISTORICAL CONTROL
conditional baselines                        OLLAMA LOCAL / PINNED OPENROUTER :FREE
```

D01 remains `PARTIALLY_ASSESSED`, but the remaining work is now precise:

1. resolve Gemini Free Tier data-use eligibility for the exact intended payload;
2. select the minimum Cloudflare representative set by capability/capacity, not popularity;
3. decide whether Groq should be historical-only or one live control under the current DecisionSource contract;
4. determine whether an Ollama baseline is hardware-feasible without inference;
5. then decide whether a **minimal prospective provider comparison** is still necessary.

This document does **not** authorize provider calls or a benchmark.

C4 exact-byte recovery remains separate and unchanged.
