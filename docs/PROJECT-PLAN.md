# Academy × TRACTIAN — Governed Project Plan to Final Delivery

**Status:** ACTIVE / canonical macro plan  
**Planning checkpoint:** 2026-09-01 — ADR-022 reset-window evidence amendment  
**Final delivery target:** 2026-09-08  
**Current status:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate next steps:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

## 1. Objective

Deliver the strongest defensible TRACTIAN × Inteli project by 2026-09-08, maximizing:

```text
required-scope coverage
× scientific credibility
× production quality
× academic evidence quality
```

subject to:

```text
external API / hosted-service project charge    USD 0
paid spillover                                  FORBIDDEN
```

The project does not optimize experiment count or architecture breadth. It closes only material evidence gaps that can still change the final delivery.

## 2. Non-negotiable governance

All work follows:

```text
decision question
→ repository evidence audit
→ evidence-sufficiency classification
→ exact material gap
→ current primary-source refresh where mutable
→ smallest credible comparison/amendment
→ preregistration when needed
→ implementation/execution
→ validation
→ immutable evidence/provenance
→ freeze
→ status/next-step reconciliation
```

A new experiment is prohibited when existing evidence already answers the decision for the current scope.

Priority:

```text
P0 required behavior + trustworthy evaluation
↓
P1 production/security/reliability closure
↓
P2 optional complexity only if evidence says it can matter and deadline allows
```

## 3. Current provider path

Completed:

```text
historical material-decision audit               COMPLETE
current zero-cost provider refresh               COMPLETE
minimum provider gap demonstrated                COMPLETE
Cloudflare comparison preregistration            FROZEN / ADR-018
Cloudflare direct client                         FROZEN / ADR-019
ADR-010/011 executor/custody reuse audit         COMPLETE
Cloudflare executor/custody v2                   FROZEN / ADR-020
original live authorization protocol             FROZEN / ADR-021
Neuron evidence-source revalidation              RESOLVED / ADR-022
```

Frozen candidates:

```text
@cf/zai-org/glm-4.7-flash
@cf/nvidia/nemotron-3-120b-a12b
```

Frozen scientific packet:

```text
8 public probes × 2 repeats × 2 candidates
max attempts      32
input ceiling     8000 accounted tokens / attempt
output ceiling    512 tokens / attempt
packet maximum    7937.522688 Neurons
selection         Pareto / NO_SELECTION permitted
```

Current consumed state:

```text
provider inference        0
credential/account probes 0
live validation           0
attempts consumed         0 / 32
provider selected         NO
```

## 4. ADR-022 resolves issue #80 prospectively

ADR-021's explicit Neuron-balance path remains historically frozen and valid when such a meter exists. The target account UI does not expose it.

ADR-022 adds a conservative fallback:

```text
RESET_WINDOW_ATTESTATION
```

A 10,000-Neuron starting state is derived only when:

```text
Workers Free / Active proved
Workers Paid false
Cloudflare docs still state 10000 Neurons/day
Cloudflare docs still state reset 00:00 UTC
observation <=00:10:00 UTC
no Workers AI calls since reset
no automated/background Workers AI consumer since reset
exclusive account use through packet completion
direct Workers AI route only
no AI Gateway / prepaid unified billing
0 / 32 attempts consumed
0 inference/probes used to obtain evidence
```

Any uncertainty fails closed.

## 5. Immediate critical path

The critical path is no longer protocol design. It is a real operational reset window.

```text
ADR-022 final PR regression/freeze
↓
wait for admissible 00:00 UTC reset
↓
within first 10 minutes capture Workers Free evidence
+ no-use/exclusive-use attestations
↓
create reset-window evidence JSON
↓
issue <=5-minute provider-free receipt
↓
only then provision Cloudflare token/account ID
↓
explicit live authorization
↓
execute frozen packet
```

If the account cannot be placed under truthful exclusive Workers AI custody, do not weaken the protocol. Freeze an external blocker.

## 6. Allowed provider outcomes

All are legitimate:

### A. Live packet executes and one candidate is supported

```text
GLM 4.7 Flash
OR
Nemotron 3 120B A12B
```

### B. Live packet executes and neither candidate qualifies

```text
NO_SELECTION
```

### C. Reset-window/exclusive-account evidence cannot be satisfied before deadline

