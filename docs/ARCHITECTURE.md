# Academy × TRACTIAN — Architecture, Stack and Techniques

**Status:** ACTIVE / canonical final-P0 architecture  
**Checkpoint:** 2026-09-05 BRT  
**Accepted main baseline:** `d3bed06b132212c85b126f56708863d45f64e03e`  
**Post-merge gate:** `final-ci-required` run #386 / `required-gate = success`  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

Historical ADRs and experiments remain authoritative for their original checkpoints. This document owns the current integrated architecture.

## 1. Architecture principles

- Agent + Evaluation are one delivered product;
- runtime and evaluator remain isolated;
- provider/model never owns identity, authorization, evaluation seed or gold truth;
- `HarnessRunner` remains the exclusive real TRACTIAN tool-execution boundary;
- consequential actions fail closed through deterministic validation, private custody, confirmation, idempotency and fencing;
- PostgreSQL rows are the durable serving truth;
- frontend observes sanitized projections, never raw sensitive traces or chain-of-thought;
- realtime wakeups cannot alter agent semantics;
- adaptive/provider/framework changes require EDD evidence and a material Pareto win;
- P0 external-service cost remains USD0.

## 2. Delivered product topology

```text
React Operator Control Room
        ↑ REST commands/reads + genuine SSE
FastAPI Product / Observability API
        ↑ signed RuntimeContextProvider + tenant authorization
PostgreSQL shared serving substrate
        ├── run ownership / execution
        ├── tenant RLS
        ├── runtime handoff work items + lease generation
        ├── action custody + idempotency claims
        ├── non-transferable action execution leases
        ├── safe observability/evaluation rows
        └── semantic-review / operational-value state
        ↑
RealtimeProductionRuntime
        ↓
provider-neutral DecisionSource
        ↓
AgentController
        ↓
HarnessRunner                     ← exclusive real tool boundary
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
FINAL | CLARIFY | ABSTAIN | ESCALATE | ACTION proposal
        ↓
RunTrace
        ↓
ProductionEvaluator               ← post-runtime only
        ↓
safe PostgreSQL projection
        ↓
REST/SSE + LISTEN/NOTIFY wakeup + durable cursor fallback
        ↓
frontend / analytics / evidence drill-down
```

`POST /api/runs` uses this path. There is no demo-only runtime.

## 3. Read-only cross-replica runtime handoff

Read-only investigation work is represented by durable PostgreSQL work items. Claiming uses row locking (`FOR UPDATE ... SKIP LOCKED`) plus:

- expiring owner lease;
- monotonically increasing generation/fencing token;
- private handoff payload unavailable to browser projections;
- terminal cleanup of private handoff state.

Tested semantics:

```text
healthy owner A        → B cannot double-claim/interfere
expired owner A        → B may claim a new generation
stale generation A     → cannot renew/finalize/publish as current owner
recovered B            → may continue to evaluation/terminal persistence
terminal completion    → private handoff payload removed
```

This proves repository-level algorithmic cross-replica correctness. It does not prove deployed HA, autoscaling, RTO/RPO or multi-region behavior.

## 4. Consequential-action architecture

Actions intentionally use different lease semantics from read-only work.

```text
agent ACTION proposal
        ↓
deterministic permission/scope/schema/justification validation
        ↓
private PostgreSQL Action Custody
        ↓
PENDING_CONFIRMATION
        ↓
authenticated operator confirms opaque action_id only
        ↓
current authorization + host action kill switch revalidated
        ↓
persistent atomic idempotency claim
        ↓
non-transferable action execution lease
        ↓
exact custodied payload
        ↓
HarnessRunner / B2 / TRACTIAN transport
        ↓
lease-fenced custody/ledger/observability/terminal persistence
        ↓
ACCEPTED | NOT_ACCEPTED | safe failure | UNCERTAIN
        ↓
separate realtime action RunTrace
        ↓
ProductionActionEvaluator
```

Properties:

