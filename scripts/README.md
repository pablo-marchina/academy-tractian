# Scripts

`scripts/` contains deterministic command-line entrypoints, validators and reporting helpers.

The directory is **not** a second application layer. Product/business logic belongs in `src/academy_tractian/`; scripts should remain thin wrappers around importable modules.

## Current roles

### Evaluation / reporting

Examples:

- `eval_driven_compare.py`
- `adaptive_stopping_report.py`
- `operational_value_analyze.py`
- `operational_value_report.py`
- `semantic_eval_calibrate.py`

### Collection / pilot helpers

Examples:

- `operational_value_pilot.py`
- `semantic_review_collect.py`
- `semantic_human_calibration.py`
- `semantic_annotation_sources.py`

### Validation / acceptance

Examples:

- `validate_delivery_reproduction.py`
- `validate_ev007_failure_campaign.py`
- `validate_ev008_stability_campaign.py`
- `validate_ev011_communication_campaign.py`
- `validate_final_freeze_bundle.py`
- `validate_final_handoff_audit.py`
- `hard_freeze_readiness.py`
- `load_concurrency_benchmark.py`

### Historical research wrappers

`scripts/research/` may contain experiment-specific wrappers retained for provenance. Treat them as research evidence unless the current product status explicitly promotes them.

## Rules for new scripts

1. Put reusable logic in `src/academy_tractian/` first.
2. Keep the script focused on parsing arguments, invoking the module and formatting output.
3. Do not embed secrets, provider credentials or environment-specific production configuration.
4. Prefer machine-readable output for CI/evidence-producing commands.
5. Make repeated execution deterministic or explicitly document the external source of nondeterminism.
6. If a script becomes required by the serving path, move that responsibility into the product package.
7. Avoid creating near-duplicate scripts for one parameter change; use CLI flags or a matrix instead.

## Cleanup policy

Before removing a script, search workflows, frozen manifests, ADRs and reproduction instructions for exact path references. Historical validators may be part of the scientific evidence trail even when they are no longer part of the active development loop.
