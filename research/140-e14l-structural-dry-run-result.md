# E14l structural dry-run result

**Date:** 2026-08-18

GitHub Actions run `32133232144`, job `95698738513`, completed the E14l structural dry-run successfully.

Sanitized structural output:

```text
status:                                   E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS
model:                                    openai/gpt-oss-120b
parent_reasoning_effort:                  high
reasoning_effort:                         medium
response_format:                          json_schema
strict:                                   true
max_completion_tokens:                    4096
between_call_delay_seconds:               25.0
total_calls:                              6
parsed_model_outputs_available:           6
scoreable_calls:                          6
validation_ran:                           false
dry_run:                                  true
completeness_pass:                        true
retry_count:                              0
repair_count:                             0
semantic_repair_triggered_calls:          3
semantic_repair_calls:                    3
semantic_repair_residual_violation_calls: 0
target_reprocess_outputs_checked:         3
authorized_target_reprocess_outputs:      3
blocked_target_reprocess_outputs:         0
```

Artifact ID: `9322971501`.

The structural workflow sets pacing sleeps to zero only for dry-run speed. The E14l real runner still requires and asserts `E8_BETWEEN_CALL_DELAY_SECONDS=25` and `E14F_REPAIR_DELAY_SECONDS=25`.

This is structural evidence only. It is not model-quality evidence.

Next authorized step: exactly one real E14l DEV-only capture. E9 v3 may run exactly once only if that capture is 6/6 parsed and scoreable. VALIDATION and LOCKED_TEST remain blocked unless the unchanged DEV hard gate passes.
