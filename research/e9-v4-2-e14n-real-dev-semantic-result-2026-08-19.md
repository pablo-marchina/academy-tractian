# E9 v4.2 real DEV semantic groundedness — E14n result

**Date:** 2026-08-19  
**Scope:** fixed historical E14l DEV outputs after the preregistered E14n deterministic identifier-provenance transform

## Measurement validity

The reliability-qualified independent judge (`qwen/qwen3.6-27b`) completed the single preregistered real DEV semantic measurement attempt over the already-built E14n claim packet.

```text
fixed calls:                         6 / 6
claim units:                        69 / 69
valid unique prediction rows:      69 / 69
missing / duplicate / invalid:      0 / 0 / 0
full coverage:                      true
provider calls:                     6 / 6
rerun allowed:                      false
private oracle used:                false
private scorer rows used:           false
VALIDATION feedback used:           false
LOCKED_TEST used:                    false
```

The raw claim packet and per-claim judge rows remain local/uncommitted.

## Aggregate semantic result

```text
status:                              E9_V4_2_REAL_DEV_SEMANTIC_GROUNDEDNESS_FAIL
claim type counts:
  factual_assertion:                  4
  procedural_recommendation:        50
  uncertainty_or_epistemic:         14
  non_world_metadata:                1

support label counts:
  SUPPORTED:                          2
  NOT_SUPPORTED:                     2
  NOT_APPLICABLE:                   65

factual claims total:                4
factual supported:                   2
factual contradicted:                0
factual not supported:               2
factual not applicable:              0
non-factual claims total:           65
non-factual NOT_APPLICABLE:         65
non-factual non-NOT_APPLICABLE:      0
factual groundedness rate:          0.5000
type/support consistency rate:      1.0000
```

Gate results:

```text
full coverage:                              PASS
zero contradicted factual claims:           PASS
zero NOT_SUPPORTED factual claims:          FAIL
zero factual/NOT_APPLICABLE pairs:          PASS
zero nonfactual/non-NOT_APPLICABLE pairs:   PASS
semantic groundedness gate:                 FAIL
validation authorized:                      false
```

## Interpretation

This is a valid aggregate DEV failure, not an operational failure. The observed remaining groundedness defect is narrow at the aggregate level: all 65 non-factual claim units were type/support consistent, while 2 of the 4 factual assertions were judged not directly supported by the visible packet. No per-claim labels, claim text, identifiers, group IDs, or private trajectories are used for follow-up design.

E14n therefore remains validated only as an identifier-provenance safeguard. It does not establish general semantic groundedness.

## Next-methodology boundary

A subsequent DEV candidate may address the aggregate failure class only: factual assertions must be directly grounded in visible evidence or expressed instead as conditional hypotheses, procedural recommendations, or explicit uncertainty. The follow-up must not use the identities or text of the two failed claims. Evidence-planning changes are kept out of that intervention so the experiment remains single-class.

VALIDATION and LOCKED_TEST remain blocked.