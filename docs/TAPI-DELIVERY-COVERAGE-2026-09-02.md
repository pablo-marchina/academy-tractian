# TAPI Delivery Coverage — Stack, Techniques, Frameworks and Final Outputs

**Status:** ACTIVE / canonical TAPI-to-delivery coverage  
**Final-P0 checkpoint:** 2026-09-05 BRT  
**Project:** Academy × TRACTIAN — Engenharia e Avaliação de Agentes Industriais  
**Source:** TAPI `Engenharia e Avaliação de Agentes Industriais`  
**Functional P0 baseline:** `d3bed06b132212c85b126f56708863d45f64e03e`  
**Post-merge gate:** `final-ci-required` run #386 / `required-gate = success`  
**Delivery:** 2026-09-08

This document answers one question: **how the delivered product covers the assignment scope and expected technical/evaluation outputs**. Historical ADRs/experiments remain authoritative for their original checkpoints.

## 1. Declared combined track

The delivery combines the two TAPI capabilities in one solution:

- **Agent construction:** governed industrial support agent with typed TRACTIAN tools, bounded investigation, evidence-aware outcomes, escalation and controlled consequential actions;
- **Agent evaluation framework:** scenario/campaign execution, deterministic trace/safety/trajectory metrics, failure/stability/communication analysis, provider experiments and safe trace-inspection product surfaces.

Project research question:

> How can an industrial support agent use typed tools and evidence while remaining reliable under incomplete/conflicting/unavailable API responses, consequential-action risk and provider variability?

## 2. Final technical stack

### Agent/runtime

| Layer | Final choice | State |
|---|---|---|
| Language | Python >=3.11 | implemented |
| Schemas | Pydantic 2.x | implemented |
| Product/API | FastAPI + Uvicorn | implemented |
| Agent orchestration | custom `AgentController` | final P0 `NO_CHANGE` |
| Execution boundary | `HarnessRunner` | frozen hard boundary |
| Tool contract | 18 typed `ToolSpec`s | implemented |
| TRACTIAN integration | typed adapter/transport | implemented |
| Serving persistence | PostgreSQL + psycopg | promoted |
| Tenant isolation | PostgreSQL RLS + signed server context | promoted/tested |
| Realtime wakeup | PostgreSQL LISTEN/NOTIFY + durable fallback | promoted/tested |
| Read-only handoff | PostgreSQL work items + generation leases | promoted/tested |
| Consequential action ownership | custody + idempotency + non-transferable lease | promoted/tested |
| Packaging | hatchling wheel | reproduced |

DuckDB is not a production dependency. It remains only in explicit dev/benchmark compatibility extras.

### Frontend

| Layer | Choice |
|---|---|
| Language | TypeScript |
| UI | React 19 |
| Build | Vite |
| Server state | TanStack Query |
| Analytics | Apache ECharts |
| Trace/architecture graph | React Flow / `@xyflow/react` |
| Unit tests | Vitest |
| Browser acceptance | Playwright / Chromium |
| Dependency lock | committed `package-lock.json` + `npm ci` |

### Evaluation/research

| Technique | Delivered role | State |
|---|---|---|
| deterministic trace evaluator | structure/safety/trajectory/provenance | implemented |
| scenario/failure campaigns | complete/partial/conflict/unavailable/provider/tool cases | implemented |
| repeated runs | stability/signature behavior | implemented |
| communication campaign | customer-safe terminal/handoff behavior | implemented |
| action safety evaluation | proposal/confirmation/idempotency/fencing/no-replay | implemented |
| provider comparison | D01/D02 controlled USD0 experiments | complete / `NO_SELECTION` |
| load/concurrency | queue/latency/resource description | measured / bounded |
| restart/recovery | conservative persisted-state semantics | measured / bounded |
| realtime benchmark | polling vs LISTEN/NOTIFY | measured / candidate promoted |
| human semantic review | blinded collection/adjudication infrastructure | implemented; real labels missing |
| operational value | blinded MANUAL×ASSISTED collection + paired analysis | implemented; real observations missing |
| adaptive stopping | evaluator-only replay diagnostic | implemented / not promoted |

## 3. Agent techniques

### T1 — Typed tool-augmented loop

```text
decision
→ optional typed tool proposal
→ deterministic validation/policy
→ execution
→ normalized observation
→ next decision or terminal outcome
```

No hidden chain-of-thought is claimed or exposed.

### T2 — Typed function/tool calling

- one canonical 18-operation registry;
- strict parameter schemas;
- deterministic argument validation;
- identity/tenant/permissions outside model control;
- no arbitrary model-generated HTTP path.

### T3 — Evidence-aware outcomes

First-class outcomes:

- orient/final;
- investigate;
- clarify;
- abstain;
- escalate;
- bounded consequential-action proposal.

