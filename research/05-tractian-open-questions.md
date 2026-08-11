# TRACTIAN / Inteli Open Questions

These questions cannot be safely resolved from the TAPI alone. They are **not implementation blockers for generic research**, but they block architecture freeze and/or experimental validity.

Priority legend: `P0` = must resolve at/near onboarding; `P1` = needed before final benchmark; `P2` = useful clarification.

## A. Formal academic scope

| Priority | Question | Why it matters |
|---|---|---|
| P0 | May the final submission formally claim both tracks, or must exactly one be declared primary? | TAPI says solution in one track, while our integrated scope covers both |
| P0 | If one track must be primary, can a complete evaluation framework be an integral subsystem of the construction track and count toward the rubric? | Submission framing |
| P1 | Is there any expected minimum/maximum scope, endpoint coverage or scenario count not written in the TAPI? | Prevent over/under-scoping |
| P1 | Are there restrictions on external/open-source frameworks or model providers beyond the suggested free/open feasibility guidance? | Stack/model shortlist |

## B. API contract and authentication

| Priority | Question | Why it matters |
|---|---|---|
| P0 | Can we receive the complete OpenAPI/Swagger contract and example payloads? | Tool/schema architecture |
| P0 | What authentication mechanism is used? | Client architecture/security |
| P0 | Are there separate environments/credentials per student? | Reproducibility/isolation |
| P1 | Are there rate limits, quotas or concurrency limits? | Experiment design |
| P1 | Are endpoint behaviors/versioning expected to change during the project? | Contract pinning/regression |
| P1 | Are errors fully documented in the OpenAPI schema or only successful responses? | Fault handling |

## C. State, side effects and reset

| Priority | Question | Why it matters |
|---|---|---|
| P0 | Which endpoints mutate platform state? | Safety/evaluation |
| P0 | Which mutations are considered high-impact? | Risk policy |
| P0 | Can the environment be reset to a known baseline? Per company/user/scenario or globally? | Final-state evaluation/repeated runs |
| P0 | Is there a snapshot/clone mechanism for state? | Paired experiments/replay |
| P0 | Are side effects persistent across sessions/runs? | Dataset contamination |
| P0 | Are mutating actions idempotent? Is an idempotency key supported? | Duplicate-action safety |
| P1 | Can we query all relevant state needed to verify a mutation after execution? | Executable ground truth |
| P1 | Is there any destructive action that should never be invoked even in the synthetic environment? | Hard policy |

## D. Permissions and authority

| Priority | Question | Why it matters |
|---|---|---|
| P0 | How are user identity, role and permissions represented? | Deterministic authorization |
| P0 | Are permissions returned by the API, embedded in scenario context, or both? | Source of truth |
| P0 | Are there resource-level permissions (company/asset/action) or only coarse roles? | Policy evaluator |
| P0 | Does the API itself reject unauthorized actions, or is the agent expected to enforce policy before calling? | Safety boundary |
| P1 | Are there policies/rules not represented in Swagger? | Domain policy corpus |

## E. Probabilistic / uncertain query behavior

| Priority | Question | Why it matters |
|---|---|---|
| P0 | How is “partial information” represented in the response? Missing fields, flags, confidence, or content semantics? | Evidence evaluator/recovery |
| P0 | How is “inconclusive” represented? | Abstention/investigation policy |
| P0 | How is “conflict between sources” surfaced? | Conflict resolution benchmark |
| P0 | How is temporary unavailability represented? HTTP code, structured payload, timeout, or randomized behavior? | Retry/fault policy |
| P0 | Can randomness be seeded or controlled? | Reproducibility |
| P1 | Are probabilities fixed/documented by endpoint or scenario? | Reliability experiments |
| P1 | Does repeated querying change the probability or content distribution? | Evidence acquisition policy |
| P1 | Are there freshness/timestamps/version fields that let the agent reason about stale evidence? | Evidence quality |

## F. Data model and industrial semantics

| Priority | Question | Why it matters |
|---|---|---|
| P0 | What are the concrete entities and stable identifiers for company, user, assets, analyses, data/model resources and actions? | Scenario/state schema |
| P0 | What does asset criticality mean in the synthetic API and how is it encoded? | Risk/action prioritization |
| P0 | Which technical-signal fields are actually exposed and what interpretation is expected from students? | Avoid inventing domain logic |
| P0 | What does analysis confidence/limitation mean in the supplied data? | Evidence policy |
| P1 | Are there relationships/hierarchies that must be traversed (company → plant → asset, etc.)? | Tool planning |
| P1 | Are signal/spectrum values meant to be numerically interpreted or treated as simplified evidence supplied by the API? | Agent expertise boundary |
| P1 | Is there a ground-truth diagnosis/action encoded for scenarios? | Evaluation oracle |

## G. Knowledge and retrieval

| Priority | Question | Why it matters |
|---|---|---|
| P0 | What “knowledge” resources will the API expose: procedures, glossary, policies, troubleshooting guidance? | RAG decision |
| P0 | Is the knowledge corpus entirely accessible through API endpoints, or are documents/files also supplied? | Retrieval architecture |
| P1 | Does the corpus have stable IDs/version/timestamps/provenance? | Evidence trace |
| P1 | Are we expected to implement external RAG, or is it intentionally optional? | Avoid unnecessary complexity |
| P1 | May provided documents be indexed locally for experiments? | Storage/privacy |

## H. Recording, observability and experiment artifacts

| Priority | Question | Why it matters |
|---|---|---|
| P0 | May we persist request/response payloads from the synthetic API in the public GitHub repository? | Data handling |
| P0 | If not public, may we store them locally/private for replay? | Reproducibility |
| P0 | Are there any values that must be redacted from traces even though data is synthetic? | Telemetry schema |
| P1 | May we publish generated scenario fixtures derived from the API? | Benchmark reproducibility |
| P1 | Can API executions be recorded/replayed for model comparisons? | Controlled experiments |

## I. Model and compute constraints

| Priority | Question | Why it matters |
|---|---|---|
| P0 | Are external model APIs allowed? | Model shortlist |
| P0 | Are there partner-provided model endpoints/credits or required providers? | Experiment budget |
| P1 | Are fully local models preferred or merely suggested as a feasibility option? | Architecture/model routing |
| P1 | Are internet calls from the final demo environment permitted? | Demo reliability |

## J. Evaluation expectations

| Priority | Question | Why it matters |
|---|---|---|
| P0 | Will TRACTIAN provide canonical cases/expected outcomes, or must students author all scenarios? | Benchmark design |
| P0 | Are hidden evaluation cases used by the partner/instructors? | Generalization strategy |
| P1 | Does the rubric prioritize breadth of endpoint coverage or depth/quality of experiment? | Scope allocation |
| P1 | Is live API execution required during the final demo? | Demo architecture |
| P1 | Is a quantitative comparison against baseline expected or only encouraged? | Experimental planning |

## Onboarding output required

Immediately after onboarding, convert answers into:

1. versioned copy/reference of Swagger/OpenAPI;
2. `research/domain-model.md`;
3. `research/api-behavior.md`;
4. updated requirement matrix;
5. closed/open dependency table;
6. ADR candidates unlocked by the answers;
7. concrete minimal scenario set for framework spikes.

Do **not** close an item based on inference. Record the partner/API evidence supporting the answer.
