# TAPI Delivery Coverage — Current Crosswalk

**Status:** ACTIVE TAPI/output crosswalk  
**Original filename checkpoint:** 2026-09-02  
**Current rebaseline:** 2026-09-05  
**Project:** Academy × TRACTIAN — Engenharia e Avaliação de Agentes Industriais  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This document maps the audited TAPI/delivered-package expectations to the current product. It deliberately separates **assignment requirements** from **project-added production-quality gates** so the repository does not misrepresent an internal engineering choice as a TAPI mandate.

## 1. Audited scope interpretation

The project delivers one integrated solution containing:

- **Industrial Agent** — typed TRACTIAN API/tool use, evidence-aware investigation, bounded decisions, clarification/abstention/escalation and governed actions.
- **Agent Evaluation Framework** — scenario execution, trace/trajectory evaluation, tool/argument/evidence/safety/failure/stability analysis and controlled experiments.

The operational support modes remain:

```text
CONTEXTUALIZE
INVESTIGATE
EXECUTE
```

The product-level outcomes remain:

```text
FINAL / ORIENT
CLARIFY
ABSTAIN
ESCALATE
ACTION_PROPOSAL / CONFIRMED_ACTION
```

## 2. What is TAPI/delivered-package driven

The current crosswalk treats the following as assignment/delivery obligations or direct quality dimensions:

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

## 3. Project-added production-quality gates

The following are **stronger internal acceptance gates chosen for this project**. They improve the final delivery but must not be cited as though the TAPI explicitly mandated the exact implementation:

- remote production deployment;
- no local serving dependency in production;
- multi-user product behavior;
- standards-based end-user IAM;
- PostgreSQL RLS tenant isolation;
- protected CI/CD and tested rollback;
- remote load/soak and evidence-based SLOs;
- backup/restore and measured recovery evidence;
- human calibration before semantic-judge promotion;
- paired operational-value measurement;
- live architecture/trace/evidence/health visualization;
- systematic research/Pareto decision records for material choices.

These gates exist because the project target is production-quality, evidence-driven engineering rather than a demo-only implementation.

## 4. Current technical stack

### 4.1 Agent/runtime

| Layer | Current choice | State |
|---|---|---|
| Language | Python >=3.11 | implemented |
| Typed schemas | Pydantic 2.x | implemented |
| API/product service | FastAPI + Uvicorn | implemented |
| Agent orchestration | custom `AgentController` | promoted baseline |
| Tool execution | `HarnessRunner` | hard execution boundary |
| Tool contract | typed `ToolSpec` registry | 18 operations |
| TRACTIAN integration | typed HTTP transport/normalization | implemented |
| Action safety | deterministic validation/policy + custody/idempotency/leases/fencing | implemented |
| Durable serving state | PostgreSQL + psycopg | promoted |
| Packaging | hatchling/wheel | clean-clone proved |

**Why no automatic LangGraph/LangChain/Pydantic-AI migration:** the current controller/tool boundary already covers the measured requirements. A framework change is a challenger only after a material gap is measured.

**Why no MCP in the main path:** the delivered API is already represented by typed tools. MCP remains optional for a future interoperability requirement.

### 4.2 Model/provider

Historical Cloudflare D01/D02 experiments are complete and preserved as research evidence.

Current result:

```text
production provider/model = NO_SELECTION
```

The Cloudflare route is **not** the promoted production provider merely because its historical experiment implementation remains in the repository.

The current production rebaseline requires any future production model candidate to be remotely hosted and evaluated through a new controlled provider/model tournament. Local model serving is not a production candidate under the no-local-serving requirement.

### 4.3 Evaluation

| Capability | State |
|---|---|
| pytest unit/integration/regression | implemented |
| scenario runner | implemented |
| deterministic structural/safety/trajectory evaluator | implemented |
| failure/adversarial/stability campaigns | implemented |
| trace capture/reproduction | implemented |
| provider/model experiment machinery | implemented/historical D01-D02 complete |
| human semantic-review collection/protocol | implemented |
| real human semantic calibration | not ready — labels required |
| operational-value collection/paired analysis | implemented |
| real human operational-value claim | not ready — observations required |
| adaptive-stopping replay diagnostic | evaluator-only; not runtime-promoted |

The evaluator is isolated from runtime/model context. Gold/private evaluator truth cannot become model input.

### 4.4 Realtime observability

