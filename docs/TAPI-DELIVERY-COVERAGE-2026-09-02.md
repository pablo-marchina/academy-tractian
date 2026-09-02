# TAPI Delivery Coverage — Stack, Techniques, Frameworks and Final Outputs

**Checkpoint:** 2026-09-02  
**Project:** Academy × TRACTIAN — Engenharia e Avaliação de Agentes Industriais  
**Source:** TAPI `Engenharia e Avaliação de Agentes Industriais`  
**Delivery target:** 2026-09-08

This document makes explicit the technical choices and final outputs that were previously distributed across runtime/evaluation/observability issues. It is a prospective delivery plan; frozen historical ADRs/results remain authoritative for their exact scopes.

## 1. Declared TAPI track

The delivery combines both allowed TAPI tracks:

- **Track A — Agent construction:** governed industrial agent with typed tools over the TRACTIAN API, bounded planning/stopping, evidence-aware outcomes and read/action/escalation safety boundaries.
- **Track B — Agent evaluation framework:** scenario runner, metrics/evaluators, adversarial/failure/stability campaigns, trace capture/reproduction, provider comparison experiments and realtime trace-inspection application.

Research question instantiated for the project:

> How can a single-agent industrial support system use typed tools and evidence while remaining reliable under incomplete/conflicting/unavailable API responses, constrained actions and provider variability?

Primary experiment line:

1. establish a deterministic provider-free baseline and safety/evaluation harness;
2. compare live free-provider candidates under a frozen public packet (D01);
3. diagnose the observed exact-512-token output censoring with a single-variable 1024 completion-cap experiment (D02);
4. retain `NO_SELECTION` when hard quality/stability gates are not met;
5. preserve or change architecture only when a measured material gap supports it.

## 2. Final technical stack

### 2.1 Agent/runtime

| Layer | Choice | Role | Status |
|---|---|---|---|
| Language | Python >=3.11 | Main agent/runtime/evaluation implementation | Implemented |
| Schemas | Pydantic 2.x | Frozen typed inputs, tool contracts, decisions, traces, evaluator reports | Implemented |
| Agent orchestration | Custom `AgentController` | Single-agent tool/terminal decision loop, bounded turns/tool calls | Implemented |
| Execution boundary | `HarnessRunner` | Sole real tool execution boundary, trace capture and policy containment | Implemented |
| Tool contract | `ToolSpec` + JSON-schema-like parameter contracts | 18 canonical operations, argument validation, permissions | Implemented |
| API integration | Typed HTTP adapter/transport | TRACTIAN API requests/responses | Implemented |
| Action safety | B1/B2/B3-style deterministic gates + authorization/idempotency custody | Argument, policy, evidence/action safety | Implemented |
| Packaging | hatchling wheel | Clean standalone reproduction | Implemented |

**Why no LangGraph/LangChain/Pydantic AI:** TAPI lists them as suggested/equivalent orchestration choices, not mandatory dependencies. The custom controller is deliberately smaller, deterministic and already measured. Adding another orchestration framework without a material gap would add risk without evidence of benefit.

**Why no MCP in the main path:** TAPI accepts tools, MCP or equivalent. Native typed tools currently preserve stronger direct contracts and lower complexity for this API scope. MCP can be an evolution path, not a delivery requirement.

### 2.2 Model/provider

| Item | Choice/status |
|---|---|
| Route | Direct Cloudflare Workers AI |
| Candidate A | `@cf/zai-org/glm-4.7-flash` |
| Candidate B | `@cf/nvidia/nemotron-3-120b-a12b` |
| D01 | 32/32 live attempts; USD0; `NO_SELECTION`; 24/24 `CLIENT_FAILURE` at exactly 512 output tokens |
| D02 | Same packet/provider/prompt/schema, completion cap 1024 + sanitized failure subtype; live pending governed reset window |
| Production provider | Must remain evidence-driven; `NO_SELECTION` is valid |

Provider/model version, route, configuration, completion limits, resource accounting and known limitations must be visible in the final documentation and Quality & Provider frontend screen.

### 2.3 Evaluation/research

| Technique/framework | Role | Status |
|---|---|---|
| pytest | Unit/integration/regression tests | Implemented |
| Scenario runner | Controlled industrial cases | Implemented |
| Deterministic trace evaluator | Structural/safety/provenance validation | Implemented |
| Frozen public provider comparison | Controlled model behavior experiment | Implemented D01; D02 prepared |
| Repeated trials | Stability/signature repeatability | Implemented |
| Failure campaigns | Partial/inconclusive/conflict/unavailable/provider/tool failure behavior | Implemented |
| Adversarial/policy cases | Invalid arguments, blocked actions, evidence insufficiency | Implemented |
| Trace capture + replay/reproduction | Auditable executions | Implemented |
| Sanitized provider-call provenance | Provider/model/latency/outcome without raw prompt/response | Implemented |
| Human escalation handoff validation | Safe operational escalation output | Implemented |

