# Production Final Implementation Log — 2026-09-05

**Scope:** final production promotion from `main@12b4753d3e39c86f7c68f0ea7b4f321549049fc7`  
**Execution branch:** `release/production-final`  
**Canonical plan:** [`../DELIVERY-PLAN.md`](../DELIVERY-PLAN.md)  
**Draft integration PR:** `#196`

No secrets, passwords or raw DSNs are recorded in this log.

## 1. Branch and governance baseline

### PASS

- Created `release/production-final` from exact current-main baseline `12b4753d3e39c86f7c68f0ea7b4f321549049fc7`.
- Rebaselined `ACTIVE-PROJECT-STATUS.md` to the real post-cleanup repository and external-infrastructure state.
- Added `decision-registry.yaml` with material decisions DP-001 through DP-010.
- Replaced the active delivery plan with the final dependency-ordered implementation plan.
- Opened draft PR #196 to make the final branch continuously exercise PR CI without prematurely merging to `main`.

### OPEN

- `main` protection and required-PR enforcement remain a later P0 release gate.

## 2. Architecture truth

### PASS

The product-visible architecture manifest was corrected so the promoted architecture no longer labels DuckDB as the serving observability store.

Added explicit current boundaries/components for trusted runtime identity, PostgreSQL operational core, PostgreSQL runtime handoff, governed consequential-action custody/lease, PostgreSQL safe observability, PostgreSQL LISTEN/NOTIFY wake-up with durable cursor truth, human semantic review and operational-value collection.

A regression test now guards these promoted architecture facts.

## 3. Railway remote backend preparation

Historical service `hosted-pilot` was preserved rather than repurposed.

### PASS

Created a separate clean Railway service:

```text
service: production-api
source: pablo-marchina/academy-tractian
branch: release/production-final
build path: repository Dockerfile
region: Railway US East Metal
restart: ON_FAILURE
public HTTPS domain: allocated
```

The service source branch was explicitly corrected after detecting an earlier Railway source mismatch. Non-secret fail-closed production configuration is installed with provider calls disabled.

After the managed IAM composition was implemented, the remote config was updated to `browser_iam_mode=neon-auth`. This removes the former browser HMAC signing secret/issuer/audience requirement from this deployment path.

### BLOCKED / NEXT

The cross-connector security boundary refused transmitting the two PostgreSQL DSNs from Neon to Railway. No unsafe workaround was used.

Remaining secret variables must be installed through an approved Railway secret mechanism:

- internal PostgreSQL DSN;
- scoped PostgreSQL DSN.

After that: redeploy exact SHA, validate DB connectivity, `/health`, release identity and restart/persistence.

## 4. Neon PostgreSQL migration

Existing project/database:

```text
project: academy-tractian-hosted-pilot
database: academy_tractian
```

### Role audit

Observed candidate scoped roles included:

```text
academy_tractian_rls   superuser=false  BYPASSRLS=false
academy_live_scoped    superuser=false  BYPASSRLS=true
```

`academy_live_scoped` is excluded from the production scoped path.

### Validation-first migration

Created a temporary validation branch and applied the DDL derived from the production PostgreSQL initializers in independent idempotent groups:

1. operational core / ownership / run execution / RLS;
2. pending actions / idempotency / action execution leases;
3. runtime handoff;
4. operational-value collection;
5. semantic-review collection;
6. safe observability store.

Initial malformed multi-command driver attempts were fully rolled back and did not modify main. Migration was then validated using one DDL statement per transaction entry.

### Structural validation result

```text
required tables                    15 / 15
required operational metadata       7 / 7
observability schema metadata       PASS
scoped role superuser               false
scoped role BYPASSRLS               false
run_ownership owner                 academy_tractian_owner
tenant SELECT policies              5
```

### RLS validation

Two rows were placed on the isolated validation branch:

```text
rls-validation-a → org-a
rls-validation-b → org-b
```

Under the scoped role with transaction-local `academy.organization_id=org-a`, the query returned the org-a row and did not return the org-b row.

