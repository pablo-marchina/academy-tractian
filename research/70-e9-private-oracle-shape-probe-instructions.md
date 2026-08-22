# E9 Private Oracle Shape Probe Instructions

**Status:** READY_FOR_LOCAL_PRIVATE_ORACLE_DIAGNOSTIC  
**Date:** 2026-08-16  
**Purpose:** diagnose why `eval/expected-paths.json` loads zero scorer oracles  
**LOCKED_TEST:** still blocked  
**Commit probe output:** no, unless manually sanitized further

## Why the last E9 run stayed in contract mode

The fixed Groq output capture succeeded and produced 12 parsed model outputs. The private oracle file also existed. However, the scorer loaded zero group-matched oracles:

```json
{
  "fixed_calls_consumed": 12,
  "parsed_model_outputs_available": 12,
  "private_oracle_file_provided": true,
  "private_oracles_loaded": 0,
  "scoreable_calls": 0
}
```

That means `eval/expected-paths.json` is not keyed in one of the currently supported scorer shapes:

- `{"oracles": {"asset_X": {...}}}`;
- `{"asset_X": {...}}`;
- a list of records with `group_id`, `asset_id`, or `assetId`.

It is likely keyed by scenario/case/ticket or another expected-path structure. E9 should not guess that schema blindly because that could mis-score the benchmark.

## Safe local probe

Run this probe locally. It prints structural metadata only: top-level keys, key-frequency counts, identifier-key counts and whether the fixed Groq output groups appear anywhere. It does not print expected answers or raw trajectories.

```powershell
cd "C:\Users\Inteli\Documents\Projetos\academy-tractian"
git checkout research/systematic-foundation
git pull
$env:PYTHONPATH = "."

$TRACTIAN_PACKAGE = "C:\Users\Inteli\Documents\Projetos\academy-tractian\inteli-tractian-project\inteli-tractian-project"
$PRIVATE_ORACLE = "$TRACTIAN_PACKAGE\eval\expected-paths.json"

python scripts/research/e9_private_oracle_probe.py `
  --oracle-file $PRIVATE_ORACLE `
  --fixed-output-file "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json" `
  --out "$env:TEMP\e9-private-oracle-shape-probe.json"

Get-Content "$env:TEMP\e9-private-oracle-shape-probe.json"
```

## What to share

Share only the probe output if it contains no raw expected answers. The probe intentionally avoids values for sensitive keys, but review before sharing.

Especially useful fields:

- `top_level`;
- `key_frequency_top_60`;
- `identifier_key_frequency`;
- `fixed_output_groups_with_direct_mentions`;
- `locked_test_literal_seen_in_oracle_file`.

## What not to share or commit

Do not share or commit:

- raw `eval/expected-paths.json`;
- expected answers;
- reference trajectories;
- evaluator-only labels;
- `data/cases.parquet`;
- LOCKED_TEST labels or cases;
- any API key or secret.

## Next step after probe

Use the probe result to implement a format-specific E9 oracle adapter that maps the private expected-path schema to fixed Groq output groups without leaking gold into prompts or public artifacts.
