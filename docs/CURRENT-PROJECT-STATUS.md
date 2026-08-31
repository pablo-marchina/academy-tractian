# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-31 — minimum Cloudflare provider/model comparison preregistered by ADR-018  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)  
**Historical evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)  
**Provider factual gates:** [`PROVIDER-PREBENCHMARK-FACTUAL-GATES-2026-08-28.md`](PROVIDER-PREBENCHMARK-FACTUAL-GATES-2026-08-28.md)  
**Frozen preregistration:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Protocol:** [`../research/provider-model-comparison-design-v2-2026-08-31.md`](../research/provider-model-comparison-design-v2-2026-08-31.md)  
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
minimum Cloudflare comparison preregistration FROZEN BY ADR-018
provider/model inference calls in ADR-018 work 0
credential/account probes in ADR-018 work     0
Cloudflare client implementation in ADR-018   0

provider/model final selection               NO
provider/model quality                       PARTIALLY_ASSESSED
broad USD-0 provider discovery               CLOSED FOR CURRENT SCOPE
D01 material gap                             DEMONSTRATED
D01 prospective comparison design            FROZEN
provider/model inference                     NOT AUTHORIZED

core candidate 1                             @cf/zai-org/glm-4.7-flash
core candidate 2                             @cf/nvidia/nemotron-3-120b-a12b
public probe units                           8
repetitions / unit / candidate               2
max future live attempts                     32
max completion tokens / attempt              512
max accounted prompt tokens / attempt        8000
max complete-packet neurons                  7937.522688
Workers Free daily allocation                10000
frozen free-allocation headroom              2062.477312 / 20.6248%
minimum free neurons before future attempt 1 9000
Workers Paid / prepaid Gateway               FORBIDDEN

Gemini 3.7 Flash public/synthetic eval        ELIGIBLE
Gemini arbitrary production payload          INELIGIBLE_BY_DEFAULT UNDER CURRENT FREE DATA-USE TERMS
Cloudflare Gemma 4 26B A4B                   EXCLUDED FROM MINIMUM FIRST PACKET
Groq GPT-OSS                                 HISTORICAL_CONTROL_ONLY
Ollama qwen3:4b                              SPEC_FEASIBLE_LOCAL_BASELINE / OUTSIDE CORE PACKET
old ADR-008 through ADR-011 execution         HISTORICAL / MUST NOT EXECUTE AS-IS
old packet calls consumed                    0 / 32

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

## 1. Evidence-first provider state

Permanent sequence:

```text
decision question
→ historical evidence audit
→ current external facts only where mutable
→ exact remaining material gap
→ preregister minimum experiment
→ freeze exact bytes + provider-free validation
→ only then separate implementation authorization
→ provider-free implementation validation
→ only then separate live-execution authorization
→ inference / evaluation / selection or NO_SELECTION
```

For D01, the project has completed through **preregistration/freeze**. No later stage is implicitly authorized by ADR-018.

## 2. ADR-018 frozen comparison

ADR-018 freezes exactly two live production-selection candidates:

1. `cloudflare_glm_4_7_flash_workers_free` → `@cf/zai-org/glm-4.7-flash`;
2. `cloudflare_nemotron_3_120b_a12b_workers_free` → `@cf/nvidia/nemotron-3-120b-a12b`.

It reuses the existing 8-unit public/synthetic population without mutation:

```text
research/experiments/provider-model-comparison-dev-population-v1.json
SHA-256 561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251
```

Geometry remains 8 units × 2 repeats × 2 live candidates = **32 maximum future live attempts**.

## 3. Frozen request boundary

A future implementation must preserve:

```text
direct Workers AI OpenAI-compatible chat completions
AI Gateway                    disabled
provider-native tool execution disabled
provider conversation state   disabled
built-in web search           disabled
stream                        false
n                             1
temperature                   0
max_completion_tokens         512
provider seed                 none
store                         false
response format               strict ProviderDecisionPayload JSON Schema
automatic repair              disabled
```

`AgentController` remains the orchestration owner and `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary.

If provider-free implementation cannot satisfy these exact semantics, inference stays blocked and ADR-018 must be amended prospectively.

## 4. Zero-cost envelope

The frozen packet upper bound is:

```text
GLM 16-attempt maximum         1002.188800 neurons
Nemotron 16-attempt maximum    6935.333888 neurons
complete packet maximum        7937.522688 neurons
Workers Free allocation       10000.000000 neurons
headroom                       2062.477312 neurons
headroom                            20.6248%
```

A future live authorization must prove without inference that execution is on **Workers Free**, prepaid AI Gateway billing is not used, Workers Paid is not used, and at least **9,000 neurons remain** for the current UTC day before attempt 1.

Provider-reported prompt/completion usage becomes authoritative during live execution. Missing accounting, exceeding the frozen per-attempt token ceilings, or a projected free-allocation breach causes fail-closed stop and incomplete `NO_SELECTION`.

## 5. Metrics / selection

M1-M7, M9 and M10 reuse ADR-008 definitions/thresholds where the provider-neutral contract is unchanged.

M8 is now Cloudflare-specific:

- actual cash cost must remain USD 0;
- exact observed neurons are calculated from provider-reported usage and frozen model rates;
- total observed neurons are the resource Pareto axis;
- missing usage is not imputed.

`NO_SELECTION` remains a valid and required outcome for hard-gate failure, unresolved ties, incomplete accounting, incomplete packet or protocol uncertainty. No weighted global score or post-result threshold tuning is allowed.

## 6. What ADR-018 does not authorize

```text
Cloudflare client/runtime implementation     NOT AUTHORIZED BY ADR-018
credential/account probing                   NOT AUTHORIZED
provider/model inference                     NOT AUTHORIZED
provider selection                           NOT DONE
production actions                           DISABLED
old #44 execution                            FORBIDDEN AS-IS
C4 change                                    NONE
semantic/blind evaluation                    NOT AUTHORIZED
topology/runtime experiments                 NOT AUTHORIZED
global architecture freeze                   NO
```

## 7. Next admissible provider step

After ADR-018 is merged with all provider-free CI green, create a **separate governed implementation task** that may implement only the minimum Cloudflare client/adapter needed to satisfy the frozen request contract and validate it provider-free.

That implementation task must still execute **zero inference**. A further explicit live-execution authorization is required before attempt 1.

## 8. Agent topology/runtime ordering

The single-agent controller remains the strong qualified baseline. Multi-agent and runtime comparisons remain queued until the provider/model basis is controlled. Do not implement them yet.

## 9. C4 — unchanged parallel track

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
gate     REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

Only exact-byte recovery is authorized. Reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain unauthorized.

## 10. Still forbidden

- executing ADR-008/#44 as frozen;
- writing provider-specific runtime code as part of ADR-018;
- provider inference before a separately frozen live authorization;
- credential/account probing merely to prove connection state;
- Paid Workers, prepaid AI Gateway or any paid spillover;
- Groq rerun for freshness;
- silently adding Gemma/Gemini/Ollama/other candidates;
- hidden retries/fallbacks/warm-ups/provider state;
- weakening `HarnessRunner`, authorization/idempotency or evaluator-private boundaries;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime work;
- final architecture or production-readiness claims before remaining material decisions close.
