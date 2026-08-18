# E14g — DEV-only GPT-OSS 120B Model Selection

**Status:** PREREGISTERED DEV-only candidate  
**Parent:** E14f  
**Single intervention:** model only (`openai/gpt-oss-20b` -> `openai/gpt-oss-120b`)

## Why this candidate exists

E14f produced complete parseable outputs and its single conditional public semantic-repair call removed the detected public contradiction, yet the absolute task-quality gate still failed materially. In the same real E14f execution, E10e, E10g and E11 changed zero outputs and E14 saw no target reprocess action. Current evidence therefore does not support another downstream guard or threshold intervention.

The next clean experiment changes model capability only while holding the entire E14f stack fixed.

## Frozen configuration

E14g preserves:

- Groq provider;
- all initial and conditional-repair prompts;
- E14f semantic-repair triggers and max-one-repair rule;
- E14c action-endpoint canonicalization;
- E14d evidence-resource canonicalization;
- E14e explicit-current-handoff semantics;
- E10e/E10g/E11/E14 policy and thresholds;
- temperature `0`;
- reasoning effort `medium`;
- max completion tokens `1600`;
- JSON Object Mode;
- E9 v3 private scorer;
- DEV split and acceptance gate.

Only `E8_GROQ_MODEL` changes to `openai/gpt-oss-120b`.

## Provider availability boundary

Before any real measurement, run the no-inference model-list preflight. It must report `E14G_GROQ_MODEL_PREFLIGHT_PASS`, the requested model active, HTTP 200 and zero-cost operator confirmation. The preflight never prints the API key and does not make an inference call.

Official Groq documentation was checked at preregistration time and listed GPT-OSS 120B as a production model with Free Plan rate limits. Runtime availability is still verified immediately before the experiment rather than assumed from documentation.

## Methodological interpretation

E14g is a **model-selection** experiment. E14f and E14g are separate generations from different models; score differences must not be described as a paired causal effect of model size. Promotion is based only on whether E14g itself satisfies every absolute frozen DEV threshold.

No private scorer row, oracle answer, evaluator label, VALIDATION feedback or LOCKED_TEST material may enter model selection, prompts, repair or policy.

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

Only a complete real E14g DEV measurement passing every item may proceed to measurement-only DEV+VALIDATION.
