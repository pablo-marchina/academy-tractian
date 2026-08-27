# Wave 4 — Contract and Package Quality Audit

Status: **SOURCE-QUALITY AUDIT / NORMALIZATION REQUIRED BEFORE TOOL GENERATION**

Date: 2026-08-15

## Purpose

Audit the supplied TRACTIAN project package before any framework, client generator or agent runtime is allowed to treat its artifacts as unquestioned ground truth. The goal is not to criticize the partner package; it is to prevent silent parser behavior, benchmark leakage and evaluator mistakes from contaminating the experiment.

## Q01 — Duplicate OpenAPI path key (`CRITICAL`)

The raw YAML contains `/assets/{assetId}` twice: once for `GET` and later again for `PATCH`.

Consequences:

- ordinary YAML loaders can overwrite one mapping with the other;
- parsing the supplied YAML with a permissive loader loses the GET operation;
- the actual FastAPI runtime exposes both GET and PATCH;
- any direct OpenAPI-to-tools/codegen pipeline can silently generate an incomplete tool surface.

Required handling:

1. archive/hash the raw partner YAML unchanged;
2. detect duplicate YAML mapping keys before semantic parsing;
3. produce a project-owned normalized contract that merges both operations;
4. record every normalization transformation and source location;
5. conformance-test normalized operations against the actual FastAPI router/generated `/openapi.json`.

No tool registry may be generated from a parser that silently drops one operation.

## Q02 — Runtime contract and raw contract must be cross-checked (`HIGH`)

The FastAPI-generated OpenAPI surface contains both asset methods and should be used as a conformance signal, not as a replacement for the supplied raw contract.

Canonical source handling:

- raw partner contract = immutable provenance artifact;
- runtime-generated contract = executable-behavior observation;
- normalized project contract = tool-generation input;
- mismatches = explicit audit findings.

## Q03 — Response schemas are weakly typed (`HIGH`)

Several read endpoints return a generic query envelope whose `data` field is effectively unconstrained, while some list operations do not expose rich response schemas.

Implication:

- generated clients alone cannot establish semantic output correctness;
- project-owned response models/adapters may need to be derived from executable payloads + documented data schema;
- the evaluator should validate important observable fields explicitly rather than assume generator-produced response models are complete.

## Q04 — Action request validation is weaker than the intended domain contract (`CRITICAL`)

The action handlers receive open dictionaries and primarily enforce:

- resource existence;
- coarse permission class;
- a justification string with minimum length.

Independent probes show requests can be accepted with semantically invalid or incomplete change payloads, including invalid criticality values and missing expected change structure.

Implication:

This creates a high-value project-specific architecture experiment:

- minimally wrapped/raw action exposure;
- strict typed argument validation;
- strict validation + policy/resource guards.

The raw API's acceptance must not be confused with semantically valid agent behavior.

## Q05 — Resource/tenant isolation is not enforced by the backend (`CRITICAL`)

The API exposes user company context, but the action implementation checks permission class without verifying that the target asset/case belongs to the current user's company.

Independent cross-company probes were accepted when the caller had the required coarse permission.

Implication:

- evaluation must distinguish API enforcement from agent/system enforcement;
- current user identity must be bound outside model control;
- a deterministic company/resource guard is a strong candidate for the guarded architecture;
- cross-tenant attempts belong in adversarial evaluation.

Do not claim the partner intended cross-tenant access; treat this as executable behavior of the simplified API and test whether a safer agent boundary should compensate for it.

## Q06 — Action endpoints are accepted-event simulations, not persistent mutations (`HIGH`)

After an accepted asset update, a subsequent asset read still returns the seeded configuration. Other action routes likewise return accepted events without mutating the underlying parquet/in-memory state.

Implication:

For the supplied environment, action success should be evaluated via:

- correct decision to act;
- correct target/tool;
- correct/valid arguments;
- authority/policy compliance;
- evidence-backed justification;
- `accepted=true` response;
- absence of duplicate/unnecessary actions.

Final-state equality cannot be required for effects the environment does not persist.

## Q07 — Documented no-seed probability semantics differ from implementation (`HIGH`)

Documentation describes omitted seed behavior as sampling the configured mode distribution. The implementation derives mode deterministically from a hash containing `noseed`, resource and category.

Implication:

