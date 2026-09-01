# Academy × TRACTIAN — Governed Project Plan to Final Delivery

**Status:** ACTIVE / canonical macro plan  
**Planning checkpoint:** 2026-09-01 — ADR-023 governed entrypoint merged; standalone production wheel reproducibility proved; real D01 reset-window evidence pending  
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

The project does not optimize experiment count, framework novelty or architecture breadth. It closes only material evidence gaps that can still change the final delivery.

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
P1 production/security/reliability/reproducibility closure
↓
P2 optional complexity only if evidence says it can matter and deadline allows
```

Provider-free audits may continue before D01 only when they cannot alter or consume the frozen Cloudflare packet and do not pre-empt a post-D01 topology/runtime decision.

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
governed entrypoint audit/contract               ACCEPTED / ADR-023
minimal gate-specific live launcher              MERGED / PROVIDER-FREE VALIDATED
standalone production wheel reproduction         PROVED / PR #91
```

Canonical current `main` after the reproduction closure:

```text
a93854dd5e70edf8084bdaae1762dd64cdb6aa48
```

The ADR-023/launcher merge remains historical provenance at:

```text
5b4b0a2f4bbf51215c901af534216805d26386b0
```

PR #91 added no runtime/provider/evaluator semantic change. Its clean-wheel job built the root wheel, installed only that wheel in a clean virtual environment, executed outside the repository checkout, imported both `academy_tractian` and `research.e2`, and validated the canonical 18-operation registry. Existing production/runtime regressions remained green.

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

## 4. ADR-022 reset-window authorization path

ADR-021's explicit Neuron-balance path remains historically frozen and valid when such a meter exists. The target account UI does not expose it.

ADR-022 adds the conservative fallback:

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

## 5. ADR-023 entrypoint boundary

The entrypoint audit found:

```text
substantive composition sufficient
operational entrypoint missing
no executor/custody/client/authorization changes authorized
minimal gate-specific launcher only
```

ADR-023 freezes the only allowed live composition:

```text
reset_window_authorization_to_adr020_pre_live_evidence(...)
→ CloudflareLiveSecrets from environment only
→ build_cloudflare_one_shot_transport_v2()
→ GovernedCloudflareLiveTaskV2.prepare(..., fixture_result=False)
→ execute_all()
```

The canonical operator command is:

```text
python scripts/research/execute_cloudflare_live_comparison_v2.py --evidence <evidence.json> --receipt <receipt.json> --custody-root <canonical-root>
```

No direct client construction, duplicate authorization, retry, fallback, alternate custody/model/provider, generic CLI framework or `[project.scripts]` promotion is authorized.

## 6. Pre-D01 work allowed before the reset

The provider path itself needs no more implementation before the reset. The remaining safe work is acceptance/reliability auditing that is independent of provider choice.

Priority order:

```text
A. standalone distribution/reproduction risk      CLOSED / PR #91
B. canonical action-plan reconciliation            ACTIVE
C. delivery-acceptance gap audit                   NEXT
D. real-demo path completeness audit               NEXT
E. security / trace / failure-containment audit    NEXT
```

For C–E, classify every finding as:

```text
PROVED
PARTIAL
BLOCKED
MISSING
```

A finding may be fixed before D01 only if all are true:

1. it maps to a concrete P0/P1 acceptance row or reproducibility/security risk;
2. it is provider-independent;
3. it does not change ADR-018→023 semantics, packet, custody or attempt accounting;
4. it does not select or implement a topology/runtime/RAG/memory decision reserved for post-D01;
5. the smallest fix can be validated provider-free.

Otherwise record it and defer to the relevant post-D01 materiality gate.

## 7. Immediate D01 critical path

The next admissible target reset window is:

```text
2026-09-02 00:00–00:10 UTC
=
2026-09-01 21:00–21:10 America/Sao_Paulo
```

Operational sequence:

```text
ADR-018→023 provider-free path frozen/validated
↓
enter admissible 00:00 UTC reset
↓
within first 10 minutes capture Workers Free evidence
+ no-use/exclusive-use attestations
↓
create reset-window evidence JSON
↓
issue <=5-minute provider-free receipt bound to exact custody root
↓
only then provision Cloudflare token/account ID
↓
explicitly invoke the ADR-023 governed launcher
↓
ADR-020 governed executor/custody path
↓
execute frozen packet
```

If the account cannot be placed under truthful exclusive Workers AI custody, do not weaken the protocol. Freeze an external blocker.

## 8. Allowed provider outcomes

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

## 9. Decision state by architecture area

