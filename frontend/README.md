# Operator Frontend

Production-oriented React frontend for the Academy × TRACTIAN industrial agent.

## Current vertical slice

The Live Run Cockpit consumes only the real safe product API:

```text
POST /api/runs
  -> safe run id
  -> GET /api/stream (SSE)
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

A production deployment should use HTTPS and a backend CORS allow-list for the exact frontend origin. Authentication is intentionally not encoded in this URL; bearer/session credentials must come from the selected identity integration rather than build-time URL secrets.

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

Reducer and API-boundary tests cover canonical sequence ordering, transport replay deduplication, conflicting event-id containment, runtime KPI derivation, real `run_finished` terminal semantics, and hosted API URL validation.

## Product surfaces

The frontend currently includes the connected operator/product areas defined by the project acceptance contract, including live execution, historical inspection, architecture, evidence/lineage, actions, evaluation/provider views and quantitative production health. New surfaces must consume real safe backend data rather than introduce demo-only state.
