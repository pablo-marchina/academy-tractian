# Academy × TRACTIAN — Active Project Status

**Status:** Release 0 **PROMOTED / HARDENED V13** / task-driven UX live / governed actions enabled with live-validation gap  
**Last verified:** 2026-09-07 BRT  
**Current merged backend/runtime source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`  
**Current healthy backend release:** same source SHA, Railway hosted and healthy after #213  
**Current hosted frontend UX SHA:** `1bc124a8d4dbd029178ff8129b25452129445de7`  
**Frontend Railway deployment:** `f78e88cd-82c2-4fcf-8f59-a51168f10fad` — `SUCCESS`  
**Current hosted supplied-API SHA:** `47561c1175181b508139e23e6e39b555c1347d57`  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Release branch:** `release/production-final`

This file is the mutable source of truth for **current execution state**. Frozen/history files remain immutable.

The original Release 0 acceptance campaign remains anchored to backend `082d6f115c070fdc898df749b4b3018efd9ceeab`. Current production is a prospectively tested/hardened descendant; updating this current-state document does not rewrite the original campaign.

## 1. Current objective

The hosted vertical slice, response-mode semantics, explicit-asset grounding, managed-session incident and task-driven frontend are no longer the primary blockers. Governed consequential-action execution has now been implemented, CI-qualified and enabled in production configuration, but the five-action live acceptance gate is still open.

Current objective:

> **close the server-owned upstream action-actor identity gap, re-run the five-action production smoke to explicit acceptance, then finish broad live coverage/security/capacity/recovery/value evidence without weakening any deterministic safety boundary.**

Current user path:

```text
authenticated remote user
→ Home
→ natural-language equipment question
→ server-owned identity + authorized fleet discovery when needed
→ live provider + typed TRACTIAN reads
→ persisted evidence
→ terminal decision + response_mode
→ customer-first result + next step
→ contextual evidence detail
→ Analyses for persisted history
→ Technical for trace/quality/data/system/actions/studies
```

Consequential actions are no longer deny-all at composition time. They are gated by exact proposal custody, explicit confirmation, server-owned grant authorization, resource scope, idempotency, lease/fencing, kill switch and explicit upstream acceptance.

## 2. Current hosted component ledger

| Component | State | Identity / evidence |
|---|---|---|
| public HTTPS product | **PASS** | Railway public origin |
| backend/runtime source | **PASS / hosted** | `3545d75c...`; #213 release deployed successfully |
| frontend UX | **PASS / task-driven** | `1bc124a...`, deployment `f78e88cd...` |
| supplied TRACTIAN API | **PASS / hosted** | `47561c...` |
| Neon PostgreSQL | **PASS Release 0** | durable serving state + RLS |
| managed browser auth | **PASS hardened scope** | server-owned context; read-burst cache + fresh mutation validation |
| hosted provider | **PASS — PROVISIONAL** | Cloudflare Release 0 route |
| typed TRACTIAN reads | **PASS sampled live paths** | real remote HTTP 2xx observed |
| governed action architecture | **PASS implementation/CI** | custody + confirmation + grants + idempotency + lease/fencing + uncertainty |
| action production configuration | **ENABLED** | five executable governed actions advertised |
| all five upstream writes | **NOT PROVEN** | live smoke blocked on `update_asset_config` HTTP 403 |
| safe deployment containment | **PASS** | failed validation did not replace healthy serving deployment |
| actual project cash cost | **USD0 policy** | no automatic paid fallback |
| local/mock production dependency | **ZERO** | remote serving only |

## 3. Release 0 live-hardening sequence — 2026-09-07

The hardening work was driven by **actual production prompts, traces, deployment behavior and upstream responses**, not hypothetical cleanup.

| PR | Problem / objective | Production effect |
|---|---|---|
| #197 | agent could ask user for discoverable IDs after fleet evidence | continue grounded discovery; customer does not need internal IDs |
| #198 | nested structured asset/analysis IDs were not reliably recovered | bounded structured nested ID extraction |
| #199 | redundant `get_asset` loops after fleet listing | remove redundant metadata path |
| #200 | terminal could occur after baseline without real condition evidence | require condition evidence when needed |
| #201 | useful directional answer could be labelled `inconclusive` | explicit `response_mode` semantics |
| #207 | dashboard read burst caused `managed_session_unavailable` | bounded read-session coalescing + correct 401/503 semantics |
| #208 | explicit labels/comparisons could request internal IDs or under-investigate | resolve labels through fleet; bilateral evidence; data-quality requirement |
| #209 | frontend remained too navigation/depth centric | task-driven Home / Analyses / Technical UX |
| #210 | explicit label could terminate before initial identity discovery; completed quality read could reappear | force `get_current_user` first; suppress completed single-asset quality read |
| #211 | five canonical action tools existed but production execution was not promoted | governed execution path enabled behind deterministic safety + server-owned grants |
| #213 | action capability could be configured without a single auditable five-write live gate | manual production smoke requires all five writes to return accepted status + `accepted=true` |

Current read orchestration remains V13 through `build_release_provider_decision_source_factory_v13`.

## 4. Read-path V13 semantics

### Response modes

`response_mode` is customer-visible epistemic status, independent from authorization and distinct from the terminal decision:

- `complete` — all material requested parts are supported;
- `partial` — useful supported conclusion exists but a material part remains probabilistic/incomplete;
- `inconclusive` — inspected evidence cannot support a reliable directional answer to the core question;
- `conflict` — material observations contradict each other;
- `unavailable` — required authorized evidence could not be obtained.

Critical live rule: **supported directional answer + probabilistic causal mechanism → `partial`, not `inconclusive`.**

### Asset grounding

For an investigative request containing a human-readable label such as `R310`:

```text
get_current_user
→ list_assets_by_company(company_id from structured user observation)
→ resolve label only against authorized fleet IDs
→ inspect evidence required by the question
→ terminal
```

The runtime must not ask for a discoverable `company_id`/`asset_id`.

For comparisons, evidence for one asset cannot authorize a comparative claim about another. If a requested label is not present in the authorized fleet, return bounded unavailability rather than inventing another company/tenant.

### Evidence requirements

- diagnostic/condition questions require condition evidence from `get_analysis`, `get_rms` or `get_spectrum` before terminal where applicable;
- baseline/data quality alone are not substitutes for condition evidence when the core question asks what is happening;
- explicit data-quality questions require `get_data_quality`;
- once a successful single-asset data-quality read satisfies that requirement, it is removed from the visible surface for that question;
- `list_assets_by_company` already grounds fleet metadata, so `get_asset` is suppressed as a redundant post-fleet read.

## 5. Managed-session resilience

Current #207 contract:

- GET/HEAD: server-validated context may be reused for ≤2 s;
- cache key: SHA-256 of cookie only; raw cookie not cached;
- 256-entry cap + singleflight coalescing;
- POST/non-read: always fresh validation;
- no stale-on-error after TTL;
- invalid session: `401`;
- temporary managed-auth failure: `503 managed_session_unavailable`, `Retry-After: 1`;
- frontend reconciles auth on invalid/unavailable signals and on focus/visibility return.

Live retesting after #207 did not reproduce the earlier burst in the tested scope. This is not a final auth availability SLO.

## 6. Final V13 live read retest matrix

### A. Data quality / diagnosis trust

Run: `run_21813cb7b4ad9adbdc5e`

```text
get_current_user
→ list_assets_by_company
→ get_data_quality(asset_R310)
→ get_rms(asset_R310)
→ get_rms(asset_R310, point_id=pt_R310_de)
→ FINAL
```

Observed: `response_mode=complete`, 5 tool calls, all remote reads HTTP 200, 0 errors, 0 policy blocks, one data-quality read.

### B. Comparison with unavailable asset

Run: `run_547b2a62d84ef56a3d3d`

R310 was present; R420 was not present in the authorized fleet. The runtime did not invent R420, cross tenant scope or ask the user for its internal ID. This validates fail-closed missing-label behavior, not bilateral comparison quality.

### C. Probabilistic causal investigation

Run: `run_97b91f6e0feb91184283`

```text
get_current_user
→ list_assets_by_company
→ get_spectrum(asset_R310)
→ point-specific spectrum drill-down
→ FINAL
```

Observed: `response_mode=partial`, 5 tool calls, remote reads HTTP 200, 0 errors, 0 policy blocks and no request for internal IDs.

## 7. Task-driven UX

Hosted frontend `1bc124a...` is task-driven:

- **Home** — primary question entry;
- **Result** — conclusion, next step and contextual evidence;
- **Analyses** — persisted run history;
- **Technical** — specialist analysis/quality/data/system/actions/studies.

The user review in this conversation reinforced a stricter UX north star:

> each screen should have one main question for the user to answer.

Therefore continuing simplification should reduce simultaneous cards, labels, statuses, duplicated evidence and specialist terminology in the normal path. This is an open UX-quality target; automated tests do not constitute human usability validation.

## 8. Governed action architecture now promoted

Canonical actions:

| Tool | Permission |
|---|---|
| `reprocess_analysis` | `action_low` |
| `request_specialist_analysis` | `action_low` |
| `update_asset_config` | `action_high` |
| `request_retraining` | `action_high` |
| `escalate_case` | `escalate` |

Confirmed execution requires independent gates for authenticated requester ownership, server-owned tenant-aware grant, canonical ToolSpec permission, resource/company binding, exact server-custodied fingerprint/arguments, explicit confirmation, durable idempotency claim, active lease/generation and the host-owned kill switch.

A write is not marked `ACCEPTED` unless the external API explicitly returns acceptance. Ambiguous outcomes are contained as `UNCERTAIN` and are never blindly retried.

## 9. CI evidence for the action promotion

PR #213 final required-gate run: `34164123263`.

Green surfaces included:

- production runtime and standalone wheel;
- PostgreSQL action lease/fencing/restart semantics;
- horizontal PostgreSQL runtime/handoff;
- Railway IaC contracts;
- remote production image and release-SHA drift rejection;
- clean-clone full product reproduction;
- full-product Chromium Playwright;
- final required gate.

This proves source/artifact regression quality for the tested contract. It does not substitute for live upstream write acceptance.

## 10. Live five-action smoke and current blocker

PR #213 added `src/academy_tractian/governed_write_transport_smoke.py` and merged at:

```text
3545d75c00ca30419e0f47e8b1950aa50cbbf462
```

The smoke first requires five executable governed capabilities and then calls all five canonical action endpoints through the canonical binder + production transport. Success requires accepted HTTP status and `accepted=true` for every action.

A fresh Railway configuration snapshot executed the smoke in pre-deploy. Deployment `5ba36471-776c-4e15-919b-56e2da216b74` failed safely with:

```text
update_asset_config: http_403:accepted_false
```

The healthy prior production release continued serving. This is the correct deployment/safety behavior.

## 11. Upstream actor identity finding

Inspection of the immutable supplied TRACTIAN runtime established:

- upstream user context is selected via `x-user-id`;
- action endpoints enforce `action_low`, `action_high` or `escalate` explicitly;
- for the company scope under test, low-impact actions and high/escalation actions are represented by **different supplied-runtime upstream users**.

The existing runner identity binding forwards the local requester user ID to the upstream `x-user-id`. Therefore the current mapping cannot satisfy every upstream action family by design.

Corrective target:

```text
local authenticated product user
→ local tenant/resource authorization, confirmation, custody, idempotency, audit

