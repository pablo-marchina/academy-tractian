# E14l real DEV measurement result

**Date:** 2026-08-18  
**Scope:** DEV only  
**Status:** complete real measurement; hard gate failed

## Configuration

E14l changed only `reasoning_effort: high -> medium` relative to E14k while preserving:

- Groq `openai/gpt-oss-120b`;
- JSON Schema Structured Outputs with `strict=true`;
- the exact existing public E10b output schema;
- `max_completion_tokens=4096`;
- temperature 0;
- initial prompt and E14f conditional repair;
- E14c/E14d/E14e/E10e/E10g/E11/E14 policies and thresholds;
- E9 v3 scorer and the unchanged DEV hard gate.

## Operational completeness

The real capture completed successfully:

```text
status:                         E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS
total_calls:                    6
parsed_model_outputs_available: 6
scoreable_calls:                6
retry_count:                    0
repair_count:                   0
validation_ran:                 false
```

## Private evaluator aggregate only

E9 v3 ran exactly once after the fixed capture was complete:

```text
real_task_quality:             0.6190
decision_correctness:          0.3333
evidence_correctness:          1.0000
action_correctness:            0.0000
escalation_correctness:        0.0000
premature_action_rate:         0.0000
unsupported_final_claim_rate:  0.0000
proxy_vs_real_disagreement:    1.0000
```

The DEV gate failed. VALIDATION remains blocked and LOCKED_TEST remains untouched.

## Public boundary observations

The fixed capture had:

- zero semantic-repair triggers;
- zero E10d/E10e/E10g/E11 output changes;
- six calls with concrete public-read equivalents;
- normalized public evidence-family counts of 5, 7, 8, or 9;
- zero E14 selective-reprocess checks.

Therefore the remaining blocker is not operational completeness, evidence breadth, or a closed deterministic guard/canonicalization boundary. The failing dimensions are upstream semantic decision/action/escalation selection.

## Methodological consequence

The reasoning/budget/response-format tuning family is closed after E14k/E14l:

- high reasoning + 4096 is operational but fails quality;
- medium reasoning + 4096 is operational but fails quality;
- changing reasoning effort again would not be justified by current public evidence;
- changing completion budget again is not justified now that both candidates are complete;
- changing JSON response format again is not justified after strict mode is operational.

No per-row private labels are inferred from aggregate E9 metrics. The next candidate must be motivated by public model-output behavior only and may not use scorer rows, expected paths, VALIDATION feedback, or LOCKED_TEST material.
