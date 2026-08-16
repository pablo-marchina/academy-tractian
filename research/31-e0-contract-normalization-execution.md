# E0 — Contract Normalization & Conformance Execution

Status: **IN PROGRESS — normalized candidate generated; semantic divergences classified; not frozen**

Date: **2026-08-16**

## Objective

Produce a trustworthy project contract from the supplied TRACTIAN OpenAPI without mutating the partner artifact or silently accepting parser loss.

E0 is deliberately separate from Canonical ToolSpec generation. The HTTP contract must be audited first; model-facing tool semantics are derived later.

## Reproducible pipeline

Implemented:

- `scripts/research/e0_contract_pipeline.py`

The script:

1. reads the immutable partner YAML;
2. detects duplicate YAML mapping keys before ordinary parsing;
3. merges only duplicate mappings whose child keys are disjoint;
4. emits a private normalized candidate + manifest/hash;
5. extracts FastAPI runtime `/openapi.json` without changing partner source;
6. compares structural operations/parameters/request schemas/response codes;
7. executes source-faithful semantic probes through the supplied FastAPI handlers;
8. emits a private conformance report.

Generated normalized/runtime reports remain local/private until partner artifact-publication policy is clarified.

## Source and candidate hashes

Current local execution:

- raw `docs/api-contract.openapi.yaml` SHA-256: `8b3fdc5da50a8fa2923928a2f5aebcfe5034c622dba222df84f56abcd0b4aabf`
- normalized candidate SHA-256: `c15c44ac84f77a6efe0fe1a4ed1e35f02dcf24d72d66b04bb028b5cb67cb958c`
- FastAPI-generated runtime OpenAPI SHA-256: recorded by the E0 manifest for each execution.

The partner ZIP itself remains immutable and is not committed publicly.

## E0.1 — Duplicate-key result

The raw YAML contains a duplicate path mapping:

- first `/assets/{assetId}` occurrence at line 331;
- second occurrence at line 348;
- one contains GET and one contains PATCH.

The duplicate-aware loader classifies this as:

`MERGED_DISJOINT_MAPPING`

because the two path objects have non-overlapping HTTP method keys.

No general "last key wins" behavior is allowed. Any duplicate with overlapping child keys causes the pipeline to fail instead of guessing.

## E0.2 — Structural runtime conformance

After only the lossless duplicate merge:

- normalized operations: **18**;
- normalized unique path templates: **17**;
- runtime operations: **18**;
- runtime unique path templates: **17**;
- canonical method + route-shape set: **exact match**.

This confirms the duplicate path is the reason a naïve YAML parse can lose one of the runtime operations.

## E0.3 — Declared-contract vs runtime differences

Structural route coverage matches, but the hand-written contract and FastAPI-generated contract are not semantically identical.

### Path/parameter naming

The partner contract uses camelCase path parameter names such as `assetId`, while FastAPI generates snake_case names such as `asset_id`.

This does not change HTTP route identity, but it matters for generated client/tool argument names and must be normalized intentionally rather than accidentally.

### Action request schemas

All five action operations are more strictly described in the hand-written contract than in the executable FastAPI signature.

The runtime handlers accept `dict[str, Any]`, so generated runtime OpenAPI exposes an open object. The hand-written contract instead declares `ActionRequest` and, for asset PATCH, the `criticality` enum/config structure.

This is an intentional research surface, not a reason to weaken the normalized contract to the runtime's permissive schema.

### Response-code declarations

FastAPI-generated OpenAPI adds framework validation responses such as 422 that are not consistently present in the hand-written contract. Conversely, some hand-written error semantics are enforced manually at runtime rather than represented precisely in generated OpenAPI.

The conformance manifest therefore records response-code differences instead of pretending the two descriptions are identical.

### Authentication/security representation

The raw contract has a global `UserContext` security declaration. Executable behavior is more nuanced:

- ordinary read endpoints can be called without `x-user-id`;
- `/users/me` rejects a missing user context;
- all five action endpoints reject a missing user context;
- action permission is then checked against the bound synthetic user.

FastAPI models the dependency as a header parameter rather than a true OpenAPI security scheme, and the generated schema does not express the manual 401 behavior perfectly.

Therefore **raw OpenAPI security metadata, generated OpenAPI security representation and executable authorization behavior are three distinct evidence surfaces**.

## E0.4 — Runtime semantic probes

The E0 pipeline reproduced the important package-level behaviors against unchanged handlers using the same seeded source records at the store boundary.

Confirmed again:

1. read endpoints tested are callable without user context, except `/users/me`;
2. all five action classes return 401 without `x-user-id` and accept the intended authorized user;
3. asset PATCH accepts an invalid criticality value if the justification passes;
4. asset PATCH accepts a body with no `changes` field;
5. asset PATCH accepts arbitrary extra fields;
6. a high-permission user from one company can target an asset belonging to another company in the simplified backend;
7. an accepted asset update does not persist to the seeded store;
8. repeated unseeded calls to the same resource/category are deterministic;
9. fixed scenario overrides beat `seed=complete`.

These are executable observations. They do not imply that TRACTIAN intends such behavior in production; they define the supplied challenge environment that our benchmark must handle correctly.

## Normalization policy candidate

Do **not** make the normalized contract a silent rewrite of either source.

Proposed separation:

### A. `RAW-CONTRACT`

Immutable partner YAML + hash.

### B. `NORMALIZED-CONTRACT-v1`

Lossless/explicit transformation of the intended partner contract:

- merge duplicate disjoint path mapping;
- preserve stronger declared action schemas;
- preserve operation IDs/tags/descriptions;
- normalize naming only through an explicit transformation manifest;
- never weaken a declared safety/domain constraint merely because the simplified runtime is permissive.

### C. `API-BEHAVIOR-MAP-v1`

Executable observations that differ from the declared contract:

- actual auth behavior;
- actual action permissiveness;
- accepted-event/non-persistent semantics;
- deterministic seed behavior;
- backend company/resource behavior;
- response-mode degradation details.

### D. Canonical ToolSpec

Built later from **B + C + reviewed scenario policy**, with evaluator-bound identity/seed removed from model control.

This separation avoids conflating "what the partner contract says", "what the simplified implementation does" and "what the safe agent interface should expose".

## E0 exit conditions

Before marking E0 complete / freezing `NORMALIZED-CONTRACT-v1`:

- [x] raw contract hash recorded;
- [x] duplicate-key-aware loader implemented;
- [x] duplicate GET/PATCH path merged losslessly;
- [x] all 18 runtime operations structurally accounted for;
- [x] semantic probe suite implemented and executed;
- [x] declared-vs-runtime divergences classified;
- [ ] freeze exact parameter naming transformation policy;
- [ ] emit final transformation manifest with no unresolved silent changes;
- [ ] run final normalized-contract structural/schema validation in the project environment;
- [ ] produce `API-BEHAVIOR-MAP-v1` machine-readable metadata consumed by ToolSpec generation;
- [ ] freeze `NORMALIZED-CONTRACT-v1` hash.

E0 is therefore **substantially advanced but intentionally not declared complete yet**.
