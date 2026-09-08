# Academy × TRACTIAN — Active Project Status

**Status:** hosted production active / OpenRouter V14 functional acceptance **FAILING**  
**Last verified:** 2026-09-08 BRT  
**Production backend/runtime SHA:** `5611687556b3d50c31f20fa85ede794f2500f05c`  
**Backend Railway deployment:** `542bf459-353d-432c-b2ff-b862cedf1574` — `SUCCESS`  
**Hosted frontend UX SHA:** `4364364266c6a88d4affd85cb3a734c774cd42c8`  
**Frontend Railway deployment:** `8375d735-539c-46af-b299-9ee4aca8e505` — `SUCCESS`  
**Hosted supplied-API SHA:** `47561c1175181b508139e23e6e39b555c1347d57`  
**Supplied-API deployment:** `d5593f37-64ec-442f-a168-d82490e58dbb` — `SUCCESS`  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Production branch:** `release/production-final`  
**Functional-closure PR:** #222 (`fix/functional-acceptance-closure`, draft)

This file is the mutable source of truth for **current execution state**. Frozen/history files remain immutable. See the complete dated record: [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md).

## 1. Current objective

The project has moved beyond the earlier read-only V13 release. Governed actions and independent verification have been promoted, and production provider composition is now OpenRouter V14. The immediate blocking objective is:

> **close real authenticated OpenRouter V14 functional acceptance without weakening model pinning, structured-output integrity, tenant/action safety, or the USD0/no-paid-fallback boundary.**

Current target path:

```text
authenticated remote user
→ POST /api/runs
→ server-owned tenant/runtime context
→ OpenRouter V14 typed decision
→ AgentController
→ HarnessRunner
→ real TRACTIAN tools
→ normalized evidence / governed action proposal
→ terminal + response_mode
→ deterministic evaluation
→ PostgreSQL safe projection
→ REST/SSE
→ Home / Analyses / Technical
```

The current B204 campaign reaches the OpenRouter decision call but fails there before the first TRACTIAN tool.

## 2. Current hosted component ledger

| Component | State | Identity / evidence |
|---|---|---|
| public HTTPS product | **PASS** | Railway public origin |
| backend/runtime | **PASS deployment / V14 functional gate FAIL** | `5611687556...`, deployment `542bf459...` |
| frontend UX | **PASS hosted** | `436436426...`, deployment `8375d735...` |
| supplied TRACTIAN API | **PASS hosted** | `47561c117...`, deployment `d5593f37...` |
| Neon PostgreSQL | **PASS serving scope** | durable state + tenant RLS |
| managed browser auth | **PASS tested scope** | real managed login/session/protected run creation |
| provider configuration | **PASS provisional** | OpenRouter fixed-free V14 |
| provider functional first decision | **FAIL** | `finish_reason=length` |
| typed TRACTIAN reads under V14 B204 matrix | **NOT REACHED** | provider failed before first tool |
| governed action transport | **PASS controlled smoke** | 5/5 canonical actions HTTP 200 |
| final end-user action/security acceptance | **PENDING** | SECURITY-V1/adversarial campaign open |
| actual project cash cost | **USD0 hard gate** | paid fallback disabled |
| local/mock production dependency | **ZERO** | remote serving only |

## 3. Material progress since V13

### Governed writes

Production descendant includes server-owned upstream TRACTIAN action actors. The controlled production pre-deploy smoke proved all five canonical governed transports:

```text
reprocess_analysis            accepted / HTTP 200
request_specialist_analysis  accepted / HTTP 200
update_asset_config          accepted / HTTP 200
request_retraining           accepted / HTTP 200
escalate_case                accepted / HTTP 200
```

The smoke reported `GOVERNED_CONFIRMATION`, five executable actions and no credential/resource/user/response-body recording.

### Verification V1

The production sequence also promoted claim-bounded independent verification, independent functional/evidence oracles, evaluator meta-evaluation, release/supply-chain checks and truthful Verification UI surfaces.

### Read access with action grants enabled

Ordinary authenticated users retain genuine read access even if they have no consequential-action grant. The zero-action fallback authorizes no write; confirmation still revalidates strict server-owned tenant-aware action authority.

### Exact duplicate non-progress invariant

An exact successful read cannot execute twice in the same run after its evidence has been accepted. Same tool name with different normalized arguments/resource remains eligible for progressive drill-down.

## 4. OpenRouter V14 provider state

Exact current provider contract:

```text
provider_id  = openrouter
model_id     = nvidia/nemotron-3-super-120b-a12b:free
route_id     = openrouter.chat_completions.v1.fixed_free
fallbacks    = false
cost_policy  = usd0-hard-gate
```

V14 keeps V13 grounding/response semantics and changes the provider adapter. It requires:

- exact free-model pin;
- strict JSON Schema output;
- exactly one assistant choice;
- exact model identity when returned;
- `finish_reason=stop`;
- no provider-side tool/function calls;
- nonempty structured decision content;
- no automatic retry/output repair/paid fallback.

These are safety/provenance gates, not optional parsing preferences.

## 5. Authenticated B204 functional matrix — current blocker

Real managed-session cases:

| Case | Run | Result |
|---|---|---|
| F01 explicit asset condition | `run_437a59ba893a96e3f902` | **FAIL** |
| F02 causal investigation | `run_86c832ce46189200b613` | **FAIL** |
| F03 data quality | `run_f081d5d45b0cf4caf4b3` | **FAIL** |

