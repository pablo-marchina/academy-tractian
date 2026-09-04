# Identity + tenant production closure — 2026-09-03

## Decision

Promote a concrete authenticated product entrypoint that binds every browser/API request to a cryptographically verified server-side runtime identity before existing authorization and PostgreSQL RLS are evaluated.

The promoted path is:

`Authorization: Bearer <signed envelope>`

→ `SignedBearerRuntimeContextProvider`

→ explicit `organization_id + identity_id + user_id + permissions`

→ product permission checks / run ownership

→ PostgreSQL non-owner scoped connection

→ RLS `organization_id = current_setting('academy.organization_id')`

The generic `create_postgres_action_capable_product_app(..., context_provider=...)` remains available for tests and embedding applications. The production-closure entrypoint is `create_authenticated_postgres_action_capable_product_app`, which does **not** accept an arbitrary context provider.

## Authenticated bearer contract

The bearer format is a small project-owned signed envelope, not OAuth/OIDC/JWT and not claimed to be one:

`academy-runtime-v1.<base64url canonical JSON claims>.<base64url HMAC-SHA256 signature>`

Required signed claims are:

- schema version;
- issuer and audience;
- token ID;
- identity ID;
- user ID;
- organization ID;
- role;
- permissions;
- issued-at and expires-at timestamps.

Verification is fail-closed:

- exactly one Bearer authorization value is required;
- HMAC signature is checked with constant-time comparison before claims are trusted;
- malformed/non-canonical base64url and duplicate JSON keys are rejected;
- issuer and audience must match server configuration;
- future-issued, expired and excessive-lifetime tokens are rejected;
- signing secret must be at least 32 bytes;
- all identity/tenant identifiers are explicit; no browser payload fallback exists;
- the claims schema forbids unknown fields.

`seed` is deliberately absent from the production identity schema. Benchmark/replay seed control cannot be smuggled through the authenticated browser identity path.

## Privilege boundary

Role names do not grant permissions.

The existing permissions continue to be capability strings evaluated by the API. Cross-tenant/global capabilities are additionally protected at the identity-provider configuration boundary:

- `runs:read:any`
- `analytics:read:global`

A valid signed token carrying either capability is still rejected unless that exact privileged capability is enabled in server configuration. Therefore possession of a token signed for a nominal `admin` role is insufficient to create global visibility.

Normal tenant-scoped permissions remain issuer-controlled signed claims and are still checked by each API surface.

## Tenant isolation layers

The production path intentionally keeps two independent controls.

### Application ownership

A submitted run is claimed under the authenticated `organization_id` and `user_id`. Run, evidence, evaluation, lineage, execution and SSE reads use persisted ownership and return 404 when the authenticated principal is outside the allowed scope.

The browser run payload contains only the user request; attempts to submit tenant, user, identity, role, permissions or seed are rejected by the request schema.

### PostgreSQL RLS

The existing operational database already fails startup if the scoped role is:

- superuser;
- `BYPASSRLS`;
- owner of the RLS-protected ownership table.

Tenant reads use a transaction-local `academy.organization_id` and PostgreSQL policy enforcement. The new integration test proves that a scoped connection for tenant B cannot read a known tenant-A run ID even after the request-layer identity check has been bypassed by going directly to SQL.

This is defense in depth: signed identity does not replace RLS, and RLS does not replace request authentication.

## Consequential actions

The existing action path continues to re-check authenticated context at confirmation time, resolve the server-side action principal, verify requester ownership of the origin run, honor the kill switch, and use persistent idempotency custody. The bearer token never contains private action payloads and does not bypass those checks.

This slice does not weaken or replace action authorization with a token role.

## Secret and issuer custody

The HMAC secret is server/issuer configuration and must not be placed in browser code, request bodies, repository files, command-line arguments, logs or observability payloads. The included issuer helper is trusted deployment/test tooling; there is no browser token-mint endpoint.

This repository does not implement human account lifecycle, password login, SSO, token revocation lists or an enterprise identity directory. A deployment that already has OIDC/SSO can replace `SignedBearerRuntimeContextProvider` behind the existing `RuntimeContextProvider` contract without changing run ownership, action authorization or RLS.

For the current deployment, short token TTL and secret rotation are the revocation boundary. The default maximum token lifetime is one hour; callers may configure a lower value.

## Evidence added by this slice

Provider-free tests verify:

- valid signed identity round-trip;
- tenant/user/identity binding;
- missing/malformed/tampered token rejection;
- issuer/audience mismatch rejection;
- expiry/future-issued/excessive-TTL rejection;
- explicit tenant requirement;
- unknown `seed` rejection;
- duplicate permission rejection;
- global privilege server opt-in;
- payload spoof rejection;
- same-user cross-tenant and same-tenant cross-user isolation.

The PostgreSQL integration additionally verifies authenticated tenant ownership plus direct RLS isolation through the scoped role.

## Claim boundary

This slice closes the repository's production **request authentication + tenant isolation path** for the promoted factory. It does not claim enterprise IAM/SSO completeness, external identity-provider availability, or production secret-management infrastructure. Those deployment integrations are separate from the runtime authorization contract and must not be inferred from these tests.
