# Academy × TRACTIAN — Architecture, Stack and Techniques

**Status:** ACTIVE / canonical architecture document  
**Checkpoint:** 2026-09-05 BRT  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Code map:** [`CODEBASE-MAP.md`](CODEBASE-MAP.md)  
**TAPI crosswalk:** [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md)

This document owns the **promoted current architecture, stack and technique decisions**. Historical ADRs remain authoritative for their original scopes, but they do not override current state when later accepted evidence has superseded an earlier baseline.

## 1. Architecture principles

- Agent + Evaluation are one integrated product, with runtime/evaluator isolation.
- Identity, tenant scope, permissions, evaluator truth and private custody stay outside model control.
- All real TRACTIAN tools execute through the typed `HarnessRunner` boundary.
- Consequential actions remain behind deterministic authorization, confirmation, custody, idempotency and lease/fencing controls.
- PostgreSQL is the promoted durable serving substrate; no local-file store is the production source of truth.
- Realtime wake-up/delivery is not a correctness or authorization boundary; durable rows/cursors are authoritative.
- Frontend surfaces safe structured provenance, not raw sensitive traces or hidden chain-of-thought.
- Adaptive/model/framework changes are challengers, not automatic upgrades; promotion requires measured Pareto benefit and hard-gate preservation.
- Claims must remain narrower than the evidence that supports them.
- The current project governance still records the USD0 external-service constraint for the existing evidence program; any production-hosting policy change requires an explicit new decision rather than silent drift.

## 2. Promoted product architecture

```text
Browser / React Operator Control Room
        ↑ REST commands/reads + SSE
FastAPI Product / Observability API
        ↑ trusted server-owned runtime context
Signed bearer runtime identity
        ↓
PostgreSQL tenant RLS + operational state
        ↓
PostgreSQL runtime handoff queue / generation-fenced lease
        ↓
RealtimeProductionRuntime.prepare()/execute()
        ↓
provider-neutral DecisionSource
        ↓
AgentController
        ↓
HarnessRunner                       ← exclusive real tool boundary
        ↓
18-operation typed ToolSpec registry
        ↓
B1 schema/argument validation
        ↓
B2 permission/resource/action policy
        ↓
B3 evidence/authorization boundary where applicable
        ↓
TRACTIAN HTTP transport
        ↓
normalized observation/evidence
        ↓
AgentController
        ↓
FINAL | CLARIFY | ABSTAIN | ESCALATE | ACTION_PROPOSAL
        ↓
RunTrace
        ↓
ProductionEvaluator                ← post-runtime only
        ↓
sanitized PostgreSQL observability/evaluation projection
        ↓
PostgreSQL durable cursor + LISTEN/NOTIFY wake-up
        ↓
REST / SSE / React control room
```

`POST /api/runs` exercises the promoted product path. Provider-free acceptance substitutes the model decision source only; runtime, tools, policies, persistence, evaluation, SSE and frontend remain the product path.

## 3. Runtime ownership and horizontal handoff

Read-only runtime work is durable and replica-safe at the tested repository-algorithm level.

```text
prepared runtime payload
→ PostgreSQL ownership row
→ replica claims generation-fenced lease
→ execute/evaluate/persist
→ terminal state + private payload cleanup
```

Properties proven by PostgreSQL-real tests:

- a healthy lease is not double-claimed;
- another replica cannot interfere with healthy ownership;
- an expired read-only runtime lease may transfer to another replica;
- stale generations cannot renew/finalize/publish as current owner;
- recovered runtime work can complete evaluation/terminal persistence;
- private handoff payload is removed after terminal completion.

This is a repository-level correctness claim, not proof of deployed HA, autoscaling, multi-region failover, RTO/RPO or uptime.

## 4. Consequential-action architecture

Consequential actions use a distinct non-transferable ownership contract:

```text
agent ACTION proposal
→ deterministic scope/schema/permission/evidence validation
→ private PostgreSQL action custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ current authorization + host kill switch revalidated
→ atomic persistent idempotency claim
→ non-transferable PostgreSQL action execution lease
→ exact custodied payload executes
→ lease-fenced custody/ledger/observability persistence
→ action RunTrace
→ ProductionActionEvaluator
→ safe REST/SSE/frontend projection
```

Safety properties:

- proposal is never execution;
- browser confirmation cannot supply raw args, tenant/identity/permissions or idempotency material;
- action custody is private and separate from safe observability projections;
- duplicate confirmation does not create a replacement transport call;
- an action execution lease is not transferred to another replica;
- lost/stale ownership converges to `UNCERTAIN`;
- stale late responses cannot overwrite `UNCERTAIN` with a false terminal success/failure;
- no blind replay/retry is authorized after ambiguous external-side-effect ownership loss.

The product deliberately does **not** claim distributed exactly-once external side effects because the external TRACTIAN API does not participate in a shared fencing/idempotency transaction.

## 5. Identity and tenant isolation

The current promoted identity boundary is the project-owned `academy-runtime-v1` signed bearer envelope:

- HMAC-SHA256 verification;
- issuer/audience/lifetime checks;
- explicit `organization_id`, `user_id`, `identity_id`, role and permissions;
- tenant/identity/permission data is server-trusted, not taken from browser request bodies;
- privileged permissions require explicit server enablement.

It is intentionally **not** described as OAuth/OIDC/JWT, enterprise SSO or complete production IAM.

PostgreSQL provides an independent tenant boundary through RLS using a non-superuser, non-`BYPASSRLS`, non-owner application role and transaction-local organization scope. Integration tests prove cross-tenant denial for tested rows.

## 6. Persistence architecture

Promoted production-path persistence:

```text
PostgreSQL  run ownership/execution + tenant isolation
PostgreSQL  runtime handoff payload/lease/generation state
PostgreSQL  action custody/idempotency/non-transferable leases
PostgreSQL  sanitized observability runs/events/evidence/evaluations
PostgreSQL  semantic-review collection state
PostgreSQL  operational-value collection state
DuckDB      optional dev/benchmark compatibility only
```

The root production package depends on PostgreSQL/psycopg, not DuckDB. DuckDB remains an optional development/benchmark extra and must not be described as the promoted serving/read-model truth.

## 7. Realtime observability

```text
canonical runtime transition
→ immutable/sanitized PostgreSQL event row
→ authoritative (run_id, sequence) cursor
→ transaction commit
→ PostgreSQL NOTIFY wake-up
→ one listener per application replica
→ local fan-out + bounded durable catch-up reads
→ FastAPI SSE
→ idempotent React reducer
→ Live Run / Trace / Architecture / Health / Analytics
```

Rules:

- durable PostgreSQL rows/cursors are truth;
- `LISTEN/NOTIFY` is wake-up only;
- missed notifications are recoverable through durable cursor reads;
- tenant authorization never depends on notification payloads;
- event publication cannot expose raw identity, private custody, evaluator-only truth or chain-of-thought;
- browser reconnect uses persisted sequence state rather than fabricated progress.

The RT-WAKEUP comparison promoted LISTEN/NOTIFY over polling after hard gates remained green and the successful rerun measured event p95 improvement plus lower idle durable-read volume. Runner variance remains part of the evidence record.

## 8. Frontend architecture

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
      ├── Action Control
      ├── Tools & Policy analytics
      ├── Eval Lab
      ├── Provider Lab
      ├── Dynamic Data Explorer
      └── Production Health