| Layer | Current choice | State |
|---|---|---|
| Safe telemetry projection | typed Python/Pydantic projection | implemented |
| Durable event/run/evidence/eval store | PostgreSQL | implemented/promoted |
| Service/API | FastAPI | implemented |
| Realtime transport | SSE | implemented |
| Wake-up | PostgreSQL LISTEN/NOTIFY | promoted wake-up only |
| Correctness source | PostgreSQL rows + sequence cursor | promoted |
| Cross-replica read-only handoff | PostgreSQL lease/generation fencing | implemented/tested |

DuckDB is **not** the production observability/read-model truth. It remains optional development/benchmark compatibility only.

### 4.5 Frontend

| Layer | Current choice | State |
|---|---|---|
| UI | React 19 + TypeScript | implemented |
| Build | Vite | implemented |
| Server state | TanStack Query | implemented |
| Analytics | Apache ECharts | implemented |
| Trace/architecture graph | React Flow / `@xyflow/react` | implemented |
| Unit/component tests | Vitest | implemented |
| Browser acceptance | Playwright | implemented/gated |
| Dependency lock | `frontend/package-lock.json` + `npm ci` | implemented/gated |

The React control room is a project choice to maximize realtime inspection, drill-down and visualization quality; Streamlit/Gradio are examples/alternatives, not required formats.

## 5. Agent techniques

### T1 — Typed tool-augmented iterative loop

```text
decision
→ optional typed tool proposal
→ deterministic validation/policy
→ execution
→ normalized evidence
→ next decision / terminal outcome
```

No hidden chain-of-thought claim is made.

### T2 — Typed function/tool calling

- canonical 18-tool registry;
- strict schemas;
- deterministic argument validation;
- identity/tenant/evaluator seed outside model control;
- no arbitrary model-authored HTTP requests.

### T3 — Evidence-aware outcomes

The controller explicitly supports orient/final, investigate, clarify, abstain, escalate and bounded action proposal.

### T4 — Bounded planning/stopping

- hard turn/tool ceilings;
- conservative failure behavior;
- no uncontrolled provider retries/fallbacks on governed paths.

### T5 — Fail-closed action safety

- schema/argument validation;
- permission/resource/action policy;
- evidence/authorization gates where applicable;
- private custody;
- explicit confirmation;
- persistent idempotency;
- non-transferable execution lease/generation fencing;
- lost ownership → `UNCERTAIN`, no blind replay.

### T6 — Evidence/provenance tracing

Ordered safe trace/event/evidence lineage supports evaluation and frontend explanation without exposing private raw traces or chain-of-thought.

### T7 — Robustness to probabilistic/degraded evidence

Explicitly evaluate complete, partial, inconclusive, conflicting and unavailable evidence plus tool/provider failures.

### T8 — Repeated-execution stability

Use repeated runs and sliced distributions/signatures rather than one favorable sample.

### T9 — Controlled provider/model experimentation

Frozen workload/config, explicit hard gates, resource/cost accounting and Pareto/`NO_SELECTION` semantics.

### T10 — Deterministic-first evaluation + calibrated semantic layer

Use exact deterministic truth wherever available. Semantic judgment is separate and cannot gate promotion until human calibration exists.

### T11 — Durable realtime observability

Persist safe events first; use wake-up + cursor catch-up; apply idempotently in the browser.

### T12 — Schema-driven quantitative visualization

Allow-listed safe data/fields/aggregations drive charts and drill-down; browser SQL/private-schema guessing is not permitted.

### T13 — Evaluation-driven engineering

Material changes follow baseline → preregistered challenger → controlled quantitative evaluation → Pareto decision → regression.

## 6. Frameworks/components not currently promoted

| Technology | Current decision | Reason |
|---|---|---|
| LangGraph | NO_CHANGE / qualified historical challenger | no measured controller/HITL gap requiring migration |
| LangChain | not used | no measured benefit over current typed boundary |
| Pydantic AI orchestration | not used | Pydantic schemas are used directly; no orchestration gap |
| MCP | NO_CHANGE | no measured interoperability requirement |
| RAG/vector/hybrid/reranking | NO_CHANGE | no demonstrated retrieval gap in current TAPI path |
| Persistent agent memory | NO_CHANGE | no demonstrated cross-request need; leakage/staleness risk |
| Multi-agent | NO_CHANGE | no measured topology/specialization gap |
| Redis/Kafka/shared event bus | NO_CHANGE | PostgreSQL durable rows + wake-up currently satisfy tested semantics; add only after measured scale gap |
| Kubernetes/microservices | NO_CHANGE | no measured deployment/topology need yet |

