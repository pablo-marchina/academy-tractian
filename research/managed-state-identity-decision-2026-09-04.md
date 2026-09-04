# Managed PostgreSQL + hosted identity static decision

**Date:** 2026-09-04  
**Status:** STATIC_SCREENING_COMPLETE; LIVE_PILOT_NOT_RUN  
**Scope:** production-path managed state + browser identity under the cloud-only / USD0 constraints

## Decision question

Which hosted PostgreSQL and hosted identity combination deserves the next live production-path pilot without introducing a local dependency, an uncontrolled billing path, or a security downgrade?

This record is an admission decision only. `PILOT_ADMISSIBLE` is not a production selection and cannot be promoted without live evidence.

## Hard constraints

The database and identity layers are evaluated independently. There is no weighted score and no compensating tradeoff between them.

### Database admission

A database candidate must provide:

- hosted service with zero required local components;
- a bounded USD0 path;
- GA service maturity;
- PostgreSQL wire compatibility, TLS, pooling, transactions and RLS;
- no inactivity behavior that requires a human to manually reactivate the production service;
- at least 6 hours of restore history for the pilot;
- at least 500 MB free storage;
- no more than a minor migration from the current managed-PostgreSQL boundary.

Scale-to-zero is explicitly allowed when a new request reactivates the service automatically. It is not equivalent to a manually paused project.

### Identity admission

An identity candidate must provide:

- hosted service with zero required local components;
- a bounded USD0 production path without requiring a billing instrument;
- GA maturity;
- asymmetric JWT/JWKS verification compatible with the current resource server;
- `iss`, `sub` and configurable `aud`;
- a trustworthy organization/tenant claim, role and permission claims;
- configurable token TTL <= 3600 seconds;
- first-class organization support for the multi-tenant production claim;
- at least 1,000 free active users and at least 2 organizations so the tenant-isolation campaign can exercise a real cross-tenant pair;
- no inactivity behavior that requires manual service reactivation.

The existing application remains authoritative for authorization. Provider permissions are still intersected with the server allow-list and privileged permissions still require explicit server-side enablement.

## Static results

### PostgreSQL

| Candidate | Static result | Main evidence boundary |
|---|---|---|
| Supabase Free | `STATIC_REJECT` | Free project can be paused for inactivity and Free does not include automatic backups/PITR. |
| Neon Free | `PILOT_ADMISSIBLE` | PostgreSQL + TLS + PgBouncer + RLS; scale-to-zero wakes automatically; 6-hour restore window; no-credit-card Free path. |

Supabase remains a technically strong platform and is not rejected on API/database quality. It is rejected only against the final production-path constraints currently preregistered.

### Identity

| Candidate | Static result | Main evidence boundary |
|---|---|---|
| Supabase Auth Free | `STATIC_REJECT` | The Free project pause boundary remains and first-class end-user organizations are not the native tenancy model. |
| Clerk Hobby | `STATIC_REJECT` for current adapter | Excellent free B2B capacity, but the current v2 organization token representation is not yet proven compatible with the application's flat claim mapping. Do not infer compatibility. |
| Auth0 Free | `PILOT_ADMISSIBLE` | Direct JWT fit: `iss`, `sub`, `aud`, `azp`, `org_id`, permissions, RS256 and configurable access-token TTL; 5 Free organizations. |
| Neon Auth Free | `STATIC_REJECT` | Auth was rebuilt recently; current maturity/claim details required by this resource server are not sufficiently proven in the source set. Unknown fails closed. |
| WorkOS AuthKit | `STATIC_REJECT` | Production requires billing information, which violates the current no-billing-instrument guardrail even while usage may remain free. |

## Current static bundle decision

`neon-free + auth0-free` is the only currently `PILOT_ADMISSIBLE` bundle under the preregistered hard gates.

This is **not** a claim that Neon or Auth0 are production winners. It means only that this pair has enough public evidence to justify spending the next engineering cycle on a real hosted pilot.

## Why Clerk is not silently discarded

Clerk has a materially larger free organization allowance than Auth0 and strong organization/RBAC primitives. The current blocker is contract compatibility, not product quality. A later challenger may reopen Clerk if either:

1. a live token proves a safe flat claim mapping for `organization_id`, role and permissions, or
2. a preregistered minor adapter for Clerk v2 compact organization claims passes the same security tests without weakening the provider-neutral OIDC boundary.

No adapter will be added merely to make a vendor pass.

## Required live pilot before promotion

The Neon + Auth0 pilot must prove, on the real hosted path:

1. database migrations from a clean environment;
2. TLS pooled PostgreSQL connectivity from the hosted backend;
3. PostgreSQL RLS with two real organizations and at least two users;
4. Auth0 RS256/JWKS validation through `OIDCRuntimeContextProvider`;
5. exact `aud`, issuer, `org_id`, role/permission mapping and <=3600-second TTL;
6. allowed tenant request succeeds;
7. cross-tenant read and mutation both fail closed;
8. expired, wrong-audience, wrong-issuer, malformed and unknown-organization tokens fail closed;
9. SSE reconnect preserves tenant isolation;
10. restart/recovery preserves durable runs/evidence/evaluations;
11. no local database, local identity service or filesystem durability dependency;
12. zero unexpected cash charge during the controlled pilot.

Only after those gates pass may this bundle enter the hosted full-product Playwright and load/security campaigns.

## Evidence files

- `research/managed-state-identity-source-manifest-2026-09-04.json`
- `research/managed-state-identity-static-screening-2026-09-04.json`
- `src/academy_tractian/managed_state_identity_feasibility.py`
- `tests/test_managed_state_identity_feasibility.py`
- `tests/test_managed_state_identity_static_screening.py`

The source manifest and each candidate snapshot are hash-bound. Any material pricing, quota, maturity or contract change must create new dated evidence rather than editing this decision in place.
