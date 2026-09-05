# Academy × TRACTIAN — Current Project Status

**Status:** production implementation / final remote promotion  
**Checkpoint:** 2026-09-05 BRT  
**Current `main`:** `12b4753d3e39c86f7c68f0ea7b4f321549049fc7`  
**Final implementation branch:** `release/production-final`  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file is the sole mutable human-readable summary of current project state. Historical/frozen ADRs and result artifacts remain immutable evidence for their original scopes.

## 1. Executive status

```text
formal product scope                         Agent + Evaluation in one solution
project cash-cost constraint                 USD 0 HARD CONSTRAINT
current main                                 12b4753d3e39c86f7c68f0ea7b4f321549049fc7
repository branches before final work        main only after reconciliation
open pull requests at rebaseline              none
final required CI on current main             PASS
GitHub branch protection                      NOT ENFORCED

production agent runtime                      IMPLEMENTED in repository
production deterministic evaluator            IMPLEMENTED
TRACTIAN typed tool registry                  18 operations
React operator control room                   IMPLEMENTED
PostgreSQL serving persistence                IMPLEMENTED in code
PostgreSQL observability/evaluation            IMPLEMENTED in code
realtime durable truth                        PostgreSQL rows + sequence cursor
realtime wake-up                              LISTEN/NOTIFY + durable catch-up
read-only cross-replica handoff               IMPLEMENTED / tested
consequential-action safety                   IMPLEMENTED / tested

remote Railway project                       PROVISIONED PILOT / STALE, not current product
remote Neon project                          PROVISIONED / database currently not migrated
remote production schema                     NOT YET APPLIED
remote tenant-scoped DB role                  MUST BE RECREATED/VALIDATED without BYPASSRLS
remote public product URL                     NOT YET PROVED
browser/end-user IAM                          NOT IMPLEMENTED
production provider/model                     NO_SELECTION
production TRACTIAN transport                 NOT COMPOSED
production authorization resolver             DENY-ALL baseline
frontend production hosting                  NOT YET PROVED
remote capacity/SLO                           NOT PROVED
remote recovery/reconnect                     NOT PROVED

human semantic collector/protocol             IMPLEMENTED
real human semantic calibration               NOT READY — labels required
operational-value collector/analysis          IMPLEMENTED
real engineer-time/value claim                NOT READY — human observations required
adaptive runtime policy                       NOT PROMOTED; baseline first
```

## 2. Current promoted logical product path

```text
browser
→ end-user IAM target (standards-based; not yet deployed)
→ FastAPI/BFF product boundary
→ server-owned organization/user/permissions
→ PostgreSQL ownership + tenant isolation
→ runtime handoff / generation-fenced read lease
→ RealtimeProductionRuntime
→ provider-neutral DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ deterministic safety boundaries
→ normalized evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE | ACTION_PROPOSAL
→ RunTrace
→ ProductionEvaluator
→ sanitized PostgreSQL observability/evaluation
→ durable cursor + LISTEN/NOTIFY wake-up
→ REST/SSE
→ React Production Control Room
```

The repository proves this architecture in controlled product/CI paths, but the complete remote path is not a production claim until the external provider, TRACTIAN transport, IAM, hosted database, frontend and backend are composed and tested together.

## 3. External infrastructure actually provisioned

### Railway

A project/service named `academy-tractian-hosted-pilot` exists. It belongs to an older preflight experiment, uses a stale Railpack/start-command configuration and is not evidence that the current Docker production server is live.

### Neon

A project named `academy-tractian-hosted-pilot` and database `academy_tractian` exist. Project roles were created previously, but the current production schema has not been applied to the live database. A scoped role used for tenant traffic must be a non-owner, non-superuser, `NOBYPASSRLS` login role and must pass the runtime identity guard after migration.

### Supabase

No current Supabase project is part of the `academy-tractian` production topology. A connected Supabase account/project is not evidence that this product uses Supabase.

## 4. Consequential actions

The current product safety contract is preserved:

```text
agent proposes exact action
→ deterministic schema/scope/permission/evidence validation
→ private server-side custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ current authorization + kill switch revalidated
→ persistent idempotency claim
→ non-transferable action execution lease
→ exact custodied transport attempt
→ SUCCEEDED | FAILED | UNCERTAIN
```

Lost/ambiguous action ownership converges to `UNCERTAIN`; automatic blind replay remains forbidden. This is not a distributed exactly-once external-side-effect claim.

## 5. Evaluation and research state

Implemented:

- deterministic structural/safety/trajectory evaluation;
- EDD baseline/candidate comparison machinery;
- failure/stability/communication campaigns;
- semantic-review collection/protocol;
- operational-value collection + paired analysis;
- evaluator-only adaptive stopping replay;
- preserved experiment provenance and negative results.

Not yet claim-ready:

- real human semantic calibration;
- judge-vs-human reliability;
- real manual-vs-agent-assisted engineer-time measurements;
- business-value claims;
- adaptive runtime superiority.

## 6. Provider state

Historical Cloudflare D01/D02 were USD-zero experiments and remain immutable evidence. They did not pass the complete frozen promotion contract.

Current production provider state remains:

**`NO_SELECTION`**.

A new provider may be promoted only after a new controlled comparison among currently USD-zero eligible hosted candidates. Paid candidates may be external references but cannot be selected while the project USD0 hard gate remains active.

## 7. Immediate critical path

```text
1. correct active architecture/status truth
2. establish decision registry for material choices
3. select/validate final USD0 remote topology
4. create safe PostgreSQL roles and apply production migrations
5. deploy current immutable backend and expose health/version
6. implement standards-based browser IAM + tenant-safe REST/SSE
7. run hosted provider tournament and compose winner or retain explicit blocker
8. compose real TRACTIAN transport + authorization resolver
9. deploy authenticated frontend and close live end-to-end path
10. run remote realtime/reconnect, adversarial-security and load campaigns
11. enforce main protection + deploy/rollback pipeline
12. calibrate semantic evaluation and collect operational-value evidence where possible
13. freeze final evidence bundle and release
```

## 8. Current non-claims

Do not claim yet:

- remote product production-readiness;
- a selected production model/provider;
- real production TRACTIAN integration;
- OAuth/OIDC end-user IAM;
- tenant isolation on the currently provisioned Neon role before it passes the production RLS guard;
- capacity/SLO/HA/RTO/RPO from repository CI;
- human semantic calibration;
- engineer minutes saved/business value without observations;
- adaptive runtime superiority;
- enterprise 24/7 HA on a free tier;
- distributed exactly-once external side effects.

## 9. State update rule

Update this file whenever current state changes. Never rewrite frozen/source-pinned historical artifacts to fit the present. Every material production decision must link to current evidence and preserve valid negative results and reversal triggers.
