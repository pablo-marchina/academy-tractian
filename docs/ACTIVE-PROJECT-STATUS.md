# Academy × TRACTIAN — Current Project Status

**Status:** production rebaseline / pre-development cleanup  
**Checkpoint:** 2026-09-05 BRT  
**Current `main`:** `c5cc56acc74f5cc64b0f617ec718f95d01f8fca6`  
**Cleanup PR:** #192 (`chore/repository-cleanup`)  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file is the sole mutable human-readable summary of current project state. Historical ADRs/results remain immutable evidence for their original scopes.

## 1. Executive status

```text
formal product scope                         Agent + Evaluation in one solution
project cash-cost constraint                 USD 0 HARD CONSTRAINT
production agent runtime                    IMPLEMENTED in repository
production deterministic evaluator          IMPLEMENTED
TRACTIAN typed tool registry                18 operations
React operator control room                 IMPLEMENTED
PostgreSQL serving persistence              IMPLEMENTED
PostgreSQL observability/evaluation          IMPLEMENTED
PostgreSQL tenant RLS                       IMPLEMENTED / tested
realtime durable truth                      PostgreSQL rows + sequence cursor
realtime wake-up                            PostgreSQL LISTEN/NOTIFY + durable fallback
read-only cross-replica handoff              IMPLEMENTED / PostgreSQL-real tested
runtime generation fencing                  IMPLEMENTED
consequential actions                       IMPLEMENTED
confirmation + custody + idempotency         IMPLEMENTED
non-transferable action execution lease      IMPLEMENTED
lost action ownership                       UNCERTAIN / no replacement replay
full-product Playwright E2E                  PASS on current product gates
frontend lockfile + npm ci                   IMPLEMENTED / gated
clean-clone reproduction                    IMPLEMENTED / gated
stable final required CI                    final-ci-required / required-gate

current browser identity                     signed bearer HMAC-SHA256 V1
OAuth/OIDC/enterprise SSO                    NOT IMPLEMENTED
remote production deployment                NOT PROVED / P0 blocker
production serving local dependency          must become NONE before production claim
production capacity/SLO                      NOT PROVED
backup/restore + RTO/RPO                     NOT PROVED
remote HA/autoscaling                        NOT PROVED
GitHub branch protection                     NOT ENFORCED (main.protected=false)

human semantic collector/protocol            IMPLEMENTED
real human semantic calibration              NOT READY — labels required
operational-value collector/analysis         IMPLEMENTED
real engineer-time/business-value claim      NOT READY — human observations required
adaptive stopping                            evaluator/replay only
adaptive runtime stopping                    NOT PROMOTED
provider comparison D01/D02                  COMPLETE / historical / USD0
production provider/model                    NO_SELECTION

repository cleanup                           IN PROGRESS / PR #192
historical research workflows on product PRs being removed by PR #192
old hard-freeze sequencing                   SUPERSEDED by production rebaseline
```

## 2. Product path currently implemented

```text
browser request
→ signed RuntimeContextProvider
→ organization/user/identity/permissions
→ FastAPI product API
→ PostgreSQL tenant RLS + ownership/execution state
→ PostgreSQL runtime handoff/generation-fenced lease
→ RealtimeProductionRuntime
→ provider-neutral DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ deterministic B1/B2/B3 boundaries
→ normalized evidence
→ FINAL / CLARIFY / ABSTAIN / ESCALATE / action proposal
→ RunTrace
→ ProductionEvaluator
→ sanitized PostgreSQL observability/evaluation projection
→ durable cursor + LISTEN/NOTIFY wake-up
→ REST/SSE
→ React operator control room
```

Provider-free browser/CI acceptance replaces only the model decision source; it still exercises the product runtime, tool/policy boundary, PostgreSQL, evaluation, SSE and frontend.

## 3. Consequential actions

