# E14f Real DEV Measurement Result

**Status:** FAIL — unchanged E14 hard gate remains closed  
**Scope:** DEV only  
**VALIDATION:** not run  
**LOCKED_TEST:** not accessed

## Capture integrity

- capture status: `E14F_DEV_ONLY_PUBLIC_SEMANTIC_REPAIR_CAPTURE_PASS`
- total calls: 6
- parsed outputs: 6
- scoreable calls: 6
- retries: 0
- syntax repairs: 0
- E9 scorer status: `E9_TASK_QUALITY_SCORER_PASS`

`E9_TASK_QUALITY_SCORER_PASS` means the scorer executed correctly; it does not mean the quality gate passed.

## Safe aggregate DEV result

| Metric | E14f | Required | Gate |
|---|---:|---:|---|
| Parsed / scoreable | 6/6 | 6/6 | PASS |
| Real task quality | 0.6429 | >= 0.8571 | FAIL |
| Decision correctness | 0.5000 | >= 0.7500 | FAIL |
| Evidence correctness | 0.1667 | 1.0000 | FAIL |
| Action correctness | 0.3333 | >= 0.7500 | FAIL |
| Escalation correctness | 0.5000 | 1.0000 | FAIL |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |
| LOCKED_TEST accessed | false | false | PASS |

Overall E14f gate: **FAIL**.

## E14f intervention behavior

The preregistered conditional public semantic repair triggered on exactly one of six calls:

- triggered calls: 1
- repair calls: 1
- trigger: `immediate_action_while_needs_more_evidence`
- parseable repair responses: 1
- calls with residual public consistency violations: 0

This is structural evidence that E14f detected and reconciled the targeted public contradiction in this execution. It is not evidence that the repaired output matched the private benchmark answer.

## Downstream boundary effects

After E14f repair and the already-retained E14c/E14d/E14e corrections:

- E10d changed 1 output, for `explicit_current_handoff_phrase`
- E10e changed 0 outputs
- E10g changed 0 outputs
- E11 changed 0 outputs
- E14 selective reprocess saw 0 target reprocess outputs

The deterministic boundary investigation is therefore considered closed under current public evidence. There is no observed downstream guard rejection in this E14f execution that supports relaxing E10d/E10e/E10g/E11/E14.

## Evidence representation diagnostic

The historical literal evidence-marker histogram was heavily sparse (`0` on five calls), while E14d normalization recognized concrete public-read equivalents in all six calls. The normalized public evidence-family histogram was 1, 2, 2, 3, 4 and 8 families across the six outputs.

This supports retaining E14d representation canonicalization, but it does **not** imply evaluator evidence correctness: E9 evidence correctness was only 0.1667. The remaining issue is semantic task behavior, not merely concrete-vs-template resource representation.

## Interpretation

E14f succeeded at its narrow public-consistency objective but failed the task-quality gate. In particular, a parseable, internally/publicly consistent output can still choose the wrong evidence plan, decision, action or escalation under the private evaluator.

Do not infer that E14f caused the aggregate score change relative to E14e: the real model generation was different. Separate generations at temperature 0 are not treated as paired causal observations.

Current evidence does not justify:

- lowering any safety/action threshold;
- weakening `needs_more_evidence` or `safe_to_act` checks;
- changing E10d/E10e/E10g/E11/E14 ordering;
- adding further evaluator-shaped post-model guards;
- using VALIDATION for tuning.

## Next experimental direction

The next candidate should operate at the model-selection/configuration layer rather than add another deterministic benchmark-shaped boundary. A clean candidate may change exactly one model-level variable while preserving E14f, all prompts/policies, scorer, split and gate.

VALIDATION remains blocked until one DEV candidate passes every unchanged threshold.
