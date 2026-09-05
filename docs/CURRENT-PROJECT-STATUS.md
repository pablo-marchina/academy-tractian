# Academy × TRACTIAN — Current Project Status

**Status:** `READY_FOR_HARD_FREEZE` candidate / sole canonical human-readable state  
**Checkpoint:** 2026-09-05 BRT  
**Scheduled hard feature/visual/architecture freeze:** end of 2026-09-05  
**Final delivery:** 2026-09-08  
**Historical freeze candidate:** [`../research/final-freeze-decision-2026-09-04.md`](../research/final-freeze-decision-2026-09-04.md)  
**Current P0 closure addendum:** [`../research/p0-hard-freeze-closure-2026-09-05.md`](../research/p0-hard-freeze-closure-2026-09-05.md)

## 1. Executive status

```text
updated TAPI scope                         Agent + Evaluation in one solution
external API/hosted-service cash cost     USD 0 hard constraint
production agent runtime                  IMPLEMENTED
production deterministic evaluator        IMPLEMENTED
TRACTIAN typed tool registry              18 operations
safe realtime observability               IMPLEMENTED / PostgreSQL-backed
React operator control room               IMPLEMENTED
full-product Playwright E2E                PASS / gated
frontend lockfile + npm ci                 PASS / gated
current clean-clone reproduction           PASS / gated
stable final required CI                   PASS / required-gate

read-only cross-replica runtime handoff    IMPLEMENTED / PostgreSQL-real tested
runtime lease takeover                     IMPLEMENTED / generation-fenced
production consequential actions          IMPLEMENTED
custody + explicit confirmation            IMPLEMENTED
persistent idempotency/no blind replay     IMPLEMENTED
action execution lease                    IMPLEMENTED / non-transferable
lost action ownership outcome              UNCERTAIN / no replacement replay

request authentication                    SIGNED BEARER HMAC-SHA256 V1
enterprise OIDC/SSO claim                  FALSE
production serving persistence             PostgreSQL
production observability/evaluation        PostgreSQL
DuckDB production dependency               FALSE
PostgreSQL tenant RLS                      IMPLEMENTED / tested

realtime wakeup                            PostgreSQL LISTEN/NOTIFY + durable fallback
realtime durable truth                     PostgreSQL rows + sequence cursor

human semantic-review collector            IMPLEMENTED
VALIDATION source generation               IMPLEMENTED
human semantic calibration claim           NOT READY — real labels required

operational-value collector                IMPLEMENTED
frozen paired time analysis                IMPLEMENTED
engineer-minutes-saved business claim      NOT READY — real human data required

adaptive stopping replay diagnostic        IMPLEMENTED / evaluator-only
adaptive runtime stopping promoted         NO

load/concurrency campaign                  MEASURED / descriptive only
production capacity claim                  FALSE
restart/recovery campaign                  VERIFIED safety contract
cross-replica correctness                  VERIFIED for tested repository algorithms
RTO/RPO/deployed HA claim                  FALSE

D01/D02 provider comparison                COMPLETE
D01/D02 cash cost                          USD 0.00
provider selection                         NO_SELECTION

main branch CI contract                    PASS / one required-gate
GitHub branch-protection enforcement       PENDING EXTERNAL
last observed main.protected               false (2026-09-05)
last observed repository rulesets          [] (2026-09-05)

final evidence bundle                      CURRENT P0 / READY candidate
hard freeze effective now                  NO — scheduled end 2026-09-05
```

## 2. Exact current integration evidence

The accepted repository-side P0 integration is merged on `main` at:

`9e160e9badcf6ba0d5ebba39b7d64d24380408c6`

This includes PR #187 (read-only cross-replica runtime handoff) and PR #188 (non-transferable consequential-action execution leases).

Post-merge `final-ci-required` run `33970100750` / run #384 completed successfully on that exact `main` SHA:

```text
clean-clone / reproduce-current-product                 success
full-product-browser / chromium-full-product             success
horizontal-runtime-handoff / postgres-horizontal-runtime success
action-execution-lease / postgres-action-lease           success
required-gate                                            success
```

