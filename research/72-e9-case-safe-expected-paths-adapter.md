# E9 Case-Safe Expected-Paths Adapter

**Status:** READY_FOR_LOCAL_E9_REAL_SCORE_V3  
**Date:** 2026-08-16  
**Purpose:** fix case-sensitive asset ID mismatch in expected-paths adapter  
**LOCKED_TEST:** blocked  
**Raw private oracle values printed:** false

## Diagnosis

The v2 expected-paths adapter still loaded zero private oracles even though the private probe showed direct mentions for every fixed output group. The cause is a case mismatch:

- fixed Groq output groups preserve canonical IDs such as `asset_B204`, `asset_C710`, `asset_G501`, `asset_M102`, and `asset_S420`;
- the adapter lowercased the expected-path row text before regex matching, producing mentions such as `asset_b204`;
- the comparison stayed case-sensitive against the fixed output group IDs, so no oracle group matched.

## Fix

`scripts/research/e9_evaluator_side_scorer_v3.py` wraps the v2 scorer and patches only the expected-path mapping step:

- match asset mentions case-insensitively;
- preserve canonical fixed-output group IDs in the scorer output;
- keep the v2 gold-leakage boundary;
- keep LOCKED_TEST blocked;
- print only sanitized counts, booleans, hashes and aggregate metrics.

## Local command

```powershell
python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json" `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json" `
  --out "$env:TEMP\e9-private-task-quality-summary-v3.json" `
  --include-rows

Get-Content "$env:TEMP\e9-private-task-quality-summary-v3.json"
```

Expected mapping result:

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

Only commit a later sanitized aggregate summary. Do not commit `expected-paths.json`, fixed parsed Groq outputs, raw expected-path rows, expected answers, reference trajectories, labels, API keys, or LOCKED_TEST material.
