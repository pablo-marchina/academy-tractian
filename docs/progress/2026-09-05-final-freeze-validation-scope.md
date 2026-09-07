# Final Freeze Validation Scope — 2026-09-05

**Branch:** `release/production-final`  
**PR:** `#196`  
**Plan workstream:** evidence integrity / clean-clone required gate  
**Validation state:** IMPLEMENTED / REQUIRED CI PENDING

## 1. Failure observed

The clean-clone required workflow failed only on:

```text
FINAL_FREEZE_FAILURES=artifact_0_blob_mismatch
```

The registered artifact was `.github/workflows/final-ci-required.yml` inside the dated `2026-09-04` freeze candidate. Its recorded blob is historical. The workflow legitimately evolved afterward to add the Railway IaC and immutable production-runtime/release-identity gates.

All functional Python, controller, PostgreSQL, reproduction and historical evaluation checks in that job passed before the freeze validation step.

## 2. Invalid fix rejected

The historical manifest is **not** re-pinned to the new workflow blob. Rewriting its recorded hash would destroy the meaning of the dated evidence snapshot and make an old freeze appear to have contained future code.

Disabling freeze validation entirely is also rejected.

## 3. Validation model

`validate_final_freeze_manifest` now exposes two explicit scopes:

```text
current-head
historical-snapshot
```

### `current-head`

Used for a prospective/current hard freeze. Every registered artifact must still exist and its current Git blob must exactly equal the manifest. Any drift fails closed.

### `historical-snapshot`

Used only to validate the dated `2026-09-04` bundle after legitimate repository evolution.

It still validates:

- manifest SHA-256;
- schema and fixed bundle dates/state;
- artifact path safety and existence;
- decision set/statuses;
- registered evidence references;
- required non-claims;
- truthful `branch_protection_enforced=false`;
- byte identity for artifacts explicitly marked `frozen_historical_evidence`.

Artifacts whose role was explicitly `current_ci`, `current_contract`, `current_decision` or `current_reproduction` remain historically hash-recorded inside the hash-bound manifest, but are not required to equal a later worktree.

## 4. Regression contract

Tests now require:

```text
current-head + any artifact drift                 → FAIL
historical-snapshot + current-role evolution      → PASS
historical-snapshot + frozen evidence tamper      → FAIL
historical-snapshot + missing registered artifact → FAIL
manifest hash tamper                              → FAIL
```

The existing `scripts/validate_final_freeze_bundle.py` explicitly declares `HISTORICAL_SNAPSHOT` in its output. A future final freeze must use strict `current-head` validation rather than inheriting the historical scope implicitly.

## 5. Evidence preservation

`research/results/final-freeze-evidence-bundle-2026-09-04.json` was not changed by this correction.

## 6. Non-claims

This does not declare a new final freeze, final production readiness, branch protection enforcement or release completion. The current complete head still requires a green `final-ci-required / required-gate` before this correction is accepted as source-level evidence.
