# Academy × TRACTIAN

This repository contains the governed research, evaluation and production-path implementation for the Academy × TRACTIAN individual project.

## Current state

The canonical current project state and authorization boundary are documented in [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md). Do not infer authorization from the presence of code, historical branches or experiment artifacts.

## Development

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before changing experiment semantics, evaluation, runtime behavior, production architecture or canonical project state.

The repository currently separates:

- `research/` — controlled research/evaluation evidence and validated experimental boundaries;
- `src/` — production-path implementation surfaces;
- `tests/` — production-path tests;
- `docs/` — canonical status, planning, ADRs, architecture and delivery acceptance;
- `scripts/` — governed research/engineering utilities.

The first production runtime slice is intentionally provider-free and read-only while the production authorization/idempotency policy remains a separate governed decision. It reuses the accepted ADR-004 controller and the validated E2 `HarnessRunner` execution boundary instead of duplicating research execution logic.

## Local production-runtime tests

```bash
python -m pip install -e ".[dev]" -e "research/e2[dev]"
python -m pytest -q tests
python -m pytest -q research/e2/tests/test_controller.py
```

This does not authorize provider/model calls, benchmark rescoring, semantic evaluation, blind evaluation or production action execution.