- proposal is never execution;
- browser cannot inject action args, requester identity, permissions, scope or idempotency key at confirmation;
- healthy action owner renews only its exact lease generation;
- action lease expiry/missing stale ownership never transfers to another worker;
- lost ownership converges ambiguous state to `UNCERTAIN`;
- stale late responses cannot overwrite `UNCERTAIN` with success/failure terminal claims;
- duplicate confirmation cannot produce a second product transport attempt;
- restart/lease expiry never authorizes replay.

This is **not** distributed exactly-once external side effects. That stronger guarantee requires the TRACTIAN API to participate in a shared idempotency/fencing protocol.

## 5. Realtime observability

```text
runtime/evaluator transition
        ↓
SafeObservabilityProjector
        ↓
PostgreSQL SafeRun / SafeEvent / SafeEvidence / SafeEvaluation rows
        ↓
commit durable row + bounded NOTIFY cursor payload
        ↓
one LISTEN connection per application replica
        ↓
local wakeup fan-out to SSE waiters
        ↓
durable sequence read / Last-Event-ID catch-up
        ↓
idempotent React reducer
```

Durable rows remain authoritative. NOTIFY is only a latency optimization; missed notifications recover through bounded durable polling/cursor reads.

RT-WAKEUP-001 evidence retained:

- one hosted-runner sample was efficiency-inconclusive with every hard safety/delivery gate green;
- identical same-SHA rerun, with unchanged thresholds/protocol, passed;
- passing rerun: polling p95 `52.10 ms`, LISTEN/NOTIFY p95 `23.71 ms`, idle durable-read reduction `62.5%`.

Do not infer a deterministic production latency SLO from hosted CI.

## 6. Persistence and dependency stack

### Serving

| Layer | Technology | State |
|---|---|---|
| Language | Python >=3.11 | PREFERRED/FROZEN P0 |
| Typed schemas | Pydantic >=2.6,<3 | PREFERRED |
| API | FastAPI >=0.141.1,<0.142 | PREFERRED |
| ASGI | Uvicorn >=0.52.4,<0.53 | PREFERRED |
| Serving persistence | PostgreSQL + psycopg | PROMOTED |
| Tenant boundary | PostgreSQL RLS + scoped role | PROMOTED/tested |
| Realtime wakeup | PostgreSQL LISTEN/NOTIFY + durable fallback | PROMOTED |
| Runtime handoff | PostgreSQL queue + generation lease | PROMOTED/tested |
| Consequential action fencing | PostgreSQL non-transferable lease | PROMOTED/tested |
| Agent orchestration | custom `AgentController` | P0 `NO_CHANGE` |
| Tool execution | `HarnessRunner` | FROZEN hard boundary |
| Tool contracts | 18 typed `ToolSpec`s | FROZEN P0 |
| Evaluation | deterministic-first custom evaluator/campaigns | FROZEN primary layer |
| Tests | pytest | PREFERRED |
| Packaging | hatchling/wheel | PREFERRED/proved |

DuckDB is **not** a production dependency. It remains only in optional `dev` / `operational-store-benchmark` extras for historical/test compatibility.

### Frontend

- React 19
- TypeScript
- Vite
- TanStack Query
- Apache ECharts
- React Flow / `@xyflow/react`
- Vitest
- Playwright
- committed `package-lock.json` + `npm ci`

## 7. Identity and tenant isolation

The promoted product uses the project-owned `academy-runtime-v1` signed bearer envelope with HMAC-SHA256 verification and server-owned organization/user/identity/permission claims.

It is deliberately not described as OAuth/OIDC/JWT/enterprise SSO.

PostgreSQL RLS is an independent data boundary: scoped serving reads use a non-owner, non-superuser, non-`BYPASSRLS` role plus transaction-local organization context.

## 8. Agent/evaluation techniques

### Typed iterative loop

```text
decision
→ optional typed tool proposal
→ deterministic B1/B2/B3 checks
→ execution
→ normalized observation
→ next decision or terminal outcome
```

