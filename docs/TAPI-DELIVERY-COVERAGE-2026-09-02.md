# TAPI Delivery Coverage — Active Crosswalk

**Status:** ACTIVE assignment/output reference  
**Original filename checkpoint:** 2026-09-02  
**Current rebaseline:** 2026-09-06 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)

This crosswalk separates **TAPI/delivered-package expectations** from **project-added production/quality constraints**.

## 1. Integrated deliverable

The project delivers:

1. **Industrial Agent** — contextualizes/investigates industrial requests through typed TRACTIAN operations and produces safe operational outcomes/proposals.
2. **Agent Evaluation Framework** — evaluates observable tool/argument/trajectory/evidence/terminal/safety/failure/stability behavior and supports controlled experiments.

Operational intent: `CONTEXTUALIZE`, `INVESTIGATE`, `EXECUTE` (Release 0 Execute is proposal-only).  
Terminal behavior: `FINAL/ORIENT`, `CLARIFY`, `ABSTAIN`, `ESCALATE`, plus governed action proposal state.

## 2. TAPI/delivery expectations mapped to product evidence

| Expectation | Current evidence / boundary |
|---|---|
| functional agent | hosted Release 0 provider→controller→tool→evidence→terminal path |
| supplied TRACTIAN API use | canonical 18-operation typed contract; 13 reads live in Release 0 |
| function/tool selection | ToolSpec proposals + trace/evaluator |
| argument validity | typed schema/B1 validation + evaluator/tests |
| execution process/trajectory | RunTrace, Evidence timeline, Trace Graph |
| evidence use | persisted evidence IDs, normalized read semantics, lineage |
| response/conclusion | customer-safe terminal outcome + mode-specific next step |
| clarification | hosted CLARIFY acceptance |
| abstention | hosted ABSTAIN acceptance |
| human escalation | hosted ESCALATE acceptance |
| safety/high-impact behavior | deterministic policy + action proposal-only Release 0 boundary |
| failure/degraded behavior | provider/tool/evidence failure campaigns + safe modes |
| stability | repeated/campaign evaluation surfaces |
| technical experiment | frozen provider/architecture/evaluator experiment evidence |
| result analysis | machine-readable results + Engineering evaluation/analytics surfaces |
| reproducibility | clean clone, lockfiles, required CI, exact release identity |
| documentation | active docs hub + ADRs + runbook + changelog + preserved evidence |
| demonstration | normal hosted product with Results/Evidence/Investigation/Engineering |

## 3. Project-added hard constraints

These are deliberate project rules, not presented as literal TRACTIAN wording:

- actual project cash cost = USD0;
- no automatic paid spillover;
- remote production serving with no developer-machine dependency;
- multi-user tenant safety;
- systematic research before material decisions;
- quantitative/Eval-Driven Development;
- adaptive behavior only after measured advantage over a simpler baseline;
- safe live frontend observability.

Additional final-quality gates include hosted security, capacity/SLO, restore/recovery, human semantic calibration and operational-value evidence.

## 4. Current stack and state

| Layer | Current choice/state |
|---|---|
| language | Python 3.11+ |
| API | FastAPI + Uvicorn |
| typed schemas | Pydantic 2.x |
| orchestration | custom `AgentController` promoted baseline |
| real tool boundary | `HarnessRunner` + canonical `ToolSpec` registry |
| TRACTIAN transport | direct typed HTTPS adapter; live reads proved |
| durable state | Neon PostgreSQL + psycopg |
| browser IAM | managed Neon Auth/session, server-owned scope |
| backend/frontend hosting | Railway production services |
| model/provider | Cloudflare GLM-4.7-Flash provisional Release 0; final decision `NO_SELECTION` |
| evaluation | deterministic-first production evaluator + controlled research layers |
| realtime | durable Postgres cursor + LISTEN/NOTIFY wake-up + authenticated SSE |
| frontend | React/TypeScript/Vite/Caddy, progressive Results/Evidence/Investigation/Engineering |

## 5. 18-operation contract

Release 0 browser-safe capability reference exposes:

```text
18 total canonical operations
13 READ  → live read path when release provider + TRACTIAN transport are enabled
5 ACTION → proposal-only; external execution disabled
```

This allows the complete assignment capability surface to remain inspectable without pretending Release 0 executes consequential changes.

## 6. User/reviewer outputs

Current product outputs include:

- customer-safe terminal outcome and next step;
- read/evidence semantics;
- canonical timeline;
- evidence references;
- tool/model/policy provenance;
- Trace Graph;
- output/evaluation lineage;
- deterministic post-runtime evaluation;
- persisted history and SSE/reconnect;
- architecture/capability views;
- proposal-only action/policy state;
- operations/analytics research surfaces in Engineering.

The current UX exposes these through four depths rather than placing all technical information on the first screen.

## 7. Evaluation coverage

The evaluation system is designed to inspect:

- correct function/tool;
- argument validity;
- trajectory/process;
- evidence/provenance;
- final operational conclusion;
- clarification/abstention/escalation;
- action safety;
- provider/tool/runtime failures;
- repeated-run stability;
- reproducible config/result identities;
- baseline-vs-candidate deltas.

Deterministic checks remain authoritative where exact truth exists. Semantic judges remain non-gating until real human calibration.

## 8. What is deliberately not promoted

LangGraph migration, multi-agent topology, RAG/vector DB, persistent memory, MCP, Redis/Kafka, Kubernetes/microservices and adaptive runtime stopping/routing are not required merely because they are modern or appear in examples. They need a measured gap, USD0 eligibility and a controlled challenger win.

## 9. Remaining final-delivery evidence

Release 0 closes the real user/read-only product path. Final work still includes as applicable:

- full Provider Tournament v3;
- SECURITY-V1 hosted campaign;
- load/capacity and evidence-derived SLO;
- restore/recovery evidence;
- governed consequential action execution if promoted;
- human semantic calibration;
- real operational-value comparison;
- final evidence freeze.

## 10. Demonstration contract

Demonstrate the **normal hosted product**:

```text
sign in
→ Results: real request + live progress + conclusion
→ Evidence: supporting trail
→ Investigation: runtime/history/trace/action boundary
→ Engineering: evaluator/architecture/capabilities
→ exact limitations/non-claims
```

No separate demo-only, local or paid serving stack is compatible with the project claim.