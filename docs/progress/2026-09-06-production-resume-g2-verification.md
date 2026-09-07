# 2026-09-06 — Production resume and G2 verification

## Objective

Resume the consolidated production implementation plan from the current `release/production-final` line, preserving frozen historical evidence and converting source-gated claims into independently observed hosted evidence in dependency order.

## Current branch state

- integration PR: `#196` (`release/production-final` → `main`), still draft;
- pre-resume head: `a9347ce85402b9b888d04a88a7d3d4b88c17ba36`;
- first hosted G2 artifact SHA: `ff8b42058f9f79762a51d9e0e17e6ad17d2a2950`;
- production provider remains `NO_SELECTION`;
- consequential actions remain disabled for remote production until hosted IAM, real authorization and action gates pass.

## G2 Railway verification

The Railway production project and services were inspected directly.

Observed topology:

```text
project       academy-tractian-hosted-pilot
environment   production
web service   production-web
api service   production-api
legacy        hosted-pilot
```

### Failure 1 — missing database secrets

The original `production-api` deployment failed closed in `RemoteProductionConfig.from_env` with exactly these missing variables:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

The values were then attached to the **`production-api` service in the `production` environment** through Railway's native variable/secret surface. No DSN value was read into project evidence, copied into Git, logged by this audit, or pasted into documentation/chat.

### Failure 2 — mutable release metadata disagreed with the artifact

After the DSNs were present, Railway built artifact `ff8b42058f9f79762a51d9e0e17e6ad17d2a2950`, but serving correctly failed closed because the existing `ACADEMY_RELEASE_GIT_SHA` still referred to the previous deployed source identity.

This is positive evidence that the immutable release-identity contract rejects a runtime variable that claims a different commit from the baked artifact.

`ACADEMY_RELEASE_GIT_SHA` was then aligned to the exact baked SHA using the Railway service variable boundary.

### Failure 3 — Railway healthcheck port contract

With PostgreSQL configuration and release identity accepted, the container started successfully and Uvicorn reported application startup complete on `0.0.0.0:8000`; however Railway still marked the deployment failed because every `/health` probe returned `service unavailable`.

Railway's current healthcheck contract uses its `PORT` service variable. The service used an explicit target port/`ACADEMY_PORT=8000` but did not expose `PORT`, matching Railway's documented `service unavailable` failure mode.

The production service was corrected with:

```text
PORT=8000
```

and `.railway/railway.ts` now preserves `PORT` so future IaC convergence does not remove the healthcheck-port contract.

### Successful hosted boot

Deployment `1967d979-a2ae-4593-b0b6-93061e2fca74` reached Railway `SUCCESS` for commit:

```text
ff8b42058f9f79762a51d9e0e17e6ad17d2a2950
```

Railway's deployment evidence records:

```text
Application startup complete
Uvicorn running on http://0.0.0.0:8000
GET /health HTTP/1.1 200 OK
[1/1] Healthcheck succeeded!
```

Therefore the remote backend boot and Railway `/health` serving boundary are now proven for that artifact.

## Neon production verification during G2

The production Neon `main` branch remained `ready` while the hosted backend was promoted.

Observed production database state:

```text
database                         academy_tractian
academy_operational base tables 16
promoted scoped role             academy_tractian_rls
scoped role superuser            false
scoped role BYPASSRLS            false
legacy academy_live_scoped       BYPASSRLS=true / remains ineligible
```

Five tenant-scoped tables currently expose `tenant_select` policies:

```text
run_ownership
operational_pilot_tasks
operational_pilot_assignments
semantic_review_tasks
semantic_review_assignments
```

RLS is enabled on all five. The owner/internal role remains privileged by design; serving tenant reads use the promoted `academy_tractian_rls` role, not the BYPASSRLS compatibility role.

## Reproducible hosted verification

A dedicated hosted G2 smoke surface was added:

```text
.github/workflows/hosted-production-g2-smoke.yml
scripts/production_hosted_g2_smoke.py
```

The verifier checks the real public deployment for:

```text
/health == ok
/ready == ready
/api/meta/release schema == remote-production-release-v3
release_git_sha == expected deployed SHA
artifact_git_sha == expected deployed SHA
artifact_identity_verified == true
railway_runtime_identity_verified == true
environment == production
browser_iam_mode == neon-auth
cost_policy == usd0-hard-gate
```

This prevents a browser observation from being the only proof of immutable hosted release identity. The workflow is intentionally separate from provider-free repository reproduction.

## Remaining G2 work

Hosted backend boot is now successful, but the full G2 gate is not closed until all of the following are evidenced:

```text
hosted /api/meta/release equality       pending reproducible smoke result
hosted /ready                           pending reproducible smoke result
runtime durable state creation          pending
backend restart                         pending
state/cursor survives restart           pending
```

## State reconciliation discovered while resuming

The active ledger is slightly behind the current source state in two places:

1. `trusted_action_authorization.py` already implements an organization-bound, server-owned authorization contract and resolver factory with fail-closed missing/ambiguous/mismatched/inactive grants and canonical permission separation. The remaining work is real hosted source composition and acceptance, not initial source preparation.
2. `SECURITY-V1` is already preregistered and validator/regression-locked. Its hosted probes have **not** run and remain downstream of the functional hosted path.

These corrections must be synchronized into mutable active status/plan/decision documentation before final promotion. Frozen historical evidence remains unchanged.

## Non-claims

This checkpoint does **not** yet prove:

- full G2 durable restart/cursor acceptance;
- hosted IAM/multi-tenant acceptance;
- provider selection;
- real TRACTIAN reachability;
- hosted action authorization or execution;
- hosted adversarial security acceptance;
- remote capacity/SLO or recovery/backup claims.

CI/source evidence remains distinct from hosted production evidence.
