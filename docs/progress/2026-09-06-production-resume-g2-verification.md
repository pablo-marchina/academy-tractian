# 2026-09-06 — Production resume and G2 verification

## Objective

Resume the consolidated production implementation plan from the current `release/production-final` line, preserving frozen historical evidence and converting source-gated claims into independently observed hosted evidence in dependency order.

## Current branch state

- integration PR: `#196` (`release/production-final` → `main`), still draft;
- pre-resume head: `a9347ce85402b9b888d04a88a7d3d4b88c17ba36`;
- source/runtime CI at that head was green before this progress-only commit;
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

Observed service state:

```text
production-web    SUCCESS
production-api    CRASHED
hosted-pilot      SUCCESS (historical / outside production partial)
```

The latest `production-api` deployment fails closed in `RemoteProductionConfig.from_env` with exactly these missing variables:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

A direct variable-name inspection of `production-api` in the `production` environment also showed that neither name was attached to that service at verification time. No DSN value was read, copied, logged, committed or requested in chat.

## Required user action

Add the two DSNs through Railway's native variable/secret surface on the **`production-api` service in the `production` environment**, using the exact names above. Secret values must never be committed or pasted into repository documentation or chat.

After the variables are visible to the service, G2 continues immediately with:

```text
exact-SHA redeploy
→ /health 200
→ /api/meta/release identity equality
→ internal PostgreSQL connection PASS
→ scoped PostgreSQL connection PASS
→ schema/stores READY
→ create durable state
→ backend restart
→ state/cursor persistence proof
```

## State reconciliation discovered while resuming

The active ledger is slightly behind the current source state in two places:

1. `trusted_action_authorization.py` already implements an organization-bound, server-owned authorization contract and resolver factory with fail-closed missing/ambiguous/mismatched/inactive grants and canonical permission separation. The remaining work is real hosted source composition and acceptance, not initial source preparation.
2. `SECURITY-V1` is already preregistered and validator/regression-locked. Its hosted probes have **not** run and are still unauthorized until the functional hosted dependencies exist.

These corrections must be synchronized into mutable active status/plan/decision documentation before final promotion. Frozen historical evidence remains unchanged.

## Non-claims

This checkpoint does **not** prove:

- the two PostgreSQL DSNs are present on `production-api`;
- a successful Railway backend boot;
- hosted release-SHA parity;
- hosted IAM/multi-tenant acceptance;
- provider selection;
- real TRACTIAN reachability;
- hosted action authorization or execution;
- hosted adversarial security acceptance.

CI/source evidence remains distinct from hosted production evidence.