`required-gate` is the stable status context intended for branch protection. It now succeeds only after all four reusable product/reproduction/distributed-correctness gates above succeed.

GitHub enforcement remains a separate external control. The 2026-09-05 branch read still reports `main.protected=false`, and the repository ruleset collection remains empty. Direct pushes/merges therefore must not be described as technically blocked yet.

## 3. Promoted product path

```text
browser request
→ signed RuntimeContextProvider
→ organization/user/identity/permissions
→ FastAPI product API
→ PostgreSQL tenant RLS + ownership/execution state
→ PostgreSQL runtime handoff queue / generation-fenced lease
→ RealtimeProductionRuntime.prepare()
→ provider-neutral DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ deterministic B1/B2/B3 boundaries
→ normalized evidence
→ FINAL / CLARIFY / ABSTAIN / ESCALATE / action proposal
→ RunTrace
→ ProductionEvaluator
→ safe PostgreSQL observability/evaluation projection
→ REST/SSE
→ PostgreSQL LISTEN/NOTIFY wakeup + durable cursor fallback
→ React operator control room
```

Read-only runtime work may transfer to another replica only after the current lease expires. Generation fencing prevents a stale worker from renewing/finalizing/publishing as the current owner.

Consequential action path:

```text
agent proposes exact action
→ deterministic scope/schema/permission validation
→ private PostgreSQL custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ authorization + kill switch revalidated
→ atomic persistent idempotency claim
→ non-transferable PostgreSQL action execution lease
→ exact custodied action executes once from this product attempt
→ lease-fenced custody/ledger/observability/terminal persistence
→ separate action execution/run trace
→ ProductionActionEvaluator
→ safe REST/SSE/frontend projection
```

If action ownership expires or becomes stale/missing, the product converges the ambiguous attempt to `UNCERTAIN`; it does not transfer the lease to another replica and does not begin a replacement transport attempt. A stale late response cannot overwrite uncertainty with `ACCEPTED` or `NOT_ACCEPTED`.

This is deliberately not a distributed exactly-once external-side-effect claim. That stronger guarantee would require the external TRACTIAN API to participate in a common idempotency/fencing protocol.

## 4. Identity and tenant isolation

The promoted entrypoint uses the project-owned `academy-runtime-v1` signed bearer envelope with HMAC-SHA256 verification, issuer/audience/lifetime checks and explicit organization/user/identity/permission claims. Browser payloads cannot provide tenant, identity, role, permissions or benchmark seed.

This is deliberately **not** described as OAuth/OIDC/JWT or enterprise SSO.

PostgreSQL provides an independent tenant boundary. Scoped reads use a non-superuser, non-`BYPASSRLS`, non-owner role and transaction-local `academy.organization_id`; direct SQL integration proves tenant B cannot read a known tenant-A ownership row.

## 5. Production persistence and distributed correctness

`OPS-STORE-001` originally promoted PostgreSQL for mutable operational state after the prior DuckDB operational baseline produced concurrent operational errors. Subsequent P0 increments removed local serving fallbacks and moved the sanitized production observability/evaluation read model onto the same qualified PostgreSQL substrate.

Current promoted serving persistence is:

```text
PostgreSQL  run ownership/execution + tenant isolation
PostgreSQL  runtime handoff payload/lease/generation state
PostgreSQL  action custody/idempotency/non-transferable leases
PostgreSQL  sanitized observability runs/events/evidence/evaluations
PostgreSQL  semantic-review + operational-value collection state
DuckDB      explicit dev/benchmark compatibility only
```

The root production package no longer depends on DuckDB; DuckDB is present only in optional dev/benchmark extras.

### Read-only runtime handoff

PostgreSQL-real cross-replica campaigns prove the tested algorithm can:

- avoid double-claiming a healthy lease;
- avoid replica-B interference with healthy replica-A ownership;
- transfer an expired read-only runtime lease to a new replica;
- fence stale lease generations from renew/finalize/publish;
- complete recovered runtime evaluation/terminal persistence;
- remove private handoff payload after terminal completion.

