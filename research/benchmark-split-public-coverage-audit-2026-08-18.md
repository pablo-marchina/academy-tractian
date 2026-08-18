# Benchmark split public coverage audit

**Date:** 2026-08-18  
**Scope:** frozen public split metadata + public representative-group manifest only; no oracle values, no model outputs, no VALIDATION feedback, no LOCKED_TEST answer inspection

## Split leakage result

The frozen `benchmark-split-v1` is structurally disjoint:

- DEV vs VALIDATION: 0 group overlap, 0 scenario overlap, 0 ticket overlap
- DEV vs LOCKED_TEST: 0 group overlap, 0 scenario overlap, 0 ticket overlap
- VALIDATION vs LOCKED_TEST: 0 group overlap, 0 scenario overlap, 0 ticket overlap

Declared source-group and aggregate counts match the actual public metadata.

## Representative DEV-gate coverage

The E10b manifest inherited by the E14 family declares only three representative DEV groups:

```text
asset_G501
asset_C710
asset_S420
```

The frozen DEV split contains five groups total. Therefore the historical E10b→E14m gate covers:

```text
groups:    3 / 5 = 60%
scenarios: 6 / 8 = 75%
tickets:   6 / 8 = 75%
```

The omitted DEV groups are:

### asset_M208

- modality: investigate
- public coverage tags: symptom detection, baseline-not-applicable, learning baseline, knowledge support, partial-evidence variant

### asset_M101

- modality: contextualize
- public coverage tags: procedure retrieval, source fidelity, knowledge partial variant, baseline invalidation context

## Critical coverage implication

Full DEV contains all three modalities:

```text
investigate
execute
contextualize
```

The representative historical gate contains only:

```text
investigate
execute
```

So `contextualize` has never been exercised by the six-call hard gate used throughout the E14 family.

This does not make the historical representative experiments useless; they remain valid as preregistered calibration measurements on their declared subset. It does mean they must not be described as full-DEV coverage evidence.

## Methodological consequence

- Do not change E14m-R1: it remains the single preregistered replacement on the same three representative groups for historical comparability.
- A representative R1 pass is necessary but not sufficient for a DEV-complete claim.
- Before VALIDATION, require both evaluator validity and a full-DEV measurement covering all five frozen DEV groups under the selected, frozen candidate.
- No candidate tuning may occur on VALIDATION.
- The full-DEV measurement design must be preregistered before its real generation and must preserve the selected candidate unchanged.

## CI

`research-benchmark-split-audit` reproduces this audit from public metadata only.
