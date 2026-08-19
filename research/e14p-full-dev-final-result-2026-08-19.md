# E14p full-DEV final result — 2026-08-19

## Scope

Frozen candidate stack: E14o generation → E14n v1.1 identifier guard → E14p epistemic serializer. Full DEV only: 5/5 groups, 2 repeats/group, 10 fixed calls. VALIDATION and LOCKED_TEST were not used.

## Structural and surface result

- full-DEV generation: PASS, 10/10 parsed and scoreable, 5/5 groups, exactly 2 calls/group;
- E14n v1.1: PASS, 2 unsupported identifier mentions replaced, 0 after transform, 0 decision/action/escalation semantic changes;
- E14p serializer: PASS, 10/10 calls transformed, 0 decision/action/escalation changes, 0 action-endpoint changes, 0 trace changes, 0 public evidence-signature loss/gain/order changes;
- public groundedness surface audit: complete 10/10, 0 unsupported IDs, 0 unrecognized METHOD+path mentions, 0 unsupported unit numerics, 0 false trace flags, 0 concrete provenance violations.

## Frozen E9 v4.1 full-DEV measurement

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
```

Preregistered full-DEV thresholds were not met for evidence correctness (required >= 0.5000), expected-read recall (required >= 0.8333), premature action (required 0), and unsupported action/escalation (required 0). Therefore the candidate is rejected for VALIDATION transition independently of semantic groundedness.

## E9 v4.2 full-DEV semantic characterization

The claim packet shape was frozen before labels: 10 calls, 206 claims, source counts 40 calibration_reason / 126 evidence_plan / 11 proposed_next_step / 29 risk_notes. The already reliability-qualified independent Qwen judge was reused without prompt/model/settings tuning.

Observed aggregate:

```text
status:                                  PASS
valid unique rows:                       206 / 206
full coverage:                           true
claim types:                             45 non_world_metadata; 161 procedural_recommendation
support labels:                          206 NOT_APPLICABLE
factual claims:                          0
nonfactual claims:                       206
nonfactual NOT_APPLICABLE:               206 / 206
factual_groundedness_rate:               1.0000 (vacuous zero-factual definition frozen before labels)
type_support_consistency_rate:           1.0000
semantic_groundedness_gate_pass:         true
```

No private oracle, scorer rows, VALIDATION feedback, LOCKED_TEST, claim text, visible-case values, identifiers, group IDs, hashes, or private paths were exposed to the semantic result.

## Interpretation

E14p **does generalize as a semantic serialization safeguard**: it removed factual assertions across the full DEV packet while preserving the deterministic v4.1 decision/evidence signatures by construction.

E14p **does not pass as a full candidate stack**. Its full-DEV v4.1 evidence and action-safety gates fail. The semantic PASS cannot rescue the candidate and does not authorize VALIDATION.

The next DEV work must remain independent of per-row scorer or semantic labels. First isolate the zero-tolerance action-safety failure with a public-only, paired action-authorization intervention while preserving evidence_plan. Evidence-plan quality remains a separate later intervention class.
