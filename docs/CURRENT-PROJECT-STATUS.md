# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-09-01 — ADR-023 governed Cloudflare entrypoint merged/provider-free validated; standalone production wheel reproduction proved; D01 reset-window evidence pending  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Immediate plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)

This is the sole canonical human-readable current authorization state. Historical frozen ADRs/artifacts remain authoritative for their exact scopes.

## Executive state

```text
external API / hosted-service project cost      USD 0 HARD CONSTRAINT
evidence audit before new experiment             REQUIRED

historical evidence audit                        COMPLETE
provider factual refresh                         COMPLETE
Cloudflare comparison preregistration             FROZEN / ADR-018
Cloudflare provider client                        FROZEN / ADR-019
Cloudflare executor/custody v2                    FROZEN / ADR-020
Cloudflare original authorization protocol        FROZEN / ADR-021
reset-window Neuron evidence amendment            FROZEN / ADR-022
governed entrypoint audit/contract                ACCEPTED / ADR-023
minimal governed live launcher                    MERGED / PROVIDER-FREE VALIDATED
standalone production wheel reproduction          PROVED / PR #91

implementation baseline after PR #91              a93854dd5e70edf8084bdaae1762dd64cdb6aa48
standalone-wheel-smoke                            PASSED
existing production-runtime regression            PASSED

Workers Free / Active account state               PROVED MANUALLY
explicit current Neuron meter in target UI        NOT AVAILABLE
ADR-021 explicit-balance path                     PRESERVED BUT NOT OPERABLE ON TARGET UI
ADR-022 reset-window fallback                     PROVIDER-FREE VALIDATED
ADR-023 receipt→ADR-020 composition               PROVIDER-FREE VALIDATED
issue #44 OpenAI/Gemini path                      CLOSED / HISTORICAL / SUPERSEDED
issue #79 real evidence/receipt                    READY PENDING VALID RESET WINDOW
issue #89 standalone wheel gap                    CLOSED / PROVED
issue #92 architecture materiality/Pareto         PLANNING ONLY / STARTS AFTER D01
issue #9 C4 exact artifact                        EXTERNALLY BLOCKED / EXACT BYTES ONLY

provider/model inference calls                    0
credential/account probes                         0
live network validation                           0
comparison attempts consumed                      0 / 32
real reset-window evidence captured               NO
real authorization receipt issued                 NO
Cloudflare credentials provisioned                NO
attempt 1 authorized                              NO
production provider/model selected                NO
```

Frozen candidates/packet:

```text
@cf/zai-org/glm-4.7-flash
@cf/nvidia/nemotron-3-120b-a12b
8 public probes × 2 repeats × 2 candidates = max 32 calls
plan SHA 092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
packet max 7937.522688 neurons
Workers Free documented allocation 10000 neurons/day
historical start gate >=9000 neurons remaining
reset-window derived start state 10000 neurons
```

## 1. Current D01 sequence

Completed/provider-free validated:

```text
historical evidence audit                    DONE
current USD-0 factual refresh                DONE
minimum provider gap demonstrated            DONE
comparison preregistration                   FROZEN / ADR-018
Cloudflare direct client                     FROZEN / ADR-019
ADR-010/011 reuse audit                      DONE
executor/custody v2                          FROZEN / ADR-020
original live authorization protocol         FROZEN / ADR-021
Neuron evidence-source revalidation          RESOLVED / ADR-022
entrypoint sufficiency audit/contract         ACCEPTED / ADR-023
minimal gate-specific launcher               MERGED
provider-free receipt→governed-task test      PASSED
standalone distribution smoke                PASSED / PR #91
```

Next operational gate:

```text
2026-09-01 21:00–21:10 America/Sao_Paulo
=
2026-09-02 00:00–00:10 UTC
↓
within first 10 minutes:
  prove Workers Free / Active
  attest no Workers AI calls since reset
  attest no automated/background Workers AI consumer since reset
  attest exclusive Workers AI account use until packet completion
↓
create sanitized reset-window evidence
↓
issue short-lived provider-free receipt bound to exact custody root
↓
only then provision Cloudflare token/account ID
↓
revalidate receipt/evidence/custody with ADR-022 adapter
↓
explicitly invoke scripts/research/execute_cloudflare_live_comparison_v2.py
↓
ADR-020 GovernedCloudflareLiveTaskV2
↓
attempt 1
```

