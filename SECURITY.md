# Security Policy

Security issues in this repository should be handled as vulnerabilities, not as ordinary public bug reports when disclosure could increase risk.

## Supported product state

The actively supported security target is the current production path documented in [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md). Historical research branches, frozen experiment artifacts and provider-free test profiles are retained for provenance but are not production serving targets.

The current product is no longer accurately described as permanently read-only: governed consequential actions are implemented and enabled behind deterministic safety controls. Complete five-action vendor acceptance is still an open readiness gate because the live smoke found an upstream identity/permission mismatch.

## Reporting a vulnerability

Prefer GitHub **private vulnerability reporting / Security Advisories** when it is available. Do not post exploit details, secrets, cross-tenant data, credentials, session material, private action grants, vendor actor mappings or a working attack path in a public issue.

A useful report contains affected component, impact/preconditions, safe reproduction, whether tenant/auth/policy/action-actor boundaries are crossed, observed versus expected behavior, and no real secrets or unrelated personal/customer data.

## High-priority classes

Treat these as P0 until triaged:

- authentication/session bypass or persistent managed-session outage caused by product behavior;
- cross-user or cross-tenant disclosure;
- browser-controlled tenant/role/permission escalation;
- browser/model-controlled upstream action actor or confused-deputy escalation;
- server secret/credential/grant/vendor-actor leakage;
- evaluator/gold/private-custody leakage;
- unauthorized or duplicate consequential external action;
- automatic retry of an ambiguous consequential write;
- paid-spillover/cost-boundary bypass;
- chain-of-thought/private reasoning exposure;
- release-identity/provenance bypass;
- injection that changes tool/action authority;
- RLS bypass or unsafe database role configuration.

## Current production boundary

Current production deliberately separates user/model intent from authority:

- tenant authority is server-owned;
- PostgreSQL RLS is an independent boundary;
- provider and TRACTIAN credentials stay server-side;
- raw sensitive provider/tool payloads and hidden reasoning are excluded from browser projections;
- no automatic paid provider fallback exists;
- action proposals do not execute automatically;
- exact action arguments/fingerprint are privately custodied before confirmation;
- confirmation refers only to the existing action and cannot replace arguments/permissions;
- canonical permissions/resource authority come from server-owned grants;
- persistent idempotency and lease/fencing protect the external attempt;
- `ACCEPTED` requires explicit vendor acceptance;
- ambiguous writes become `UNCERTAIN` and are not blindly retried;
- vendor action identity must be server-owned and selected only after local authorization.

### Current action-readiness limitation

The five-action live production smoke currently does **not** pass 5/5. `update_asset_config` returned HTTP 403 / `accepted=false` under the then-current identity binding, and the validation deployment was aborted before replacing healthy production.

Inspection of the supplied runtime showed different vendor users for low-impact versus high-impact/escalation permissions in the tested company scope. The corrective design therefore separates:

```text
local authenticated product user
→ tenant/resource authorization + custody + confirmation + idempotency + audit

(company_id, required_permission)
→ server-owned TRACTIAN vendor actor
→ injected only at the final action network boundary
```

The browser/model/confirmation payload must never select or upgrade this actor. Missing or ambiguous mappings must fail closed. The corrective routing is still in progress and is not a completed security/readiness claim.

### Managed-session resilience contract

The current auth boundary is intentionally fail-closed **without making every dashboard read a mandatory remote identity round-trip**:

- browser contributes only the opaque managed-session cookie;
- GET/HEAD bursts may reuse a server-validated context for at most **2 seconds**;
- cache key is SHA-256 of the opaque cookie; raw cookie is not stored in the cache;
- cache is bounded to 256 entries and concurrent misses are coalesced;
- POST and other non-read requests always bypass the read cache and validate fresh;
- expired entries are never used as stale-on-error fallback;
- invalid/forbidden managed session → `401 managed_session_invalid`;
- identity service unavailable/non-200 unexpected response → `503 managed_session_unavailable` with `Retry-After: 1`;
- frontend clears authenticated state on invalid session and exposes an explicit retry state on temporary unavailability;
- focus/visibility return triggers session reconciliation in the browser.

This contract was introduced after a live test burst exposed `managed_session_unavailable` while `/health` stayed healthy. The fix reduced auth fan-out while preserving server-owned identity and fresh validation for state-changing requests.

See [`docs/SECURITY-MODEL.md`](docs/SECURITY-MODEL.md) for trust boundaries and remaining non-claims.

## Agent/tool security boundary

Human-readable asset names do not become authority. The runtime resolves labels through the authenticated company/fleet and constrains tool arguments to structured resource IDs observed from authorized responses. If a requested label is absent from the authorized fleet, the agent must fail closed rather than invent another tenant/company scope.

Response-mode semantics are epistemic metadata, not authorization. `complete`, `partial`, `inconclusive`, `conflict` and `unavailable` cannot grant tool/action privileges.

## Action security reporting guidance

A vendor 401/403 caused by an expected permission mismatch is not automatically a vulnerability; it is a readiness/integration failure. It becomes security-relevant if the product can bypass it by client-controlled identity, silently substitute a more privileged actor, cross tenant/company scope, duplicate an external side effect, expose grants/actor mappings or report success without explicit vendor acceptance.

Preserve failed action evidence. Do not widen grants or select a more privileged vendor actor solely to make a test green.

## Disclosure and remediation

Do not weaken or bypass frozen evidence to hide a security failure. Preserve the failing evidence, fix prospectively, add regression coverage and update the active status/architecture/security model when the trusted boundary changes.

A security fix is not considered complete merely because a unit test passes; the applicable hosted tenant/action/auth/vendor-actor boundary must be revalidated before a production claim is restored.

Current dated production evidence: [`docs/progress/2026-09-07-production-governed-actions-ux-and-validation.md`](docs/progress/2026-09-07-production-governed-actions-ux-and-validation.md).