### T4 — Deterministic safety envelope

- B1 schema/argument checks;
- B2 permission/resource/action policy;
- B3 evidence/authorization where applicable;
- explicit confirmation;
- persistent idempotency;
- non-transferable action execution lease;
- privacy field deny-list;
- hard resource/turn/tool caps.

### T5 — Distributed ownership with asymmetric semantics

Read-only runtime lease expiry may allow takeover with a new generation. Consequential action lease expiry/loss does not transfer; the product converges ambiguity to `UNCERTAIN` and forbids replacement replay.

### T6 — Evidence/provenance tracing

Ordered runtime/evaluator transitions become safe PostgreSQL run/event/evidence/evaluation rows. Frontend exposes producer/evidence lineage without raw private trace material.

### T7 — Realtime durable projection

PostgreSQL rows/cursors are authoritative. LISTEN/NOTIFY is wakeup-only; missed notifications recover through bounded durable reads. SSE/browser reduction is idempotent.

### T8 — Eval-Driven Development

```text
requirement
→ metric/evaluator
→ baseline
→ preregistered candidate
→ repeated/sliced comparison
→ hard gates + uncertainty
→ PROMOTE / REJECT / INCONCLUSIVE / NO_CHANGE
→ regression
```

## 4. TAPI analysis objects covered

The evaluation framework covers the assignment's meaningful agent dimensions:

1. function/tool selection;
2. argument validity/accuracy where deterministically measurable;
3. execution trajectory;
4. evidence/provenance use;
5. response/operational-conclusion quality;
6. safety/authorization;
7. failure behavior;
8. stability between executions;
9. high-impact/consequential-action behavior;
10. escalation/handoff and communication behavior.

Semantic response-quality claims remain bounded where real human labels are unavailable.

## 5. Provider/model experiment line

### D01

- 2 Cloudflare Workers AI free candidates;
- frozen public packet;
- 32/32 governed attempts completed;
- USD0;
- substantial exact-512 completion-cap censoring observed;
- selection: `NO_SELECTION`.

### D02

Controlled change:

```text
completion cap 512 → 1024
```

All 32/32 governed attempts completed at USD0. Quality improved materially on several public metrics, but both candidates still failed frozen M1/M4/M7 promotion gates.

Accepted aggregate D02:

| Candidate | M1 | M4 | success | stability | median | p95 | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| GLM 4.7 Flash | 0.4375 | 0.3750 | 0.4375 | 0.2500 | 15329 ms | 38270 ms | FAIL M1/M4/M7 |
| Nemotron 3 120B A12B | 0.5625 | 0.5625 | 0.5625 | 0.5000 | 4218.5 ms | 9168 ms | FAIL M1/M4/M7 |

Final provider/model state: **`NO_SELECTION`**.

D01/D02 are consumed and must not be replayed. Any future provider/model comparison is P1 with a new experiment ID/protocol.

## 6. Frameworks/tools intentionally not on the P0 critical path

| Technology | Final P0 decision | Reason |
|---|---|---|
| LangGraph | not promoted / `NO_CHANGE` | PostgreSQL handoff/action fencing closed measured durability/HITL gaps without framework migration |
| LangChain | not used | no measured benefit over typed bounded path |
| Pydantic AI orchestration | not used | schemas use Pydantic directly; no orchestrator gap |
| MCP migration | not used | native typed tools satisfy supplied API need |
| RAG/vector/hybrid retrieval | not used | no demonstrated retrieval gap |
| persistent cross-request memory | not used | no demonstrated requirement; privacy/reproducibility cost |
| multi-agent | not used | no measured topology gap |
| Redis/Kafka/Temporal | not required | PostgreSQL topology satisfies tested P0 serving/handoff/realtime needs |
| Streamlit/Gradio | not used | React control room better fits realtime/drill-down/trace needs |

Absence is an evidence-backed scope decision, not an omission.

## 7. Final product outputs

### O1 — Functional industrial agent

Can:

- contextualize/orient;
- investigate through typed TRACTIAN reads;
- clarify;
- abstain;
- escalate with structured handoff;
- propose actions under deterministic policy;
- execute only after explicit governed confirmation in enabled profiles;
- fail safely under tool/provider/runtime issues.

### O2 — Typed TRACTIAN integration

- 18-operation registry;
- typed adapter/transport;
- strict schemas;
- normalized observations;
- action-policy integration;
- standalone reproducible package.

### O3 — Agent evaluation framework

- scenario runner;
- deterministic metrics/evaluators;
- trace validators;
- failure/adversarial/stability/communication campaigns;
- action-safety evaluation;
- provider comparison harness/evidence;
- safe per-run evaluation in product UI.

