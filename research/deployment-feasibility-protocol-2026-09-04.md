# Hosted backend deployment bake-off protocol

**Status:** preregistered P0 protocol  
**Date:** 2026-09-04  
**Scope:** final hosted-only Academy × TRACTIAN backend  
**Hard constraints:** required local components = 0; required external cash cost = USD 0; multi-user product path; no demo-only deployment

## Decision question

Which hosted compute platform can run the existing production-shaped FastAPI product with the least architecture distortion while preserving the hard USD0 boundary, managed PostgreSQL connectivity, live SSE observability and reproducible deployment/recovery?

Static feasibility and empirical promotion are separate. `PILOT_ADMISSIBLE` is not a host selection.

## Candidate set

The 2026-09-04 systematic screen covers:

- Vercel Hobby Python Functions;
- Google Cloud Run request-based free tier;
- Cloudflare Python Workers Free;
- Oracle OCI Ampere A1 Always Free;
- Railway Free Docker.

Koyeb Free and Render Free are not included in the live pilot frontier because their own current documentation explicitly positions the free offering as unsuitable for production applications. Their rejection remains source evidence, not a performance result.

## D0 — static hard-gate admission

A backend candidate enters a live pilot only if current evidence establishes all of the following:

1. hosted service, with zero required local components;
2. a zero-cost guardrail that does not silently create paid overage;
3. GA runtime boundary;
4. Dockerfile compatibility for the existing image;
5. Python 3.11 compatibility;
6. outbound HTTPS for hosted LLM and TRACTIAN calls;
7. managed PostgreSQL connectivity;
8. streaming HTTP compatible with the current REST/SSE product contract;
9. no durable local disk requirement;
10. provider does not explicitly position the selected free tier as unsuitable for production;
11. migration class is `none` or `minor`.

Unknown required facts fail closed. No weighted score can compensate for a failed hard gate.

The frozen static evidence is bound to `research/deployment-feasibility-source-manifest-2026-09-04.json` and executed by `tests/test_deployment_feasibility_research_snapshot.py`.

## D0 current outcome

Under the preregistered policy, only `oracle-oci-always-free-a1` is `PILOT_ADMISSIBLE`.

This is not a production claim. It means only that Oracle is the current backend candidate worth spending implementation effort on before reopening the alternative set.

The principal static rejection reasons are:

- Vercel backend: Python runtime Beta, no direct Dockerfile execution model for the current backend, major deployment adaptation and unresolved production-suitability evidence on Hobby;
- Cloud Run: technically excellent container fit, but usage beyond free tier is billed and the current project hard constraint requires a zero-cost guardrail;
- Cloudflare Python Workers: Python Worker model differs materially from the current CPython/Docker runtime, current FastAPI path requires Python >=3.13, free CPU limit is 10 ms/request, and current psycopg/PostgreSQL path is not yet proven under Pyodide/Hyperdrive;
- Railway Free: excellent Docker/FastAPI fit, but the Free tier is currently positioned for experimentation while production applications are positioned on Pro.

## D1 — architecture-preservation experiment

For each D0-admitted candidate, build and run the exact production image or a documented architecture-equivalent image. Do not introduce a provider-specific demo server.

Required evidence:

- source SHA;
- image digest;
- target architecture (`linux/arm64` for OCI A1 when used);
- dependency lock hash;
- startup command;
- environment validator PASS;
- `/health` and `/ready` PASS;
- no local persistent-state dependency;
- outbound HTTPS PASS;
- managed PostgreSQL migration/read/write/RLS PASS;
- OIDC/JWKS reachability PASS;
- bounded SSE stream + reconnect PASS;
- clean restart PASS;
- no duplicate consequential action on restart/replay.

A platform that requires changing product semantics, evaluator isolation or action safety fails D1.

## D2 — hosted full-product E2E

Run Playwright against real hosted endpoints, not localhost:

`browser → OIDC login/token → hosted frontend → hosted FastAPI → provider decision → TRACTIAN transport → PostgreSQL → evaluation → SSE → frontend evidence`

Until the real external OIDC/provider/TRACTIAN credentials are available, D2 remains unexecuted rather than replaced by synthetic evidence.

Hard gates:

- tenant leaks = 0;
- unauthorized action executions = 0;
- duplicate action executions = 0;
- forbidden browser data exposures = 0;
- raw secret leakage = 0;
- uncaught 5xx on canonical flows = 0;
- hosted Playwright canonical flows = PASS.

## D3 — quantitative concurrency and recovery

Use the same scenario corpus and request mix across all surviving candidates.

Record at minimum:

- concurrency level;
- successful requests;
- failed requests by reason;
- p50/p95/p99 request latency;
- p50/p95 provider-decision latency;
- SSE reconnect success rate;
- PostgreSQL acquisition/query latency;
- CPU/memory measurements where platform exposes them;
- cold-start latency;
- restart recovery time;
- event/evidence loss count;
- duplicate event/action count.

Capacity claims must be bounded to the measured campaign. No CI benchmark is converted into an unmeasured SLO.

## D4 — operational complexity

Quantify the operational cost of the surviving topology using observable counts rather than subjective labels:

- number of manually provisioned cloud resources;
- number of secret/config values;
- number of deploy commands/actions;
- rollback steps;
- recovery steps;
- required scheduled maintenance tasks;
- infrastructure-specific code lines/files added;
- median deploy duration over repeated deploys;
- failed-deploy rate.

The final decision may use these metrics only after all safety/correctness hard gates pass.

## D5 — host promotion

Promote a backend host only when:

1. static feasibility evidence is current;
2. D1 architecture preservation passes;
3. D2 hosted full-product E2E passes;
4. D3 concurrency/recovery has a bounded acceptable result;
5. D4 operational complexity is measured;
6. hard USD0 remains true for the exact selected configuration;
7. exact deployment SHA/image digest are recorded.

If Oracle fails D1–D4, reopen D0 and either test the next defensible challenger or explicitly renegotiate a hard constraint. Do not silently relax USD0 or cloud-only requirements.

## Frontend hosting is a separate decision

Backend compute does not determine frontend hosting. The React/Vite static frontend will be compared separately between Vercel Hobby static hosting and Cloudflare Pages/static assets (and any credible challenger found in the same systematic screen). Vercel's Python Beta status therefore does not disqualify Vercel as a static frontend host.

## Managed PostgreSQL and identity are separate decisions

The backend host does not select the database or IdP automatically. Supabase and other credible managed PostgreSQL/Auth alternatives must receive their own systematic comparison. The final topology may therefore use, for example, OCI compute with a different managed PostgreSQL/OIDC provider.

## Evidence hygiene

- All external facts are timestamped and source-manifest-bound.
- Unknown facts are not inferred into PASS.
- Free-tier marketing is not treated as production-capacity evidence.
- Platform limitations are kept separate from measured application performance.
- Historical localhost/PostgreSQL evidence remains regression evidence only and cannot satisfy hosted gates.
