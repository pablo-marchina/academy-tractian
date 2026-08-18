# E14i Structural Dry-run Result

**Status:** PASS — structural only  
**GitHub Actions run:** `32123377075`  
**Job:** `95668510359`

The E14i dry-run passed with the preregistered configuration:

```text
status:                                   E14I_DEV_ONLY_GPT_OSS_120B_HIGH_REASONING_HIDDEN_FORMAT_CAPTURE_PASS
model:                                    openai/gpt-oss-120b
reasoning_effort:                         high
reasoning_format:                         hidden
max_completion_tokens:                    1600
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

This is structural evidence only. It does not demonstrate that Groq will accept the real provider combination or that task quality improves.

The next mandatory precondition is the one-call non-benchmark compatibility preflight for `openai/gpt-oss-120b + reasoning_effort=high + reasoning_format=hidden + json_object + max_completion_tokens=1600`. Only a preflight PASS authorizes one real DEV E14i capture.
