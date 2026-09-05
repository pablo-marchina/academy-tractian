# Academy × TRACTIAN — Delivery Acceptance

**Status:** ACTIVE / canonical final Definition of Done  
**Checkpoint:** 2026-09-05 BRT  
**Accepted baseline:** `d3bed06b132212c85b126f56708863d45f64e03e`  
**Post-merge acceptance:** `final-ci-required` run #386 / `required-gate = success`  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)

This document defines what must be demonstrably true at final delivery. Historical acceptance hypotheses remain in Git/ADR history; this file reflects the current P0 architecture and evidence state.

## 1. Final acceptance rule

```text
Agent + Evaluation scope covered
+
typed TRACTIAN integration demonstrated
+
deterministic safety/privacy boundaries preserved
+
consequential-action custody/confirmation/idempotency/fencing proven
+
PostgreSQL serving/recovery topology reproduced
+
realtime safe observability + browser product demonstrated
+
material architecture decisions evidence-backed
+
provider/human/adaptive claims bounded by evidence
+
clean-clone + Chromium + distributed hard gates green
+
canonical docs/runbook/evidence match committed product
```

An uncovered P0 is a blocker unless the final claim is explicitly reduced with an evidence-honest limitation.

## 2. Current acceptance matrix

| Area | Final P0 state | Acceptance |
|---|---|---|
| Industrial agent | implemented | PASS_EVIDENCED |
| Agent evaluation framework | implemented | PASS_EVIDENCED |
| 18 typed TRACTIAN tools | implemented | PASS_EVIDENCED |
| Deterministic B1/B2/B3 safety | implemented | PASS_EVIDENCED |
| Identity + tenant RLS | PostgreSQL / signed bearer | PASS_EVIDENCED |
| Serving persistence | PostgreSQL | PASS_EVIDENCED |
| Safe observability/evaluation persistence | PostgreSQL | PASS_EVIDENCED |
| Read-only cross-replica handoff | generation-fenced leases | PASS_EVIDENCED |
| Consequential action fencing | non-transferable leases | PASS_EVIDENCED |
| Realtime wakeup | LISTEN/NOTIFY + durable fallback | PASS_BOUNDED |
| Chromium full-product E2E | gated | PASS_EVIDENCED |
| Clean-clone reproduction | gated | PASS_EVIDENCED |
| Provider/model selection | D01/D02 failed promotion | NO_SELECTION |
| Semantic human calibration | real labels absent | NOT_READY_HUMAN_DATA |
| Engineer-time/business value | real measurements absent | NOT_READY_HUMAN_DATA |
| Adaptive runtime stopping | evaluator-only | NOT_PROMOTED |
| Custom controller vs framework migration | no challenger win | NO_CHANGE |
| CI load/capacity | descriptive | PASS_BOUNDED |
| Deployment HA/RTO/RPO | not demonstrated | NOT_CLAIMED |
| Branch protection | GitHub reports disabled | PENDING_EXTERNAL_ENFORCEMENT |
| Exact historical C4 artifact | unavailable | EXTERNALLY_BLOCKED |

## 3. Agent acceptance

The product must demonstrate on integrated paths:

- contextualize/orient from grounded evidence;
- investigate through appropriate typed TRACTIAN read tools;
- select valid tools and construct valid arguments;
- handle complete, partial, conflicting, inconclusive and unavailable evidence;
- clarify when required;
- abstain safely where no justified path exists;
- escalate with structured handoff;
- contain denied/invalid consequential actions;
- propose consequential actions without equating proposal to execution;
- produce customer-safe terminal communication;
- preserve inspectable trajectory/provenance;
- fail safely when provider/tool/runtime boundaries fail.

Evidence must include traces and negative/degraded cases, not final text alone.

## 4. Consequential-action acceptance

Required properties:

- proposal is not execution;
- permission/resource/schema/justification validation is deterministic;
- exact action payload stays in private PostgreSQL custody;
- browser confirms only opaque `action_id` + consent;
- browser cannot inject args, permissions, requester identity, scope or idempotency key;
- current authorization and host action kill switch are revalidated at execution time;
- persistent atomic idempotency claim precedes transport;
- executing replica acquires the exact non-transferable action lease;
- a healthy remote action is not treated as an orphan;
- lost/stale ownership converges custody/execution/claimed ledger to `UNCERTAIN`;
- action lease cannot transfer to another replica after expiry;
- stale late terminal result cannot overwrite uncertainty;
- duplicate confirmation cannot create a second product transport attempt;
- automatic action replay remains false;
- confirmed action produces a separate realtime RunTrace + ProductionActionEvaluator;
- another requester cannot enumerate/confirm the action.

Do not claim external exactly-once side effects; external API participation would be required.

## 5. Read-only runtime handoff acceptance

Required repository-level semantics:

- healthy lease cannot be double-claimed;
- replica B cannot interfere with healthy replica A;
- expired read-only lease may transfer to B;
- generation/fencing token changes on takeover;
- stale generation cannot renew/finalize/publish as current owner;
- recovered runtime can continue to evaluation/terminal persistence;
- private handoff payload is removed at terminal completion.

