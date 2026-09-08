# Academy × TRACTIAN — Active Project Status

**Status:** Release 0 **PROMOTED / HARDENED V13** / task-driven UX live  
**Last verified:** 2026-09-07 BRT  
**Promoted backend/runtime SHA:** `08866da60245f58f217981b7ae668b10be45cc67`  
**Backend Railway deployment:** `062c3cc4-4ac9-48ac-be06-2b4c490cea2a` — `SUCCESS`  
**Current hosted frontend UX SHA:** `1bc124a8d4dbd029178ff8129b25452129445de7`  
**Frontend Railway deployment:** `f78e88cd-82c2-4fcf-8f59-a51168f10fad` — `SUCCESS`  
**Current hosted supplied-API SHA:** `47561c1175181b508139e23e6e39b555c1347d57`  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Release branch:** `release/production-final`

This file is the mutable source of truth for **current execution state**. Frozen/history files remain immutable.

The original Release 0 acceptance campaign remains anchored to backend `082d6f115c070fdc898df749b4b3018efd9ceeab`. The current backend `08866da...` is a prospectively tested/hardened descendant; updating this current-state document does not rewrite the original campaign.

## 1. Current objective

The basic hosted vertical slice, response-mode semantics, explicit-asset grounding and managed-session incident are no longer blockers. Current objective:

> **systematically expand live API/prompt coverage, measure semantic/trajectory correctness and close final security/capacity/recovery/value gates without weakening the read-only production boundary.**

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

Consequential external action execution remains disabled.

## 2. Current hosted component ledger

| Component | State | Identity / evidence |
|---|---|---|
| public HTTPS product | **PASS** | Railway public origin |
| backend/runtime | **PASS / V13** | `08866da...`, deployment `062c3cc4...` |
| frontend UX | **PASS / task-driven** | `1bc124a...`, deployment `f78e88cd...` |
| supplied TRACTIAN API | **PASS / hosted** | `47561c...` |
| Neon PostgreSQL | **PASS Release 0** | durable serving state + RLS |
| managed browser auth | **PASS hardened scope** | server-owned context; read-burst cache + fresh mutation validation |
| hosted provider | **PASS — PROVISIONAL** | Cloudflare Release 0 route |
| typed TRACTIAN reads | **PASS** | real remote HTTP 2xx observed |
| external consequential actions | **DISABLED** | Release 0 deny-all |
| actual project cash cost | **USD0 policy** | no automatic paid fallback |
| local/mock production dependency | **ZERO** | remote serving only |

## 3. Release 0 live-hardening sequence — 2026-09-07

The hardening work was driven by **actual production prompts and traces**, not hypothetical cleanup.

| PR | Problem found live | Production effect |
|---|---|---|
| #197 | agent could ask user for discoverable IDs after fleet evidence | continue grounded discovery; customer does not need internal IDs |
| #198 | nested structured asset/analysis IDs were not reliably recovered | bounded structured nested ID extraction |
| #199 | redundant `get_asset` loops after fleet listing | remove redundant metadata path |
| #200 | terminal could occur after baseline without real condition evidence | require `get_analysis`/`get_rms`/`get_spectrum` condition evidence when needed |
| #201 | useful directional answer could be labelled `inconclusive` | explicit `response_mode` semantics |
| #207 | dashboard read burst caused `managed_session_unavailable` | bounded read-session coalescing + correct 401/503 semantics |
| #208 | explicit labels/comparisons could request internal IDs or under-investigate | resolve labels through fleet; bilateral comparison evidence; data-quality requirement |
| #210 | explicit label could still terminate before initial identity discovery; completed quality read could reappear | force `get_current_user` first; suppress completed single-asset `get_data_quality` |

Current backend serves `build_release_provider_decision_source_factory_v13`.

## 4. V13 orchestration semantics

### Response modes

`response_mode` is customer-visible epistemic status, independent from authorization and distinct from the terminal decision:

- `complete` — all material requested parts are supported;
- `partial` — useful supported conclusion exists but a material part remains probabilistic/incomplete;
- `inconclusive` — inspected evidence cannot support a reliable directional answer to the core question;
- `conflict` — material observations contradict each other;
- `unavailable` — required authorized evidence could not be obtained.

Critical rule validated live: **supported directional answer + probabilistic causal mechanism → `partial`, not `inconclusive`.**

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

## 5. Managed-session resilience — hardened after live incident

Observed incident pattern:

```text
/health = 200
protected dashboard/API reads = 200 → 401/403 instability
user-visible managed_session_unavailable
```

