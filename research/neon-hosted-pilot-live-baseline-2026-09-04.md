# Neon hosted pilot live baseline

**Date:** 2026-09-04  
**Status:** LIVE_BASELINE_COLLECTED; MIGRATION_NOT_EXECUTED  
**Candidate:** Neon Free managed PostgreSQL  
**Purpose:** record the first live, sanitized state evidence for the preregistered Neon + Auth0 hosted pilot without promoting the candidate or leaking credentials.

## Claim boundary

This artifact does **not** claim that Neon has passed the hosted state pilot. It records only facts observed before the exact repository migration runs through the intended application connections. In particular, `clean_migration_passed`, `pooled_tls_postgres_passed`, restart persistence, tenant isolation, SSE isolation and the full bundle result remain unmeasured.

## Provisioned environment

- project: `academy-tractian-hosted-pilot`;
- project identifier: `orange-wave-78442427`;
- region: `aws-sa-east-1` (São Paulo);
- PostgreSQL major version requested: `18`;
- server version observed from the live database: `18.6 (c5250a2)`;
- database: `academy_tractian`;
- branch: `main`;
- branch identifier: `br-calm-poetry-acsa9vbh`;
- compute: read-write;
- observed recovery state: `pg_is_in_recovery() = false`;
- history retention configured at project creation: `21600` seconds (6 hours);
- compute size requested: `0.25 CU` minimum and maximum.

The project was created only for the hosted pilot. This is infrastructure evidence, not a production-vendor selection.

## Clean database baseline

Before any Academy migration, the live database returned no schemas named:

- `academy_operational`;
- `academy_observability`.

This establishes a clean starting point for the future `clean_migration_passed` measurement. The project must remain unmodified by Academy schema DDL until the exact repository migrator is executed.

## Scoped-role experiment

The product requires two distinct PostgreSQL identities:

1. an internal/trusted migration and server-owned state identity;
2. a scoped read identity that is **not** superuser, does **not** bypass RLS and does **not** own the tenant-protected tables.

### Native Neon role API result

A role created through the Neon role-management API was empirically observed with:

- `rolsuper = false`;
- `rolcanlogin = true`;
- **`rolbypassrls = true`**.

Attempting to change that API-created role to `NOBYPASSRLS` from the project owner failed with `permission denied to alter role`.

Therefore the native role-creation path is **not admissible** for the Academy scoped role under the current account/project behavior. This is a live finding that could not be established from feature-list research alone.

The inadmissible experimental role was deleted after the test so it does not remain as unnecessary privileged surface.

### Explicit DDL role result

A replacement role was created explicitly by the database owner with a fail-closed privilege set. Its live PostgreSQL flags are:

| Property | Observed |
|---|---:|
| `rolsuper` | `false` |
| `rolcreaterole` | `false` |
| `rolcreatedb` | `false` |
| `rolbypassrls` | `false` |
| `rolinherit` | `false` |
| `rolcanlogin` | `true` |

This role is named `academy_tractian_rls`. A password was initialized and rotated through managed Neon role tooling; no password or connection string is stored in this artifact or in the repository.

Current live role inventory relevant to the pilot therefore contains:

- `academy_tractian_owner`: trusted owner/internal role, expected to have elevated DDL capabilities and `BYPASSRLS`;
- `academy_tractian_rls`: restricted scoped role with `NOBYPASSRLS`.

The restricted role still does not constitute RLS proof. It must be exercised through the repository migration and cross-tenant read/mutation campaign.

## TLS evidence boundary

The public connection material emitted for the application endpoints is configured to require TLS/channel binding. However, a SQL query executed through the Neon administrative connector reported `ssl = false` for **that connector session**. Because the connector session is not the intended public/pooled application connection, this observation is not used to pass or fail `pooled_tls_postgres_passed`.

The TLS gate remains **NOT_MEASURED** until the exact hosted runtime/migration executor connects through the intended product DSN and records the connection-level proof.

## Scale/suspend observation

The initial project-creation attempt tried to set a custom suspend timeout and Neon rejected the change for this account/plan. The project was then created using plan-supported defaults. The observed endpoint metadata must be treated as empirical plan behavior rather than inferred from generic documentation.

No availability, wake-up latency, capacity or SLO claim follows from this baseline.

## Current gate state

| Gate | State |
|---|---|
| Hosted managed database exists | `PASS` |
| PostgreSQL 18 baseline | `PASS` |
| Clean Academy schema starting point | `PASS` |
| Distinct restricted scoped role exists | `PASS` |
| Scoped role `NOBYPASSRLS` | `PASS` |
| Scoped role is non-superuser | `PASS` |
| Scoped role does not own RLS tables | `NOT_MEASURED` — tables do not exist yet |
| Exact repository migration | `NOT_MEASURED` |
| Pooled public TLS session | `NOT_MEASURED` |
| Operational schema readiness | `NOT_MEASURED` |
| Observability schema readiness | `NOT_MEASURED` |
| Cross-tenant read denial | `NOT_MEASURED` |
| Cross-tenant mutation denial | `NOT_MEASURED` |
| Restart persistence | `NOT_MEASURED` |
| Unexpected cash charge | `NOT_FINALIZED` |
| Required local components | target remains `0`; full hosted topology not yet executed |

## Next admissible step

Run `scripts/migrate_hosted_postgres.py` from an ephemeral hosted executor using secret-injected **distinct** internal and scoped Neon DSNs. The executor must consume the repository's frozen dependency set and exact Git SHA. Credentials must never be committed, printed into CI logs, added to an evidence JSON, or embedded in workflow source.

Only after the migration reports `PASS` may the pilot proceed to PostgreSQL readiness, RLS isolation, identity and full hosted-product tests.