### O4 — Governed experiment reports

Final evidence includes:

- provider-free baseline/failure/stability/communication evidence;
- D01/D02 design/results/limitations;
- realtime wakeup comparison;
- operational-store/load/restart/distributed ownership decisions;
- negative outcomes such as `NO_SELECTION`, `NO_CHANGE`, `NOT_PROMOTED`.

### O5 — Realtime Operator Control Room

Connected surfaces include:

1. Mission Control;
2. Live Run Cockpit;
3. Run Explorer;
4. Timeline / Waterfall;
5. Trace Graph;
6. Architecture Explorer;
7. Evidence Explorer;
8. Output Lineage;
9. Action Control;
10. Tools & Policy analytics;
11. Eval Lab;
12. Provider D01/D02 Lab;
13. Dynamic Data Explorer;
14. Production Health.

### O6 — Output lineage

Safe outputs identify producer classes:

```text
MODEL
CONTROLLER
POLICY
TOOL
OBSERVATION
EVALUATOR
SYSTEM
```

The UI answers what happened, what evidence fed it, what happened next, what became terminal and what evaluation followed.

### O7 — Reproduction/evidence package

- clean-clone backend/evaluator/frontend reproduction;
- Chromium full-product acceptance;
- horizontal runtime handoff gate;
- action execution lease gate;
- stable aggregate `required-gate`;
- final freeze bundle with exact Git blobs and canonical manifest hash;
- provider-independent final rehearsal path.

## 8. Requirement-to-evidence map

| TAPI expectation | Final evidence/disposition |
|---|---|
| API integration quality | typed 18-tool registry + adapter + contract/runtime tests |
| Functional agent | production runtime + browser/provider-free integrated paths |
| Function selection | traces/evaluator/campaigns |
| Argument accuracy | ToolSpec/B1 deterministic validation + tests |
| Execution trajectory | RunTrace + timeline/graph + evaluator |
| Evidence use | evidence rows/lineage + clarify/abstain/escalate cases |
| Response quality | deterministic communication + human-review infrastructure; real semantic calibration still NOT READY |
| Safety | B1/B2/B3 + action custody/confirmation/idempotency/leases |
| Failure behavior | EV-007 + tool/provider/restart/distributed tests |
| Stability | EV-008 repeated-run campaign |
| High-impact actions | controlled action proposal/confirmation/execution + stale-owner fencing |
| Technical experiment | D01/D02 + storage/realtime/load/recovery comparisons |
| Result analysis | frozen decision docs + crosswalk + product analytics |
| Limitations/risks | explicit bounded non-claims and external blockers |
| Reproducibility | clean clone + exact evidence pins + lockfile |
| Documentation | README + architecture + plan + acceptance + runbook + rubric crosswalk |
| Demonstration quality | real provider-free Chromium path + presentation rehearsal sequence |

## 9. Final demonstration coverage

The final provider-independent presentation should visibly show:

```text
request
→ live run
→ architecture activation
→ structured decision/model metadata
→ typed tool proposal
→ deterministic policy result
→ TRACTIAN transport metadata
→ safe evidence
→ next decision
→ terminal / clarification / abstention / escalation / governed action
→ RunTrace completion
→ post-runtime evaluation
→ output lineage
→ Production Health
→ dynamic analytics
→ D01/D02 + architecture-decision evidence
```

Live provider availability must not be a single point of failure.

## 10. Exact current acceptance evidence

Functional P0 baseline:

`d3bed06b132212c85b126f56708863d45f64e03e`

Post-merge `final-ci-required` run #386 / `33971230788`:

```text
clean-clone                         success
Chromium                            success
horizontal runtime handoff          success
action execution lease              success
required-gate                       success
```

## 11. Explicit boundaries

Final delivery must not claim:

- a selected production provider/model;
- completed semantic human calibration;
- measured Engineer Minutes Saved/business value;
- adaptive stopping runtime improvement;
- production capacity/SLO from hosted CI;
- deployed Cloud Run/Cloud SQL HA, RTO/RPO, autoscaling, multi-region failover or uptime;
- distributed exactly-once external side effects;
- enterprise OAuth/OIDC/SSO;
- superiority/necessity of LangGraph/RAG/multi-agent/etc.;
- branch protection while GitHub reports `main.protected=false`, `rulesets=[]`;
- reconstruction/substitution/rescoring of the externally unavailable exact C4 artifact.

## 12. Freeze/delivery state

Before end of 2026-09-05, canonical documentation/evidence drift must be closed and the exact final PR head must pass clean clone + Chromium + horizontal runtime + action lease + `required-gate`.

After hard freeze, only delivery-blocking fixes with targeted regression are allowed. Final rehearsal is 2026-09-06/07; delivery is 2026-09-08.