# Neon Free + Auth0 Free hosted production-path pilot

**Date:** 2026-09-04  
**Status:** PREREGISTERED; LIVE_RUN_NOT_STARTED  
**Candidate bundle:** `neon-plus-auth0`  
**Purpose:** determine whether the only statically admissible managed-state + identity bundle can safely enter the full hosted-product campaign.

## Non-claim boundary

This protocol does not select Neon or Auth0 for production. Static admission only means the bundle deserves a live experiment. No hosted production, capacity, availability, security, recovery or tenant-isolation claim exists until the corresponding live gates pass on one exact code SHA.

## Hypothesis

A hosted deployment using Neon Free as PostgreSQL and Auth0 Free as the browser identity issuer can run the existing provider-neutral product path with:

- zero required local components;
- zero unexpected cash charge;
- the existing PostgreSQL operational/observability stores;
- the existing provider-neutral `OIDCRuntimeContextProvider`;
- two real organizations with cross-tenant denial enforced by application + PostgreSQL boundaries;
- durable recovery and SSE tenant isolation.

## Frozen identity profile

The pilot uses the declarative `AUTH0_PILOT_PROFILE` only. No Auth0 SDK is allowed in the backend.

Required public mapping:

| Contract field | Auth0 pilot claim |
|---|---|
| algorithm | `RS256` |
| organization | `org_id` |
| role | `https://academy.tractian/role` |
| permissions | `permissions` |
| identity | `sub` |
| authorized party | `azp` |
| token TTL | <= 3600 seconds |

The role claim is a required custom namespaced claim. Native provider permissions are accepted only after intersection with the server-owned permission allow-list. Privileged application permissions remain disabled unless a separate deterministic server-side authorization gate is promoted.

## Minimum live topology

- hosted backend candidate admitted by the deployment pilot;
- Neon Free managed PostgreSQL;
- Auth0 Free tenant/application/API;
- hosted frontend origin;
- supplied hosted TRACTIAN API;
- one hosted provider/model admitted by provider feasibility;
- two Auth0 organizations (`tenant-a`, `tenant-b` or equivalent);
- at least one distinct test user per organization.

No local Postgres, local identity server, local LLM, local durable file, localhost callback or operator machine may be required for the running product.

## Pre-run freeze

Before collecting evidence:

1. record exact Git SHA;
2. record deployment artifact/image digest where available;
3. record sanitized SHA-256 of deployment origin, DB endpoint hostname and identity issuer;
4. verify source/static-screen evidence is current;
5. initialize schemas only through the documented migration path;
6. freeze Auth0 issuer, API audience, JWKS URL, client/authorized-party ID and custom role Action/configuration;
7. freeze the two organizations and test-user assignments;
8. do not change RLS policies, claim mapping or authorization code after the first scored request.

Any material configuration change creates a new pilot run rather than mutating the prior result.

## Execution order

### P1 — managed PostgreSQL baseline

1. Apply migrations from a clean managed database state.
2. Connect through the intended pooled TLS endpoint.
3. Verify operational, observability and campaign schemas are ready.
4. Start the hosted backend without any durable local path.

Hard stop if migration, TLS pooling or readiness fails.

### P2 — positive Auth0 resource-server path

Using a real Auth0 access token for organization A:

1. verify JWKS RS256 signature;
2. exact issuer;
3. exact API audience;
4. authorized party/client;
5. `org_id` mapping;
6. namespaced role mapping;
7. permissions allow-list intersection;
8. token TTL <= 3600 seconds;
9. create/read an allowed organization-A run through the normal product API.

Hard stop if any identity contract is inferred from browser headers or bypassed through a test-only route.

### P3 — adversarial identity matrix

The normal hosted API must reject:

- expired token;
- wrong audience;
- wrong issuer;
- malformed token;
- unauthorized `azp`;
- missing organization;
- unknown organization;
- missing required role claim;
- malformed permissions claim.

These are resource-server requests, not isolated unit tests.

### P4 — tenant isolation

Create distinct state for organizations A and B, then prove:

1. A can read its own run;
2. B cannot read A's run;
3. B cannot mutate/confirm A's action state;
4. guessed run IDs do not cross tenant boundaries;
5. organization switching requires a newly valid organization-scoped token/context and cannot be supplied through a request header/body override.

Required result: zero cross-tenant reads and zero cross-tenant mutations.

### P5 — SSE isolation

1. open an authenticated run event stream for A;
2. generate A and B events;
3. reconnect A using the documented last-event mechanism;
4. prove only A's safe projection appears before and after reconnect;
5. repeat with B.

Required result: zero tenant leaks.

### P6 — restart/recovery

1. create durable run/evidence/evaluation state;
2. terminate/restart the hosted backend process/deployment;
3. reconnect through the same public product path;
4. prove required durable state is preserved;
5. prove no duplicate consequential action occurs as a side effect of recovery.

This proves only the tested recovery contract; it does not establish an RTO/RPO/SLA.

### P7 — cost and local-dependency audit

Record:

- unexpected cash charge observed during the controlled pilot: must equal `$0.00`;
- required local components: must equal `0`;
- all production endpoints must be non-local HTTPS/PostgreSQL endpoints;
- no raw credential, token, DSN or provider output may enter the evidence artifact.

## Machine-readable gate

The sanitized run produces `HostedStateIdentityPilotEvidence` and is verified with:

```bash
python scripts/check_hosted_state_identity_pilot.py \
  --evidence <sanitized-evidence.json> \
  --expected-code-sha <exact-git-sha> \
  --expected-bundle-id neon-plus-auth0
```

A zero exit code is necessary, not sufficient, for bundle promotion. The evidence artifact is SHA-256 bound and stores only hashes, counts, booleans and bounded identifiers.

## Promotion rule

Promote the bundle to the full hosted-product campaign only if all of the following are true on the same exact SHA:

- CLI outcome `PILOT_PASS`;
- required local components = 0;
- unexpected cash charge = $0.00;
- organizations >= 2 and users >= 2;
- clean migration PASS;
- pooled TLS Postgres PASS;
- all positive OIDC contract checks PASS;
- every negative identity case is rejected;
- cross-tenant read denied;
- cross-tenant mutation denied;
- SSE reconnect isolation PASS;
- restart persistence PASS.

There is no weighted score and no exception for a failing hard gate.

## After promotion

Only after this pilot passes should the project proceed to:

1. hosted full-product Playwright: login -> API -> provider -> TRACTIAN tool -> evaluation -> PostgreSQL -> SSE -> frontend;
2. hosted concurrency/load measurement;
3. OWASP agentic/adversarial campaign;
4. real TRACTIAN 18/18 transport + semantic certification;
5. governed hosted Execute authorization;
6. human semantic/OCA calibration and MANUAL vs ASSISTED value study.

If the pilot fails because of an Auth0-specific compatibility defect, reopen the preregistered Clerk challenger only after the exact failure is documented; do not add vendor-specific complexity merely to salvage the chosen candidate.
