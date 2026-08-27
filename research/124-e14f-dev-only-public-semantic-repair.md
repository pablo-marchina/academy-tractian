# E14f — DEV-only Conditional Public Semantic Repair

**Date:** 2026-08-17  
**Parent:** E14e  
**Status:** preregistered and implemented; structural dry-run required before real DEV

## Motivation

E14e closed the remaining deterministic boundary hypotheses. Its fixed-capture diagnosis found one explicit `needs_more_evidence` contradiction with immediate action and one weak immediate reprocess that the specialized E14 policy would independently reject for missing a human-readable visible reprocess reason and having zero of the required two support-anchor classes.

The existing post-model guards are therefore preserved. The remaining experiment surface is upstream semantic consistency of the GPT-OSS draft.

Rejected E14b is not reused as a parent. E14b expanded every prompt with broad evidence-surface and all-endpoint instructions and regressed DEV quality. E14f instead changes no initial prompt and performs no always-on broad reconciliation pass.

## Single intervention

For each fixed DEV call:

1. run the unchanged E14e initial model call;
2. if the draft is parseable, apply a deterministic public semantic-consistency checker;
3. if no preregistered violation exists, keep the initial draft unchanged and make no second call;
4. if at least one violation exists, call the same model exactly once with:
   - the original visible prompt;
   - the model's own first draft;
   - public violation codes only;
   - narrow repair rules that forbid invented evidence and broad endpoint/evidence enumeration;
5. pass the resulting draft through the unchanged E14c/E14d/E14e and E10e/E10g/E11/E14 policies.

## Preregistered trigger classes

The repair can trigger only when `should_take_action_now=true` and one or more of these public contradictions exist:

- rubric `needs_more_evidence=true`;
- rubric `safe_to_act=false`;
- no supported public action endpoint;
- decision class is `investigate_only` or `insufficient_evidence`;
- autonomous state change is below the unchanged E10e minimum of three existing public evidence families;
- reprocess lacks a human-readable visible evidence-to-reprocess reason;
- reprocess has fewer than the unchanged E14 minimum of two existing public support-anchor classes.

These are consistency conditions, not benchmark labels. Absence of a trigger does not imply benchmark correctness.

## Repair constraints

The repair prompt explicitly requires:

- use only the original visible packet;
- treat planned GETs as plans, not observations;
- never invent measurements, status, severity, permissions, identifiers, model state, knowledge results, or hidden facts;
- do not add irrelevant reads merely to satisfy a count;
- preserve non-conflicting fields where possible;
- if visible support is insufficient, downgrade immediate action rather than fabricate support;
- do not enumerate all five action endpoints;
- do not enumerate the full evidence surface;
- return the same JSON schema only.

## Preserved stack

Unchanged from E14e:

- initial system/user prompt;
- Groq `openai/gpt-oss-20b`;
- temperature `0`;
- reasoning effort `medium`;
- E14 max completion tokens `1600`;
- JSON Object Mode;
- E14c action-endpoint canonicalization;
- E14d public evidence-family canonicalization;
- E14e explicit-current-handoff semantics;
- E10e, E10g, E11 and E14 policies/thresholds;
- E9 v3 scorer;
- acceptance gate;
- DEV-only selection boundary.

A conservative delay before the conditional repair call defaults to the existing between-call delay through `E14F_REPAIR_DELAY_SECONDS` falling back to `E8_BETWEEN_CALL_DELAY_SECONDS`.

## Leakage boundary

The repair receives no private expected paths, scorer rows, evaluator labels, VALIDATION feedback, reference trajectories, or LOCKED_TEST material. Group-specific expected behavior is forbidden.

## Acceptance gate

Exactly unchanged:

```text
parsed outputs = 6
scoreable calls = 6
real_task_quality >= 0.8571
decision_correctness >= 0.75
action_correctness >= 0.75
evidence_correctness = 1.0
escalation_correctness = 1.0
premature_action_rate = 0.0
unsupported_final_claim_rate = 0.0
LOCKED_TEST accessed = false
```

No VALIDATION run is authorized until a complete real E14f DEV measurement passes every threshold simultaneously.

## Causal interpretation

Real E14e and E14f use separate model generations, so aggregate score differences are not paired causal estimates. Structural claims are limited to whether the preregistered repair trigger fired, whether one repair call occurred, and whether public contradictions remained after the repair response.
