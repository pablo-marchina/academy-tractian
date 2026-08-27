# Wave 4 — API-MAP-v0

Status: **API-SPECIFIC RESEARCH MAP / NOT FINAL ARCHITECTURE**

Date: 2026-08-15

## Runtime surface

The supplied FastAPI application exposes **18 HTTP operations across 17 unique path templates**.

### Context / read operations

| Operation | Category | Model-visible purpose |
|---|---|---|
| `GET /companies/{companyId}` | Contexto | company context |
| `GET /companies/{companyId}/assets` | Contexto | list company assets |
| `GET /users/me` | Contexto | current role/permissions/company |
| `GET /assets/{assetId}` | Ativos | asset/config/points |
| `GET /assets/{assetId}/analyses` | Análises | analyses, optional status filter |
| `GET /analyses/{analysisId}` | Análises | analysis evidence/confidence/limitations |
| `GET /assets/{assetId}/baseline` | Dados técnicos | baseline state/features/detection mode |
| `GET /assets/{assetId}/rms` | Dados técnicos | RMS series + derived threshold |
| `GET /assets/{assetId}/spectrum` | Dados técnicos | simplified FFT evidence |
| `GET /assets/{assetId}/data-quality` | Dados técnicos | completeness/freshness/SNR |
| `GET /models/{modelId}` | Modelos | coverage/requirements/processing state |
| `GET /knowledge/search` | Conhecimento | substring/diacritic-tolerant knowledge search |
| `GET /knowledge/{docId}` | Conhecimento | procedure/glossary/guidance document |

### Action operations

| Operation | Required API permission | Justification | API-side persistence |
|---|---|---|---|
| `PATCH /assets/{assetId}` | `action_high` | required, >=20 chars | **no stored mutation** |
| `POST /analyses/{analysisId}/reprocess` | `action_low` | required, >=20 chars | accepted event only |
| `POST /analyses/{analysisId}/request-specialist` | `action_low` | required, >=20 chars | accepted event only |
| `POST /models/{modelId}/request-retraining` | `action_high` | required, >=20 chars | accepted event only |
| `POST /cases/{caseId}/escalate` | `escalate` | required, >=20 chars | accepted event only |

All action handlers return `accepted=true` + a generated `action_id` when their coarse permission and justification checks pass. The written TAPI/guide explicitly defines accepted action call = execution, without a later status cycle.

## Critical state-semantics finding

The provided action endpoints **do not write back to the in-memory/parquet store**.

Example independently probed:

1. `GET /assets/asset_V301?seed=complete` -> `criticality=high`;
2. authorized `PATCH ... {criticality: medium}` -> `accepted=true`;
3. subsequent `GET` -> still `criticality=high`.

Therefore, for this supplied API:

- `accepted=true` + correct endpoint/arguments/authority is the executable action oracle;
- generic final-database-state equality cannot be the primary action oracle;
- post-action GET may still be useful as trace/context, but cannot prove persistence;
- volatile `action_id` must be normalized in replay/comparison.

This project-specific evidence supersedes the generic pre-API assumption that every mutation could be verified via final state.

## User context and permission binding

`x-user-id` identifies the current synthetic user. `/users/me` returns:

- `role`;
- permission list;
- `company_id`.

Important integration rule:

> **The model should not choose `x-user-id`.**

The evaluation/runtime harness should bind the case's `user_id` outside model control. Otherwise a model could impersonate a different supplied user and obtain a higher permission class.

## Evaluation seed binding

All query operations expose optional `seed` in the OpenAPI contract.

Important benchmark-integrity rule:

> **The model should not choose `seed`.**

If exposed directly, the model could request `seed=complete` and intentionally bypass most degraded-response experiments. `seed` is an **environment/evaluator variable**, not a semantic task argument.

Canonical tool adapters should therefore remove it from the model-facing schema and inject it from the run configuration.

## Probabilistic mode mechanics

Envelope modes:

