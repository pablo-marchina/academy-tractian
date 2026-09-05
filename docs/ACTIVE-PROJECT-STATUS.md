# Academy × TRACTIAN — Current Project Status

**Status:** production implementation / final remote promotion  
**Checkpoint:** 2026-09-05 BRT  
**Current `main`:** `12b4753d3e39c86f7c68f0ea7b4f321549049fc7`  
**Final implementation branch:** `release/production-final`  
**Draft integration PR:** `#196`  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file is the sole mutable human-readable summary of current project state. Historical/frozen ADRs and result artifacts remain immutable evidence for their original scopes.

## 1. Executive status

```text
formal product scope                         Agent + Evaluation in one solution
project cash-cost constraint                 USD 0 HARD CONSTRAINT
current main                                 12b4753d3e39c86f7c68f0ea7b4f321549049fc7
final implementation branch                  release/production-final
draft integration PR                         #196 / OPEN / DRAFT
GitHub branch protection                     NOT ENFORCED

production agent runtime                     IMPLEMENTED in repository
production deterministic evaluator           IMPLEMENTED
TRACTIAN typed tool registry                  18 operations
React operator control room                   IMPLEMENTED
PostgreSQL serving persistence               IMPLEMENTED + REMOTE SCHEMA APPLIED
PostgreSQL observability/evaluation           IMPLEMENTED + REMOTE SCHEMA APPLIED
realtime durable truth                       PostgreSQL rows + sequence cursor
realtime wake-up                             LISTEN/NOTIFY + durable catch-up
read-only cross-replica handoff              IMPLEMENTED / tested
consequential-action safety                  IMPLEMENTED / tested
architecture manifest                        REBASELINED to promoted truth
material decision registry                   IMPLEMENTED / ACTIVE

remote Railway historical pilot              PRESERVED / STALE, not current product
remote Railway production-api                FINAL BRANCH / Docker build path / US East
remote Railway production-web                DEPLOYED / SUCCESS / US East
remote public product origin                 HTTPS domain allocated for production-web
same-origin auth/API proxy                   IMPLEMENTED in Caddy
remote Neon project                          PROVISIONED
remote production schema                     APPLIED / STRUCTURALLY VALIDATED
remote tenant-scoped DB role                 academy_tractian_rls / NOBYPASSRLS / non-superuser
remote RLS validation                        PASS on isolated migration-validation branch
browser/end-user IAM                         IN IMPLEMENTATION / managed Neon Auth challenger
backend managed-session verifier             IMPLEMENTED / PR regression running
remote backend serving boot                  BLOCKED on approved injection of two PostgreSQL DSNs
production provider/model                    NO_SELECTION
production TRACTIAN transport                NOT COMPOSED
production authorization resolver            DENY-ALL baseline
remote capacity/SLO                          NOT PROVED
remote recovery/reconnect                    NOT PROVED

human semantic collector/protocol            IMPLEMENTED
real human semantic calibration              NOT READY — labels required
operational-value collector/analysis         IMPLEMENTED
real engineer-time/value claim               NOT READY — human observations required
adaptive runtime policy                      NOT PROMOTED; baseline first
```

## 2. Current promoted / candidate product path

