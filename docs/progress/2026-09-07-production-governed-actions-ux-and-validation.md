# 2026-09-07 — Production UX, governed actions and live validation

**Record type:** append-only progress/evidence note  
**Date:** 2026-09-07 BRT  
**Canonical release branch at record time:** `release/production-final`  
**Current merged backend/runtime source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`

This note records the material progress completed during the 2026-09-07 production hardening conversation. It intentionally separates implementation, CI evidence, hosted deployment evidence and unresolved live-production validation.

## 1. Frontend and authentication progress

The public product remains hosted on Railway and uses the task-driven frontend architecture documented in `ACTIVE-PROJECT-STATUS.md` and `ARCHITECTURE.md`.

Material frontend/auth milestones during this hardening sequence include:

- progressive-disclosure UX work that moved the product away from exposing engineering depth as the default journey;
- task-driven navigation centered on Home, result/evidence drill-down, Analyses and Technical surfaces;
- managed-session resilience hardening in PR #207, including bounded reuse for already validated read sessions, fresh validation for mutations, explicit invalid-vs-unavailable auth states, and browser reconciliation on focus/visibility return;
- explicit asset-label grounding and evidence/stopping fixes through PRs #208 and #210;
- browser acceptance and clean-clone reproduction remained green after the later governed-action work.

A user review also identified continuing UX debt: the frontend can still feel visually dense and over-structured. The current design rule is therefore stronger than simple progressive disclosure:

> each screen should answer one primary user question, with specialist/technical depth outside the normal journey.

This UX simplification direction is a design/development target, not a claim of completed human usability validation. Automated browser tests and accessibility-oriented implementation checks are not substitutes for representative-user testing.

## 2. Governed consequential actions promoted in code

PR #211 promoted governed execution support for all five canonical TRACTIAN action operations.

Merge commit:

```text
1a1e7139bfa0361416120b3f21937c4048b5bb1f
```

Canonical action contract:

| Tool | Upstream operation | Required permission |
|---|---|---|
| `reprocess_analysis` | POST `/analyses/{analysis_id}/reprocess` | `action_low` |
| `request_specialist_analysis` | POST `/analyses/{analysis_id}/request-specialist` | `action_low` |
| `update_asset_config` | PATCH `/assets/{asset_id}` | `action_high` |
| `request_retraining` | POST `/models/{model_id}/request-retraining` | `action_high` |
| `escalate_case` | POST `/cases/{case_id}/escalate` | `escalate` |

The production action architecture preserves these invariants:

- canonical permissions are server-owned;
- tenant/company/resource authority is server-owned;
- browser/model output cannot grant permission or resource authority;
- proposals are privately custodied before execution;
- confirmation is for the exact existing action, not a new browser-supplied payload;
- action fingerprint and idempotency material are server-owned;
- external I/O is attempted only after the deterministic safety boundary passes;
- action execution is protected by durable lease/generation ownership;
- ambiguous write outcomes become `UNCERTAIN` and are not retried automatically;
- `ACCEPTED` is only used when the external API explicitly confirms acceptance.

The action state vocabulary remains:

```text
PENDING_CONFIRMATION
CONFIRMED
EXECUTING
ACCEPTED
BLOCKED
NOT_ACCEPTED
UNCERTAIN
```

## 3. Production configuration and initial deployment

The `production-api` Railway service was configured for the governed write path with:

- live provider execution;
- live TRACTIAN transport;
- `ACADEMY_ACTIONS_ENABLED=true`;
- a minimum-scope server-owned authorization grant document;
- no canonical permission or resource authority supplied by the browser/model.

Real secret/grant/user/resource values are intentionally excluded from this record.

Deployment for PR #211:

```text
Railway deployment: 9732a2cb-c321-4fcf-83f8-c6f87eeab06a
source SHA:        1a1e7139bfa0361416120b3f21937c4048b5bb1f
status:            SUCCESS
```

This proved that the governed-action composition can boot and serve under the production configuration. It did **not** by itself prove that all five upstream writes are accepted by the supplied TRACTIAN runtime.

## 4. Auditable five-action production smoke

PR #213 added the manual-only production smoke module:

```text
src/academy_tractian/governed_write_transport_smoke.py
```

PR #213 merge commit:

```text
3545d75c00ca30419e0f47e8b1950aa50cbbf462
```

The smoke contains no production credentials, tenant IDs, resource IDs or authorization grants in source. Runtime targets and credentials are supplied only through server-owned environment variables.

Before attempting writes it requires the hosted capability endpoint to report:

- exactly five canonical action operations;
- exactly five executable actions;
- `action_execution.enabled=true`;
- `action_execution.mode=GOVERNED_CONFIRMATION`;
- the governed action path enabled.

It then binds and sends all five canonical action requests through the same canonical binder and `ProductionTractianTransport` used by production. An action passes only when:

```text
HTTP status ∈ {200, 201, 202}
AND response.accepted == true
```

Safe output contains only action name, HTTP status, acceptance boolean and aggregate capability state. Credentials, resource IDs and upstream response bodies are not printed.

## 5. CI evidence for PR #213

The final required gate for the smoke head passed.

Required-gate workflow run:

```text
34164123263
```

Green jobs included:

- standalone production wheel smoke;
- PostgreSQL action execution lease and stale-result fencing;
- production runtime unit regression;
- Railway IaC TypeScript/static contracts;
- remote production image smoke and release-SHA drift rejection;
- horizontal PostgreSQL runtime/handoff/recovery;
- clean-clone full product reproduction;
- Chromium full-product Playwright acceptance;
- final `required-gate`.

The clean-clone job reproduced the full Python product suite with PostgreSQL enabled, promoted P0 campaigns, accepted ADR-004 controller boundary, EV-007/008/011 evidence, provider-free final-delivery/handoff/freeze checks, and frontend typecheck/tests/production build without mutating the checkout.

This is strong source/artifact regression evidence. It is not equivalent to upstream live write acceptance.

## 6. Hosted deployment of the smoke-capable release

PR #213 deployment:

```text
Railway deployment: 2cbc4215-f59a-4947-8691-0d4776458445
source SHA:        3545d75c00ca30419e0f47e8b1950aa50cbbf462
status:            SUCCESS
```

The built image baked the exact Railway Git commit SHA and the normal TRACTIAN connectivity pre-deploy probe returned HTTP 200.

A later Railway `redeploy` reused an older captured snapshot. Because a redeploy is not proof that newly edited service configuration was materialized, that run was **not** accepted as evidence that the five-action smoke had executed.

To force a fresh configuration snapshot, an operational validation marker was changed and a new deployment was created.

## 7. Decisive live write result: fail-closed 403

Fresh validation deployment:

```text
5ba36471-776c-4e15-919b-56e2da216b74
status: FAILED in pre-deploy by design
```

The failure was:

```text
RuntimeError: governed write transport smoke failed for update_asset_config: http_403:accepted_false
```

This is a successful safety outcome and a failed capability proof:

- the validation gate actually ran;
- it refused to promote a deployment when one canonical write was not accepted;
- the prior healthy production deployment remained serving;
- therefore the project must **not** claim that all five production actions have been live-proven.

Current truth:

> governed action execution is implemented, configured and advertised, but complete five-action upstream acceptance is not yet proven. `update_asset_config` was live-tested and rejected by the supplied TRACTIAN API with HTTP 403 under the then-current upstream identity binding.

## 8. Root cause: product identity and TRACTIAN actor identity are different concepts

An investigation reconstructed the immutable supplied TRACTIAN runtime and inspected its action authorization contract.

The supplied API resolves the acting user from the `x-user-id` header and applies endpoint-specific permission checks. For the production company scope under test, the supplied runtime has distinct upstream actors:

- an actor with `read + action_low`;
- a different actor with `read + action_high + escalate`.

Therefore one product-authenticated user identifier cannot simply be forwarded as the upstream TRACTIAN actor for all five action families.

The current `ProductionTractianTransport` correctly prevents caller/server headers from arbitrarily overriding the runner-bound `x-user-id`; however the existing execution binding couples the local requester user ID to that upstream header. That coupling is the discovered integration gap.

## 9. Corrective architecture in progress

The corrective design separates two trust concepts:

```text
local authenticated product user
  → owns tenant authorization, resource scope, confirmation, custody, idempotency and audit

