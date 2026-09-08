# TAPI Delivery Coverage — Active Crosswalk

**Status:** ACTIVE assignment/output reference  
**Original filename checkpoint:** 2026-09-02  
**Current rebaseline:** 2026-09-08 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Latest material progress:** [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md)

This crosswalk maps the **updated TAPI** to current product/evidence while separating explicit assignment requirements from project-added production constraints. Historical Release 0/V13 evidence remains valid for its original scope but is not the current runtime state.

## 1. Integrated deliverable required by the updated TAPI

The solution contains both required tracks:

1. **Industrial Agent** — contextualizes, investigates and may execute/escalate through typed TRACTIAN operations while preserving safe authority boundaries.
2. **Agent Evaluation Framework** — evaluates observable tool/function selection, arguments, trajectory, evidence, response, safety/high-impact behavior, failure and stability with reproducible provenance.

The updated TAPI expects API integration, technical experimentation and documented results/limitations. The project therefore treats configuration, deployment, functional acceptance, evaluation and final claims as separate evidence classes.

## 2. TAPI expectation → current evidence / boundary

| TAPI expectation | Current evidence / boundary |
|---|---|
| integrated agent | production runtime exists; current OpenRouter V14 provider migration is deployed but authenticated functional gate is currently **FAIL** |
| supplied TRACTIAN API use | canonical 18-operation contract; historical real read evidence; controlled 5/5 governed action transport smoke |
| contextualize | managed identity/tenant + authenticated fleet discovery + persisted run context |
| investigate | typed tool proposals and evidence-driven controller/harness loop |
| execute justified platform actions | governed action custody/confirmation/authorization/idempotency/lease/upstream-actor architecture; controlled transport smoke 5/5; final adversarial/end-user acceptance pending |
| ask relevant questions | clarification terminal exists; discoverable internal IDs should be resolved rather than requested |
| escalate to human | ESCALATE terminal + governed `escalate_case` action contract |
| function/tool selection | typed DecisionSource proposal + ToolSpec registry + trace/evaluator |
| argument accuracy | strict schema/B1 validation + observed-resource constraints + normalized argument fingerprints |
| planning/stopping | custom `AgentController`, hard budgets and exact-success duplicate suppression; progressive drill-down preserved |
| incomplete/failure handling | bounded complete/partial/inconclusive/conflict/unavailable + explicit provider/tool/auth/action failure states |
| grounding | IDs only from authorized structured observations; human asset labels resolved via authenticated fleet |
| memory/context | durable run/runtime context where needed; no unsupported persistent-memory layer claim |
| traceability | PostgreSQL run/event/evidence/evaluation/verification projections + exact release/provider provenance |
| high-impact safety | deterministic action authority; proposal ≠ execution; server-owned grants/actors/kill switch/idempotency/leases |
| technical experiment | provider tournament/eligibility, V14 response-shape/length/rate-limit experiments, action/security/evaluator campaigns |
| documented results | append-only progress/evidence, ADRs, manifests, machine-readable experiment results, active acceptance ledger |
| reproducibility | exact SHA/deployment identities, lockfiles, required CI, clean-clone/browser workflows |
| demonstration | normal hosted task-driven product; no separate demo-only stack |

## 3. Current product-added hard constraints

These are stronger than the assignment minimum and must remain true for project claims:

```text
actual project cash cost = USD 0
no automatic paid spillover
no local production dependency
multi-user tenant isolation
server-owned action authority
quantitative / Eval-Driven Development
adaptive behavior only after measured advantage
live safe observability
claims no stronger than evidence
```

## 4. Current stack / architecture state

| Layer | Current promoted choice/state |
|---|---|
| language | Python 3.11+ |
| API | FastAPI + Uvicorn |
| schemas | Pydantic 2.x |
| orchestration | custom `AgentController` baseline |
| provider wrapper | `release_provider_v14.py` preserving V13 agent semantics |
| hosted provider | OpenRouter fixed-free route, provisional |
| exact model | `nvidia/nemotron-3-super-120b-a12b:free` |
| provider fallback | disabled |
| tool boundary | `HarnessRunner` + canonical ToolSpec registry |
| TRACTIAN transport | typed real HTTP transport; 13 reads + 5 governed action operations |
| actions | governed server-owned authorization/custody/confirmation/idempotency/lease/actor path |
| durable state | Neon PostgreSQL + psycopg |
| tenant boundary | server-owned scope + PostgreSQL RLS |
| browser IAM | Neon managed session; bounded validated read cache; fresh non-read validation |
| evaluation | deterministic-first post-runtime evaluator + independent verification + research layers |
| realtime | durable PostgreSQL cursor + LISTEN/NOTIFY wake-up + authenticated SSE |
| frontend | React/TypeScript/Vite/Caddy; Home / Analyses / Technical |
| hosting | Railway production services |

No evidence currently justifies replacing this with LangGraph/multi-agent/RAG/vector DB/MCP/Redis/Kafka/Kubernetes.

## 5. Canonical 18-operation contract

```text
18 total operations
13 READ
5 ACTION
```

Current claim discipline:

- **contract coverage**: 18/18 represented;
- **historical recent read evidence**: multiple real paths proven before V14;
- **current V14 B204 read execution**: `NOT REACHED` because the provider first decision failed;
- **governed action transport**: controlled smoke 5/5 accepted HTTP 200;
- **full recent 13-read live coverage**: `PENDING`;
- **full action security/end-user acceptance**: `PENDING`.

Do not collapse these into one generic “API integration PASS”.

## 6. Current OpenRouter V14 functional gate

