# Academy × TRACTIAN — Unified Delivery Plan

**Status:** ACTIVE / canonical execution plan  
**Checkpoint:** 2026-09-02  
**Final delivery:** 2026-09-08  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This document replaces the previous split responsibilities of `PROJECT-PLAN.md`, `NEXT-STEPS.md` and `ARCHITECTURE-ROADMAP.md` for active scheduling/prioritization. Those paths are compatibility shims only.

## 1. Delivery objective

Maximize final TAPI coverage and evidence quality under:

```text
external API / hosted-service project cost   USD 0
paid spillover                               FORBIDDEN
final delivery                               2026-09-08
```

Critical paths:

1. governed D02 provider diagnosis;
2. safe realtime observability substrate;
3. realtime control-room frontend;
4. architecture/output explanation;
5. dynamic data visualization;
6. integrated frontend/realtime/security testing;
7. clean final reproduction/documentation/demo.

## 2. Priority rules

### P0

- required TAPI agent/evaluation behavior;
- trustworthy evidence/integrity;
- D02 result or bounded `NO_SELECTION`;
- realtime control room;
- safe browser telemetry boundary;
- architecture/output lineage;
- dynamic visualization required for final demo;
- final reproduction/test/freeze.

### P1

- presentation quality;
- performance/a11y improvements;
- reusable exports/secondary analytics;
- production-scale adapter only when necessary to support a claim.

### Not on critical path without new evidence

- LangGraph;
- multi-agent decomposition;
- LangChain/Pydantic AI orchestration migration;
- MCP migration;
- RAG/vector/hybrid/reranking;
- persistent memory;
- adaptive routing;
- Grafana/Phoenix/Langfuse as primary UI.

## 3. Workstream order

```text
#119 safe observability/realtime/output contract
        ↓
#121 safe projection + persistence + read API
        ↓
#124 runtime event sink + SSE/reconnect
        ↓
#122 control-room frontend
        ↓
#125 architecture explorer + output lineage
        ↓
#123 dynamic data explorer
        ↓
#114 integrated E2E/security/visual acceptance
        ↓
HARD FEATURE + VISUAL FREEZE
```

D02 (#117) proceeds independently after an eligible fresh reset/authorization and must not block provider-free frontend development.

## 4. 2026-09-02 — contracts/foundation + D02 after reset

Before D02:

- freeze safe telemetry schema and browser deny-list;
- define `ObservabilityEvent` and sink semantics;
- define architecture manifest and output-origin vocabulary;
- scaffold FastAPI/DuckDB observability package;
- scaffold React/TypeScript/Vite frontend;
- implement safe provider-free telemetry fixtures/path;
- freeze actual frontend dependency versions in lockfile;
- keep provider credentials absent until governed D02 authorization.

After the Workers AI UTC reset, execute D02 exactly once only if fresh zero-use evidence and receipt are valid. No replay of claimed/uncertain attempts.

## 5. 2026-09-03 — realtime telemetry + core control room

Backend:

- safe `RunTrace`/event projection;
- DuckDB persistence;
- overview/runs/events/tools/policy/provider/evaluation endpoints;
- SSE stream with event ids;
- reconnect/catch-up;
- bounded slow-consumer behavior;
- sanitizer/ordering/idempotency tests.

Frontend:

- Mission Control;
- Live Runs;
- Run Explorer;
- run detail;
- live timeline;
- trace graph;
- connection states `LIVE / RECONNECTING / CAUGHT_UP / HISTORICAL`.

D02:

- analyze result versus D01;
- apply frozen hard-gate/Pareto rules;
- integrate selected/bounded provider state into UI;
- retain `NO_SELECTION` if necessary.

## 6. 2026-09-04 — explanation + dynamic visualization

Implement:

- global Architecture Explorer;
- architecture manifest/version/config display;
- selected-run active architecture path;
- `Explain this run` / output lineage;
- origin labels `MODEL / CONTROLLER / POLICY / TOOL / OBSERVATION / EVALUATOR / SYSTEM`;
- Tools & Policy screen;
- Quality & Providers screen;
- Dynamic Data Explorer;
- global filters and drill-down;
- ECharts line/bar/scatter/heatmap/histogram/table grammar;
- D01/D02 attempt matrix/token-cap/Neuron views;
- loading/empty/error/partial/inconclusive states;
- responsive presentation pass.

No new architecture framework is introduced merely for polish.

## 7. 2026-09-05 — dedicated integrated test/fix day

Run the complete acceptance matrix:

- success/orient;
- clarification;
- abstention;
- escalation/handoff;
- policy/action blocked;
- tool/provider failure;
- partial/inconclusive/conflict/unavailable;
- live execution updates;
- SSE disconnect/reconnect/catch-up;
- duplicate delivery/idempotent reducer;
- slow browser non-blocking runtime;
- long content/overflow;
- invalid dynamic-query/chart combination;
- cross-filter/drill-down consistency;
- architecture/output lineage consistency;
- browser security deny-list;
- frontend build;
- clean start.

Use pytest/Vitest/Testing Library/Playwright as applicable.

**Hard visual + feature freeze at end of 2026-09-05.**

After freeze: P0/P1 delivery-blocking corrections only, each followed by targeted regression.

## 8. 2026-09-06 — clean reproduction and final acceptance

From a clean checkout:

- install Python/backend;
- install frontend from lockfile;
- build frontend;
- run complete Python tests/campaign validators;
- run observability/API tests;
- run frontend unit/E2E tests;
- execute provider-independent realtime demo;
- verify architecture/output explanation;
- verify documentation links/commands;
- run final acceptance audit.

No open P0 is allowed after this phase without explicit blocking status.

## 9. 2026-09-07 — final rehearsal and contingency

- execute exact presentation flow end to end;
- verify presentation machine/environment;
- verify provider-independent fallback;
- verify D01/D02 views;
- verify live run + trace + architecture + lineage + data explorer narrative;
- fix demo-blocking P0 only;
- rerun affected regression after every fix.

No redesign or feature expansion.

## 10. 2026-09-08 — delivery

- short smoke test only;
- no same-day feature work;
- deliver exact frozen code/docs/evidence;
- present limitations and `NO_SELECTION` honestly if applicable.

## 11. Final demo contract

The final presentation should visibly exercise:

```text
request enters runtime
→ run appears LIVE
→ architecture path highlights
→ model-call metadata
→ structured decision
→ typed tool proposal
→ B1/B2/B3 policy result as applicable
→ TRACTIAN call metadata
→ safe observation/evidence
→ subsequent decision
→ terminal outcome
→ RunTrace completes
→ evaluator appears only after runtime completion
→ output lineage explains provenance
→ dynamic explorer analyzes run/experiment data
→ D01/D02 quality/provider evidence
```

Also show multiple outcome classes, not only a happy path.

## 12. Stop rules

Stop/defer work when it:

- has no TAPI/acceptance/material-risk mapping;
- requires paid spillover;
- weakens evaluator/runtime isolation;
- exposes private/raw material to browser;
- changes D01/D02 frozen semantics without a prospective amendment;
- introduces topology/framework complexity without measured benefit;
- occurs after hard freeze and is not P0/P1 delivery blocking.

The current plan is intentionally deadline-protective: complete the observable, explainable, reproducible agent/evaluator product before optional sophistication.