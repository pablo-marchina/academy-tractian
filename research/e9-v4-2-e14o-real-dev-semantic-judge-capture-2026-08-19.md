# E9 v4.2 E14o real DEV semantic judge capture — operational result

Status: `E9_V4_2_QWEN_E14O_REAL_DEV_SEMANTIC_JUDGE_CAPTURE_PASS`

Sanitized aggregate operational metadata only:

```text
judge_model:                             qwen/qwen3.6-27b
fixed_calls_consumed:                    6
claim_units_consumed:                    66
valid_prediction_rows_written:           66
provider_attempts_made:                  6
completed_provider_calls:                6
response_format:                         json_object
reasoning_effort:                        none
temperature:                             0
system_prompt_reused_without_edits:      true
provider_output_contract_reused_case_id: true
provider_case_id_mapped_back_locally:    true
real_measurement_attempt_consumed:       true
rerun_allowed:                           false
semantic_metrics_authorized:             true
real_dev_packet_read:                    true
validation_gate_authorized:              false
```

Scope and privacy:

- candidate: `E14o-after-E14n-v1.1`;
- expected source-field claim-unit counts: 12 calibration-reason, 39 evidence-plan, 6 proposed-next-step, 9 risk-notes;
- no private oracle, private scorer rows, VALIDATION feedback, or LOCKED_TEST were used;
- raw provider responses, claim text, visible-case values, judge rows, identifiers, group IDs, hashes, and API key were not printed or committed;
- the semantic measurement attempt is consumed and must not be rerun;
- semantic PASS/FAIL is not inferred from this operational capture. It must be determined only by the frozen offline E14o semantic aggregate.

This record contains no per-claim labels or raw benchmark content.