```

The frontend observes server-owned safe state. It is not an authorization source, policy engine, evaluator or owner of tenant scope.

A selected run should be able to answer, from safe structured data:

1. which components participated;
2. which component produced each visible output;
3. which evidence/tool transition fed it;
4. why the run stopped or escalated at the structured reason-code level;
5. what evaluation occurred after runtime completion;
6. whether an action was proposed, pending, confirmed, executed, rejected or uncertain.

Do not expose hidden model chain-of-thought.

## 9. Current dependency stack

### Backend/runtime

| Layer | Technology | Current state |
|---|---|---|
| Language | Python >=3.11 | preferred/current |
| Typed schemas | Pydantic >=2.6,<3 | preferred |
| Product/API | FastAPI >=0.141.1,<0.142 | preferred |
| ASGI serving | Uvicorn >=0.52.4,<0.53 | preferred |
| PostgreSQL client/pool | psycopg[binary,pool] >=3.2,<4 | promoted |
| Agent orchestration | custom `AgentController` | promoted baseline |
| Tool execution | `HarnessRunner` | hard boundary |
| Tool contracts | typed `ToolSpec` registry | current 18-operation scope |
| Evaluation | deterministic-first custom evaluator/campaigns | promoted primary layer |
| Tests | pytest | preferred |
| Packaging | hatchling/wheel | clean-clone proved |
| DuckDB | optional dev/benchmark extra | not production dependency |

### Frontend

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
| Playwright | 1.62.0 |

`frontend/package-lock.json` is committed and CI uses deterministic `npm ci` in the current reproduction/browser paths.

## 10. Agent techniques

### Typed tool-augmented iterative loop

```text
decision
→ optional typed tool proposal
→ deterministic policy/validation
→ execution
→ normalized observation
→ next decision or terminal outcome
```

### Evidence-aware outcomes

First-class terminal/interaction behavior:

- orient/final;
- continue investigation;
- clarify;
- abstain;
- escalate;
- bounded action proposal.

### Bounded execution

- hard turn/tool budgets;
- deterministic safety caps;
- safe terminal behavior on exhaustion/failure;
- no uncontrolled retry/fallback on governed experiment paths.

### Robustness dimensions

Evaluation explicitly covers complete, partial, inconclusive, conflicting and unavailable evidence; tool/provider failures; invalid arguments; denied actions; and insufficient evidence.

## 11. Evaluation architecture

Primary promoted layer:

```text
RunTrace
→ deterministic structural/safety/trajectory evaluator
→ safe PostgreSQL evaluation projection
→ Eval Lab / EDD comparison
```

Human-dependent semantic closure remains separate:

```text
blinded human-labelled sample
→ independent adjudication where required
→ semantic judge candidate(s)
→ judge-vs-human agreement/error analysis
→ accept / reject / recalibrate judge
```

Semantic judges cannot receive runtime-hidden gold/private evaluator information, and they cannot displace deterministic exact checks where structural ground truth exists.

Current repository includes the collector, rubric, calibration protocol and trusted VALIDATION source generation, but **real human labels/adjudication do not yet exist**, so a human semantic-calibration claim is not authorized.

## 12. Operational-value architecture

The project provides server-owned collection and frozen paired analysis for MANUAL × ASSISTED investigations.

The intended primary business metric is elapsed time to a correct operational decision, with correctness/safety/escalation evidence preserved separately.

Real human observations are still required. The repository must not fabricate engineer-time savings or auto-resolution value.

## 13. Adaptive-policy state

The current runtime baseline remains bounded/fixed. Adaptive stopping exists as an evaluator/replay diagnostic only.

Potential future adaptive choices may include investigation continuation, clarification/escalation thresholds or routing, but promotion requires:

```text
observable runtime features only
→ preregistered challenger
→ same hard safety envelope
→ locked controlled evaluation
→ material Pareto improvement
→ promotion decision
```

Auth, tenant isolation, permissions, action confirmation, custody, idempotency, leases/fencing and other hard safety boundaries remain deterministic.

No adaptive runtime-stopping policy is currently promoted.

## 14. Framework and topology decision states

| Area | Current state | Rule |
|---|---|---|
| Native typed tools | PREFERRED | current hard tool boundary |
| MCP | NO_CHANGE | add only for measured interoperability need |
| Custom AgentController | PREFERRED | current promoted controller |
| LangGraph | QUALIFIED/HISTORICAL challenger | no migration without measured advantage |
| Multi-agent | NO_CHANGE | no measured topology gap |
| RAG/vector/hybrid/reranking | NO_CHANGE | no measured retrieval gap |
| Persistent memory | NO_CHANGE | no demonstrated cross-request need |
| Adaptive stopping | EVALUATOR-ONLY | runtime promotion requires oracle-free challenger win |
| Provider routing | DEFERRED | requires production-eligible alternatives and new experiment |
| FastAPI | PREFERRED | current Python API/SSE fit |
| REST + SSE | PREFERRED | one-way telemetry + REST commands |
| React + Vite | PREFERRED | operator SPA fit |
| ECharts | PREFERRED | dynamic analytics |
| React Flow | PREFERRED | trace/architecture graph |
| PostgreSQL serving state | PROMOTED | operational + observability/evaluation truth |
| DuckDB | DEV/BENCHMARK ONLY | no production serving claim |
| PostgreSQL LISTEN/NOTIFY | PROMOTED WAKE-UP | durable rows remain truth |
| OpenTelemetry | NOT YET PROMOTED | candidate for external/platform telemetry, not product truth |
| Redis/Kafka/shared bus | NO_CHANGE | require measured throughput/realtime gap |

## 15. Provider experiment state

Historical D01/D02 Cloudflare experiments are complete and consumed. D02 improved several public metrics after the controlled completion-budget change, but no candidate crossed all frozen promotion gates.

Current provider decision:

**`NO_SELECTION` / no production provider claim.**

The Cloudflare implementation/workflow/ADR family is retained as historical research evidence. Its presence does not make Cloudflare the promoted production provider and does not authorize replay of consumed experiment packets.

A future hosted-provider tournament requires a new experiment/protocol and must compare quality, safety, latency, reliability and cost under the same workload/hard gates.

## 16. Reproduction and CI architecture

The stable top-level product CI contract is:

```text
final-ci-required
  ├── clean-clone-full-product-reproduction
  ├── full-product-playwright
  ├── horizontal-runtime-handoff
  └── action-execution-lease
        ↓
  required-gate
