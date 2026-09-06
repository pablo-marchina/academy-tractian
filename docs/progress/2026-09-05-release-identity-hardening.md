# Release Identity Hardening — 2026-09-05

**Branch:** `release/production-final`  
**PR:** `#196`  
**Plan workstream:** P0-C / remote backend boot prerequisite  
**Validation state:** IMPLEMENTED / REQUIRED CI PENDING

No secret or credential value is recorded in this evidence note.

## 1. Risk closed in source

Before this change, `ACADEMY_RELEASE_GIT_SHA` was validated as a 40-character SHA but remained a mutable runtime value. The Docker artifact also accepted an independent release build argument. Therefore the public `/api/meta/release` response could not by itself prove that the claimed source SHA was the commit actually baked into the serving image.

The new contract treats the built artifact as an independent identity source and fails closed on disagreement.

## 2. Artifact identity contract

The production Dockerfile now consumes Railway's Git-backed build identity through:

```text
RAILWAY_GIT_COMMIT_SHA
```

The build rejects a missing or malformed SHA and writes an immutable runtime file:

```text
/app/.academy-release-identity.json
schema_version = academy-release-artifact-v1
git_sha        = exact 40-character lowercase build SHA
```

The same SHA is written to the OCI `org.opencontainers.image.revision` label. The file is read-only in the non-root runtime image.

## 3. Boot-time verification

`academy_tractian.release_identity` validates the baked file with a frozen, extra-forbidden schema.

Before any PostgreSQL/IAM product builder is invoked, remote production now requires:

```text
configured ACADEMY_RELEASE_GIT_SHA == baked artifact git_sha
```

When Railway also exposes `RAILWAY_GIT_COMMIT_SHA` at runtime, it must independently equal the baked artifact SHA.

Any absence, corruption, invalid SHA, unexpected field, or mismatch aborts production boot. Runtime environment cannot manufacture or override the baked artifact identity.

## 4. Public release metadata

A valid `/api/meta/release` is upgraded to `remote-production-release-v3` and includes only safe identity evidence:

```text
release_git_sha
artifact_git_sha
artifact_identity_schema_version
artifact_identity_verified
railway_runtime_identity_verified
```

Hosted acceptance must prove `release_git_sha == artifact_git_sha == expected deployed commit` before G2 can pass.

## 5. Regression evidence added

The source test suite now covers:

- missing baked identity;
- invalid JSON;
- missing/uppercase/malformed SHA;
- unexpected identity fields;
- frozen identity mutation;
- configured SHA vs artifact mismatch;
- Railway runtime SHA vs artifact mismatch;
- verification before the product/database delegate is invoked.

The existing `production-runtime` workflow now additionally proves:

- Docker build from exact `GITHUB_SHA` via `RAILWAY_GIT_COMMIT_SHA`;
- baked file equals OCI revision label;
- malformed source identity prevents image construction;
- configured/artifact mismatch prevents serving boot before connection attempts;
- non-root and production-only dependency contracts remain intact.

`production-runtime` is now a reusable job consumed directly by `final-ci-required`; therefore release artifact identity is part of `required-gate` rather than an advisory workflow.

## 6. Non-claims

This checkpoint does **not** claim:

- the new image is already deployed on Railway;
- remote `/api/meta/release` v3 has been observed;
- production-api has booted;
- live IAM is ready;
- a provider is selected;
- TRACTIAN is composed.

The two PostgreSQL DSNs remain the external G2 blocker. CI for the complete documented head must be green before this source-level gate is marked PASS.

## 7. Next gates

```text
required CI for complete head
→ offline IAM negative-gap audit
→ user supplies two Railway Postgres DSNs
→ exact-SHA Railway deployment
→ /health + /api/meta/release v3 + DB role/store evidence
→ restart/persistence
→ live IAM/two-tenant acceptance
```
