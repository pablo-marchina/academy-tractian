# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-09-01 — ADR-023 governed Cloudflare entrypoint merged and provider-free validated; real reset-window evidence pending  
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

canonical merge containing ADR-023 launcher       5b4b0a2f4bbf51215c901af534216805d26386b0
main push production-runtime validation           PASSED

Workers Free / Active account state               PROVED MANUALLY
explicit current Neuron meter in target UI        NOT AVAILABLE
ADR-021 explicit-balance path                     PRESERVED BUT NOT OPERABLE ON TARGET UI
ADR-022 reset-window fallback                     PROVIDER-FREE VALIDATED
ADR-023 receipt→ADR-020 composition               PROVIDER-FREE VALIDATED
issue #44 OpenAI/Gemini path                      CLOSED / HISTORICAL / SUPERSEDED
issue #79 real evidence/receipt                    READY PENDING VALID RESET WINDOW
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
```

Next operational gate:

```text
wait for a real 00:00 UTC reset window
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

## 2. What ADR-022 changes

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

## 3. What ADR-023 changes

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

## 4. Evidence freshness and custody

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

## 5. Resource/safety behavior unchanged

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

## 6. Explicitly rejected paths

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

## 7. Allowed provider outcomes

```text
A  reset-window evidence + receipt → governed launcher → live packet → GLM / Nemotron / NO_SELECTION
B  reset-window custody cannot be satisfied before deadline → LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
C  live packet executes but no candidate qualifies → NO_SELECTION
```

Forced provider selection remains forbidden.

## 8. Other architecture decisions

```text
single-agent controller      STRONG QUALIFIED BASELINE
multi-agent comparison       CONDITIONAL AFTER PROVIDER D01
runtime comparison           CONDITIONAL AFTER TOPOLOGY/MATERIALITY AUDIT
native tools vs MCP          EVIDENCE SUFFICIENT CURRENT SCOPE
stopping/evidence policy     EVIDENCE SUFFICIENT CURRENT SCOPE
RAG/vector/reranking         NO MATERIAL CURRENT GAP / NO EXPERIMENT
persistent memory            NO MATERIAL CURRENT GAP / NO EXPERIMENT
adaptive routing             UNASSESSED / NOT CURRENTLY MATERIAL
rich UI/deployment work      P2 UNLESS ACCEPTANCE GAP APPEARS
```

## 9. C4 parallel track

```text
required SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes             177350
rows              144
geometry          36 common parents × 4 arms
```

Only exact-byte recovery is authorized. Reconstruction/rescoring/substitution remains forbidden.

A fresh 2026-09-01 recovery check found no candidate in connected ChatGPT Library/conversation storage or Google Drive by exact SHA or deterministic-scoring identifiers. Issue #9 remains the explicit external scientific blocker.

## 10. Deadline state

```text
09-01 → 09-02  ADR-023/launcher merged; use next admissible reset window if account custody is possible
09-02 → 09-03  live provider result OR external-blocker freeze
09-03 → 09-05  close only still-material architecture decisions + full reliability/regression
09-05 → 09-07  architecture freeze + acceptance/demo/runbook/reproduction
09-08          delivery
```

After 2026-09-05, default against speculative P2 experiments.

## 11. Still forbidden

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
- final provider/architecture/production-readiness claims beyond evidence.
