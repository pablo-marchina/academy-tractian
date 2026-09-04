# Semantic review UI + VALIDATION source generation decision — 2026-09-03

## Decision

Add the missing bridge between persisted production-safe run outputs and the authenticated human semantic-review collector:

`frozen safe-run selection -> safe DuckDB read model -> VALIDATION-only SemanticAnnotationSource -> blind reviewer packet -> authenticated reviewer UI -> PostgreSQL labels/adjudication`

This slice does **not** create real human labels, a calibrated judge, acceptance thresholds, or a business/quality claim.

## Trusted source boundary

Held-out semantic source generation reads only the existing `ObservabilityStore` browser-safe DuckDB projection. It does not accept `RunTrace`, raw provider responses, raw prompts, chain of thought, credentials, private truth, gold labels, or judge output.

For each selected safe run, the materializer requires:

- the exact safe run ID to be present in a `FROZEN` source-selection artifact;
- the benchmark split manifest itself to be `FROZEN`;
- the persisted scenario to belong to `VALIDATION`;
- the run to be complete;
- non-empty terminal decision, response mode and customer-safe terminal message;
- at most one selected run per scenario.

DEV and LOCKED_TEST scenarios fail closed. Missing, incomplete, duplicate-scenario or terminal-incomplete runs also fail closed.

## Source selection and integrity

`SemanticSourceSelection` binds the exact ordered safe run IDs to a SHA-256 digest. `SemanticAnnotationSourceManifest` then binds:

- frozen split schema/hash;
- frozen source-selection hash;
- safe run ID;
- scenario ID;
- terminal-output hash;
- sanitized-context hash.

These hashes prove content integrity and deterministic binding. They do **not** provide an external trusted timestamp proving when the selection was frozen. Operationally, the selection artifact must therefore be frozen before reviewers see outcomes and retained with the experiment evidence bundle; the code does not overclaim cryptographic preregistration time.

## Sanitized evidence context

The source builder derives reviewer context only from the persisted safe evidence-reference table. Each entry is represented as the bounded factual reference:

`Evidence <id>: tool=<safe tool name>; status=<safe status>.`

No raw tool body is reconstructed. Existing `SemanticAnnotationSource` validation remains the final fail-closed check for forbidden evaluator/runtime material markers.

## Browser minimization

The canonical evaluator-side `SemanticReviewerTask` contains scenario identity and output/context hashes because they are needed for integrity and resolution. The browser does not need those fields.

The reviewer API now projects a smaller `SemanticReviewerTaskSafe` containing only:

- opaque task ID;
- response mode;
- semantic dimension;
- terminal decision/message;
- sanitized evidence context;
- criterion description;
- score 0/1/2 anchors.

The browser therefore does not receive scenario ID, output hash, context hash, source split/group, reviewer slot, phase/adjudication marker, previous labels, reviewer identity, private truth, gold data, raw provider material, or chain of thought.

## Reviewer interaction

The in-product reviewer surface preserves the collection protocol:

- merely opening the product does not allocate a semantic task;
- the reviewer explicitly requests a blinded task;
- score 0/1 requires one or more structured defect reasons;
- score 2 maps to exactly `NO_MATERIAL_DEFECT`;
- completion submits only score + reason codes;
- withdrawal creates no semantic label;
- completion feedback contains no score, agreement, adjudication state, gold value, or evaluator feedback;
- the UI never tells the reviewer whether the assignment is A, B, or adjudication.

## Acceptance fixture

`ACADEMY_E2E_SEMANTIC_REVIEW=1` enables a synthetic, provider-free VALIDATION packet for full-product browser acceptance only. The fixture proves authenticated allocation, browser minimization, canonical submission, withdrawal, persistence and responsive rendering through the real production API/store topology.

The fixture is not project calibration evidence and must never be exported as real human evidence. It is disabled unless the explicit E2E flag is set.

## Evidence status after this slice

Infrastructure status: ready to materialize real sanitized VALIDATION sources and collect authenticated blind human labels once eligible runs and reviewers exist.

Evidence status: **NO REAL HUMAN LABELS COLLECTED; NO CALIBRATION CLAIM; NO BUSINESS CLAIM.**

The next evidence-producing step is human work: freeze an eligible real VALIDATION safe-run selection before review outcomes, materialize the packet, assign independent reviewers, adjudicate disagreements, and only then feed the resulting human references into the already-frozen v2 semantic calibration gate.