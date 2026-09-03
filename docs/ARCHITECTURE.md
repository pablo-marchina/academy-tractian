# Academy × TRACTIAN — Architecture, Stack and Techniques

**Status:** ACTIVE / canonical architecture document  
**Checkpoint:** 2026-09-02 20:20 BRT  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**TAPI crosswalk:** [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md)

This document owns the current integrated architecture, stack, techniques and framework decision state. Historical ADRs remain authoritative for their original scopes.

## 1. Architecture principles

- updated TAPI requires one solution containing Agent + Evaluation;
- runtime and evaluator remain isolated;
- model/provider never controls identity or evaluation seed;
- all real TRACTIAN tools execute through one typed execution boundary;
- consequential actions fail closed through deterministic authorization/confirmation/idempotency boundaries;
- every meaningful observable transition is traceable;
- frontend observes safe projections, never raw sensitive traces;
- realtime telemetry cannot alter agent semantics;
- adaptive intelligence may optimize investigation/stopping/escalation only inside hard deterministic safety caps;
- every material stack/framework/topology choice is preceded by systematic comparison and evidence;
- USD0 external-service constraint remains binding.

## 2. Delivered main product architecture

```text
React Operator Control Room
        ↑ REST reads/commands + genuine SSE
FastAPI Product / Observability API
        ↑ safe projection / persisted telemetry
RealtimeProductionRuntime
        ↓
trusted RuntimeContextProvider
        ↓
DecisionSource / provider-neutral model boundary
        ↓
AgentController
        ↓
HarnessRunner                         ← exclusive real tool boundary
        ↓
18-operation typed ToolSpec registry
        ↓
B1 schema/argument validation
        ↓
B2 permission/resource/action policy
        ↓
B3 evidence/authorization where applicable
        ↓
TRACTIAN HTTP adapter / supplied API
        ↓
normalized observation/evidence
        ↓
AgentController
        ↓
FINAL | CLARIFY | ABSTAIN | ESCALATE
        ↓
RunTrace
        ↓
ProductionEvaluator                  ← post-runtime only
        ↓
safe evaluation projection
        ↓
DuckDB analytical/read model
        ↓
FastAPI REST/SSE
        ↓
frontend / analytics / evidence drill-down
```

`POST /api/runs` uses this real path. There is no demo-only runtime.

## 3. Consequential-action architecture — PR #143

The final action design is intentionally two-phase:

```text
agent ACTION proposal
        ↓
deterministic permission/scope/schema/justification validation
        ↓
private Action Custody
        ↓
PENDING_CONFIRMATION
        ↓
authenticated operator confirms opaque action_id
        ↓
current authorization + host action kill switch revalidated
        ↓
persistent atomic idempotency claim
        ↓
exact custodied payload
        ↓
HarnessRunner / B2 / TRACTIAN transport
        ↓
accepted=true OR safe failure/UNCERTAIN
        ↓
separate realtime action RunTrace
        ↓
ProductionActionEvaluator
```

Properties:

- proposal is never equivalent to execution;
- browser confirmation cannot provide raw args, identity, permissions, scope or idempotency key;
- private action custody is separate from safe observability storage;
- ambiguous post-claim failure is not automatically retried;
- requester isolation hides action existence from other requesters;
- confirmed action follows the same SSE/reducer/trace frontend mechanism as ordinary runs;
- frozen read-only ProductionRuntime and ProductionEvaluator semantics remain unchanged.

This PR is currently open but its latest head has passed the full repository workflow gate.

## 4. Realtime observability architecture — implemented

```text
canonical runtime event creation
        ↓
append immutable RunTrace event
        ↓
SafeObservabilityProjector
        ↓
SafeEvent / SafeRun / SafeEvidence / SafeEvaluation
        ↓
transactional DuckDB persistence
        ↓
FastAPI REST reads + SSE cursor stream
        ↓
idempotent React event reducer
        ↓
Live Run / Trace / Architecture / Health / Analytics
```

Implemented properties:

- event publication is fail-isolated from runtime execution;
- safe event sequence is canonical per run;
- persisted catch-up supports `Last-Event-ID` reconnect;
- browser reducer is idempotent by safe event id;
- slow/disconnected clients are outside the runtime execution path;
- no fake progress or hidden model-thinking event is generated;
- provider/adapter operability is observed passively rather than by quota-consuming health probes;
- production health exposes actual runtime/API/resource/SSE telemetry.

The delivery currently makes only a tested single-process realtime claim. Horizontal multi-instance realtime requires a separately tested shared durable stream before it may be claimed.

## 5. Frontend architecture — implemented

