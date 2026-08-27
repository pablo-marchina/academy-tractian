# E14s full-DEV public evidence candidate-pool consensus result — 2026-08-19

## Status

**FAIL for the preregistered E14s evidence gate. VALIDATION remains unauthorized.**

This record contains aggregate-only results. No raw fixed outputs, private expected-path rows, per-row scorer labels, semantic judge rows, identifiers, group-specific failures, hashes, or private paths are stored here.

## Deterministic transform

E14s consumed the same 10 fixed E14q2 full-DEV calls and changed only `evidence_plan`:

```text
fixed / parsed:                          10 / 10
calls changed:                           10
public reads before:                     63
public reads after:                      59
public reads added:                      13
public reads removed:                    17
public reads retained:                   46
public candidate pool total:             76
consensus candidates total:              21
E14r-only candidates total:              13
original-only candidates total:          42
active dependency candidates total:       0
max selected reads per call:              6
non-evidence field changes:               0
route contract failures:                  0
selected-read cap failures:               0
provider calls:                            0
```

No group/ticket-specific selector, split coverage tag, private oracle, private scorer row, semantic judge row, VALIDATION feedback, or LOCKED_TEST content was used.

## Public surface audit

The one-sided public surface audit remained clean across all 10 calls:

```text
assessed calls:                          10
complete surface coverage:             true
unsupported identifier mentions:          0
unrecognized METHOD+path mentions:        0
unsupported unit-bearing numerics:        0
false trace self-check flags:              0
concrete provenance violations:            0
```

General free-text groundedness was not measured by this surface audit.

## Frozen E9 v4.1 full-DEV measurement

The single E14s measurement was complete and scoreable for all 10 calls:

```text
reference_quality:                         0.8000
decision_correctness:                      0.8000
evidence_correctness:                      0.2000
mean_expected_read_recall:                 0.7750
mean_extra_public_read_count:              3.1000
action_correctness:                        0.8000
escalation_correctness:                    0.8000
premature_action_rate:                     0.0000
unsupported_action_or_escalation_rate:     0.0000
locked_test_or_gold_leakage_rate:           0.0000
scoreable calls:                           10 / 10
alignment resolved:                       true
normalization resolved:                   true
complete fixed measurement:               true
validation gate authorized:              false
```

Preregistered evidence thresholds were not met:

```text
evidence_correctness:          0.2000  < 0.5000
mean_expected_read_recall:     0.7750  < 0.8333
mean_extra_public_read_count:  3.1000 <= 3.5000
```

Decision/action/escalation and safety remained exactly at the accepted E14q2 levels.

## Semantic packet characterization

The deterministic E9 v4.2 packet builder completed successfully after the evidence-plan change:

```text
fixed calls:                  10
calls with visible case:      10
claim units total:           139
zero-claim calls:              0
calibration_reason claims:    40
evidence_plan claims:         59
proposed_next_step claims:    11
risk_notes claims:            29
complete coverage:          true
judge called:               false
```

Because E14s already failed the deterministic v4.1 gate, no semantic judge call is authorized for this rejected candidate.

## Interpretation

Relative to E14q2, E14s reduced total public reads from 63 to 59, slightly improved expected-read recall from 0.7667 to 0.7750, and reduced mean extra reads from 3.5 to 3.1. Evidence correctness remained 0.2.

Relative to E14r, E14s recovered substantial useful coverage while keeping extras below the ceiling. The aggregate result supports the candidate-pool consensus direction but does not meet the frozen evidence gate.

No private row was inspected and no group/ticket failure was inferred. Any next intervention must be independently preregistered from aggregate/public information only.