These tests establish algorithmic cross-replica correctness, not deployed Cloud Run/Cloud SQL HA, autoscaling, RTO/RPO or multi-region failover.

## 6. Evaluation-framework acceptance

The delivered framework must support:

- scenario execution;
- tool-selection evaluation;
- argument validity where deterministically measurable;
- trajectory integrity;
- evidence/provenance use;
- terminal/outcome quality dimensions;
- safety/containment;
- degraded API/provider/tool cases;
- repeated-run stability;
- high-impact-action behavior;
- escalation/handoff quality;
- communication behavior;
- evaluator/runtime isolation;
- reproducible config/result identities;
- baseline-vs-candidate deltas for material changes.

Private benchmark/gold truth must never enter runtime/model context.

## 7. Semantic response-quality acceptance

Deterministic evaluation remains authoritative wherever exact evidence exists.

Human semantic-review infrastructure may cover conclusion quality, groundedness, unsupported claims, handoff usefulness, communication and relevant completeness.

A semantic LLM judge may become a gate only after:

1. real blinded human-labelled calibration rows exist;
2. two-reviewer/adjudication protocol is executed;
3. judge-vs-human agreement/error is measured by relevant response-mode slices;
4. disagreement/failure examples are inspected;
5. an explicit promotion decision is frozen.

Current state is `NOT_READY_HUMAN_DATA`; final delivery must not fabricate labels or judge validity.

## 8. Eval-Driven Development acceptance

Material candidates follow:

```text
requirement
→ metric/evaluator
→ frozen baseline
→ preregistered candidate
→ controlled implementation
→ repeated/sliced comparison
→ uncertainty/failure analysis
→ PROMOTE / REJECT / INCONCLUSIVE / NO_CHANGE
→ regression
```

Hard integrity gates include:

- gold leakage = 0;
- credential/private-field leakage = 0;
- unauthorized action transport = 0;
- automatic duplicate/replacement action attempt = 0;
- known-tool validity = 100% where applicable;
- accepted trace integrity = 100%;
- no safety regression hidden by aggregate quality.

## 9. Runtime/orchestration acceptance

Final P0 baseline is:

`custom AgentController + HarnessRunner + PostgreSQL durable handoff/custody/fencing`.

Read-only takeover and action fencing solve the P0 durability/HITL correctness gap without migrating orchestration frameworks.

No LangGraph or alternate-framework challenger demonstrated a material Pareto improvement before freeze, so final state is `NO_CHANGE`. A later P1 comparison must preserve tools, HarnessRunner, safety semantics, cases and evaluator.

## 10. Storage acceptance

Final serving topology is PostgreSQL, including:

- run ownership/execution;
- tenant RLS;
- runtime handoff state;
- action custody/idempotency/leases;
- safe observability/evaluation rows;
- semantic-review / operational-value collection state.

DuckDB is not a production dependency; it remains only in explicit dev/benchmark compatibility extras.

Acceptance requires:

- concurrent ownership/claim correctness;
- duplicate-action containment;
- conservative restart semantics;
- cross-replica runtime/action ownership tests;
- fail-closed schema/readiness;
- clean reproduction;
- no mandatory local file-backed serving state.

## 11. Provider experiment acceptance

D01 and D02 are immutable consumed governed experiments.

Accepted conclusion:

```text
D01/D02 completed
cash cost = USD 0
resource accounting preserved
D02 quality improved vs D01 on several metrics
both candidates failed frozen M1/M4/M7 promotion gates
production provider/model selection = NO_SELECTION
```

D01/D02 must not be replayed.

Any P1 provider/model campaign requires a new experiment ID, current primary-source eligibility/cost verification, a fresh preregistration and explicit live authorization before attempt 1.

## 12. Realtime observability acceptance

Browser-visible telemetry must derive from safe projection, never raw RunTrace/private material.

Must prove:

- live run appears without refresh;
- genuine runtime events update product surfaces;
- event sequence/cursor ordering is authoritative in PostgreSQL;
- `Last-Event-ID`/sequence catch-up works;
- duplicate delivery is logically idempotent;
- missed NOTIFY cannot lose durable events because fallback reads catch up;
- one listener per application replica is wakeup-only;
- slow/disconnected browser does not block runtime;
- terminal UI follows genuine terminal evidence;
- no fabricated thinking/progress is presented.

RT-WAKEUP-001 is bounded CI evidence, not a production latency SLO.

## 13. Security/privacy acceptance

Browser/API/SSE/artifacts must never expose:

- provider credentials/tokens/auth headers;
- raw identity binding/signing secrets;
- evaluator seed/gold/private truth;
- raw provider request/response;
- forbidden raw prompt/system material;
- forbidden raw tool/observation bodies;
- private action custody payload/idempotency key;
- hidden chain-of-thought.

The project-owned signed bearer is not enterprise OAuth/OIDC/SSO.

## 14. Frontend acceptance

Required connected surfaces:

1. Mission Control;
2. Live Run Cockpit;
3. Run Explorer;
4. Timeline/Waterfall;
5. Trace Graph;
6. Architecture Explorer;
7. Evidence Explorer;
8. Output Lineage;
9. Action Control;
10. Tools & Policy analytics;
11. Eval Lab;
12. Provider D01/D02 Lab;
13. Dynamic Data Explorer;
14. Production Health.

