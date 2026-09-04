# Clean-clone full product reproduction — 2026-09-04

## Decision

Promote one provider-free clean-checkout reproduction workflow as the final repository-level reproducibility gate.

The previous `final-delivery-provider-free-reproduction` workflow did start from a clean GitHub checkout, but it had no PostgreSQL service. Consequently, PostgreSQL-gated integration tests could be skipped in that workflow even though separate Postgres workflows were green. It also did not reproduce the locked frontend installation/build in the same clean checkout.

The updated workflow closes that gap without duplicating the full Chromium acceptance campaign.

## Reproduction contract

From one `actions/checkout` with tracked state verified clean:

1. start PostgreSQL 18;
2. install Python production/dev + E2 dependencies;
3. execute the complete `tests` suite with `POSTGRES_OPERATIONAL_TEST_DSN` present;
4. explicitly execute the promoted authenticated Postgres/RLS test, load/concurrency campaign and restart/recovery campaign;
5. regress ADR-004 controller tests;
6. reproduce frozen EV-007 / EV-008 / EV-011;
7. validate final delivery demo + evidence index;
8. validate final handoff audit;
9. install frontend strictly from committed `package-lock.json` via `npm ci`;
10. run TypeScript typecheck, Vitest and Vite production build;
11. require zero tracked repository diff after the reproduction.

## Browser boundary

`full-product-playwright` remains a separate mandatory workflow. It already starts a real provider-free backend/frontend/Postgres stack and executes Chromium acceptance. Installing Chromium again inside the clean-clone workflow would duplicate a high-cost gate without adding a distinct reproducibility claim.

Therefore:

- clean-clone workflow proves deterministic install/test/build/evidence reproduction;
- Playwright workflow proves full-browser execution behavior.

Both must be green on the final SHA.

## Provider / customer-data boundary

The clean-clone workflow requires no provider credentials, no live provider calls and no real-customer mutations.

PostgreSQL contains only ephemeral CI fixture state. Identity tokens used by integration tests are synthetic and locally signed for the test process. No production bearer token, signing secret, account identifier or raw provider material is required.

## Evidence boundary

Frozen experiment identities are not updated to match code changes. A mismatch fails the reproduction and must be diagnosed.

Load/concurrency and restart/recovery campaigns remain bounded by their own claim contracts:

- load CI data is descriptive and not production capacity;
- restart CI data proves conservative persisted-state semantics and not RTO/RPO/availability.

Human-dependent semantic-calibration and engineer-time business claims are not synthesized by reproduction.

## Repository cleanliness

The workflow checks tracked repository state before and after reproduction. Generated caches, build output and temporary runtime artifacts may be untracked/ignored, but no tracked source, documentation or frozen evidence file may be rewritten by the reproduction commands.

This specifically protects against tests/scripts that silently regenerate accepted evidence in-place.

## Promotion rule

This P0 is closed only after the updated workflow and all other applicable exact-head workflows pass on the PR SHA. A passing older reproduction run is not sufficient.