# E0 — `NORMALIZED-CONTRACT-v1` Freeze

**Status:** FROZEN  
**Date:** 2026-08-16  
**Purpose:** freeze the contract boundary required by E2 without publishing the partner artifact itself.

## Evidence basis

- Raw partner OpenAPI SHA-256: `8b3fdc5da50a8fa2923928a2f5aebcfe5034c622dba222df84f56abcd0b4aabf`
- Lossless normalized candidate SHA-256: `c15c44ac84f77a6efe0fe1a4ed1e35f02dcf24d72d66b04bb028b5cb67cb958c`
- FastAPI runtime OpenAPI SHA-256: `1110f1b3cf360489c18fbfe22bd65a5c0e10c24e260fec1dbd133d02c9344033`
- Normalized contract: **18 operations / 17 unique path templates**.
- Canonical method + route-shape comparison with runtime: **18/18 match** after explicit path-parameter normalization.

## Frozen transformation policy

1. Raw partner YAML remains immutable.
2. Duplicate `/assets/{assetId}` path mappings are merged only because their child HTTP-method keys are disjoint (`GET` + `PATCH`).
3. Any future overlapping/non-mergeable duplicate mapping is a hard error; no last-key-wins behavior is permitted.
4. HTTP path identity is normalized independently from parameter spelling.
5. Model-facing canonical argument names use `snake_case` while the HTTP adapter preserves the partner boundary spelling (`companyId`, `assetId`, `analysisId`, `modelId`, `docId`, `caseId`).
6. `seed` is an evaluation/runtime control and is runner-bound; it is not a model-controlled semantic argument.
7. `x-user-id` is runner-bound identity context; it is not a model-controlled argument.
8. Stronger declared action schemas are preserved even where the simplified runtime handler accepts a generic object.
9. Declared contract, executable behavior and safe model-facing policy remain separate evidence layers.

## Frozen executable behavior facts

The supplied environment was probed independently at the store boundary and confirms:

- actions require a valid `x-user-id` and the corresponding coarse permission;
- action bodies require a justification according to the supplied handler;
- action handlers accept semantically weak/incomplete payloads beyond the declared contract;
- cross-company targeting is not enforced by the simplified backend's coarse permission check;
- accepted action events do not persist the underlying seeded store mutation;
- repeated unseeded reads are deterministic for the same resource/category;
- fixed scenario overrides take precedence over `seed=complete`.

These are **challenge-environment observations**, not claims about TRACTIAN production behavior.

## Frozen boundary

`NORMALIZED-CONTRACT-v1` is now the input contract for Canonical ToolSpec generation. `API-BEHAVIOR-MAP-v1` remains a separate behavioral evidence layer consumed by guards/evaluators.

The private normalized OpenAPI is intentionally not committed because the partner artifact publication policy is unresolved.

## Exit checklist

- [x] duplicate-aware parsing
- [x] lossless duplicate merge
- [x] raw/normalized/runtime hashes
- [x] 18-operation structural conformance
- [x] explicit naming transformation policy
- [x] semantic divergence classification
- [x] machine-readable freeze manifest
- [x] no unresolved silent transformation

**E0 is frozen.** Changes require a new contract version and an explicit ADR rather than editing this freeze retroactively.