### Consequential-action ownership

PostgreSQL-real two-replica campaigns prove:

- replica B does not mark replica A's healthy leased action `UNCERTAIN`;
- duplicate confirmation does not create a second transport call;
- an expired action lease cannot be acquired by B;
- lost/stale ownership converges custody, action execution and claimed ledger state to `UNCERTAIN`;
- stale terminal responses cannot publish false success;
- the forced-expiry campaign issues exactly one external transport call;
- automatic action replay remains false.

These are repository-level cross-replica correctness claims for the tested algorithms. They do not prove a deployed Cloud Run/Cloud SQL HA topology, autoscaling behavior, production RTO/RPO/uptime or multi-region failover.

## 6. Realtime state

PostgreSQL observability rows and `(run_id, sequence)` cursors remain authoritative. `LISTEN/NOTIFY` is wakeup-only: one listener per application replica fans out local wakeups, while bounded fallback durable reads preserve catch-up after a missed notification. Tenant authorization does not depend on NOTIFY payloads.

The preregistered RT-WAKEUP-001 comparison promoted PostgreSQL LISTEN/NOTIFY. One later hosted-CI sample kept all hard gates green but missed an efficiency threshold; the same job rerun on the same code SHA, without changing protocol or thresholds, passed with:

```text
polling baseline event p95                 52.10 ms
PostgreSQL LISTEN/NOTIFY event p95         23.71 ms
candidate - baseline p95                  -28.39 ms
idle durable-read ratio                    0.375
idle durable-read reduction                62.5%
hard gates                                 PASS
efficiency gates                           PASS
```

The inconclusive sample remains part of the observed runner variance; no criterion was relaxed to obtain the pass.

## 7. Evaluation and human evidence state

Delivered:

- deterministic structural/safety/trajectory evaluation;
- operational-conclusion/value contract;
- blinded operational-value collection + server-owned timing;
- frozen paired MANUAL × ASSISTED analysis;
- semantic rubric + frozen calibration protocol v2;
- blinded semantic review A/B + independent adjudication custody;
- trusted VALIDATION source generation from sanitized production read model;
- evaluator-only adaptive evidence/stopping replay.

Still human-dependent and therefore **not ready**:

- real semantic labels/adjudication;
- measured judge-vs-human agreement/error profile;
- real manual vs assisted engineer-time observations;
- Engineer Minutes Saved per Ticket;
- useful auto-resolution/business-value claim.

These values must not be fabricated. `LOCKED_TEST` remains excluded from tuning/calibration.

## 8. Adaptive/runtime topology state

The merged adaptive stopping work is DEV-only and evaluator-only. It may quantify replay headroom but cannot authorize a runtime policy change; no oracle-free adaptive challenger has won EDD.

The P0 topology remains **`NO_CHANGE`** with respect to orchestration-framework migration:

`custom AgentController + HarnessRunner + PostgreSQL durable handoff/custody/fencing + conservative failure recovery`.

Current evidence does not identify a LangGraph/multi-agent/RAG/memory/MCP topology bottleneck. Any such P1 challenger must demonstrate a material Pareto improvement without bypassing application-owned safety/tool boundaries.

## 9. Load/concurrency and recovery evidence

### Load

The provider-free authenticated PostgreSQL campaign exercised concurrency 1 and 4 with 12 synthetic measured requests. All completed without errors and higher concurrency visibly saturated the two-worker executor. Latency/throughput/persistence/resource values are preserved in the aggregate artifact.

Interpretation remains `descriptive_only`; CI data is not a production capacity/SLO/worker-sizing claim.

### Restart/recovery

Recovery authority is intentionally split:

```text
runtime handoff recovery       read-only runtime ownership only
action lease recovery          consequential-action uncertainty only
```

`running + no action lease` is immediate ownership-loss evidence. Only the short `accepted + no lease` confirmation setup window receives bounded grace. Healthy actions on another replica are not startup orphans.

The older restart campaign still proves conservative persisted-state reconciliation and idempotent second-start behavior with zero blind provider/action replay. The newer distributed campaigns add healthy cross-replica non-interference and stale-owner fencing. None of these repository tests establishes deployment RTO/RPO/HA/uptime.

