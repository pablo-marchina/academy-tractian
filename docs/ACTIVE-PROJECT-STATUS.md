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
previous complete-head required gate         PASS
current complete-head required gate          PENDING after release-identity hardening
GitHub main protection                       BLOCKED_USER_ACTION / connector has no admin write

production agent runtime                     IMPLEMENTED / REGRESSION PASS
production deterministic evaluator           IMPLEMENTED
TRACTIAN typed tool registry                  18 operations
PostgreSQL serving persistence               IMPLEMENTED + REMOTE SCHEMA APPLIED
PostgreSQL observability/evaluation           IMPLEMENTED + REMOTE SCHEMA APPLIED
realtime durable truth                       PostgreSQL rows + sequence cursor
realtime wake-up                             LISTEN/NOTIFY + durable catch-up
read-only cross-replica handoff              IMPLEMENTED / required gate baseline PASS
consequential-action safety                  IMPLEMENTED / action-lease baseline PASS
React operator control room                  IMPLEMENTED
material decision registry                   IMPLEMENTED / ACTIVE
backend immutable release identity           IMPLEMENTED / COMPLETE-HEAD CI PENDING

Railway production-web                       ONLINE / HTTPS / US East
Railway production-api                       CRASHED FAIL-CLOSED / missing only two Postgres DSNs
Railway API healthcheck desired state         /health / 60s / ON_FAILURE configured
Railway production topology IaC              VERSIONED / .railway/railway.ts; live IaC apply pending
Neon production schema                       APPLIED / STRUCTURALLY VALIDATED
Neon scoped role                             academy_tractian_rls / NOBYPASSRLS / non-superuser
remote RLS validation                        PASS on isolated validation branch
Neon Auth / Better Auth                      PROVISIONED on production main
browser IAM                                  CODE + HOSTED AUTH / LIVE E2E PENDING

provider tournament v3                       PREREGISTERED / PROVIDER-FREE VALIDATOR PRESENT
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
→ immutable artifact SHA verification
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

## 3. Release artifact identity

The backend production image now has an independent, immutable source-identity contract:

```text
Railway Git-backed build input       RAILWAY_GIT_COMMIT_SHA
baked runtime file                   /app/.academy-release-identity.json
identity schema                      academy-release-artifact-v1
OCI revision                         org.opencontainers.image.revision
public metadata schema               remote-production-release-v3
```

Image construction fails if the build SHA is missing or malformed. Serving boot fails before product/database builders if configured `ACADEMY_RELEASE_GIT_SHA` disagrees with the baked artifact, or if Railway's runtime SHA is present and disagrees with it.

`production-runtime` now contains positive and negative image identity checks and is consumed by `final-ci-required`. The current complete-head CI is still pending, so this is an implementation claim, not yet a validated hosted/release claim.

Hosted G2 evidence must show:

```text
release_git_sha == artifact_git_sha == exact deployed commit
artifact_identity_verified == true
railway_runtime_identity_verified == true  # when runtime system SHA is exposed
```

## 4. External infrastructure state

### Railway

`production-web` is online on `release/production-final` with React/Vite, Caddy, public HTTPS, same-origin `/auth`, same-origin `/api` + SSE, one `us-east4-eqdc4a` replica, explicit `ON_FAILURE` restart policy and `/` healthcheck.

`production-api` exists separately from historical `hosted-pilot` and uses the repository production Dockerfile, one `us-east4-eqdc4a` replica, `ON_FAILURE`, `/health` with 60-second timeout, provider calls disabled, actions disabled and managed `neon-auth` browser IAM mode.

Current boot remains intentionally fail-closed because exactly these values are absent:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

Those values must be inserted only through an approved Railway native secret channel. The next successful deployment must also use a configured release SHA matching the exact Git-backed build SHA; release identity drift is no longer tolerated.

### Railway Infrastructure as Code

`.railway/railway.ts` is a named `production` partial managing only `production-api` and `production-web`. Historical `hosted-pilot` remains outside the partial. Existing Railway-managed values and the two future PostgreSQL DSNs are represented with `preserve()` and no secret value is stored in Git.

Static validation and TypeScript DSL CI are versioned. A live `railway config plan`/apply remains pending before IaC ownership itself can be claimed as promoted.

### Neon

Validated production evidence remains:

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

## 5. Provider tournament state

Provider decision state remains `NO_SELECTION`.

A fresh v3 campaign is now preregistered over:

```text
17 scenarios
× 5 repetitions
× 2 current candidates
= 170 future live calls / 85 per candidate
```

The campaign is partitioned into five UTC daily packets of 34 calls to respect the Cloudflare Workers AI free-neuron envelope under the project's USD0 constraint. Historical D01/D02 results are excluded from the v3 denominator. Cash cost, gold leakage, unsafe unsupported actions, policy bypass, schema validity, quota, completeness, provenance and reliability are hard gates.

No v3 live run has been used to select a provider. Preregistration and provider-free validation do not constitute promotion.

## 6. Immediate dependency gates

### Gate G1 — repository governance

Status: `BLOCKED_USER_ACTION`.

Required: protect `main`; require pull requests; require `final-ci-required / required-gate`; require up-to-date branch; block force push; block branch deletion.

The connected GitHub integration has no administrative branch-protection write action, so this must be completed by the repository owner.

### Gate G2 — remote backend serving

Status: `BLOCKED_USER_ACTION`.

Required:

1. insert `ACADEMY_POSTGRES_INTERNAL_DSN` in Railway `production-api`;
2. insert `ACADEMY_POSTGRES_SCOPED_DSN` in Railway `production-api`;
3. redeploy the exact current branch SHA;
4. prove `/health` and `/api/meta/release` v3 exact artifact/config/runtime SHA agreement;
5. verify both DB roles, schema/stores and persistence;
6. restart and verify durable state/cursor.

No DSN may be committed or pasted into project documentation/chat.

### Gate G3 — live IAM and tenant isolation

Status: `WAITING_G2`.

Hosted acceptance must prove User A/Tenant A and User B/Tenant B, zero cross-tenant REST/SSE/action leakage, correct same-organization multi-user behavior, browser-supplied org/user/role/permission authority ignored or denied, and invalid/expired/mismatched/impersonated sessions fail closed. Offline negative-gap hardening may proceed while G2 is blocked, but cannot promote IAM to READY.

### Gate G4 — hosted provider

Status: `PREREGISTERED / NO_SELECTION`.

Execute the v3 USD0 tournament only after upstream gates permit hosted execution. Promotion requires complete quantitative evidence; no provider may be composed from preregistration alone.

### Gate G5 — real TRACTIAN path

Status: `WAITING_G4`.

Compose the real typed transport from the supplied contract. Do not guess endpoints or retry consequential writes blindly.

## 7. Current non-claims

Do not claim yet: full remote production readiness; Railway IaC ownership convergence; current complete-head CI PASS after release-identity changes; deployed release-metadata v3; IAM READY; verified-email identity; selected provider; real production TRACTIAN integration; remote action execution; enterprise availability; measured production SLO/HA/RTO/RPO; human semantic calibration; engineer-time savings; adaptive-runtime superiority; distributed exactly-once external side effects.

## 8. State update rule

Every material change must update implementation/infrastructure, validation evidence, this file, `DELIVERY-PLAN.md`, `decision-registry.yaml` when a material decision changes, and a chronological `docs/progress/` entry.

A green CI result is not a substitute for hosted production evidence.
