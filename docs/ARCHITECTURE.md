# Academy × TRACTIAN — Architecture, Stack and Techniques

**Status:** ACTIVE / canonical architecture document  
**Checkpoint:** 2026-09-02  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**TAPI crosswalk:** [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md)

This document owns the durable integrated architecture, stack, techniques and framework decisions. It replaces `ARCHITECTURE-ROADMAP.md` as the active architecture source.

## 1. Architecture principles

- runtime and evaluator remain isolated;
- model/provider never controls identity or evaluation seed;
- all real tools execute through one typed execution boundary;
- actions fail closed through deterministic gates;
- every meaningful transition is traceable;
- frontend observes safe projections, never raw sensitive traces;
- realtime telemetry cannot change agent behavior;
- architecture expands only when measured evidence supports a material gap;
- USD0 external-service constraint remains binding.

## 2. Delivered agent/evaluator architecture

```text
User request
    ↓
ProductionRequest / runtime-owned context
    ↓
ProductionRuntime
    ↓
DecisionSource
    ↓
AgentController
    ↓
HarnessRunner
    ↓
18-operation ToolSpec registry
    ↓
B1 argument validation
    ↓
B2 resource/action policy
    ↓
B3 evidence/authorization where applicable
    ↓
TRACTIAN HTTP transport
    ↓
normalized observation
    ↓
AgentController
    ↓
FINAL | CLARIFY | ABSTAIN | ESCALATE
    ↓
RunTrace
    ↓
ProductionEvaluator / controlled evaluation campaigns
```

The default production runtime keeps consequential actions disabled. A separate controlled supplied/test profile demonstrates bounded authorized action behavior and idempotency custody; it is not blanket customer authorization.

## 3. Production observability target

```text
HarnessRunner / controller event
    ↓
append canonical runtime trace event
    ↓
SafeObservabilityProjector
    ↓
ObservabilityEvent
    ├──→ durable local telemetry / DuckDB
    └──→ ObservabilityEventSink
             ↓
          SSE stream
             ↓
       React control room
```

Requirements:

- event publication is fail-isolated from runtime execution;
- safe event ids preserve per-run sequence;
- persisted catch-up supports reconnect;
- browser reducer is idempotent;
- slow clients cannot block the agent;
- no fake model-thinking/progress events;
- raw `RunTrace`, credentials, identity, seed, auth headers, raw provider material, forbidden observation bodies and evaluator-private truth never enter browser telemetry.

For a single runtime/API process, in-process fan-out + persisted safe telemetry is the delivery baseline. Horizontal multi-instance realtime requires a tested shared durable stream adapter before it may be claimed.

## 4. Frontend target architecture

```text
FastAPI REST/SSE
     ↓
TanStack Query + live event reducer
     ↓
React application
     ├── Mission Control
     ├── Live Runs
     ├── Run Explorer
     ├── Timeline / Waterfall
     ├── Trace Graph
     ├── Tools & Policy
     ├── Quality & Providers
     ├── Dynamic Data Explorer
     └── Architecture Explorer / Explain This Run
```

Every KPI/chart must be drillable to the underlying safe run/event evidence.

## 5. Stack matrix

### Implemented core

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.11+ | runtime/evaluation/research |
| Schema/contracts | Pydantic 2.x | typed immutable models and validation |
| Agent orchestration | custom `AgentController` | bounded single-agent loop |
| Execution | `HarnessRunner` | sole tool execution/trace boundary |
| Tool interface | `ToolSpec` / JSON-schema-like contracts | canonical typed TRACTIAN tools |
| Tests | pytest | unit/integration/regression/campaign tests |
| Packaging | hatchling | standalone wheel reproduction |
| Provider route | Cloudflare Workers AI | governed zero-cash provider experiments |

### P0 observability/backend

| Layer | Target | Purpose |
|---|---|---|
| Web/API | FastAPI stable line | read-only telemetry/query API + SSE |
| Analytics store | DuckDB stable line | local analytical telemetry |
| Realtime | Server-Sent Events | one-way live updates + reconnect cursor |
| Export | sanitized JSONL/Parquet | reproducible/offline evidence where useful |

### P0 frontend

| Layer | Target | Purpose |
|---|---|---|
| Language | TypeScript | browser type safety |
| UI | React stable | application/component model |
| Build | Vite stable | dev/build |
| Server state | TanStack Query | cache/loading/error/refetch |
| Analytics | Apache ECharts | dynamic/live data visualization |
| Graph topology | React Flow / `@xyflow/react` | trace + architecture graph |
| Unit/component tests | Vitest + Testing Library | frontend behavior |
| E2E | Playwright | browser/realtime/reconnect/security flows |

