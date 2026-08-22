# E14m-R1 real replacement — operational failure

Date: 2026-08-18

## Status

The single preregistered E14m-R1 real replacement capture was found locally and classified by the no-provider existing-capture diagnostic as a genuine real R1 capture.

Sanitized operator-provided summary:

```text
status: E14M_R1_OPERATIONAL_REPLACEMENT_CAPTURE_NEEDS_REVIEW
dry_run: false
replacement_amendment_id: E14m-R1
replacement_capture_index: 1
replacement_captures_allowed: 1
same_candidate: true
total_calls: 6
parsed_model_outputs_available: 1
scoreable_calls: 1
validation_ran: false
locked_test_accessed: false
provider_usage_metadata_present_calls: 1
```

## Sanitized operational post-mortem

The corrected no-provider R1 diagnostic established the operational failure mode without reading oracle/scorer data or printing model outputs:

```text
parsed calls:                         1 / 6
schema-valid calls:                   1 / 6
missing final outputs:                5
initial model-call failures:          5
initial output-parse failures:        0
attempt histogram:                    1 attempt x1; 3 attempts x5
retry histogram:                      0 retries x1; 2 retries x5
sanitized attempt failures:           model_call_failed x15
provider failure category:            rate_limit_long_window x15
calls with provider failure category: 5
```

The one retained successful provider call reported:

```text
completion tokens: 1171
prompt tokens:     1816
total tokens:      2987
reasoning tokens:   934
completion >= 4096 cap: 0 calls
```

Sanitized interpretation:

```text
incomplete_replacement_due_to_provider_failure_before_usable_output
```

This is evidence of an operational long-window provider limit affecting the replacement measurement. It is **not** a quality measurement of E14m and does not establish how the five missing semantic outputs would have behaved.

There is no evidence in this capture that completion-budget exhaustion, JSON parsing, or strict-schema validation caused the five missing outputs.

## Methodological consequence

This capture is incomplete and is **not quality-scoreable**. Frozen E9 v3 must not be run on it, and evaluator v4 must not be used to recover a quality estimate from the single surviving output.

The R1 amendment allowed exactly one operational replacement. Therefore:

- R1 has been consumed;
- no third E14m real capture is authorized;
- E14m is closed without a valid real quality measurement;
- the single surviving output and any private per-row error must not be used to tune a successor candidate;
- VALIDATION and LOCKED_TEST remain blocked.

The sanitized post-mortem classifies the failure but cannot reopen the candidate or authorize a rerun.

## Evaluator work remains independent

The evaluator-validity work was registered before any valid E14m-R1 quality result existed. Because R1 is incomplete, no R1 quality labels are available to influence evaluator-v4 design.
