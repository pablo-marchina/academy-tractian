# Changelog

Notable user-, operator- and reviewer-visible changes are recorded here. This is a curated product changelog, not a dump of Git commits.

The structure follows the useful parts of [Keep a Changelog](https://keepachangelog.com/): an `Unreleased` section, ISO dates and change categories.

## Unreleased

### Added

- Documentation architecture based on user tasks and distinct tutorial/how-to/reference/explanation needs.
- `GETTING-STARTED.md`, `DOCUMENTATION-GUIDE.md`, active security model and repository `SECURITY.md`.
- Explicit separation between promoted Release 0 evidence and final-project completion criteria.

### Changed

- Canonical architecture, runbook, TAPI crosswalk, acceptance and delivery plan rebaselined to the real hosted Release 0 state.
- Current UX documented as Results → Evidence → Investigation → Engineering progressive disclosure.
- Historical/frozen documentation remains immutable and is clearly separated from active truth.

## PR #196 integrated into `main` — 2026-09-06

### Changed

- Promoted PR `#196` from `release/production-final` after source head `d7e941b1e0ee380f3cca43816521c88eddc20e9c` completed the required regression surface successfully.
- Merged the validated release line into `main` as `9fbfbe0c5b5b80dc23941ac2850125834641e32b`.
- Updated canonical documentation so active state no longer presents PR `#196` as open or `release/production-final` as the canonical repository branch.
- Kept repository integration identity separate from hosted component identities: promoted backend/runtime `082d6f115c070fdc898df749b4b3018efd9ceeab`, hosted frontend UX `2ca6215ccc07664a9551e8363e438f0930a4d995`, and hosted supplied API `47561c1175181b508139e23e6e39b555c1347d57`.

### Boundaries

- The repository merge is not claimed as an automatic application redeploy.
- Consequential external action execution, final provider selection, full hosted security/load/recovery evidence, human semantic calibration, operational-value proof and adaptive-policy superiority remain unpromoted.

## Release 0 UX pilot — 2026-09-06

### Added

- Four progressive product-depth tabs: **Results**, **Evidence**, **Investigation**, **Engineering**.
- Keyboard-accessible tab navigation with Arrow Left/Right, Home and End.
- Customer-first Results layer with onboarding, guided/starter investigations, human-readable progress and next-step guidance.
- Evidence layer with canonical safe event/evidence trail.
- Investigation layer with persisted run history, runtime metrics, Trace Graph and governed action visibility.
- Engineering layer with capability surface, architecture, evaluator, operations analytics and controlled research collectors.
- Explicit starter examples when server-owned guided intents are unavailable; examples never masquerade as capabilities.

### Changed

- Technical surfaces moved behind progressive disclosure instead of dominating first-use experience.
- CLARIFY, ABSTAIN, ESCALATE and FINAL each communicate a distinct user next step.
- Hosted Release 0 acceptance workflow changed to intentional/manual promotion with explicit `expected_sha` rather than treating every large-PR frontend change as a backend promotion.

### Fixed

- Quick Start no longer becomes empty in provider-free acceptance environments.
- Browser acceptance scopes empty-state checks to the visible UX layer.

## Release 0 — 2026-09-06

### Added

- Real remotely hosted multi-user product path.
- Managed browser authentication and server-owned tenant context.
- Neon PostgreSQL durable serving state and tenant isolation.
- Provisional Cloudflare Release 0 DecisionSource.
- Real canonical TRACTIAN reads through the typed tool boundary.
- Hosted FINAL, CLARIFY, ABSTAIN and ESCALATE behavior.
- Durable evidence, lineage, evaluation, history and authenticated REST/SSE.
- Browser-safe Release 0 capability contract covering 13 reads and 5 proposal-only actions.

### Security

- Consequential external actions disabled for Release 0.
- Browser cannot own tenant/role/permission authority.
- Cross-tenant release negatives passed in the hosted two-user campaign.
- No automatic paid fallback; project cost policy remains USD0.
- No local/mock dependency in production serving.