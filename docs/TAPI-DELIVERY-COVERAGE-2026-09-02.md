# TAPI Delivery Coverage — Current Crosswalk

**Status:** ACTIVE TAPI/output crosswalk  
**Original filename checkpoint:** 2026-09-02  
**Current rebaseline:** 2026-09-05 corrected  
**Project:** Academy × TRACTIAN — Engenharia e Avaliação de Agentes Industriais  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This document maps audited TAPI/delivered-package expectations to the current product. It deliberately separates **assignment requirements** from **project-added hard constraints/quality gates** so the repository does not misrepresent an internal rule as a literal TRACTIAN mandate.

## 1. Audited TAPI scope

The project delivers one integrated solution containing:

- **Industrial Agent** — typed TRACTIAN API/tool use, evidence-aware investigation, bounded decisions, clarification/abstention/escalation and governed actions.
- **Agent Evaluation Framework** — scenario execution, trace/trajectory evaluation, tool/argument/evidence/safety/failure/stability analysis and controlled experiments.

Operational modes: `CONTEXTUALIZE`, `INVESTIGATE`, `EXECUTE`.

Product outcomes: `FINAL/ORIENT`, `CLARIFY`, `ABSTAIN`, `ESCALATE`, `ACTION_PROPOSAL/CONFIRMED_ACTION`.

## 2. TAPI/delivered-package driven expectations

The crosswalk treats the following as assignment/delivery obligations or direct quality dimensions:

- functional industrial agent;
- supplied TRACTIAN API integration;
- function/tool selection;
- argument quality/validity;
- execution trajectory/process;
- evidence use;
- response/operational-conclusion quality;
- safety and high-impact-action behavior;
- degraded/failure behavior;
- repeated-execution stability;
- technical experiment/hypothesis;
- result analysis and limitations;
- reproducibility/documentation;
- inspectable demonstration/evaluation output.

Suggested frameworks/libraries are not interpreted as mandatory when an equivalent architecture satisfies the requirement more directly.

## 3. Project-added hard constraints and quality gates

These are **our project rules**, not claims about exact TAPI wording:

### Hard constraints

- **actual project cash cost = USD 0**;
- no automatic paid spillover or paid fallback;
- final serving path is remote and has no developer-machine/local production dependency;
- final product is multi-user and tenant-safe;
- material decisions use systematic research + quantitative evidence;
- EDD controls promotion of material changes;
- adaptive behavior is promoted only after beating a simpler baseline without weakening hard gates;
- live frontend exposes safe architecture/runtime/evaluation/health evidence.

A paid component may be researched as an external reference but is `INELIGIBLE` for project selection. If no USD0 candidate passes the technical gates, the correct result is an explicit blocker/`NO_SELECTION`, not relaxation of the constraint.

### Additional production-quality gates

- standards-based end-user IAM;
- PostgreSQL RLS tenant isolation;
- protected CI/CD and tested rollback;
- remote load/soak and evidence-based SLOs;
- backup/restore and measured recovery evidence where claimed;
- human calibration before semantic-judge promotion;
- paired operational-value measurement;
- live architecture/trace/evidence/health visualization.

## 4. Current technical stack

### Agent/runtime

| Layer | Current choice | State |
|---|---|---|
| Language | Python >=3.11 | implemented |
| Typed schemas | Pydantic 2.x | implemented |
| API/product service | FastAPI + Uvicorn | implemented |
| Agent orchestration | custom `AgentController` | promoted baseline |
| Tool execution | `HarnessRunner` | hard execution boundary |
| Tool contract | typed `ToolSpec` registry | 18 operations |
| TRACTIAN integration | typed HTTP transport/normalization | implemented |
| Action safety | validation/policy + custody/idempotency/leases/fencing | implemented |
| Logical durable serving state | PostgreSQL + psycopg | promoted |
| Packaging | hatchling/wheel | clean-clone proved |

The final remote hosting/database/IAM/provider topology is still unselected and must satisfy USD0 plus the production gates.

### Model/provider

Historical Cloudflare D01/D02 are complete USD0 experiments.

Current result: **`NO_SELECTION`**.

D02 proved cost eligibility and completed 32/32 governed attempts, but the tested candidates failed frozen M1/M4/M7 promotion gates. Therefore Cloudflare was not rejected for cost; it simply did not satisfy the full technical promotion contract.

A new production model experiment must consider only hosted USD0-eligible candidates for final selection. A materially new Cloudflare model/configuration can re-enter only through a new preregistered experiment; consumed D01/D02 packets are not replayed.

### Evaluation

