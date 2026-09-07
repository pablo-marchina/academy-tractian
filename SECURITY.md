# Security Policy

Security issues in this repository should be handled as vulnerabilities, not as ordinary public bug reports when disclosure could increase risk.

## Supported product state

The actively supported security target is the current Release 0 production path documented in [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md). Historical research branches, frozen experiment artifacts and provider-free test profiles are retained for provenance but are not production serving targets.

## Reporting a vulnerability

Prefer GitHub **private vulnerability reporting / Security Advisories** when it is available. Do not post exploit details, secrets, cross-tenant data, credentials, session material or a working attack path in a public issue.

A useful report contains affected component, impact/preconditions, safe reproduction, whether tenant/auth/policy boundaries are crossed, observed versus expected behavior, and no real secrets or unrelated personal/customer data.

## High-priority classes

Treat these as P0 until triaged:

- authentication/session bypass or persistent managed-session outage caused by product behavior;
- cross-user or cross-tenant disclosure;
- browser-controlled tenant/role/permission escalation;
- server secret/credential leakage;
- evaluator/gold/private-custody leakage;
- unauthorized or duplicate consequential external action;
- paid-spillover/cost-boundary bypass;
- chain-of-thought/private reasoning exposure;
- release-identity/provenance bypass;
- injection that changes tool/action authority;
- RLS bypass or unsafe database role configuration.

## Current Release 0 boundary

Release 0 deliberately reduces consequence:

- external consequential actions are disabled;
- action proposals may be visible, but execution is not authorized;
- tenant authority is server-owned;
- PostgreSQL RLS is an independent boundary;
- provider and TRACTIAN credentials stay server-side;
- raw sensitive provider/tool payloads and hidden reasoning are excluded from browser projections;
- no automatic paid provider fallback exists.

### Managed-session resilience contract

The current auth boundary is intentionally fail-closed **without making every dashboard read a mandatory remote identity round-trip**:

- browser contributes only the opaque managed-session cookie;
- GET/HEAD bursts may reuse a server-validated context for at most **2 seconds**;
- cache key is SHA-256 of the opaque cookie; the raw cookie is not stored in the cache;
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

## Disclosure and remediation

Do not weaken or bypass frozen evidence to hide a security failure. Preserve the failing evidence, fix prospectively, add regression coverage and update the active status/architecture/security model when the trusted boundary changes.

A security fix is not considered complete merely because a unit test passes; the applicable hosted/tenant/action/auth boundary must be revalidated before a production claim is restored.