# LIVE-DEMO-READY — execution plan

**Status:** ACTIVE / pre-implementation gate  
**Date:** 2026-09-05  
**Functional baseline:** `d3bed06b132212c85b126f56708863d45f64e03e`  
**Objective:** public browser-only end-to-end demonstration by 2026-09-08.

## Decision question

What is the smallest evidence-honest deployment path that lets a reviewer open one public URL and execute a natural-language industrial request through the real Academy product boundaries without requiring any process on the presenter's machine?

## LIVE-DEMO-READY Definition of Done

A clean browser on another network can:

1. open the public frontend;
2. submit a natural-language industrial request;
3. create a run in the hosted FastAPI product;
4. persist state in remote PostgreSQL;
5. invoke a real USD0 demo model/provider;
6. invoke the delivered TRACTIAN HTTP contract or a clearly labelled hosted synthetic/sandbox equivalent;
7. show model/tool/policy/evidence/terminal/evaluator transitions over genuine REST/SSE;
8. survive browser reconnect through durable cursor catch-up;
9. demonstrate governed action proposal/confirmation without blind replay;
10. switch to the existing deterministic provider-free profile when an external dependency is unavailable.

No localhost, Docker Desktop, local database, local Python process, local Vite process or presenter terminal may be required for the primary demo.

## Hard constraints

- external project cost: USD 0;
- D01/D02 remain consumed and are not replayed;
- `LIVE_DEMO_PROVIDER` is distinct from `PRODUCTION_PROVIDER_SELECTION`; production remains `NO_SELECTION` unless a new preregistered experiment wins;
- deterministic safety, authorization, tenant isolation, custody, idempotency and action-lease boundaries may not be relaxed for the demo;
- no hidden chain-of-thought is exposed;
- real-customer TRACTIAN production must not be implied if the delivered environment is synthetic/sandbox;
- provider-free mode remains a contingency path, not the primary live claim;
- no LangGraph/RAG/multi-agent/memory/framework expansion without a measured live-demo blocker.

## Current baseline

Already accepted in repository-level P0 evidence:

- React/Vite control room;
- FastAPI product API;
- PostgreSQL serving/observability/evaluation topology;
- signed identity + tenant/RLS boundary;
- durable SSE rows + Last-Event-ID replay;
- PostgreSQL LISTEN/NOTIFY wakeup with fallback polling;
- read-only horizontal runtime handoff with lease generation fencing;
- consequential action custody/idempotency + non-transferable action execution lease;
- post-runtime evaluator;
- provider-free full-product Chromium acceptance.

The missing delivery-critical layer is hosted composition plus a real demo decision source and HTTP dependency path.

## Architecture candidates

### A — Railway backend + dedicated remote PostgreSQL + Vercel frontend

Preferred initial path because a Railway project already exists for this repository and the frontend is a static Vite application.

### B — single Railway project for backend + PostgreSQL + static frontend

Challenger only if it materially reduces setup without sacrificing durable database guarantees or browser/SSE behavior.

### C — Cloud Run + Cloud SQL

Not on the critical path under the permanent USD0 constraint unless another hosted option fails a hard gate.

## Implementation sequence

### LIVE-01 — Hosted database

- create/use a dedicated remote PostgreSQL instance;
- initialize the existing product schema, including RLS, runtime work items, action custody/idempotency, action leases, observability/evaluation and realtime rows;
- prove local PostgreSQL is absent from the deployed runtime configuration.

Hard gate: remote backend can initialize/read/write the schema and `/ready` reports all promoted stores ready.

### LIVE-02 — Hosted backend

- reuse the existing Railway project `academy-tractian-hosted-pilot`;
- replace its current preflight-only start command with the hosted product entrypoint;
- configure health check `/ready`;
- set restart policy suitable for an interactive demo;
- configure secrets only through hosted variables;
- expose a public HTTPS domain.

Hard gate: `/ready` returns 200 from a network unrelated to the development machine.

### LIVE-03 — Hosted frontend

- deploy `frontend/` as the real React/Vite control room;
- set the production API/SSE base URL to the public backend;
- guarantee no localhost URL survives the production build;
- configure SPA routing/CORS as needed.

Hard gate: public page loads in an anonymous browser and can query production health.

### LIVE-04 — Real demo provider

Create a new prospective experiment `LIVE-DEMO-PROVIDER-001` rather than modifying D01/D02.

Minimum hard gates before a provider is allowed in `LIVE` mode:

- USD0 for the bounded demo campaign;
- no tool hallucination on the frozen smoke set;
- no invalid tool arguments reaching execution;
- no consequential-action policy bypass;
- no tenant/private-field leakage;
- safe failure on provider timeout/rate limit;
- sufficient quota for rehearsal + presentation.

The winner is recorded only as `LIVE_DEMO_PROVIDER`, not production model selection.

### LIVE-05 — TRACTIAN HTTP path

Priority:

1. delivered/public TRACTIAN sandbox if authorized and reachable;
2. otherwise host the delivered synthetic API as a separate clearly labelled service.

Hard gate: the agent-facing ToolSpec/HarnessRunner path crosses a real HTTP boundary and records sanitized transport evidence.

### LIVE-06 — Natural-language E2E

Run without `scenario:*` tags:

`browser -> hosted frontend -> hosted FastAPI -> real demo model -> controller -> ToolSpec -> HTTP TRACTIAN/synthetic endpoint -> evidence -> model -> terminal -> evaluator -> PostgreSQL -> SSE -> browser`.

Hard gate: one ordinary industrial request reaches a grounded terminal outcome with inspectable trace/evaluation.

### LIVE-07 — Demo fallback

Expose an operator-controlled deployment setting:

- `DEMO_MODE=live`: real demo provider + HTTP TRACTIAN/sandbox path;
- `DEMO_MODE=fallback`: existing deterministic provider-free dependency profile.

Fallback must preserve the same API/frontend and safety surfaces. It must never be labelled as a live provider/customer call.

### LIVE-08 — Reliability rehearsal

Before freeze, run 20 consecutive representative browser/API demo executions.

Hard gates:

- >= 19/20 complete through the UI;
- 0 backend/frontend crashes;
- 0 lost terminal events;
- 0 logical duplicate side effects;
- 0 tenant crossover;
- reconnect catches up without reload;
- fallback switch succeeds after simulated external-provider failure.

Preferred presentation targets, not unconditional SLOs:

- first visible progress < 3 s;
- ordinary terminal result < 20 s.

## Go/no-go immediately before presentation

All must pass: public frontend, backend `/ready`, remote PostgreSQL, live provider smoke, TRACTIAN/sandbox HTTP smoke, one investigation, one safe insufficient-evidence/escalation path, one governed action proposal, SSE reconnect and fallback mode.

If an external dependency fails, switch to fallback; do not repair infrastructure from a terminal during the presentation.

## User/external dependencies

Only request user intervention when a connector cannot perform the operation or a credential/authorization decision is genuinely external. Known possible dependencies:

- authorization to create a dedicated Supabase project and its organization choice if Supabase is used;
- TRACTIAN sandbox/base URL and credential, if not already present in the delivered repository material;
- provider credential/token when no connected zero-cost provider can be provisioned autonomously;
- any platform billing/cost confirmation required before resource creation.

## Freeze rule

Once LIVE-08 passes, stop feature work. Only blocker fixes, rehearsal, exact evidence capture and final documentation synchronization are allowed before delivery.
