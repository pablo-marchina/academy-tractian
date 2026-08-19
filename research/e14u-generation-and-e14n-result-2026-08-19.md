# E14u full-DEV generation + E14n v1.1 checkpoint — 2026-08-19

## Scope

DEV-only checkpoint for the preregistered E14u public evidence-decomposition prompt candidate. VALIDATION was not run and LOCKED_TEST was not used.

## E14u real generation

The single authorized real generation attempt was consumed and completed successfully.

```text
status                         E14U_FULL_DEV_PUBLIC_EVIDENCE_DECOMPOSITION_PROMPT_CAPTURE_PASS
model                          openai/gpt-oss-120b
reasoning_effort               medium
prompt_change_class            public_evidence_decomposition_system_prompt_only
required_dev_groups            5
observed_dev_groups            5
repeats_per_group              2
total_calls                    10
parsed_model_outputs           10
scoreable_calls                10
completeness_pass              true
each_group_exactly_two_calls   true
validation_ran                 false
locked_test_used               false
real_attempt_consumed          true
rerun_allowed                  false
private_oracle_used_by_model   false
validation_feedback_used       false
```

The real E14u generation attempt must not be rerun or replaced without an explicit amendment.

## E14n v1.1 public identifier provenance guard

E14n v1.1 was applied provider-free to the fixed E14u outputs.

```text
status                                      E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_TRANSFORM_PASS
fixed_calls_consumed                        10
parsed_outputs                              10
assessed_calls                              10
complete_surface_coverage                   true
calls_changed                               1
changed_text_fields                         1
unsupported_identifier_mentions_before      1
unsupported_identifier_replacements         1
unsupported_identifier_mentions_after       0
provenance_violation_calls_before            1
provenance_violation_calls_after             0
decision_action_escalation_semantic_changes 0
typed_placeholders_only                     true
brace_placeholders_preserved_byte_for_byte  true
matching_only_outside_brace_placeholders    true
provider_calls_made                         0
private_oracle_used                         false
private_scorer_rows_used                    false
validation_feedback_used                    false
locked_test_used                            false
validation_gate_authorized                  false
```

## Interpretation

E14u has cleared the operational generation gate and the unchanged E14n v1.1 identifier-provenance guard. No deterministic quality claim is made yet. The fixed candidate must still pass the unchanged E14p serializer, E14q, E14q2, public surface audit, and frozen E9 v4.1 before any new semantic-judge measurement can be authorized.

No raw outputs, identifiers, hashes, private expected paths, scorer rows, semantic labels, private file paths, VALIDATION feedback, or LOCKED_TEST content are committed here.
