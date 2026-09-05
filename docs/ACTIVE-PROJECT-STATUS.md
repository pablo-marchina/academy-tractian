# Academy × TRACTIAN — Current Project Status

**Status:** production implementation / final remote promotion  
**Checkpoint:** 2026-09-05 BRT  
**Current `main`:** `12b4753d3e39c86f7c68f0ea7b4f321549049fc7`  
**Final implementation branch:** `release/production-final`  
**Draft integration PR:** `#196`  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file is the mutable source of truth for current state. Frozen/source-pinned historical evidence must not be rewritten.

## 1. Executive status

```text
formal product scope                         Agent + Evaluation in one solution
project cash-cost constraint                 USD 0 HARD CONSTRAINT
current main                                 12b4753d3e39c86f7c68f0ea7b4f321549049fc7
final implementation branch                  release/production-final
draft integration PR                         #196 / OPEN / DRAFT
latest required product gate                 PASS / final-ci-required required-gate
GitHub main protection                       BLOCKED_USER_ACTION / connector has no admin write

production agent runtime                     IMPLEMENTED / REGRESSION PASS
production deterministic evaluator           IMPLEMENTED
TRACTIAN typed tool registry                  18 operations
PostgreSQL serving persistence               IMPLEMENTED + REMOTE SCHEMA APPLIED
PostgreSQL observability/evaluation           IMPLEMENTED + REMOTE SCHEMA APPLIED
realtime durable truth                       PostgreSQL rows + sequence cursor
realtime wake-up                             LISTEN/NOTIFY + durable catch-up
read-only cross-replica handoff              IMPLEMENTED / required gate PASS
consequential-action safety                  IMPLEMENTED / action-lease gate PASS
React operator control room                  IMPLEMENTED
material decision registry                   IMPLEMENTED / ACTIVE

Railway production-web                       ONLINE / HTTPS / US East
Railway production-api                       CRASHED FAIL-CLOSED / missing only two Postgres DSNs
Railway API healthcheck desired state         /health / 60s / ON_FAILURE configured
Railway production topology IaC              VERSIONED / .railway/railway.ts; live IaC apply pending
Neon production schema                       APPLIED / STRUCTURALLY VALIDATED
Neon scoped role                             academy_tractian_rls / NOBYPASSRLS / non-superuser
remote RLS validation                        PASS on isolated validation branch
Neon Auth / Better Auth                      PROVISIONED on production main
browser IAM                                  CODE + HOSTED AUTH / LIVE E2E PENDING

production provider/model                    NO_SELECTION
production DecisionSource                    FAIL-CLOSED placeholder
production TRACTIAN transport                NOT COMPOSED
production authorization resolver            DENY-ALL baseline
remote capacity/SLO                          NOT PROVED
remote recovery/reconnect                    NOT PROVED
human semantic calibration                   NOT READY — labels required
operational-value claim                      NOT READY — observations required
adaptive runtime policy                      NOT PROMOTED; baseline first
```

## 2. Current target topology

```text
browser
→ production-web HTTPS
→ same-origin /auth
→ Neon Auth managed session
→ same-origin /api + SSE
→ Railway production-api
→ server-side session revalidation
→ server-owned user / organization / permissions
→ Neon PostgreSQL + RLS
→ durable runtime handoff / leases / fencing
→ selected hosted DecisionSource                  [OPEN]
→ AgentController
→ 18 typed TRACTIAN tools
→ real remote TRACTIAN transport                  [OPEN]
→ evidence-grounded final/clarify/abstain/escalate/action proposal
→ governed action confirmation + authorization    [OPEN remotely]
→ ProductionEvaluator
→ PostgreSQL observability/evaluation
→ durable cursor + LISTEN/NOTIFY
→ React Control Room
```

No component marked OPEN may be described as production-ready before hosted evidence closes it.

## 3. External infrastructure state

### Railway

`production-web` is online on `release/production-final` with:

- React/Vite production build;
- Caddy static serving;
- public HTTPS Railway domain;
- same-origin `/auth/*` proxy to production Neon Auth;
- same-origin `/api/*` and `/health` proxy to `production-api.railway.internal:8000`;
- SSE buffering disabled;
- one replica in `us-east4-eqdc4a`;
- explicit `ON_FAILURE` restart policy;
- `/` deployment healthcheck.

