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
final implementation branch                  release/production-final
open pull requests at rebaseline             none
final required CI on current main            PASS
GitHub branch protection                     NOT ENFORCED

production agent runtime                     IMPLEMENTED in repository
production deterministic evaluator           IMPLEMENTED
TRACTIAN typed tool registry                 18 operations
React operator control room                  IMPLEMENTED
PostgreSQL serving persistence               IMPLEMENTED in code + REMOTE SCHEMA APPLIED
PostgreSQL observability/evaluation           IMPLEMENTED in code + REMOTE SCHEMA APPLIED
realtime durable truth                       PostgreSQL rows + sequence cursor
realtime wake-up                             LISTEN/NOTIFY + durable catch-up
read-only cross-replica handoff              IMPLEMENTED / tested
consequential-action safety                  IMPLEMENTED / tested
architecture manifest                        REBASELINED to promoted PostgreSQL/runtime/action truth
material decision registry                   IMPLEMENTED

remote Railway historical pilot              PRESERVED / STALE, not current product
remote Railway production-api                CREATED from final branch / Dockerfile configured
remote Neon project                          PROVISIONED
remote production schema                     APPLIED / STRUCTURALLY VALIDATED
remote tenant-scoped DB role                 academy_tractian_rls / NOBYPASSRLS / non-superuser
remote RLS validation                        PASS on isolated migration-validation branch
remote public API domain                     CREATED; serving boot not yet proved
browser/end-user IAM                         NOT IMPLEMENTED
production provider/model                    NO_SELECTION
production TRACTIAN transport                NOT COMPOSED
production authorization resolver            DENY-ALL baseline
frontend production hosting                  NOT YET PROVED
remote capacity/SLO                          NOT PROVED
remote recovery/reconnect                    NOT PROVED

human semantic collector/protocol            IMPLEMENTED
real human semantic calibration              NOT READY — labels required
operational-value collector/analysis         IMPLEMENTED
real engineer-time/value claim               NOT READY — human observations required
adaptive runtime policy                      NOT PROMOTED; baseline first
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

The repository proves this architecture in controlled product/CI paths. The complete remote path is not yet a production claim because external provider, real TRACTIAN transport, browser IAM, serving boot and frontend hosting are not all composed and tested together.

## 3. External infrastructure actually provisioned

### Railway

The historical `hosted-pilot` service remains preserved as old evidence and is not the production service. A clean `production-api` service now exists in the same Railway project, sourced from `release/production-final`, configured to use the repository `Dockerfile`, restart on failure and expose a Railway HTTPS service domain. Non-secret fail-closed production variables are installed. Required secret values have not been transmitted through an unsafe channel; serving boot remains pending secret injection through an approved Railway secret mechanism.

### Neon

The existing `academy-tractian-hosted-pilot` Neon project and `academy_tractian` database now contain the promoted `academy_operational` schema.

Validated on the production branch:

```text
required product tables          15 / 15 present
required operational metadata     7 / 7 present
observability schema metadata     PASS
scoped role                       academy_tractian_rls
scoped superuser                  false
scoped BYPASSRLS                  false
run_ownership owner               academy_tractian_owner
tenant SELECT policies             5 present
```

Before application to main, the same migration was exercised on an isolated Neon validation branch. With two test organizations present and the scoped role active under `academy.organization_id=org-a`, the scoped query returned only the `org-a` row and did not expose the `org-b` row. The previously identified `academy_live_scoped` role remains unsuitable as tenant-scoped production evidence because it has `BYPASSRLS` and must not be used by the final application.

Reconnect/suspend-wake behavior remains a separate production-runtime campaign and is not implied by schema readiness.

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
1. complete active architecture/documentation truth synchronization
2. finish Railway production-api boot using approved secret injection
3. verify remote backend health/release/DB connectivity/restart
4. implement standards-based browser IAM + tenant-safe REST/SSE
5. run hosted provider tournament and compose winner or retain explicit blocker
6. compose real TRACTIAN transport + authorization resolver
7. deploy authenticated frontend and close live end-to-end path
8. run remote realtime/reconnect, adversarial-security and load campaigns
9. enforce main protection + deploy/rollback pipeline
10. calibrate semantic evaluation and collect operational-value evidence where possible
11. freeze final evidence bundle and release
```

## 8. Current non-claims

Do not claim yet:

- complete remote product production-readiness;
- a selected production model/provider;
- real production TRACTIAN integration;
- OAuth/OIDC end-user IAM;
- remote capacity/SLO/HA/RTO/RPO;
- Neon free-tier always-on/enterprise availability;
- human semantic calibration;
- engineer minutes saved/business value without observations;
- adaptive runtime superiority;
- distributed exactly-once external side effects.

## 9. State update rule

Update this file whenever current state changes. Never rewrite frozen/source-pinned historical artifacts to fit the present. Every material production decision must link to current evidence and preserve valid negative results and reversal triggers.