```text
browser
→ production-web HTTPS origin
→ managed browser session challenger (Neon Auth / Better Auth)
→ Caddy same-origin /auth + /api boundary
→ FastAPI
→ server-side managed-session revalidation
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

The managed-session IAM path is implemented as a **candidate under validation**, not yet a final production claim. The complete remote path remains incomplete until backend DB secrets are installed, authenticated REST/SSE multi-user acceptance passes, a provider is selected, and the real TRACTIAN transport/authorization path is composed.

## 3. External infrastructure actually provisioned

### Railway

The historical `hosted-pilot` service remains preserved as old evidence and is not the production service.

`production-api`:

- source branch explicitly corrected to `release/production-final`;
- repository Python 3.11 production Dockerfile;
- Railway US East Metal;
- provider calls disabled and actions denied while provider is `NO_SELECTION`;
- managed IAM mode configured through non-secret environment metadata;
- serving boot remains blocked only by the two PostgreSQL DSNs that the automation security boundary will not transfer between connectors.

`production-web`:

- source branch `release/production-final`;
- React/Vite production image + Caddy;
- Railway US East Metal;
- HTTPS public domain;
- same-origin `/auth/*` proxy to managed auth;
- same-origin `/api/*` and `/health` proxy to `production-api.railway.internal`;
- SSE proxy buffering disabled;
- latest authenticated-boundary deployment reached Railway `SUCCESS`.

No database credential or auth secret has been committed or written into documentation.

### Neon

The `academy-tractian-hosted-pilot` project / `academy_tractian` database contains the promoted `academy_operational` schema.

Validated on production main:

```text
required product tables          15 / 15
required operational metadata     7 / 7
observability schema metadata     PASS
scoped role                       academy_tractian_rls
scoped superuser                  false
scoped BYPASSRLS                  false
run_ownership owner               academy_tractian_owner
tenant SELECT policies             5
```

An isolated Neon branch was used for migration and RLS validation before main application. Under `academy.organization_id=org-a`, the scoped role returned the org-a row and did not expose org-b.

Neon Auth / Better Auth is currently provisioned only on the validation branch for IAM qualification. Its managed session/user/organization/member state was inspected before implementing the server-side session verifier. Production IAM promotion is still gated by CI and live multi-user acceptance.

### Supabase

No current Supabase project is part of the `academy-tractian` production topology.

## 4. Browser identity status

Current final-branch implementation:

- React `AuthBoundary` blocks the Control Room until managed session validation succeeds;
- sign-in/sign-up/sign-out/session calls stay same-origin under `/auth`;
- no tenant, role or permission authority is stored in browser state;
- FastAPI `NeonAuthRuntimeContextProvider` forwards only the opaque cookie to the managed session authority and forces server-side session validation;
- user/session identity mismatch, impersonation, missing cookie and auth-service failure all fail closed;
- active managed organization becomes tenant when present;
- otherwise a deterministic `user:<authenticated-user-id>` personal tenant preserves isolation;
- permissions remain server-defined by `DEFAULT_RUNTIME_PERMISSIONS`;
- old signed-bearer composition remains available for rollback/tests but is no longer required by the managed browser IAM mode.

PR #196 runs the regression matrix for this composition. Do not claim IAM READY until those checks and remote acceptance pass.

## 5. Consequential actions

The safety contract remains unchanged:

```text
agent proposes exact action
→ deterministic validation
→ private server-side custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ authorization + kill switch revalidated
→ persistent idempotency claim
→ non-transferable execution lease
→ exact custodied transport attempt
→ SUCCEEDED | FAILED | UNCERTAIN
```

Lost/ambiguous action ownership converges to `UNCERTAIN`; automatic blind replay remains forbidden. This is not a distributed exactly-once external-side-effect claim.

## 6. Provider and TRACTIAN state

Historical Cloudflare D01/D02 remain immutable negative/experimental evidence.

Current production provider state remains **`NO_SELECTION`**. Provider calls stay disabled in the remote bootstrap.

The real TRACTIAN transport is still not composed. The 18-operation typed contract exists, but implementation must follow the supplied TRACTIAN package/contract exactly rather than inventing endpoint behavior.

## 7. Immediate critical path

```text
1. finish PR #196 IAM regression checks
2. install the two PostgreSQL DSNs in production-api through approved Railway secret UI/channel
3. boot backend and verify DB connectivity + health + release identity + restart
4. run live managed-session + two-tenant REST/SSE negative acceptance
5. complete frontend authenticated E2E
6. run hosted USD0 provider tournament and compose winner or retain NO_SELECTION
7. compose real TRACTIAN transport + authorization resolver
8. validate governed consequential actions remotely
9. run realtime/reconnect, adversarial-security and load campaigns
10. enforce main protection + deploy/rollback pipeline
11. calibrate semantic evaluation / operational value where real evidence is available
12. freeze final evidence bundle and release
```

## 8. Current non-claims

Do not claim yet:

- complete remote product production-readiness;
- IAM READY before live multi-user acceptance;
- a selected production model/provider;
- real production TRACTIAN integration;
- remote capacity/SLO/HA/RTO/RPO;
- Neon/Railway enterprise always-on availability on a free tier;
- human semantic calibration;
- engineer minutes saved/business value without observations;
- adaptive runtime superiority;
- distributed exactly-once external side effects.

## 9. State update rule

Update this file whenever current state changes. Never rewrite frozen/source-pinned historical artifacts to fit the present. Every material production decision must link to current evidence and preserve valid negative results and reversal triggers.