### First-class safe outcomes

- orient/final;
- investigate;
- clarify;
- abstain;
- escalate;
- bounded action proposal / governed confirmation.

### Deterministic safety envelope

Always deterministic:

- identity/tenant/permissions;
- ToolSpec/schema validation;
- resource/action authorization;
- confirmation/idempotency/no-replay;
- privacy/field deny-list;
- hard turn/tool/resource caps;
- gold/evaluator-private boundary.

### Evaluation

```text
RunTrace
→ deterministic structural/safety/trajectory evaluation
→ safe evaluation projection
→ Eval Lab / EDD comparison
```

Semantic review infrastructure exists, but no semantic judge becomes a production gate without real blinded human labels, adjudication and measured judge-vs-human agreement. Current state remains `NOT_READY_HUMAN_DATA`.

## 9. EDD and architecture decision state

Material changes require:

```text
requirement/gap
→ baseline
→ systematic research
→ preregistered metrics + hard gates
→ controlled candidate
→ repeated/sliced comparison
→ uncertainty/failure analysis
→ PROMOTE / REJECT / INCONCLUSIVE / NO_CHANGE
→ regression
```

Current P0 decisions:

| Area | State |
|---|---|
| PostgreSQL serving state | PROMOTED |
| PostgreSQL safe observability/evaluation | PROMOTED |
| LISTEN/NOTIFY wakeup | PROMOTED |
| read-only cross-replica handoff | PROMOTED/tested |
| consequential action non-transferable lease | PROMOTED/tested |
| custom AgentController | `NO_CHANGE` / P0 baseline |
| LangGraph | not promoted |
| multi-agent | not justified |
| RAG/vector/hybrid retrieval | not justified |
| persistent cross-request memory | not justified |
| adaptive runtime stopping | not promoted; evaluator-only diagnostic |
| adaptive provider routing | deferred; no selected production providers |
| provider/model | `NO_SELECTION` |

## 10. Provider experiment state

D01 and D02 are consumed governed experiments. D02's controlled 512→1024 completion-cap change improved several public metrics, but both candidates still failed frozen M1/M4/M7 promotion gates.

Therefore:

- production provider/model selection = `NO_SELECTION`;
- D01/D02 must not be replayed;
- any P1 provider/model comparison requires a new experiment ID, current factual revalidation, new preregistration and fresh authorization.

## 11. Frontend architecture

```text
FastAPI REST/SSE
      ↓
TanStack Query + idempotent live reducer
      ↓
React Operator Control Room
      ├── Mission Control
      ├── Live Run Cockpit
      ├── Run Explorer
      ├── Timeline / Waterfall
      ├── Trace Graph
      ├── Architecture Explorer
      ├── Evidence Explorer
      ├── Output Lineage
      ├── Action Control
      ├── Tools & Policy analytics
      ├── Eval Lab
      ├── Provider D01/D02 Lab
      ├── Dynamic Data Explorer
      └── Production Health
```

Safe outputs may show component decisions, tools, evidence, policies/reason codes, latency/resource metrics and evaluation. Hidden chain-of-thought is never part of the product contract.

## 12. Bounded non-claims

The final P0 architecture does not establish:

- deployed Cloud Run/Cloud SQL HA;
- production RTO/RPO/uptime/autoscaling/multi-region failover;
- external exactly-once actions;
- enterprise OIDC/SSO;
- production provider selection;
- completed human semantic calibration;
- measured engineer-time savings/business value;
- production capacity/SLO from CI load tests;
- superiority/necessity of LangGraph, RAG, multi-agent, Redis/Kafka/Temporal/MCP;
- GitHub branch-protection enforcement while GitHub reports it disabled.

## 13. Change gate after hard freeze

At end of 2026-09-05, feature/visual/architecture contracts freeze. After that point, only delivery-blocking fixes are allowed, each with targeted regression and explicit evidence. P1 experiments must not alter the frozen delivery candidate.