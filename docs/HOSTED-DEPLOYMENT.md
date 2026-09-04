# Hosted Production Baseline

**Status:** development baseline — not yet a cloud-vendor or provider/model promotion decision.

The hosted product path is designed to run without durable local state on the serving instance.
Historical DuckDB/provider-free paths remain available only for bounded reproduction and regression.

## Runtime topology

```text
hosted browser
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
ACADEMY_RUNTIME_IDENTITY_SECRET
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
project's EDD promotion gates. Final provider/model promotion remains a separate frozen experiment.

## Secret-safe validation

Infrastructure configuration can be validated before a provider is selected:

```bash
python scripts/validate_hosted_environment.py
```

Require agent-serving readiness with:

```bash
python scripts/validate_hosted_environment.py --serving-ready
```

The validator emits only a sanitized summary and never prints DSNs, provider keys, identity secrets
or TRACTIAN bearer tokens.

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

## Frontend

A separately hosted frontend sets:

```text
VITE_API_BASE_URL=https://<hosted-api-origin>
```

REST and SSE paths then resolve to the hosted backend. Build-time API URLs must never contain
credentials.

Browser authentication is a separate P0 workstream. The current project-owned signed bearer remains
the backend baseline; external OIDC/session integration must be selected and tested before an
internet-facing multi-user production claim is made.

## Non-claims

This baseline does **not** yet claim:

- a winning cloud vendor;
- a production-selected provider/model;
- enterprise OIDC/SSO;
- hosted consequential actions;
- production SLO/capacity from CI measurements;
- all 18 TRACTIAN routes have integrated execution evidence.

Those claims require their respective controlled evidence and promotion gates.
