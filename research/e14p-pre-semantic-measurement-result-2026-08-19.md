# E14p pre-semantic paired result

Status: structurally valid and ready for one frozen E9 v4.2 semantic measurement.

Sanitized aggregate-only result:

```text
E14p transform status:                         PASS
provider calls:                               0
fixed / parsed:                               6 / 6
calls changed:                                6
changed text fields:                          24
decision/action/escalation semantic changes: 0
action endpoint changes:                      0
trace self-check changes:                     0
evidence signature loss / gain / reorder:     0 / 0 / 0
surface provenance violations after:          0
```

E9 v4.1 after E14p reproduced the E14o-after-E14n-v1.1 trajectory metrics exactly:

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

The E9 v4.2 claim packet built from the E14p output is complete:

```text
fixed calls:                          6
claim units:                          126
zero-claim calls:                     0
calibration_reason claim units:       24
evidence_plan claim units:            78
proposed_next_step claim units:        6
risk_notes claim units:               18
```

The E14p-specific semantic transport was preregistered after observing only these aggregate counts and before any E14p semantic label. It reuses the already reliability-qualified `qwen/qwen3.6-27b` judge, unchanged frozen prompt/settings, six requests (one per fixed DEV call), no fallback/retry/prompt repair, a distinct single-attempt lock, and the same zero-tolerance semantic acceptance gate.

Structural CI run `32266260669` passed the E14p 126-claim runner and aggregate regressions. No provider inference occurred in CI.

Interpretation limits:

- a future semantic PASS may support a causal claim about the deterministic serializer effect only;
- it must not be described as improvement in underlying GPT-OSS reasoning;
- targeted PASS still does not authorize VALIDATION;
- full 5/5 DEV coverage remains required before VALIDATION measurement-only;
- no raw outputs, claim text, semantic judge rows, private oracle values, identifiers, hashes, or private paths are committed here.
