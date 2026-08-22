# E14k structural dry-run result

Date: 2026-08-18

GitHub Actions run `32131684036`, job `95694004132`, completed the E14k structural dry-run successfully.

Sanitized output:

```text
status:                                   E14K_DEV_ONLY_HIGH_REASONING_4096_COMPLETION_BUDGET_CAPTURE_PASS
model:                                    openai/gpt-oss-120b
reasoning_effort:                         high
response_format:                          json_schema
strict:                                   true
parent_max_completion_tokens:             1600
max_completion_tokens:                    4096
between_call_delay_seconds:                25.0
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

Artifact ID: `9322415819`.

The structural dry-run skips pacing sleeps after first asserting the frozen real-run values. Real E14k execution still requires `E8_BETWEEN_CALL_DELAY_SECONDS=25` and `E14F_REPAIR_DELAY_SECONDS=25`.

This is structural evidence only. It makes no provider inference call and is not task-quality evidence.

Next authorized step: exactly one real DEV-only E14k capture. E9 v3 may run exactly once only if that capture is 6/6 parsed and scoreable. VALIDATION and LOCKED_TEST remain blocked.
