# E14m — DEV-only conditional public decision adjudication

**Status:** core intervention preregistered before implementation; one operational fallback amendment frozen before runner/provider execution  
**Date:** 2026-08-18  
**Scope:** DEV only

## Why E14m exists

E14l completed 6/6 real DEV calls, but its public output-distribution diagnostic showed complete policy collapse across all six drafts:

```text
decision_class:             investigate_only 6/6
should_take_action_now:     false 6/6
requires_human_escalation:  false 6/6
needs_more_evidence:        true 6/6
safe_to_act:                false 6/6
needs_human_escalation:     false 6/6
action_endpoint:            none/unsupported 6/6
```

This diagnostic reads only the model's own public outputs. It does not read E9 scores, private oracle rows, evaluator labels, VALIDATION, or LOCKED_TEST.

The result is sufficient to identify a public behavioral failure mode: different visible cases are collapsing to one fully conservative decision policy. It is not sufficient to infer which individual cases should instead be action or escalation cases.

## Single intervention

E14m keeps the first E14l model call unchanged. A second same-model adjudication call is allowed only when the first parseable draft matches **all** of the preregistered conservative-collapse conditions:

- `decision_class == investigate_only`;
- `should_take_action_now == false`;
- `requires_human_escalation == false`;
- rubric `needs_more_evidence == true`;
- rubric `safe_to_act == false`;
- rubric `needs_human_escalation == false`;
- canonical public action endpoint is absent/unsupported.

The adjudicator receives only:

1. the original visible prompt;
2. the model's own first draft;
3. the public action endpoint contract;
4. existing public action/escalation safety semantics.

It does **not** receive private expected paths, E9 per-row correctness, evaluator labels, VALIDATION feedback, or LOCKED_TEST information.

## Adjudication rule

The second pass must not force diversity, action, or escalation merely to differ from the first draft. It must re-evaluate the visible packet once and:

- select one supported immediate action only when facts already visible support it under existing public safety rules;
- select human/specialist escalation only when visible risk, severity, specialist-needed uncertainty, or permission blocking supports current handoff;
- retain `investigate_only` / `insufficient_evidence` only when a **specific visible information gap** blocks both supported action and supported human handoff;
- never treat planned GET requests as observations already made;
- never infer that a fact is absent merely because a GET was listed in `evidence_plan`;
- never invent measurements, permissions, severity, identifiers, model state, or knowledge results;
- choose at most one primary action endpoint;
- preserve existing E14 reprocess support-anchor requirements and all downstream guards.

## Ordering

```text
unchanged E14l initial model draft
→ E14m conditional public decision adjudication (0 or 1 extra call)
→ unchanged E14f public consistency repair (if its existing trigger fires)
→ unchanged E14c/E14d/E14e/E10e/E10g/E11/E14 policies
→ fixed capture
→ E9 only if capture is 6/6
```

E14m explicitly skips adjudication inside an E14f repair prompt, preventing recursive extra semantic calls.

## Frozen parent configuration

- provider: Groq
- model: `openai/gpt-oss-120b`
- reasoning effort: `medium`
- recorded `E14_REASONING_FORMAT=hidden` environment value; no GPT-OSS effect claimed
- JSON Schema Structured Outputs
- `strict=true`
- exact existing public E10b output schema
- `max_completion_tokens=4096`
- temperature `0`
- between-call delay `25s`
- adjudication delay `25s`
- E14f repair delay `25s`
- E14 max retries `2`
- E14f repair semantics unchanged
- E14c/E14d/E14e/E10e/E10g/E11/E14 unchanged
- E9 v3 unchanged
- hard DEV gate unchanged

## Operational fallback amendment

The core semantic intervention was preregistered before implementation. Before the E14m runner existed and before any provider execution, one operational behavior was additionally frozen:

- if the optional second adjudication call raises, preserve the first parseable E14l draft;
- if the adjudication response is not parseable, preserve the first parseable E14l draft;
- no third semantic call is allowed;
- the fallback reason is counted in sanitized aggregate metadata.

This prevents an optional semantic pass from converting an already complete parent call into an operational failure. It does not add semantic rescue beyond the original E14l draft.

## Acceptance

The unchanged DEV gate remains:

- parsed outputs = 6;
- scoreable calls = 6;
- real task quality >= 0.8571;
- decision correctness >= 0.75;
- evidence correctness = 1.0;
- action correctness >= 0.75;
- escalation correctness = 1.0;
- premature action rate = 0.0;
- unsupported final-claim rate = 0.0;
- LOCKED_TEST accessed = false.

VALIDATION remains blocked unless E14m passes the full DEV gate. LOCKED_TEST remains untouched.