| Area | Evidence state | Plan consequence |
|---|---|---|
| Provider/model | `PARTIALLY_ASSESSED`; live comparison pending | current operational gate |
| Provider entrypoint | `EVIDENCE_SUFFICIENT`; ADR-023 provider-free validated | preserve; no more wrapper work |
| Standalone packaging/reproduction | `EVIDENCE_SUFFICIENT`; PR #91 clean-wheel smoke passed | preserve/regress |
| Native typed tools vs MCP | `EVIDENCE_SUFFICIENT` | preserve native ToolSpec; no new experiment |
| Evidence-sufficiency stopping | `EVIDENCE_SUFFICIENT` | preserve |
| Safety/authorization/idempotency | strong deterministic boundary | preserve/strengthen only |
| RunTrace/operational evaluator | sufficient current scope | preserve/regress |
| RAG/vector/reranking | no demonstrated material gap | do not add |
| Persistent memory | no demonstrated material need | do not add |
| Agent topology | strong single-agent qualified baseline; comparative optimality conditional | audit after provider D01 |
| Runtime/orchestration | historical evidence strong but asymmetric | assess only if still material after topology |
| Adaptive model routing | unassessed but not currently material | defer |
| Rich observability/UI/deployment | P2 unless acceptance gap appears | defer |
| Architecture-selection protocol | PLANNED / issue #92 | activate only after D01 resolves/bounds |
| C4 | exact artifact externally blocked | exact-byte recovery only |

## 10. Post-provider architecture materiality and Pareto protocol

Issue #92 is the prospective planning authority for remaining architecture decisions. It authorizes no pre-D01 experiment.

Start condition:

```text
provider D01 result
OR
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED frozen
```

Then:

```text
re-audit topology evidence
→ can topology still materially change P0/P1/final architecture?
   ├─ NO → preserve single-agent qualified baseline
   └─ YES → preregister minimum controlled topology comparison
```

Every candidate must first pass hard gates for P0 coverage, deterministic safety, evaluator/gold isolation, trace integrity, clean reproduction, USD 0 feasibility and safe failure behavior.

Only hard-gate-passing candidates may be compared on a Pareto frontier covering correctness, tool/argument/evidence quality, escalation/fallback, stability, latency/resources, coordination failures, operational complexity and debuggability.

Do not collapse the decision into an arbitrary weighted score.

Runtime/orchestration is assessed only after topology/materiality is closed. RAG/vector/reranking, persistent memory, MCP migration, adaptive routing and richer observability remain conditional on a measured material gap.

## 11. C4 parallel track

Exact required artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Only exact-byte recovery is currently authorized. No reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND or LEGACY_LOCKED_TEST.

A fresh 2026-09-01 recovery pass found no candidate in connected ChatGPT Library/conversation storage or Google Drive by exact SHA or deterministic-scoring identifiers. Issue #9 remains open as the explicit external scientific blocker.

C4 does not block preserving the already validated provider-free handoff; it limits the exact claims that can be made.

## 12. Phase map

| Phase | State | Exit condition |
|---|---|---|
| Governance/benchmark foundation | COMPLETE | immutable governance and benchmark semantics |
| Historical candidate/failure learning | COMPLETE | evidence preserved |
| Provider packet foundations | COMPLETE | ADR-018→023 provider-free freezes/validation |
| Standalone packaging/reproduction | COMPLETE | clean-wheel installation/import proof |
| Pre-D01 acceptance/reliability audit | ACTIVE | provider-independent P0/P1 gaps classified/bounded |
| Operational provider selection | ACTIVE | live result, `NO_SELECTION`, or external-blocker freeze |
| Remaining architecture decisions | CONDITIONAL | #92 materiality/Pareto protocol activated after D01 |
| Final architecture integration | PENDING | supported choices integrated/regressed |
| Final demonstration/delivery | PENDING | acceptance evidence + reproducible real path |

## 13. Deadline protection

### 2026-09-01 before 21:00 America/Sao_Paulo

- standalone production wheel reproduction closed by PR #91;
- reconcile canonical action plans/status;
- audit remaining delivery-acceptance, demo-path and security/trace gaps provider-free;
- do not implement topology/runtime/RAG/memory changes;
- prepare private reset evidence source/custody inputs without provider calls or credential probes.

### 2026-09-01 21:00–21:10 America/Sao_Paulo / 2026-09-02 00:00–00:10 UTC

- use the reset window only if every ADR-022 attestation is truthful;
- capture evidence → issue receipt → provision secrets → explicit launcher invocation;
- otherwise freeze the external blocker instead of weakening evidence.

### 2026-09-02 → 2026-09-03

- finish live packet and provider decision if authorized; or
- freeze `LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED`;
- activate issue #92 only after D01 is resolved/bounded.

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

## 14. Stop/pivot rules

- preserve failed/consumed experiments;
- never fabricate quota or operational evidence;
- do not use Paid Workers or paid AI Gateway spillover;
- no provider inference before valid authorization and explicit governed launcher invocation;
- no hidden retries/fallbacks/warm-ups/provider state;
- no replay of claimed/uncertain attempts;
- do not change the ADR-018 packet after live results begin;
- do not add a second launcher/wrapper or rewrite executor/custody/client/authorization for entrypoint convenience;
- do not add RAG/memory/multi-agent/runtime/UI complexity absent a measured material gap;
- pre-D01 audits may identify gaps but may not pre-empt #92 topology/runtime decisions;
- do not promote an implemented component to final merely because it exists;
- if an external condition blocks stronger evidence, freeze the blocker and continue the strongest defensible delivery.

## 15. Repository-wide definition of done

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
P1 production/security/reliability/reproducibility risks closed or bounded
+
reproducible real-path demonstration
+
limitations/non-claims explicit
```