(company_id, required_permission)
→ server-owned TRACTIAN upstream actor
→ injected only at final action network boundary
```

The browser/model/confirmation payload must never select that upstream actor. Missing or ambiguous mapping must fail closed.

Implementation is in progress on `fix/server-owned-upstream-action-actors`; it is not merged or production-proven yet.

## 12. Provider state

Cloudflare `@cf/zai-org/glm-4.7-flash` remains a **provisional Release 0 provider**. Frozen Provider Tournament v3 remains `NO_SELECTION`; Release 0 qualification is not proof of final superiority.

## 13. Deliberate non-claims / open final gates

The project still does **not** claim:

- complete live coverage of all 13 read operations;
- complete five-action upstream acceptance;
- correctness of the in-progress upstream actor routing fix;
- true bilateral comparison quality without two authorized present assets;
- systematic multi-turn/context-retention live quality;
- final Provider Tournament v3;
- full SECURITY-V1 hosted campaign;
- final remote load/capacity/SLO/HA evidence;
- real backup/restore + measured RTO/RPO;
- human semantic calibration;
- observed MANUAL vs AGENT-ASSISTED time savings;
- adaptive-policy superiority;
- human usability validation of the current UX.

## 14. Current priority order

```text
P0 preserve auth/tenant/action/cost safety
→ finish server-owned upstream actor routing
→ unit/integration/adversarial tests for company+permission mapping
→ full required CI
→ exact-SHA deployment
→ five-action live smoke: 5/5 accepted
→ broad live read/prompt coverage
→ security/load/recovery gates
→ human semantic/usability/operational-value evidence
→ final evidence freeze
```

Do not weaken the local grant, confirmation, idempotency or tenant boundary to make an upstream 403 disappear.

See [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md) for the dated evidence record.