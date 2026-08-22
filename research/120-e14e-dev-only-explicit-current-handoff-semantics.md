# E14e — DEV-only Explicit Current-Handoff Semantics

**Date:** 2026-08-17  
**Status:** preregistered and implemented; real model measurement blocked until structural dry-run passes  
**Parent:** E14d  
**Gate:** unchanged E14 DEV acceptance gate

## Why E14e exists

E14d corrected concrete/template public evidence-family equivalence and eliminated the observed E10g insufficient-handoff-evidence downgrades, but the complete real DEV gate still failed. A sanitized fixed-capture boundary diagnostic showed two E10d changes and two E10e changes.

The E10e cases do not justify another intervention:

- one is `visible_rubric_needs_more_evidence`, an explicit model-visible safety condition that must remain blocking;
- one is `too_few_concrete_evidence_resources_for_state_change` on `POST /analyses/{analysis_id}/reprocess` with two normalized public evidence families;
- a public-policy counterfactual showed the specialized E14 selective-reprocess boundary would also reject that proposal because it lacks a human-readable reprocess reason and has zero selective reprocess support anchors.

Therefore E10e threshold, ordering, and E14 selective-reprocess semantics remain unchanged.

The remaining E10d-specific diagnostic isolated one call with historical reason `visible_human_escalation_marker`. For that call:

- `requires_human_escalation` was false before E10d;
- rubric `needs_human_escalation` was false;
- decision class was not `escalation_candidate`;
- no specialist/case-escalate endpoint was selected;
- no explicit positive current-handoff phrase was present;
- no explicit negative handoff phrase was present;
- no conditional/contingent handoff phrase was present;
- only a bare explicit handoff token appeared in `action_escalation_rubric.calibration_reason`, while generic risk markers appeared in `risk_notes`.

Historical E10d uses a whole-output substring fallback whose marker set includes broad terms such as `risk`, `safety`, `severity`, and `escalation`. That representation can convert descriptive risk/escalation context into a current handoff requirement even after every stronger structured E10d condition is false.

## Single intervention class

E14e changes only the final free-text fallback in E10d.

Historical fallback:

```text
if any historical human-escalation marker substring appears anywhere in visible output:
    force current human escalation
```

E14e fallback:

```text
if an explicit positive current-handoff phrase appears in a model-visible semantic field,
and that phrase is not negated or conditional/contingent:
    force current human escalation
```

Bare marker context, explicit negation, and conditional/contingent escalation language do not by themselves authorize a current handoff.

## Conditions preserved exactly

Before the refined fallback, E14e preserves the same stronger E10d conditions and ordering:

1. already `requires_human_escalation=true` → no rewrite;
2. rubric `needs_human_escalation=true` → escalation consistency guard;
3. `decision_class=escalation_candidate` → escalation consistency guard;
4. specialist or case-escalate action endpoint → escalation consistency guard.

After the refined fallback, E14e also preserves the existing state-changing immediate-action human-loop condition.

E14c action-endpoint canonicalization remains active before E10d comparison, and E14d public evidence-family canonicalization remains active for E10e/E10g.

## Semantic scope

The refined fallback only inspects these existing model-visible semantic fields:

- `proposed_next_step`
- `risk_notes`
- `evidence_plan`
- `action_escalation_rubric.calibration_reason`

It does not read private oracle data, evaluator labels, scorer rows, group identifiers, VALIDATION data, or LOCKED_TEST data.

## Explicit non-changes

E14e does **not** change:

- prompt;
- provider/model (`groq` / `openai/gpt-oss-20b`);
- temperature (`0`);
- reasoning effort (`medium`);
- completion budget (`1600`);
- JSON response mode;
- E10e policy or threshold;
- E10g policy or threshold;
- E11 authorization;
- E14 selective-reprocess policy or its two-anchor requirement;
- E14 acceptance thresholds;
- benchmark split;
- stored model output before deterministic guard application.

## Structural self-check contract

Before any real provider call, CI must prove:

- bare `escalation` / risk / safety / severity context does not trigger current handoff;
- explicit negative handoff language does not trigger current handoff;
- conditional/contingent handoff language does not trigger current handoff;
- explicit positive current-handoff language does trigger the refined fallback;
- already-escalated output remains unchanged;
- rubric handoff flag remains authoritative;
- `escalation_candidate` remains authoritative;
- specialist/case-escalate endpoint remains authoritative;
- state-changing immediate action still reaches the preserved human-loop branch;
- all inherited E14d structural checks still pass;
- synthetic DEV remains 6/6 parsed/scoreable with VALIDATION false.

## Measurement discipline

After structural PASS only, one complete real DEV-only E14e generation may be run under the same GPT-OSS configuration and unchanged private E9 v3 scorer.

Because E14d and E14e real measurements would be separate model generations, aggregate score differences are not a paired causal estimate. The deterministic policy behavior is causally testable through structural self-checks and fixed-capture public diagnostics; model-quality metrics remain acceptance evidence for the candidate as a whole.

VALIDATION remains blocked until every unchanged E14 DEV threshold passes simultaneously. LOCKED_TEST remains untouched.

## Files

- `experiments/e14e-dev-only-explicit-current-handoff-semantics-manifest.json`
- `../scripts/research/e14e_explicit_current_handoff_semantics.py`
- `../scripts/research/e14e_dev_only_explicit_current_handoff_semantics.py`
- `../.github/workflows/research-e14e.yml`
