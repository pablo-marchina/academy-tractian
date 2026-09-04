# Academy × TRACTIAN — Current Project Status

**Status:** ACTIVE / sole canonical human-readable state  
**Checkpoint:** 2026-09-04 BRT  
**Final delivery:** 2026-09-08  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)

## 1. Executive status

```text
updated TAPI scope                         Agent + Evaluation in one solution
external API/hosted-service cash cost     USD 0 hard constraint
production agent runtime                  IMPLEMENTED
production deterministic evaluator        IMPLEMENTED
TRACTIAN typed tool registry              18 operations
safe realtime observability               IMPLEMENTED
React operator control room               IMPLEMENTED
full-product Playwright E2E                IMPLEMENTED / gated
frontend lockfile + npm ci                 IMPLEMENTED / gated

production consequential actions          IMPLEMENTED
custody + explicit confirmation            IMPLEMENTED
persistent idempotency/no blind replay     IMPLEMENTED

request authentication                    SIGNED BEARER HMAC-SHA256 V1
enterprise OIDC/SSO claim                  FALSE
mutable operational state                 PostgreSQL
analytics/read model                       DuckDB
PostgreSQL tenant RLS                      IMPLEMENTED / tested

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
RTO/RPO/availability claim                 FALSE

D01/D02 provider comparison                COMPLETE
D01/D02 cash cost                          USD 0.00
provider selection                         NO_SELECTION

clean-clone full reproduction              ACTIVE P0 / #174
branch protection + final CI               NEXT P0
final benchmark/evidence freeze            NEXT P0
```

## 2. Promoted product path

```text
browser request
→ signed RuntimeContextProvider
→ organization/user/identity/permissions
→ FastAPI product API
→ PostgreSQL ownership + tenant RLS
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
→ safe projection
→ DuckDB analytics/read model
→ REST/SSE
→ React operator control room
```

Consequential action path:

```text
agent proposes exact action
→ deterministic scope/schema/permission validation
→ private PostgreSQL custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ authorization + kill switch revalidated
→ atomic persistent idempotency claim
→ exact custodied action executes
→ separate action execution/run trace
→ ProductionActionEvaluator
→ safe REST/SSE/frontend projection
```

Ambiguous post-claim outcomes become `UNCERTAIN`. Restart is never permission to automatically replay a runtime execution or retry a consequential action.

## 3. Identity and tenant isolation

The promoted entrypoint uses the project-owned `academy-runtime-v1` signed bearer envelope:

- HMAC-SHA256 signature;
- constant-time signature comparison;
- issuer/audience validation;
- explicit token lifetime;
- explicit organization, identity and user claims;
- no fallback to browser-controlled identity headers;
- no benchmark `seed` claim;
- privileged global capabilities require separate server opt-in.

This is deliberately **not** described as OAuth/OIDC/JWT or enterprise SSO.

PostgreSQL provides a second independent tenant boundary. Scoped reads use a non-superuser, non-`BYPASSRLS`, non-owner role and transaction-local `academy.organization_id`. Direct SQL integration tests prove tenant B cannot read a known tenant-A ownership row.

## 4. Evaluation and human evidence state

Delivered:

- deterministic structural/safety/trajectory evaluation;
- operational-conclusion/value contract;
- blinded human operational-value pilot packet + authenticated collector UI;
- frozen paired MANUAL × ASSISTED time analysis;
- semantic rubric + frozen calibration protocol v2;
- blinded semantic review A/B + third adjudicator custody;
- trusted VALIDATION source generation from the sanitized read model;
- evaluator-only adaptive evidence/stopping replay.

Still human-dependent:

- real semantic labels/adjudication;
- measured semantic evaluator agreement/error profile;
- real manual vs assisted engineer-time observations;
- useful auto-resolution/business-value claim.

These data must not be fabricated. `LOCKED_TEST` remains excluded from tuning/calibration.

## 5. Adaptive stopping state

The replay diagnostic measures where an evaluator-time evidence oracle says sufficiency first occurred and how much trajectory remained afterwards.

Important boundary:

