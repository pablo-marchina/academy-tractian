# Academy × TRACTIAN

Production-oriented **Industrial Agent + Evaluation** product built around the supplied TRACTIAN API.

**Release 0 is live and PR #196 is integrated into `main`.** The public product is remotely hosted, authenticated, multi-user/tenant-isolated, backed by Neon PostgreSQL, uses a live hosted provider and real typed TRACTIAN reads, persists evidence/evaluation, and streams safe progress through REST/SSE. Consequential external actions remain disabled in Release 0.

> Current state changes quickly. Use [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) as the mutable source of truth; historical/frozen evidence is intentionally not rewritten. Repository merge identity and hosted component identities are tracked separately so a merge is never presented as an automatic redeploy.

## Try the product

**Public URL:** https://production-web-production-c9d1.up.railway.app

The current first-user flow is:

```text
sign in
→ Results: ask or choose a guided investigation
→ follow human-readable progress
→ receive FINAL | CLARIFY | ABSTAIN | ESCALATE
→ inspect Evidence when needed
→ inspect Investigation/runtime detail when needed
→ open Engineering for architecture, capabilities and evaluation
```

Start with [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md).

## What is live now

- managed browser authentication and server-owned tenant context;
- Railway-hosted HTTPS frontend/API;
- Neon PostgreSQL durable state + tenant RLS boundary;
- provisional Release 0 provider: Cloudflare `@cf/zai-org/glm-4.7-flash`;
- 18-operation TRACTIAN capability contract: **13 live reads + 5 proposal-only actions**;
- genuine provider → controller → typed TRACTIAN read → evidence → terminal → evaluation path;
- `FINAL`, `CLARIFY`, `ABSTAIN`, `ESCALATE`;
- durable history, authenticated SSE/reconnect and safe provenance;
- four UX depth layers: **Results / Evidence / Investigation / Engineering**;
- no external consequential action execution;
- project cash-cost policy: **USD0 hard gate; no automatic paid fallback**.

The full frozen Provider Tournament v3 still has final state `NO_SELECTION`. The Release 0 provider is intentionally **provisional**, not a final superiority claim.

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
| contribute safely | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| report a vulnerability | [`SECURITY.md`](SECURITY.md) |
| understand documentation rules | [`docs/DOCUMENTATION-GUIDE.md`](docs/DOCUMENTATION-GUIDE.md) |
| browse all documentation | [`docs/README.md`](docs/README.md) |

## Promoted runtime path

```text
authenticated remote user
→ React/Caddy public origin
→ managed auth + FastAPI
→ server-owned tenant context
→ Neon PostgreSQL
→ Cloudflare provisional DecisionSource
→ AgentController
→ HarnessRunner
→ typed TRACTIAN read
→ normalized evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ deterministic post-runtime evaluator
→ durable safe projection
→ REST/SSE
→ Results / Evidence / Investigation / Engineering
```

External actions are a separate governed architecture and are **not enabled in Release 0**.

## Repository layout

| Path | Purpose |
|---|---|
| `src/academy_tractian/` | production runtime, APIs, storage, safety, observability and evaluation |
| `frontend/` | React/TypeScript product and Playwright acceptance |
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

## Current evidence anchors

- promoted backend/runtime SHA: `082d6f115c070fdc898df749b4b3018efd9ceeab`;
- Release 0 hosted acceptance: `hosted-production-release0-agent`, run `34069562818`;
- current hosted frontend UX SHA: `2ca6215ccc07664a9551e8363e438f0930a4d995`;
- current hosted supplied-API SHA: `47561c1175181b508139e23e6e39b555c1347d57`;
- validated PR #196 head: `d7e941b1e0ee380f3cca43816521c88eddc20e9c`, with the required regression surface green before merge;
- PR #196 integration into `main`: merge commit `9fbfbe0c5b5b80dc23941ac2850125834641e32b`.

See [`CHANGELOG.md`](CHANGELOG.md) for notable product evolution.