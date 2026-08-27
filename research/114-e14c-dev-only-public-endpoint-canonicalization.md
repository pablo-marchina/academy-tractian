# E14c — DEV-only public action-endpoint canonicalization

**Date:** 2026-08-17  
**Parent gate:** E14  
**Scope:** DEV only  
**Status:** preregistered candidate; real quality not yet measured

## Why E14c exists

The valid E14b DEV capture failed quality, then a no-provider-call sanitized boundary diagnostic isolated a deterministic representation mismatch:

- 6 / 6 outputs parsed;
- E10e changed 3 outputs;
- of those 3 E10e changes, 2 were `unsupported_action_endpoint_visible` and 1 was `visible_rubric_not_safe_to_act`;
- all 3 non-`none` final endpoint values had the public shape `POST /cases/<concrete-id>/escalate`;
- E10g, E11 and E14 changed zero outputs because E10e had already removed the immediate-action state;
- E14 saw zero target reprocess outputs.

The frozen public ToolSpec registry contains the case-escalation action as `POST /cases/{caseId}/escalate`. Historical guards compare endpoint strings against snake-case template forms such as `post /cases/{case_id}/escalate`. A valid concrete path therefore fails exact-template equality even though it represents the same public operation.

This is a policy-input representation bug, not evidence that the endpoint should be weakened or that all immediate actions should be allowed.

## Single candidate change

E14c canonicalizes public action endpoints **only for guard comparison**.

```text
model output action_endpoint
        |
        | stored output remains unchanged
        v
public ToolSpec-derived comparison view
        |
        +--> concrete POST /cases/<id>/escalate
        |        -> post /cases/{case_id}/escalate
        |
        +--> unrecognized / malformed / extra text
                 -> unchanged, fail closed
        v
E10d -> E10e -> E10g -> E11 -> E13/E14
```

The canonicalizer is derived from `research.e2.tool_registry.TOOLS`; it does not introduce a second manually maintained endpoint contract.

## Non-destructive rule

E14c does **not** rewrite the fixed model output. This matters because the concrete endpoint may contain model-visible resource context that the private scorer legitimately counts as evidence. Only the temporary value used by deterministic guards is canonicalized.

## Safety invariant

The diagnostic contained one separate E10e downgrade caused by `visible_rubric_not_safe_to_act`. E14c must preserve that block. Its structural self-check therefore proves both:

1. a concrete valid `POST /cases/<id>/escalate` with `safe_to_act=true` is no longer rejected merely as unsupported;
2. the same endpoint with `safe_to_act=false` is still rejected as `visible_rubric_not_safe_to_act`.

No query strings, fragments, extra prose, wrong HTTP methods or unknown paths are canonicalized into supported actions.

## Comparison anchor

E14c compares against the **recovered E14** candidate on the same provider/model/settings:

- Groq;
- `openai/gpt-oss-20b`;
- temperature `0`;
- reasoning effort `medium`;
- max completion tokens `1600`;
- JSON Object Mode.

E14b is rejected. Its prompt-policy change is not inherited by E14c; E14b is used only as diagnostic evidence that revealed the endpoint-shape bug.

## Frozen constants

E14c preserves:

- recovered E14 prompt policy;
- DEV groups and repeats;
- E10d, E10e, E10g and E11 safety/authorization semantics other than endpoint representation comparison;
- E14 selective-reprocess policy;
- E9 v3 evaluator-side scorer;
- all quality thresholds;
- zero-cost constraint;
- no VALIDATION tuning;
- no LOCKED_TEST.

## Unchanged acceptance gate

A complete real E14c DEV capture must satisfy all of:

| Target | Required |
|---|---:|
| Parsed outputs | 6 |
| Scoreable calls | 6 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| Real task quality | >= 0.8571 |
| Decision correctness | >= 0.75 |
| Action correctness | >= 0.75 |
| Evidence correctness | 1.0 |
| Escalation correctness | 1.0 |
| LOCKED_TEST accessed | false |

Only if every threshold passes may a measurement-only DEV+VALIDATION rerun be prepared.

## Interpretation limits

A DEV pass would show that the recovered E14 policy plus public-contract endpoint canonicalization satisfies the current DEV gate. It would not prove historical cross-model causality, final model/provider superiority, or final architecture readiness. VALIDATION remains measurement-only and LOCKED_TEST remains forbidden until the prescribed final phase.
