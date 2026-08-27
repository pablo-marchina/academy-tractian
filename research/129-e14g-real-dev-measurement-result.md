# E14g Real DEV Measurement Result

**Status:** FAIL — unchanged E14 hard gate remains closed  
**Scope:** DEV only  
**Model:** `openai/gpt-oss-120b`  
**VALIDATION:** not run  
**LOCKED_TEST:** not accessed

## Preflight and capture integrity

The no-inference provider preflight passed before the measurement:

- requested model: `openai/gpt-oss-120b`
- model active: true
- HTTP status: 200
- zero-cost operator confirmed: true
- inference call made by preflight: false
- API key printed: false

Real capture:

- capture status: `E14G_DEV_ONLY_GPT_OSS_120B_MODEL_SELECTION_CAPTURE_PASS`
- total calls: 6
- parsed outputs: 6
- scoreable calls: 6
- retries: 0
- syntax repairs: 0
- E9 scorer status: `E9_TASK_QUALITY_SCORER_PASS`

`E9_TASK_QUALITY_SCORER_PASS` means the private scorer executed correctly; it does not mean the quality gate passed.

## Safe aggregate DEV result

| Metric | E14g | Required | Gate |
|---|---:|---:|---|
| Parsed / scoreable | 6/6 | 6/6 | PASS |
| Real task quality | 0.6667 | >= 0.8571 | FAIL |
| Decision correctness | 0.5000 | >= 0.7500 | FAIL |
| Evidence correctness | 0.8333 | 1.0000 | FAIL |
| Action correctness | 0.1667 | >= 0.7500 | FAIL |
| Escalation correctness | 0.1667 | 1.0000 | FAIL |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |
| LOCKED_TEST accessed | false | false | PASS |

Overall E14g gate: **FAIL**.

## E14g intervention behavior

E14g changed only the model from GPT-OSS 20B to GPT-OSS 120B while preserving the full E14f stack, prompts, temperature, reasoning effort `medium`, completion budget `1600`, JSON Object Mode, post-model policies, scorer and acceptance thresholds.

In the real E14g execution:

- semantic-repair triggered calls: 0
- semantic-repair calls: 0
- residual public semantic violations: 0
- E10d outputs changed: 0
- E10e outputs changed: 0
- E10g outputs changed: 0
- E11 outputs changed: 0
- E14 selective reprocess target outputs: 0

The final outputs were therefore already internally consistent under the preregistered public invariants and passed through every downstream guard unchanged.

## Public evidence-shape diagnostic

E14d normalization recognized concrete public-read equivalents on all six calls. The normalized public evidence-family histogram was:

- 6 families: 1 call
- 7 families: 1 call
- 8 families: 4 calls

This is consistent with the relatively strong aggregate evidence correctness of 0.8333, but evidence coverage alone did not translate into correct operational decisions: action correctness was 0.1667 and escalation correctness was 0.1667.

## Interpretation

E14g rejects the hypothesis that a larger GPT-OSS model at otherwise unchanged E14f settings is sufficient to pass the hard DEV gate. It does **not** support a paired causal numerical claim against E14f because E14f and E14g are separate generations from different models.

The important structural result is that the E14g outputs required no semantic repair or downstream deterministic guard intervention. The remaining failure is therefore not explained by the already-investigated parse, endpoint-representation, evidence-representation, handoff-marker, premature-action, balanced-action, independent-authorization or selective-reprocess boundaries.

Current public evidence does not justify relaxing any guard or threshold, nor adding evaluator-shaped post-model rules.

## Next experimental direction

The next clean model-configuration experiment should keep GPT-OSS 120B and the entire E14f stack fixed while changing exactly one supported reasoning parameter: `reasoning_effort` from `medium` to `high`.

The max completion budget remains `1600` in that candidate so the reasoning-effort change is isolated. If higher reasoning cannot complete reliably under the frozen budget, that is an operational result of the candidate rather than a reason to confound the experiment with a simultaneous token-budget change.

VALIDATION remains blocked until one DEV candidate passes every unchanged threshold.
