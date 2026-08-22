# E14m-R1 — work while Groq long-window quota is exhausted

**Status:** no provider calls authorized until the long-window quota is restored.

## Safe work available now

1. Run the no-provider local R1 preflight to verify exact frozen env, local private JSON availability, amendment integrity, and that the one-shot replacement output path does not already exist.
2. Run the shape-only private-oracle diagnostic to inform evaluator-validity work without printing oracle values.
3. Keep E9 v3 frozen for the eventual R1 historical score.
4. Use the oracle-free E9 synthetic audit as evidence that a separate evaluator-validity review is required before VALIDATION.
5. Do not inspect or score the first incomplete E14m capture for candidate selection.

## No-provider R1 preflight

After setting the exact E14m-R1 environment variables, run:

```powershell
$TRACTIAN_PACKAGE = "C:\Users\Inteli\Documents\Projetos\academy-tractian\inteli-tractian-project\inteli-tractian-project"
$E14M_R1_CAPTURE = "$env:TEMP\e14m-r1-operational-replacement.json"

python scripts/research/e14m_r1_local_preflight.py `
  --private-root $TRACTIAN_PACKAGE `
  --capture-out $E14M_R1_CAPTURE
```

Expected status:

```text
E14M_R1_LOCAL_PREFLIGHT_PASS
```

The preflight makes no provider call. `safe_to_run_only_after_operator_confirms_long_window_quota_restored=true` means configuration is ready; it is **not** an automated quota check.

## Private-oracle shape diagnostic

This can run while Groq quota is exhausted:

```powershell
python scripts/research/e9_private_oracle_shape_diagnostic.py `
  --oracle-file "$TRACTIAN_PACKAGE\eval\expected-paths.json"
```

The output contains only shape information: container types, field-name counts, length buckets, and whether expected-path items have structured object fields. It does not print expected-path text, root questions, IDs, asset names, hashes, or private paths.

## After quota reset

Run exactly one `e14m_r1_operational_replacement.py` capture using the preregistered frozen environment. If it is incomplete, stop E14m with no third capture. If it is complete 6/6, run unchanged E9 v3 exactly once regardless of public output appearance.

Then produce the safe aggregate report:

```powershell
python scripts/research/e14m_r1_safe_result_summary.py `
  --capture $E14M_R1_CAPTURE `
  --score $E14M_R1_SCORE
```

This report prints only aggregate quality/gate metrics plus public pipeline counters.

## Additional gate before VALIDATION

Even if the historical E9 v3 DEV gate passes, VALIDATION remains blocked until the evaluator-validity review is resolved. This additional gate was registered before the E14m-R1 real replacement result and was motivated by oracle-free synthetic scorer findings, not candidate-specific private row feedback.
