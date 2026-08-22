# E1 — Cross-Modality Pilot Review

Status: **PILOT REVIEW COMPLETE — schema refinements identified; remaining 12 scenarios pending**

Date: **2026-08-16**

## Purpose

Before reviewing all 16 supplied scenarios into benchmark-authoritative oracles, test the ScenarioSchema v1 draft against four materially different scenario surfaces.

Reviewed privately against agent input + machine reference + narrative scenario:

- `CEN-01` — investigation ending in human escalation;
- `CEN-11` — knowledge/contextualization;
- `CEN-14` — low-impact specialist action;
- `CEN-15` — high-impact asset configuration action.

No evaluator-only resolution/path text is reproduced in this public artifact.

## Pilot result

The source layers can be represented by the current v1 direction, but the review exposed three distinctions that must be explicit before final schema freeze.

### 1. Action oracle must be independent from reference trajectory

At least one reviewed scenario has an action that is required by the expected resolution / machine supervision while the narrative numbered reference trajectory primarily describes the investigation steps.

Therefore:

> absence of an action call from one reference trajectory list does not imply that the action is optional.

`action_oracle` must be derived from policy + P1 criterion + expected resolution + machine supervision together, with provenance, rather than inferred from one path list.

### 2. Post-action validation is not final-state equality

The high-impact configuration scenario includes a post-action read as reference validation, while the supplied API's accepted action does not persist the mutation in the store.

Therefore the structured action oracle needs separate semantics for:

- successful execution signal: API accepted event;
- optional/reference post-action read;
- final-state equality: **not applicable to supplied non-persistent action simulation**.

This prevents the evaluator from incorrectly failing an action because the seeded read model does not mutate.

### 3. Escalation types must remain distinct

The reviewed action/escalation material confirms that internal technical specialist escalation and human/field escalation are not interchangeable outcomes.

The v1 decision taxonomy therefore retains distinct outcomes:

- `ACT_REQUEST_SPECIALIST`;
- `ESCALATE_HUMAN`.

A generic single `ESCALATE` label remains useful only for aggregate reporting.

## Additional schema confirmations

The pilot also confirms that the v1 draft needs to retain:

- source-citation/grounding requirements for knowledge scenarios;
- permission and justification constraints outside the language-model decision itself;
- reference trajectory as diagnostic rather than script;
- explicit forbidden/unsupported inference handling under degraded evidence;
- agent/evaluator source separation;
- runner-bound identity/seed.

## Required schema refinement before full review

Add/clarify inside `action_oracle`:

- `execution_expectation`: `required | forbidden | optional`;
- `success_semantics`: `accepted_event | blocked_by_policy | no_action_expected`;
- `post_action_read_semantics`: `diagnostic_only | required_observation | not_applicable`;
- `final_state_equality_required`: false for the supplied accepted-event simulation unless a future environment persists state.

These fields encode behavior already supported by the supplied artifacts; they do not add new domain assumptions.

## Review status

- cross-modality pilot: **4 / 16 reviewed**;
- remaining: **12 / 16**;
- final ScenarioSchema v1: **not frozen**;
- normalized gold: **not benchmark-authoritative**.

Next E1 action: apply the schema refinement, then review the remaining scenarios in storyline groups so related investigation/action cases are reconciled together rather than independently.
