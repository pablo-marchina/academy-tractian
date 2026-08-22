# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14/E14b/E14c/E14d/E14e/E14f/E14g/E14k/E14l real DEV gates failed; E14h/E14i/E14j failed operationally; semantic-selection diagnosis is next**  
**Date:** 2026-08-18

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, and a hard safety/action gate that still blocks downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the DEV gate remains failed.

## Current valid real DEV quality measurements

| Metric | E14 | E14b | E14c | E14d | E14e | E14f | E14g | E14k | E14l | Required |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Parsed / scoreable | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| Real task quality | 0.7381 | 0.6429 | 0.8333 | 0.8095 | 0.7619 | 0.6429 | 0.6667 | 0.6429 | 0.6190 | >= 0.8571 |
| Decision correctness | 0.5000 | 0.5000 | 0.6667 | 0.8333 | 0.6667 | 0.5000 | 0.5000 | 0.3333 | 0.3333 | >= 0.7500 |
| Evidence correctness | 0.5000 | 0.3333 | 1.0000 | 0.6667 | 0.5000 | 0.1667 | 0.8333 | 0.8333 | 1.0000 | 1.0000 |
| Action correctness | 0.1667 | 0.0000 | 0.1667 | 0.3333 | 0.3333 | 0.3333 | 0.1667 | 0.1667 | 0.0000 | >= 0.7500 |
| Escalation correctness | 1.0000 | 0.6667 | 1.0000 | 0.8333 | 0.8333 | 0.5000 | 0.1667 | 0.1667 | 0.0000 | 1.0000 |
| Premature action rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Unsupported final-claim rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

E14h/E14i/E14j are excluded from the quality table because they produced zero parsed real outputs. Cross-generation score deltas are descriptive only and are not treated as deterministic paired causal effects.

VALIDATION remains blocked. LOCKED_TEST remains untouched.

## Retained deterministic findings

E14c fixed public action-endpoint representation without rewriting model output. E14d fixed the analogous public evidence-resource representation. E14d/E14e closed the remaining deterministic boundary issue: the relevant reprocess proposal was not blocked by precedence but by missing public justification/anchor requirements. E14e narrowed historical broad escalation-marker semantics to explicit current handoff semantics. No further downstream guard relaxation is supported by current public evidence.

E14f added one conditional same-model repair call only for preregistered public contradictions. Real E14f was complete and safe but failed the absolute task-quality gate, so public internal consistency is insufficient for benchmark correctness.

## E14g — 120B model selection

E14g changed only the model to `openai/gpt-oss-120b`, preserving medium reasoning, 1600 completion tokens, JSON Object Mode and the frozen post-model stack. It completed 6/6 but failed the gate. All six calls contained concrete public-read equivalents and 6–8 normalized evidence families.

## E14h / E14i / E14j — operational failures

All three high-reasoning real captures used GPT-OSS 120B with `max_completion_tokens=1600` and produced 0/6 parsed outputs. Their null scorer metrics are not quality measurements. Historical telemetry also over-classified generic provider `failed_generation` payloads as JSON-validation failures; future telemetry was refined without changing request semantics.

## E14k / E14l — operational stack recovered, semantic gate still failed

E14k changed only `max_completion_tokens: 1600 -> 4096` at high reasoning and restored 6/6 operational completeness, but failed the quality gate.

E14l then changed only `reasoning_effort: high -> medium` while preserving strict JSON Schema, 4096 tokens and all prompts/policies. It also completed 6/6 and failed:

```text
real_task_quality:        0.6190
decision_correctness:     0.3333
evidence_correctness:     1.0000
action_correctness:       0.0000
escalation_correctness:   0.0000
premature_action_rate:    0.0000
unsupported_claim_rate:   0.0000
```

E14l had zero semantic-repair triggers, zero E10d/E10e/E10g/E11 output changes, six concrete public-read equivalents, normalized public evidence-family counts of 5–9, and zero selective-reprocess checks.

The reasoning/budget/response-format tuning family is therefore closed. The remaining problem class is upstream semantic decision/action/escalation selection.

No per-row private labels may be inferred from aggregate E9 metrics. Before preregistering the next candidate, inspect only public fields of the fixed E14l model outputs using `scripts/research/e14l_public_decision_distribution_diagnostic.py`.

## Required DEV acceptance

| Target | Required |
|---|---:|
| Parsed outputs | 6 |
| Scoreable calls | 6 |
| Real task quality | >= 0.8571 |
| Decision correctness | >= 0.75 |
| Evidence correctness | 1.0 |
| Action correctness | >= 0.75 |
| Escalation correctness | 1.0 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| LOCKED_TEST accessed | false |

## Recent records

- `136-e14k-dev-only-high-reasoning-4096-completion-budget.md`
- `137-e14k-structural-dry-run-result.md`
- `138-e14k-real-dev-measurement-result.md`
- `139-e14l-dev-only-120b-medium-reasoning-strict-4096.md`
- `140-e14l-structural-dry-run-result.md`
- `141-e14l-real-dev-measurement-result.md`
- `results/e14k-real-dev-sanitized-summary.json`
- `results/e14l-real-dev-sanitized-summary.json`

## Methodological rules

- DEV is the only tuning split.
- VALIDATION is measurement-only after a DEV candidate passes.
- LOCKED_TEST remains off-limits until final evaluation.
- Do not commit raw fixed outputs, private scorer rows, output hashes, private local paths, expected paths, evaluator labels, or reference trajectories.
- Private evaluator/gold never enters model prompts, schema, repair, or public policy logic.
- Scripted/dry-run outputs validate structure only, not model quality.
- Separate generations and model/provider substitutions invalidate naive paired causal claims.
- Do not infer per-row private labels from aggregate scorer metrics.

## Critical path

```text
E14l public-output-only semantic distribution diagnostic
→ preregister one upstream semantic-selection intervention using public behavior only
→ structural CI
→ one complete real DEV capture
→ only if 6/6 parsed: unchanged E9 v3 scoring exactly once
→ only if every unchanged DEV threshold passes: measurement-only DEV+VALIDATION
→ final safety/action gate decision
→ architecture decisions backed by accumulated experiments
→ integration/demo implementation
→ final locked evaluation
```
