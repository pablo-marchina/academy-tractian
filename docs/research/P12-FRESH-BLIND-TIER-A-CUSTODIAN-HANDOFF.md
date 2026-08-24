# P12 FRESH_BLIND Tier A — independent custodian handoff

Status: `READY_FOR_EXTERNAL_ATTESTATION / NO SOURCE AUTHORIZED`  
Protocol: `P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST`  
Tier A cutoff: `2026-08-25 23:59 BRT`

## Purpose

Prepare a partner-held, real-domain blind packet for one-shot final measurement without exposing hidden cases, expected paths, labels, outcomes, or candidate-specific feedback to candidate development before generation freeze.

This handoff does **not** authorize FRESH_BLIND execution or scoring. It only defines the information required to register an independent Tier A source while keeping the source blind.

## Custodian / author / adjudicator requirements

The external side must identify, by role or non-secret identifier:

- the source custodian;
- the author or authoring team;
- the adjudicator or adjudication team;
- whether author and adjudicator are isolated from candidate development;
- whether candidate developers have had any access to hidden case semantics or expected outcomes;
- whether any partial/adaptive feedback has already been provided.

The source is ineligible for the affected candidate generation if hidden semantics or outcomes were exposed to candidate development.

## Information that MAY be disclosed before generation freeze

Only non-semantic readiness metadata:

- opaque `source_id`;
- custodian/author/adjudicator roles;
- number of independent asset/story groups;
- high-level modality coverage (`investigate`, `execute`, `contextualize`, where applicable);
- high-level safety-critical coverage;
- provenance description that does not reveal hidden case content;
- custody start time;
- expected one-shot measurement window;
- breach state (`UNBREACHED` required).

## Information that MUST remain external and hidden

Do not put any of the following in this repository, issue, PR, chat, or candidate-development workspace before the final access gate:

- hidden case/ticket content;
- expected evidence paths or reads;
- expected tool calls;
- expected decisions/actions/escalations;
- labels or scores;
- partial results;
- candidate-specific failure descriptions;
- adaptive feedback that could be used to tune the candidate or evaluator.

## Required external attestation

Return only a secret-free attestation containing:

```text
source_id: <opaque id>
tier: TIER_A_PARTNER_HELD_EXTERNAL_BLIND
custodian_identity_or_role: <role>
author_identity_or_role: <role>
adjudicator_identity_or_role: <role>
author_isolated_from_candidate_development: true|false
adjudicator_isolated_from_candidate_development: true|false
developer_cannot_access_hidden_semantics_before_freeze: true|false
no_iterative_partial_feedback: true|false
asset_story_group_independence_confirmed: true|false
group_count: <integer>
modality_coverage: <non-semantic summary>
safety_critical_coverage: <non-semantic summary>
provenance_record: <non-semantic provenance>
custody_start: <timestamp>
expected_measurement_window: <window>
breach_state: UNBREACHED|BREACHED
```

Do not include credentials, hidden case text, expected paths, labels, outputs, or outcomes in the attestation.

## Registration gate

Candidate development may register the source only if:

1. the attestation is complete and secret-free;
2. author/adjudicator independence passes;
3. hidden semantics remain inaccessible to candidate development;
4. no iterative partial feedback has occurred;
5. provenance and custody are auditable;
6. group independence and non-semantic coverage metadata are recorded;
7. breach state is `UNBREACHED`.

Registration still does not authorize measurement.

## Final access gate

FRESH_BLIND execution/outcome access remains blocked until all of the following are true:

- the final candidate generation is frozen;
- the evaluator is frozen;
- blind outcomes cannot cause another same-generation candidate/evaluator change;
- source registration remains valid and unbreached;
- a separate final access authorization passes.

Results are released one-shot after that gate. Iterative partial feedback is forbidden.

## Fail-closed transitions

- Tier A not operational by `2026-08-25 23:59 BRT` → prepare/use the independently authored Tier B path without exposing/relabeling DEV, VALIDATION, or LOCKED_TEST material.
- Tier A and Tier B both unavailable by `2026-08-28 23:59 BRT` → do not manufacture a blind claim; require protocol/scope amendment and explicitly downgrade the final generalization claim.
- Any breach → the source becomes exposed for the affected candidate generation and final blind authorization is denied.

Canonical machine-readable readiness packet: `research/experiments/p12-fresh-blind-tier-a-readiness-packet-v1.json`.
