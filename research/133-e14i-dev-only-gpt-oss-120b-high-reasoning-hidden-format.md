# E14i — DEV-only GPT-OSS 120B High Reasoning with Hidden Reasoning Format

**Status:** PREREGISTERED / IMPLEMENTED DEV-only candidate  
**Parent:** E14h  
**Single intervention:** `reasoning_format` only

## Why E14i exists

E14h changed only `reasoning_effort=medium -> high` while preserving GPT-OSS 120B, JSON Object Mode, temperature 0 and the 1600 completion-token cap. Its real DEV attempt did not produce a quality measurement: all six calls exhausted three attempts each, yielding 18 provider failures classified as `json_generation_validation_failure`, zero parsed outputs and zero provider usage counters.

A fixed-capture diagnostic therefore rejected isolated completion-budget exhaustion as the next explanation.

Current Groq reasoning documentation states that `reasoning_format` must be `parsed` or `hidden` when JSON mode is used with reasoning models. The E14 transport used by E14h omitted this field. E14i corrects only that provider configuration mismatch.

## Single change

```text
E14_REASONING_FORMAT: unset/provider-default
→ E14_REASONING_FORMAT: hidden
```

`hidden` is selected instead of `parsed` because the experiment only consumes final JSON. It satisfies the documented JSON-mode constraint without exposing reasoning in the capture or changing the expected output schema.

## Frozen configuration

E14i preserves:

- Groq provider;
- `openai/gpt-oss-120b`;
- `reasoning_effort=high`;
- `max_completion_tokens=1600`;
- temperature `0`;
- JSON Object Mode;
- all initial prompts;
- E14f conditional semantic repair;
- E14c endpoint canonicalization;
- E14d evidence canonicalization;
- E14e handoff semantics;
- E10e/E10g/E11/E14 policies and thresholds;
- E9 v3 scorer;
- DEV split and hard acceptance gate.

No budget increase, model change, prompt change, JSON Schema switch or downstream guard change is allowed inside E14i.

## Compatibility precondition

Before the six-call DEV measurement, run the one-call synthetic compatibility preflight. It uses no TRACTIAN task packet, oracle, scorer rows, VALIDATION or LOCKED_TEST material.

Required status:

```text
E14I_GROQ_HIGH_JSON_HIDDEN_COMPATIBILITY_PREFLIGHT_PASS
```

Only a passing compatibility preflight authorizes one real DEV E14i capture.

## Acceptance gate

Unchanged:

- parsed outputs = 6
- scoreable calls = 6
- real task quality >= 0.8571
- decision correctness >= 0.75
- action correctness >= 0.75
- evidence correctness = 1.0
- escalation correctness = 1.0
- premature action rate = 0.0
- unsupported final-claim rate = 0.0
- LOCKED_TEST accessed = false

If the compatibility preflight passes but the real capture is incomplete, E14i fails operationally. No in-candidate token-budget rescue is allowed.