Production backend `5611687556b3d50c31f20fa85ede794f2500f05c` uses:

```text
provider = openrouter
model    = nvidia/nemotron-3-super-120b-a12b:free
route    = openrouter.chat_completions.v1.fixed_free
```

Real managed-session B204 runs:

```text
run_437a59ba893a96e3f902  F01 condition
run_86c832ce46189200b613  F02 causal
run_f081d5d45b0cf4caf4b3  F03 data quality
```

All 3 currently fail functional acceptance with `DECISION_SOURCE_FAILURE` and zero TRACTIAN tool calls.

Safe provider diagnosis observed:

```text
HTTP 200
exact pinned model served
assistant content present
finish_reason = length
```

V14 correctly refuses the truncated completion. A bounded follow-up comparison received HTTP 429 for every variant, so the proposed fix remains `INCONCLUSIVE` rather than promoted.

This is a useful TAPI-aligned experiment: hypothesis, controlled variants, sanitized evidence, explicit limitation and no result laundering.

## 7. Agent behavior relevant to TAPI

### Contextualize / discover instead of asking unnecessarily

Human-readable asset labels resolve through managed identity/company/fleet observations. The model does not get to invent tenant/company/resource IDs.

### Investigate with appropriate evidence

- condition/diagnostic questions require condition evidence where applicable;
- baseline/data quality do not substitute for fault evidence;
- explicit data-quality questions require data-quality evidence;
- comparisons require evidence per selected resource;
- missing resources fail closed.

### Stop adaptively without losing deterministic safety

The controller may adapt tool ordering/depth to observed evidence, but authority/safety remains deterministic. Exact successful duplicate operation + normalized arguments/resource is suppressed; same-tool/different-argument drill-down may remain valid.

### Communicate uncertainty

Customer-visible evidence semantics remain:

```text
complete | partial | inconclusive | conflict | unavailable
```

These are epistemic states, not permission states.

## 8. Execute / high-impact action path

The project now goes beyond proposal-only architecture. Current governed execution path is:

```text
model proposes exact canonical action
→ deterministic schema/resource/permission checks
→ private PostgreSQL custody
→ explicit opaque-ID confirmation
→ fresh server-owned tenant/user authorization + kill switch
→ persistent idempotency
→ non-transferable action lease/fencing
→ server-owned upstream TRACTIAN actor
→ one bounded external attempt
→ ACCEPTED | NOT_ACCEPTED | BLOCKED | UNCERTAIN
→ post-action evaluation + safe projection
```

Controlled production pre-deploy evidence accepted all five canonical action transports. Final full hosted adversarial action security/semantic acceptance is still open, so the defensible claim is **governed action transport proven in controlled scope**, not “all consequential action behavior production-certified”.

## 9. Evaluation framework coverage

The project evaluates or has dedicated surfaces for:

- tool/function selection;
- arguments/resource grounding;
- trajectory/stopping/duplicate calls;
- evidence completeness/provenance;
- terminal/response mode;
- provider/model/release provenance;
- safety/authorization/high-impact actions;
- failures/degraded dependencies;
- repeated-run stability;
- independent claim/evidence verification;
- semantic calibration protocol;
- operational-value protocol.

Structural evaluation is not presented as semantic correctness. Current V14 B204 is the explicit counterexample: runtime/auth plumbing can work while functional task execution fails.

## 10. User/reviewer outputs

Hosted UI exposes, as appropriate:

- customer result and next step;
- response/evidence semantics;
- evidence/lineage;
- persisted history;
- tool/model/policy/release provenance;
- trace/runtime inspection;
- deterministic evaluation + verification distinction;
- architecture/capability/action state;
- research/analytics surfaces.

Technical depth must never expose credentials, grant/custody material, benchmark-private gold or hidden reasoning.

## 11. Deliberately not promoted

`NO_CHANGE` absent a measured gap/challenger win:

- LangGraph migration;
- multi-agent topology;
- RAG/vector DB;
- persistent memory;
- MCP;
- Redis/Kafka;
- Kubernetes/microservices;
- adaptive runtime routing/stopping as a promoted replacement.

The current blocker is provider completion/availability, not evidence for architectural complexity.

## 12. Remaining final-delivery evidence

Immediate:

1. safely characterize OpenRouter key-tier/rate-limit eligibility;
2. reproduce/compare bounded V14 length fixes under eligible conditions;
3. exact-SHA CI/deploy;
4. make B204 F01/F02/F03 3/3 with real TRACTIAN calls + valid terminal/evaluation.

Then:

- broad current 13-read coverage;
- full governed-action SECURITY-V1;
- anti-hallucination/false-precision/conflict and dependency failure matrix;
- remote load staircase/soak + measured capacity/evidence-derived SLO;
- real restore drill + measured RTO/RPO;
- human semantic calibration;
- MANUAL vs AGENT-ASSISTED operational-value study;
- final provider experiment/selection or explicit `NO_SELECTION`;
- GitHub branch protection;
- exact accepted-production SHA convergence;
- final immutable evidence freeze.

## 13. Demonstration contract

Demonstrate the **normal hosted product**, not a separate demo stack:

```text
sign in
→ Home: real equipment question
→ real provider/tool/evidence path
→ Result: conclusion + response mode + evidence
→ Analyses: persisted history
→ Technical: trace / evaluator / verification / architecture / actions
→ exact release/provider/action state
→ explicit limitations/non-claims
```

Until V14 is functionally green, do not present the current failing B204 path as the final successful agent demonstration. Historical successful V13 runs may be shown only when clearly labeled historical evidence.