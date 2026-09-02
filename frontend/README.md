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