- repeated unseeded calls to the same resource/category do not generate independent API modes;
- explicit deterministic seed variation is required for environment-robustness experiments;
- fixed environment seed is excellent for isolating stochasticity from the agent/model itself.

Experiment design should follow executable behavior and document the documentation mismatch.

## Q08 — `mode` terminology is overloaded (`MEDIUM`)

The API response-mode vocabulary is:

- complete;
- partial;
- inconclusive;
- conflict;
- unavailable.

Evaluation/gold material also uses labels such as `pending` and `stale` under a `mode` field.

Implication:

ScenarioSchema v1 should separate, for example:

- `environment_response_mode`;
- `scenario_condition` / `analysis_state`;
- `fault_profile`.

Do not force all partner labels into one enum.

## Q09 — Analysis-count mismatch (`MEDIUM`)

Some written material describes 24 analyses, while the supplied generator currently defines 10.

Rule:

- runtime/data inventory reports the executable/generated count;
- documentation mismatch remains logged;
- no silent correction of partner source.

## Q10 — Referenced evaluation artifacts are not all present (`MEDIUM`)

Written instructions refer to evaluation documentation/runner artifacts that are not present in the delivered ZIP.

Implication:

Do not invent them. The project can build its own runner from the supplied cases/scenarios, but should keep the missing-reference discrepancy in the package audit.

## Q11 — Some narrative identity/role descriptions differ from seeded cases (`MEDIUM`)

Examples exist where support-ticket prose describes a role differently from the actual `agent-input` case/user mapping. One action scenario appears deliberately aligned to the executable permission requirements in the seed rather than the older prose description.

Rule:

Identity/permission evaluation must use the actual bound case user + `/users/me` semantics, while prose differences remain provenance notes.

## Q12 — Machine reference paths and narrative scenarios differ materially (`HIGH`)

`eval/expected-paths.json` is a compact reference, while the narrative scenarios include additional evidence acquisition, policies, expected resolutions and action expectations.

Implication:

- exact path sequence is not the canonical oracle;
- ScenarioSchema v1 must normalize both sources;
- narrative P1 success criterion and policies are more important for semantic correctness than raw sequence exact-match;
- machine paths remain useful for expected-tool/evidence diagnostics.

## Q13 — Model-visible `seed` would compromise benchmark integrity (`CRITICAL`)

Because the API contract exposes `seed`, directly converting HTTP parameters to model-facing tools would let the model request favorable modes such as `complete`.

Required invariant:

> environment seed is runner/evaluator configuration and is not model-controlled.

The canonical tool adapter must remove/bind this parameter before tool exposure.

## Q14 — Model-visible `x-user-id` would compromise identity integrity (`CRITICAL`)

A model choosing the authentication/user header could impersonate a higher-privilege synthetic user.

Required invariant:

> case user identity is bound by the runner/session and is not model-controlled.

This is a benchmark-integrity/security boundary, not a model reasoning task.

## Q15 — Kickoff confirmation guidance is not encoded as a universal benchmark policy (`HIGH`)

The kickoff described confirmation before state-changing operations as a real-world safety practice. The supplied canonical execution scenarios, however, directly expect requested actions after the user request and do not model a separate confirmation turn.

Therefore:

- do **not** mark confirmation as a universal hard requirement of the canonical benchmark;
- preserve it as a guarded/safety architecture experiment or controlled adversarial variant;
- promote it to canonical policy only if written partner clarification or a scenario explicitly requires it.

This corrects an earlier pre-artifact research hypothesis.

## Q16 — External RAG is not justified by package scale (`MEDIUM`)

The package contains 5 knowledge documents and already exposes dedicated knowledge search/document endpoints.

Implication:

- direct structured/API retrieval is the baseline;
- external vector infrastructure remains conditional;
- only measured retrieval failures can justify dense/hybrid/reranked retrieval.

## Normalization policy

The raw partner package must remain immutable. Any project-derived corrected/normalized artifact must contain:

- source package SHA-256;
- source file hash;
- transformation version;
- explicit change list;
- normalized artifact hash;
- generator/tool version;
- conformance-test result.

This preserves reproducibility while preventing silent source rewriting.

## Architecture consequences

The package strongly motivates a **guarded contract-aware tool layer** as an experiment, but does not yet select its implementation framework.

The key controlled contrast should be whether typed validation, bound identity/environment context and deterministic resource/policy guards materially improve safety/correctness over a minimally wrapped baseline while preserving task success and reasonable latency/tool count.
