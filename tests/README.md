# Tests

`tests/` contains the backend product, regression and integration test surface.

Many historical tests intentionally remain at the directory root because exact paths can be referenced by workflows or evidence. Do not bulk-move them for aesthetics without a reference audit.

## Test layers

### Unit / contract tests

Use for deterministic logic such as:

- schemas and validation;
- decision boundaries;
- action safety;
- evaluator logic;
- storage contracts;
- identity verification.

### Integration tests

Use real PostgreSQL where persistence, RLS, leases, concurrency, recovery or cross-replica correctness are part of the claim.

Do not substitute an in-memory/local-file backend for a production claim that depends on PostgreSQL semantics.

### Product/API tests

Exercise FastAPI contracts through the same authenticated server-owned context used by the product path.

### Browser acceptance

Full browser E2E belongs in `frontend/e2e/` and is executed through Playwright.

## Rules for new tests

1. Every production bug fix gets a regression test.
2. Every material architectural challenger needs a baseline and explicit evaluation gate.
3. Safety and tenant-isolation tests are hard gates, not score-only metrics.
4. Avoid tests that pass only because they mock away the mechanism being claimed.
5. Keep fixtures deterministic and explicit about whether they are public, synthetic or frozen.
6. New test organization may use domain subdirectories when no frozen/path-pinned evidence depends on the exact location.
7. Do not weaken an existing assertion or threshold merely to make CI green; record and investigate the regression.

## Proposed organization for new tests

Without moving historical files, new tests may gradually use:

```text
tests/
  unit/
  integration/
  acceptance/
  fixtures/
```

Pytest discovers these recursively. Physical migration of existing tests should be a separate compatibility-checked refactor.