Implemented: deterministic structural/safety/trajectory evaluation, failure/stability campaigns, EDD machinery, semantic-review collection/protocol, operational-value collection/paired analysis and evaluator-only adaptive-stopping diagnostics.

Not yet evidence-ready: real human semantic calibration and real human operational-value claims.

### Realtime observability

PostgreSQL rows/cursors are durable truth; LISTEN/NOTIFY is wake-up only; FastAPI SSE delivers safe live state to the React frontend. DuckDB is dev/benchmark compatibility only, not production serving truth.

### Frontend

React + TypeScript + Vite + TanStack Query + ECharts + React Flow + Vitest + Playwright are implemented. The final remote hosting path must itself remain USD0.

## 5. Techniques used

- typed tool-augmented iterative agent loop;
- typed function/tool calling;
- evidence-aware final/clarify/abstain/escalate/action outcomes;
- bounded execution/stopping;
- deterministic fail-closed action safety;
- structured evidence/provenance tracing;
- explicit degraded-evidence handling;
- repeated-execution stability measurement;
- controlled provider/model experiments;
- deterministic-first evaluation with human-calibrated semantic layer when ready;
- durable realtime observability;
- schema-driven quantitative visualization;
- evaluation-driven engineering.

## 6. Components not currently promoted

LangGraph, LangChain orchestration, Pydantic-AI orchestration, MCP, RAG/vector retrieval, persistent memory, multi-agent topology, Redis/Kafka and Kubernetes/microservices are not promoted without a measured gap, controlled challenger evidence **and USD0 eligibility for any selected hosted dependency**.

Absence is a decision/scope outcome, not an omission.

## 7. Product outputs

- **O1:** functional industrial agent.
- **O2:** 18-operation typed TRACTIAN integration package.
- **O3:** agent evaluation framework.
- **O4:** governed technical experiment evidence.
- **O5:** realtime Production Control Room.
- **O6:** Architecture Explorer.
- **O7:** Output Lineage / Explain This Run.
- **O8:** Dynamic Data Explorer.
- **O9:** realtime production telemetry.
- **O10:** technical documentation and reproduction/operations package.

## 8. Requirement-to-evidence map

| TAPI/delivery expectation | Current/final evidence |
|---|---|
| API integration quality | typed 18-tool registry + HTTP adapter + contract/integration tests |
| Functional agent | production runtime/controller/tool path + browser acceptance |
| Function selection | scenario/evaluator metrics + run traces |
| Argument accuracy | schema validation + evaluator/tests |
| Execution trajectory | RunTrace + Timeline/Trace Graph |
| Evidence use | evidence lineage + partial/conflict/unavailable cases |
| Response/conclusion quality | deterministic metrics + human-calibrated semantic layer when ready |
| Safety | action policy/custody/idempotency/lease/fencing + negative tests |
| Failure behavior | provider/tool/evidence degradation campaigns |
| Stability | repeated-run metrics/campaigns |
| High-impact actions | proposal/confirmation/execution/uncertainty evidence |
| Experiment/hypothesis | frozen experiment packets/results + future decision records |
| Result analysis | quantitative reports + Eval/Provider UI |
| Limitations/risks | canonical non-claims + preserved negative outcomes/blockers |
| Reproducibility | clean-clone CI + lockfile + frozen evidence |
| Documentation | canonical docs + ADR/evidence index + operations runbook |
| Demonstration quality | normal Control Room + live architecture/trace/evidence/evaluation |

## 9. Project-quality extension evidence

| Project rule/goal | Evidence required before claim |
|---|---|
| USD0 | selected external path has USD0 actual/expected cash cost and no paid spillover |
| remote production | independent deployed frontend/API/store, no local serving dependency |
| multi-user IAM | USD0 standards-based auth + server-owned scope + tenant tests |
| protected delivery | branch protection + required CI + staging/prod smoke + rollback |
| production capacity | remote load/soak + latency/error/resource/quota distributions + SLO |
| durability/recovery | free selected backup/restore/failure campaigns + measured recovery window |
| semantic evaluator reliability | real human labels + agreement/error analysis |
| operational value | paired real MANUAL vs AGENT-ASSISTED measurements |
| model/provider selection | hosted USD0 controlled tournament or explicit `NO_SELECTION` |

## 10. Final presentation contract

Use the normal remote USD0 product path and show authenticated user/build health, real request, live architecture/trace, typed tool/policy/evidence transitions, safe terminal/action behavior, post-runtime evaluation, output lineage, quantitative explorer, production health, provider/operational-value evidence and exact limitations.

No separate demo-only or paid serving stack is compatible with the final project claim.
