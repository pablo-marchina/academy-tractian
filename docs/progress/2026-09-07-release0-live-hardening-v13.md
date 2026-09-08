# Release 0 live hardening → V13 — 2026-09-07

**Status:** APPEND-ONLY PROGRESS EVIDENCE  
**Scope:** production prompt testing, response semantics, asset grounding, managed-session resilience and task-driven frontend promotion.

This note records the live-hardening episode prospectively. It does not rewrite the original Release 0 acceptance artifact or older failed runs.

## Starting point

Release 0 was already remotely hosted with managed auth, Neon PostgreSQL/RLS, provisional Cloudflare decisions, typed TRACTIAN reads, safe observability/evaluation and external consequential actions disabled.

The objective of this episode was to test the product with normal industrial prompts and fix concrete failures discovered in production traces.

## Prompt-driven failures and fixes

### Grounded resource discovery

Early live run `run_a5b9c0aa659d64e4c9d5` discovered fleet information but still asked the user to choose/provide an asset ID. PR #197 forced continued authorized discovery rather than delegating discoverable internal IDs to the customer.

Nested structured responses then exposed parser limits. PR #198 added bounded recursive extraction for assets/analyses from structured wrappers without scanning arbitrary free text.

### Metadata loops

Run `run_9ac5b656a2dad349af6b` showed:

```text
get_current_user
→ list_assets_by_company
→ get_asset
→ get_asset
→ get_asset
→ get_asset
→ TOOL_CALL_BUDGET_EXHAUSTED
```

PR #199 removed `get_asset` from the post-fleet discovery path.

### Condition evidence before terminal

After loop removal, a run could stop after analysis discovery/baseline while its own terminal message admitted RMS/spectrum were still needed. PR #200 introduced a TOOL-only continuation stage until actual condition evidence (`get_analysis`, `get_rms` or `get_spectrum`) had been inspected for an asset-investigation request.

A subsequent run reached the desired compact path:

```text
get_current_user
→ list_assets_by_company
→ list_analyses
→ get_spectrum
→ FINAL
```

### Response-mode semantics

A useful directional answer could still be labelled `inconclusive`. PR #201 defined:

```text
complete      all material parts supported
partial       useful supported answer + material probabilistic/incomplete part
inconclusive no reliable directional answer
conflict      material observations contradict
unavailable   required authorized evidence could not be obtained
```

Rule: supported ranking/priority plus probabilistic causal explanation is `partial` unless all material causal claims are sufficiently supported for `complete`.

Live acceptance run `run_46c52b8c1bd701e7d544` returned `partial` on the motivating class and preserved the compact V10 trajectory.

## Managed-session incident and PR #207

During a broader prompt battery, the UI surfaced `managed_session_unavailable`. Railway showed `/health` staying 200 while protected routes alternated auth failures. Root cause was product-induced validation fan-out: every protected read forced remote strong Neon Auth validation.

PR #207 changed the boundary without weakening server-owned authority:

- GET/HEAD cache only, TTL 2 s;
- SHA-256(cookie) key; raw cookie not cached;
- max 256 entries;
- singleflight coalescing;
- POST/non-read always fresh;
- no stale-on-error;
- invalid session → 401;
- managed-auth unavailable → 503 + `Retry-After: 1`;
- frontend invalid/unavailable signals plus focus/visibility reconciliation.

All 9 workflows on the final PR head passed. Backend and frontend were promoted together at SHA `67486667b4a27437cb4d9f30d54dcb6c0f41eb0`. Subsequent prompt/session testing did not reproduce the earlier burst failure in the tested scope.

## Explicit asset grounding — PR #208 / V12

The broader battery found prompts such as R310/R420 comparison and R310 causal certainty could still ask for discoverable internal IDs.

V12 added:

- recognition of human-readable asset labels;
- authenticated identity → company → fleet resolution;
- no request for discoverable `asset_id`;
- per-asset condition evidence for real comparisons;
- fail closed when a requested label is absent from authorized fleet;
- explicit `get_data_quality` requirement for data-quality questions;
- condition evidence additionally required when asking whether a diagnosis can be trusted;
- post-fleet `get_asset` suppression.

PR #208 passed all required workflows and deployed as backend `524bf18569babd00b9238e4ced115d3beef128c1`.

## Initial grounding gap — PR #210 / V13

V12 live retesting exposed two residuals:

1. a prompt beginning with only explicit label R310 could still terminate before any tool and ask for `company_id`;
2. after successful single-asset `get_data_quality`, that tool could reappear in the general surface.

V13 forces the first explicit-asset step to `get_current_user` when no authenticated company observation exists and removes completed single-asset data-quality reads from the subsequent visible registry.

PR #210 passed all 8 required workflows and was squash-merged as:

`08866da60245f58f217981b7ae668b10be45cc67`

Railway deployment:

`062c3cc4-4ac9-48ac-be06-2b4c490cea2a` — `SUCCESS`

Build evidence included exact `RAILWAY_GIT_COMMIT_SHA=08866da...`, wheel installation, `pip check` with no broken requirements, TRACTIAN predeploy smoke HTTP 200/PASS, application startup and `/health` 200.

## Final V13 live retests

### Data quality

`run_21813cb7b4ad9adbdc5e`

```text
get_current_user
→ list_assets_by_company
→ get_data_quality(asset_R310)
→ get_rms(asset_R310)
→ get_rms(asset_R310, point_id=pt_R310_de)
→ FINAL complete
```

5 tools, remote 200s, 0 errors, 0 policy blocks. `get_data_quality` did not repeat.

### Missing comparison asset

`run_547b2a62d84ef56a3d3d`

```text
get_current_user
→ list_assets_by_company
→ FINAL unavailable
```

R420 was absent from authorized `comp_papel_sul` inventory. Runtime did not fabricate the asset, switch scope or ask for internal ID. This is a missing-resource fail-closed pass, not a bilateral-comparison-quality pass.

### Causal investigation

`run_97b91f6e0feb91184283`

```text
get_current_user
→ list_assets_by_company
→ get_spectrum(asset_R310)
→ point-specific spectrum reads
→ FINAL partial
```

5 tools, remote 200s, 0 errors, 0 policy blocks. The terminal identified bearing-related evidence as the most likely mechanism while `partial` preserved causal uncertainty.

All persisted blocking structural checks for the three runs passed.

## Important stopping lesson

Tool-name repetition alone is not a valid redundancy detector.

The TRACTIAN logs proved that apparent repeats were parameter refinement:

```text
/assets/asset_R310/rms
/assets/asset_R310/rms?point_id=pt_R310_de
```

and similarly for spectrum. Future repetition metrics must distinguish exact same resource/arguments from legitimate drill-down.

## Task-driven frontend promotion

PR #209 subsequently reorganized the user experience around Home / Analyses / Technical while preserving result/evidence and full technical observability. Railway deployed merge `1bc124a8d4dbd029178ff8129b25452129445de7` as `production-web` deployment `f78e88cd-82c2-4fcf-8f59-a51168f10fad`.

## Current open validation work

- exercise a larger share of the 13 canonical reads with live prompts;
- choose two assets actually present in one authorized fleet before claiming comparative behavior is fully tested;
- test knowledge/model/analysis/baseline/data-quality surfaces systematically;
- test anti-hallucination/false-precision/conflict/unavailable cases;
- test multi-turn referents/context if product conversation semantics are expected;
- stress managed session/concurrency without bypassing auth;
- maintain zero action execution under action/prompt-injection challenges;
- quantify tool success, exact duplicate rate, drill-down rate, terminal semantic correctness, response-mode correctness and read-operation coverage.

No new orchestration framework is justified by this episode. The fixes remain narrow extensions of the promoted controller/provider boundary.