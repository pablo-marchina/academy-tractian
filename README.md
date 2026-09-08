# Academy × TRACTIAN

Production-oriented **Industrial Agent + Evaluation** product built around the supplied TRACTIAN API.

**Release 0 is live.** The public product is remotely hosted, authenticated, multi-user/tenant-isolated, backed by Neon PostgreSQL, uses a provisional hosted model provider, performs real typed TRACTIAN reads, persists safe evidence/evaluation and streams progress through REST/SSE. Consequential external actions remain disabled.

> Current facts change quickly. Use [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) for overall state and [`docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md) for the provider-selection state. Frozen/historical evidence is intentionally not rewritten.

## Try the product

**Public URL:** https://production-web-production-c9d1.up.railway.app

```text
sign in
→ Home: ask an equipment question
→ live progress
→ customer-safe result + response mode
→ inspect evidence when useful
→ Analyses: persisted runs
→ Technical: trace / quality / data / system / actions / studies
```

Start with [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md).

## What is promoted now

- Railway-hosted HTTPS frontend/API;
- managed browser authentication with server-owned tenant context;
- Neon PostgreSQL durable state + tenant RLS;
- provisional Release 0 model provider;
- 18-operation TRACTIAN contract: **13 reads + 5 proposal-only action operations**;
- provider → controller → typed TRACTIAN read → evidence → terminal → evaluation path;
- customer-visible `complete | partial | inconclusive | conflict | unavailable` evidence semantics;
- explicit authorized-fleet grounding for human asset labels;
- condition/data-quality evidence requirements;
- durable history and authenticated SSE/reconnect;
- task-driven Home / Analyses / Technical UX;
- no consequential external action execution;
- no automatic hidden paid/provider fallback.

## Provider selection — current result

The previous README wording that the final provider tournament was merely “pending” is no longer accurate.

On 2026-09-08:

1. a Cloudflare/Groq GPT-OSS-120B V4 comparison was prepared on the frozen 17×5 population;
2. Cloudflare GPT-OSS-120B was quota-blocked during non-scored preflight;
3. the user explicitly requested proceeding without Cloudflare, so no comparative Cloudflare-vs-Groq result is claimed;
4. Groq `openai/gpt-oss-120b` completed a full **85/85 single-provider qualification**;
5. the result was **`NO_SELECTION`** under the unchanged hard gates.

Groq final qualification metrics:

| Metric | Result |
|---|---:|
| rubric pass | 69/85 = **81.18%** |
| reliability | 70/85 = **82.35%** |
| contract failures | **9** |
| repeat stability | 11/17 = **64.71%** |
| p50 provider latency | **1.154 s** |
| p95 provider latency | **2.904 s** |

This result does **not** authorize a production provider change.

The main failure class is structured decision/terminal stability, not unknown tools or invalid known-tool arguments. Current work therefore investigates output budget, reasoning effort and `strict:true` constrained structured output rather than lowering reliability/contract gates.

See [`docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md).

## Current provider-development sequence

```text
clean isolated 21/21 causal matrix
→ recover exact supplied ActionRequest
→ derive canonical strict:true decision schema
→ small strict eligibility preflights
→ freeze only causally justified challengers
→ unchanged-rubric comparison
→ unchanged hard gates
→ fresh 85/85 for winner only
→ Academy live E2E
→ explicit production promotion decision
```

Candidate concepts, only if justified:

```text
B0 best-effort / medium / 512
B1 best-effort / medium / 2048
C1 strict / medium / 2048
C2 strict / low / 2048
```

No failed scored attempt may be selectively retried/repaired away.

## Why `strict:true` is being investigated

Causal diagnostics have already shown that a provider response can return:

```text
HTTP 200
+ finish_reason=stop
+ valid JSON
+ enough completion budget
+ invalid ProviderDecisionPayload relation
```

Therefore 512 tokens are not the sole cause. The strict challenger will derive closed per-tool/terminal variants from the project's canonical ToolSpecs/OpenAPI rather than weakening the application validator.

The exact supplied `ActionRequest` definition is still a prerequisite for complete strict action variants.

## Experiment-infrastructure note

The Railway account is at its current five-service resource envelope. Provider research has used the disposable `qa-live-prompt-matrix` slot; overlapping unrelated experiment deployments caused some partial causal runs to be discarded rather than stitched together.

A benchmark-shaped Groq admission/rate diagnostic has been frozen because 2048-token requests produced 429 behavior not fully explained by the earlier emitted-token pacing. It had not yet produced a canonical result at the current documentation checkpoint.

Production API/web were not changed by this provider-research episode.

## Documentation map

| I want to… | Start here |
|---|---|
| use the product | [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md) |
| know the exact current state | [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) |
| know the provider decision | [`docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md) |
| see current execution order | [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) |
| understand architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| see final Definition of Done | [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) |
| map implementation | [`docs/CODEBASE-MAP.md`](docs/CODEBASE-MAP.md) |
| operate/promote/rollback | [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md) |
| map to TAPI | [`docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`](docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md) |
| inspect 2026-09-08 chronology | [`docs/progress/2026-09-08-provider-qualification-and-causal-debug.md`](docs/progress/2026-09-08-provider-qualification-and-causal-debug.md) |
| prepare presentation | [`docs/presentation/README.md`](docs/presentation/README.md) |
| browse documentation | [`docs/README.md`](docs/README.md) |

## Repository layout

| Path | Purpose |
|---|---|
| `src/academy_tractian/` | production runtime, APIs, storage, safety, observability, evaluation |
| `frontend/` | task-driven React/TypeScript product |
| `tests/` | backend/product/regression/integration tests |
| `research/e2/` | accepted controller/tool/trace/evaluation harness |
| `research/experiments/` | preregistered/frozen experiment definitions |
| `research/frozen/` | immutable evidence contracts/inputs |
| `research/results/` | machine-readable results/closures |
| `scripts/verification/` | deterministic provider/product verification runners |
| `docs/` | active docs + preserved history |

## Core engineering rules

```text
no hidden paid/provider fallback
+ no local production dependency
+ multi-user tenant safety
+ quantitative / eval-driven decisions
+ adaptive only after measured advantage
+ deterministic safety/authority boundaries
+ live safe observability
+ negative experiment results remain evidence
+ claims no stronger than proof
```

Do not add LangGraph, multi-agent, RAG/vector DB, MCP, persistent memory, Redis/Kafka or Kubernetes because they are fashionable. They remain challengers only after a measured gap and controlled win.

See [`CHANGELOG.md`](CHANGELOG.md) for notable evolution.
