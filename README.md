# Academy × TRACTIAN

Production-oriented **Industrial Agent + Evaluation** product built around the supplied TRACTIAN API.

**Release 0 is live and prospectively hardened.** The public product is remotely hosted, authenticated, multi-user/tenant-isolated, backed by Neon PostgreSQL, uses a provisional hosted model provider and real typed TRACTIAN reads, persists safe evidence/evaluation, streams progress through REST/SSE, and now has a governed consequential-action path whose five canonical endpoints have passed the current hosted production smoke.

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
- 18-operation TRACTIAN capability contract: **13 reads + 5 governed action operations**;
- genuine provider → controller → typed TRACTIAN read → evidence → terminal → evaluation path;
- customer-visible evidence semantics: `complete`, `partial`, `inconclusive`, `conflict`, `unavailable`;
- explicit asset-label grounding and condition/data-quality evidence gates;
- durable history, authenticated SSE/reconnect and safe provenance;
- task-driven UX: **Home / Analyses / Technical**, with result/evidence detail contextual to the selected run;
- governed action custody, exact confirmation, server-owned authorization grants, persistent idempotency, lease/fencing and `UNCERTAIN` containment;
- server-owned vendor actor routing by `(company_id, required_permission)` for consequential TRACTIAN calls;
- auditable production write smoke using the same action-routing boundary as production;
- current production smoke result: **5/5 canonical actions returned HTTP 200 with `accepted=true`**;
- project cash-cost policy: **USD0 hard gate; no automatic paid fallback**.

The full frozen Provider Tournament v3 still has final state `NO_SELECTION`. The Release 0 provider is intentionally **provisional**, not a final superiority claim.

## Current production identities

| Component | Current hosted identity | Evidence |
|---|---|---|
| backend/runtime source | `d43644d22df8e3ee5bb5a1532bbea3512c3a7ac0` | Railway deployment `b1259276-0c1b-425b-bf81-ab9a748a5089` — SUCCESS + five-action smoke PASS |
| frontend UX | `1bc124a8d4dbd029178ff8129b25452129445de7` | Railway deployment `f78e88cd-82c2-4fcf-8f59-a51168f10fad` — SUCCESS |
| supplied TRACTIAN API | `47561c1175181b508139e23e6e39b555c1347d57` | hosted supplied-API deployment |

The original immutable Release 0 acceptance campaign remains anchored to backend `082d6f115c070fdc898df749b4b3018efd9ceeab`. The current backend is a **prospectively hardened descendant**, not a rewrite of that historical evidence.

## 2026-09-07 production hardening highlights

The production validation loop closed real issues found through hosted prompts/traces and then advanced into governed writes:

```text
#197  continue grounded fleet discovery; stop asking for discoverable IDs
#198  parse nested structured asset/analysis IDs safely
#199  stop redundant get_asset metadata loops
#200  require real condition evidence before diagnostic terminal
#201  define response_mode semantics
#207  harden managed-session resilience
#208  ground explicit asset labels and comparisons
#209  promote task-driven Home / Analyses / Technical UX
#210  force initial identity grounding and suppress repeated completed data-quality reads
#211  enable governed execution architecture for all five canonical actions
#213  add auditable manual production smoke for all five governed writes
#214  route governed writes through server-owned company+permission TRACTIAN actors
```

### Governed-write progression

PR #211 merged at `1a1e7139...` and enabled the local governed execution path. PR #213 merged at `3545d75...` and added the auditable five-write smoke. Its first fresh production validation correctly failed closed when `update_asset_config` returned HTTP 403, leaving the prior healthy deployment serving.

Inspection of the supplied runtime showed the root cause: the tested company uses different upstream actors for `action_low` and `action_high + escalate`. PR #214 therefore separated the authenticated local product user from the provider-side TRACTIAN actor. The local user remains authoritative for grant resolution, tenant/resource ownership, confirmation, idempotency and observability; only canonical ACTION calls are remapped at the final network boundary through immutable server-owned company+permission bindings.

PR #214:

```text
head          1b63898eda14c04fa5c245c75a9d719ea138816f
merge         d43644d22df8e3ee5bb5a1532bbea3512c3a7ac0
required CI   all triggered final gates SUCCESS
Railway       b1259276-0c1b-425b-bf81-ab9a748a5089 — SUCCESS
```

Hosted smoke v2:

```text
reprocess_analysis           200 accepted=true
request_specialist_analysis  200 accepted=true
update_asset_config          200 accepted=true
request_retraining           200 accepted=true
escalate_case                200 accepted=true
```

The safe smoke also recorded `credentials_recorded=false`, `local_user_ids_recorded=false`, `upstream_user_ids_recorded=false`, `resource_ids_recorded=false` and `response_bodies_recorded=false`.

This proves five-endpoint acceptance for the **current tested release/configuration**. It is not a guarantee that an external service can never fail in the future.

See [`docs/progress/2026-09-07-production-governed-actions-ux-and-validation.md`](docs/progress/2026-09-07-production-governed-actions-ux-and-validation.md).

## Documentation map

| I want to… | Start here |
|---|---|
| use the product | [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md) |
| know the exact current state | [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) |
| understand the architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| operate governed actions | [`docs/GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`](docs/GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md) |
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
→ typed TRACTIAN reads / governed action proposal
→ normalized evidence or private action custody
→ terminal/result or exact operator confirmation
→ deterministic local action authorization / idempotency / lease
→ server-owned company+permission TRACTIAN actor
→ one governed external action attempt
→ explicit upstream acceptance / safe non-success state
→ deterministic post-runtime evaluator
→ durable safe projection
→ REST/SSE
→ Home / result detail / Analyses / Technical
```

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