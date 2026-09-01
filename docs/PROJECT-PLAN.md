# Academy × TRACTIAN — Governed Project Plan to Final Delivery

**Status:** ACTIVE / canonical macro plan  
**Planning checkpoint:** 2026-09-01  
**Final delivery target:** 2026-09-08  
**Current status:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate next steps:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Decision revalidation:** [`DECISION-REVALIDATION-MASTER-PLAN.md`](DECISION-REVALIDATION-MASTER-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

## 1. Purpose

This document is the canonical macro plan for delivering the strongest defensible TRACTIAN × Inteli project by 2026-09-08.

The optimization target is:

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

The goal is not to maximize architecture breadth or experiment count. The goal is to close the smallest set of material evidence gaps that can still change the final delivery.

## 2. Non-negotiable rules

All work continues under P1–P4:

- **P1 — systematic comparison:** no material final choice without credible alternatives or a documented evidence-based reason that alternatives are not material;
- **P2 — production-first:** production/security/reliability risks are part of selection;
- **P3 — quantitative/adaptive by default:** measurable choices use evidence, uncertainty and simple baselines;
- **P4 — eval-driven engineering:** requirements/evaluators/regressions drive implementation;
- **USD 0:** no production/provider/service choice may require a project charge or uncontrolled paid spillover.

### 2.1 Evidence audit before experiments

Before any new experiment:

```text
decision question
→ repository-wide historical evidence audit
→ evidence sufficiency classification
→ exact material gap
→ only if gap remains: preregister minimum experiment
→ implementation/execution
```

A new experiment is prohibited when existing repository evidence already answers the decision for the current scope.

### 2.2 Documentation before development

For every material future workstream:

```text
plan/status update
→ requirement/risk mapping
→ hard constraints
→ evidence audit/current fact refresh
→ alternatives/simple baseline
→ preregistration when experiment is still necessary
→ implementation
→ validation
→ freeze/status update
```

### 2.3 Acceptance-first priority

Work must map to at least one of:

1. P0/P1 acceptance requirement;
2. official evaluation criterion;
3. material production/security/reliability risk;
4. experiment needed to choose among credible alternatives above.

Otherwise defer it.

Priority:

```text
P0 required behavior + trustworthy evaluation
↓
P1 production/partner-quality closure
↓
P2 optional complexity only when measured benefit is plausible and deadline-safe
```

## 3. Current project state — 2026-09-01

The earlier global-revalidation program is no longer a future discovery phase. Most provider groundwork is complete.

```text
historical material-decision audit                 COMPLETE
current USD-0 provider factual refresh              COMPLETE
minimum Cloudflare provider comparison              FROZEN / ADR-018
Cloudflare direct provider client                   FROZEN / ADR-019
ADR-010/011 executor/custody reuse audit            COMPLETE
Cloudflare executor/custody v2                      FROZEN / ADR-020
Cloudflare live authorization protocol              FROZEN / ADR-021

provider/model inference calls                      0
credential/account probes                           0
live network validation                             0
comparison attempts consumed                        0 / 32
production provider/model selected                  NO
```

Frozen comparison candidates:

```text
@cf/zai-org/glm-4.7-flash
@cf/nvidia/nemotron-3-120b-a12b
```

Frozen packet:

```text
8 public probes × 2 repeats × 2 candidates = max 32 calls
plan SHA-256 092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
packet worst-case 7937.522688 neurons
Workers Free daily allocation 10000 neurons
```

## 4. Current critical path — ADR-021 evidence-source revalidation

The current blocker is **not model implementation**.

The target account proves:

```text
Workers Free / Active                 YES
Workers Paid active                   NO
```

But the current `AI → Workers AI` dashboard does not expose an explicit current Neuron usage/remaining meter. Therefore ADR-021's original account-evidence assumption cannot currently be satisfied as written.

Issue #79 is blocked pending issue #80:

```text
#79 capture real Cloudflare pre-live evidence
    BLOCKED

#80 prospectively amend ADR-021 Neuron evidence source
    CURRENT D01 CRITICAL PATH
```

Until #80 is resolved:

```text
receipt issuance                 NO
Cloudflare credential provision  NO
provider inference               NO
attempt 1                        NOT AUTHORIZED
```

No `used=0` or `remaining=10000` value may be inferred from a missing dashboard meter.

## 5. Decision state by material area

| Area | Current evidence state | Plan consequence |
|---|---|---|
| Provider/model | `PARTIALLY_ASSESSED`; Cloudflare live comparison frozen but not executed | close #80; execute only if defensibly authorized |
| Native typed tools vs MCP | `EVIDENCE_SUFFICIENT` for current scope | no new experiment |
| Evidence-sufficiency stopping | `EVIDENCE_SUFFICIENT` | preserve |
| RAG/vector/reranking | no demonstrated material retrieval gap | no experiment |
| Persistent memory | no demonstrated material need | no experiment |
| Safety/authorization | strong deterministic boundary | preserve; no weakening |
| Evaluator/RunTrace | sufficient for operational scope, C4 separate | preserve/regress |
| Agent topology | single-agent is strong qualified baseline; final comparison gap remains conditional | reassess only after provider result/blocker resolution |
| Runtime/orchestration | strong but asymmetric historical evidence | reassess only if still material after provider/topology basis |
| Adaptive model routing | unassessed but not currently material | defer |
| Deployment/UI richness | P2 unless acceptance evidence shows a gap | defer |
| C4 | exact artifact externally blocked | exact-byte recovery only |

## 6. Phase map — reconciled

| Phase | State | Exit condition |
|---|---|---|
| 1. Governance/benchmark foundations | COMPLETE | governance + benchmark semantics frozen |
| 2. Candidate/failure learning | COMPLETE | historical evidence preserved |
| 3. Confirmatory packet foundations | COMPLETE for current provider path | ADR-018/019/020/021 freezes |
| 4. Deterministic/statistical evaluation foundations | COMPLETE with bounded C4 exception | operational evaluator evidence + explicit C4 blocker |
| 4R. Global decision revalidation | **MOSTLY COMPLETE** | only genuinely material unresolved decisions remain |
| 5. Production-fit selection | **ACTIVE / provider gate** | provider result, `NO_SELECTION`, or defensible external-blocker freeze |
| 6. Final architecture freeze/integration | PENDING | remaining material decisions closed or bounded |
| 7. Regression/demo/final delivery | PENDING | reproducible acceptance evidence |

## 7. Provider decision outcomes allowed

The project must not make the final delivery depend on one optimistic external path.

Three legitimate provider outcomes exist:

### A. Live Cloudflare packet becomes authorized

```text
#80 amendment/gate resolved
→ real admissible evidence
→ short-lived receipt
→ explicit live authorization
→ execute max 32 frozen attempts
→ evaluate M1–M10/H8–H10
→ select GLM / Nemotron / NO_SELECTION
```

### B. Cloudflare remains externally blocked before deadline

Freeze an explicit bounded result:

```text
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

Then final delivery must reuse provider-free/historical evidence and clearly state that live Cloudflare comparative quality was not established.

### C. Live packet executes but no candidate qualifies

`NO_SELECTION` is a valid preregistered scientific outcome. Do not force-select a provider.

## 8. Topology/runtime plan — now conditional, not automatic

The old schedule assumed provider, topology and runtime experiments would all run in sequence. That is no longer deadline-safe or evidence-first.

After provider D01 reaches A/B/C above, perform a **fresh evidence sufficiency check**:

```text
Does single-agent vs multi-agent still materially affect a P0/P1/final architecture decision?
```

If **NO**:

- preserve the qualified single-agent controller;
- document bounded non-final comparative claim;
- do not create a topology experiment merely for completeness.

If **YES**:

- preregister the minimum controlled comparison;
- hold provider/task/tools/evaluators constant where feasible;
- compare single-agent vs only materially distinct topology candidates.

Runtime/orchestration gets the same gate **after topology**, rather than automatic experimentation.

## 9. C4 parallel recovery

C4 remains scientifically separate:

```text
required SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes             177350
rows              144
geometry          36 parents × 4 arms
```

Only exact-byte recovery is currently authorized.

C4 must not be silently reconstructed/rescored, but an external C4 block also must not erase already valid provider-free production/evaluator evidence. Final claims must separate the two scopes.

## 10. Deadline-protection plan

### 2026-09-01 → 2026-09-02 — close provider authorization evidence decision

Priority:

1. resolve #80 prospectively and provider-free;
2. either freeze a defensible replacement evidence path or freeze the live packet as externally blocked;
3. do not spend time on speculative P2 architecture.

### 2026-09-02 → 2026-09-03 — provider result or bounded blocker

If live authorization is defensible:

- execute exactly the frozen Cloudflare packet;
- preserve all failures/usage/provenance;
- evaluate and freeze candidate or `NO_SELECTION`.

If not defensible:

- stop the provider live track;
- freeze the blocker/non-claim;
- continue final delivery from existing evidence.

### 2026-09-03 → 2026-09-05 — architecture closure + production reliability

- audit whether topology/runtime are still material;
- run only minimum justified comparisons;
- freeze remaining material architecture choices;
- full production-path regression;
- degraded/conflicting/unavailable evidence tests;
- action/permission/idempotency/security tests;
- fallback/escalation continuity;
- latency/resource/trace evidence;
- fix only demonstrated blockers.

**After 2026-09-05, no new speculative architecture experiment.**

### 2026-09-05 → 2026-09-07 — final evidence package

- final architecture ADR/reconciliation;
- clean-environment reproduction;
- acceptance/rubric-to-evidence index;
- demo/runbook/fallback/rollback;
- limitations/non-claims;
- real integrated path demonstration where authorized.

### 2026-09-08 — delivery

Deliver the strongest evidence-backed scope actually achieved. Do not overstate production readiness, provider comparison, C4 completion or architecture optimality.

## 11. Stop/pivot rules

- no experiment before repository evidence sufficiency audit;
- no new provider call because credentials happen to exist;
- no fabricated quota/evidence value;
- no retry/replay of consumed/uncertain attempts;
- no paid provider/service spillover;
- no RAG/memory/multi-agent/runtime/UI complexity without a material decision gap;
- no architecture freeze based on implementation effort/popularity;
- no C4 reconstruction/rescoring without prospective amendment;
- no P2 experiment after 2026-09-05 unless it closes a demonstrated P0/P1 blocker;
- no last-minute architecture change without regression.

## 12. Repository-wide definition of done

Final completion means:

```text
all required P0 capabilities demonstrably covered
+
trustworthy integrated evaluation framework
+
material final choices supported or explicitly bounded
+
USD 0 feasibility
+
production/security/reliability risks closed or bounded
+
reproducible integrated delivery
+
rubric claims linked to evidence
+
explicit external blockers/non-claims where unresolved
```

The final answer may legitimately be the strongest bounded architecture rather than an overclaimed globally optimal one.
