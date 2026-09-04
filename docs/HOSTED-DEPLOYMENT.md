# Hosted Production Baseline

**Status:** active hosted-only P0 candidate — not yet a cloud-vendor, identity-vendor or provider/model promotion decision.

The final product must require **zero local runtime components**. Historical DuckDB, signed-HMAC and provider-free paths remain only for bounded regression/reproduction where explicitly documented; they must not become required final-product dependencies.

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

The hosted configuration supports two explicit identity backends without changing the agent/runtime contract.

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

Only explicitly configured asymmetric JWT algorithms are accepted. The application validates issuer, audience, signature, expiry, issued-at time, optional authorized party and mandatory configured claims. External permission claims do not automatically become application privileges; they are intersected with application-owned allow-lists.

A regression discovered during the hosted pilot showed that a configured Auth0 role claim could be absent while the token was still accepted. The provider-neutral boundary now supports required claims and rejects the token fail-closed when those claims are missing.

### Signed bearer — bounded regression/backend baseline

```text
ACADEMY_IDENTITY_BACKEND=signed_bearer
ACADEMY_RUNTIME_IDENTITY_SECRET=<at-least-32-bytes>
ACADEMY_RUNTIME_IDENTITY_ISSUER=...
ACADEMY_RUNTIME_IDENTITY_AUDIENCE=...
```

This exists for reproducible historical/backend regression only. It is not the internet-facing final IAM target.

## Serving-ready configuration

The serving entrypoint additionally requires:

```text
ACADEMY_PROVIDER=openai|google|groq
ACADEMY_MODEL=<registered-model-id>
OPENAI_API_KEY=...        # when openai is selected
GOOGLE_API_KEY=...        # when google is selected
GROQ_API_KEY=...          # when groq is selected
ACADEMY_TRACTIAN_BASE_URL=https://...
ACADEMY_TRACTIAN_BEARER_TOKEN=...   # only if required by the supplied API
```

The current hosted candidate registry contains an OpenAI control candidate, Google Gemini 3.7 Flash, Google Gemini 3.8 Flash and Groq GPT-OSS-120B. Deployment configuration is **not** model-selection evidence; the final provider/model must still pass the preregistered EDD promotion decision.

## Secret-safe validation

Infrastructure configuration can be validated before a provider is selected:

```bash
python scripts/validate_hosted_environment.py
```

Require full agent-serving readiness with:

```bash
python scripts/validate_hosted_environment.py --serving-ready
```

The validator emits only a sanitized summary and never prints DSNs, provider keys, signing secrets, JWKS contents or TRACTIAN bearer tokens.

## Hosted deployment evidence chain

Provider documentation is only a static feasibility admission. It does not prove what source or runtime actually executed. Hosted evidence therefore follows this mandatory sequence:

```text
static provider feasibility
→ live source/build/runtime attestation
→ hosted PostgreSQL preflight
→ explicit migration
→ RLS/isolation verification
→ readiness
→ hosted product E2E
```

The live attestation gate is:

```bash
python scripts/check_live_deployment_attestation.py <evidence.json>
```

The default production policy requires:

- exact expected source revision;
- exact expected branch;
- approved build contract (`root-dockerfile`);
- approved Python runtime (`3.11`).

The attestation artifact is hash-bound. A mismatch is a hard, non-compensatory failure and blocks database mutation or readiness claims.

## Hosted PostgreSQL preflight

Only after live deployment attestation passes, execute the read-only application-connection preflight:

```bash
python scripts/check_hosted_postgres_preflight.py
```

This is a hard gate for the hosted production candidate. It rejects local endpoints before any network I/O and checks the real application sessions for:

- distinct internal/scoped database identities;
- required PostgreSQL major version;
- TLS on both connections;
- same intended database;
- scoped role not superuser;
- scoped role `NOBYPASSRLS`.

