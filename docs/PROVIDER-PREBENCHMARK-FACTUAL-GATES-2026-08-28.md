# Academy × TRACTIAN — Provider Pre-Benchmark Factual Gates

**Status:** COMPLETE / no-inference decision checkpoint  
**Date:** 2026-08-28  
**Baseline:** `main@7e364ff6c7636d0719935c48349a322b87878007`  
**Provider/model inference calls:** 0  
**Credential/account probes:** 0  
**Scientific state changed:** no  
**Purpose:** close the four factual decisions left by Addendum 003 before deciding whether a new provider/model experiment is justified.

## 1. Decision summary

| Gate | Decision | Result |
|---|---|---|
| G1 Gemini data use | Is the exact provider payload admissible on Gemini Free Tier? | `PUBLIC_SYNTHETIC_EVAL_ELIGIBLE / PRODUCTION_PAYLOAD_INELIGIBLE_BY_DEFAULT` |
| G2 Cloudflare representatives | Which current Free models are minimally necessary? | retain `GLM-4.7-Flash` + `Nemotron-3-120B-A12B`; exclude Gemma from the minimum set |
| G3 Groq control role | Must Groq be called again? | `HISTORICAL_CONTROL_ONLY` |
| G4 Ollama baseline | Does a realistically runnable local baseline exist by specs? | `SPEC_FEASIBLE_LOCAL_BASELINE`: `qwen3:4b`; exact host performance remains unverified |
| D01 remaining gap | Is a new quality comparison still materially necessary? | **YES — minimum prospective comparison is justified; inference remains unauthorized until preregistration is frozen** |

No provider is selected by this document.

## 2. G1 — Gemini Free Tier payload gate

### 2.1 What the repository actually sends

`src/academy_tractian/decision_source.py` defines the provider-visible `ProviderDecisionRequest`. It intentionally excludes runtime-owned secrets/identity/action authorization/evaluator-private state, but it includes:

- `user_request` verbatim;
- `turn_index` and `tool_call_count`;
- every provider-visible observation, including `tool_name`, status metadata and `body`;
- the public projection of all canonical ToolSpecs.

Therefore the production adapter can send raw user text and raw supplied-API/tool observation bodies to a provider. Sanitized trace provenance does not change what is transmitted to the provider itself.

### 2.2 Upcoming public comparison payload

The frozen public provider population in `provider-model-comparison-dev-population-v1.json` is explicitly synthetic/public DEV-only:

- 8 public probes;
- synthetic IDs such as `asset_dev_probe_001`;
- no private oracle;
- no validation/locked-test/fresh-blind inputs;
- no historical private task-quality truth;
- provider calls authorized by the population: 0.

On data-classification grounds, those exact public/synthetic probe payloads are acceptable for a Free-Tier comparison because they do not expose project-private evaluator truth or real operational observation bodies.

### 2.3 Production payload

Current Google Gemini pricing documentation states that Gemini Developer API Free Tier content is used to improve Google products, while Paid Tier content is not.

Because the production `ProviderDecisionRequest` can contain unsanitized user text and tool observation bodies, the project cannot make a defensible blanket claim that arbitrary operational/customer payload is suitable for that data-use policy. The project has no separate provider-visible redaction/classification boundary proving otherwise.

**Decision:**

```text
Gemini 3.7 Flash / public synthetic probes      ELIGIBLE
Gemini 3.7 Flash / arbitrary production payload INELIGIBLE_BY_DEFAULT
Gemini final production selection               NO
```

Do not benchmark Gemini merely for final production selection while that production eligibility is absent. A later prospective privacy/redaction architecture could reopen this decision, but it would require its own evidence and must not silently alter the current provider contract.

Primary source checked 2026-08-28:
- https://ai.google.dev/gemini-api/docs/pricing

Repository evidence:
- `src/academy_tractian/decision_source.py`
- `research/experiments/provider-model-comparison-dev-population-v1.json`
- ADR-006 through ADR-008

## 3. G2 — Minimum Cloudflare Workers AI representative set

Workers Free provides 10,000 neurons/day and requires a plan upgrade to consume paid overage. The three screened models remain available on Workers Free.

| Candidate | Context | Function/reasoning | Neurons/M input | Neurons/M output | Current role |
|---|---:|---|---:|---:|---|
| `@cf/zai-org/glm-4.7-flash` | 131,072 | yes / yes | 5,500 | 36,400 | retain — efficient agentic point |
| `@cf/google/gemma-4-26b-a4b-it` | 256,000 | yes / yes | 9,091 | 27,273 | exclude from minimum set |
| `@cf/nvidia/nemotron-3-120b-a12b` | 256,000 | yes / yes | 45,455 | 136,364 | retain — materially heavier model/capacity point |

### Why GLM is retained

GLM is the lowest input-neuron-cost point of the three and its 131k context already exceeds the current public DecisionSource probe needs by a very large margin. It is a credible efficiency-side representative without weakening the required function/reasoning contract.

### Why Nemotron is retained

Nemotron is materially separated from GLM in model scale/serving resource consumption and provider positioning. It creates the clearest current hypothesis that additional model capacity may trade efficiency for decision quality. This is a hypothesis to measure, not a quality claim.

### Why Gemma is excluded from the minimum comparison

Gemma has a larger context than GLM and lower output-neuron cost, but neither advantage maps to a demonstrated current requirement:

- the current public probe population is far below 131k context;
- the `ProviderDecisionPayload` is a compact structured decision, so output volume is intentionally bounded;
- Gemma does not introduce a required capability absent from both retained endpoints;
- its resource point sits between the efficient GLM path and the substantially heavier Nemotron path for the dimensions material to this task.

Including all three would increase calls without testing a clearly separate current requirement or risk. Under the evidence-first/minimum-experiment rule, Gemma is therefore prospectively excluded from the **minimum first comparison**, not globally rejected.

