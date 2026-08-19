# E14u full-DEV generation + deterministic postprocessing checkpoint — 2026-08-19

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

## E14p full-DEV epistemic serializer

The frozen E14p serializer was then applied with the full-DEV 10-call cardinality wrapper. It rewrote only the intended epistemic text fields while preserving all public evidence signatures and operational state.

```text
status                                      E14P_FULL_DEV_PUBLIC_EPISTEMIC_SERIALIZATION_GUARD_PASS
parent_capture_status                       E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_TRANSFORM_PASS
provider_calls_made                         0
fixed_calls_consumed                        10
parsed_outputs                              10
required_dev_groups                         5
observed_dev_groups                         5
repeats_per_group                           2
each_group_exactly_two_calls                true
complete_fixed_transform                    true
calls_changed                               10
changed_text_fields                         40
decision_action_escalation_semantic_changes 0
action_endpoint_changes                     0
trace_quality_self_check_changes             0
evidence_public_signature_loss              0
evidence_public_signature_gain              0
evidence_public_signature_order_changes     0
serializer_reused_without_edits             true
task_world_facts_added_by_serializer        false
private_oracle_used                         false
private_scorer_rows_used                    false
semantic_judge_rows_used                    false
validation_feedback_used                    false
locked_test_used                            false
validation_gate_authorized                  false
```

## E14q full-DEV public action-authorization guard

The frozen E14q authorization guard was applied provider-free to the E14u-after-E14p fixed outputs. It fail-closed one action because the public evidence plan did not include the required `GET /users/me` authorization read. The evidence plan and all v4.2 free-text/trace fields were preserved exactly.

```text
status                                      E14Q_FULL_DEV_PUBLIC_ACTION_AUTHORIZATION_CONSISTENCY_GUARD_PASS
provider_calls_made                         0
fixed_calls_consumed                        10
parsed_outputs                              10
complete_fixed_transform                    true
calls_changed                               1
action_demotions                            1
escalation_demotions                        0
action_endpoints_cleared                    1
decision_class_changes                      1
authorization_failure_reason                missing_users_me_authorization_read: 1
evidence_plan_changes                       0
v4_2_free_text_or_trace_changes             0
private_oracle_used                         false
private_scorer_rows_used                    false
semantic_judge_rows_used                    false
validation_feedback_used                    false
locked_test_used                            false
validation_gate_authorized                  false
```

## E14q2 full-DEV route-role-purpose consistency guard

The frozen E14q2 fail-closed consistency guard was then applied provider-free. It changed two calls to remove inconsistent escalation/action state while preserving the evidence plan and all v4.2 free-text/trace fields exactly. No action or escalation was promoted.

```text
status                                      E14Q2_FULL_DEV_PUBLIC_ROUTE_ROLE_PURPOSE_CONSISTENCY_GUARD_PASS
provider_calls_made                         0
fixed_calls_consumed                        10
parsed_outputs                              10
complete_fixed_transform                    true
calls_changed                               2
action_demotions                            1
escalation_demotions                        2
action_endpoints_cleared                    1
decision_class_changes                      1
consistency_failure_reason                  escalation_true_without_action_now: 1
consistency_failure_reason                  escalation_true_without_escalation_candidate_decision: 1
evidence_plan_changes                       0
v4_2_free_text_or_trace_changes             0
promotions_made                             0
private_oracle_used                         false
private_scorer_rows_used                    false
semantic_judge_rows_used                    false
validation_feedback_used                    false
locked_test_used                            false
validation_gate_authorized                  false
```

## Interpretation

E14u has now cleared the operational generation gate and the unchanged deterministic postprocessing stack E14n v1.1 -> E14p -> E14q -> E14q2. The E14p transform preserved ordered public evidence signatures exactly; E14q and E14q2 preserved the evidence plan and v4.2 claim-source fields while fail-closing unsupported or inconsistent action/escalation state. The evidence-selection hypothesis under test therefore remains intact through the deterministic safety stack.

No deterministic quality claim is made yet. The fixed E14u-after-E14q2 candidate must now run the public surface audit and one frozen E9 v4.1 measurement, after which a new v4.2 claim packet may be built. No semantic judge is authorized unless the deterministic full-DEV gate passes.

No raw outputs, identifiers, hashes, private expected paths, scorer rows, semantic labels, private file paths, VALIDATION feedback, or LOCKED_TEST content are committed here.
