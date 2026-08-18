# E14l — DEV-only 120B medium reasoning under strict schema + 4096

**Status:** preregistered before implementation  
**Date:** 2026-08-18  
**Scope:** DEV only

## Motivation

E14k restored operational completeness: 6/6 real outputs were parsed and scored under GPT-OSS 120B, `reasoning_effort=high`, strict JSON Schema Structured Outputs, and a 4096 completion-token budget. The candidate nevertheless failed the unchanged absolute DEV quality gate.

The E14k capture showed broad public evidence coverage and zero deterministic guard/repair changes, so another downstream rule relaxation is not justified. The next clean question is whether the `high` reasoning setting is worth retaining inside the now-operational strict-schema 4096 stack.

E14g previously completed 6/6 at `reasoning_effort=medium`, but E14g differed in response format and completion budget. Its scores are therefore not treated as a paired causal comparator.

## Single intervention

Relative to E14k:

```text
reasoning_effort: high
→ reasoning_effort: medium
```

Everything else is frozen.

## Frozen configuration

- provider: Groq
- model: `openai/gpt-oss-120b`
- `E14_REASONING_FORMAT=hidden` environment value preserved only for experiment isolation; no effect is claimed
- response format: JSON Schema Structured Outputs
- `strict=true`
- exact existing public E10b output schema
- `max_completion_tokens=4096`
- temperature 0
- between-call delay 25 seconds
- semantic-repair delay 25 seconds
- E14 max retries 2
- initial prompt unchanged
- E14f conditional public semantic repair unchanged
- E14c/E14d/E14e/E10e/E10g/E11/E14 policies unchanged
- E9 v3 scorer unchanged
- absolute DEV gate unchanged

## Interpretation discipline

E14l is selected only on the absolute preregistered gate. Separate model generations mean score deltas versus E14k or E14g are descriptive, not deterministic paired causal effects.

No private evaluator row, expected path, reference trajectory, raw model output, output hash, or LOCKED_TEST information may influence the candidate.

VALIDATION remains blocked unless E14l passes every DEV threshold.