TAPI analysis objects explicitly covered:

1. function/tool selection;
2. argument accuracy;
3. execution trajectory;
4. evidence use;
5. response quality;
6. safety;
7. failure behavior;
8. stability between executions;
9. high-impact-action behavior.

### 2.4 Realtime observability backend

| Layer | Choice | Role | Delivery status |
|---|---|---|---|
| Safe telemetry projection | New typed Python/Pydantic models | Convert raw runtime trace to browser-safe observability records | P0 planned (#121) |
| Event sink | `ObservabilityEventSink` protocol | Fail-isolated live event publication boundary | P0 planned (#124) |
| Service/API | FastAPI stable 0.140.x line | Read-only telemetry/query endpoints + SSE | P0 planned |
| Realtime transport | Server-Sent Events | Genuine live run updates, reconnect/cursor catch-up | P0 planned |
| Analytics store | DuckDB stable 1.5.5 | Local USD0 analytical persistence/query | P0 planned |
| Export | Sanitized JSONL/Parquet where useful | Reproduction/offline analysis | Planned |
| Multi-instance adapter | Redis Streams or equivalent behind sink | Optional scale-out only if configured/tested | Conditional, not claimed by default |

Raw `RunTrace` is never served directly to the browser. Identity, user id, seed, credentials, auth headers, raw provider material, forbidden raw tool/observation bodies and evaluator-private truth remain outside the frontend boundary.

### 2.5 Frontend/data visualization

Target stable frontend baseline (versions must be frozen in the lockfile at scaffold time):

| Layer | Choice | Role |
|---|---|---|
| UI language | TypeScript | Frontend type safety |
| UI framework | React 19.2 stable line | Application/component model |
| Build/dev | Vite 8.1 stable line | Fast local build/dev server |
| Server state | TanStack Query 5.x | REST cache/loading/error/refetch |
| Live state | Idempotent event reducer/store | SSE event application by event id/cursor |
| Analytics visualization | Apache ECharts 6.1 | Dynamic charts, datasets, live updates |
| Trace/architecture graph | `@xyflow/react` / React Flow 12.11 | Interactive execution + architecture topology |
| Styling | Lightweight local CSS/component primitives | Presentation-grade control room without hosted dependency |

Frontend is intentionally richer than TAPI's Streamlit/Gradio examples because the TAPI leaves delivery format open and explicitly values trace inspection and demonstration quality.

### 2.6 Frontend/contract QA

| Tool/technique | Role | Target |
|---|---|---|
| Vitest 4.1 stable line | Frontend unit/component logic | P0 |
| Testing Library | User-facing component behavior | P0 |
| Playwright 1.62 stable line | E2E/browser/realtime/reconnect tests | P0 |
| FastAPI/Pydantic contract tests | API schema/sanitization | P0 |
| pytest | Backend/runtime/observability regression | P0 |
| Clean frontend build gate | Reproducible UI artifact | P0 |
| Security field-deny tests | Prove private fields cannot cross API/SSE | P0 |
| Reconnect/idempotency tests | Realtime correctness | P0 |
| Presentation viewport tests | Demo quality | P1 |

## 3. Agent techniques used

The plan must name techniques independently of library choice.

### T1 — Tool-augmented iterative agent loop

A bounded observation/action loop structurally inspired by tool-using agent patterns: model decision -> typed tool proposal -> deterministic validation/policy -> observation -> next decision or terminal outcome. Do **not** claim hidden chain-of-thought or literal ReAct prompting unless implemented and measured.

### T2 — Typed function/tool calling

- canonical typed tool registry;
- strict argument schemas;
- deterministic argument validation;
- identity/seed binding outside model control;
- no arbitrary HTTP construction by the model.

### T3 — Evidence-aware decision policy

The agent must distinguish:

- contextualize/orient;
- investigate with tools;
- ask clarification;
- abstain safely;
- escalate to a human;
- propose/execute an action only through deterministic safety gates.

### T4 — Bounded planning and stopping

- maximum turns;
- maximum tool calls;
- no hidden retry/fallback on governed paths;
- safe abstention on exhausted/failing boundaries.

### T5 — Fail-closed action safety

- B1 argument/schema validation;
- B2 permission/resource policy;
- B3 evidence/authorization where applicable;
- justification requirements;
- idempotency/no-replay custody for consequential actions.

### T6 — Evidence/provenance tracing

Every meaningful execution transition is represented as an ordered trace event; provider-call metadata is sanitized and hash/provenance oriented. Final UI exposes safe evidence lineage without exposing chain-of-thought.

### T7 — Robustness under probabilistic API behavior

Explicitly test TAPI response modes:

- complete;
- partial;
- inconclusive;
- conflict;
- unavailable.

### T8 — Repeated-execution stability

Repeat public units, compare terminal/tool signatures and quantify consistency rather than judging one favorable sample.

### T9 — Controlled provider/model experimentation

Frozen packet, same units/repeats/config, explicit hard gates, resource/cost accounting, Pareto/`NO_SELECTION` outcome. D02 changes one measured variable after D01 censoring evidence.

### T10 — Trace-only deterministic evaluation + separated semantic experiments

Production evaluator consumes only runtime trace-visible structural/safety evidence. Evaluator-private/gold information never enters runtime/model input. Semantic/provider quality experiments remain explicitly separated.

### T11 — Realtime event-sourcing-style observability projection

Runtime trace events are append-only operational truth; safe projected events are persisted and streamed. Reconnect performs cursor-based catch-up. Browser reducers are idempotent.

### T12 — Schema-driven dynamic visualization

Allow-listed telemetry schema describes field type, semantic role, units and valid aggregations. The explorer chooses/validates visual grammar deterministically rather than allowing arbitrary SQL/private-schema guessing.

## 4. Frameworks/tools explicitly not used in the delivery critical path

| Technology | Decision | Reason |
|---|---|---|
| LangGraph | NO_CHANGE / not used | Current single-agent controller covers measured needs; no proven topology gap |
| LangChain | Not used | Adds abstraction without measured benefit to typed bounded path |
| Pydantic AI | Not used as orchestrator | Pydantic schemas already used directly; custom controller retained |
| MCP SDK | Not used on main path | Native typed tools are an accepted equivalent and simpler for supplied API |
| RAG/vector/hybrid/reranking | Not used | TAPI says optional; no demonstrated knowledge-retrieval gap in current public cases |
| Persistent agent memory | Not used | No measured requirement; risks state leakage/reproducibility |
| Grafana/Phoenix/Langfuse | Not primary UI | Native control room is delivery-critical; optional export/benchmark later |
| Redis Streams | Conditional | Only required to claim horizontal multi-instance realtime; single-process delivery can use in-process sink + durable telemetry |
| Streamlit/Gradio | Not used | React control room better satisfies realtime, drill-down, trace topology and dynamic visualization requirements |

Absence of these frameworks is an evidence-backed scope decision, not an omission.

## 5. Final product outputs

### O1 — Functional industrial agent

Executable agent path that accepts a user support request and can:

- contextualize/orient;
- investigate assets/analyses/data/model/knowledge through typed TRACTIAN tools;
- ask clarification;
- abstain;
- escalate with structured handoff;
- contain unsafe/unauthorized actions;
- execute only explicitly authorized supplied/test actions where the existing controlled path permits.

### O2 — Typed TRACTIAN integration package

- 18-operation canonical tool registry;
- HTTP adapter/transport;
- strict schemas;
- response normalization;
- action-policy integration;
- reproducible standalone wheel.

### O3 — Agent evaluation framework

- scenario runner;
- metric/evaluator library;
- trace validators;
- failure/adversarial/stability campaigns;
- provider comparison harness;
- reproducible frozen results/evidence.

### O4 — Governed experiment reports

At minimum final documentation must summarize:

- provider-free baseline evidence;
- D01 design/result and limitations;
- D01 exact-512-token censoring diagnosis;
- D02 hypothesis/design/result when executed;
- provider selection or `NO_SELECTION` justification;
- latency/resource/cost findings;
- architecture materiality decision.

### O5 — Realtime Observability Control Room

Screens:

1. Mission Control;
2. Live Runs;
3. Run Explorer;
4. Trace Timeline / Waterfall;
5. Trace Graph;
6. Tools & Policy;
7. Quality & Providers;
8. Dynamic Data Explorer;
9. Architecture Explorer / Explain This Run.

### O6 — Architecture Explorer

Interactive implementation-backed diagram showing:

`request -> runtime -> decision source/provider -> controller -> runner -> tools -> policy/action gates -> TRACTIAN API -> observations -> terminal output -> trace -> evaluator -> observability -> frontend`

Selected runs highlight the exact active path.

### O7 — Per-run output lineage

Every safe output is labeled by producer:

- `MODEL`;
- `CONTROLLER`;
- `POLICY`;
- `TOOL`;
- `OBSERVATION`;
- `EVALUATOR`;
- `SYSTEM`.

UI answers: what happened, which component produced it, what safe evidence fed it, what happened next and what became terminal output. No hidden chain-of-thought.

### O8 — Dynamic Data Explorer

User-selectable safe dataset/dimensions/measures/filters/aggregations with deterministic chart compatibility and drill-down to underlying run/event evidence.

### O9 — Realtime production telemetry

- safe runtime event stream;
- SSE updates;
- event ids/cursors;
- persisted catch-up;
- explicit `LIVE`, `RECONNECTING`, `CAUGHT_UP`, `HISTORICAL` states;
- live trace graph/timeline/counters;
- fail-isolated slow-client behavior.

### O10 — Technical documentation/reproduction package

README and docs must explicitly cover TAPI-required common documentation:

- problem;
- declared combined track/scope;
- architecture;
- installation/execution;
- full stack/framework matrix;
- model/version/configuration;
- agent techniques;
- experimental methodology;
- results;
- limitations/risks;
- evolution opportunities;
- demo/reproduction runbook.

## 6. TAPI requirement-to-evidence map

| TAPI expectation | Planned/final evidence |
|---|---|
| API integration quality | typed 18-tool registry + HTTP adapter + contract tests |
| Functional agent | ProductionRuntime + AgentController demo/live path |
| Function selection | scenario/provider metrics + run traces |
| Argument accuracy | B1 schema validation + metrics/tests |
| Execution trajectory | RunTrace + Trace Graph/Timeline |
| Evidence use | observation/evidence lineage + abstain/escalate cases |
| Response quality | public experiment rubric/provider metrics |
| Safety | action policy, permissions, idempotency, containment campaigns |
| Failure behavior | partial/inconclusive/conflict/unavailable/provider/tool campaigns |
| Stability | repeated-run signature/stability metrics |
| High-impact actions | supplied/test controlled action evidence + policy blocks |
| Experiment/hypothesis | D01/D02 preregistration/results + architecture materiality protocol |
| Result analysis | experiment reports + Quality & Provider UI |
| Limitations/risks | explicit bounded claims/NO_SELECTION/external blockers |
| Reproducibility | clean wheel + provider-free reproduction + lockfiles/tests |
| Documentation | README + ADRs + this coverage matrix + runbooks |
| Demonstration quality | realtime control room + trace/architecture/output lineage + dynamic explorer |

## 7. Final demo outputs to show live

The final demonstration should deliberately show, rather than merely mention:

1. a real support request entering the runtime;
2. live architecture path activation;
3. model-call metadata and structured decision;
4. typed tool proposal;
5. validation/policy result;
6. TRACTIAN API call metadata;
7. safe observation/evidence reference;
8. subsequent decision;
9. one terminal success/orientation;
10. one clarification/abstention/failure path;
11. one escalation + structured human handoff;
12. one blocked high-impact action or controlled authorized action example;
13. trace timeline/graph and per-output lineage;
14. evaluator results appearing only after runtime completion;
15. D01/D02 provider experiment comparison;
16. dynamic data explorer interaction over safe telemetry;
17. realtime disconnect/reconnect/catch-up if presentation time permits;
18. exact limitations and provider-selection state.

## 8. Delivery order

```text
#119 safe observability/realtime/explanation matrix
→ #121 telemetry read model/API/persistence
→ #124 realtime runtime event sink + SSE/reconnect
→ #122 Mission Control / Live Runs / Run Explorer / Trace views
→ #125 Architecture Explorer + Output Lineage
→ #123 Dynamic Data Explorer + Quality/Provider/Tools/Policy visualizations
→ #114 integrated E2E/security/realtime/front acceptance
→ hard visual/feature freeze
→ clean reproduction / documentation / final rehearsal
```

D02 (#117) remains parallel and must not block provider-free frontend implementation/testing.

## 9. Definition of done against TAPI

The project is not considered delivery-complete merely because the runtime and tests pass. Before final delivery, the repository must make it straightforward for a reviewer to identify:

- the exact declared TAPI track(s);
- the exact stack and framework choices;
- the exact model/provider/configuration;
- the agent techniques used;
- the experiment hypothesis and controls;
- quantitative and qualitative results;
- all final executable/product/documentation outputs;
- limitations and consciously rejected optional technologies;
- a reproducible run path;
- a realtime, inspectable demonstration connecting request -> tools/API -> outcome -> trace/evaluation.