`production-api` exists separately from historical `hosted-pilot` and uses:

- `release/production-final`;
- repository production Dockerfile;
- one replica in `us-east4-eqdc4a`;
- explicit `ON_FAILURE` restart policy;
- `/health` deployment healthcheck with 60 second timeout;
- provider calls disabled;
- actions disabled at the current infrastructure/IAM boundary;
- managed `neon-auth` browser IAM mode.

Current boot remains intentionally fail-closed because exactly these values are absent:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

Those values must be inserted only through an approved Railway native secret channel.

### Railway Infrastructure as Code

The production topology is versioned in the current Railway IaC surface:

```text
.railway/railway.ts
```

The file is a named `production` partial so it manages only `production-api` and `production-web`. Historical `hosted-pilot` remains outside the partial and must not be deleted.

All existing Railway-managed values and the two future PostgreSQL DSNs are represented as `preserve()`. No secret value is stored in Git. Repository validation and a dedicated IaC CI workflow guard the expected service scope and reject literal PostgreSQL URLs.

A live `railway config plan`/apply remains pending before IaC ownership itself can be claimed as promoted. Dashboard/service state remains the effective platform state until that plan is reviewed and applied.

### Neon

The `academy_tractian` database contains the promoted `academy_operational` schema.

Validated evidence remains:

```text
required product tables          15 / 15
required operational metadata     7 / 7
observability schema metadata     PASS
scoped role                       academy_tractian_rls
scoped superuser                  false
scoped BYPASSRLS                  false
run_ownership owner               academy_tractian_owner
tenant SELECT policies             5
cross-tenant validation           org-a visible / org-b denied
```

Production Neon Auth is provisioned and trusts the production-web origin. Email/password sessions are enabled; email verification is not required, so verified-email identity is not claimed.

## 4. Immediate dependency gates

### Gate G1 — repository governance

Status: `BLOCKED_USER_ACTION`.

Required:

- protect `main`;
- require pull requests;
- require `final-ci-required / required-gate`;
- require up-to-date branch;
- block force push;
- block branch deletion.

The connected GitHub integration does not expose an admin write action for branch protection, so this must be completed by the repository owner.

### Gate G2 — remote backend serving

Status: `BLOCKED_USER_ACTION`.

Required:

1. insert `ACADEMY_POSTGRES_INTERNAL_DSN` in Railway `production-api`;
2. insert `ACADEMY_POSTGRES_SCOPED_DSN` in Railway `production-api`;
3. redeploy exact branch SHA;
4. verify `/health`, `/api/meta/release`, both DB roles and persistence;
5. restart and verify durable state.

No DSN may be committed or pasted into project documentation/chat.

### Gate G3 — live IAM and tenant isolation

Status: `WAITING_G2`.

After backend boot:

- User A / Tenant A and User B / Tenant B;
- cross-tenant REST reads = 0;
- cross-tenant SSE leakage = 0;
- cross-tenant action access/confirmation = 0;
- browser-supplied org/user/role/permissions ignored or denied;
- same-organization multi-user behavior tested;
- invalid/expired/mismatched/impersonated sessions fail closed.

### Gate G4 — hosted provider

Status: `NO_SELECTION`.

Run a preregistered USD0 tournament. Promotion requires quantitative evidence for task quality, tools, arguments, evidence, safety, latency, quota and stability.

### Gate G5 — real TRACTIAN path

Status: `WAITING_G4`.

Compose the real typed transport from the supplied contract. Do not guess endpoints or retry consequential writes blindly.

## 5. Current non-claims

Do not claim yet:

- full remote production readiness;
- Railway IaC ownership/apply convergence before a live plan/apply;
- IAM READY;
- verified-email identity;
- selected production model/provider;
- real production TRACTIAN integration;
- remote action execution;
- enterprise availability;
- measured production SLO/HA/RTO/RPO;
- human semantic calibration;
- engineer-time savings;
- adaptive-runtime superiority;
- distributed exactly-once external side effects.

## 6. State update rule

Every material change must update:

1. implementation/infrastructure;
2. validation evidence;
3. this current-state document;
4. `DELIVERY-PLAN.md`;
5. `decision-registry.yaml` when a material decision changes;
6. `docs/progress/` with chronological evidence.

A green CI result is not a substitute for hosted production evidence.
