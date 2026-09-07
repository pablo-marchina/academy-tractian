# Changelog

Notable user-, operator- and reviewer-visible changes are recorded here. This is a curated product changelog, not a dump of Git commits.

## Unreleased

### Added

- Release 0 V13 live-hardening documentation and production validation matrix.
- Explicit customer-visible `response_mode` contract: `complete`, `partial`, `inconclusive`, `conflict`, `unavailable`.
- Human-readable explicit-asset grounding for labels such as R310/R420 without requiring users to know internal resource IDs.
- Per-asset evidence requirements for comparative questions.
- Data-quality-specific evidence requirement before answering data-quality questions.
- Managed-session resilience semantics that distinguish invalid session (`401`) from temporary identity-service unavailability (`503`, retryable).
- Task-driven hosted UX organized around **Home / Analyses / Technical**.

### Changed

- Backend production runtime advanced prospectively from the original Release 0 acceptance artifact to V13 at `08866da60245f58f217981b7ae668b10be45cc67`.
- Frontend production advanced to task-driven UX at `1bc124a8d4dbd029178ff8129b25452129445de7`.
- Diagnostic asset investigations now require condition evidence from analysis/RMS/spectrum before a diagnostic terminal answer where the request requires it.
- Fleet discovery suppresses redundant `get_asset` metadata reads after `list_assets_by_company` has grounded the inventory.
- Repetition analysis now distinguishes exact duplicate calls from legitimate asset → `point_id` technical drill-down.
- Documentation and presentation material now reflects the actual task-driven hosted UI and current hardened backend, while preserving frozen historical evidence.

### Fixed

- Repeated identity/fleet-discovery loops that previously exhausted the tool-call budget.
- Premature terminal responses that identified a critical asset but stopped before condition evidence.
- Useful directional answers incorrectly labelled `inconclusive`; supported ranking plus probabilistic mechanism now maps to `partial` unless evidence justifies `complete`.
- Requests for user-supplied `asset_id`/`company_id` when the authorized runtime could discover those resources itself.
- Explicit-asset comparison paths that could attempt a conclusion without grounding both requested assets.
- Repeated completed `get_data_quality` calls for the same constrained single-asset question.
- `managed_session_unavailable` caused by forcing remote strong session validation on every protected dashboard read burst.
- Frontend “authenticated ghost” state after backend auth/session failure.

### Security

- GET/HEAD managed-session validation now uses a bounded 2-second server cache keyed only by SHA-256 of the opaque cookie, with 256-entry cap and singleflight coalescing.
- Non-read requests continue to force a fresh managed-session validation.
- Expired cache entries are never used as stale-on-error fallback.
- `401` invalid session and `503 managed_session_unavailable` are separate fail-closed states.
- Consequential external actions remain disabled; live prompt testing produced zero action execution.

### Live evidence

- Backend deployment `062c3cc4-4ac9-48ac-be06-2b4c490cea2a` — `SUCCESS`, exact SHA `08866da...`.
- Frontend deployment `f78e88cd-82c2-4fcf-8f59-a51168f10fad` — `SUCCESS`, exact SHA `1bc124a...`.
- V13 data-quality run `run_21813cb7b4ad9adbdc5e`: `complete`, 5 tools, 0 errors, 0 policy blocks.
- V13 missing-asset comparison `run_547b2a62d84ef56a3d3d`: `unavailable`, R420 not found in authorized fleet, no invented ID/tenant scope.
- V13 causal investigation `run_97b91f6e0feb91184283`: `partial`, 5 tools, 0 errors, 0 policy blocks.

## Task-driven UX promotion — 2026-09-07

- PR #209 rebuilt the primary user navigation around Home / Analyses / Technical while preserving contextual result/evidence and full engineering observability.
- Railway `production-web` promoted exact merge `1bc124a8d4dbd029178ff8129b25452129445de7`.
- The frontend promotion is tracked independently from backend runtime promotion.

## Release 0 live hardening — 2026-09-07

- #197 continued grounded fleet discovery and aligned user-visible response semantics.
- #198 hardened structured nested asset/analysis ID extraction.
- #199 removed redundant asset-metadata loops.
- #200 required condition evidence before diagnostic terminal.
- #201 defined response-mode semantics.
- #207 hardened managed session resilience.
- #208 grounded explicit asset labels/comparisons and data-quality requirements.
- #210 closed the initial explicit-asset identity-grounding gap and removed completed single-asset data-quality reads from the visible surface.

## PR #196 integrated into `main` — 2026-09-06

PR #196 remains historical repository-integration evidence. It did not freeze all later hosted component identities. Current hosted identities live in `docs/ACTIVE-PROJECT-STATUS.md`.

## Release 0 UX pilot — 2026-09-06

The earlier Results / Evidence / Investigation / Engineering progressive-disclosure UX established the first-user baseline and remains historical context. It was superseded in the hosted frontend by the task-driven Home / Analyses / Technical navigation without removing the underlying evidence/runtime/engineering capabilities.

## Release 0 — 2026-09-06

### Added

- Real remotely hosted multi-user product path.
- Managed browser authentication and server-owned tenant context.
- Neon PostgreSQL durable serving state and tenant isolation.
- Provisional Cloudflare Release 0 DecisionSource.
- Real canonical TRACTIAN reads through the typed tool boundary.
- Hosted safe terminal behavior.
- Durable evidence, lineage, evaluation, history and authenticated REST/SSE.
- Browser-safe Release 0 capability contract covering 13 reads and 5 proposal-only actions.

### Security

- Consequential external actions disabled for Release 0.
- Browser cannot own tenant/role/permission authority.
- Cross-tenant release negatives passed in the hosted two-user campaign.
- No automatic paid fallback; project cost policy remains USD0.
- No local/mock dependency in production serving.