```text
agent proposes exact action
→ deterministic scope/schema/permission validation
→ private PostgreSQL custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ authorization + kill switch revalidated
→ atomic persistent idempotency claim
→ non-transferable PostgreSQL action execution lease
→ exact custodied action transport attempt
→ lease-fenced persistence/evaluation
→ safe REST/SSE/frontend projection
```

Current safety contract:

- duplicate confirmation does not start a second product transport attempt;
- healthy action ownership is not stolen by another replica;
- action leases are not transferred after expiry;
- stale/lost ownership converges to `UNCERTAIN`;
- stale late responses cannot publish false success;
- automatic blind replay is forbidden.

This is **not** a distributed exactly-once external-side-effect claim.

## 4. Identity and tenant isolation

Current repository identity is the project-owned `academy-runtime-v1` signed bearer envelope with HMAC-SHA256, issuer/audience/lifetime validation and explicit organization/user/identity/permission claims.

It is a real server-trusted boundary but not a complete end-user IAM product. Do not call it OAuth/OIDC/JWT/SSO.

PostgreSQL RLS independently restricts tenant data using a non-superuser, non-`BYPASSRLS`, non-owner application role and transaction-local organization scope. Tested cross-tenant rows are denied.

**P0 next state:** select and deploy a **USD-zero eligible** standards-based remote user-authentication path while preserving server-owned scope + RLS.

## 5. Persistence and distributed correctness

Promoted serving persistence:

```text
PostgreSQL  run ownership/execution + tenant isolation
PostgreSQL  runtime handoff payload/lease/generation
PostgreSQL  action custody/idempotency/action leases
PostgreSQL  sanitized observability/evaluation
PostgreSQL  semantic-review collection
PostgreSQL  operational-value collection
DuckDB      optional dev/benchmark compatibility only
```

The production package does not require DuckDB.

PostgreSQL-real tests prove the repository algorithms for:

- healthy read-only lease non-interference;
- expired read-only lease takeover;
- stale-generation fencing;
- recovered terminal persistence;
- healthy action non-interference;
- non-transferable action lease behavior;
- stale/lost action ownership → `UNCERTAIN`;
- no duplicate replacement action transport attempt.

These tests do not prove deployed HA/RTO/RPO/autoscaling.

## 6. Realtime

Durable `(run_id, sequence)` PostgreSQL rows are authoritative. `LISTEN/NOTIFY` is wake-up only, with bounded durable catch-up reads after missed notifications/reconnects.

The RT-WAKEUP experiment promoted LISTEN/NOTIFY after passing hard correctness gates and showing a successful measured sample with lower event p95 and lower idle durable-read volume. Historical runner variance remains preserved rather than hidden.

## 7. Evaluation state

Delivered:

- deterministic structural/safety/trajectory evaluation;
- EDD baseline/candidate comparison machinery;
- failure/stability/communication campaigns;
- semantic-review collection/protocol/source generation;
- operational-value collection + paired analysis;
- evaluator-only adaptive stopping replay.

Not yet evidence-ready:

- real human semantic labels/adjudication;
- judge-vs-human reliability metrics;
- real manual vs assisted engineer-time measurements;
- business-value / engineer-minutes-saved claim.

Those values must not be fabricated.

## 8. Provider/model state

D01/D02 are completed historical **USD-zero** provider experiments. D02 completed 32/32 attempts at USD 0.00, but neither tested Cloudflare model candidate crossed the frozen M1, M4 and M7 promotion gates.

Current state:

**`NO_SELECTION` / no production provider-model claim.**

This does **not** mean Cloudflare is rejected because of cost. Cloudflare was cost-eligible for D01/D02, but cost eligibility was not sufficient for technical promotion.

The next production-provider experiment must satisfy both conditions:

```text
hosted + remote + actual cash cost USD 0
AND
all preregistered quality/safety/reliability/production gates
```

Only USD-zero eligible hosted candidates may be selected. If none pass all gates, the result remains `NO_SELECTION`; the cost-zero hard constraint is not relaxed.

