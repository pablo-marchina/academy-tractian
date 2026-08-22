# E14h — DEV-only GPT-OSS 120B High Reasoning

**Status:** PREREGISTERED DEV-only candidate  
**Parent:** E14g  
**Single intervention:** `reasoning_effort: medium -> high`

## Why this candidate exists

E14g changed only the model from GPT-OSS 20B to GPT-OSS 120B. The real E14g capture was complete and internally consistent under every retained public invariant, but the unchanged private DEV gate still failed:

- real task quality: 0.6667
- decision correctness: 0.5000
- evidence correctness: 0.8333
- action correctness: 0.1667
- escalation correctness: 0.1667
- premature action rate: 0.0000
- unsupported final-claim rate: 0.0000

No E14f semantic repair and no E10d/E10e/E10g/E11/E14 downstream guard changed any output in that execution. Public evidence coverage was also comparatively strong: all six calls contained concrete public-read equivalents, with normalized evidence-family counts of 6, 7 or 8.

This makes a narrow reasoning-depth experiment more appropriate than another evidence-surface, parser, schema, endpoint, guard or threshold intervention.

## Candidate change

E14h keeps GPT-OSS 120B and changes only:

```text
E14_REASONING_EFFORT=medium
->
E14_REASONING_EFFORT=high
```

Official Groq documentation supports `low`, `medium` and `high` reasoning effort for GPT-OSS 120B. `high` is documented as using more reasoning tokens.

## Frozen configuration

E14h preserves exactly:

- provider: Groq;
- model: `openai/gpt-oss-120b`;
- E14f initial prompt and conditional semantic-repair prompt;
- E14f repair triggers and maximum one repair call per draft;
- E14c action-endpoint canonicalization;
- E14d evidence-resource canonicalization;
- E14e explicit-current-handoff semantics;
- E10e/E10g/E11/E14 policies and thresholds;
- temperature `0`;
- max completion tokens `1600`;
- JSON Object Mode;
- E9 v3 private scorer;
- DEV split;
- unchanged acceptance gate.

## Completion-budget boundary

The completion budget intentionally remains `1600` even though high reasoning may consume more reasoning tokens. Increasing both reasoning effort and output budget would confound the experiment.

Therefore:

- if E14h remains complete, score it once with unchanged E9 v3;
- if high reasoning causes incomplete/unparseable outputs under the frozen 1600-token budget, record E14h as an operational failure;
- do not increase the token budget inside E14h;
- any later token-budget candidate must be separately preregistered.

## Methodological interpretation

Temperature 0 does not make separate provider generations identical, so E14g -> E14h aggregate score deltas are not treated as deterministic paired effects. The intervention itself is isolated to reasoning effort, while promotion remains based on E14h satisfying every absolute frozen DEV threshold.

No private scorer row, oracle answer, evaluator label, VALIDATION feedback or LOCKED_TEST material may enter prompts, repair or policy.

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

Only a complete real E14h DEV measurement passing every item may proceed to measurement-only DEV+VALIDATION.
