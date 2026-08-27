# E14o postprocess diagnostic note — E14n v1 placeholder over-transform

Date: 2026-08-19

The single real E14o generation completed successfully with 6/6 parsed outputs and no retries or repairs. The generation itself remains valid and must not be rerun.

The first provider-free E14n v1 postprocess returned `TRANSFORM_NEEDS_REVIEW` with aggregate-only metadata:

```text
fixed / parsed / assessed:                   6 / 6 / 6
unsupported identifier mentions before:      1
unsupported identifier replacements:         3
unsupported identifier mentions after:       0
decision/action/escalation semantic changes: 0
```

Public code inspection identified a deterministic guard bug: the surface auditor removes `{...}` placeholders before concrete-ID matching, but E14n v1 matched namespaced IDs directly inside brace placeholders. Therefore valid public placeholders whose inner token is absent from the visible case could be rewritten even though they are excluded from provenance auditing.

Consequences:

- The E14o real generation is retained as the fixed capture.
- The E14n v1 guarded E14o output is diagnostic-only and is not valid for candidate selection.
- The surface audit, E9 v4.1 measurement, and E9 v4.2 claim packet produced from that E14n v1 transformed output are also diagnostic-only and must not be used for selection.
- No provider call is rerun.
- Only provider-free postprocessing may be repeated after the preregistered E14n v1.1 bugfix passes structural CI.

`research/experiments/e14n-v1-1-placeholder-preservation-amendment.json` preregistered the bugfix before implementation. Structural CI run `32260343772` passed, including a synthetic regression that preserves existing brace placeholders byte-for-byte while still replacing unsupported concrete identifiers.

No raw outputs, identifiers, per-call results, hashes, private expected paths, scorer rows, VALIDATION feedback, or LOCKED_TEST material are recorded here.