- predicates are explicit evaluator judgments;
- the oracle never enters runtime;
- headroom is diagnostic, not automatically waste;
- no runtime stopping rule was promoted;
- any future challenger must be oracle-free at execution time and win under EDD/hard gates.

## 6. Load/concurrency evidence

The provider-free authenticated PostgreSQL campaign is reproducible and hash-bound. CI exercised concurrency levels 1 and 4 with 12 synthetic requests total.

Observed on the CI runner:

```text
concurrency 1  6/6 completed, 0 errors, peak executor utilization 0.5
concurrency 4  6/6 completed, 0 errors, peak active 2, peak queued 2,
               peak inflight 4, executor utilization 1.0
```

Latency, throughput, persistence, CPU and RSS aggregates are recorded in the campaign artifact. Interpretation remains `descriptive_only`; no CI measurement is presented as deployment capacity or an SLO.

## 7. Restart/recovery evidence

The promoted PostgreSQL topology now has an integrated restart campaign.

Verified first-start behavior:

```text
2 orphaned runtime executions              → interrupted
1 orphaned action execution                → uncertain
1 custody EXECUTING row                    → UNCERTAIN
1 ledger CLAIMED row                       → UNCERTAIN
PENDING_CONFIRMATION                       preserved
completed / failed executions              preserved
provider calls during recovery             0
action transport calls during recovery     0
```

A fresh authenticated run completes after recovery and remains tenant-isolated. A second startup produces zero new recovery transitions. The artifact explicitly states `production_availability_claim_ready=false`; no RTO/RPO/HA/uptime claim follows from this repository-level test.

## 8. Provider state

D01 and D02 are complete governed USD-zero experiments. Neither candidate crossed the frozen quality/stability gates, so the evidence-backed state remains:

**`NO_SELECTION` / no production provider claim.**

Historical frozen evidence must not be rewritten or replayed merely to improve the narrative.

## 9. Reproduction state

The previous reproduction workflow started from a clean checkout but did not provide PostgreSQL, which meant promoted Postgres tests could be skipped there even though separate Postgres workflows were green.

Issue #174 closes this by consolidating one provider-free clean-checkout workflow that runs:

```text
PostgreSQL 18
→ complete Python test suite with Postgres enabled
→ explicit identity/RLS + load + recovery P0 checks
→ ADR-004 controller regression
→ frozen EV-007 / EV-008 / EV-011
→ final delivery demo/evidence validation
→ final handoff audit
→ npm ci from committed package-lock
→ TypeScript typecheck / Vitest / production build
→ tracked repository cleanliness check
```

The full Chromium path remains separately gated by `full-product-playwright` and is not duplicated inside the clean-clone workflow.

## 10. Current critical path

```text
1. close clean-clone full reproduction       #174 / CURRENT P0
2. branch protection + final CI              NEXT P0
3. final freeze + benchmark/evidence bundle  NEXT P0
4. real human calibration/value collection   when reviewers/operators are available
5. runtime LangGraph comparison              P1 only if time/materiality justify
6. final provider/model benchmark            P1; USD0 and hard gates remain
7. adaptive model routing                    P1 only after measured benefit
8. OpenTelemetry standardization             P1 only if it improves handoff/ops
9. final frontend consolidation              P1 / final polish, no feature sprawl
```

## 11. Current non-claims

Do not claim:

- a production provider has been selected;
- human semantic calibration is complete;
- engineer minutes saved without real human observations;
- adaptive stopping improves runtime behavior before an oracle-free challenger wins;
- the CI load campaign establishes production capacity/SLOs;
- restart safety establishes deployment RTO/RPO, HA, multi-region failover or uptime;
- enterprise IAM/SSO is implemented;
- LangGraph or another framework is needed/superior before a controlled comparison;
- RAG/GraphRAG/vector DB/Kubernetes/Kafka/Redis/multi-agent/Temporal/MCP migration is justified without a measured gap and challenger win.

## 12. State update rule

This file is the mutable current-state summary. Accepted changes update it; historical ADRs, frozen experiment evidence and prior campaign artifacts remain immutable and authoritative for their original scopes.