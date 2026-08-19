# E14p full-DEV pre-semantic result — 2026-08-19

## Scope

Full DEV only: 5 frozen DEV groups, 2 repeats per group, 10 fixed calls. VALIDATION and LOCKED_TEST were not run.

## Deterministic post-processing

E14n v1.1 passed on all 10 calls. Two unsupported identifier mentions were replaced; zero remained afterward; decision/action/escalation semantics did not change.

E14p full-DEV serializer passed on all 10 calls. It reused the targeted E14p serializer function without edits and preserved decision/action/escalation, action endpoint, trace-quality self-check, and the ordered public evidence signatures exactly.

The public groundedness surface audit completed on all 10 calls with zero unsupported identifiers, zero unrecognized METHOD+path mentions, zero unsupported unit-bearing numeric mentions, zero false trace self-check flags, and zero concrete provenance violations.

## E9 v4.1 full-DEV aggregate

```text
fixed / scoreable:                         10 / 10
reference_quality:                         0.7571
decision_correctness:                      0.7000
evidence_correctness:                      0.2000
mean_expected_read_recall:                 0.7667
mean_extra_public_read_count:              3.5000
action_correctness:                        0.7000
escalation_correctness:                    0.7000
premature_action_rate:                     0.1000
unsupported_action_or_escalation_rate:     0.1000
locked_test_or_gold_leakage_rate:          0.0000
alignment_resolved:                        true
normalization_resolved:                    true
complete_fixed_measurement:                true
validation_gate_authorized:                false
```

The preregistered full-DEV acceptance gate failed on evidence correctness, expected-read recall, premature-action rate, and unsupported action/escalation rate. This blocks VALIDATION regardless of the subsequent semantic groundedness result.

## E9 v4.2 full-DEV packet

The semantic claim packet was built after the fixed full-DEV output and before any full-DEV semantic label:

```text
fixed calls:                                10
calls with visible case:                    10
claim units:                               206
zero-claim calls:                            0
calibration_reason claims:                  40
evidence_plan claims:                      126
proposed_next_step claims:                  11
risk_notes claims:                          29
complete packet coverage:                 true
```

Raw fixed outputs, transformed outputs, private scorer rows, claim text, semantic judge rows, identifiers, hashes, private paths, expected paths, VALIDATION, and LOCKED_TEST material are not committed.

The full-DEV semantic judge transport is separately preregistered for this exact packet shape. Its result is characterization-only and cannot rescue this candidate from the already-observed v4.1 full-DEV failure.