Primary sources checked 2026-08-28:
- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/
- https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/
- https://developers.cloudflare.com/workers-ai/models/nemotron-3-120b-a12b/

## 4. G3 — Groq role

**Decision: `HISTORICAL_CONTROL_ONLY`. No new Groq inference is justified for the next provider-selection packet.**

Evidence chain:

1. E8 already established zero-cost Groq operational/schema/trace feasibility.
2. E14g→E14l exercised `openai/gpt-oss-120b`; operational completeness was recovered, but task-quality/decision/action/escalation gates still failed. The historical evidence audit explicitly closes that tuning family.
3. P12-C2 completed 31/36 parents and P12-C3 only 3/36 before provider rate-limit/transport failure; ADR-001 rejected the same Groq Free route under those limits.
4. Current first-party Free limits for GPT-OSS 120B remain 30 RPM / 1K RPD / 8K TPM / 200K TPD. No capacity reversal trigger has appeared.
5. `openai/gpt-oss-20b` has the same published Free quota and does not supply a new requirement-specific hypothesis strong enough to justify resetting the larger model's negative quality evidence.
6. Qwen 3.8 has more daily-token headroom but is Preview; Groq states Preview models are evaluation-only and should not be used in production.

A new Groq call would therefore be a freshness rerun, not the minimum work needed to answer D01. Historical Groq results remain visible as negative/control evidence when interpreting the future comparison.

Reversal trigger: reopen only if a production Groq model/route changes a material previously failing dimension (quality hypothesis, contract semantics, or free capacity) rather than merely being newly available.

Primary sources checked 2026-08-28:
- https://console.groq.com/docs/rate-limits
- https://console.groq.com/docs/models
- https://console.groq.com/docs/structured-outputs

Repository evidence:
- `MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`
- ADR-001
- E8/E14/P12 preserved results

## 5. G4 — Ollama baseline feasibility by specifications only

A realistic local baseline exists without using an external inference service.

**Selected factual baseline:** `qwen3:4b` on local Ollama.

Current first-party model metadata:

```text
model tag                         qwen3:4b
model artifact size               ~2.5 GB
advertised model context          256K on current tag
modal input                       text
Ollama tool-calling examples      Qwen3 supported
thinking                          Qwen3 supported
structured JSON schema            Ollama local API supported
external API charge               USD 0
```

Ollama's own documentation uses Qwen3 for tool calling and explicitly demonstrates `qwen3:4b` in an agent/tool workflow. Ollama also supports JSON-schema structured output through the local API. The 2.5 GB model artifact is materially more realistic for commodity local hardware than the historical 80GB-class self-hosted GPT-OSS-120B path rejected in ADR-001.

Important boundary: artifact size is not a promise of acceptable latency or enough RAM/VRAM on this exact host. Ollama states context length increases memory requirements and chooses lower default context on lower-VRAM hardware. No model was downloaded or executed here, and the repository still lacks an exact current-host RAM/VRAM performance proof.

**Decision:** `qwen3:4b` is a `SPEC_FEASIBLE_LOCAL_BASELINE`, not yet a measured production candidate. It may enter a future preregistration only after a no-inference host inventory confirms sufficient storage/memory/runtime availability. That host inventory is operational metadata, not a model-quality experiment.

Primary sources checked 2026-08-28:
- https://ollama.com/library/qwen3
- https://ollama.com/library/qwen3/tags
- https://docs.ollama.com/capabilities/tool-calling
- https://docs.ollama.com/capabilities/structured-outputs
- https://docs.ollama.com/context-length
- https://docs.ollama.com/faq

## 6. Does D01 still require a benchmark?

**Yes. A precise new gap remains.**

After closing G1-G4:

```text
Gemini Free                    public/synthetic eval only; not final production candidate by default
Cloudflare GLM 4.7 Flash      current production-eligible USD-0 candidate; no project task-quality evidence
Cloudflare Nemotron 120B      current production-eligible USD-0 candidate; no project task-quality evidence
Cloudflare Gemma 4 26B        excluded from minimum first packet
Groq GPT-OSS                  historical control only; no rerun
Ollama qwen3:4b               spec-feasible local baseline; host performance not yet qualified
```

The repository has no controlled project-specific decision-quality/reliability/latency evidence that can choose between the two retained current Cloudflare models. Documentation/capability tables cannot establish which lies on the best project-specific Pareto frontier.

Therefore D01 remains `PARTIALLY_ASSESSED`, but the missing evidence is now small and explicit:

> compare the retained production-eligible Cloudflare models under the existing public DecisionSource population and frozen safety/evaluator boundaries, with an Ollama local baseline only if host feasibility is confirmed before preregistration.

This checkpoint authorizes **planning/preregistration of the minimum prospective comparison only**. It does not authorize inference, credential probing, provider calls or modification of the old ADR-008 packet.

## 7. Next step

Create a prospective provider/model comparison amendment that:

- supersedes the old candidate set prospectively without rewriting ADR-008;
- uses exactly `@cf/zai-org/glm-4.7-flash` and `@cf/nvidia/nemotron-3-120b-a12b` as the core live candidates;
- optionally adds `qwen3:4b` only if a no-inference host inventory passes before freeze;
- reuses the existing 8 public synthetic probe units unless an evidence audit finds a concrete defect;
- reuses frozen M1–M10 definitions where still applicable rather than inventing new metrics;
- keeps Groq as historical control only and Gemini outside final production selection;
- freezes exact call budget, repetitions, output/token ceilings, Cloudflare neuron upper bound, no-retry/no-fallback semantics and durable evidence custody before attempt 1;
- executes zero inference until that packet is reviewed/frozen.

C4 remains separate and unchanged.