# TAPI Delivery Coverage — Active Crosswalk

**Status:** ACTIVE assignment/output reference  
**Original filename checkpoint:** 2026-09-02  
**Current rebaseline:** 2026-09-07 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Current backend source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`

This crosswalk separates TAPI/delivered-package expectations from project-added production/quality constraints.

## 1. Integrated deliverable

The project delivers:

1. **Industrial Agent** — contextualizes/investigates industrial requests through typed TRACTIAN operations and produces safe grounded outcomes/proposals; consequential actions use a separate governed confirmation/execution boundary.
2. **Agent Evaluation Framework** — evaluates observable tool/argument/trajectory/evidence/terminal/safety/failure/stability behavior and supports controlled experiments.

The original Release 0 acceptance was read-only. Current production has subsequently promoted governed action execution architecture. Complete five-action vendor acceptance remains an open gate and must not be inferred from capability/configuration state.

## 2. TAPI/delivery expectations mapped to current evidence

| Expectation | Current evidence / boundary |
|---|---|
| functional agent | hosted V13 provider→controller→tool→evidence→terminal path |
| supplied TRACTIAN API use | canonical 18-operation typed contract; multiple live reads + governed action endpoints integrated |
| function/tool selection | ToolSpec proposals + trace/evaluator |
| argument validity | typed schema/B1 validation + resource-ID constraints |
| resource grounding | authenticated identity/company/fleet + structured observed IDs |
| process/trajectory | RunTrace + Technical analysis/trace |
| evidence use | persisted evidence IDs, normalized read semantics, lineage |
| response/conclusion | customer-safe terminal + explicit `response_mode` semantics |
| clarification/abstention/escalation | promoted terminal behavior + persisted traces |
| missing resource | V13 R420 case fails closed without invented ID/scope |
| data quality | V13 explicit quality read + condition evidence path |
| condition diagnosis | V13 mandatory analysis/RMS/spectrum evidence gate |
| safety/high-impact behavior | exact custody/confirmation + server-owned grant/resource scope + idempotency + lease/fencing; 5/5 vendor acceptance pending |
| failure/degraded behavior | provider/tool/evidence/auth/action failure semantics + safe modes; live action 403 failed deployment safely |
| stability | repeated/campaign evaluation surfaces; broader live matrix pending |
| technical experiment | frozen provider/architecture/evaluator evidence |
| result analysis | machine-readable results + Technical evaluation/analytics surfaces |
| reproducibility | clean clone, lockfiles, required CI, exact release identity, fresh-snapshot deployment discipline |
| documentation | active docs + ADRs + runbooks + changelog + append-only evidence |
| demonstration | normal hosted task-driven product + Technical depth + truthful action limitation |

## 3. Project-added hard constraints

- actual project cash cost = USD0;
- no automatic paid spillover;
- remote production serving with no developer-machine dependency;
- multi-user tenant safety;
- systematic research before material decisions;
- quantitative/Eval-Driven Development;
- adaptive behavior only after measured advantage over simpler baseline;
- deterministic action authority/confirmation/idempotency/lease boundaries;
- safe live frontend observability;
- claims no stronger than hosted/vendor evidence.

Final-quality gates include hosted security, action vendor-identity acceptance, capacity/SLO, restore/recovery, human semantic/usability calibration and operational-value evidence.

## 4. Current stack/state

| Layer | Current choice/state |
|---|---|
| language | Python 3.11+ |
| API | FastAPI + Uvicorn |
| schemas | Pydantic 2.x |
| orchestration | custom `AgentController` promoted baseline |
| provider wrapper | Release 0 V13 (`release_provider_v13.py`) |
| real tool boundary | `HarnessRunner` + canonical ToolSpec registry |
| TRACTIAN transport | direct typed HTTPS adapter; live reads proved; governed writes integrated |
| action control | PostgreSQL custody/idempotency/execution lease + server-owned grants + exact confirmation |
| vendor action identity | company+permission server-owned actor routing designed/in progress; not yet live-proven |
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
13 READ
  → live Release 0 read surface when provider + TRACTIAN transport enabled

5 ACTION
  → governed confirmation/execution path implemented and enabled in production config
  → local safety architecture CI-qualified
  → full vendor acceptance still NOT PROVEN
```

Canonical actions/permissions:

