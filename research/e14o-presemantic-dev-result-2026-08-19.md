# E14o pre-semantic DEV result — 2026-08-19

## Scope

This record contains aggregate-only DEV evidence for the single real E14o generation capture after the corrected E14n v1.1 identifier-provenance guard. Raw model outputs, identifiers, hashes, private scorer rows, expected paths, semantic claim text, and judge rows remain local and are not committed.

E14o generation was executed exactly once and completed 6/6 calls with 6/6 parsed/scoreable outputs, zero retries, zero repairs, VALIDATION=false, and LOCKED_TEST=false. The generation must not be rerun.

## E14n v1.1 postprocess

The first E14n v1 result on E14o was invalidated for quality selection because the v1 guard could transform public brace placeholders. E14n v1.1 was preregistered and structurally validated before reprocessing the fixed E14o capture.

Sanitized v1.1 result:

```text
fixed / parsed / assessed:                         6 / 6 / 6
complete surface coverage:                         true
calls changed:                                     1
changed text fields:                               1
unsupported identifier mentions before:            1
unsupported identifier replacements:               1
replacement occurrences:                           1
unsupported identifier mentions after:             0
calls with provenance violation before:             1
calls with provenance violation after:              0
decision/action/escalation semantic changes:        0
brace placeholders preserved byte-for-byte:         true
provider calls:                                     0
```

The oracle-free groundedness-surface audit on the v1.1 transformed output then reported zero concrete provenance violations, zero unsupported IDs, zero unrecognized public METHOD+path mentions, zero unsupported unit-bearing numeric mentions, and zero false trace self-check flags.

## E9 v4.1 aggregate measurement

The corrected v4.1 measurement on the E14n-v1.1-transformed fixed E14o capture is complete and structurally valid:

```text
fixed / scoreable:                                  6 / 6
reference_quality:                                  0.7857
decision_correctness:                               0.6667
evidence_correctness:                               0.5000
mean_expected_read_recall:                          0.8333
mean_extra_public_read_count:                       3.5000
action_correctness:                                 0.6667
escalation_correctness:                             0.6667
premature_action_rate:                              0.0000
unsupported_action_or_escalation_rate:              0.0000
locked_test_or_gold_leakage_rate:                   0.0000
visible-case alignment resolved:                    true
expected-step normalization resolved:               true
complete fixed measurement:                         true
validation_gate_authorized:                         false
```

All E14o preregistered v4.1 non-inferiority constraints pass:

```text
decision_correctness >= 0.6667:                     PASS
action_correctness >= 0.6667:                       PASS
escalation_correctness >= 0.6667:                   PASS
evidence_correctness >= 0.1667:                     PASS
mean_expected_read_recall >= 0.70:                  PASS
mean_extra_public_read_count <= 4.0:                 PASS
premature_action_rate == 0:                         PASS
unsupported_action_or_escalation_rate == 0:         PASS
locked_test_or_gold_leakage_rate == 0:              PASS
```

Relative to the valid historical E14l v4.1 measurement, the aggregate changes are:

```text
reference_quality:                 0.7381 -> 0.7857
decision_correctness:              0.6667 -> 0.6667
evidence_correctness:              0.1667 -> 0.5000
mean_expected_read_recall:         0.7222 -> 0.8333
mean_extra_public_read_count:      3.8333 -> 3.5000
action_correctness:                0.6667 -> 0.6667
escalation_correctness:            0.6667 -> 0.6667
safety/leakage rates:              0.0000 -> 0.0000
```

These are separate temperature-0 generations, so no paired causal claim is made. E14o nevertheless satisfies its preregistered aggregate non-inferiority gate.

## E9 v4.2 claim packet

The E14o-after-E14n-v1.1 semantic claim packet is complete:

```text
fixed calls:                                       6
claim units:                                      66
calls with zero claim units:                       0
calibration_reason claim units:                   12
evidence_plan claim units:                        39
proposed_next_step claim units:                    6
risk_notes claim units:                            9
```

No semantic judge has read this E14o packet yet. `research/experiments/e9-v4-2-qwen36-27b-e14o-real-dev-semantic-measurement-preregistration.json` freezes the 66-claim transport and semantic acceptance gate before any E14o semantic label.

## Current interpretation

E14o is a valid targeted DEV candidate and passes all preregistered deterministic/non-inferiority checks so far. It is **not yet accepted** because the v4.2 semantic groundedness gate remains pending. Even a semantic PASS will not authorize VALIDATION by itself: the frozen candidate must still be measured across all five DEV groups before any measurement-only VALIDATION transition.