Absence is a scope/decision outcome, not an omission.

## 7. Final product outputs

### O1 — Functional industrial agent

Integrated agent for contextualization, investigation, clarification, abstention, escalation and governed action behavior.

### O2 — Typed TRACTIAN integration package

18-operation tool registry, typed schemas, transport/normalization, policy integration and reproducible package.

### O3 — Agent evaluation framework

Scenario runner, deterministic metrics/evaluators, trace validation, failure/stability/action campaigns and EDD comparisons.

### O4 — Governed technical experiment evidence

Historical D01/D02 plus subsequent material architecture/model/provider experiments, with hypotheses, controls, quantitative results, limitations and negative decisions preserved.

### O5 — Realtime Production Control Room

Live operational screens for active runs, trace/timeline, evidence, policy/tools, evaluation, provider/model evidence and production health.

### O6 — Architecture Explorer

Implementation-backed graph of the real active request/runtime/tool/evaluation/observability path, highlighting selected-run participation.

### O7 — Output Lineage / Explain This Run

Safe output provenance using producer categories such as `MODEL`, `CONTROLLER`, `POLICY`, `TOOL`, `OBSERVATION`, `EVALUATOR`, `SYSTEM`.

### O8 — Dynamic Data Explorer

Allow-listed datasets/dimensions/measures/filters/aggregations with deterministic chart compatibility and source-record drill-down.

### O9 — Realtime production telemetry

Durable safe events/cursors, SSE delivery, reconnect/catch-up and explicit connection/degraded states.

### O10 — Technical documentation and reproduction package

Canonical state/plan/architecture/acceptance/runbook/ADRs/research evidence plus local/CI reproduction and, once built, remote production operations/rollback instructions.

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
| Safety | deterministic action policy/custody/idempotency/lease/fencing + negative tests |
| Failure behavior | provider/tool/evidence degradation campaigns |
| Stability | repeated-run metrics/campaigns |
| High-impact actions | proposal/confirmation/execution/uncertainty evidence |
| Experiment/hypothesis | frozen experiment packets/results + future decision records |
| Result analysis | quantitative reports + Eval/Provider UI |
| Limitations/risks | canonical non-claims + preserved negative outcomes/blockers |
| Reproducibility | clean-clone CI + lockfile + frozen evidence |
| Documentation | canonical docs + ADR/evidence index + operations runbook |
| Demonstration quality | normal product Control Room + live architecture/trace/evidence/evaluation |

## 9. Production-quality extension evidence

These rows are project-added gates, not assertions of exact TAPI wording:

| Project quality goal | Required evidence before claim |
|---|---|
| remote production | independently reachable deployed frontend/API/DB, no local serving dependency |
| multi-user IAM | standards-based auth + server-owned scope + cross-user/tenant tests |
| protected delivery | branch protection + required CI + staging/prod smoke + rollback |
| production capacity | remote load/soak + latency/error/resource distributions + SLO |
| durability/recovery | backup/restore/failover campaigns + measured recovery/data-loss window |
| semantic evaluator reliability | real human labels + agreement/error analysis |
| operational value | paired real MANUAL vs AGENT-ASSISTED measurements |
| model/provider selection | new hosted-candidate controlled tournament or explicit `NO_SELECTION` |

## 10. Final live presentation contract

The strongest final presentation uses the normal deployed product path and shows:

1. authenticated remote user + build/health identity;
2. real support request;
3. live architecture/trace activation;
4. typed tool and deterministic policy transition;
5. safe evidence;
6. final/clarify/abstain/escalate behavior;
7. governed action proposal/confirmation in an authorized safe profile;
8. post-runtime evaluation;
9. output lineage and quantitative explorer;
10. production health;
11. model/provider and operational-value evidence states;
12. exact limitations/non-claims.

No separate demo-only runtime is required or allowed for the final production claim.

## 11. Definition of done against TAPI + project quality target

A reviewer should be able to identify without reconstructing repository history:

- the exact integrated Agent + Evaluation scope;
- the real current architecture and stack;
- the model/provider state, including `NO_SELECTION` when applicable;
- the techniques used and optional technologies consciously rejected;
- experiment hypotheses/controls/results;
- quantitative and semantic evidence boundaries;
- final executable/frontend/documentation outputs;
- limitations/non-claims;
- a clean reproducible repository path;
- the remotely deployed production path when completed;
- live request → tool/API → evidence → outcome → trace → evaluation → frontend lineage.

The complete production Definition of Done lives in [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md); this file remains the TAPI/output crosswalk.
