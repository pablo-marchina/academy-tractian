# TAPI Delivery Coverage — Active Crosswalk

**Status:** ACTIVE assignment/output reference  
**Original filename checkpoint:** 2026-09-02  
**Current rebaseline:** 2026-09-07 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)

This crosswalk separates TAPI/delivered-package expectations from project-added production/quality constraints.

## 1. Integrated deliverable

The project delivers:

1. **Industrial Agent** — contextualizes/investigates industrial requests through typed TRACTIAN operations and produces safe grounded outcomes/proposals.
2. **Agent Evaluation Framework** — evaluates observable tool/argument/trajectory/evidence/terminal/safety/failure/stability behavior and supports controlled experiments.

Release 0 Execute remains proposal-only; external consequential action execution is disabled.

## 2. TAPI/delivery expectations mapped to current evidence

| Expectation | Current evidence / boundary |
|---|---|
| functional agent | hosted V13 provider→controller→tool→evidence→terminal path |
| supplied TRACTIAN API use | canonical 18-operation typed contract; multiple real read paths proven |
| function/tool selection | ToolSpec proposals + trace/evaluator |
| argument validity | typed schema/B1 validation + resource-ID constraints |
| resource grounding | authenticated identity/company/fleet + structured observed IDs |
| process/trajectory | RunTrace + Technical Current analysis / trace |
| evidence use | persisted evidence IDs, normalized read semantics, lineage |
| response/conclusion | customer-safe terminal + explicit `response_mode` semantics |
| clarification/abstention/escalation | promoted terminal behavior + persisted traces |
| missing resource | V13 R420 case fails closed without invented ID/scope |
| data quality | V13 explicit quality read + condition evidence path |
| condition diagnosis | V13 mandatory analysis/RMS/spectrum evidence gate |
| safety/high-impact behavior | deterministic policy + external actions disabled |
| failure/degraded behavior | provider/tool/evidence/auth failure semantics + safe modes |
| stability | repeated/campaign evaluation surfaces; broader live matrix pending |
| technical experiment | frozen provider/architecture/evaluator evidence |
| result analysis | machine-readable results + Technical evaluation/analytics surfaces |
| reproducibility | clean clone, lockfiles, required CI, exact release identity |
| documentation | active docs + ADRs + runbook + changelog + append-only evidence |
| demonstration | normal hosted task-driven product + Technical depth |

## 3. Project-added hard constraints

- actual project cash cost = USD0;
- no automatic paid spillover;
- remote production serving with no developer-machine dependency;
- multi-user tenant safety;
- systematic research before material decisions;
- quantitative/Eval-Driven Development;
- adaptive behavior only after measured advantage over simpler baseline;
- safe live frontend observability.

Final-quality gates include hosted security, capacity/SLO, restore/recovery, human semantic calibration and operational-value evidence.

## 4. Current stack/state

| Layer | Current choice/state |
|---|---|
| language | Python 3.11+ |
| API | FastAPI + Uvicorn |
| schemas | Pydantic 2.x |
| orchestration | custom `AgentController` promoted baseline |
| provider wrapper | Release 0 V13 (`release_provider_v13.py`) |
| real tool boundary | `HarnessRunner` + canonical ToolSpec registry |
| TRACTIAN transport | direct typed HTTPS adapter; live reads proved |
| durable state | Neon PostgreSQL + psycopg |
| browser IAM | Neon managed session, server-owned scope, bounded read cache |
| hosting | Railway production services |
| provider | Cloudflare GLM-4.7-Flash provisional; final decision `NO_SELECTION` |
| evaluation | deterministic-first production evaluator + controlled research layers |
| realtime | durable Postgres cursor + LISTEN/NOTIFY wake-up + authenticated SSE |
| frontend | React/TypeScript/Vite/Caddy, task-driven Home / Analyses / Technical |

## 5. 18-operation contract

```text
18 total canonical operations
13 READ  → Release 0 read surface when provider + TRACTIAN transport enabled
5 ACTION → represented/proposal-only; external execution disabled
```

Current live testing does **not** yet claim every one of the 13 reads has been exercised by a recent V13 user prompt. Contract coverage and live exercised coverage are distinct metrics.

## 6. Current agent behavior relevant to TAPI

### Discover instead of ask unnecessarily

For asset investigations, V13 uses server-owned identity/company context and fleet listing to resolve discoverable IDs. Human labels like R310 are not treated as raw internal authority.

### Investigate with evidence appropriate to the question

- condition/diagnostic questions require analysis/RMS/spectrum evidence where applicable;
- baseline/data-quality support context but do not replace condition evidence;
- data-quality questions explicitly inspect data quality;
- comparisons require evidence per requested asset;
- missing requested resource returns bounded unavailability.

### Communicate uncertainty

`response_mode` separates evidence completeness from the controller terminal:

`complete | partial | inconclusive | conflict | unavailable`

This prevents ordinary causal uncertainty from being mislabeled as total inconclusiveness while still bounding unsupported claims.

## 7. User/reviewer outputs

Current product exposes:

- customer-safe result and next step;
- response/evidence semantics;
- contextual evidence references;
- persisted history;
- safe tool/model/policy provenance;
- trace/runtime inspection;
- deterministic post-runtime evaluation;
- architecture/capability views;
- proposal-only action/policy state;
- analytics/research surfaces under Technical.

The current UI organizes these by task rather than by four permanent engineering-depth tabs.

## 8. Evaluation coverage

Evaluation is designed to inspect correct function/tool, argument validity, trajectory, evidence/provenance, final operational conclusion, clarification/abstention/escalation, action safety, failures, repeated-run stability, reproducible identities and baseline-vs-candidate deltas.

Current V13 live traces pass structural blocking checks for their tested scope. Semantic judges remain non-gating until real human calibration.

## 9. Deliberately not promoted

LangGraph migration, multi-agent topology, RAG/vector DB, persistent memory, MCP, Redis/Kafka, Kubernetes/microservices and adaptive stopping/routing need a measured gap, USD0 eligibility and controlled challenger win.

## 10. Remaining final-delivery evidence

- broader recent V13 live coverage across canonical reads;
- true bilateral comparison with two real fleet assets;
- knowledge/model/analysis/baseline live coverage;
- anti-hallucination/false-precision/conflict prompt matrix;
- multi-turn behavior if required;
- full Provider Tournament v3;
- SECURITY-V1;
- load/capacity and evidence-derived SLO;
- restore/recovery;
- governed consequential actions if promoted;
- human semantic calibration;
- real operational-value comparison;
- final evidence freeze.

## 11. Demonstration contract

Demonstrate the **normal hosted product**:

```text
sign in
→ Home: real equipment question
→ Result: conclusion + response mode + evidence
→ Analyses: persisted alternate run
→ Technical: trace / evaluator / architecture / actions
→ exact limitations/non-claims
```

No separate demo-only, local or paid serving stack is compatible with the project claim.