Attempt 1 remains unauthorized until a real evidence packet and receipt exist and the operator explicitly invokes the ADR-023 launcher while every attestation remains true.

## 2. Work authorized before D01

The provider path requires no additional implementation before the reset.

Provider-independent work is authorized only as an acceptance/reliability audit or the smallest fix to a demonstrated P0/P1 gap.

Current order:

```text
1. canonical plan/status reconciliation          ACTIVE
2. delivery-acceptance row audit                 NEXT
3. final demo-path completeness audit            NEXT
4. security / trace / failure-containment audit  NEXT
5. D01 reset-window execution                    AT 21:00 BRT IF AUTHORIZED
```

Every acceptance finding must be classified:

```text
PROVED / PARTIAL / BLOCKED / MISSING
```

A pre-D01 fix must be provider-independent, preserve ADR-018→023, consume no provider call/probe and not pre-empt issue #92 topology/runtime decisions.

## 3. Standalone production distribution closure

Before PR #91, the root production package imported `research.e2.*` while the root wheel target packaged only `src/academy_tractian`. Existing CI installed both projects editably, so checkout-mode success did not prove an autonomous production distribution.

PR #91 closed that gap without modifying source semantics:

```text
root wheel includes accepted research.e2 package at existing import path
↓
clean virtual environment
↓
install only root wheel
↓
working directory outside repository checkout
↓
import academy_tractian
+ import research.e2.controller
+ validate canonical 18-operation registry
+ validate read-only production default
```

Result:

```text
STANDALONE_WHEEL_REPRODUCIBILITY_PROVED
```

This is now a regression obligation, not a reason to redesign the runtime.

## 4. What ADR-022 changes

ADR-021 remains byte-identical and its explicit-balance path remains valid if a dashboard balance becomes available.

ADR-022 adds only:

```text
RESET_WINDOW_ATTESTATION
```

A 10,000-Neuron starting allocation may be derived only if:

```text
Cloudflare primary docs still state 10000 Neurons/day
Cloudflare primary docs still state reset at 00:00 UTC
observation occurs <=00:10:00 UTC
Workers Free / Active is proved
Workers Paid is false
no Workers AI calls since reset
no automated/background Workers AI consumers since reset
exclusive account usage through packet completion
direct Workers AI route only
AI Gateway/prepaid unified billing absent
comparison attempts = 0
inference/probes used to obtain evidence = 0
```

Any uncertainty fails closed.

## 5. What ADR-023 changes

ADR-023 closes only the operational entrypoint gap. It does not change executor, custody, client, authorization, comparison, scoring or resource policy.

The canonical live composition is now:

```text
CloudflareResetWindowEvidenceV1 + CloudflareResetWindowReceiptV1 + custody root
↓
reset_window_authorization_to_adr020_pre_live_evidence(...)
↓
CloudflareLiveSecrets from environment only
↓
build_cloudflare_one_shot_transport_v2()
↓
GovernedCloudflareLiveTaskV2.prepare(..., fixture_result=False)
↓
execute_all()
```

The only operator-facing live command is:

```text
python scripts/research/execute_cloudflare_live_comparison_v2.py --evidence <evidence.json> --receipt <receipt.json> --custody-root <canonical-root>
```

No ad-hoc execution wrapper, retry, fallback, alternate custody, alternate model/provider or `[project.scripts]` surface is authorized.

## 6. Evidence freshness and custody

```text
reset observation window       00:00:00–00:10:00 UTC
evidence maximum age           600 seconds
receipt maximum lifetime       300 seconds
same UTC day                    required
source artifact                 Workers Free proof retained outside repo
serialized source evidence      SHA-256 only
account ID / token              never serialized
```

The receipt remains bound to the exact evidence hash, custody-root hash, ADR-018/019/020/021 pins, plan SHA, direct route and exact model IDs.

## 7. Resource/safety behavior unchanged

ADR-020 still owns:

- exact usage/Neuron accounting;
- H8/H9/H10;
- 8000 input / 512 output ceilings;
- stop-before-next-attempt projection;
- missing usage fail-closed;
- write-ahead `CLAIMED` ledger;
- uncertain/no-replay semantics.

ADR-022 does not weaken the 9000-Neuron start requirement: an admissible reset-window derives 10000, which is strictly stronger.

ADR-023 duplicates none of these mechanisms; it only composes the frozen authorization adapter into the frozen governed task.

## 8. Explicitly rejected paths

Still forbidden:

