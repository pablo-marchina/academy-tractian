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
- Governed production execution architecture for all five canonical TRACTIAN actions: private custody, exact confirmation, server-owned grants, resource/company authorization, persistent idempotency, non-transferable lease/fencing and explicit `UNCERTAIN` containment.
- Manual-only `academy_tractian.governed_write_transport_smoke` production validator that requires the hosted capability surface to advertise five executable actions and requires every canonical write to return an accepted HTTP status plus `accepted=true`.
- Dated production evidence note covering the governed-action rollout, CI, Railway snapshot behavior, live 403 and upstream actor identity finding.

### Changed

- Backend production source advanced prospectively from the earlier V13 read-hardening artifact to `3545d75c00ca30419e0f47e8b1950aa50cbbf462`, which includes the governed-action path and auditable write smoke.
- Frontend production remains task-driven at `1bc124a8d4dbd029178ff8129b25452129445de7`; further structural simplification is now explicitly tracked around the principle that each screen should answer one primary user question.
- The 18-operation capability contract is now described as **13 reads + 5 governed actions**, not as five permanently proposal-only actions.
- Diagnostic asset investigations require condition evidence from analysis/RMS/spectrum before a diagnostic terminal answer where the request requires it.
- Fleet discovery suppresses redundant `get_asset` metadata reads after `list_assets_by_company` has grounded the inventory.
- Repetition analysis distinguishes exact duplicate calls from legitimate asset → `point_id` technical drill-down.
- Production promotion guidance now distinguishes Railway generic `redeploy` from a fresh source/configuration snapshot; a redeploy may reuse captured configuration and is not sufficient provenance for a changed pre-deploy gate.
- Documentation/presentation material now separates implemented/CI-proven/hosted-proven/live-upstream-proven claims explicitly.

### Fixed

- Repeated identity/fleet-discovery loops that previously exhausted the tool-call budget.
- Premature terminal responses that identified a critical asset but stopped before condition evidence.
- Useful directional answers incorrectly labelled `inconclusive`; supported ranking plus probabilistic mechanism now maps to `partial` unless evidence justifies `complete`.
- Requests for user-supplied `asset_id`/`company_id` when the authorized runtime could discover those resources itself.
- Explicit-asset comparison paths that could attempt a conclusion without grounding both requested assets.
- Repeated completed `get_data_quality` calls for the same constrained single-asset question.
- `managed_session_unavailable` caused by forcing remote strong session validation on every protected dashboard read burst.
- Frontend “authenticated ghost” state after backend auth/session failure.
- Production documentation drift that continued to describe the current runtime as read-only after governed actions had been promoted.

### Security

- GET/HEAD managed-session validation uses a bounded 2-second server cache keyed only by SHA-256 of the opaque cookie, with 256-entry cap and singleflight coalescing.
- Non-read requests continue to force fresh managed-session validation.
- Expired cache entries are never used as stale-on-error fallback.
- `401` invalid session and `503 managed_session_unavailable` remain separate fail-closed states.
- Consequential actions are no longer deny-all in the current production composition; they are protected by exact private custody, server-owned authorization/resource scope, explicit confirmation, persistent idempotency, lease/fencing and a host-owned kill switch.
- `ACCEPTED` requires explicit upstream acceptance. Ambiguous writes become `UNCERTAIN` and are not blindly retried.
- A live five-action validation correctly failed closed on `update_asset_config` HTTP 403 / `accepted=false`; the local grant was **not** widened to work around the vendor denial.
- Investigation identified a vendor-principal separation requirement: local product identity must remain the authorization/audit principal while the final TRACTIAN actor must be selected server-side by company + required permission. The corrective routing is still in progress and is not yet a production-readiness claim.

### Live evidence

- Governed-action enablement PR #211 merge `1a1e7139bfa0361416120b3f21937c4048b5bb1f`; Railway deployment `9732a2cb-c321-4fcf-83f8-c6f87eeab06a` — `SUCCESS`.
- Auditable smoke PR #213 merge `3545d75c00ca30419e0f47e8b1950aa50cbbf462`; Railway deployment `2cbc4215-f59a-4947-8691-0d4776458445` — `SUCCESS`.
- PR #213 required-gate workflow run `34164123263` — `SUCCESS`, including action lease/fencing, horizontal runtime, production image, Railway IaC, clean-clone reproduction and Chromium full-product acceptance.
- Fresh write-validation deployment `5ba36471-776c-4e15-919b-56e2da216b74` — `FAILED SAFE` in pre-deploy because `update_asset_config` returned HTTP 403 / `accepted=false`; prior healthy production remained serving.
- Frontend deployment `f78e88cd-82c2-4fcf-8f59-a51168f10fad` remains the task-driven UI at exact SHA `1bc124a...`.
- V13 data-quality run `run_21813cb7b4ad9adbdc5e`: `complete`, 5 tools, 0 errors, 0 policy blocks.
- V13 missing-asset comparison `run_547b2a62d84ef56a3d3d`: `unavailable`, R420 not found in authorized fleet, no invented ID/tenant scope.
- V13 causal investigation `run_97b91f6e0feb91184283`: `partial`, 5 tools, 0 errors, 0 policy blocks.

## Governed actions production rollout — 2026-09-07

- PR #211 promoted governed execution for all five canonical actions after the required production/action safety gates passed.
- Production booted with live provider, live TRACTIAN transport, action switch enabled and server-owned minimum-scope authorization grants.
- PR #213 added an auditable five-action smoke that contains no real credentials/resources/grants in source and never prints them.
- A fresh Railway configuration snapshot was required to prove the intended pre-deploy command actually ran; generic redeploy had reused an older captured snapshot.
- The first decisive live write campaign surfaced `update_asset_config` HTTP 403 and safely stopped deployment promotion.
- Inspection of the immutable supplied runtime showed separate vendor users for `action_low` and `action_high + escalate` in the tested company scope.
- Corrective design separates local requester authorization/audit from a server-owned vendor actor selected by `(company_id, required_permission)` only at the final network boundary.
- Until that routing is merged, retested and the smoke passes 5/5, complete governed-action readiness remains explicitly **NOT PROVEN**.

## Task-driven UX promotion — 2026-09-07

- PR #209 rebuilt the primary user navigation around Home / Analyses / Technical while preserving contextual result/evidence and full engineering observability.
- Railway `production-web` promoted exact merge `1bc124a8d4dbd029178ff8129b25452129445de7`.
- The frontend promotion is tracked independently from backend runtime promotion.
- Subsequent user review established an additional global simplification target: fewer simultaneous cards/statuses/labels, evidence contextual to result, technical depth outside the normal path, and one primary question/action per screen.

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
- Browser-safe Release 0 capability contract covering 13 reads and 5 proposal-only actions **at that historical Release 0 stage**.

### Security

- Consequential external actions were disabled for the original Release 0 acceptance scope.
- Browser could not own tenant/role/permission authority.
- Cross-tenant release negatives passed in the hosted two-user campaign.
- No automatic paid fallback; project cost policy remained USD0.
- No local/mock dependency in production serving.