Root cause: every protected read forced remote strong Neon Auth validation; dashboard fan-out amplified transient identity-service dependency.

Current contract:

- GET/HEAD: server-validated context may be reused for ≤2 s;
- cache key: SHA-256 of cookie only; raw cookie not cached;
- 256-entry cap + singleflight coalescing;
- POST/non-read: always fresh validation;
- no stale-on-error after TTL;
- invalid session: `401`;
- temporary managed-auth failure: `503 managed_session_unavailable`, `Retry-After: 1`;
- frontend reconciles auth on invalid/unavailable signals and on focus/visibility return.

Live retesting after #207 did not reproduce the earlier `managed_session_unavailable` burst. This is evidence for the tested scope, not a final auth availability SLO.

## 6. Final V13 live retest matrix

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

Observed:

- `response_mode=complete`;
- 5 tool calls;
- all remote reads HTTP 200;
- 0 errors;
- 0 policy blocks;
- `get_data_quality` executed once.

The two RMS calls are progressive asset → point drill-down, not an exact duplicate loop.

### B. Comparison with unavailable asset

Run: `run_547b2a62d84ef56a3d3d`

```text
get_current_user
→ list_assets_by_company
→ FINAL unavailable
```

R310 was present; R420 was not present in the authorized `comp_papel_sul` fleet. The agent did not invent R420, cross tenant scope or ask the user for its internal ID. This validates fail-closed missing-label behavior. It does **not** validate bilateral comparison quality; that requires two assets actually present in the same authorized fleet.

### C. Probabilistic causal investigation

Run: `run_97b91f6e0feb91184283`

```text
get_current_user
→ list_assets_by_company
→ get_spectrum(asset_R310)
→ point-specific spectrum drill-down
→ FINAL
```

Observed:

- `response_mode=partial`;
- 5 tool calls;
- remote reads HTTP 200;
- 0 errors;
- 0 policy blocks;
- no request for `company_id` or `asset_id`.

The answer identified bearing-related evidence as the most likely mechanism. Confidence wording remains a semantic-calibration target; `partial` correctly preserves that the causal conclusion is probabilistic.

All persisted blocking structural checks for these three runs passed, including execution-chain integrity, model-call provenance, production-trace identity, proposal-contract validity, read-only action safety and terminal consistency.

## 7. Repetition / stopping interpretation

Do **not** classify repetition by tool name alone.

```text
get_spectrum(asset_R310)
→ get_spectrum(asset_R310, point_id=...)
```

or

```text
get_rms(asset_R310)
→ get_rms(asset_R310, point_id=...)
```

can be valid progressive investigation. Redundancy metrics should compare `(tool, normalized arguments/resource target, evidence contribution)` and distinguish exact duplicate calls from drill-down.

## 8. Current UX

Hosted frontend `1bc124a...` is task-driven:

- **Home** — one natural-language question, examples optional, service state visible;
- **Result** — selected run conclusion, next step and contextual evidence access;
- **Analyses** — persisted run history;
- **Technical** — Current analysis / Quality / Data / System / Actions / Studies.

The previous four global depth tabs remain historical UX context, not current navigation.

## 9. Provider state

Cloudflare `@cf/zai-org/glm-4.7-flash` remains a **provisional Release 0 provider**. Frozen Provider Tournament v3 remains `NO_SELECTION`; Release 0 qualification is not proof of final superiority.

## 10. Deliberate non-claims / open final gates

Release 0 still does **not** close:

- broad live prompt/API coverage across all 13 read operations;
- true bilateral comparison evaluation using two assets that actually exist in the same authorized fleet;
- systematic multi-turn/context-retention live evaluation;
- final Provider Tournament v3;
- full SECURITY-V1 hosted campaign;
- final remote load/capacity + evidence-derived SLO;
- real backup/restore drill + measured RTO/RPO;
- governed consequential external action execution;
- human semantic calibration;
- real MANUAL vs AGENT-ASSISTED operational-value study;
- adaptive-policy superiority;
- final evidence freeze/delivery bundle.

## 11. Current priority order

```text
P0 auth/tenant/action/cost regression
→ P1 broaden live prompt + canonical-read coverage
→ P1 semantic/grounding/stopping failures
→ comparative test using two actually available assets
→ multi-turn + failure + session/concurrency tests
→ final provider/security/load/recovery gates
→ human calibration + operational value
→ adaptive challengers only after measured gaps
→ final evidence freeze
```

Do not add new architecture layers unless a measured blocker justifies them.