- infer `used=0` because no dashboard meter is visible;
- DevTools/private dashboard endpoints as canonical quota evidence;
- Alpha/Restricted billable usage API as canonical balance source;
- sacrificial inference;
- credential/account probe merely to discover quota;
- Workers Paid / prepaid AI Gateway / paid spillover;
- operator attestation with uncertainty about background/other-account usage;
- bypassing the governed launcher with ad-hoc Python;
- modifying executor/custody/client/authorization semantics for launcher convenience.

If exclusive account custody cannot be truthfully attested, the correct result is `LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED`.

## 9. Allowed provider outcomes

```text
A  reset-window evidence + receipt → governed launcher → live packet → GLM / Nemotron / NO_SELECTION
B  reset-window custody cannot be satisfied before deadline → LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
C  live packet executes but no candidate qualifies → NO_SELECTION
```

Forced provider selection remains forbidden.

## 10. Other architecture decisions

```text
single-agent controller      STRONG QUALIFIED BASELINE
standalone packaging         EVIDENCE SUFFICIENT / REGRESSION OBLIGATION
multi-agent comparison       CONDITIONAL AFTER PROVIDER D01
runtime comparison           CONDITIONAL AFTER TOPOLOGY/MATERIALITY AUDIT
native tools vs MCP          EVIDENCE SUFFICIENT CURRENT SCOPE
stopping/evidence policy     EVIDENCE SUFFICIENT CURRENT SCOPE
RAG/vector/reranking         NO MATERIAL CURRENT GAP / NO EXPERIMENT
persistent memory            NO MATERIAL CURRENT GAP / NO EXPERIMENT
adaptive routing             UNASSESSED / NOT CURRENTLY MATERIAL
rich UI/deployment work      P2 UNLESS ACCEPTANCE GAP APPEARS
issue #92                    PLANNING-ONLY HARD-GATE + PARETO PROTOCOL
```

The architecture baseline is not frozen as globally optimal. It is the current strongest qualified baseline. After D01 resolves/bounds, #92 determines whether any remaining alternative is material enough to compare.

## 11. Post-D01 architecture protocol

Issue #92 activates only after:

```text
provider D01 result
OR
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED frozen
```

Candidate architecture changes must first pass hard gates for:

```text
P0 coverage
deterministic safety
evaluator-private/gold isolation
trace integrity
clean reproduction
USD 0 feasibility
bounded state/retry/fallback behavior
safe failure containment
```

Only hard-gate-passing candidates may enter a Pareto comparison. No arbitrary weighted architecture score is authorized.

Topology is assessed first. Runtime/orchestration is one gate later. RAG/vector/reranking, memory, MCP migration, adaptive routing and rich observability remain conditional on a measured gap.

## 12. C4 parallel track

```text
required SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes             177350
rows              144
geometry          36 common parents × 4 arms
```

Only exact-byte recovery is authorized. Reconstruction/rescoring/substitution remains forbidden.

A fresh 2026-09-01 recovery check found no candidate in connected ChatGPT Library/conversation storage or Google Drive by exact SHA or deterministic-scoring identifiers. Issue #9 remains the explicit external scientific blocker.

## 13. Deadline state

```text
09-01 before 21:00  plan reconciliation + provider-free acceptance/demo/security audits
09-01 21:00–21:10 D01 reset-window evidence/receipt/live gate if truthful custody exists
09-02 → 09-03       live provider result OR external-blocker freeze; activate #92
09-03 → 09-05       close only still-material architecture decisions + full reliability/regression
09-05 → 09-07       architecture freeze + acceptance/demo/runbook/reproduction
09-08               delivery
```

After 2026-09-05, default against speculative P2 experiments.

## 14. Still forbidden

- provider inference before a real valid receipt and explicit governed launcher invocation;
- credential/account probes merely to obtain quota evidence;
- fabricated quota values;
- concurrent/unaccounted Workers AI use during reset-window custody;
- Paid Workers / AI Gateway prepaid or paid spillover;
- changing ADR-018 packet post hoc;
- retry/replay of claimed/uncertain attempts;
- C4 reconstruction/rescoring/substitution;
- unnecessary RAG/memory/multi-agent/runtime/UI complexity;
- topology/runtime work before D01 is resolved or explicitly bounded;
- treating pre-D01 audits as authorization to pre-select post-D01 architecture;
- final provider/architecture/production-readiness claims beyond evidence.