## 10. Provider state

D01 and D02 are complete governed USD-zero experiments. D02 improved multiple public metrics after the 512→1024 completion-budget change, but neither candidate crossed frozen M1/M4/M7 promotion gates.

Final P0 provider state remains:

**`NO_SELECTION` / no production provider claim.**

The consumed D01/D02 packets must not be replayed merely to seek a preferable result. Any P1 provider/model comparison requires a new preregistered experiment ID and a newly frozen packet/protocol.

## 11. Reproduction and browser acceptance

Current clean-clone reproduction proves from one fresh checkout:

```text
PostgreSQL 18
→ complete Python suite with PostgreSQL enabled
→ identity/RLS + load + recovery P0 checks
→ promoted PostgreSQL distributed correctness regressions
→ ADR-004 controller regression
→ frozen EV-007 / EV-008 / EV-011
→ historical delivery/evidence validation
→ final handoff audit
→ final freeze-bundle validation
→ npm ci from committed package-lock
→ TypeScript typecheck / Vitest / production build
→ zero tracked repository mutation
```

Full Chromium acceptance proves genuine backend/frontend/PostgreSQL execution, SSE reconnect/catch-up, post-runtime evaluation, action confirmation/follow-run, tenant isolation, safe browser projections and responsive product behavior.

The historical final-delivery reproduction workflow remains immutable evidence and is intentionally distinct from the current-product reproduction contract.

## 12. External blockers / explicit bounded state

### Branch protection

Repository CI is branch-protection-ready, but enforcement remains external. Last observed on 2026-09-05:

```text
main.protected = false
repository rulesets = []
```

Required settings and verification procedure are documented in `docs/BRANCH-PROTECTION.md`. No branch-protection enforcement claim is authorized until a later GitHub read reports the control active.

### Historical C4 exact artifact

The required evaluator-side artifact with SHA-256
`b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`
remains externally unavailable. Reconstruction, substitution or rescoring is forbidden. The blocker remains visible in final handoff and does not become resolved because current product CI is green.

## 13. Critical path to delivery

```text
1. P0 distributed runtime/action correctness             merged
2. post-merge required-gate on exact main SHA            PASS (#384)
3. synchronize current status/freeze bundle              current closure PR
4. hard feature/visual/architecture freeze               end 2026-09-05
5. apply + verify GitHub branch protection               external control
6. final rehearsal/evidence inspection                   2026-09-06/07
7. delivery                                              2026-09-08
```

Human semantic/value collection can proceed when reviewers/operators are available, but absent real data the final delivery must preserve `NOT READY` rather than manufacture a claim.

P1 work — new provider/model benchmark, LangGraph comparison, adaptive routing, broader OpenTelemetry standardization or frontend consolidation — must not displace the freeze/rehearsal path and requires measured materiality.

## 14. Current non-claims

Do not claim:

- a production provider/model has been selected;
- human semantic calibration is complete;
- engineer minutes saved without real human observations;
- adaptive stopping improves runtime behavior before an oracle-free challenger wins;
- CI load measurements establish production capacity/SLOs;
- repository restart/cross-replica tests establish deployed RTO/RPO, HA, autoscaling, multi-region failover or uptime;
- distributed exactly-once external action side effects;
- enterprise IAM/SSO is implemented;
- LangGraph or another orchestration framework is needed/superior before a controlled comparison;
- GitHub branch protection is enforced before GitHub reports it active;
- RAG/GraphRAG/vector DB/Kubernetes/Kafka/Redis/multi-agent/Temporal/MCP migration is justified without a measured gap and challenger win.

## 15. State update rule

This file is the mutable current-state summary. Accepted changes update it. Historical ADRs, frozen experiment evidence, prior campaign artifacts and the historical delivery reproduction workflow remain immutable and authoritative for their original scopes. The 2026-09-05 closure addendum may supersede only mutable current-state statements that were true at the 2026-09-04 freeze-candidate checkpoint but were later improved by accepted P0 work.