- `complete`;
- `partial`;
- `inconclusive`;
- `conflict`;
- `unavailable`.

Default weights in `seed.json`:

- complete 0.60;
- partial 0.15;
- inconclusive 0.10;
- conflict 0.08;
- unavailable 0.07.

### Determinism nuance

The implementation does **not** call a runtime RNG for each unseeded request. It hashes:

`seed-or-'noseed' | resource | category`

into the distribution.

Therefore:

- same explicit seed + same resource/category -> same mode;
- omitted seed + same resource/category -> also the same mode across repeated calls;
- API variability must be created by **varying explicit seeds** or fixed scenario overrides;
- repeated runs with the same environment seed isolate **agent/model variability**, not API-mode randomness.

This differs from documentation wording that says omitting the seed “samples” the distribution. Evaluation code must follow executable behavior.

## Fixed scenario overrides

`seed.json` currently fixes important scenario resources:

- G501: analyses inconclusive, RMS unavailable, data-quality partial, baseline partial;
- C710: RMS complete;
- S420: analyses conflict;
- M208: analyses partial;
- M605: spectrum partial;
- V301: data-quality partial;
- M205: analyses conflict.

Overrides win even when `seed=complete`.

## Mode degradation behavior

Runtime behavior is category-specific:

- complete -> full payload;
- partial -> drops selected fields for some categories;
- inconclusive -> generally returns an inconclusive marker/minimal payload, except “stable” categories;
- conflict -> adds `conflict=true` while retaining payload;
- unavailable -> generally empty data, except stable categories.

Specific partial-field rules currently include:

- analysis detail: drop `evidence`, `limitations`;
- baseline: drop `features`;
- data quality: drop `freshness_minutes`;
- RMS: drop `samples`;
- model: drop `requirements`, `last_run_at`.

Caveat: list-analysis partial behavior differs from detail behavior because the drop rule applies only at the top-level payload; nested analysis rows remain present. This must be treated as executable semantics rather than assumed symmetry.

## API-side validation is intentionally/coarsely incomplete

Action routes accept `dict[str, Any]` and enforce only:

1. recognized resource;
2. coarse permission;
3. justification string >=20 chars.

Independent probes show the raw API will accept, for example:

- `PATCH` with an invalid criticality value;
- `PATCH` with no `changes` field at all;
- arbitrary extra request fields.

Therefore a major project opportunity is **contract-aware pre-execution validation outside the raw API**.

This is directly aligned with the TAPI requirement to evaluate argument accuracy and behavior on high-impact actions.

## Tenant/resource isolation finding

The API checks permission class but does **not** enforce `user.company_id == resource.company_id`.

Independent probes show a user with `action_high` from one company can successfully call the asset-update endpoint for another company's asset; a user with `escalate` can likewise escalate another company's case if the ID is known.

This may be simplification rather than accidental implementation behavior, but it creates an excellent adversarial safety test. The project should distinguish:

- API enforcement;
- agent/system policy enforcement.

Candidate deterministic invariant for the guarded variant:

`current_user.company_id == target_resource.company_id`

where the target resource is company-scoped and the mapping can be resolved from API observations.

## Canonical ToolSpec consequences

Actual API evidence now strongly supports these wrapper rules:

- bind `user_id` outside model control;
- bind `seed` outside model control;
- expose one stable tool contract independent of agent runtime;
- validate arguments against project-owned schemas before execution;
- annotate action permission class and impact;
- enforce resource/tenant policy in a guarded architecture candidate;
- trace proposed arguments separately from executed arguments;
- normalize volatile IDs in replay/evaluation.

These are **experimentable architecture candidates**, except binding evaluator/auth context, which is required to preserve benchmark validity and identity integrity.

## Knowledge/retrieval implication

The supplied knowledge base contains only **5 documents** and already has dedicated API search + document retrieval operations. This makes external RAG/vector infrastructure unnecessary as a default assumption. The RAG ADR should start from the direct API-search baseline and add external retrieval only if measured failures justify it.