```text
reprocess_analysis             action_low
request_specialist_analysis    action_low
update_asset_config            action_high
request_retraining             action_high
escalate_case                  escalate
```

Current live testing does **not** yet claim every one of the 13 reads has been exercised by a recent V13 user prompt. Contract coverage and live exercised coverage are distinct metrics.

Likewise, five executable action capabilities do not mean five vendor-side successes. The current live write smoke failed safely on `update_asset_config` HTTP 403 / `accepted=false` under the then-current upstream identity binding.

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

```text
complete | partial | inconclusive | conflict | unavailable
```

### Govern consequential actions instead of treating proposals as execution

```text
proposal
→ deterministic policy
→ private exact custody
→ operator confirmation
→ fresh server-owned tenant/resource authorization
→ persistent idempotency
→ action execution lease/fencing
→ server-owned vendor actor
→ one typed upstream attempt
→ explicit acceptance or safe non-success/uncertain state
```

The vendor actor must never be browser/model controlled. Current integration work is correcting the local-requester-to-vendor-actor coupling discovered by the live 403.

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
- governed action proposal/confirmation/state surfaces;
- analytics/research surfaces under Technical.

The current UI organizes these by task rather than by four permanent engineering-depth tabs.

A later user review identified further global simplification work: one primary question/action per screen, less default card/status density, evidence contextual to Result and technical depth outside the normal path. This is an active UX target, not completed human usability evidence.

## 8. Action implementation / evidence status

### PR #211

Promoted governed execution for all five canonical actions.

```text
merge SHA   1a1e7139bfa0361416120b3f21937c4048b5bb1f
Railway     9732a2cb-c321-4fcf-83f8-c6f87eeab06a — SUCCESS
```

### PR #213

Added auditable five-action production smoke.

```text
merge SHA   3545d75c00ca30419e0f47e8b1950aa50cbbf462
CI          required-gate run 34164123263 — SUCCESS
Railway     2cbc4215-f59a-4947-8691-0d4776458445 — SUCCESS
```

### Decisive live gate

Fresh configuration-snapshot deployment:

```text
5ba36471-776c-4e15-919b-56e2da216b74 — FAILED SAFE
update_asset_config -> HTTP 403 / accepted=false
```

The previous healthy production deployment remained serving.

This proves fail-closed validation and disproves the stronger claim that all five vendor writes were already ready under the existing identity mapping.

## 9. Evaluation coverage

Evaluation is designed to inspect correct function/tool, argument validity, trajectory, evidence/provenance, final operational conclusion, clarification/abstention/escalation, action safety, failures, repeated-run stability, reproducible identities and baseline-vs-candidate deltas.

PR #213 source passed the required regression matrix including action execution lease/fencing, horizontal runtime, production image, clean clone and Chromium product acceptance. Semantic judges remain non-gating until real human calibration.

CI/provider-free evidence does not replace hosted vendor action acceptance.

## 10. Deliberately not promoted

LangGraph migration, multi-agent topology, RAG/vector DB, persistent memory, MCP, Redis/Kafka, Kubernetes/microservices and adaptive stopping/routing need a measured gap, USD0 eligibility and controlled challenger win.

## 11. Remaining final-delivery evidence

- finish server-owned upstream vendor actor routing;
- prove actor mapping is fail-closed and not client/model controlled;
- full required CI on that correction;
- exact-SHA/fresh-snapshot deployment;
- five-action live smoke 5/5 explicit acceptance;
- normal product confirmation-path hosted action evidence;
- broader recent V13 live coverage across canonical reads;
- true bilateral comparison with two real fleet assets;
- knowledge/model/analysis/baseline live coverage;
- anti-hallucination/false-precision/conflict prompt matrix;
- multi-turn behavior if required;
- full Provider Tournament v3;
- SECURITY-V1;
- load/capacity and evidence-derived SLO;
- restore/recovery;
- human semantic/usability calibration;
- real operational-value comparison;
- final evidence freeze.

## 12. Demonstration contract

Demonstrate the **normal hosted product**:

```text
sign in
→ Home: real equipment question
→ Result: conclusion + response mode + evidence
→ Analyses: persisted alternate run
→ Technical: trace / evaluator / architecture / governed actions
→ explain current action live-validation gap truthfully
→ exact limitations/non-claims
```

No separate demo-only, local or paid serving stack is compatible with the project claim.

See [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md).