Its output is bounded and secret-safe; it uses fingerprints/security properties instead of serializing DSNs or passwords.

## Database migration

Schema creation is explicit and separate from serving:

```bash
python scripts/migrate_hosted_postgres.py
```

The migration initializes operational state, browser-safe observability, bounded hosted TRACTIAN transport evidence and the bounded semantic campaign-evidence store. The serving process uses `initialize_schema=False`; deployment must run this migration before the application version is marked ready.

An empty semantic table is valid and means `0/18` semantic proof. A missing required table makes hosted startup fail closed.

## Managed PostgreSQL pilot

An isolated Neon pilot is currently used to produce live managed-PostgreSQL evidence. It is not a vendor promotion decision.

Observed pilot facts include:

- PostgreSQL 18 in AWS São Paulo;
- separate internal and scoped credentials;
- TLS-required application DSNs;
- Neon API-native role creation produced a role incompatible with the project's RLS hard gate because it had `BYPASSRLS`;
- that role path was rejected;
- the scoped application role was created explicitly with `NOSUPERUSER`, `NOBYPASSRLS`, no `CREATEROLE/CREATEDB` and `NOINHERIT`;
- the incompatible experimental role was removed.

Sanitized evidence is documented in `research/neon-hosted-pilot-live-baseline-2026-09-04.md`.

The database was intentionally not migrated after the connected Railway deployment failed live source/build attestation. This preserves experimental integrity: wrong code cannot create schema and then be counted as evidence for the intended SHA.

## Railway deployment challenger result

An isolated Railway project named `academy-tractian-hosted-pilot` was used only as a hosted executor challenger. Secrets were injected through Railway environment variables rather than GitHub or repository files.

The connected Git-source deployment was requested against the PR branch, but observed deployment metadata/logs showed:

```text
expected branch             feat/cloud-production-baseline
observed branch             main
observed source revision    acb786e3a4cf45500fd68741e1ecedba1f624e5d
expected build              root-dockerfile
observed build              railpack
expected Python             3.11
observed Python             3.13.15
outcome                     LIVE_ATTESTATION_FAIL
```

The older source revision did not contain `scripts/check_hosted_postgres_preflight.py`, so the process failed before a valid preflight could run.

The evidence is stored in:

`research/results/railway-live-deployment-attestation-2026-09-04.json`.

Current decision:

- Railway is **not qualified through the connected Git-source path**;
- this deployment does not count as PostgreSQL, RLS, readiness or full-product evidence;
- no cloud-vendor winner is selected;
- Railway can be reconsidered only if a future path independently proves immutable source/build provenance, for example an approved OCI image pinned by digest.

## Container

The root `Dockerfile` builds the production Python package, frozen E2 runtime contract and bounded operational scripts required for validation, migration and evidence import. It runs as a non-root user and starts `academy_tractian.hosted_product`.

The container healthcheck queries `/ready`. A platform should use `/health` for liveness and `/ready` for dependency/readiness gating.

## Consequential actions

Hosted product actions are intentionally fail-closed in the current candidate. The hosted entrypoint supplies an authorization resolver with zero action permissions and starts the action kill switch disabled.

This is temporary qualification state, not the final functional target. The final TAPI-compliant production path must support governed Execute after independent authorization/isolation evidence passes.

The target action path is:

```text
agent proposal
→ deterministic schema/scope/permission validation
→ tenant/resource authorization
→ private PostgreSQL custody
→ explicit authenticated confirmation
→ authorization + kill-switch revalidation
→ atomic idempotency claim
→ exact action execution
→ action trace/evaluation
→ safe frontend projection
```

Controlled campaign approvals never grant product-runtime authorization.

## Frontend authentication and SSE

A separately hosted frontend sets:

```text
VITE_API_BASE_URL=https://<hosted-api-origin>
```

The frontend exposes a provider-neutral in-memory `AccessTokenProvider`. The selected hosted OIDC adapter supplies current access tokens through that boundary; the core does not require a vendor SDK and does not place tokens in URLs.

