# Hosted Production Baseline

**Status:** development baseline — not yet a cloud-vendor or provider/model promotion decision.

The hosted product path is designed to run without durable local state on the serving instance.
Historical DuckDB/provider-free paths remain available only for bounded reproduction and regression.

## Runtime topology

```text
hosted browser
  -> hosted OIDC identity provider
  -> bearer-authenticated REST + fetch-stream SSE
  -> hosted FastAPI container
  -> managed PostgreSQL
       - operational ownership/execution/action custody/idempotency
       - browser-safe observability/evaluation read model
  -> selected hosted provider/model
  -> supplied hosted TRACTIAN HTTPS API
```

The hosted entrypoint is:

```bash
python -m academy_tractian.hosted_product
```

It fails closed unless serving-required configuration is present.

## Required infrastructure configuration

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
ACADEMY_RUNTIME_IDENTITY_ISSUER
ACADEMY_RUNTIME_IDENTITY_AUDIENCE
ACADEMY_CORS_ORIGINS
```

The CORS origin list must contain exact HTTPS origins only.

Optional schema/runtime tuning:

```text
ACADEMY_POSTGRES_SCHEMA=academy_operational
ACADEMY_OBSERVABILITY_SCHEMA=academy_observability
ACADEMY_MAX_WORKERS=4
ACADEMY_HEARTBEAT_INTERVAL_MS=1000
```

## Identity backend

The hosted configuration supports two explicit identity backends without changing the agent/runtime
contract.

### OIDC/JWKS — hosted browser target

```text
ACADEMY_IDENTITY_BACKEND=oidc
ACADEMY_RUNTIME_IDENTITY_ISSUER=https://<issuer>
ACADEMY_RUNTIME_IDENTITY_AUDIENCE=<api-audience>
ACADEMY_OIDC_JWKS_URL=https://<issuer-or-jwks-host>/.well-known/jwks.json
ACADEMY_OIDC_ALGORITHMS=RS256
ACADEMY_OIDC_AUTHORIZED_PARTIES=<optional-azp-allow-list>
```

Optional claim names default to:

```text
ACADEMY_OIDC_ORGANIZATION_CLAIM=organization_id
ACADEMY_OIDC_ROLE_CLAIM=role
ACADEMY_OIDC_PERMISSIONS_CLAIM=permissions
ACADEMY_OIDC_IDENTITY_CLAIM=sid
```

Only explicitly configured asymmetric JWT algorithms are accepted. The application validates
issuer, audience, signature, expiry, issued-at time, optional authorized party and the mandatory
organization claim. External permission claims do not automatically become application privileges;
the hosted entrypoint currently starts with an empty claim-permission allow-list.

### Signed bearer — bounded regression/back-end baseline

```text
ACADEMY_IDENTITY_BACKEND=signed_bearer
ACADEMY_RUNTIME_IDENTITY_SECRET=<at-least-32-bytes>
ACADEMY_RUNTIME_IDENTITY_ISSUER=...
ACADEMY_RUNTIME_IDENTITY_AUDIENCE=...
```

This preserves reproducible regression paths. It is not the preferred internet-facing browser IAM
claim once a hosted OIDC provider is provisioned.

## Serving-ready configuration

The agent-serving entrypoint additionally requires:

```text
ACADEMY_PROVIDER=openai|google
OPENAI_API_KEY=...        # when openai is selected
GOOGLE_API_KEY=...        # when google is selected
ACADEMY_TRACTIAN_BASE_URL=https://...
ACADEMY_TRACTIAN_BEARER_TOKEN=...   # only if required by the supplied API
```

`ACADEMY_PROVIDER` is an explicit deployment input, not proof that the provider/model has won the
project's EDD promotion gates. Final provider/model promotion remains a separate controlled
experiment.

## Secret-safe validation

Infrastructure configuration can be validated before a provider is selected:

```bash
python scripts/validate_hosted_environment.py
```

Require agent-serving readiness with:

```bash
python scripts/validate_hosted_environment.py --serving-ready
```

The validator emits only a sanitized summary and never prints DSNs, provider keys, signing secrets,
JWKS contents or TRACTIAN bearer tokens.

## Database migration

Schema creation is explicit and separate from serving:

```bash
python scripts/migrate_hosted_postgres.py
```

The serving process uses `initialize_schema=False`; deployment must run the migration before the new
application version is marked ready.

## Container

The root `Dockerfile` builds only the production Python package and its frozen E2 runtime contract.
It runs as a non-root user and starts `academy_tractian.hosted_product`.

The container healthcheck queries `/ready`. A platform should also use `/health` for liveness and
`/ready` for dependency/readiness gating.

## Consequential actions

Hosted actions are intentionally fail-closed in this baseline. The hosted entrypoint supplies an
authorization resolver with zero action permissions and starts the action kill switch disabled.

This is not a permanent product decision. It prevents a cloud deployment from gaining mutation
capability before hosted resource/company authorization has independent integration evidence.

## Frontend authentication and SSE

A separately hosted frontend sets:

```text
VITE_API_BASE_URL=https://<hosted-api-origin>
```

The frontend exposes a provider-neutral in-memory `AccessTokenProvider` boundary. A selected hosted
OIDC client supplies its current access token through `setAccessTokenProvider(...)`; the core does
not require a Supabase/Clerk/Auth0-specific SDK and does not place tokens in URLs.

Both REST and live SSE use `fetch` and attach the same `Authorization: Bearer ...` header. Native
`EventSource` is deliberately not used because it cannot set the required custom Authorization
header. The streaming transport preserves `after_sequence` reconnect/catch-up semantics and checks
that persisted SSE `id` values match the safe event payload.

Build-time API URLs must never contain credentials. The frontend auth core does not persist access
tokens to local storage by itself; token lifecycle remains owned by the selected hosted identity
adapter.

## Non-claims

This baseline does **not** yet claim:

- a winning cloud vendor;
- a production-selected provider/model;
- a selected/validated external OIDC vendor deployment;
- hosted consequential actions;
- production SLO/capacity from CI measurements;
- all 18 TRACTIAN routes have integrated execution evidence.

Those claims require their respective controlled evidence and promotion gates.
