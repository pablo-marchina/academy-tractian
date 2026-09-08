# Changelog

Notable user-, operator- and reviewer-visible changes are recorded here. This is a curated product changelog, not a dump of Git commits. Historical sections remain intentionally preserved.

## Unreleased — 2026-09-08 functional-closure work

### Added

- Governed production execution path for the five canonical TRACTIAN consequential actions using server-owned authorization grants, private custody, explicit confirmation, persistent idempotency, non-transferable action leases and server-owned upstream TRACTIAN actors.
- Production pre-deploy governed-write smoke covering all five canonical actions; all five controlled calls were accepted with HTTP 200 while recording no credentials, resource IDs, local/upstream user IDs or response bodies.
- Full-system independent Verification V1 with claim-bounded functional/evidence oracles, evaluator meta-evaluation and verification surfaces that distinguish structural integrity from functional correctness.
- Provider-independent exact-success duplicate-call invariant using safe normalized argument fingerprints; same-tool/different-argument technical drill-down remains allowed.
- OpenRouter V14 provider adapter preserving V13 grounding/response semantics while pinning `nvidia/nemotron-3-super-120b-a12b:free` under a fixed-free route with provider fallbacks disabled.
- Authenticated hosted functional campaign for B204 condition, causal and data-quality tasks.
- Sanitized OpenRouter diagnostics: model-call diagnosis, initial-call probe, response-shape probe, bounded length/reasoning experiment and safe key-tier/rate-limit probe.
- Cross-provider tournament/eligibility infrastructure for new governed provider research without rewriting consumed historical tournaments.
- Comprehensive 2026-09-08 progress record at `docs/progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`.

### Changed

- Production backend advanced to `5611687556b3d50c31f20fa85ede794f2500f05c` (`production-api` deployment `542bf459-353d-432c-b2ff-b862cedf1574`) and now serves the V14 provider composition.
- Current hosted frontend identity is `4364364266c6a88d4affd85cb3a734c774cd42c8`; supplied TRACTIAN API remains `47561c1175181b508139e23e6e39b555c1347d57`.
- Production action identity is separated from local user authorization: confirmed writes route through immutable server-owned upstream TRACTIAN actor bindings rather than browser/model-provided identity.
- Ordinary authenticated users retain read access even when no consequential-action grant exists; the fallback principal authorizes zero actions and confirmation remains strict/tenant-aware.
- Current documentation no longer describes production as read-only Cloudflare V13. Active docs now represent governed actions, OpenRouter V14, exact hosted identities and the current failing functional gate while preserving frozen history.

### Fixed / hardened

- Incomplete active action-grant→upstream-actor coverage is a boot blocker rather than a late runtime surprise.
- Exact successful direct-measurement loops are suppressed without incorrectly blocking valid asset→point progressive reads.
- Verification UX/documentation no longer treats structural evaluator success as generic end-to-end functional success.

### Current OpenRouter V14 functional result

Real managed-session B204 runs:

```text
F01 condition      run_437a59ba893a96e3f902  FAIL
F02 causal         run_86c832ce46189200b613  FAIL
F03 data quality   run_f081d5d45b0cf4caf4b3  FAIL
```

All three reach authenticated production runtime creation/execution but terminate with `DECISION_SOURCE_FAILURE` and zero TRACTIAN calls.

Sanitized first-call response evidence:

```text
HTTP 200
served model = nvidia/nemotron-3-super-120b-a12b:free
one assistant choice
content present
finish_reason = length
```

V14 correctly rejects the truncated completion rather than granting tool authority from incomplete output. A bounded follow-up comparison of current output budget, reasoning minimization and larger bounded output budget was blocked by HTTP 429 on every variant, so the fix remains `INCONCLUSIVE`.

### Security / claim boundary

- OpenRouter fallback remains disabled; USD0/no-paid-spillover remains a hard gate.
- No workaround may accept `finish_reason=length`, silently substitute model/provider, bypass structured-output integrity or add unbounded retries.
- Governed action transport smoke 5/5 is not equivalent to completed full hosted action SECURITY-V1.
- Latest observed GitHub branch metadata still reports `main.protected=false` and required status-check enforcement off.
- Production SHA and draft functional-closure PR head intentionally differ until the exact candidate is accepted/promoted.

## V13 live hardening / task-driven UX — 2026-09-07

### Added

- Explicit customer-visible `response_mode` contract: `complete`, `partial`, `inconclusive`, `conflict`, `unavailable`.
- Human-readable explicit-asset grounding for labels such as R310/R420 without requiring users to know internal resource IDs.
- Per-asset evidence requirements for comparative questions.
- Data-quality-specific evidence requirement before answering data-quality questions.
- Managed-session resilience semantics that distinguish invalid session (`401`) from temporary identity-service unavailability (`503`, retryable).
- Task-driven hosted UX organized around **Home / Analyses / Technical**.

### Changed

- Backend production runtime advanced prospectively from the original Release 0 acceptance artifact to V13 at `08866da60245f58f217981b7ae668b10be45cc67`.
- Frontend production advanced to task-driven UX at `1bc124a8d4dbd029178ff8129b25452129445de7`.
- Diagnostic asset investigations require condition evidence from analysis/RMS/spectrum before a diagnostic terminal answer where the request requires it.
- Fleet discovery suppresses redundant `get_asset` metadata reads after `list_assets_by_company` has grounded inventory.
- Repetition analysis distinguishes exact duplicate calls from legitimate asset→`point_id` drill-down.

### Fixed

- Repeated identity/fleet-discovery loops that exhausted tool-call budget.
- Premature terminal responses before condition evidence.
- Useful directional answers incorrectly labelled `inconclusive` where `partial` better matched supported evidence.
- Requests for user-supplied discoverable `asset_id`/`company_id`.
- Explicit-asset comparison paths lacking both-resource grounding.
- Repeated completed `get_data_quality` calls for the same constrained single asset.
- managed-session read fan-out and frontend authenticated-ghost behavior.

### Security

- GET/HEAD managed-session validation uses a bounded two-second server cache keyed only by SHA-256 of the opaque cookie, with bounded capacity/singleflight.
- Non-read requests force fresh managed-session validation.
- Expired contexts are never stale-on-error authorization.

## Task-driven UX promotion — 2026-09-07

PR #209 rebuilt primary navigation around Home / Analyses / Technical while preserving contextual result/evidence and engineering observability. Its original Railway/frontend identity remains historical evidence; the frontend has since advanced.

## Release 0 live hardening — 2026-09-07

- #197 continued grounded fleet discovery and aligned response semantics.
- #198 hardened structured nested asset/analysis ID extraction.
- #199 removed redundant asset-metadata loops.
- #200 required condition evidence before diagnostic terminal.
- #201 defined response-mode semantics.
- #207 hardened managed-session resilience.
- #208 grounded explicit asset labels/comparisons and data-quality requirements.
- #210 closed the explicit-asset identity-grounding gap and removed completed single-asset data-quality repetition.

## Release 0 — 2026-09-06

Original Release 0 established:

- real remotely hosted multi-user product path;
- managed browser authentication and server-owned tenant context;
- Neon PostgreSQL durable state and tenant isolation;
- provisional Cloudflare DecisionSource;
- real canonical TRACTIAN reads through the typed tool boundary;
- safe terminal behavior;
- durable evidence/lineage/evaluation/history/REST/SSE;
- 18-operation capability contract with actions then proposal-only;
- no automatic paid fallback and no local production serving dependency.

This section is historical. Current production state is owned by `docs/ACTIVE-PROJECT-STATUS.md`.