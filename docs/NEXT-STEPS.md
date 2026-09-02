# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / FINAL SPRINT  
**Checkpoint:** 2026-09-02 — D01 complete; D02 provider-free ready; realtime observability/control-room delivery is P0  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**TAPI stack/techniques/outputs:** [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md)  
**Final output inventory:** [`FINAL-DELIVERY-OUTPUT-INVENTORY-2026-09-02.md`](FINAL-DELIVERY-OUTPUT-INVENTORY-2026-09-02.md)  
**Realtime/frontend acceptance:** GitHub issues #114, #119, #121, #122, #123, #124, #125  
**D02 live execution:** GitHub issue #117

This is the short-horizon execution plan. It does not authorize provider inference by itself.

## 1. Declared academic scope

The project combines both TAPI tracks:

```text
Track A  functional industrial agent + typed TRACTIAN tools
Track B  evaluation framework + trace inspection + robustness/stability experiments
```

The final delivery must make the exact stack, techniques, framework choices, model/provider configurations and executable outputs visible rather than leaving them implicit in code/ADRs.

## 2. Critical stack to deliver

```text
AGENT/RUNTIME
Python >=3.11
Pydantic 2.x
custom AgentController
HarnessRunner
ToolSpec / typed schemas
TRACTIAN HTTP adapter
B1/B2/B3-style deterministic safety/action boundaries

MODEL/PROVIDER
Cloudflare Workers AI
GLM 4.7 Flash
Nemotron 3 120B A12B
D01 + D02 controlled comparison

EVALUATION
pytest
scenario runner
trace-only deterministic evaluator
failure/adversarial/stability campaigns
provider comparison harness
trace capture/reproduction

OBSERVABILITY
safe telemetry projection
ObservabilityEventSink
FastAPI
SSE
DuckDB
optional stream adapter only when multi-instance behavior is actually tested

FRONTEND
TypeScript
React 19.2 stable line
Vite 8.1 stable line
TanStack Query 5.x
Apache ECharts 6.1
React Flow 12.11

FRONTEND QA
Vitest 4.1 stable line
Testing Library
Playwright 1.62 stable line
API/SSE contract tests
clean build + E2E + security/reconnect gates
```

Exact frontend dependency versions must be frozen in the lockfile when scaffolded. Stable releases are preferred over beta/alpha dependencies.

## 3. Named agent/evaluation techniques

The final documentation/demo must explicitly name and evidence:

1. bounded tool-augmented iterative agent loop;
2. typed function/tool calling;
3. evidence-aware orient/investigate/clarify/abstain/escalate/action policy;
4. bounded planning and stopping;
5. fail-closed argument/permission/evidence action safety;
6. evidence/provenance tracing;
7. robustness to complete/partial/inconclusive/conflict/unavailable API behavior;
8. repeated-execution stability measurement;
9. frozen controlled provider/model experimentation;
10. trace-only deterministic evaluation with evaluator isolation;
11. realtime append-only safe observability projection and reconnect/catch-up;
12. schema-driven dynamic data visualization.

Do not claim hidden chain-of-thought or literal ReAct prompting unless such prompting is explicitly implemented and tested. The architecture is structurally tool-observation iterative but its evidence is the actual controller/trace behavior.

## 4. Framework decisions that must be explained

```text
LangGraph      not used: no measured topology gap
LangChain      not used: unnecessary abstraction for current typed path
Pydantic AI    not used as orchestrator: direct Pydantic + custom controller retained
MCP            not main path: native typed tools are an accepted equivalent
RAG            not used: no demonstrated retrieval gap
Memory         not used: no measured requirement; reproducibility/state risk
Streamlit      not used: realtime control-room requirements exceed demo-only UI
Grafana/Phoenix/Langfuse optional only: native product UI is delivery-critical
Redis Streams conditional: required only if claiming tested multi-instance realtime
```

Absence is a scoped technical decision, not an undocumented omission.

## 5. D01 / D02

D01 facts:

