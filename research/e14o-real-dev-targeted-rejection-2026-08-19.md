# E14o representative-DEV targeted gate — rejected

Status: `E9_V4_2_E14O_REAL_DEV_SEMANTIC_GROUNDEDNESS_FAIL`

Sanitized aggregate result only:

```text
fixed calls / semantic claims:              6 / 66
semantic full coverage:                     true
factual assertions:                         4
factual supported:                          2
factual contradicted:                       0
factual not supported:                      2
factual groundedness rate:                  0.5000
nonfactual claims:                          62
nonfactual type/support consistent:          62 / 62
semantic groundedness gate:                 FAIL
VALIDATION:                                  not run
LOCKED_TEST:                                 not used
```

E14o is rejected at its preregistered targeted acceptance gate. Its single prompt-only factual-grounding intervention did not change the aggregate target failure relative to the preceding valid E14n semantic measurement: both measurements contained four factual assertions, two supported and two not supported. This comparison is aggregate-only; no per-claim labels or claim text are used for follow-up design.

E14o did improve the independently preregistered E9 v4.1 trajectory metrics after E14n v1.1:

```text
reference_quality:                    0.7857
decision_correctness:                 0.6667
evidence_correctness:                 0.5000
mean_expected_read_recall:            0.8333
mean_extra_public_read_count:         3.5000
action_correctness:                   0.6667
escalation_correctness:               0.6667
premature_action_rate:                0.0000
unsupported_action_or_escalation:     0.0000
locked_test_or_gold_leakage:          0.0000
```

These trajectory improvements do not override the failed semantic-groundedness gate. E14o is therefore not eligible for full-DEV promotion as-is.

No raw outputs, claim text, judge rows, identifiers, hashes, private paths, private oracle values, VALIDATION feedback, or LOCKED_TEST material are recorded here.
