# E14u full-DEV final result — 2026-08-19

## Scope

DEV-only final result for E14u (`public_evidence_decomposition_system_prompt_only`). VALIDATION was not run and LOCKED_TEST was not used. The real generation attempt was already consumed and must not be rerun.

## Deterministic stack

The fixed E14u generation completed 10/10 calls across 5 DEV groups x 2 repeats. E14n v1.1, E14p, E14q, and E14q2 all completed structurally. E14n removed one unsupported identifier with zero decision/action/escalation semantic changes. E14p preserved the ordered public evidence signatures exactly. E14q and E14q2 were fail-closed and preserved `evidence_plan` and all v4.2 free-text claim-source fields.

## Public surface audit

```text
fixed_calls_consumed                    10
assessed_calls                          10
complete_surface_coverage               true
unsupported_id_mentions                 0
unrecognized_method_path_mentions       0
unsupported_unit_numeric_mentions       0
false_trace_self_check_flags            0
concrete_provenance_violation_count     0
```

The one-sided surface audit is clean but does not establish general semantic groundedness.

## Frozen E9 v4.1 aggregate measurement

```text
status                                  E9_V4_1_MEASUREMENT_ONLY_PASS
fixed_calls_consumed                    10
scoreable_calls                         10
reference_quality                       0.7857
decision_correctness                    0.8000
evidence_correctness                    0.1000
mean_expected_read_recall               0.7417
mean_extra_public_read_count            4.0000
action_correctness                      0.8000
escalation_correctness                  0.8000
premature_action_rate                   0.0000
unsupported_action_or_escalation_rate   0.0000
locked_test_or_gold_leakage_rate        0.0000
alignment_resolved                      true
normalization_resolved                  true
complete_fixed_measurement              true
validation_gate_authorized              false
```

Frozen E14u target gate:

```text
evidence_correctness                    >= 0.5000   FAIL
mean_expected_read_recall               >= 0.8333   FAIL
mean_extra_public_read_count            <= 3.5000   FAIL
decision_correctness                    >= 0.8000   PASS
action_correctness                      >= 0.8000   PASS
escalation_correctness                  >= 0.8000   PASS
premature_action_rate                   = 0.0000    PASS
unsupported_action_or_escalation_rate   = 0.0000    PASS
leakage                                 = 0.0000    PASS
```

## v4.2 packet characterization

The post-E14q2 packet built successfully with complete coverage:

```text
claim_units_total                        214
action_escalation_rubric.calibration_reason 40
evidence_plan[]                          134
proposed_next_step                       12
risk_notes                               28
calls_with_zero_claim_units              0
complete_claim_packet_coverage           true
judge_called                             false
```

Because E14u fails the deterministic full-DEV gate, this packet is characterization-only. No Qwen/semantic judge attempt is authorized for E14u.

## Decision

**E14u is rejected.**

The public evidence-decomposition prompt intervention increased evidence-plan surface area while failing all three evidence gates: evidence correctness fell to 0.1, expected-read recall fell to 0.7417, and mean extras rose to 4.0. Decision/action/escalation and safety remained acceptable, so the unresolved blocker remains evidence selection rather than action safety.

No private scorer rows, expected-path rows, semantic judge rows, VALIDATION feedback, or LOCKED_TEST content were inspected to derive the next hypothesis.

## Next research direction

Do not continue prompt-only whole-response evidence decomposition and do not tune from private rows. The next candidate should isolate evidence planning from the rest of response generation: a narrow public evidence-route planner that sees only the runner-selected visible case plus the public tool/output contract and emits a constrained set of canonical GET routes. It must be qualified on a public synthetic route-selection suite before any real DEV planner attempt is consumed.
