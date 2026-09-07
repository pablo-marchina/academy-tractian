# Academy × TRACTIAN

Production-oriented **Industrial Agent + Evaluation** product built around the supplied TRACTIAN API.

**Release 0 is live.** The public product is remotely hosted, authenticated, multi-user/tenant-isolated, backed by Neon PostgreSQL, uses a provisional hosted model provider and real typed TRACTIAN reads, persists safe evidence/evaluation, and streams progress through REST/SSE. Consequential external actions remain disabled.

> Current state changes quickly. Use [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) as the mutable source of truth. Historical/frozen evidence is intentionally not rewritten. Repository source identity, backend runtime identity, frontend identity and supplied-API identity are tracked separately.

## Try the product

**Public URL:** https://production-web-production-c9d1.up.railway.app

Current first-user flow:

```text
sign in
→ Home: ask an equipment question
→ human-readable live progress
→ customer-safe result + response mode
→ inspect supporting evidence when useful
→ Analyses: reopen persisted runs
→ Technical: trace, quality, data, system, actions and studies
```

Start with [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md).

## What is live now

- managed browser authentication with server-owned tenant context;
- Railway-hosted HTTPS frontend/API;
- Neon PostgreSQL durable state + tenant RLS boundary;
- provisional Release 0 provider: Cloudflare `@cf/zai-org/glm-4.7-flash`;
- 18-operation TRACTIAN capability contract: **13 reads + 5 action operations represented as proposal-only capabilities**;
- genuine provider → controller → typed TRACTIAN read → evidence → terminal → evaluation path;
- customer-visible evidence semantics: `complete`, `partial`, `inconclusive`, `conflict`, `unavailable`;
- terminal behavior including ORIENT/FINAL, CLARIFY, ABSTAIN and ESCALATE;
- explicit human-readable asset-label grounding (`R310`, `R420`, `PM-22`, etc.) through authenticated fleet discovery rather than asking users for internal IDs;
- condition-evidence requirements before diagnostic terminal answers;
- data-quality-specific evidence requirements;
- durable history, authenticated SSE/reconnect and safe provenance;
- task-driven UX: **Home / Analyses / Technical**, with result/evidence detail contextual to the selected run;
- no external consequential action execution;
- project cash-cost policy: **USD0 hard gate; no automatic paid fallback**.

The full frozen Provider Tournament v3 still has final state `NO_SELECTION`. The Release 0 provider is intentionally **provisional**, not a final superiority claim.

## Current production identities

| Component | Current hosted identity | Evidence |
|---|---|---|
| backend/runtime | `08866da60245f58f217981b7ae668b10be45cc67` | Railway deployment `062c3cc4-4ac9-48ac-be06-2b4c490cea2a` — SUCCESS |
| frontend UX | `1bc124a8d4dbd029178ff8129b25452129445de7` | Railway deployment `f78e88cd-82c2-4fcf-8f59-a51168f10fad` — SUCCESS |
| supplied TRACTIAN API | `47561c1175181b508139e23e6e39b555c1347d57` | hosted supplied-API deployment |

The original immutable Release 0 acceptance campaign remains anchored to backend `082d6f115c070fdc898df749b4b3018efd9ceeab`. The current backend is a **prospectively hardened descendant**, not a rewrite of that historical evidence.

## Live-hardening highlights

The production validation loop on 2026-09-07 closed several real issues found through user-driven prompts:

```text
#197  continue grounded fleet discovery; stop asking for discoverable IDs
#198  parse nested structured asset/analysis IDs safely
#199  stop redundant get_asset metadata loops
#200  require real condition evidence before diagnostic terminal
#201  define response_mode semantics
#207  harden managed-session resilience
#208  ground explicit asset labels and comparisons
#210  force initial identity grounding and suppress repeated completed data-quality reads
```

Current V13 live checks include:

- data quality: `get_current_user → list_assets_by_company → get_data_quality → get_rms → get_rms(point_id) → FINAL`, `complete`, 0 errors/blocks;
- unavailable comparison: authenticated fleet discovery correctly reports R420 absent rather than inventing a cross-tenant asset or asking for its internal ID;
- causal investigation: `get_current_user → list_assets_by_company → get_spectrum → point-specific spectrum drill-down → FINAL`, `partial`, 0 errors/blocks.

Repeated tool names are not automatically loops: an asset-level read followed by a `point_id`-specific read is legitimate progressive drill-down. Redundancy must be evaluated by operation **and arguments/resource**, not tool name alone.

See [`docs/progress/2026-09-07-release0-live-hardening-v13.md`](docs/progress/2026-09-07-release0-live-hardening-v13.md).

## Documentation map

| I want to… | Start here |
|---|---|
| use the product | [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md) |
| know the exact current state | [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) |
| understand the architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| see what is next | [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) |
| understand Release 0 evidence | [`docs/RELEASE-0-ACCEPTANCE.md`](docs/RELEASE-0-ACCEPTANCE.md) |
| see final-project Definition of Done | [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) |
| map the implementation | [`docs/CODEBASE-MAP.md`](docs/CODEBASE-MAP.md) |
| operate/recover the product | [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md) |
| map work to the TAPI | [`docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`](docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md) |
| prepare the 5-minute technical presentation | [`docs/presentation/README.md`](docs/presentation/README.md) |
| contribute safely | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| report a vulnerability | [`SECURITY.md`](SECURITY.md) |
| browse all documentation | [`docs/README.md`](docs/README.md) |

## Promoted runtime path

```text
authenticated remote user
→ task-driven React/Caddy public origin
→ managed auth + FastAPI
→ server-owned tenant context
→ Neon PostgreSQL ownership/RLS
→ Cloudflare provisional DecisionSource V13
→ AgentController
→ HarnessRunner
→ typed TRACTIAN reads
→ normalized evidence
→ ORIENT | CLARIFY | ABSTAIN | ESCALATE
   + complete | partial | inconclusive | conflict | unavailable
→ deterministic post-runtime evaluator
→ durable safe projection
→ REST/SSE
→ Home / result detail / Analyses / Technical
```

External actions are a separate governed architecture and are **not enabled in Release 0**.

## Repository layout

| Path | Purpose |
|---|---|
| `src/academy_tractian/` | production runtime, APIs, storage, safety, observability and evaluation |
| `frontend/` | React/TypeScript task-driven product and Playwright acceptance |
| `tests/` | backend product/regression/integration tests |
| `research/e2/` | accepted controller/tool/trace/evaluation harness |
| `research/experiments/` | preregistered experiments |
| `research/frozen/` | immutable evidence contracts/inputs |
| `research/results/` | machine-readable results/closures |
| `scripts/` | deterministic validation/reporting/operations wrappers |
| `docs/` | active docs plus preserved historical evidence |
| `.github/workflows/` | required CI, promotion gates and preserved research workflows |

## Core engineering rules

```text
actual project cash cost = USD 0
+ no paid spillover
+ no local production dependency
+ multi-user tenant safety
+ quantitative / eval-driven decisions
+ adaptive only after measured advantage
+ deterministic safety boundaries
+ live safe observability
+ claims no stronger than evidence
```

Do not add orchestration/framework/infrastructure complexity because it is fashionable. LangGraph, multi-agent, RAG/vector DB, MCP, persistent memory, Redis/Kafka and Kubernetes remain challengers only after a measured gap and controlled comparison.

See [`CHANGELOG.md`](CHANGELOG.md) for notable product evolution.