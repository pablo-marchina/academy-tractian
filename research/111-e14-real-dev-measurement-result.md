# E14 real DEV-only measurement — sanitized result

**Date:** 2026-08-17  
**Status:** valid measurement; DEV quality gate **FAIL**

## Measurement validity

The recovered E14 run on Groq `openai/gpt-oss-20b` completed all required fixed DEV calls with the preregistered replacement-model compatibility settings:

- DEV calls: 6/6;
- parsed outputs: 6/6;
- scoreable outputs: 6/6;
- retries: 0;
- syntax repairs: 0;
- VALIDATION ran: false;
- LOCKED_TEST accessed: false;
- model prompt received private oracle: false;
- E9 v3 private scorer ran only after fixed outputs existed.

The earlier provider-shutdown and completion-budget-invalidated attempts are not quality measurements. This record covers only the complete recovered run.

## Sanitized aggregate E9 v3 metrics

| Metric | E14 real DEV | Required | Gate |
|---|---:|---:|---|
| Scoreable calls | 6 | 6 | PASS |
| Real task quality | 0.7381 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.5000 | >= 0.7500 | **FAIL** |
| Evidence correctness | 0.5000 | 1.0000 | **FAIL** |
| Action correctness | 0.1667 | >= 0.7500 | **FAIL** |
| Escalation correctness | 1.0000 | 1.0000 | PASS |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |
| LOCKED_TEST accessed | false | false | PASS |

No raw scorer rows, output hashes, private paths, expected-path values, evaluator labels, fixed model outputs, or oracle material are committed here.

## Boundary instrumentation

The complete real run reported:

- target reprocess outputs checked: 0;
- authorized target reprocess outputs: 0;
- blocked target reprocess outputs: 0.

Therefore the selective reprocess boundary introduced in E14 was not exercised by the real fixed outputs. The active blocker is upstream of that boundary: the candidate model/prompt is not reliably producing the required evidence/action/decision behavior on DEV.

## Interpretation

E14 succeeded at its completeness objective but failed the real DEV quality gate. The failure pattern is semantic rather than transport or parsing:

1. safety/escalation behavior is preserved;
2. evidence coverage is insufficient;
3. action selection is the largest aggregate deficit;
4. decision selection is also below gate;
5. the real run produced no reprocess-target outputs, so further tuning of the E14 reprocess filter alone is not justified by this measurement.

The historical E13 measurement used a different Groq model. No causal E13→E14 quality delta is claimed across the provider-forced model change.

## Gate decision

**Do not run VALIDATION.**  
**Do not access LOCKED_TEST.**  
**Do not freeze architecture or progress to integration/UI/demo.**

The next candidate must remain DEV-only and target the upstream evidence→action→decision mapping while preserving:

- completeness 6/6;
- zero premature actions;
- zero unsupported final claims;
- escalation correctness 1.0;
- private-oracle isolation;
- the recovered GPT-OSS transport settings.
