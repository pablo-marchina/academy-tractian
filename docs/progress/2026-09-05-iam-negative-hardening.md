# Managed Session IAM Negative Hardening — 2026-09-05

**Branch:** `release/production-final`  
**PR:** `#196`  
**Plan workstream:** P0-D preparation while G2 is externally blocked  
**Validation state:** IMPLEMENTED / REQUIRED CI PENDING

This work does not promote live IAM readiness. Hosted two-user/two-tenant acceptance remains mandatory after the production backend can boot.

## 1. Audit finding

The managed Neon Auth context provider already rejected missing, expired, mismatched and impersonated sessions and ignored browser-owned tenant/role authority. During the negative-boundary audit, one additional transport risk was identified:

```text
urllib default HTTP redirect handling
+ server-forwarded opaque session cookie
→ possible cookie forwarding outside the configured auth endpoint after redirect
```

This is unnecessary for session revalidation and violates the fail-closed credential boundary.

## 2. Hardening implemented

The managed-session fetch now installs an explicit no-redirect handler. A 3xx response is returned to the context provider as a non-200 auth response and becomes `managed_session_unavailable`; the client never follows the redirect with the session cookie.

Server-verified managed identifiers are also bounded before they become runtime authority:

```text
user id                    required, trimmed exactly, <= 256 UTF-8 bytes, no control chars
session user id            same contract + must exactly equal user id
active organization id     same contract when present
```

This prevents malformed or resource-amplifying identity values from reaching tenant/identity storage boundaries.

## 3. Negative regression coverage

The IAM test surface now covers:

- browser `organization`, `user`, `role` and `permissions` headers cannot change trusted context;
- missing cookie fails before the auth service is called;
- duplicate cookie headers fail before auth service use;
- oversized cookie fails before auth service use;
- user/session mismatch fails closed;
- impersonated session fails closed;
- whitespace/control/oversized managed IDs fail closed;
- invalid organization shape fails closed;
- malformed or oversized auth response fails closed;
- 401/403 session rejection maps to invalid session;
- auth service failure maps to unavailable session;
- redirect handling is explicitly disabled;
- redirect response is never accepted as a valid session;
- auth base URL remains remote HTTPS without embedded credentials.

## 4. Existing downstream boundaries retained

Existing product regressions already cover run-level cross-user isolation, cross-organization isolation, SSE denial, query denial, global-capability denial, payload scope-injection rejection, and PostgreSQL RLS with a NOBYPASSRLS scoped role.

This change does not alter runtime permissions or grant any new production authority.

## 5. Non-claims

Do not claim from this checkpoint alone:

- live Neon Auth end-to-end PASS;
- same-organization multi-user acceptance;
- production tenant isolation PASS;
- CSRF/origin/session-invalidation acceptance;
- production actions authorized;
- IAM READY.

All of those remain gated by G2/G3 remote evidence.
