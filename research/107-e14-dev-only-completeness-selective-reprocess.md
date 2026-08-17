# E14 DEV-only Completeness-Preserving Selective Reprocess Candidate

**Status:** E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_IMPLEMENTED  
**Date:** 2026-08-16  
**Scope:** DEV-only implementation  
**Demo:** false  
**Integration:** false  
**Full rerun:** false  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Purpose

Implement only the candidate preregistered in E14 after the E13 blocker audit. E13 failed DEV-only for two independent reasons: one fixed DEV call had no parsed output after a model-call failure, and the E13 reprocess boundary blocked every parsed target reprocess action.

E14 addresses both blockers without using VALIDATION or private evaluator information.

## Completeness implementation

The E14 capture replaces the inherited DEV stage with a fixed-call completeness wrapper. For each of the six fixed DEV calls it:

1. builds the same DEV-only visible packet and prompt path;
2. retries only a failed model call or a parse failure, up to two retries by default (`E14_MAX_RETRIES` may lower or raise this locally);
3. after a parse failure, attempts deterministic syntax-only JSON repair;
4. never invents, defaults, or infers missing semantic fields;
5. records only sanitized attempt/retry/repair counters;
6. fails the E14 gate unless all six calls have parsed, schema-valid outputs.

The syntax-only repair is intentionally narrow: strip a Markdown JSON fence, extract the outer JSON object, or remove trailing commas. Missing keys or semantic values are never synthesized.

Required completeness before acceptance:

```text
total_calls = 6
parsed_outputs = 6
scoreable_calls = 6
```

## Selective reprocess authorization

E14 replaces the E13 endpoint-defect-phrase requirement with the preregistered selective visible-support rule for:

```text
POST /analyses/{analysis_id}/reprocess
```

A target reprocess action is preserved only when **all** of the following are visible:

- exact reprocess endpoint;
- analysis identifier or analysis resource reference;
- asset or case identifier/reference from visible DEV context/output;
- proposed action limited to reprocess, with no asset patch or model retraining mutation;
- a human-readable reason that links visible evidence to reprocess.

It must also contain at least two concrete support-anchor classes:

- concrete sensor/RMS/spectrum/baseline/data-quality observation;
- diagnosis uncertainty or incompleteness;
- stale/failed/unreliable/incomplete analysis signal;
- mismatch between current evidence and the existing analysis conclusion;
- case/user request for updated or recomputed analysis;
- knowledge/model context supporting reprocess as the low-risk next diagnostic action.

Generic evidence-family count and generic human-review language remain insufficient.

If the target action lacks sufficient support, E14 downgrades it to investigation/human review and marks the action rubric as not safe to execute yet. Evidence-plan content is preserved.

## Dry-run verification

The E14 dry-run exercises both sides of the selective boundary using synthetic DEV-only schema-valid outputs:

- strong visible support → reprocess preserved;
- generic/weak support → reprocess blocked;
- syntax-only malformed JSON example → repaired without semantic field invention.

Command:

```bash
PYTHONPATH=. python scripts/research/e14_dev_only_completeness_selective_reprocess.py \
  --manifest research/experiments/e14-dev-only-completeness-selective-reprocess-manifest.json \
  --split-manifest research/frozen/benchmark-split-v1.json \
  --out /tmp/e14-dev-only-dry-run.json \
  --dry-run
```

Expected dry-run gate:

```text
parsed_model_outputs_available = 6
scoreable_calls = 6
completeness_pass = true
target_reprocess_outputs_checked = 6
authorized_target_reprocess_outputs > 0
blocked_target_reprocess_outputs > 0
validation_ran = false
```

The dry-run is structural evidence only. It is not model-quality evidence and does not authorize a full rerun.

## Next allowed step

Run the real zero-cost E14 DEV-only capture locally with the existing Groq opt-in, keep the fixed-output file private, and score it with E9 v3 against the private DEV oracle. Only if all E14 DEV acceptance targets pass may a measurement-only DEV+VALIDATION rerun be prepared.

## Boundary

No VALIDATION tuning. No LOCKED_TEST. No private expected paths in prompt or policy. No raw fixed outputs, score rows, output hashes, private paths, evaluator labels, reference trajectories, or validation feedback committed. No integration, demo, UI progression, downstream product phase, or architecture freeze until this gate passes.