REST and live SSE use `fetch` with `Authorization: Bearer ...`. Native `EventSource` is not used because it cannot set the required custom Authorization header. Streaming preserves `after_sequence` reconnect/catch-up semantics and validates persisted SSE ids against safe event payloads.

The auth core does not persist tokens to local storage by itself.

## TRACTIAN integration evidence

The hosted product exposes two authenticated and separate evidence surfaces:

- `GET /api/tools/coverage` — contract/route registration plus bounded transport observations;
- `GET /api/tools/campaign` — empirical transport, semantic and combined 18-operation gates.

Transport completion for one operation requires all of:

- canonical route reached;
- valid request succeeded;
- HTTP-error behavior observed;
- for consequential actions, explicit safety block observed.

Semantic completion independently requires:

- invalid parameters rejected before transport;
- live response normalized correctly;
- agent/evaluator behavior correct for that operation and observed response.

Route definitions, registered schemas, mocks, synthetic fixtures and transport success cannot substitute for semantic proof. End-to-end completion requires both transport and semantic `18/18`.

The packaged historical artifact `research/e2/frozen_tool_integration_evidence.json` remains historical and does not establish hosted-live 18/18 coverage.

### Live transport + semantic certification

```bash
python scripts/run_tractian_transport_campaign.py path/to/campaign.json \
  --persist \
  --persist-semantic \
  --require-gate runner
```

The semantic certifier reuses the already-observed live response in process memory and replays it through the frozen `HarnessRunner`, `AgentController` and default `EvaluationSuite`; it does not issue a duplicate TRACTIAN request.

For consequential operations, valid live mutation requires all of:

1. `action_execution_approved=true` in the fixture;
2. non-empty `action_approval_ref`;
3. invocation-level `--allow-actions`.

An action HTTP-error probe is a second mutation and additionally requires `action_error_probe_approved=true`.

Release gate scopes:

- `runner` — no unexpected campaign outcomes; not an 18/18 claim;
- `transport` — empirical transport 18/18;
- `semantic` — semantic 18/18;
- `end_to_end` — both transport and semantic 18/18.

The final integration claim requires `end_to_end`.

## Frontend truth provenance

Final product surfaces should distinguish at minimum:

```text
LIVE_PRODUCTION
LIVE_EXPERIMENT
HISTORICAL_EVIDENCE
SYNTHETIC_TEST
NOT_MEASURED
```

The UI must not infer completion from missing/unavailable evidence.

## Hard gate state before new freeze

The current freeze remains reopened until at least the following hosted gates close:

```text
HOSTED_EXACT_SOURCE_ATTESTATION
HOSTED_APPROVED_BUILD_RUNTIME
HOSTED_POSTGRES_PREFLIGHT
HOSTED_POSTGRES_MIGRATION
HOSTED_POSTGRES_RLS_ISOLATION
HOSTED_OIDC_LIVE
HOSTED_PROVIDER_SELECTION
TRACTIAN_TRANSPORT_18_OF_18
TRACTIAN_SEMANTIC_18_OF_18
HOSTED_ACTION_AUTHORIZATION
HOSTED_FULL_PRODUCT_PLAYWRIGHT
HOSTED_SECURITY_CAMPAIGN
HUMAN_SEMANTIC_CALIBRATION
BRANCH_PROTECTION_ENFORCEMENT
```

## Non-claims

This candidate does **not** yet claim:

- a winning cloud vendor;
- Railway qualification through the currently connected Git-source path;
- a production-selected provider/model;
- a selected/live-validated external OIDC deployment;
- hosted consequential-action authorization;
- hosted transport or semantic 18/18 completion;
- hosted full-product E2E completion;
- production SLO/capacity from CI measurements;
- human semantic calibration/business-value completion;
- hard freeze or unconditional production readiness.
