# Production Final Implementation Log — 2026-09-05

**Scope:** final production promotion from `main@12b4753d3e39c86f7c68f0ea7b4f321549049fc7`  
**Execution branch:** `release/production-final`  
**Canonical plan:** [`../DELIVERY-PLAN.md`](../DELIVERY-PLAN.md)

No secrets, passwords or raw DSNs are recorded in this log.

## 1. Branch and governance baseline

### PASS

- Created `release/production-final` from exact current-main baseline `12b4753d3e39c86f7c68f0ea7b4f321549049fc7`.
- Rebaselined `ACTIVE-PROJECT-STATUS.md` to the real post-cleanup repository and external-infrastructure state.
- Added `decision-registry.yaml` with material decisions DP-001 through DP-010.
- Replaced the active delivery plan with the final dependency-ordered implementation plan.

### OPEN

- `main` protection and required-PR enforcement remain a later P0 release gate.

## 2. Architecture truth

### PASS

The product-visible architecture manifest was corrected so the promoted architecture no longer labels DuckDB as the serving observability store.

Added explicit current boundaries/components for:

- trusted runtime identity;
- PostgreSQL operational core;
- PostgreSQL runtime handoff;
- governed consequential-action custody/lease;
- PostgreSQL safe observability store;
- PostgreSQL LISTEN/NOTIFY wake-up with durable cursor truth;
- human semantic review;
- operational-value collection.

A regression test now guards these promoted architecture facts.

### NOT CLAIMED

Browser OIDC/IAM is still not implemented; the manifest states that the current runtime identity is not a complete browser OIDC claim.

## 3. Railway remote backend preparation

Historical service `hosted-pilot` was preserved rather than repurposed.

### PASS

Created a separate clean Railway service:

```text
service: production-api
source: pablo-marchina/academy-tractian
branch: release/production-final
build path: repository Dockerfile
restart: ON_FAILURE
public HTTPS domain: allocated
```

Non-secret fail-closed production configuration was installed with provider calls disabled.

### BLOCKED / NEXT

The connector refused transmitting secret DSN/signing values. No unsafe workaround was used.

Required secret variables must be installed through an approved Railway secret mechanism before live boot:

- internal PostgreSQL DSN;
- scoped PostgreSQL DSN;
- runtime identity signing secret.

After that: update exact release SHA, redeploy, validate DB connectivity/health/release identity/restart.

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

### Structural validation branch result

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

The same validated idempotent DDL groups were then applied to Neon main.

Final main validation:

```text
required product tables             15 / 15
required operational metadata        7 / 7
observability schema metadata        PASS
academy_tractian_rls superuser       false
academy_tractian_rls BYPASSRLS       false
run_ownership owner                  academy_tractian_owner
tenant SELECT policies               5
```

### Remaining DB work

This closes schema/role promotion, not all database production evidence. Still required:

- application connection from remote backend;
- free-tier suspend/wake reconnect;
- durable cursor catch-up;
- latency/capacity measurements;
- recovery evidence before any HA/RTO/RPO claim.

## 5. Current critical path after this log

```text
Railway secret injection
→ live fail-closed backend boot
→ health/release/DB connectivity
→ browser IAM/BFF/OIDC
→ multi-user remote negative tests
→ hosted provider tournament
→ real DecisionSource
→ real TRACTIAN transport
→ authorization/actions
→ production frontend + authenticated SSE
→ recovery/security/load campaigns
→ protected delivery + final evidence freeze
```

Optional framework/RAG/multi-agent work remains deferred unless a measured P0/P1 gap justifies a challenger experiment.
