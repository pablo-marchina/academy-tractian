# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-31 — Cloudflare provider-free client implementation frozen by ADR-019  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)  
**Historical evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)  
**Frozen preregistration:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Frozen provider-free client:** [`adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md`](adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts and ADRs remain authoritative for their exact historical scopes.

## Executive state

```text
Project North Star                              strongest defensible TRACTIAN/Inteli delivery under P1-P4
permanent external service/API cost             USD 0 HARD CONSTRAINT
evidence audit before new experiment            REQUIRED
historical material-decision audit              COMPLETE
provider factual gates                          COMPLETE
minimum Cloudflare comparison preregistration   FROZEN BY ADR-018
Cloudflare provider-free client implementation  FROZEN BY ADR-019

provider/model inference calls in ADR-019 work  0
credential/account probes in ADR-019 work       0
live network validation in ADR-019 work         0
comparison attempts consumed                    0 / 32
production provider/model selected              NO
provider/model inference                        NOT AUTHORIZED

core candidate 1                                @cf/zai-org/glm-4.7-flash
core candidate 2                                @cf/nvidia/nemotron-3-120b-a12b
public probe units                              8
repetitions / unit / candidate                  2
max future live attempts                        32
max completion tokens / attempt                 512
max accounted prompt tokens / attempt           8000
max complete-packet neurons                     7937.522688
Workers Free daily allocation                   10000
minimum free neurons before future attempt 1    9000
Workers Paid / prepaid Gateway                  FORBIDDEN

Cloudflare direct client                        IMPLEMENTED / PROVIDER-FREE VALIDATED
client environment credential lookup            NONE
client concrete network transport               NONE / INJECTED INTERFACE ONLY
client retry/fallback/warm-up                    NONE
provider-native tool execution                  REJECTED
AI Gateway                                      DISABLED
model allowlist                                 EXACT ADR-018 TWO MODELS
usage fabrication                               FORBIDDEN

old ADR-008 through ADR-011 execution            HISTORICAL / MUST NOT EXECUTE AS-IS
Groq GPT-OSS                                    HISTORICAL_CONTROL_ONLY
Gemini arbitrary production payload             INELIGIBLE_BY_DEFAULT UNDER CURRENT FREE DATA-USE TERMS
Ollama qwen3:4b                                 SPEC_FEASIBLE_LOCAL_BASELINE / OUTSIDE CORE PACKET

single-agent controller                         STRONG QUALIFIED BASELINE
single-vs-multi final topology                  NOT SELECTED / QUEUED AFTER PROVIDER BASIS
runtime/orchestration final choice              NOT SELECTED / QUEUED
native ToolSpec + conditional MCP adapter       EVIDENCE SUFFICIENT FOR CURRENT SCOPE
evidence-sufficiency stopping                   EVIDENCE SUFFICIENT FOR CURRENT SCOPE
RAG/vector/reranking                            NO MATERIAL CURRENT GAP / NO EXPERIMENT
persistent memory                               NO MATERIAL CURRENT GAP / NO EXPERIMENT
adaptive model routing                          UNASSESSED / NOT CURRENTLY MATERIAL

C4 scientific gate                              REQUIRED_PER_GROUP_AND_SLICE_REPORTING
C4 exact-row artifact                           EXTERNALLY BLOCKED / EXACT-BYTE RECOVERY ONLY
provider-free safety/reliability                EVIDENCE SUFFICIENT WITH BOUNDED NON-CLAIMS
operational deterministic evaluator             EVIDENCE SUFFICIENT
scientific evaluator / EV-012                   PARTIALLY ASSESSED / C4 BLOCKED
observability via RunTrace                      EVIDENCE SUFFICIENT FOR CURRENT SCOPE

global final architecture                       UNFROZEN
production-readiness claim                      NOT AUTHORIZED
real customer mutations performed               0
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
→ separate implementation authorization
→ provider-free implementation validation + freeze
→ audit existing execution/custody evidence before new live machinery
→ only concrete gaps may authorize new implementation
→ separate live-execution authorization
→ inference / evaluation / selection or NO_SELECTION
```

For D01, the project has completed through **provider-free client implementation/freeze**. Attempt 1 remains unauthorized.

## 2. ADR-018 — frozen comparison design

ADR-018 freezes exactly two production-selection candidates:

1. `cloudflare_glm_4_7_flash_workers_free` → `@cf/zai-org/glm-4.7-flash`;
2. `cloudflare_nemotron_3_120b_a12b_workers_free` → `@cf/nvidia/nemotron-3-120b-a12b`.

It reuses the existing 8-unit public/synthetic population without mutation:

```text
research/experiments/provider-model-comparison-dev-population-v1.json
SHA-256 561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251
```

Geometry remains 8 units × 2 repeats × 2 live candidates = **32 maximum future live attempts**.

## 3. ADR-019 — provider-free client implementation

ADR-019 freezes these implementation identities:

```text
src/academy_tractian/cloudflare_provider_client.py
blob a5c814b519584b6d4346e3b0567bbc3da8ba0bf4

tests/test_cloudflare_provider_client.py
blob 4c455b35d3949e809848017d478507141f278e42

.github/workflows/cloudflare-provider-client-provider-free.yml
blob 88b0542acf9c2de2916484f3b435e8ed7ad8b191
```

The implementation is intentionally isolated from historical `provider_clients.py` bytes.

The client requires explicit constructor-supplied token/account/model/transport and performs no environment lookup, SDK invocation or bundled network I/O. The transport is injected so the complete contract can be tested with fakes.

Frozen request semantics:

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
tool_choice                   none
parallel_tool_calls           false
response format               ProviderDecisionPayload JSON Schema
automatic repair              disabled
retry/fallback/warm-up         none
```

The response parser fails closed on model drift, non-single-choice envelopes, non-stop completion, provider-native tool/function calls, refusals or invalid text. HTTP/transport failures are sanitized and not retried. Provider usage is retained only when reported as valid nonnegative integers; missing/invalid values remain unknown.

## 4. Provider-free validation result

The final client head passed all workflows triggered by the implementation, including:

- `cloudflare-provider-client-provider-free`;
- `production-runtime`;
- `final-handoff-acceptance-audit`;
- `final-delivery-provider-free-reproduction`;
- E9/E14 and benchmark-split regressions.

The first CI attempt found a test-only substring false positive (`environ` inside `environment`); the test was corrected to inspect AST references. Client behavior did not change for the fix.

This evidence proves provider-free contract conformance only. It does **not** prove credential validity, live Cloudflare API behavior, remaining free quota, live latency, model quality or production-provider selection.

## 5. Zero-cost envelope — unchanged

```text
GLM 16-attempt maximum         1002.188800 neurons
Nemotron 16-attempt maximum    6935.333888 neurons
complete packet maximum        7937.522688 neurons
Workers Free allocation       10000.000000 neurons
headroom                       2062.477312 neurons / 20.6248%
```

A future live authorization must prove without inference that execution uses Workers Free only, no prepaid AI Gateway/Workers Paid path is active, and at least **9,000 neurons remain** for the UTC day before attempt 1.

## 6. Next admissible provider step — audit before new code

The next provider task is **not automatically a new live executor**.

First audit existing ADR-010/ADR-011 execution/custody machinery against ADR-018/ADR-019. Determine, component by component:

```text
REUSE_UNCHANGED
REUSE_WITH_BOUNDED_ADAPTER
INCOMPATIBLE_HISTORICAL_ASSUMPTION
MISSING_MATERIAL_CAPABILITY
```

At minimum audit:

- deterministic 32-attempt order/denominators;
- M1–M10 aggregation and `NO_SELECTION` logic;
- ADR-007 provenance emission/validation;
- durable custody root;
- write-ahead attempt claims / uncertain-attempt handling;
- zero retry/fallback/warm-up semantics;
- route/model verification;
- exact usage capture and new Cloudflare-neuron M8 accounting;
- free-tier preflight requirements;
- provider/client injection assumptions;
- old OpenAI/Gemini-specific secrets/routes.

Only gaps demonstrated by that audit may authorize new live-execution implementation.

## 7. Still not authorized

```text
credential/account probe for evidence      NO
live Cloudflare request                    NO
comparison attempt 1                       NO
provider selection                         NO
production actions                         DISABLED
old #44 OpenAI/Gemini execution            FORBIDDEN AS-IS
C4 change                                  NONE
semantic/blind evaluation                  NOT AUTHORIZED
topology/runtime experiment                NOT AUTHORIZED
global architecture freeze                 NO
```

A connected Cloudflare credential, if later supplied, is an operational prerequisite only; it is not evidence and does not authorize a call.

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

- any real Cloudflare/provider inference before separate live authorization;
- credential/account probing merely to establish availability;
- Paid Workers, prepaid AI Gateway or paid spillover;
- modifying ADR-018/ADR-019 frozen bytes after live evidence begins;
- inventing a replacement executor before auditing ADR-010/011;
- executing the old ADR-008/#44 packet;
- Groq freshness reruns;
- silently adding candidate models;
- hidden retries/fallbacks/warm-ups/provider state;
- weakening `HarnessRunner`, authorization/idempotency or evaluator-private boundaries;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime implementation;
- final architecture or production-readiness claims before evidence supports them.