server-owned TRACTIAN action actor
  → selected only at the final vendor network boundary
  → selected by company + canonical required permission
```

Required invariant:

```text
(company_id, required_permission) -> server-owned upstream actor
```

The browser, model and confirmation payload must never choose or submit that actor. Missing/ambiguous actor bindings must fail closed.

Implementation work has started on branch:

```text
fix/server-owned-upstream-action-actors
```

The intended components are a server-owned actor source and an action transport adapter that replaces only the final vendor-bound identity while preserving the original local user identity everywhere else in authorization and audit.

This corrective branch is **not merged or production-proven at the time of this record**.

## 10. Truth table

| Claim | State on 2026-09-07 |
|---|---|
| Release 0 remote product is hosted | PROVEN |
| managed auth + tenant isolation are active | IMPLEMENTED / tested in current scope |
| provider + TRACTIAN read path is live | PROVEN for exercised reads |
| five canonical action operations exist in contract | PROVEN |
| governed confirmation/custody/idempotency/lease architecture exists | PROVEN by tests and CI |
| actions can be configured/enabled in production | PROVEN by hosted boot |
| capability surface advertises five executable governed actions | PROVEN in hosted configuration |
| all five upstream action endpoints accept the current identity mapping | **NOT PROVEN** |
| `update_asset_config` accepted under current mapping | **FALSE in live smoke: HTTP 403** |
| failed validation can leave healthy production serving | PROVEN |
| server-owned upstream actor routing fixes the 403 | DESIGNED / implementation in progress, not yet proven |
| actions can be guaranteed to succeed forever | impossible claim; external dependencies can fail |

## 11. Reliability guarantee target

The correct production guarantee is not “every external action succeeds forever.” The controllable contract is:

- deterministic local authorization and tenant/resource scope;
- exact operator confirmation;
- one-shot/idempotent write custody;
- server-owned upstream identity mapping;
- explicit upstream acceptance required for `ACCEPTED`;
- fail closed on missing permission, actor mapping, release drift or unhealthy dependency;
- no invented success;
- no blind retry after an ambiguous write;
- deployment validation prevents a failing release from replacing a healthy one.

## 12. Next gate

Before claiming complete governed-action readiness:

1. finish the server-owned upstream actor routing implementation;
2. test company/permission actor selection and fail-closed missing/ambiguous mappings;
3. pass the full required CI matrix again;
4. merge by expected green head SHA;
5. deploy the exact merged SHA;
6. execute the auditable five-action smoke against approved supplied-runtime resources;
7. require all five actions to return an accepted HTTP status and `accepted=true`;
8. repeat idempotency/duplicate/uncertain-outcome checks without weakening safety policy;
9. record the final live evidence prospectively.

Until those gates close, active documentation must describe the action path as **enabled but live-validation incomplete**, never as universally successful.