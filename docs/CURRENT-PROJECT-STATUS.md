# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 09:17 BRT  
**Canonical implementation baseline before this planning checkpoint:** `main@5c353aa86747073d4b2ab32c1519e518c8d2b2c6`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Decision-revalidation program:** [`DECISION-REVALIDATION-MASTER-PLAN.md`](DECISION-REVALIDATION-MASTER-PLAN.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Master project plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts and ADRs remain authoritative for their exact historical semantics. This checkpoint changes the **prospective development policy and final-choice interpretation**; it does not rewrite prior experiment results.

## Executive state

```text
Project North Star                           strongest defensible TRACTIAN/Inteli delivery under P1-P4
Final delivery target                        2026-09-08
permanent external service/API cost          USD 0 HARD CONSTRAINT
planning before material implementation      REQUIRED
systematic decision revalidation              ACTIVE
historical frozen evidence                    PRESERVED
historical freeze == global optimality        NO

P12-C4 packet                                FROZEN_COMPLETE_C4_PACKET
P12-C4 deterministic scoring                 FROZEN / 144 OF 144 / 0 RECOMPUTATION MISMATCHES
P12-C4 bootstrap 20k                         FROZEN / PASS / INDEPENDENT RECOMPUTATION PASS
P12-C4 LOGO sensitivity                      FROZEN / 7 OF 7 / INDEPENDENT RECOMPUTATION PASS
current authorized scientific gate           REQUIRED_PER_GROUP_AND_SLICE_REPORTING
per-group/slice reporting                    BLOCKED ON EXACT SCORE-ROW ARTIFACT
semantic / FRESH_BLIND / LEGACY_LOCKED_TEST  NOT AUTHORIZED

provider/model final selection               NO
old ADR-008 OpenAI/Gemini live packet        SUSPENDED_PENDING_PROSPECTIVE_AMENDMENT
old packet live calls consumed               0 / 32
credential/account probes                    0
Groq API connection                          USER-REPORTED CONNECTED / NOT PROBED
Gemini API connection                        PENDING USER CONNECTION / NOT PROBED
OpenAI GPT-5.6 Sol production eligibility    INELIGIBLE UNDER USD 0 HARD CONSTRAINT
new provider candidate search                REQUIRED BEFORE LIVE EXECUTION

single-agent controller                      QUALIFIED_BASELINE / NOT FINAL TOPOLOGY
multi-agent alternatives                     REVALIDATION REQUIRED
runtime/orchestration final choice            REVALIDATION REQUIRED
retrieval/memory/adaptive decisions           SYSTEMATIC SCREENING REQUIRED
native tools vs MCP                           STRONG HISTORICAL COMPARATIVE EVIDENCE / PROVISIONAL

global final architecture                    UNFROZEN
production-readiness claim                   NOT AUTHORIZED
real customer mutations performed            0
```

## 1. Prospective development policy — effective now

Every future material development cycle must follow:

```text
plan / decision inventory update
→ decision question + requirement/risk mapping
→ hard constraints
→ systematic current research
→ credible materially different alternatives + simple/null baseline
→ preregistered comparison
→ implementation / execution
→ quantitative evaluation
→ uncertainty / repeated runs
→ robustness / failure analysis
→ production-fit analysis
→ Pareto / trade-off analysis
→ decision + reversal triggers
→ regression
→ PREFERRED / FROZEN only when justified
```

If the plan, alternatives and comparison protocol are not documented, implementation is not authorized.

A historical ADR/freeze remains immutable evidence. When a hard assumption changes or a credible alternative was omitted, the correct action is prospective revalidation/supersession, not rewriting the historical artifact.

## 2. Permanent zero-cost constraint

The production/project path must remain monetarily free:

```text
external API / hosted-service project charge    USD 0
paid subscription required                      NO
purchased API credits                           NO
unbounded paid spillover                        FORBIDDEN
```

Within this feasible set, the project still targets the strongest credible quality frontier; free status is only an eligibility gate, not a quality decision.

Free-credit/free-tier routes are eligible only when the project run can be bounded to USD 0 without silent billable spillover.

## 3. Provider/model state — previous execution plan suspended

ADR-008 through ADR-011 remain historical frozen evidence of the previously designed OpenAI/Gemini comparison infrastructure and governance. They are **not deleted or rewritten**.

However, the previously planned live execution is no longer prospectively valid because its OpenAI GPT-5.6 Sol candidate violates the now-explicit USD 0 hard constraint.

Therefore:

```text
old comparison plan SHA-256             69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
historical design                         PRESERVED
old live execution                        SUSPENDED
old live calls consumed                   0 / 32
first live attempt executed               NO
production provider/model selected        NO
new live execution                        REQUIRES PROSPECTIVE AMENDMENT
```

Issue #44 must not execute the old packet. A new provider comparison must first research and preregister the credible **zero-cost** candidate set.

Minimum current screening scope includes:

- Gemini free-tier candidates compatible with the required structured decision/tool contract;
- Groq free-tier candidates compatible with the same contract;
- OpenRouter explicitly free routes/models if model identity and zero-cost containment are adequate;
- Cloudflare Workers AI free-tier candidates if contract fit is adequate;
- at least one feasible local/open-weight baseline when project hardware permits;
- other materially distinct zero-cost options discovered by primary-source research.

Connection state is not evaluation evidence and must not be verified by secret/account probing:

```text
Groq API     user reports connected
Gemini API   user will connect / pending
```

## 4. Agent architecture decision state

The existing explicit single-agent controller remains valuable, tested and historically frozen within ADR-004's scope. Its provider-free reliability/safety evidence remains valid.

Its current **final-choice** interpretation is now:

```text
single-agent explicit controller    QUALIFIED_BASELINE
final topology                      NOT SELECTED
```

Before global architecture freeze, prospectively compare materially distinct topologies under controlled conditions, including at least where feasible:

```text
A  single agent / explicit controller
B  planner → executor
C  agent → critic/reviewer
```

Hold provider/model, case distribution, ToolSpecs, HarnessRunner, authorization policy and evaluator definitions constant where possible so topology is the changed variable.

## 5. Other material decisions requiring review

The active decision-revalidation program covers:

- provider/model;
- agent topology;
- orchestration/runtime;
- tool topology/protocol;
- evidence/retrieval;
- memory/state;
- adaptive stopping/planning/model routing;
- safety/authorization additions without weakening hard boundaries;
- evaluator/judge scope;
- observability;
- deployment;
- UI/integration where material to delivery quality.

Historical evidence may be sufficient to retain some choices. It must still be checked against the current search scope and hard constraints.

Native typed tools vs MCP currently has comparatively strong historical evidence: E7 demonstrated equal 18-tool coverage/schema/invocation/guard/trace fidelity with greater MCP complexity. This remains provisional evidence for native tools unless new requirements or alternatives change the trade-off.

## 6. Scientific C4 critical path — exact recovery first

The scientific gate remains `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` on the exact original evaluator-side score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

The repository contains the scorer, frozen outputs, deterministic scoring freeze, bootstrap and LOGO derivatives, but the exact full score-row bytes were deliberately not committed in the original workflow.

Authorized now:

- search local/historical/temporary/workflow storage for exact bytes;
- verify exact SHA-256, size and geometry if recovered.

Not authorized by this checkpoint:

- reconstruction;
- rescoring;
- substitution;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- downstream survivor/PREFERRED inference.

If exact bytes cannot be recovered, a **separate prospective scientific amendment** must first define whether a byte-identical reproduction attempt is admissible. Any reproduction that does not match the exact frozen SHA-256 and byte count is rejected and cannot substitute for the original artifact.

## 7. Preserved provider-free production/reliability foundation

The following historical evidence remains valid in its original scope:

```text
ADR-004  Agent Controller                              FROZEN HISTORICAL EVIDENCE
ADR-005  production action safety                     FROZEN HISTORICAL EVIDENCE
ADR-006  provider-neutral DecisionSource              FROZEN HISTORICAL EVIDENCE
ADR-007  model-call provenance                        FROZEN HISTORICAL EVIDENCE
ADR-008  prior provider comparison design             FROZEN HISTORICAL EVIDENCE / EXECUTION SUSPENDED
ADR-009  prior concrete provider clients              FROZEN HISTORICAL EVIDENCE
ADR-010  prior provider comparison executor           FROZEN HISTORICAL EVIDENCE
ADR-011  prior governed live wrapper                  FROZEN HISTORICAL EVIDENCE
ADR-012  controlled supplied/test action execution    FROZEN HISTORICAL EVIDENCE
ADR-013  EV-007 failure performance                   FROZEN HISTORICAL EVIDENCE
ADR-014  EV-008 repeated-run stability                FROZEN HISTORICAL EVIDENCE
ADR-015  EV-011 customer-safe communication           FROZEN HISTORICAL EVIDENCE
ADR-016  final-delivery reproduction/evidence         FROZEN HISTORICAL EVIDENCE
ADR-017  final handoff acceptance audit               FROZEN HISTORICAL EVIDENCE
```

Key preserved evidence:

```text
EV-007 report SHA-256                    7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
EV-008 report SHA-256                    1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
EV-011 report SHA-256                    cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
ADR-016 demo SHA-256                     43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
final acceptance rows                    83
PASS_EVIDENCED                           41
PASS_BOUNDED                             40
EXTERNALLY_BLOCKED                        1
UNEXECUTED_GATED                          1
GAP_ACTION_REQUIRED                       0
clean-checkout production tests         251 passed
ADR-004 regression                       12 passed
```

ADR-017 continues to prove reviewer-ready provider-free acceptance within its evidenced scope. It does **not** prove global architecture optimality, live provider quality, C4 completion or unconditional production readiness.

## 8. Immediate priorities

1. merge/freeze this planning/governance update before new material development;
2. complete current primary-source research and the material-decision inventory;
3. create/freeze a prospective zero-cost provider-comparison amendment before any provider call;
4. preregister the agent-topology comparison before implementing alternative topologies;
5. preregister runtime/adaptive comparisons one dimension at a time;
6. search for the exact C4 artifact in parallel;
7. integrate only the best-supported zero-cost Pareto configuration after controlled evidence;
8. rerun full regression and reconcile delivery evidence before final architecture freeze.

## 9. Still forbidden

- executing the old ADR-008/#44 provider packet as-is;
- treating credential presence as authorization or evidence;
- credential/account probing merely to verify user-reported connections;
- paid provider/service production usage;
- hidden provider retries/fallbacks/warm-ups or uncontrolled provider state in controlled comparisons;
- reconstructing/rescoring/substituting C4 without a separate prospective amendment;
- semantic/FRESH_BLIND/LEGACY_LOCKED_TEST access without explicit authorization;
- provider-native TRACTIAN tool execution that bypasses the governed execution boundary;
- weakening deterministic action safety/authorization/idempotency boundaries;
- treating historical freeze/acceptance PASS as proof of optimality;
- claiming global architecture freeze or production readiness before revalidation closes.