```text
FastAPI REST/SSE
      ↓
TanStack Query + live event reducer
      ↓
React application
      ├── Mission Control
      ├── Live Run Cockpit
      ├── Run Explorer
      ├── Timeline / Waterfall
      ├── Trace Graph
      ├── Architecture Explorer
      ├── Evidence Explorer
      ├── Output Lineage
      ├── Action Control (PR #143)
      ├── Tools & Policy analytics
      ├── Eval Lab
      ├── Provider D01/D02 Lab
      ├── Dynamic Data Explorer
      └── Production Health
```

Every run-specific analytical surface uses the same safe run identity/scope and must drill toward exact safe event/evidence rows where semantically meaningful.

## 6. Current dependency stack

### Backend/runtime

| Layer | Current technology | Decision state |
|---|---|---|
| Language | Python >=3.11 | PREFERRED/FROZEN scope |
| Typed schemas | Pydantic >=2.6,<3 | PREFERRED |
| Product/API | FastAPI >=0.141.1,<0.142 | PREFERRED |
| ASGI serving | Uvicorn >=0.52.4,<0.53 | PREFERRED |
| Analytics/read store | DuckDB >=1.5.5,<1.6 | PREFERRED for analytics |
| Agent orchestration | custom `AgentController` | PREFERRED baseline; HITL revalidation pending |
| Tool execution | `HarnessRunner` | FROZEN hard boundary |
| Tool contracts | typed `ToolSpec` registry | FROZEN current API scope |
| Evaluation | deterministic-first custom evaluator/campaigns | FROZEN primary layer |
| Tests | pytest | PREFERRED |
| Packaging | hatchling/wheel | PREFERRED/proved |
| Provider experiment route | direct Cloudflare Workers AI | D01/D02 experiment route, not yet production selection |

### Frontend

Current pinned direct dependencies in `frontend/package.json`:

| Layer | Version |
|---|---:|
| React | 19.2.8 |
| React DOM | 19.2.8 |
| TanStack Query | 5.102.8 |
| React Flow / `@xyflow/react` | 12.11.5 |
| Apache ECharts | 6.1.0 |
| TypeScript | 7.0.2 |
| Vite | 8.2.2 |
| Vitest | 4.1.11 |

The final freeze must additionally commit a deterministic transitive dependency lockfile and use lockfile installation in CI.

## 7. Agent techniques

### Typed tool-augmented iterative loop

```text
decision
→ optional typed tool proposal
→ deterministic policy/validation
→ execution
→ normalized observation
→ next decision or terminal outcome
```

Do not claim hidden chain-of-thought. Observable structured decisions and traces are the evaluation surface.

### Evidence-aware outcomes

First-class behavior:

- orient/final;
- investigate;
- clarify;
- abstain;
- escalate;
- bounded action proposal.

### Bounded planning/stopping

- hard max turns;
- hard max tool calls;
- safe terminal behavior on exhaustion/failure;
- no uncontrolled provider retries/fallbacks on governed experiment paths.

### Deterministic safety envelope

- B1 typed/schema validation;
- B2 permission/resource/action authorization;
- B3 evidence/authorization where applicable;
- action confirmation/custody/idempotency/no-replay;
- identity/seed outside model control;
- browser privacy deny-list.

### Robustness to probabilistic API behavior

Explicitly evaluate:

- complete;
- partial;
- inconclusive;
- conflict;
- unavailable;
- tool/provider failures;
- invalid arguments;
- denied consequential actions;
- insufficient evidence.

### Repeated-run stability

Use repeated execution and grouped/sliced metrics rather than one favorable run.

### Eval-Driven Development

Material candidates are compared against a frozen baseline with hard integrity gates, group-aware metrics and explicit `PROMOTE / REJECT / INCONCLUSIVE` semantics.

## 8. Evaluation architecture

Current primary layer:

```text
RunTrace
→ deterministic structural/safety/trajectory evaluator
→ safe evaluation projection
→ Eval Lab / EDD delta gate
```

Required closure before final freeze where deterministic scoring is insufficient:

```text
human-labelled calibration sample
        ↓
semantic judge candidate(s)
        ↓
judge-vs-human agreement/error analysis
        ↓
accept or reject judge
        ↓
calibrated semantic layer
```

Semantic dimensions may include operational conclusion quality, evidence support, unsupported claims, escalation/handoff usefulness and customer-safe communication.

Semantic judges cannot see evaluator-private/gold information that would leak into runtime, and they cannot displace deterministic ground truth where exact checks exist.

## 9. Adaptive-policy candidate architecture

The current fixed/bounded controller is the baseline.

Authorized candidate under #129:

```text
observable evidence state
  ├── evidence sufficiency
  ├── contradiction/uncertainty
  ├── previous response mode
  ├── action risk
  ├── remaining hard budget
  └── marginal evidence gain
        ↓
adaptive choice
  ├── continue investigation
  ├── clarify
  ├── finalize
  ├── abstain
  ├── escalate
  └── propose bounded action
```

Hard authorization/schema/privacy/idempotency/resource limits remain deterministic. The adaptive layer is adopted only after a controlled EDD comparison proves material Pareto benefit.

