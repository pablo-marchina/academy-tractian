# Final Plan Execution Start — 2026-09-05

**Branch:** `release/production-final`  
**PR:** `#196`  
**Execution authority:** [`../DELIVERY-PLAN.md`](../DELIVERY-PLAN.md)

This record starts execution of the consolidated final plan after the repository-wide audit and the remote hosting/IAM work already completed.

No secrets or raw credentials are recorded here.

## 1. Governance gate

Observed GitHub state:

```text
main protected                 false
required check enforcement     off
```

The connected GitHub integration exposes branch-protection reads but no administrative write action. Therefore:

```text
P0-A main protection = BLOCKED_USER_ACTION
```

Required owner action remains: require pull requests, require `final-ci-required / required-gate`, require an up-to-date branch, and block force pushes/deletion.

## 2. Railway production state revalidation

Railway project:

```text
academy-tractian-hosted-pilot
environment: production
```

Observed services:

```text
production-web    ONLINE
production-api    CRASHED / fail-closed
hosted-pilot      ONLINE / historical only
```

`production-api` logs were revalidated and still fail for exactly:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

No unsafe fallback was introduced.

## 3. Health/restart hardening

The live Railway desired state was updated for `production-api`:

```text
healthcheck path       /health
healthcheck timeout    60s
restart policy         ON_FAILURE
restart retries        5
```

`production-web` was explicitly synchronized to:

```text
healthcheck path       /
healthcheck timeout    120s
restart policy         ON_FAILURE
restart retries        5
```

The API is intentionally not redeployed solely for this change while its two mandatory Postgres secrets are still absent.

## 4. Infrastructure as Code decision

Current Railway documentation deprecates per-service `railway.toml/json` and promotes project-level `.railway/railway.ts`.

The production topology is therefore versioned using a named `production` partial that manages only `production-api` and `production-web`. Historical `hosted-pilot` remains outside this partial.

All existing Railway-managed values plus the two future PostgreSQL DSNs use `preserve()` so values remain external to Git.

A repository validator and dedicated CI workflow guard service scope, source branch, Dockerfile/root paths, healthchecks, region/replicas, restart policy, required preserved variables, absence of literal PostgreSQL URLs/secrets, and absence of accidental management of `hosted-pilot`.

A live `railway config plan` and first apply remain required before IaC ownership can be claimed as promoted.

## 5. Commit-chain correction

The first documentation update landed as an intermediate commit before the complete IaC tree was attached. The final integration commit was rebuilt on top of that live branch head rather than force-moving or rewriting history. The branch therefore remains linear and auditable; no history rewrite was used.

## 6. Next dependency

Two user actions are currently externally blocking the exact plan:

```text
1. enable GitHub main protection
2. insert the two Postgres DSNs into Railway production-api using the native secret UI/channel
```

Immediately after the DSNs exist:

```text
redeploy exact SHA
→ health/release/DB checks
→ restart/persistence
→ live two-user/two-tenant IAM acceptance
```

Provider tournament remains downstream and `NO_SELECTION` remains fail-closed until then.
