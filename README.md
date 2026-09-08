# Academy × TRACTIAN

Production-oriented **Industrial Agent + Evaluation** product built around the supplied TRACTIAN API.

**The product is live; the current OpenRouter V14 migration is still under functional acceptance.** The public product is remotely hosted, authenticated, multi-user/tenant-isolated, backed by Neon PostgreSQL, exposes real typed TRACTIAN reads and governed consequential actions, persists safe evidence/evaluation, and streams progress through REST/SSE. The current backend uses a pinned fixed-free OpenRouter model route under a USD0/no-paid-fallback policy, but the latest authenticated B204 campaign fails before the first TRACTIAN read because the provider completion ends with `finish_reason=length`.

> Current state changes quickly. Use [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) as the mutable source of truth. Historical/frozen evidence is intentionally not rewritten. The full 2026-09-08 progress record is [`docs/progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](docs/progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md).

## Public product

**URL:** https://production-web-production-c9d1.up.railway.app

Current user flow:

```text
sign in
→ Home: ask an equipment question
→ live authenticated run
→ model decision
→ typed TRACTIAN evidence when the provider decision succeeds
→ customer-safe terminal + response_mode
→ persisted deterministic evaluation
→ Analyses / Technical drill-down
```

Start with [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md).

## Current hosted identities

| Component | Hosted identity | State |
|---|---|---|
| backend/runtime | `5611687556b3d50c31f20fa85ede794f2500f05c` | Railway deployment `542bf459-353d-432c-b2ff-b862cedf1574` — `SUCCESS` |
| frontend UX | `4364364266c6a88d4affd85cb3a734c774cd42c8` | Railway deployment `8375d735-539c-46af-b299-9ee4aca8e505` — `SUCCESS` |
| supplied TRACTIAN API | `47561c1175181b508139e23e6e39b555c1347d57` | deployment `d5593f37-64ec-442f-a168-d82490e58dbb` — `SUCCESS` |

The functional-closure work is intentionally ahead of production on draft PR #222. Production SHA and PR head must not be described as equivalent until the exact accepted candidate is promoted.

## What is live now

- managed browser authentication with server-owned tenant context;
- Railway-hosted HTTPS frontend/API;
- Neon PostgreSQL durable state + tenant RLS boundary;
- provisional provider: OpenRouter V14, pinned to `nvidia/nemotron-3-super-120b-a12b:free`;
- provider fallbacks disabled and actual project cash-cost policy fixed at **USD0**;
- canonical 18-operation TRACTIAN contract: **13 reads + 5 governed action operations**;
- `AgentController` + `HarnessRunner` remain the only orchestration/tool authority path;
- deterministic schema/resource/policy/evidence boundaries;
- customer-visible evidence semantics: `complete`, `partial`, `inconclusive`, `conflict`, `unavailable`;
- terminal behavior including ORIENT/FINAL, CLARIFY, ABSTAIN and ESCALATE;
- human-readable asset-label grounding through authenticated fleet discovery;
- exact-success duplicate-call suppression while legitimate same-tool/different-argument drill-down remains allowed;
- durable history, authenticated SSE/reconnect and safe provenance;
- task-driven UX: **Home / Analyses / Technical**;
- independent verification/evidence surfaces;
- governed action custody/confirmation/authorization/idempotency/lease architecture;
- no local production dependency.

## Governed actions

A controlled production pre-deploy smoke proved the configured governed transport for all five canonical actions:

```text
reprocess_analysis            PASS / HTTP 200
request_specialist_analysis  PASS / HTTP 200
update_asset_config          PASS / HTTP 200
request_retraining           PASS / HTTP 200
escalate_case                PASS / HTTP 200
```

Production action authority remains server-owned. The browser/model never supplies canonical permissions, tenant/company authority, upstream action identity, confirmation fingerprints, credentials or idempotency material. A 5/5 transport smoke is **not** the same claim as final end-user action/security acceptance; the hosted adversarial SECURITY-V1 action campaign remains open.

See [`docs/GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`](docs/GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md).

## OpenRouter V14 — current functional gate

Exact route:

```text
provider  openrouter
model     nvidia/nemotron-3-super-120b-a12b:free
route     openrouter.chat_completions.v1.fixed_free
fallback  disabled
cost      USD0 hard gate
```

A real managed-session B204 campaign created three production runs:

```text
F01 condition       run_437a59ba893a96e3f902
F02 causal          run_86c832ce46189200b613
F03 data quality    run_f081d5d45b0cf4caf4b3
```

All three proved authentication/run orchestration but failed functional acceptance with `DECISION_SOURCE_FAILURE` and **0 TRACTIAN tool calls**.

A sanitized response-shape probe then localized the failure:

```text
HTTP 200
exact pinned model served
one assistant choice
content present
finish_reason = length
```

V14 correctly rejects truncated output rather than granting tool authority from an incomplete decision. A bounded follow-up experiment was blocked by HTTP 429 on all tested variants, so there is currently **no promoted length fix**.

Current gate:

```text
managed auth                    PASS
exact release identity          PASS
OpenRouter configuration        PASS
OpenRouter valid first decision FAIL
TRACTIAN reads in V14 campaign  NOT REACHED
valid terminal/evaluation       NOT READY
```

Do not work around this by accepting `finish_reason=length`, enabling paid/model fallback, silently changing the served model, bypassing structured output or introducing unbounded retries.

## Promoted architecture

```text
authenticated remote user
→ React/Caddy public origin
→ managed auth + FastAPI
→ server-owned tenant context
→ PostgreSQL ownership/RLS
→ OpenRouter V14 DecisionSource (provisional)
→ custom AgentController
→ HarnessRunner
→ typed TRACTIAN read/action boundary
→ normalized evidence / governed action proposal
→ terminal + response_mode
→ deterministic post-runtime evaluator
→ PostgreSQL safe projection
→ authenticated REST/SSE
→ Home / Analyses / Technical
```

For confirmed consequential actions, the branch is:

```text
proposal
→ deterministic policy
→ private custody
→ explicit confirmation
→ fresh server-owned authorization + kill switch
→ persistent idempotency
→ non-transferable execution lease
→ server-owned upstream TRACTIAN actor
→ bounded remote attempt
→ action evaluation + safe projection
```

## Architecture decisions that remain NO_CHANGE

The current blocker is provider completion/availability, not an orchestration-topology gap. Keep the measured baseline unless a challenger wins:

- custom `AgentController`;
- `HarnessRunner` hard tool boundary;
- FastAPI/Pydantic;
- PostgreSQL + tenant RLS;
- Neon managed auth;
- PostgreSQL durable cursor + LISTEN/NOTIFY wake-up;
- REST/SSE;
- React/TypeScript/TanStack Query/React Flow/ECharts;
- Railway/Neon hosted production.

LangGraph migration, multi-agent, RAG/vector DB, persistent memory, MCP, Redis/Kafka and Kubernetes remain challengers only after a measured material gap.

## Final open gates

Before the strongest final-delivery claim, current open work includes:

- make the authenticated OpenRouter V14 B204 matrix 3/3 with real TRACTIAN calls and valid terminal/evaluation;
- broad live coverage of the 13 read operations;
- full hosted SECURITY-V1, especially now that governed writes exist;
- final load staircase/soak, measured capacity and evidence-derived SLO;
- real restore drill with measured RTO/RPO;
- human semantic calibration;
- MANUAL vs AGENT-ASSISTED operational-value study;
- final provider/tournament conclusion or explicit `NO_SELECTION`;
- GitHub branch protection enforcement;
- exact accepted-production SHA convergence and final immutable evidence freeze.

Use `PASS`, `FAIL`, `NOT REACHED`, `NOT READY`, `PENDING`, `INCONCLUSIVE` and `NO_SELECTION` rather than strengthening a claim beyond evidence.

## Documentation map

| I want to… | Start here |
|---|---|
| use the product | [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md) |
| know the exact current state | [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) |
| see the complete 2026-09-08 episode | [`docs/progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](docs/progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md) |
| understand the architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| see what is next | [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) |
| see final Definition of Done | [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) |
| map implementation ownership | [`docs/CODEBASE-MAP.md`](docs/CODEBASE-MAP.md) |
| operate/recover the product | [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md) |
| operate governed actions | [`docs/GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`](docs/GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md) |
| map work to the TAPI | [`docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`](docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md) |
| understand security | [`docs/SECURITY-MODEL.md`](docs/SECURITY-MODEL.md) |
| browse all documentation | [`docs/README.md`](docs/README.md) |

## Repository layout

| Path | Purpose |
|---|---|
| `src/academy_tractian/` | production runtime, provider adapters, APIs, storage, safety, observability and evaluation |
| `frontend/` | React/TypeScript product and browser acceptance |
| `tests/` | backend/product/regression/integration tests |
| `research/e2/` | accepted controller/tool/trace/evaluation harness |
| `research/experiments/` | preregistered experiments |
| `research/frozen/` | immutable evidence contracts/inputs |
| `research/results/` | machine-readable results/closures |
| `scripts/` | deterministic validation/research/operations wrappers |
| `docs/` | active docs plus preserved historical evidence |
| `.github/workflows/` | CI, promotion, verification and research workflows |

## Core engineering rules

```text
actual project cash cost = USD 0
+ no paid spillover
+ no local production dependency
+ multi-user tenant safety
+ quantitative / eval-driven decisions
+ adaptive only after measured advantage
+ deterministic authority and safety boundaries
+ live safe observability
+ claims no stronger than evidence
```

See [`CHANGELOG.md`](CHANGELOG.md) for notable product evolution.