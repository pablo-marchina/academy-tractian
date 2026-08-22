# E9 Expected-Paths Oracle Adapter

**Status:** READY_FOR_LOCAL_E9_REAL_SCORE_V2  
**Date:** 2026-08-16  
**Purpose:** map private TRACTIAN `eval/expected-paths.json` to fixed Groq output groups  
**LOCKED_TEST:** blocked  
**Raw private oracle values printed:** false

## Probe result used

The local private oracle probe showed that `eval/expected-paths.json` has this structural shape:

```json
[
  {
    "expected_path": [...],
    "id": "...",
    "mode": "...",
    "root_question": "...",
    "ticket_id": "..."
  }
]
```

It also showed direct asset mentions for all fixed output groups used by the E9 run:

- `asset_G501`
- `asset_C710`
- `asset_S420`
- `asset_B204`
- `asset_M102`

The prior scorer loaded zero oracles because it expected direct `asset_X` keys, `group_id`, `asset_id`, or an `oracles` map. The actual file is keyed by expected-path rows.

## Adapter added

`scripts/research/e9_evaluator_side_scorer_v2.py` maps private expected-path rows to fixed Groq output groups by detecting local-only asset mentions inside each expected-path row.

It then computes real evaluator-side metrics while preserving the benchmark boundary:

- model outputs are already fixed and hashed;
- private expected-path data is loaded only by the scorer;
- the model never receives expected answers, reference trajectories, evaluator-only labels or scorer oracles;
- LOCKED_TEST groups remain blocked;
- the summary reports only counts, booleans and aggregate metrics;
- raw expected path text, notes, root questions, labels and trajectories are not printed.

## Local command

```powershell
python scripts/research/e9_evaluator_side_scorer_v2.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e9-private-task-quality-summary-v2.json" `
  --include-rows

Get-Content "$env:TEMP\e9-private-task-quality-summary-v2.json"
```

## Expected result

If the adapter maps fixed output groups correctly, the command should report:

```json
{
  "status": "E9_TASK_QUALITY_SCORER_PASS",
  "fixed_calls_consumed": 12,
  "parsed_model_outputs_available": 12,
  "private_oracles_loaded": 5,
  "calls_with_matching_private_oracle": 12,
  "scoreable_calls": 12
}
```

The actual `real_task_quality`, correctness rates and disagreement rates should be interpreted as local/private evaluator-side results. Only a sanitized aggregate summary should be committed afterwards.

## Do not commit

- `eval/expected-paths.json`
- fixed parsed Groq output rows
- raw expected-path rows
- expected answers
- reference trajectories
- evaluator-only labels
- API keys or secrets
- LOCKED_TEST labels/cases
