# E9 v3 synthetic scorer-contract audit

**Date:** 2026-08-18  
**Scope:** source/synthetic audit only; no private oracle, no fixed benchmark outputs, no VALIDATION, no LOCKED_TEST

## Why this audit was run

E14m-R1 is waiting for the Groq long-window quota to reset. Before any VALIDATION decision, the evaluator itself should be checked for semantic fidelity independently of model results. E9 v3 remains frozen for the preregistered E14m-R1 historical comparison; this audit does not change E14m, E14m-R1, or E9 v3.

## CI evidence

GitHub Actions workflow `research-e9-scorer-audit` ran the synthetic audit and passed structurally. The audit result was:

```text
status: E9_SYNTHETIC_SCORER_CONTRACT_AUDIT_FINDINGS_PRESENT
finding_count: 6
```

All six synthetic probes demonstrated a possible mismatch between the scorer's lexical heuristics and ordinary semantic interpretation:

1. A negative phrase such as “human escalation is not required” still sets the scorer's expected-escalation flag to true because the lexical marker is present.
2. A negative action phrase such as “do not reprocess” still sets expected action to true.
3. The word “action” in the root question can set expected action to true even when the expected path says to investigate first.
4. A conditional specialist phrase can set expected escalation to true even when escalation is not currently required.
5. Required evidence terms can satisfy `evidence_correctness` when they appear anywhere in the output, even outside `evidence_plan`.
6. `unsupported_final_claim` currently detects locked-test/gold leakage phrases, not general semantic unsupportedness; a strong unsupported operational claim can therefore score as not unsupported.

## Source-level cause

E9 v3 patches only case-safe asset mapping and inherits v2 semantic scoring. E9 v2 derives action/escalation labels from substring markers over the normalized private row and derives evidence correctness from lexical term overlap anywhere in the full model output.

This is deterministic and reproducible, but the metric names can imply stronger semantic guarantees than the implementation currently provides.

## Methodological consequence

- E9 v3 stays frozen for E14m-R1. Changing it before R1 would break the preregistered historical evaluation contract.
- If E14m-R1 is complete, run E9 v3 exactly once as already preregistered.
- The E9 v3 result may be recorded as the historical DEV metric, but **must not by itself unlock VALIDATION or final architecture selection**.
- Before VALIDATION, perform an evaluator-validity review designed independently of E14m-R1 private per-row results.
- The next evaluator design must be based on the public task contract plus the structural shape of the private expected-path oracle, not on model-specific errors.
- Historical fixed outputs may later be rescored by a preregistered improved evaluator without new model generation, but the evaluator must be frozen before inspecting model-specific per-row outcomes.

## Next no-provider diagnostic

Run `scripts/research/e9_private_oracle_shape_diagnostic.py` locally on the private `expected-paths.json`. It reports only schema/container shape, field names, counts, and length buckets; it prints no oracle values, expected-path text, root-question text, IDs, asset names, hashes, or private paths.

The shape diagnostic will determine whether the private oracle contains structured step fields that can support deterministic semantic scoring, or whether a stronger evaluator needs a separately preregistered semantic annotation/normalization layer.
