# Security Policy

Security issues in this repository should be handled as vulnerabilities, not as ordinary public bug reports when disclosure could increase risk.

## Supported product state

The actively supported security target is the current Release 0 production path documented in [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md). Historical research branches, frozen experiment artifacts and provider-free test profiles are retained for provenance but are not production serving targets.

## Reporting a vulnerability

Prefer GitHub **private vulnerability reporting / Security Advisories** when it is available for this repository. Do not post exploit details, secrets, cross-tenant data, credentials, session material or a working attack path in a public issue.

If private GitHub reporting is unavailable, contact the repository owner through an already-established private channel and include only a minimal public reference if coordination requires one.

A useful report contains:

- affected path/component;
- impact and preconditions;
- safe reproduction steps;
- whether the issue crosses tenant/auth/policy boundaries;
- observed versus expected behavior;
- suggested mitigation when known;
- no real secrets or unrelated personal/customer data.

## High-priority classes

Treat these as P0 until triaged:

- authentication/session bypass;
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

See [`docs/SECURITY-MODEL.md`](docs/SECURITY-MODEL.md) for active trust boundaries, threats, mitigations and remaining non-claims.

## Disclosure and remediation

Do not weaken or bypass frozen evidence to hide a security failure. Preserve the failing evidence, fix prospectively, add regression coverage and update the active status/architecture/security model when the trusted boundary changes.

A security fix is not considered complete merely because a unit test passes; the applicable hosted/tenant/action boundary must be revalidated before a production claim is restored.