```text
attempts                  32 / 32 completed
cash cost                 USD 0.00
observed Neurons          2813.628464
selection                 NO_SELECTION
CLIENT_FAILURE            24 / 24 at exact 512 output tokens
```

D02 changes only the completion cap (512 -> 1024) plus sanitized failure subtypes while holding packet/provider/prompt/schema/evaluator geometry constant. Execute #117 only after a fresh eligible Workers AI reset/authorization. `NO_SELECTION` remains a valid result.

## 6. Build order

```text
#119 safe observability/realtime/explanation matrix
→ #121 telemetry read model/API/persistence
→ #124 runtime event sink + SSE/reconnect/catch-up
→ #122 Mission Control / Live Runs / Run Explorer / Trace views
→ #125 Architecture Explorer + Explain This Run / Output Lineage
→ #123 Dynamic Data Explorer + Quality/Provider + Tools/Policy
→ #114 integrated E2E/security/realtime/frontend acceptance
→ hard visual/feature freeze
→ clean reproduction + README/runbook + final rehearsal
```

D02 runs in parallel and must not block provider-free frontend implementation/testing.

## 7. Final executable/product outputs

The final delivery is expected to contain:

```text
O1  functional industrial agent
O2  typed TRACTIAN integration package
O3  evaluation framework
O4  governed D01/D02 experiment package
O5  realtime Observability Control Room
O6  Architecture Explorer
O7  per-run Output Lineage / Explain This Run
O8  schema-driven Dynamic Data Explorer
O9  realtime production telemetry + reconnect/catch-up
O10 complete technical documentation/reproduction package
```

The final output inventory document is the completion checklist. A runtime-only deliverable is not sufficient.

## 8. Required frontend areas

```text
Mission Control
Live Runs
Run Explorer
Trace Timeline / Waterfall
Trace Graph
Tools & Policy
Quality & Providers
Dynamic Data Explorer
Architecture Explorer
Explain This Run / Output Lineage
```

Every KPI/graph/output must drill down to safe run/event evidence where applicable.

## 9. Realtime requirements

- genuine emitted runtime events only;
- no fake thinking/progress animations;
- persistent sanitized events before/with publication;
- SSE event id/cursor;
- reconnect + persisted catch-up;
- idempotent browser reducer;
- slow/disconnected browser cannot block runtime;
- terminal state only from genuine terminal evidence;
- browser never receives raw RunTrace/private material.

## 10. Architecture/output explanation requirements

For every selected run, the UI must answer:

```text
what happened?
which component produced it?
which safe evidence/input fed it?
what output was produced?
what component consumed it next?
what became the terminal result?
what evaluation happened only after runtime completion?
```

Every output is labeled `MODEL`, `CONTROLLER`, `POLICY`, `TOOL`, `OBSERVATION`, `EVALUATOR` or `SYSTEM`.

## 11. Testing schedule

```text
2026-09-02  contracts + observability/realtime foundation + D02 after eligible reset
2026-09-03  telemetry API/realtime stream + core control room
2026-09-04  architecture/output lineage + dynamic visualization + feature completion
2026-09-05  dedicated integrated frontend/realtime/security test + fixes; HARD FREEZE EOD
2026-09-06  clean reproduction + full acceptance + final README/runbook
2026-09-07  exact demo rehearsal + contingency
2026-09-08  delivery; smoke check only, no same-day feature development
```

## 12. TAPI completion gate

Before final delivery, a reviewer must be able to identify from README/UI/docs:

- declared combined TAPI tracks;
- API integration and tool contracts;
- exact agent/framework architecture;
- exact stack and frozen versions;
- provider/model/configuration;
- named techniques and why they were used;
- experiment hypothesis, controls, metrics and results;
- failure/stability/high-impact-action evidence;
- final product/executable outputs;
- limitations and rejected optional frameworks;
- clean reproduction;
- realtime request -> tool/API -> output -> trace/evaluation demonstration.

Do not mark the project complete merely because backend tests pass.