```text
cross-tenant read in validation test = 0
result                               = PASS
```

### Production main application

The same validated idempotent DDL groups were applied to Neon main. Final structural gates matched the validation branch.

### Remaining DB work

Schema/role promotion is closed. Runtime evidence still requires application connection, free-tier suspend/wake reconnect, durable cursor catch-up, latency/capacity and recovery measurements.

## 5. Production frontend hosting

Created `frontend/Dockerfile.production` and `frontend/Caddyfile.production` rather than reusing the backend image.

### Initial failure and correction

The first `production-web` deploy failed because Railway was still sourcing `main`, which did not contain the production frontend Dockerfile. The service source branch was corrected to `release/production-final`; no file-copy or stale-main workaround was used.

### PASS

```text
service: production-web
branch: release/production-final
runtime: Caddy serving built React/Vite SPA
region: Railway US East Metal
public HTTPS domain: allocated
same-origin /api proxy: production-api.railway.internal:8000
SSE reverse-proxy buffering: disabled
latest authenticated-boundary deployment: SUCCESS
```

This proves remote frontend deployment, not authenticated backend E2E.

## 6. Managed browser IAM challenger

### Validation substrate

Neon Auth / Better Auth was provisioned only on the isolated Neon validation branch before any production IAM claim. The production-web HTTPS origin was added as a trusted origin. Auth database structure for managed users, sessions, organizations and memberships was inspected.

### Frontend implementation

Added a React `AuthBoundary` that:

- checks `/auth/get-session?disableCookieCache=true` before rendering the Control Room;
- supports same-origin email sign-up/sign-in/sign-out;
- keeps credentials in managed HttpOnly cookie flow rather than application state;
- fails closed when the auth service is unavailable;
- does not accept or store tenant/permission authority.

Caddy now proxies `/auth/*` same-origin to the managed Neon Auth endpoint and `/api/*` to the private Railway backend.

### Backend implementation

Added `NeonAuthRuntimeContextProvider` and a dedicated PostgreSQL composition. The provider:

- accepts only the browser's opaque cookie;
- revalidates session server-side against managed auth with cookie-cache bypass;
- uses only remote HTTPS configuration;
- bounds cookie and response sizes and timeout;
- rejects missing, rejected, malformed, mismatched and impersonated sessions;
- ignores browser organization/role headers;
- derives a personal tenant `user:<verified-user-id>` if no managed active organization exists;
- otherwise uses the managed active organization;
- assigns only server-defined default runtime permissions.

`RemoteProductionConfig` now has explicit `signed-bearer` and `neon-auth` IAM modes. Signed bearer remains compatible for rollback/tests; managed IAM mode no longer requires the browser HMAC secret.

### Regression coverage added

Tests cover personal-tenant derivation, active organization mapping, missing cookie, user mismatch, impersonation, malformed JSON, managed rejection, auth-service failure and invalid/local auth base URLs. Remote-production config/composition tests cover both IAM modes.

### Current CI evidence

PR #196 triggered the repository PR matrix. At the first observed checkpoint:

```text
frontend-provider-free                    PASS
eval-driven-development-provider-free     PASS
observability-api-provider-free            PASS
production-runtime                         RUNNING
full-product-playwright                    RUNNING
final-ci-required                          RUNNING
additional reproduction/audit workflows   RUNNING
```

No IAM promotion claim is made until required regression checks finish and the live remote multi-user path passes.

## 7. Current critical path after this log

```text
finish PR #196 regression
→ approved Railway injection of internal/scoped PostgreSQL DSNs
→ live fail-closed backend boot
→ health/release/DB connectivity/restart
→ managed-session two-user/two-tenant REST+SSE negative acceptance
→ authenticated frontend E2E
→ hosted provider tournament
→ real DecisionSource
→ real TRACTIAN transport
→ authorization/actions
→ recovery/security/load campaigns
→ protected delivery + final evidence freeze
```

Optional framework/RAG/multi-agent work remains deferred unless a measured P0/P1 gap justifies a challenger experiment.
