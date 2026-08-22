# E14 GPT-OSS completion-budget recovery

**Status:** E14_GPT_OSS_COMPLETION_BUDGET_RECOVERY_PREREGISTERED  
**Date:** 2026-08-17  
**Scope:** DEV only  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**E14 policy changed:** false  
**Acceptance thresholds changed:** false

## Evidence from the invalid recovered run

The second real recovered E14 attempt on `openai/gpt-oss-20b` did not produce a complete fixed-output set and therefore is not E14 quality evidence.

Sanitized diagnostics showed:

- 6 total calls;
- 1 parsed/scoreable output;
- 16 model-call failures;
- 0 output-parse failures;
- all observed provider failures classified as non-retryable request failures;
- the one successful call used 1,481 prompt tokens, 754 completion tokens and 553 reasoning tokens, for 2,235 total tokens;
- the harness completion cap was 800 tokens.

The successful response therefore consumed 94.25% of the harness completion budget. Because GPT-OSS reasoning tokens are part of completion usage, the prior 800-token cap leaves little room for the required final JSON after reasoning.

## Isolated compatibility change

For the next DEV-only attempt, change only the completion budget / pacing layer:

- model remains `openai/gpt-oss-20b`;
- reasoning effort is explicitly fixed to `medium`, matching the provider default;
- response format remains JSON Object Mode;
- temperature remains 0;
- E14 prompt remains unchanged;
- E14 selective-reprocess policy remains unchanged;
- max completion tokens becomes 1,600;
- between-call delay becomes 25 seconds;
- rate-limit-aware transport remains enabled.

Do not combine this rerun with either `reasoning_effort=low` or JSON Schema strict mode. Those are separate compatibility interventions and require their own preregistration if needed.

## Gate

The recovered run is scoreable only if all six DEV calls are parsed and schema-valid. Only then may E9 v3 read the private DEV oracle.

Existing E14 thresholds remain unchanged:

- parsed outputs = 6;
- scoreable calls = 6;
- premature action rate = 0.0;
- unsupported final-claim rate = 0.0;
- real task quality >= 0.8571;
- decision correctness >= 0.75;
- action correctness >= 0.75;
- evidence correctness = 1.0;
- escalation correctness = 1.0;
- LOCKED_TEST remains blocked.

No VALIDATION measurement, integration, demo, UI progression or architecture freeze occurs before the DEV gate passes.
