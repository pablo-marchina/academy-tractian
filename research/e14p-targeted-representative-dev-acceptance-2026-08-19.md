# E14p targeted representative-DEV acceptance

Status: `E9_V4_2_E14P_REAL_DEV_SEMANTIC_GROUNDEDNESS_PASS`

Sanitized aggregate result only.

```text
fixed calls:                                  6
semantic claims:                            126
semantic full coverage:                    true
factual assertions:                           0
factual groundedness rate:                1.0000
nonfactual claims:                           126
nonfactual NOT_APPLICABLE:                   126
semantic groundedness gate:                 PASS
serializer provider calls:                     0
VALIDATION:                              not run
LOCKED_TEST:                            not used
```

The paired E14p serializer preserved the targeted E9 v4.1 trajectory metrics from E14o-after-E14n-v1.1:

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

Paired serializer invariants were also satisfied: zero decision/action/escalation semantic changes, zero action-endpoint changes, zero trace-self-check changes, and zero loss/gain/reordering of recognized public evidence signatures.

Interpretation is deliberately narrow: E14p establishes that the deterministic epistemic serialization layer removed the observed semantic-groundedness failure on the targeted representative DEV gate while preserving the measured trajectory/decision surface. It does **not** establish improved underlying GPT-OSS reasoning and does **not** authorize VALIDATION.

The next required gate is the already-preregistered full DEV coverage gate over all five frozen DEV groups. No raw outputs, claim text, judge rows, identifiers, hashes, private paths, private oracle values, VALIDATION feedback, or LOCKED_TEST material are recorded here.
