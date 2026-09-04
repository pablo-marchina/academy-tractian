# Operator Frontend

Production-oriented React frontend for the Academy × TRACTIAN industrial agent.

## Current vertical slice

The Live Run Cockpit consumes only the real safe product API:

```text
POST /api/runs
  -> safe run id
  -> GET /api/stream (fetch SSE)
  -> idempotent event reducer
  -> terminal run snapshot
  -> execution completed
  -> post-runtime evaluation
```

There are no frontend fixtures, fake progress timers or demo-only runtime paths in this slice.

## Hosted backend configuration

The production frontend may run on a different hosted origin from the FastAPI service. Set:

```bash
VITE_API_BASE_URL=https://api.example.com
```

REST requests and SSE streams resolve through this base URL. The value must be an absolute `http` or `https` URL with no embedded credentials, query string or fragment. Omit it to keep same-origin behavior.

A production deployment should use HTTPS and a backend CORS allow-list for the exact frontend origin. Authentication is intentionally not encoded in this URL.

## Browser identity boundary

The core frontend is identity-provider-neutral. The selected hosted OIDC adapter supplies the current
access token through:

```ts
import { setAccessTokenProvider } from "./src/api/auth";

setAccessTokenProvider(async () => currentAccessTokenOrNull);
```

The token provider may be backed by Supabase, Clerk, Auth0 or another hosted OIDC implementation;
the API layer itself does not depend on a vendor SDK. The core does not persist the access token to
local storage or place it in URLs.

The same provider is used by REST and SSE. Live streaming uses `fetch` rather than native
`EventSource` so the browser can send `Authorization: Bearer ...`. The SSE decoder preserves
`after_sequence` reconnect/catch-up semantics, ignores keepalives, rejects malformed/truncated
frames, rejects cross-run data, and checks SSE ids against safe event ids.

When no access-token provider is configured, requests remain unauthenticated. That behavior is kept
only for bounded provider-free CI/development topologies whose backend supplies its own controlled
test identity boundary.

## TRACTIAN integration coverage

The production UI polls the authenticated `GET /api/tools/coverage` surface and renders the canonical
18-operation integration matrix. It keeps these claims visually separate:

- contract registration;
- executable implementation-route presence;
- historical frozen route evidence;
- hosted-live route observation;
- hosted-live success;
- hosted HTTP errors, transport failures, unavailable outcomes and safety blocks.

A fresh hosted environment therefore shows `18/18` contract and implementation while remaining
`0/18` hosted-live until validated runtime evidence exists. An HTTP error can prove that a real route
was reached, but it is never displayed as success. Safety-blocked consequential actions also remain
explicitly different from executed actions.

If the evidence endpoint is unavailable, malformed or fail-closed, the frontend does not infer a
coverage percentage. It displays the evidence state and safe validation codes supplied by the
backend instead. The UI receives no raw requests, tool bodies, response bodies, credentials,
fingerprints or probe payloads.

## Development-only proxy

For isolated development and CI browser acceptance, Vite can still proxy the API. Start the backend on `127.0.0.1:8000`, then:

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api`, `/health`, `/ready` and `/version` to `http://127.0.0.1:8000` by default. Override only the development proxy target with:

```bash
VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev
```

The browser never receives or submits runner-owned identity, user id or evaluation seed through the run payload.

## Quality gates

```bash
npm run typecheck
npm test
npm run build
```

Reducer and API-boundary tests cover canonical sequence ordering, transport replay deduplication, conflicting event-id containment, runtime KPI derivation, real `run_finished` terminal semantics, hosted API URL validation, bearer-token validation, SSE framing/integrity and fail-closed TRACTIAN integration-coverage rendering.

## Product surfaces

The frontend currently includes the connected operator/product areas defined by the project acceptance contract, including live execution, historical inspection, architecture, TRACTIAN operation evidence, evidence/lineage, actions, evaluation/provider views and quantitative production health. New surfaces must consume real safe backend data rather than introduce demo-only state.
