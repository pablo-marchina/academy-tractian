# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-31 — ADR-010/011 reuse audit complete; bounded Cloudflare v2 execution adapter justified  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)  
**Historical evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)  
**Frozen preregistration:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Frozen provider-free client:** [`adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md`](adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md)  
**Execution/custody reuse audit:** [`ADR-010-011-REUSE-AUDIT-2026-08-31.md`](ADR-010-011-REUSE-AUDIT-2026-08-31.md)  
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
ADR-010/011 reuse audit                         COMPLETE / ISSUE #73

provider/model inference calls in current work  0
credential/account probes in current work       0
live network validation in current work         0
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

ADR-010 historical executor live path           DO NOT EXECUTE AS-IS
ADR-010 provider-neutral scientific logic       HIGH REUSE
ADR-011 historical live entrypoint              DO NOT EXECUTE AS-IS
ADR-011 custody/write-ahead invariants           HIGH REUSE
full new executor redesign                      NOT JUSTIFIED
bounded Cloudflare v2 execution adapter         JUSTIFIED / NOT YET IMPLEMENTED
minimum demonstrated implementation gaps        7

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
→ close only demonstrated gaps with prospective versioned code
→ provider-free validate/freeze execution adapter
→ separate live-execution authorization
→ inference / evaluation / selection or NO_SELECTION
```

For D01, the project has completed through **ADR-010/011 reuse audit**. Attempt 1 remains unauthorized.

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

The client requires explicit constructor-supplied token/account/model/transport and performs no environment lookup, SDK invocation or bundled network I/O. It fails closed on route/model/response drift, contains no retry/fallback/warm-up and retains usage only when actually reported.

## 4. ADR-010/011 reuse audit result

The audit inspected ADR-010/011 ADRs, frozen implementation blobs, tests, freeze artifacts, ADR-018 design v2 and ADR-019 client bytes.

Result:

```text
historical ADR-010 executor as-is             INCOMPATIBLE FOR CURRENT LIVE PATH
historical ADR-011 governed entrypoint as-is  INCOMPATIBLE FOR CURRENT LIVE PATH
provider-neutral execution/eval behavior      HIGH REUSE
custody/write-ahead/no-replay behavior         HIGH REUSE
```

### Reuse unchanged

- public population/P01-P08 rubrics;
- 32-attempt geometry and alternating-order semantics;
- canonical in-memory attempt budget behavior;
- controller-context conversion;
- public deterministic adjudication;
- scripted null baseline;
- forbidden-key inspection and B1 validation;
- ADR-007 route/model/provenance checks;
- sanitized attempt evidence fields;
- one-shot stdlib JSON transport;
- atomic/exclusive persistence primitives;
- fixed internal run directory;
- write-ahead `CLAIMED` semantics;
- uncertain-attempt stop and no replay/resume;
- sanitized error/result custody.

### Reuse with bounded adapter

- M1-M7/M10 aggregation;
- H1/H3/H4/H6/H7 hard-gate logic;
- Pareto/quality-margin/latency/`NO_SELECTION` skeleton;
- M9 operational portability concept;
- 32-entry ledger metadata schema;
- fixed provider-free M5 probe logic;
- authorization custody marker schema;
- claim → execute → complete loop.

### Historical assumptions that must not execute as-is

- v1 bundle loader pins design-v1/ADR-009/historical provider-client blobs;
- old plan SHA contains OpenAI/Gemini candidate identity;
- live executor requires exact ADR-009 OpenAI/Gemini classes;
- M8 is encoded as normalized USD cost;
- ADR-011 secrets/client factory are OpenAI/Google-specific;
- ADR-011 preparation pins the old bundle and old plan hash.

## 5. Seven minimum demonstrated implementation gaps

Only these new capabilities are justified:

1. current-scope ADR-018/019 frozen bundle + new v2 plan SHA;
2. result/summary v2 fields for exact usage, observed neurons, zero-cash status and Cloudflare M9/H8-H10;
3. Cloudflare M8 neuron calculation plus H8/H9/H10 and per-attempt/resource-projection stop rules;
4. provider-free fixed M5 probes for both exact ADR-019 model configurations;
5. exact Cloudflare live-client factory using explicit token + account ID and generic one-shot transport;
6. current authorization/custody marker v2 pinning ADR-018/019 plus v2 execution identities;
7. pre-live evidence gate requiring Workers Free, no Paid/prepaid Gateway path and >=9000 free neurons before attempt 1.

A full executor/custody redesign is not supported by evidence.

## 6. Next admissible provider step

Create **one separate provider-free implementation task** for a prospective, versioned Cloudflare executor/custody v2 adapter implementing only the seven gaps above.

Requirements:

- preserve ADR-010/011 frozen bytes;
- reuse unchanged behavior rather than reimplementing it unnecessarily;
- keep ADR-018 candidates/population/metrics/thresholds/budget unchanged;
- keep ADR-019 client bytes unchanged;
- use mocks/fakes/local transport only;
- prove the new M8/H8/H9/H10 resource logic deterministically;
- perform zero provider inference, zero credential/account probe and zero live network validation;
- freeze new implementation bytes only after provider-free regression passes.

This implementation task still **must not authorize attempt 1**.

## 7. Later live authorization gate

Only after the v2 adapter is provider-free validated/frozen may a separate task authorize live execution. Before attempt 1 it must freeze evidence that:

- exact ADR-018/ADR-019/v2 execution identities are present;
- execution uses Workers Free only;
- Workers Paid and prepaid AI Gateway are not active;
- at least 9,000 free neurons remain for the current UTC day;
- exact GLM/Nemotron IDs and direct route are unchanged;
- one canonical durable custody root exists;
- write-ahead claim/no-replay semantics are active;
- production actions remain disabled.

## 8. Still not authorized

```text
credential/account probe for evidence      NO
live Cloudflare request                    NO
comparison attempt 1                       NO
provider selection                         NO
production actions                         DISABLED
old ADR-008/009/010/011 live execution     FORBIDDEN AS-IS
C4 change                                  NONE
semantic/blind evaluation                  NOT AUTHORIZED
topology/runtime experiment                NOT AUTHORIZED
global architecture freeze                 NO
```

## 9. Agent topology/runtime ordering

The single-agent controller remains the strong qualified baseline. Multi-agent and runtime comparisons remain queued until the provider/model basis is controlled. Do not implement them yet.

## 10. C4 — unchanged parallel track

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
gate     REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

Only exact-byte recovery is authorized. Reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain unauthorized.

## 11. Still forbidden

- any real Cloudflare/provider inference before separate live authorization;
- credential/account probing merely to establish availability;
- Paid Workers, prepaid AI Gateway or paid spillover;
- modifying ADR-010/011/018/019 frozen historical bytes to fit the new path;
- redesigning executor/custody beyond the seven demonstrated gaps;
- executing the old ADR-008/#44 packet;
- Groq freshness reruns;
- silently adding candidate models;
- hidden retries/fallbacks/warm-ups/provider state;
- weakening `HarnessRunner`, authorization/idempotency or evaluator-private boundaries;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime implementation;
- final architecture or production-readiness claims before evidence supports them.
