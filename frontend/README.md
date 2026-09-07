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

## Production source contract

The hosted `production-web` service must build from the canonical release branch `release/production-final`, with Railway root directory `frontend` and `Dockerfile.production`. A Railway **Redeploy** reuses the previously captured source snapshot; it is not evidence that the current branch head was fetched. Production release evidence must therefore record the deployed commit SHA and compare it with the intended release head.

The same-origin Caddy boundary proxies the product API/SSE and managed Neon Auth endpoints. The proxy intentionally canonicalizes the upstream Neon Auth `Host` and `X-Forwarded-Host` while preserving the public browser `Origin`, so upstream base-URL resolution does not leak an internal `/academy_tractian` path and origin/CSRF checks remain meaningful.

## Local development

Start the production API on `127.0.0.1:8000`, then:

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api`, `/health`, `/ready` and `/version` to `http://127.0.0.1:8000` by default. Override only the local proxy target with:

```bash
VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev
```

The browser never receives or submits runner-owned identity, user id or seed through the run payload.

## Quality gates

```bash
npm run typecheck
npm test
npm run build
```

The first reducer tests cover canonical sequence ordering, transport replay deduplication, conflicting event-id containment, runtime KPI derivation and real `run_finished` terminal semantics.

## Next frontend increments

1. Run Explorer + historical run selection.
2. Timeline/waterfall timing model.
3. Trace Graph using `@xyflow/react` from actual safe event sequence.
4. Versioned Architecture Explorer and active-path highlighting.
5. Evidence Explorer + Output Lineage.
6. Production Health, Mission Control, Tools & Policy.
7. Eval/Provider Lab and ECharts-backed quantitative analytics.