Safe drill-downs must answer what happened, which component acted, what evidence fed it, what happened next, which output became terminal and what evaluation occurred afterward.

Hidden chain-of-thought is explicitly outside this contract.

## 15. Browser/E2E acceptance

Chromium must exercise the real provider-free product path and cover:

- run submission;
- genuine SSE;
- ordering/idempotency;
- disconnect/reconnect/catch-up;
- trace + architecture;
- evidence + lineage;
- global scope/cross-filter/drill-down;
- real Production Health;
- clarify/abstain/escalate/error/blocked-action states;
- pending action + controlled confirmation + separate live execution run;
- terminal/evaluator timing;
- forbidden-field absence;
- loading/empty/long/unsupported states;
- presentation viewport.

Latest post-merge P0 evidence: run #386 `full-product-browser = success`.

## 16. Reproduction/CI acceptance

The final dependency graph uses committed frontend lockfile + `npm ci`.

Clean clone must reproduce:

```text
PostgreSQL 18
→ full Python tests
→ promoted PostgreSQL P0 regressions
→ ADR-004
→ frozen EV-007 / EV-008 / EV-011
→ historical delivery/evidence validation
→ final handoff audit
→ final freeze bundle validation
→ frontend npm ci / typecheck / tests / build
→ tracked repository mutation = 0
```

Stable final gate requires:

```text
clean clone                       success
Chromium                          success
horizontal runtime handoff        success
action execution lease            success
required-gate                     success
```

Latest accepted post-merge run at this checkpoint: #386 / `33971230788` on `d3bed06b…`.

## 17. Load/recovery claim boundary

CI campaigns may describe measured queueing, latency, throughput, resource usage, restart behavior and cross-replica algorithm correctness.

They do **not** establish:

- production capacity or SLO;
- optimal worker sizing;
- deployed RTO/RPO;
- Cloud Run/Cloud SQL HA;
- autoscaling or multi-region failover;
- uptime.

## 18. Human/business-value acceptance

Operational-value collection and paired analysis are implemented. A business claim such as Engineer Minutes Saved requires real human timing/outcome data.

Without such observations, final status stays `NOT_READY_HUMAN_DATA`.

## 19. Documentation acceptance

README and canonical docs must accurately state:

- Agent + Evaluation scope;
- PostgreSQL serving/realtime architecture;
- read-only takeover vs non-transferable action lease semantics;
- current stack/dependencies;
- installation/reproduction;
- provider `NO_SELECTION`;
- human/adaptive limitations;
- production measurements with bounded claims;
- branch-protection/C4 external blockers;
- exact final SHA + required-gate evidence.

No active/canonical doc may describe current PostgreSQL-promoted work as planned/candidate or show DuckDB in the production serving path.

## 20. Freeze acceptance

By end of 2026-09-05:

- feature set frozen;
- visual/information hierarchy frozen;
- runtime→telemetry→frontend contracts frozen;
- action contract frozen;
- semantic gating state frozen (`NOT_READY_HUMAN_DATA` unless real calibration appears);
- adaptive stopping frozen as not promoted;
- runtime/orchestration frozen as `NO_CHANGE`;
- PostgreSQL storage/distributed correctness state frozen;
- no open unbounded P0 defect;
- remaining P1 explicitly deferred.

After freeze, only delivery-blocking fixes with targeted regression are allowed.

## 21. Final presentation acceptance

The final presentation must use the normal provider-independent product path and visibly show:

```text
request
→ live run
→ architecture activation
→ structured model/decision metadata
→ typed tool proposal
→ deterministic policy/safety
→ TRACTIAN transport metadata
→ safe evidence
→ next decision
→ final / clarify / abstain / escalation / governed action
→ completed RunTrace
→ post-runtime evaluation
→ output lineage
→ Production Health
→ dynamic quantitative analytics
→ D01/D02 + final architecture-decision evidence
```

Multiple outcome/failure classes must be available without depending on a live provider.

## 22. External blockers

### Branch protection

Repository exposes stable `required-gate`, but last GitHub read still reports:

```text
main.protected = false
rulesets = []
```

Acceptance state: `PENDING_EXTERNAL_ENFORCEMENT` until a GitHub read proves enforcement active.

### C4 exact artifact

The exact required historical evaluator-side C4 artifact remains unavailable. Reconstruction, substitution and rescoring are forbidden.

Acceptance state: `EXTERNALLY_BLOCKED` for claims requiring that exact artifact.

## 23. Evidence-honest final rule

Negative/bounded outcomes strengthen rather than weaken the project when they are evidence-backed:

- `NO_SELECTION` for provider/model;
- `NOT_PROMOTED` for adaptive stopping;
- `NO_CHANGE` for orchestration migration;
- `NOT_READY_HUMAN_DATA` for semantic/value claims;
- `PENDING_EXTERNAL_ENFORCEMENT` for branch protection;
- `EXTERNALLY_BLOCKED` for missing C4.

Never replace these states with invented winners or broader production claims.