```

Clean-clone reproduction covers the Python/PostgreSQL product suite, distributed correctness regressions, accepted controller/safety evidence, historical final evidence validation, frontend lockfile install/typecheck/tests/build and repository cleanliness.

Full Chromium acceptance exercises real backend/frontend/PostgreSQL/SSE behavior with provider-free deterministic decision input.

Historical E-series/BIG-B/provider experiment workflows are evidence/reproduction surfaces and are not ordinary product-PR gates.

## 17. Current non-claims

Do not claim:

- a production provider/model has been selected;
- OAuth/OIDC/enterprise SSO is implemented;
- human semantic calibration is complete;
- engineer minutes saved without real human observations;
- adaptive stopping improves production runtime behavior;
- CI load results establish production capacity/SLOs;
- repository restart/cross-replica tests establish deployed RTO/RPO, HA, autoscaling, multi-region failover or uptime;
- distributed exactly-once external side effects;
- branch protection is enforced until GitHub reports it active;
- LangGraph, multi-agent, RAG, memory, MCP, Kafka, Redis or another platform component is superior without a measured gap and challenger win.

## 18. Architecture change gate

Any material framework, topology, store, model/provider, retrieval, memory, routing, deployment or frontend-data-path proposal must follow:

```text
material requirement / measured gap
→ current/simple baseline
→ systematic research
→ credible alternatives
→ preregistered metrics + hard gates
→ controlled comparison
→ uncertainty/failure/production-fit analysis
→ Pareto decision
→ ADR + reversal trigger
→ regression protection
```

Without evidence of material benefit, `NO_CHANGE` is the correct architecture decision.
