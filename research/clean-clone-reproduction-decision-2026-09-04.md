# Clean-clone full product reproduction — 2026-09-04

## Decision

Promote a **new** provider-free clean-checkout workflow for the current product while preserving the historical final-delivery reproduction workflow byte-for-byte.

The historical `.github/workflows/final-delivery-provider-free-reproduction.yml` starts from a clean GitHub checkout, but it predates the promoted PostgreSQL/identity/load/recovery/frontend closure. Its exact Git blob is referenced by the frozen delivery evidence index.

An initial attempt to extend that file was correctly rejected by the frozen-reproduction tests because changing its blob would rewrite accepted historical evidence. The freeze is therefore preserved; its expected hash is **not** updated.

The current-product gap is closed by:

`.github/workflows/clean-clone-full-product-reproduction.yml`

## Reproduction contract

From one `actions/checkout` with tracked state verified clean:

1. start PostgreSQL 18;
2. install Python production/dev + E2 dependencies;
3. execute the complete `tests` suite with `POSTGRES_OPERATIONAL_TEST_DSN` present;
4. explicitly execute the promoted authenticated Postgres/RLS test, load/concurrency campaign and restart/recovery campaign;
5. regress ADR-004 controller tests;
6. reproduce frozen EV-007 / EV-008 / EV-011;
7. validate the historical final delivery demo + evidence index, including the unchanged frozen workflow blob;
8. validate final handoff audit;
9. install frontend strictly from committed `package-lock.json` via `npm ci`;
10. run TypeScript typecheck, Vitest and Vite production build;
11. require zero tracked repository diff after reproduction.

## Why a new workflow is required

The delivery freeze is an evidence artifact, not a mutable pointer to whatever workflow happens to be current. Updating its expected blob to accept new content would erase the distinction between historical evidence and present architecture.

The project therefore keeps both contracts:

- **historical frozen reproduction:** immutable evidence for the accepted delivery freeze;
- **current clean-clone reproduction:** evolving P0 gate for the product that exists now.

This is consistent with the repository rule that historical evidence is never rewritten merely to align a later narrative or architecture.

## Browser boundary

`full-product-playwright` remains a separate mandatory workflow. It already starts a real provider-free backend/frontend/Postgres stack and executes Chromium acceptance. Installing Chromium again inside the clean-clone workflow would duplicate a high-cost gate without adding a distinct reproducibility claim.

Therefore:

- current clean-clone workflow proves deterministic install/test/build/evidence reproduction;
- Playwright workflow proves full-browser execution behavior.

Both must be green on the final SHA.

## Provider / customer-data boundary

The clean-clone workflow requires no provider credentials, no live provider calls and no real-customer mutations.

PostgreSQL contains only ephemeral CI fixture state. Identity tokens used by integration tests are synthetic and locally signed for the test process. No production bearer token, signing secret, account identifier or raw provider material is required.

## Evidence boundary

Frozen experiment identities and frozen workflow blobs are not updated to match code changes. A mismatch fails reproduction and must be diagnosed.

Load/concurrency and restart/recovery campaigns remain bounded by their own claim contracts:

- load CI data is descriptive and not production capacity;
- restart CI data proves conservative persisted-state semantics and not RTO/RPO/availability.

Human-dependent semantic-calibration and engineer-time business claims are not synthesized by reproduction.

## Repository cleanliness

The workflow checks tracked repository state before and after reproduction. Generated caches, build output and temporary runtime artifacts may be untracked/ignored, but no tracked source, documentation or frozen evidence file may be rewritten by reproduction commands.

This protects against tests/scripts silently regenerating accepted evidence in-place.

## Promotion rule

This P0 is closed only after the **new current-product workflow** and all other applicable exact-head workflows pass on the PR SHA. A passing historical reproduction run is necessary for freeze integrity but is not sufficient for current-product reproducibility.