Exact frontend dependency versions become authoritative only when the scaffold/lockfile is committed and tested.

## 6. Agent techniques

### Tool-augmented iterative loop

Decision → typed tool proposal → validation/policy → observation → next decision/terminal outcome.

This is structurally aligned with tool-using agent patterns but the project does not claim hidden chain-of-thought or literal ReAct prompting unless explicitly implemented/tested.

### Typed function/tool calling

- fixed canonical registry;
- strict arguments;
- no arbitrary model-generated HTTP;
- identity/seed fields outside model control.

### Evidence-aware terminal policy

First-class outcomes:

- orient/final;
- investigate/tool;
- clarify;
- abstain;
- escalate;
- consequential action only through deterministic authorization.

### Bounded planning/stopping

- max turns;
- max tool calls;
- fail-safe terminal behavior;
- no hidden automatic provider retry/fallback in governed experiment paths.

### Fail-closed safety

- B1 argument/schema correctness;
- B2 permissions/resource safety;
- B3 evidence/authorization for applicable actions;
- idempotency/no-replay for consequential work.

### Robustness techniques

Test complete/partial/inconclusive/conflict/unavailable responses, tool/provider faults, invalid arguments, denied actions and insufficient evidence.

### Repeated-run stability

Controlled repetitions compare decisions/tool signatures and failure behavior instead of relying on one favorable sample.

### Controlled model experimentation

Frozen inputs/configuration, explicit hard gates, resource accounting, Pareto/`NO_SELECTION`, no after-the-fact tuning of D01.

### Trace-only production evaluation

Production evaluator validates what is actually visible in the trace. Private benchmark/gold data never enters runtime.

### Realtime safe event projection

Trace events become allow-listed observable records; persistence/streaming are derived views, not alternate truth.

### Schema-driven visualization

Allow-listed field metadata controls dimensions/measures/aggregations/chart compatibility. Browser never executes arbitrary SQL over private schema.

## 7. Provider experiment architecture

D01:

```text
8 public probes × 2 repeats × 2 models = 32 attempts
completion cap 512
USD0 / Workers Free
no retries/fallback
Pareto / NO_SELECTION permitted
```

Observed result: 24/24 generic `CLIENT_FAILURE` attempts hit exactly 512 output tokens.

D02 preserves the packet and changes only:

```text
completion cap 1024
sanitized client failure subtype
```

The provider experiment is a model/interface behavior comparison, not an excuse to rewrite the agent architecture.

## 8. Explicit framework decisions

| Technology | Current decision | Why |
|---|---|---|
| LangGraph | not used | custom bounded controller already covers measured needs; no topology gap proved |
| LangChain | not used | unnecessary abstraction for current typed path |
| Pydantic AI | not orchestrator | direct Pydantic contracts already used |
| MCP | not main path | TAPI accepts native tools/equivalent; direct typed contracts are simpler here |
| RAG/vector/hybrid/reranking | not used | no measured retrieval gap |
| Persistent memory | not used | no requirement; increases leakage/reproducibility risk |
| Adaptive model routing | not used | provider selection not yet established and no routing benefit measured |
| Grafana/Phoenix/Langfuse | optional only | native product control room owns reviewer/demo UX |
| OpenTelemetry | optional export | useful later but not required to make native telemetry correct |
| Redis Streams | conditional | needed only for claimed tested multi-instance live fan-out |
| Streamlit/Gradio | not used | React better fits realtime graphs, cross-filtering and architecture/output explanation |

Framework absence is a deliberate engineering decision, not missing implementation.

## 9. Architecture explanation contract for frontend

The frontend must be able to answer, for a selected run:

1. which components participated;
2. which component produced each output;
3. what safe evidence/input fed it;
4. what policy/tool transition occurred next;
5. what became the terminal customer-safe output;
6. which evaluation happened afterward and was not visible to runtime.

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

No hidden chain-of-thought is exposed.

## 10. Architecture change gate

Any proposal for RAG, multi-agent, memory, MCP migration, adaptive routing or another major framework must state:

```text
material P0/P1 gap
→ simple baseline
→ measurable hypothesis
→ comparison
→ quality/latency/reliability/resource result
→ ADR if materially better
```

Without that evidence, `NO_CHANGE` is the correct architecture decision.