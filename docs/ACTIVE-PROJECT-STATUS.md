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
latest required product gate                 PASS / final-ci-required required-gate
GitHub branch protection                     NOT ENFORCED

production agent runtime                     IMPLEMENTED / REGRESSION PASS
production deterministic evaluator           IMPLEMENTED
TRACTIAN typed tool registry                  18 operations
React operator control room                   IMPLEMENTED
PostgreSQL serving persistence               IMPLEMENTED + REMOTE SCHEMA APPLIED
PostgreSQL observability/evaluation           IMPLEMENTED + REMOTE SCHEMA APPLIED
realtime durable truth                       PostgreSQL rows + sequence cursor
realtime wake-up                             LISTEN/NOTIFY + durable catch-up
read-only cross-replica handoff              IMPLEMENTED / required gate PASS
consequential-action safety                  IMPLEMENTED / action-lease gate PASS
architecture manifest                        SYNCHRONIZED to managed-session candidate + compatibility identity
material decision registry                   IMPLEMENTED / ACTIVE

remote Railway historical pilot              PRESERVED / STALE, not current product
remote Railway production-api                FINAL BRANCH / Docker / US East / FAIL-CLOSED
remote Railway production-web                DEPLOYED / SUCCESS / US East
remote public product origin                 HTTPS domain allocated for production-web
same-origin auth/API proxy                   IMPLEMENTED in Caddy
remote Neon project                          PROVISIONED
remote production schema                     APPLIED / STRUCTURALLY VALIDATED
remote tenant-scoped DB role                 academy_tractian_rls / NOBYPASSRLS / non-superuser
remote RLS validation                        PASS on isolated migration-validation branch
production Neon Auth                         PROVISIONED on Neon main / trusted product origin
browser/end-user IAM                         CODE + HOSTED AUTH PROVISIONED / LIVE E2E PENDING
backend managed-session verifier             IMPLEMENTED / production-runtime PASS
remote backend serving boot                  BLOCKED only on approved injection of two PostgreSQL DSNs
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
→ managed browser session candidate (Neon Auth / Better Auth on production main)
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

The managed-session IAM infrastructure and code are now present in the production topology, but IAM is still **not READY** until the DB-backed API can boot and live two-user/two-tenant REST/SSE negative acceptance passes. The complete remote agent path also remains incomplete until a provider is selected and real TRACTIAN transport/authorization are composed.

## 3. External infrastructure actually provisioned

### Railway

The historical `hosted-pilot` service remains preserved as old evidence and is not the production service.

`production-api`:

- source branch `release/production-final`;
- repository Python 3.11 production Dockerfile;
- Railway US East Metal;
- provider calls disabled and consequential actions denied while provider is `NO_SELECTION`;
- managed IAM mode points to the production-main Neon Auth endpoint;
- latest boot fails closed with exactly two missing required values: `ACADEMY_POSTGRES_INTERNAL_DSN` and `ACADEMY_POSTGRES_SCOPED_DSN`;
- no other mandatory production configuration is currently reported missing.

`production-web`:

- source branch `release/production-final`;
- React/Vite production image + Caddy;
- production Docker build forces browser auth enabled while provider-free dev/CI remains deterministic;
- Railway US East Metal;
- HTTPS public domain;
- same-origin `/auth/*` proxy now points to Neon Auth on production main;
- same-origin `/api/*` and `/health` proxy to `production-api.railway.internal`;
- SSE proxy buffering disabled;
- post-production-Auth-host redeploy reached Railway `SUCCESS`.

No database credential or authentication secret is committed or recorded in documentation.

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

Neon Auth / Better Auth was first qualified on the isolated validation branch, then provisioned on the production main branch after managed-session regression and provider-free browser acceptance were green. The production product origin is in its trusted-origin allowlist. Current production Auth supports managed email/password sessions; email verification is not currently required, so **verified-email identity is not claimed**. Live authenticated API/SSE multi-user acceptance remains open.

### Supabase

No current Supabase project is part of the `academy-tractian` production topology.

## 4. Browser identity status

Current final-branch implementation:

- production React `AuthBoundary` blocks the Control Room until managed session validation succeeds;
- sign-in/sign-up/sign-out/session calls stay same-origin under `/auth`;
- provider-free Vite/CI does not enable the external browser-auth gate, while `Dockerfile.production` forces it on;
- no tenant, role or permission authority is stored in browser state;
- FastAPI `NeonAuthRuntimeContextProvider` forwards only the opaque cookie to the managed session authority and forces server-side session validation with cookie-cache bypass;
- user/session identity mismatch, impersonation, missing cookie and auth-service failure all fail closed;
- active managed organization becomes tenant when present;
- otherwise a deterministic `user:<authenticated-user-id>` personal tenant preserves isolation;
- permissions remain server-defined by `DEFAULT_RUNTIME_PERMISSIONS`;
- old signed-bearer composition remains available for rollback/tests but is no longer required by the managed browser IAM mode.

Regression evidence is green for the backend managed-session implementation and provider-free browser flow. `final-ci-required` also passed its `required-gate`. Do not claim IAM READY until live authenticated two-user/two-tenant acceptance passes through the remotely hosted backend.

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
1. install the two PostgreSQL DSNs in production-api through approved Railway secret UI/channel
2. boot backend and verify DB connectivity + health + release identity + restart
3. run live managed-session + two-user/two-tenant REST/SSE negative acceptance
4. close authenticated frontend E2E and mark IAM capability accordingly
5. run hosted USD0 provider tournament and compose winner or retain NO_SELECTION
6. compose real TRACTIAN transport + authorization resolver
7. validate governed consequential actions remotely
8. run realtime/reconnect, adversarial-security and load campaigns
9. enforce main protection + deploy/rollback pipeline
10. calibrate semantic evaluation / operational value where real evidence is available
11. freeze final evidence bundle and release
```

## 8. Current non-claims

Do not claim yet:

- complete remote product production-readiness;
- IAM READY before live multi-user acceptance;
- verified-email identity under the current Auth configuration;
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
