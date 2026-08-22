# E10h Non-validation-tuned Safety Blocker Analysis

**Status:** E10H_SAFETY_BLOCKER_ANALYSIS_RECORDED  
**Date:** 2026-08-16  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why this exists

E10g passed DEV-only safety/action scoring, but the full DEV+VALIDATION remeasurement did not solve the full safety problem.

The full E10g result matches the E10d/E10e full pattern: average task quality, evidence and action remain improved relative to the E9 full baseline, but the full `premature_action_rate` remains `0.25`. The safety acceptance target for integration remains `0.0`, so E10g is not promotable.

This document is a blocker analysis, not a new guard and not a tuning step.

## Boundary

This analysis may use only sanitized aggregate results and general public/project action-safety invariants.

It must not use:

- VALIDATION for tuning;
- private expected-path values in a model or guard;
- raw fixed parsed model outputs;
- raw scorer rows;
- output hashes;
- evaluator labels;
- reference trajectories;
- validation feedback as rule design input;
- `eval/expected-paths.json`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST material.

## Observed blocker

Sanitized full score context:

```text
E9 full baseline → E10d full → E10e full → E10g full
real_task_quality:       0.631  → 0.8214 → 0.8214 → 0.8214
decision_correctness:    0.6667 → 0.75   → 0.75   → 0.75
evidence_correctness:    0.0    → 0.75   → 0.75   → 0.75
action_correctness:      0.25   → 0.75   → 0.75   → 0.75
escalation_correctness:  0.5    → 0.5    → 0.5    → 0.5
premature_action_rate:   0.0    → 0.25   → 0.25   → 0.25
unsupported_claim_rate:  0.0    → 0.0    → 0.0    → 0.0
proxy_disagreement_rate: 1.0    → 0.5    → 0.5    → 0.5
```

E10g full checked 12 visible outputs and changed 0. This means the balanced visible-output guard did not detect the holdout safety failure.

## Why the safety gate does not generalize

The repeated E10d/E10e/E10g full pattern suggests the failed design assumption is not just a threshold issue.

The failed assumption is:

> A post-hoc guard over the model's own visible output can reliably detect premature action whenever the model's answer is internally coherent.

That assumption is too weak. The visible-output guards check whether the answer appears to support action according to its own fields, such as endpoint, `safe_to_act`, `needs_more_evidence`, evidence count and escalation flags. When the model produces an internally coherent but overconfident action recommendation, the guard has no independent authorization layer strong enough to reject it.

So the blocker is not simply "make the visible guard stricter". E10f showed that stricter thresholds can restore safety but collapse action correctness. E10g showed that balancing the thresholds restores DEV quality but still does not solve full premature action.

The general failure mode is:

> Self-attested action safety is being treated as sufficient evidence for action authorization.

## Non-validation-tuned design implication

The next design step should not be a validation-derived case rule.

The next design step should be an independent action-authorization policy based on public/project invariants and DEV-only tests. That policy should decide whether an action is allowed before trusting the model's own `safe_to_act` claim.

A future action-authorization policy should require at least:

- exact supported endpoint classification;
- action type classification: human handoff vs autonomous state-changing maintenance;
- independently computed evidence sufficiency from retrieved resources, not only model self-report;
- required identifier availability for the endpoint;
- explicit human confirmation or review path for high-autonomy maintenance changes;
- no action execution when evidence sufficiency is below the action class threshold;
- no action execution when the policy cannot independently explain why action is allowed.

This is a class-level safety policy, not a VALIDATION-specific patch.

## Gate decision

Do not promote E10g to integration gates.

Do not run another full DEV+VALIDATION measurement until a new candidate is preregistered as a non-validation-tuned action-authorization design and passes DEV-only safety/action scoring.

## Next recommended gate

Prepare an E11 independent action-authorization policy using only DEV/public invariants.

The E11 candidate should be evaluated DEV-only first. Only if DEV safety/action passes should a new full DEV+VALIDATION remeasurement be considered.

## Required constraints for E11

- VALIDATION must remain protected from tuning.
- LOCKED_TEST must remain blocked.
- Private expected paths must remain scorer-only after outputs are fixed.
- The model and policy must not receive evaluator labels or reference trajectories.
- Raw fixed outputs, score rows, output hashes and private oracle material must not be committed.
- Final architecture must remain unfrozen.
