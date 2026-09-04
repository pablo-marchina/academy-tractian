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
       - bounded hosted TRACTIAN transport evidence
       - bounded semantic 18-operation campaign proof
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

The migration initializes operational state, browser-safe observability, bounded hosted TRACTIAN
transport evidence and the bounded semantic campaign-evidence store. The serving process uses
`initialize_schema=False`; deployment must run this migration before the new application version is
marked ready. An empty semantic table is valid and means `0/18` semantic proof, while a missing table
makes hosted startup fail closed.

## Container

The root `Dockerfile` builds the production Python package, frozen E2 runtime contract and the
bounded operational scripts required for validation, migration and evidence import. It runs as a
non-root user and starts `academy_tractian.hosted_product`.

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

## TRACTIAN integration evidence

The hosted product exposes two authenticated and deliberately separate evidence surfaces:

- `GET /api/tools/coverage` reports contract/route registration and bounded transport observations;
- `GET /api/tools/campaign` reports the empirical 18-operation transport gate, semantic gate and
  combined end-to-end completion state.

Transport completion for one operation requires all of the following empirical observations:

- canonical route reached;
- a valid request succeeded;
- HTTP-error behavior was observed;
- for consequential actions, an explicit safety block was also observed.

Semantic completion is independent. It requires explicit proof that:

- invalid parameters are rejected;
- the response is normalized correctly;
- agent/evaluator behavior is correct for the operation.

A route definition, registered schema, mock, synthetic fixture or transport success can never
substitute for those semantic dimensions. The API only emits `TRANSPORT_COMPLETE_18_OF_18` or
`SEMANTIC_COMPLETE_18_OF_18` when every canonical operation independently passes the respective
gate. End-to-end completion requires both gates.

The packaged frozen artifact is `research/e2/frozen_tool_integration_evidence.json`. It currently
contains explicit historical route-execution evidence for `get_asset` only. A fresh hosted database
therefore starts with **1/18 aggregate historical evidence but 0/18 hosted-live transport complete
and 0/18 semantic complete**. The remaining operations are never inferred from route existence.

The hosted transport is wrapped by a bounded, thread-safe evidence recorder. It stores only the
canonical operation, method/path template, outcome, optional HTTP status, timestamp and a safe
fingerprint. It deliberately never stores request arguments, query values, headers, request bodies,
response bodies, credentials or DSNs. A real 2xx/3xx response counts as hosted-live success; a real
4xx/5xx response proves the route was observed but does not count as success; transport failure does
not prove route execution. Safety-blocked actions also do not count as route execution by themselves.

Hosted transport evidence is persisted in managed PostgreSQL under the observability schema. Storage
is deliberately bounded by the primary key `(operation, outcome)`: the table keeps first/last
observation, latest safe metadata and an observation count instead of one row per request. With 18
canonical operations and five allowed outcomes this bounds the logical transport-evidence
cardinality to at most **90 operation/outcome aggregates**, independent of user or request volume.

Semantic campaign proof is persisted separately with primary key `(operation, dimension, passed)`.
With 18 operations, three semantic dimensions and PASS/FAIL states, the logical semantic evidence is
bounded to at most **108 aggregates**. PASS and FAIL are intentionally separate rows. A later PASS
cannot erase a previously observed FAIL, and the campaign gate treats any persisted FAIL for a
dimension as dominant until the evidence protocol is explicitly revised.

Persistent transport rows are revalidated against the canonical method/path contract when read.
Semantic rows are revalidated against the canonical operation and strict campaign schema. A
corrupted or unknown operation invalidates the corresponding ledger and makes the public campaign
fail closed instead of inflating coverage.

### Importing semantic campaign proof

The application never manufactures semantic proof from transport telemetry. After a controlled
experiment produces a `tractian-campaign-evidence-v1` document, import only that validated bounded
artifact:

```bash
python scripts/import_tractian_campaign_evidence.py path/to/campaign-evidence.json
```

The importer requires the configured managed PostgreSQL DSNs and a previously migrated schema. It
validates the entire document atomically, persists only bounded proof metadata and emits only counts,
status and safe validation codes. It never prints raw requests, responses, prompts, provider output,
credentials, evidence payloads or fingerprints. Import success means the evidence was accepted; it
does **not** imply that the semantic 18/18 gate passed.

### Transport artifact validation

A controlled transport experiment artifact can be checked without printing raw evidence:

```bash
python scripts/validate_tractian_integration_evidence.py path/to/evidence.json \
  --environment hosted_live
```

The validator is fail-closed: unknown operations, route mismatches, wrong environments, schema
version mismatches, extra fields or malformed HTTP semantics invalidate the whole document and
produce zero trusted records.

The production frontend polls both authenticated evidence surfaces and renders all 18 operations,
including independent transport and semantic completion columns, open/failed dimensions and the
combined gate. If either endpoint/evidence provider is unavailable, the UI does not infer proof.

## Non-claims

This baseline does **not** yet claim:

- a winning cloud vendor;
- a production-selected provider/model;
- a selected/validated external OIDC vendor deployment;
- hosted consequential actions;
- a controlled semantic integration certification for all 18 TRACTIAN operations;
- production SLO/capacity from CI measurements;
- all 18 TRACTIAN routes have hosted-live execution evidence.

Those claims require their respective controlled evidence and promotion gates.