## 10. Runtime/HITL revalidation

ADR-004 froze the custom controller for the original P0 scope, when durable pause/resume was not required.

The two-phase action workflow creates a legitimate new materiality question.

Prospective comparison under #92:

```text
A — current custom AgentController + private action custody
B — LangGraph-compatible durable/checkpoint/HITL adapter
```

Provider, ToolSpecs, HarnessRunner, safety semantics, cases and evaluator must remain fixed.

Measure task/trace equivalence, pause/resume, restart recovery, duplicate-action rate, failure containment, latency/resource overhead, dependency/maintenance complexity, clean reproduction and debuggability.

No framework migration is pre-authorized. `NO_CHANGE` is preferred when the current architecture remains Pareto-optimal.

## 11. Operational state/storage revalidation

DuckDB is the selected sanitized analytics/read-model baseline.

A separate decision applies to mutable action/HITL operational state:

```text
A — current DuckDB single-process custody/idempotency
B — local PostgreSQL operational state
```

Compare only to support the production claim we intend to make.

If single-process/single-node is the final bounded claim and restart/concurrency tests pass, the current baseline can remain.

If multi-process durable action execution is claimed, a tested multi-process-capable operational store is required.

Potential final separation if evidence supports it:

```text
PostgreSQL → mutable operational state
DuckDB     → safe analytical telemetry
```

## 12. Provider experiment architecture

D01:

```text
8 public probes × 2 repeats × 2 models = 32 attempts
completion cap 512
Workers Free / USD0
no hidden retries/fallback
Pareto / NO_SELECTION permitted
```

Observed: 24/24 generic CLIENT_FAILURE attempts landed at the exact 512 output-token cap.

D02 holds provider/models/tasks/prompt/schema/evaluator/topology constant and changes only:

```text
completion cap 1024
sanitized failure subtype
```

This is a controlled provider/interface diagnosis, not an architecture bake-off.

## 13. Current framework/technology decision states

| Technology/area | Current state | Rule |
|---|---|---|
| Native typed tools | PREFERRED | MCP only if interoperability need becomes material |
| MCP | NO_CHANGE | not required by updated TAPI |
| Custom AgentController | PREFERRED baseline | revalidate only for new HITL/restart requirement |
| LangGraph | QUALIFIED alternative | compare prospectively under #92; no automatic migration |
| Multi-agent | NO_CHANGE | no measured topology gap |
| RAG/vector/hybrid/reranking | NO_CHANGE | no measured retrieval gap |
| Persistent memory | NO_CHANGE | no demonstrated cross-request requirement |
| Adaptive investigation/stopping | RESEARCH / #129 | adopt only on EDD Pareto improvement |
| Adaptive provider routing | UNASSESSED/DEFERRED | requires >=2 production-eligible providers |
| FastAPI | PREFERRED | strong fit for current Python product/API/SSE boundary |
| REST + SSE | PREFERRED | one-way runtime telemetry + REST commands |
| React + Vite | PREFERRED | internal SPA/control-room fit; no SSR/SEO requirement |
| ECharts | PREFERRED | schema/dataset-driven dynamic analytics |
| React Flow | PREFERRED | trace/architecture graph fit |
| DuckDB analytics | PREFERRED | local analytical telemetry |
| DuckDB operational mutation | REVALIDATE | bounded by final production topology claim |
| PostgreSQL operational state | CANDIDATE | compare only if broader durability/concurrency claim is needed |
| OpenTelemetry | OPTIONAL EXPORT | not primary product truth/UI |
| Grafana/Phoenix/Langfuse | OPTIONAL | not primary delivery UI |
| Redis/shared stream | CONDITIONAL | only for actually tested multi-instance realtime |

## 14. Architecture/output explanation contract

For a selected run, the frontend must be able to answer:

1. which delivered components participated;
2. which component produced each safe output;
3. which safe evidence/input fed it;
4. which policy/tool transition occurred next;
5. which output became terminal;
6. which evaluation occurred afterward;
7. whether a consequential action was proposed, pending, confirmed, executed or uncertain.

Output origin vocabulary:

```text
MODEL
CONTROLLER
POLICY
TOOL
OBSERVATION
EVALUATOR
SYSTEM
```

Runtime-time and evaluator-time information remain visually and architecturally separate.

## 15. Architecture change gate

Any material proposal — framework, topology, store, RAG, memory, routing, deployment or major frontend data path — must state:

```text
material TAPI/P0/P1 gap
→ current/simple baseline
→ systematic research
→ credible alternatives
→ preregistered metrics/hard gates
→ controlled comparison
→ uncertainty/failure/production-fit analysis
→ Pareto decision
→ ADR/reversal trigger
```

Without evidence of material benefit, `NO_CHANGE` is the correct architecture decision.
