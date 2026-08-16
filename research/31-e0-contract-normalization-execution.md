# E0 — Contract Normalization & Conformance Execution

**Status: FROZEN**  
**Date:** 2026-08-16

## Result

E0 produced `NORMALIZED-CONTRACT-v1` and froze the contract boundary for E2.

Evidence:

- raw OpenAPI SHA-256: `8b3fdc5da50a8fa2923928a2f5aebcfe5034c622dba222df84f56abcd0b4aabf`;
- normalized candidate SHA-256: `c15c44ac84f77a6efe0fe1a4ed1e35f02dcf24d72d66b04bb028b5cb67cb958c`;
- FastAPI runtime OpenAPI SHA-256: `1110f1b3cf360489c18fbfe22bd65a5c0e10c24e260fec1dbd133d02c9344033`;
- 18 operations / 17 unique path templates;
- canonical method + route-shape surface: 18/18 match after explicit parameter-name normalization.

## Frozen decisions

- duplicate `/assets/{assetId}` GET/PATCH mapping is merged only because child method keys are disjoint;
- overlapping/non-mergeable duplicate mappings are hard errors;
- canonical model-facing path arguments use snake_case while the HTTP adapter preserves partner spelling;
- `x-user-id` and `seed` are runner-bound;
- declared action schemas are not weakened because the simplified runtime accepts generic objects;
- declared contract, runtime behavior and safe agent policy remain separate evidence layers.

## Controlled behavior probes

The supplied implementation was probed independently at the store boundary. Confirmed behaviors include action authentication/permission checks, weak action payload validation, cross-company targeting permissiveness, accepted-but-non-persistent actions and deterministic seeded behavior.

These are challenge-environment observations, not production claims.

## Exit

All E0 exit conditions are satisfied. The machine-readable freeze manifest and behavior map are in `research/frozen/`.

**Any material contract change requires a new contract version and explicit ADR.**
