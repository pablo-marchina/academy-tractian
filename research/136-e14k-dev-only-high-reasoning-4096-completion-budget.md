# E14k — DEV-only high-reasoning 4096 completion budget

**Status:** preregistered before implementation; implementation follows the frozen manifest  
**Date:** 2026-08-18  
**Scope:** DEV only

## Why this candidate exists

E14j did not produce a valid quality measurement: 0/6 parsed outputs and 0/6 scoreable calls. The strict Structured Outputs exact-schema synthetic preflight had passed, so another response-format change is not justified by that result.

The public-safe operational pattern is instead consistent across the high-reasoning candidates:

- E14g used GPT-OSS 120B, `reasoning_effort=medium`, `max_completion_tokens=1600` and completed 6/6 calls.
- E14h, E14i and E14j each used GPT-OSS 120B, `reasoning_effort=high`, `max_completion_tokens=1600` and produced 0/6 complete outputs in their real DEV captures.
- Synthetic high-reasoning compatibility preflights succeeded, including the E14j exact strict schema preflight.
- Groq's public reasoning documentation states that high effort uses a large number of reasoning tokens and that the default completion budget can be too low for complex reasoning.

The historical sanitized provider failure classifier also treated any 400/422 `failed_generation` payload as JSON-validation failure. That was too broad to establish schema non-adherence as the real mechanism. Telemetry classification has therefore been refined without changing provider request semantics.

## Single intervention

Relative to E14j:

```text
max_completion_tokens: 1600
→ max_completion_tokens: 4096
```

No other candidate variable changes.

## Frozen configuration

- provider: Groq
- model: `openai/gpt-oss-120b`
- reasoning effort: `high`
- `E14_REASONING_FORMAT=hidden` environment value preserved only for experiment isolation; no GPT-OSS effect is claimed
- response format: JSON Schema Structured Outputs
- `strict=true`
- exact existing public E10b output schema
- temperature: 0
- between-call delay: 25 seconds
- semantic repair delay: 25 seconds
- E14 max retries: 2
- initial prompt unchanged
- E14f conditional semantic repair unchanged
- E14c endpoint canonicalization unchanged
- E14d evidence canonicalization unchanged
- E14e handoff semantics unchanged
- E10e/E10g/E11/E14 guards and thresholds unchanged
- E9 v3 scorer unchanged
- acceptance gate unchanged

## Execution rule

One real E14k DEV capture is allowed after structural CI passes. If and only if the capture is 6/6 parsed and scoreable, E9 v3 may score it once. No in-candidate increase beyond 4096 is allowed if E14k fails.

VALIDATION remains blocked unless the complete E14k DEV measurement passes every existing hard-gate threshold. LOCKED_TEST remains untouched.

## Privacy

Do not commit raw fixed outputs, private scorer rows, output hashes, private paths, expected paths, evaluator labels or reference trajectories.
