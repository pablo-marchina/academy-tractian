# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 — provider pre-benchmark factual gates closed  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)  
**Historical evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)  
**Provider fact refresh:** [`PROVIDER-ZERO-COST-FACT-REFRESH-2026-08-28.md`](PROVIDER-ZERO-COST-FACT-REFRESH-2026-08-28.md)  
**Pre-benchmark gates:** [`PROVIDER-PREBENCHMARK-FACTUAL-GATES-2026-08-28.md`](PROVIDER-PREBENCHMARK-FACTUAL-GATES-2026-08-28.md)  
**Latest addendum:** [`DECISION-REVALIDATION-ADDENDUM-004-PROVIDER-PREBENCHMARK-GATES.md`](DECISION-REVALIDATION-ADDENDUM-004-PROVIDER-PREBENCHMARK-GATES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts and ADRs remain authoritative for their exact historical scopes.

## Executive state

```text
Project North Star                           strongest defensible TRACTIAN/Inteli delivery under P1-P4
permanent external service/API cost          USD 0 HARD CONSTRAINT
evidence audit before new experiment         REQUIRED
historical material-decision audit           COMPLETE
current provider fact refresh                COMPLETE
provider pre-benchmark factual gates         COMPLETE
provider/model inference calls in this work  0
credential/account probes in this work       0

provider/model final selection               NO
provider/model quality                       PARTIALLY_ASSESSED
broad USD-0 provider discovery               CLOSED FOR CURRENT SCOPE
new material provider gap                    DEMONSTRATED
minimum comparison preregistration           AUTHORIZED NEXT
provider/model inference                      NOT AUTHORIZED YET

Gemini 3.7 Flash public/synthetic eval        ELIGIBLE
Gemini 3.7 Flash arbitrary production data   INELIGIBLE_BY_DEFAULT UNDER CURRENT FREE DATA-USE TERMS
Cloudflare GLM 4.7 Flash                     RETAIN FOR MINIMUM PROSPECTIVE COMPARISON
Cloudflare Nemotron 3 120B A12B              RETAIN FOR MINIMUM PROSPECTIVE COMPARISON
Cloudflare Gemma 4 26B A4B                   EXCLUDED FROM MINIMUM FIRST COMPARISON
Groq GPT-OSS                                 HISTORICAL_CONTROL_ONLY
Ollama qwen3:4b                              SPEC_FEASIBLE_LOCAL_BASELINE / HOST FIT UNVERIFIED
old ADR-008 OpenAI/Gemini packet             HISTORICAL / MUST NOT EXECUTE AS-IS

single-agent controller                      STRONG QUALIFIED BASELINE
single-vs-multi final topology               NOT SELECTED / QUEUED AFTER PROVIDER BASIS
runtime/orchestration final choice           NOT SELECTED / QUEUED
native ToolSpec + conditional MCP adapter    EVIDENCE SUFFICIENT FOR CURRENT SCOPE
evidence-sufficiency stopping                EVIDENCE SUFFICIENT FOR CURRENT SCOPE
RAG/vector/reranking                         NO MATERIAL CURRENT GAP / NO EXPERIMENT
persistent memory                            NO MATERIAL CURRENT GAP / NO EXPERIMENT
adaptive model routing                       UNASSESSED / NOT CURRENTLY MATERIAL

C4 scientific gate                          REQUIRED_PER_GROUP_AND_SLICE_REPORTING
C4 exact-row artifact                        EXTERNALLY BLOCKED / EXACT-BYTE RECOVERY ONLY
provider-free safety/reliability             EVIDENCE SUFFICIENT WITH BOUNDED NON-CLAIMS
operational deterministic evaluator          EVIDENCE SUFFICIENT
scientific evaluator / EV-012                PARTIALLY ASSESSED / C4 BLOCKED
observability via RunTrace                   EVIDENCE SUFFICIENT FOR CURRENT SCOPE

global final architecture                    UNFROZEN
production-readiness claim                   NOT AUTHORIZED
real customer mutations performed            0
```

## 1. Evidence-first state

Permanent sequence:

```text
decision question
→ repository historical evidence audit
→ current external facts only where mutable
→ exact remaining gap
→ preregister minimum experiment only if necessary
→ only then implementation / inference
→ evaluation / regression / decision
```

The provider path has now completed the first four stages. A new benchmark is justified only for the narrow current gap described below; no inference is authorized until its prospective packet is frozen.

## 2. Provider factual gates — closed

### Gemini Free Tier

The provider adapter sends provider-visible `user_request`, tool status metadata and observation `body` while withholding runtime secrets, authorization and evaluator-private state. The old eight-probe provider population is public/synthetic and can be used without exposing private evaluator truth.

Current Gemini Free Tier content is used to improve Google products. Therefore:

```text
public/synthetic provider probes              eligible
general production payload                    ineligible by default
final production candidate under current path no
```

A future validated data-minimization/redaction boundary or changed terms may reopen this decision prospectively.

### Cloudflare Workers AI Free

Retain exactly two materially distinct representatives for the minimum prospective comparison:

- `@cf/zai-org/glm-4.7-flash` — efficient current agentic point;
- `@cf/nvidia/nemotron-3-120b-a12b` — materially heavier model/capacity point.

`@cf/google/gemma-4-26b-a4b-it` is not globally rejected, but is excluded from the minimum first comparison because its larger context/lower output-neuron advantage does not map to a demonstrated current requirement and it adds calls without a clearly separate decision dimension.

### Groq Free

Groq is now `HISTORICAL_CONTROL_ONLY` for the next provider-selection step. E8 operational evidence, E14 GPT-OSS negative task-quality evidence and P12-C2/C3 capacity failures remain binding. Current GPT-OSS-120B Free limits do not reverse the capacity evidence; Qwen 3.8 remains Preview. No freshness rerun is justified.

### Ollama local

`qwen3:4b` is a factually credible local baseline: current model artifact is about 2.5 GB and Ollama documents Qwen3 tool calling plus local JSON-schema structured output. Exact current-host performance/RAM/VRAM remains unverified. It can enter a future packet only if a no-inference host inventory passes before freeze.

## 3. D01 — exact remaining gap

A new material gap is now demonstrated:

> the repository has no controlled project-specific decision-quality/reliability/latency evidence that can choose between current production-eligible Cloudflare GLM 4.7 Flash and Nemotron 3 120B A12B.

Documentation capability claims are not enough to select the best project-specific Pareto point.

Therefore:

```text
minimum prospective comparison required       YES
planning / preregistration                     AUTHORIZED NEXT
provider inference                             NOT AUTHORIZED
production provider selected                   NO
```

The future packet should reuse the existing eight public synthetic DecisionSource probes and M1–M10 definitions wherever they remain valid rather than inventing a new benchmark population.

## 4. Next provider task

Create and freeze a **prospective provider/model comparison amendment** before any inference. Core candidates:

1. `@cf/zai-org/glm-4.7-flash`;
2. `@cf/nvidia/nemotron-3-120b-a12b`.

Conditional local baseline: `qwen3:4b` only if no-inference host metadata proves it can be run locally.

Historical control: existing Groq evidence only.

The packet must freeze exact route IDs, public probe population, repetitions/call ceiling, token/output bounds, Cloudflare neuron upper bound, no-retry/no-fallback/no-warm-up behavior, M1–M10 mapping, hard gates, Pareto semantics and durable evidence custody before attempt 1.

## 5. Agent topology/runtime ordering

The single-agent controller remains the strong qualified baseline. Multi-agent and runtime comparisons remain queued until the provider/model basis is controlled; do not implement them yet. Historical runtime and topology evidence remains preserved.

## 6. C4 — unchanged parallel track

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
gate     REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

Only exact-byte recovery is authorized. Reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain unauthorized.

## 7. Preserved delivery evidence

```text
ADR-004 controller regression              12 / 12 PASS
EV-007 safety expectations                 11 / 11
EV-008 stability                           30 / 30 runs; 66 / 66 checks
EV-011 communication predicates            60 / 60
ADR-016 integrated demo                     5 / 5
ADR-017 acceptance rows                    83
PASS_EVIDENCED                             41
PASS_BOUNDED                               40
EXTERNALLY_BLOCKED                          1   C4 / EV-012
UNEXECUTED_GATED                            1   historical live-provider row
GAP_ACTION_REQUIRED                         0
```

These are bounded historical claims; they do not establish current Cloudflare model quality, C4 completion, final topology or unconditional production readiness.

## 8. Still forbidden

- executing ADR-008/#44 as currently frozen;
- provider inference before the new prospective packet is frozen;
- redundant Groq reruns;
- using Gemini Free for arbitrary production payload under the current unsanitized provider request path;
- silently adding Gemma or any other provider/model without a new material inclusion rationale;
- hidden retry/fallback/warm-up/provider state;
- paid provider/service production usage;
- weakening `HarnessRunner`, authorization/idempotency or evaluator-private boundaries;
- reconstructing/rescoring/substituting C4;
- starting multi-agent/runtime work before the provider basis is controlled;
- claiming final architecture or production readiness before remaining material decisions close.
