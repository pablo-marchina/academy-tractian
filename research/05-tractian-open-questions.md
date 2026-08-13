# TRACTIAN / Inteli Open Questions

These are the remaining partner/API questions after the TAPI update of 2026-08-13.

## Resolved by the updated TAPI

The project no longer has a one-track-vs-two-tracks ambiguity. The updated objective explicitly requires a solution containing both **Construção de agente** and **Framework de avaliação de agentes**.

## Remaining P0 questions for onboarding

### API contract

- Can we receive the complete OpenAPI/Swagger contract and example payloads?
- What authentication mechanism is used?
- Are there separate environments/credentials per student?
- Are there rate limits or quotas relevant to experiments?

### State and actions

- Which endpoints change platform state?
- Which actions are considered high impact?
- Can the environment be reset to a known baseline?
- Is snapshot/clone/replay available?
- Are state-changing actions idempotent?
- Can all relevant state be queried after execution so we can verify postconditions?

### Permissions

- How are user identity, roles and permissions represented?
- Are permissions resource-specific or role-level?
- Is authorization enforced by the API, expected from the agent, or both?
- Are there domain rules not represented in Swagger?

### Probabilistic behavior

- How are partial, inconclusive and conflicting results represented?
- How is temporary unavailability represented?
- Can randomness be seeded or controlled?
- Are there freshness, timestamp or version fields?

### Industrial semantics

- What are the concrete entities and stable identifiers?
- How is asset criticality represented?
- Which technical-signal fields are exposed and what interpretation is expected?
- What do analysis confidence and limitation fields mean?
- Is there ground-truth diagnosis/action information for scenarios?

### Knowledge

- What knowledge resources are provided?
- Is knowledge entirely exposed through API endpoints or are documents/files supplied too?
- Does knowledge have stable provenance/version metadata?

### Experiment artifacts

- Which API request/response artifacts may be stored for reproducibility?
- Are any values required to be removed from traces/artifacts?
- May generated scenario fixtures be versioned in the repository?
- Can observations be recorded and replayed for controlled model comparisons?

### Models and compute

- Are external model APIs allowed?
- Are partner-provided model endpoints/credits available or required?
- Are fully local models preferred or merely suggested?
- Are internet calls allowed in the final demo environment?

### Evaluation expectations

- Will TRACTIAN provide canonical cases/expected outcomes, or must all scenarios be authored by students?
- Are hidden evaluation cases used?
- Does the rubric favor endpoint breadth, experiment depth, or a balance?
- Is live API execution required during the final demo?
- Are there any minimum scenario/endpoint coverage expectations not written in the TAPI?

## Onboarding output required

Immediately after onboarding, convert answers into:

1. versioned Swagger/OpenAPI reference;
2. `research/domain-model.md`;
3. `research/api-behavior.md`;
4. updated requirement matrix;
5. closed/open dependency table;
6. ADR candidates unlocked by answers;
7. concrete minimal scenario set for framework spikes.

Do not close an item by inference. Record the partner/API evidence supporting each answer.
