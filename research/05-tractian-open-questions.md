# TRACTIAN / Inteli Open Questions

Status after receiving `inteli-tractian-project.zip` on 2026-08-15.

The package resolves most API/canonical-case questions. This file now records only questions that **cannot be safely answered from the supplied written/executable artifacts**, plus package inconsistencies that need explicit treatment.

See:

- `26-tractian-artifact-ingestion-wave-4.md`;
- `27-api-map-v0-wave-4.md`;
- `28-gold-map-v0-wave-4.md`;
- `29-contract-and-package-quality-audit-wave-4.md`.

## Resolved by supplied artifacts

### Scope / benchmark material

- Both agent construction and evaluation are mandatory.
- 17 agent-input cases are supplied.
- 16 richer narrative evaluation scenarios are supplied.
- Agent-visible material and evaluator-only gold material are explicitly separated.
- Reference trajectories are guidance/reference, **not mandatory scripts**.
- Cases contain explicit `company_id`, `user_id`, `asset_id` bindings.
- Evaluation material contains machine reference paths plus narrative policies/resolutions/P1/P2 criteria.

### API/runtime surface

- Local FastAPI implementation supplied.
- 18 runtime HTTP operations across 17 unique path templates.
- Synthetic resources/IDs/relationships are inspectable in source/data.
- User context/permissions exposed through `/users/me` and `x-user-id` binding.
- Action permission classes and justification behavior are inspectable.
- Accepted action calls are terminal successful execution events.
- Action handlers do not persist state changes in the supplied store.
- Response modes and fixed scenario overrides are inspectable.
- Explicit seed controls deterministic mode selection.
- No-seed mode behavior is also deterministic per resource/category in executable implementation.
- Knowledge corpus is supplied through five API-searchable documents.

### Reproducibility/state

- Synthetic data generation source is supplied.
- Base environment can be reconstructed from source/generator.
- Because actions do not persist mutations, base benchmark reset/snapshot is not required to restore action state between runs.
- Volatile action IDs still require normalization for replay/comparison.

## Remaining partner/instructor questions

### Evaluation packaging / grading

- Will instructors/TRACTIAN use **additional hidden evaluation cases** beyond the delivered package?
- Is any official score/weighting expected beyond the TAPI rubric and supplied P1/P2 scenario guidance?
- Is there a required minimum endpoint/scenario coverage for grading beyond what is written?
- Is live API execution required during the final presentation, or is a reproducible local run sufficient?

### Models / compute

- Are external commercial model APIs allowed for students without restriction?
- Are any model/provider credits or required endpoints supplied by the partner/Inteli?
- Are fully local/open models a preference, feasibility reference, or hard requirement?
- Are internet calls allowed in the final demo environment?

### Artifact publication

- May the raw partner ZIP, canonical cases, eval gold and generated synthetic data be committed to a **public** GitHub repository?
- If not, may derived normalized scenario oracles be public if they reveal expected resolutions/reference paths?
- Are any synthetic fields still expected to be redacted from public traces/artifacts?

Until answered, preserve hashes/derived research findings but do not publish the raw package/eval gold to the public branch.

### Confirmation policy

Kickoff guidance described requester confirmation for state-changing operations, but the delivered canonical execution scenarios do not model a universal confirmation turn before action.

Question:

- Should confirmation be considered an official canonical requirement for any supplied action, or should it remain a project-authored safety extension/experiment?

Current treatment: **experimental guarded variant, not canonical benchmark hard rule**.

## Package inconsistencies that do not require guessing

These are already documented and should be handled through normalization/conformance rather than silently fixed:

- duplicate `/assets/{assetId}` YAML key causes naïve parse loss of GET vs PATCH;
- written analysis count (24 in some docs) differs from supplied generator count (10);
- raw OpenAPI response schemas are weaker than executable payload semantics;
- documentation says omitted seed samples distribution, while implementation hashes `noseed|resource|category` deterministically;
- eval `mode` mixes API response modes with scenario labels such as `pending`/`stale`;
- some prose role descriptions differ from seeded case users;
- machine expected paths omit evidence/actions present in narrative scenarios;
- referenced evaluation helper artifacts are not all present in ZIP.

## Questions now answered by our own experiments rather than partner clarification

These should **not** be sent to TRACTIAN as requirements questions; they are research questions for this project:

- best runtime among finalists;
- native tools vs MCP adapter;
- value of strict typed validation;
- value of deterministic company/resource policy guard;
- evidence/stopping strategy;
- best model configuration;
- need for external RAG;
- need for multi-agent decomposition;
- value of routing/prompt optimization;
- final repetition count `k` / statistical precision.

## Next decision boundary

Before `FROZEN-v1` we still need to:

1. normalize/conformance-test the OpenAPI contract;
2. human-review ScenarioSchema v1 oracles from machine + narrative gold;
3. freeze leakage-aware benchmark groups/splits;
4. run guarded-boundary experiment;
5. run runtime/MCP/model discriminating experiments;
6. run statistical pilot;
7. close ADRs.
