# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-09-01 — Cloudflare executor/custody v2 provider-free implementation frozen by ADR-020  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)  
**Historical evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)  
**Frozen preregistration:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Frozen provider-free client:** [`adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md`](adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md)  
**Execution/custody reuse audit:** [`ADR-010-011-REUSE-AUDIT-2026-08-31.md`](ADR-010-011-REUSE-AUDIT-2026-08-31.md)  
**Frozen executor/custody v2:** [`adr/020-cloudflare-executor-custody-v2-provider-free-implementation-2026-09-01.md`](adr/020-cloudflare-executor-custody-v2-provider-free-implementation-2026-09-01.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts and ADRs remain authoritative for their exact scopes.

## Executive state

```text
Project North Star                              strongest defensible TRACTIAN/Inteli delivery under P1-P4
permanent external service/API cost             USD 0 HARD CONSTRAINT
evidence audit before new experiment            REQUIRED

historical material-decision audit              COMPLETE
current provider factual gates                  COMPLETE
minimum Cloudflare comparison preregistration   FROZEN / ADR-018
Cloudflare provider-free client                 FROZEN / ADR-019
ADR-010/011 reuse audit                         COMPLETE
Cloudflare executor/custody v2                  FROZEN PROVIDER-FREE / ADR-020

provider/model inference calls in ADR-020 work  0
credential/account probes in ADR-020 work       0
live network validation in ADR-020 work         0
comparison attempts consumed                    0 / 32
production provider/model selected              NO
provider/model inference                        NOT AUTHORIZED

core candidate 1                                @cf/zai-org/glm-4.7-flash
core candidate 2                                @cf/nvidia/nemotron-3-120b-a12b
public probe units                              8
repetitions / unit / candidate                  2
max future live attempts                        32
canonical Cloudflare v2 plan SHA                092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
max completion tokens / attempt                 512
max accounted prompt tokens / attempt           8000
max complete-packet neurons                     7937.522688
Workers Free daily allocation                   10000
minimum free neurons before future attempt 1    9000
Workers Paid / prepaid Gateway                  FORBIDDEN

Cloudflare direct client                        IMPLEMENTED / PROVIDER-FREE VALIDATED
Cloudflare comparison executor v2               IMPLEMENTED / PROVIDER-FREE VALIDATED
Cloudflare custody/write-ahead v2               IMPLEMENTED / PROVIDER-FREE VALIDATED
Cloudflare pre-live evidence contract           IMPLEMENTED / REAL ACCOUNT EVIDENCE NOT YET SUPPLIED
Cloudflare exact @cf provenance adapter          IMPLEMENTED / PROVIDER-FREE VALIDATED

client environment credential lookup            NONE
credential/account probing                      NONE
retry/fallback/warm-up                          NONE
parallel live calls                             NONE
provider-native tool execution                  REJECTED
AI Gateway                                      DISABLED
model allowlist                                 EXACT ADR-018 TWO MODELS
usage fabrication                               FORBIDDEN
claimed/uncertain automatic replay              FORBIDDEN

ADR-010 historical executor live path           DO NOT EXECUTE AS-IS
ADR-010 provider-neutral scientific logic       REUSED
ADR-011 historical live entrypoint              DO NOT EXECUTE AS-IS
ADR-011 custody/write-ahead invariants           REUSED
full executor redesign                          NOT USED / NOT JUSTIFIED

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

## 1. Evidence-first provider sequence

Permanent sequence:

```text
decision question
→ historical evidence audit
→ update only mutable external facts
→ demonstrate exact material gap
→ preregister minimum comparison
→ freeze preregistration
→ implement provider-free client
→ freeze client
→ audit historical executor/custody reuse
→ implement only demonstrated execution gaps provider-free
→ freeze execution/custody capability
→ design/freeze separate live authorization
→ only then permit attempt 1
→ execute/evaluate/select candidate or honest NO_SELECTION
```

For D01, the project has completed through **provider-free execution/custody capability freeze**. Attempt 1 remains unauthorized.

## 2. ADR-018 comparison contract — unchanged

Two production-selection candidates only:

1. `cloudflare_glm_4_7_flash_workers_free` → `@cf/zai-org/glm-4.7-flash`;
2. `cloudflare_nemotron_3_120b_a12b_workers_free` → `@cf/nvidia/nemotron-3-120b-a12b`.

Population remains unchanged:

```text
research/experiments/provider-model-comparison-dev-population-v1.json
SHA-256 561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251
8 units × 2 repeats × 2 candidates = 32 maximum attempts
```

No candidate, population, metric, threshold, request contract or resource budget changed in ADR-020.

## 3. ADR-019 client — unchanged and still frozen

```text
src/academy_tractian/cloudflare_provider_client.py
blob a5c814b519584b6d4346e3b0567bbc3da8ba0bf4
```

ADR-020 does not modify that client. It constructs it with explicit token/account/model/transport and exact allowlisted model IDs.

## 4. ADR-020 exact implementation freeze

```text
cloudflare_provider_comparison_v2.py     e12b1dfa03eb1c50bc97848821235ef422516092
cloudflare_provider_live_v2.py           70d8e0ccc4d4eb003d78cdd152b1dffd30b43f29
cloudflare_provider_provenance_v2.py     e7f8bdc60910ef0acf7b14c71616448338eeefc2
test_cloudflare_provider_comparison_v2   b9d02070ed0d17a66a5e9aed69bf3ff6cd4d2b39
test_cloudflare_provider_provenance_v2   f9e752523d50876f88a6de100afb33948c602157
provider-free workflow                   752f9c8906b124578164ee21885a90387842ff19
validation result                        d7a9d04028408d2492e0d11e20c90430709f0a3a
```

Canonical v2 plan:

```text
092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
```

This plan is intentionally distinct from the historical ADR-010 OpenAI/Gemini plan because exact candidate/model/route identities changed while geometry remained identical.

## 5. Seven audited execution gaps — status

```text
1 current ADR-018/019 bundle + v2 plan                    CLOSED
2 result/summary v2 resource fields                       CLOSED
3 M8 neurons + H8/H9/H10 + resource stop guards          CLOSED PROVIDER-FREE
4 fixed M5 probes for both Cloudflare configs             CLOSED PROVIDER-FREE
5 exact Cloudflare client factory                         CLOSED PROVIDER-FREE
6 current authorization/custody marker + ledger v2        CLOSED PROVIDER-FREE
7 Workers Free/no-paid/>=9000 pre-live evidence contract  IMPLEMENTED PROVIDER-FREE
```

Gap 7 is an **interface/capability freeze**, not proof of current account state. Real evidence has not yet been supplied or probed.

## 6. Resource and fail-closed behavior

Frozen accounting:

```text
GLM input       5,500 neurons / 1M input tokens
GLM output     36,400 neurons / 1M output tokens
Nemotron input 45,455 neurons / 1M input tokens
Nemotron output 136,364 neurons / 1M output tokens
prompt max       8,000 tokens / attempt
completion max     512 tokens / attempt
packet max      7,937.522688 neurons
```

The v2 executor stops fail-closed when:

- exact prompt/output usage is missing;
- observed prompt exceeds 8,000;
- observed completion exceeds 512;
- packet observed neurons exceed the frozen ceiling;
- current observed neurons + frozen worst-case remaining attempts can exceed available free-neuron evidence;
- provenance/model/route/raw-material hard gates fail.

Incomplete/resource-uncertain packets cannot select a provider.

## 7. Custody / no-replay behavior

The ADR-011 security model is preserved prospectively:

```text
one durable custody root
exclusive authorization marker
fixed root/run directory
32 canonical ledger entries
CLAIMED persisted before network-capable invocation
claimed crash/exception -> uncertain
no automatic resume
no retry/replay of uncertain attempt
second run in same root refused
sanitized immutable result
credentials persisted false
raw provider material persisted false
```

Current marker name:

`cloudflare-adr018-live-comparison-custody-v2.json`

## 8. Exact Cloudflare provenance compatibility

Provider-free CI exposed that historical ADR-007 Pydantic regexes reject model IDs beginning with `@`, while both official Workers AI IDs begin `@cf/`.

The project did **not**:

- strip or rewrite `@`;
- weaken M10;
- modify frozen historical `decision_source.py` bytes.

Instead, ADR-020 freezes a Cloudflare-only provenance extension that accepts only the exact two ADR-018 model IDs while preserving:

- `provider-model-call-v1` event shape;
- `provider-decision-adapter-v1`;
- ADR-007 call-id derivation;
- exact provider/model/route/request hashes;
- one client invocation;
- zero retry/fallback;
- raw request/response/exception flags false.

## 9. Provider-free validation

Initial dedicated CI: `23 passed / 6 failed`; all failures were the historical `@cf/...` regex incompatibility. No provider call occurred.

Corrected dedicated run `33507169465` on head `9c25143c1b37c7728d4c3130263607e6e6b0f1ed`:

```text
Cloudflare v2/client/provenance tests       32 passed
historical ADR-010/011 regressions          29 passed
provider credentials in workflow           absent
provider calls                              0
```

All 14 workflows on that implementation head completed successfully, including `production-runtime`, `final-handoff-acceptance-audit` and `final-delivery-provider-free-reproduction`.

## 10. Next admissible provider step

The next provider task is **not inference**. It is a separate **live-execution authorization design/freeze**, still with zero inference.

That authorization must define and freeze:

- exact ADR-018/019/020 identities;
- how genuine non-inference evidence of `Workers Free` is obtained;
- how `Workers Paid = false` and prepaid AI Gateway = false are established;
- how >=9,000 free neurons for the current UTC day are established without consuming inference;
- explicit secret provisioning without persistence;
- one canonical durable custody root;
- exact one-shot invocation command/entrypoint;
- operator stop conditions and artifact custody;
- explicit statement that attempt 1 is authorized only after all above gates pass.

Until that later authorization freezes, connected credentials are operational prerequisites only and have no authorization effect.

## 11. Still not authorized

```text
real Cloudflare HTTP request                 NO
credential/account probe merely for evidence NO
comparison attempt 1                         NO
provider/model selection                     NO
production actions                           DISABLED
old ADR-008/009/010/011 live packet          FORBIDDEN AS-IS
C4 change                                    NONE
semantic/FRESH_BLIND/LEGACY_LOCKED_TEST      NOT AUTHORIZED
topology/runtime experiment                  NOT AUTHORIZED
global architecture freeze                   NO
```

## 12. Agent topology/runtime ordering

The single-agent controller remains the strong qualified baseline. Multi-agent and runtime comparisons remain queued until provider/model evidence selects a basis or freezes an honest `NO_SELECTION`.

## 13. C4 — unchanged parallel track

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
gate     REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

Only exact-byte recovery is authorized. Reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain unauthorized.

## 14. Still forbidden

- real provider inference before separate live authorization;
- using connected credentials as evidence or authorization;
- Paid Workers, prepaid AI Gateway or paid spillover;
- modifying ADR-010/011/018/019 historical frozen bytes;
- changing ADR-020 implementation post hoc after live evidence begins;
- changing ADR-018 candidates/population/metrics/thresholds/budget without a prospective amendment;
- hidden retries/fallbacks/warm-ups/provider state;
- weakening `HarnessRunner`, authorization/idempotency or evaluator-private boundaries;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime implementation;
- final architecture or production-readiness claims before evidence supports them.
