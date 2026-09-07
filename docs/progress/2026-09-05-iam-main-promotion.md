# Production IAM Main-Promotion Checkpoint — 2026-09-05

**Branch:** `release/production-final`  
**PR:** `#196`  
**Master plan:** [`../DELIVERY-PLAN.md`](../DELIVERY-PLAN.md)

This checkpoint records only non-secret evidence. Database credentials and session secrets are deliberately excluded.

## 1. Regression gates before hosted promotion

The managed-session implementation was exercised before production Auth was enabled:

```text
production-runtime managed-session backend tests     PASS
frontend-provider-free                               PASS
full-product Chromium provider-free                  PASS
clean-clone full-product reproduction                PASS
horizontal runtime handoff                           PASS
action execution lease                               PASS
final-ci-required / required-gate                    PASS
```

The production frontend image forces browser authentication on while the provider-free Vite fixture keeps external IAM disabled. This preserves test determinism without weakening the production artifact.

## 2. Neon Auth promotion

Neon Auth / Better Auth was first exercised on the isolated migration-validation branch. After regression gates were green, it was provisioned on Neon production main (`br-calm-poetry-acsa9vbh`) against database `academy_tractian`.

The public `production-web` HTTPS origin was added to the production-main trusted-origin allowlist.

Current identity limitations are explicit:

- managed email/password sessions are enabled;
- email verification is not required by the current hosted configuration;
- therefore verified-email identity is **not** a product claim;
- Google appears as a managed shared provider but the application does not yet expose a Google-login flow.

## 3. Railway frontend promotion

`production-web` was switched from the validation Auth upstream to the production-main Auth upstream using non-secret service variables.

Latest observed state after this switch:

```text
production-web Railway status      SUCCESS
source branch                      release/production-final
region                             us-east4-eqdc4a
production browser auth            forced ON by Docker build
/auth upstream                     Neon Auth production main
/api upstream                      production-api.railway.internal:8000
SSE buffering                      disabled
```

## 4. Railway backend state

`production-api` is configured for `browser_iam_mode=neon-auth` and points to the production-main Neon Auth base URL.

Its current serving failure is intentionally fail-closed. Latest runtime logs report exactly these missing required variables:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

No runtime identity HMAC secret, issuer or audience is required by the selected managed-browser-session mode.

The two database DSNs must be inserted only through an approved Railway native secret channel. They must not be committed, documented, pasted into chat, or transferred through a connector that rejects cross-provider secret movement.

## 5. Architecture synchronization

`architecture_manifest.py` and its regression test were updated so the product-visible architecture now states:

- managed session is the current remote identity candidate;
- signed bearer is a compatibility/rollback input path;
- server-owned `AuthenticatedRuntimeContext` remains the output boundary;
- IAM remains not READY until live multi-user acceptance passes.

`ARCHITECTURE.md`, `ACTIVE-PROJECT-STATUS.md`, `DELIVERY-PLAN.md` and `decision-registry.yaml` were synchronized to the same truth.

## 6. Next dependency gate

```text
approved native Railway insertion of the two PostgreSQL DSNs
→ exact-SHA backend boot
→ /health + release identity + DB connectivity
→ restart/persistence
→ two-user/two-tenant authenticated REST/SSE negative acceptance
→ IAM capability decision
```

Provider selection and real TRACTIAN composition remain downstream and must not bypass this dependency gate.
