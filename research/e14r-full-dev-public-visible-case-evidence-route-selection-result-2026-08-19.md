# E14r full-DEV public visible-case evidence route selection result — 2026-08-19

## Status

**REJECTED for the preregistered E14r target gate. VALIDATION remains unauthorized.**

This record is aggregate-only. No raw fixed outputs, private expected-path rows, per-row scorer labels, semantic judge rows, identifiers, group-specific failures, hashes, or private paths are stored here.

## Deterministic transform

The provider-free E14r transform consumed the same 10 fixed E14q2 full-DEV calls and changed only `evidence_plan`:

```text
fixed / parsed:                           10 / 10
calls changed:                            10
public read signatures before:            63
public read signatures after:             34
public read signatures added:             13
public read signatures removed:           42
non-evidence field changes:                0
route-contract failures:                   0
selected-read cap failures:                0
provider calls:                            0
group/ticket-specific rules used:       false
split coverage tags used:               false
```

Aggregate public route-selection reasons were:

```text
non_contextual_core:          10
visible_case_cue:baseline:     2
visible_case_cue:rms:          2
```

These counts do not identify any benchmark row, group, ticket, or private evaluator target.

## Public surface audit

The unchanged one-sided surface diagnostic remained clean over all 10 calls:

```text
assessed calls:                         10
complete surface coverage:            true
unsupported identifier mentions:         0
unrecognized METHOD+path mentions:       0
unsupported unit-bearing numerics:       0
false trace self-check flags:             0
concrete provenance violations:           0
```

## Frozen E9 v4.1 full-DEV measurement

The single preregistered E14r v4.1 measurement was complete and scoreable for all 10 calls:

```text
reference_quality:                         0.7714
decision_correctness:                      0.8000
evidence_correctness:                      0.0000
mean_expected_read_recall:                 0.4000
mean_extra_public_read_count:              2.0000
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

## Semantic packet shape

Because E14r changed `evidence_plan`, a new semantic claim packet was built but no semantic judge was called:

```text
fixed calls:                             10
claim units:                            114
calibration_reason:                      40
evidence_plan:                           34
proposed_next_step:                      11
risk_notes:                              29
calls with zero claim units:              0
complete packet coverage:              true
judge called:                          false
```

No real semantic labels are authorized for E14r because the candidate already fails the frozen full-DEV evidence gate. The packet remains local/uncommitted.

## Interpretation

E14r successfully reduced extra public reads from 3.5 to 2.0 while preserving all non-evidence metrics, but the replacement policy removed too much useful evidence: evidence correctness fell from 0.2 to 0.0 and mean expected-read recall fell from 0.7667 to 0.4. The aggregate route-reason counts also show that only two lexical cue families fired in the 10-call full-DEV transform.

This supports rejecting pure visible-case lexical replacement as the next evidence strategy. It does not identify which rows or expected routes failed and does not justify per-group or per-ticket rules.

The next DEV intervention, if any, must be separately preregistered and may use only aggregate E14r findings plus public candidate evidence information. No VALIDATION or LOCKED_TEST feedback is authorized.