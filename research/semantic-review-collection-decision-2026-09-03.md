# Semantic review collection decision — 2026-09-03

## Decision

Add a persistent, authenticated human-review collector for the held-out semantic calibration workflow. The collector reuses the production `RuntimeContextProvider` identity boundary and PostgreSQL operational database; it does not introduce a parallel login or a browser-owned reviewer identity.

This slice is collection infrastructure only. **It contains no real human labels, no real adjudication, no calibrated judge and no quality/business claim.**

## Scope

The collector accepts only packets already produced by the frozen semantic-review preparation path with:

- `purpose = HELD_OUT_CALIBRATION`;
- private manifest `source_split = VALIDATION`;
- the frozen semantic rubric hash;
- exact packet/manifest task binding validated by the canonical resolver.

DEV/PILOT and `LOCKED_TEST` material are not accepted by this production calibration collector.

## Identity and authorization

The HTTP surface is attached to the existing product app and requires the explicit permission:

`semantic-calibration:review`

`organization_id` and `user_id` come only from the trusted runtime context. The browser cannot submit reviewer identity, reviewer slot, organization or split. A packet-scoped SHA-256 pseudonym is derived server-side for evaluator exports so raw product identity never enters calibration artifacts.

## Blind assignment contract

The browser receives only:

- opaque assignment ID;
- packet ID;
- the existing sanitized `SemanticReviewerTask`.

It does **not** receive:

- reviewer slot A/B;
- whether the task is first-pass review or adjudication;
- prior reviewer scores/reason codes;
- source split or group ID;
- reviewer/user identity;
- frozen annotation manifest;
- private truth/gold material;
- raw prompt/provider output;
- chain of thought.

Hiding the adjudication phase prevents prior disagreement itself from becoming a reviewer cue.

## Persistent assignment invariants

PostgreSQL owns task reservation and terminal labels.

For each semantic task:

1. slot A and slot B are independently assigned;
2. one principal can never be exposed to the same task twice, including after withdrawal;
3. a slot has at most one active and at most one completed assignment;
4. adjudication becomes eligible only after A and B both complete with different scores;
5. prior A/B reviewers are excluded from adjudicating their task;
6. one task has at most one active/completed adjudication;
7. one principal has at most one active semantic assignment at a time;
8. same-principal concurrent assignment requests converge through a PostgreSQL advisory transaction lock;
9. task reservation uses `FOR UPDATE ... SKIP LOCKED` to prevent cross-worker double assignment;
10. withdrawn assignments persist no score or reason codes.

The scoped PostgreSQL role has tenant-filtered RLS reads. Mutations remain behind the authenticated application/store boundary.

## Label validity

Reviewer submissions use the existing 0/1/2 semantic score ontology and structured reason-code contract:

- score `2` requires exactly `NO_MATERIAL_DEFECT`;
- scores `0` or `1` require at least one structured defect reason;
- defect scores cannot contain `NO_MATERIAL_DEFECT`;
- duplicate reason codes are rejected.

Completed first-pass rows are reconstructed as canonical `SemanticReviewerLabel` values during trusted export. Adjudication rows are reconstructed as canonical `SemanticHumanAdjudication` values. Corrupt database material therefore fails closed during export/resolution rather than silently becoming calibration evidence.

## Trusted administration

`scripts/semantic_review_collect.py` reads database credentials only from:

- `ACADEMY_POSTGRES_INTERNAL_DSN`;
- `ACADEMY_POSTGRES_SCOPED_DSN`.

It supports:

- `register`: persist a held-out VALIDATION reviewer packet plus evaluator-private manifest;
- `export`: write completed evaluator-private labels/adjudications and optionally run the existing resolution step.

`--require-complete` returns non-zero while any reviewer pair/adjudication remains unresolved. Exported reviewer references are packet-scoped pseudonyms; raw `user_id` values are never exported.

## What this unlocks

Once real sanitized VALIDATION outputs exist, the real human sequence is:

`prepare held-out packet -> register -> authenticated blind A/B review -> blind third adjudication where needed -> trusted export -> human resolution -> v2 evidence manifest -> frozen judge calibration gate`

The next implementation step after this backend is an in-product reviewer UI (or equivalent authorized client) and the trusted generation of `SemanticAnnotationSource` records from actual sanitized VALIDATION run outputs. Neither may fabricate labels or material from `LOCKED_TEST`.