Historical D01/D02 packets are consumed and must not be replayed merely to search for a winner. Cloudflare can be reconsidered only through a new preregistered experiment if a materially new eligible model/configuration/hypothesis exists.

## 9. Load/recovery evidence boundaries

Existing provider-free load/concurrency measurements are descriptive and do not establish production capacity, SLO or worker sizing.

Existing restart/cross-replica campaigns prove conservative repository-level safety and fencing semantics, but do not establish deployed:

- availability;
- RTO/RPO;
- autoscaling behavior;
- database failover quality;
- multi-region behavior.

Those claims move to remote production campaigns in the current action plan, using only USD-zero eligible infrastructure for the selectable project path.

## 10. Repository/CI state

`main` remains unprotected as of the latest GitHub read on 2026-09-05:

```text
main.protected = false
required status-check enforcement = off
```

The repository nevertheless has a stable product CI contract:

```text
final-ci-required
  ├── clean-clone-full-product-reproduction
  ├── full-product-playwright
  ├── horizontal-runtime-handoff
  └── action-execution-lease
       ↓
  required-gate
```

PR #192 is cleaning navigation, canonical documentation and workflow activation. Historical E2/E9/E14/BIG-B research suites are being removed from ordinary product-PR triggers while their manual/research provenance is preserved.

## 11. Production rebaseline

The previous “hard freeze at end of 2026-09-05” sequence is superseded prospectively by the current requirement to make the system remotely deployable and production-usable rather than freezing known production blockers.

The production target requires **all** of the following simultaneously:

- actual project cash cost = USD 0;
- remote serving with no local dependency;
- real user IAM through a USD-zero eligible path;
- protected CI/CD;
- production observability;
- remote load/SLO evidence;
- backup/recovery/HA evidence where claimed;
- human semantic calibration;
- measured operational value;
- hosted provider/model selection by controlled comparison among USD-zero eligible candidates;
- complete live frontend visibility.

There is no paid fallback in the project-selection policy. Paid products may be researched as external references, but they are ineligible for final selection while the user-specified USD0 rule remains active.

## 12. Immediate critical path

```text
1. merge repository cleanup / corrected canonical rebaseline
2. systematic USD0-eligible remote hosting + PostgreSQL decision
3. remote USD0 production deployment with local-dependency + paid-spillover guards
4. USD0 standards-based IAM + multi-user/tenant acceptance
5. main protection + deploy pipeline + rollback
6. production telemetry/health correlation using USD0-eligible components
7. remote load/soak → evidence-based SLO
8. backup/failover/recovery → measured RTO/RPO where claimed
9. human semantic calibration
10. manual-vs-assisted operational-value study
11. hosted USD0 provider/model tournament
12. adaptive challengers only after P0 closure
13. final production freeze/evidence bundle
```

See `DELIVERY-PLAN.md` for acceptance details.

## 13. Current non-claims

Do not claim:

- the product is already remotely deployed production infrastructure;
- a production provider/model is selected;
- Cloudflare is selected merely because it satisfies USD0;
- a paid service is eligible for final selection under the current hard constraint;
- OAuth/OIDC/enterprise SSO is implemented;
- human semantic calibration is complete;
- engineer minutes saved without real human observations;
- adaptive stopping improves production runtime behavior;
- current CI load measurements establish production capacity/SLOs;
- repository correctness tests establish deployed RTO/RPO/HA/autoscaling/uptime;
- distributed exactly-once external side effects;
- GitHub branch protection is enforced;
- LangGraph, multi-agent, RAG, memory, MCP, Kafka, Redis or another technology is justified without a measured gap and challenger win.

## 14. State update rule

Update this file when **current state** changes. Do not rewrite frozen ADRs/results to match newer decisions. New evidence may prospectively supersede old decision roles while preserving historical bytes/provenance. User-specified hard constraints, including USD 0, remain binding until the user explicitly changes them.
