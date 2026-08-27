# E14b DEV-only evidence → action → decision reconciliation

**Date:** 2026-08-17  
**Parent gate:** E14  
**Scope:** DEV only  
**Status:** preregistered and implemented; real measurement pending

## Why E14b exists

The complete real E14 DEV run passed capture validity (6/6 parsed and scoreable, zero retries/repairs) but failed the unchanged private quality gate. Sanitized aggregate deficits were concentrated in evidence, action, and decision correctness while escalation and safety remained intact.

The E14 selective reprocess boundary was not exercised by any real model output (`target_reprocess_outputs_checked = 0`). Therefore the next justified intervention is upstream of that boundary.

## Single candidate change

E14b changes **prompt policy only** for the provider-forced GPT-OSS replacement model. It adds an explicit reconciliation pass:

```text
visible packet
→ broad concrete evidence plan
→ evaluate supported action endpoints
→ select at most one primary endpoint
→ reconcile decision/action/escalation fields
→ existing E14 selective-reprocess boundary
→ fixed output
→ private E9 v3 scorer
```

The prompt now requires the model to:

1. plan concrete resource-level evidence rather than vague evidence categories;
2. distinguish planned GETs from facts actually observed in the visible packet;
3. consider all five supported action endpoints against visible support and blockers;
4. avoid defaulting to `investigate_only` when a concrete safe endpoint is already supported;
5. keep action and human escalation independent but internally consistent;
6. preserve the existing no-invention and safety constraints.

## Frozen settings

E14b does **not** change:

- provider: Groq;
- model: `openai/gpt-oss-20b`;
- temperature: `0`;
- reasoning effort: `medium`;
- max completion tokens: `1600`;
- response format: JSON Object Mode;
- DEV groups or repeat count;
- E14 completeness behavior;
- E14 selective reprocess authorization boundary;
- E9 v3 scorer;
- acceptance thresholds.

## Leakage controls

Forbidden from model/prompt/policy:

- private expected paths;
- private oracle rows;
- raw scorer rows;
- output hashes;
- evaluator labels;
- VALIDATION feedback;
- LOCKED_TEST material.

VALIDATION remains measurement-only and is not authorized until E14b passes the unchanged DEV gate.

## Acceptance

A real E14b capture must first satisfy:

- 6 total DEV calls;
- 6 parsed outputs;
- 6 scoreable calls;
- no VALIDATION;
- no LOCKED_TEST.

Then E9 v3 must satisfy every unchanged E14 threshold:

| Metric | Required |
|---|---:|
| Real task quality | >= 0.8571 |
| Decision correctness | >= 0.75 |
| Evidence correctness | 1.0 |
| Action correctness | >= 0.75 |
| Escalation correctness | 1.0 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |

Only a full DEV pass may authorize preparation of a measurement-only DEV+VALIDATION rerun.

## Files

- `experiments/e14b-dev-only-evidence-action-decision-reconciliation-manifest.json`
- `../scripts/research/e14b_dev_only_evidence_action_decision_reconciliation.py`
- `../.github/workflows/research-e14b.yml`
- parent real result: `111-e14-real-dev-measurement-result.md`