```text
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

Forced provider selection is forbidden.

## 7. Decision state by architecture area

| Area | Evidence state | Plan consequence |
|---|---|---|
| Provider/model | `PARTIALLY_ASSESSED`; live comparison pending | current operational gate |
| Native typed tools vs MCP | `EVIDENCE_SUFFICIENT` | preserve native ToolSpec; no new experiment |
| Evidence-sufficiency stopping | `EVIDENCE_SUFFICIENT` | preserve |
| Safety/authorization/idempotency | strong deterministic boundary | preserve/strengthen only |
| RunTrace/operational evaluator | sufficient current scope | preserve/regress |
| RAG/vector/reranking | no demonstrated material gap | do not add |
| Persistent memory | no demonstrated material need | do not add |
| Agent topology | strong single-agent qualified baseline; comparative optimality conditional | audit after provider D01 |
| Runtime/orchestration | historical evidence strong but asymmetric | assess only if still material |
| Adaptive model routing | unassessed but not currently material | defer |
| Rich observability/UI/deployment | P2 unless acceptance gap appears | defer |
| C4 | exact artifact externally blocked | exact-byte recovery only |

## 8. Post-provider evidence audit

After the provider result or external-blocker freeze:

```text
provider D01 resolved/bounded
→ re-audit topology evidence
→ can topology still materially change P0/P1/final architecture?
   ├─ NO → preserve single-agent qualified baseline
   └─ YES → preregister minimum controlled topology comparison
```

Runtime/orchestration is assessed only after topology/materiality is closed.

Do not automatically launch multi-agent or framework experiments because they were once on a roadmap.

## 9. C4 parallel track

Exact required artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Only exact-byte recovery is currently authorized. No reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND or LEGACY_LOCKED_TEST.

C4 does not block preserving the already validated provider-free handoff; it limits the exact claims that can be made.

## 10. Phase map

| Phase | State | Exit condition |
|---|---|---|
| Governance/benchmark foundation | COMPLETE | immutable governance and benchmark semantics |
| Historical candidate/failure learning | COMPLETE | evidence preserved |
| Provider packet foundations | COMPLETE | ADR-018→022 provider-free freezes |
| Operational provider selection | ACTIVE | live result, `NO_SELECTION`, or external-blocker freeze |
| Remaining architecture decisions | CONDITIONAL | only still-material gaps closed/bounded |
| Final architecture integration | PENDING | supported choices integrated/regressed |
| Final demonstration/delivery | PENDING | acceptance evidence + reproducible real path |

## 11. Deadline protection

### 2026-09-01 → 2026-09-02

- freeze ADR-022;
- use the next admissible reset window only if exclusive account custody can be truthfully established;
- otherwise prepare the external-blocker outcome rather than weakening evidence.

### 2026-09-02 → 2026-09-03

- finish live packet and provider decision if authorized; or
- freeze `LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED`.

### 2026-09-03 → 2026-09-05

- re-audit topology/runtime materiality;
- run only minimum experiments still capable of changing final P0/P1 decisions;
- full reliability/regression/integration pass;
- fix evidence-backed failures only.

### 2026-09-05 → 2026-09-07

- final architecture freeze;
- delivery-acceptance reconciliation;
- clean-environment reproduction;
- final demo/runbook/fallback/limitations;
- concise rubric-to-evidence index.

### 2026-09-08

Deliver only evidence-backed claims.

After 2026-09-05, default against speculative P2 work.

## 12. Stop/pivot rules

- preserve failed/consumed experiments;
- never fabricate quota or operational evidence;
- do not use Paid Workers or paid AI Gateway spillover;
- no provider inference before valid authorization;
- no hidden retries/fallbacks/warm-ups/provider state;
- no replay of claimed/uncertain attempts;
- do not change the ADR-018 packet after live results begin;
- do not add RAG/memory/multi-agent/runtime/UI complexity absent a measured material gap;
- do not promote an implemented component to final merely because it exists;
- if an external condition blocks stronger evidence, freeze the blocker and continue the strongest defensible delivery.

## 13. Repository-wide definition of done

```text
all requested P0 capabilities demonstrably covered
+
trustworthy integrated evaluation
+
scientific evidence proportional to all claims
+
material final decisions resolved or explicitly bounded
+
USD 0 feasibility
+
P1 production/security/reliability risks closed or bounded
+
reproducible real-path demonstration
+
limitations/non-claims explicit
```