Common observed chain:

```text
managed login/session        PASS
release identity             PASS
POST /api/runs               PASS / 202
runtime worker               PASS
OpenRouter first decision    FAIL
TRACTIAN tool calls          0
terminal reason              DECISION_SOURCE_FAILURE
functional acceptance        FAIL 0/3
```

This isolates the immediate failure before the TRACTIAN boundary.

## 6. Root-cause evidence

A sanitized response-shape probe reproduced the first provider request and observed:

```text
http_status       200
served_model      nvidia/nemotron-3-super-120b-a12b:free
choices_count     1
message_role      assistant
content_present   true
finish_reason     length
```

Therefore the current root cause is a truncated provider completion, which V14 correctly rejects rather than trusting incomplete structured output.

A bounded comparison of 1024/default reasoning, 1024/minimized reasoning and 4096/default reasoning was subsequently blocked by HTTP 429 for all variants. The fix comparison is currently **INCONCLUSIVE**; no variant has been promoted.

A safe OpenRouter key-tier/rate-limit probe is the next diagnostic. At the last verification, the new probe code existed on the closure branch but had not yet produced a later QA deployment result.

## 7. Action authority model

When actions are configured:

```text
model proposes exact action
→ deterministic schema/resource/permission checks
→ private server custody
→ explicit opaque-ID confirmation
→ fresh user/tenant grant resolution + kill switch
→ persistent idempotency claim
→ non-transferable execution lease/fencing
→ server-owned upstream TRACTIAN actor
→ one bounded external attempt
→ ACCEPTED | NOT_ACCEPTED | BLOCKED | UNCERTAIN
→ evaluation + safe observability
```

The browser/model never supplies canonical permissions, tenant/company authority, upstream action identity, credentials, confirmation fingerprint or idempotency material.

The 5/5 smoke is evidence for the configured transport path, not a completed final adversarial/end-user action campaign.

## 8. Current UX

Hosted frontend remains task-driven:

- **Home** — natural-language question and run progress;
- **Result** — conclusion, response mode, next step and supporting evidence;
- **Analyses** — persisted run history;
- **Technical** — trace, evidence, evaluation, data, system, actions, studies and verification depth.

Frontend is a projection of server-owned truth, never policy/tenant authority.

## 9. Current architecture decision

No major architecture migration is justified by the observed blocker.

**Promoted baseline remains:** FastAPI/Pydantic + managed auth + PostgreSQL/RLS + custom `AgentController` + `HarnessRunner` + typed TRACTIAN transport + deterministic evaluation + REST/SSE + PostgreSQL durable cursor/LISTEN-NOTIFY wake-up + React/TanStack Query/React Flow/ECharts + Railway/Neon.

`NO_CHANGE` absent a measured challenger win: LangGraph, multi-agent, RAG/vector DB, persistent memory, MCP, Redis/Kafka/Kubernetes and adaptive runtime routing/stopping.

## 10. Current final-gate ledger

| Gate | State |
|---|---|
| remote hosted product | **PASS** |
| managed multi-user auth | **PASS tested scope** |
| tenant isolation/RLS | **PASS tested scope** |
| no local production dependencies | **PASS** |
| USD0 / no paid spillover | **PASS policy** |
| structural evaluation/verification | **PASS tested scope** |
| governed action transport | **PASS 5/5 controlled smoke** |
| authenticated OpenRouter V14 E2E | **FAIL** |
| B204 V14 tools/terminal/eval | **NOT REACHED / NOT READY** |
| broad 13-read live coverage | **PENDING** |
| full action/security adversarial campaign | **PENDING** |
| remote load staircase/soak | **PENDING** |
| measured production capacity | **UNKNOWN** |
| evidence-derived SLO | **PENDING** |
| real restore drill | **PENDING** |
| measured RTO/RPO | **UNKNOWN** |
| human semantic calibration | **PENDING** |
| MANUAL vs AGENT-ASSISTED value study | **PENDING** |
| final provider selection | **NO_SELECTION / PENDING eligible evidence** |
| main branch protection | **FAIL / external control pending** |
| production SHA == accepted final candidate | **NO** |
| final evidence bundle | **PENDING** |

## 11. Git/release governance

PR #222 remains draft by design and should not merge until hosted functional acceptance is green. Current closure work is ahead of the production release and includes diagnostics, provider-tournament eligibility, duplicate-call invariants, action/controller/runtime hardening and regressions.

Latest observed GitHub metadata still reports:

```text
main.protected = false
required status-check enforcement = off
```

The repository has a stable required CI gate, but CI existence is not branch-protection enforcement.

## 12. Immediate priority order

```text
P0 safely measure OpenRouter rate-limit/key-tier eligibility
→ reproduce `finish_reason=length` under eligible quota
→ bounded fix comparison without weakening safety/cost/provenance
→ regression on winning behavior only if evidence supports it
→ required CI on exact candidate SHA
→ exact-SHA production deploy
→ authenticated B204 F01/F02/F03 rerun
→ require 3/3 with real TRACTIAN calls + valid terminal + evaluation
→ close branch protection
→ broaden read/action security/capacity/recovery/human-value evidence
→ final evidence freeze
```

Do not accept `finish_reason=length`, enable paid/model fallback, silently substitute a provider/model, bypass structured output or introduce unbounded retries to manufacture a green result.