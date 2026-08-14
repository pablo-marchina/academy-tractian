# TRACTIAN / Inteli Open Questions

These are the remaining partner/API questions after the updated TAPI and the 2026-08-13 kickoff.

The kickoff transcript is noisy. Only clearly stated points are marked resolved; exact API/dataset semantics remain open until written artifacts arrive.

## Resolved by updated TAPI / kickoff

- Both **Construção de agente** and **Framework de avaliação de agentes** are required.
- TRACTIAN intends to provide canonical/reference cases derived from real customer questions rather than requiring students to author the entire benchmark from scratch.
- The provided supervision is expected to include the question/request, engineer investigation/reference trajectory and expected final output/conclusion.
- Evaluation is expected to inspect intermediate tool/process behavior as well as the final answer.
- Final-answer target is primarily the operational conclusion/decision, not exact wording.
- Insufficient/meaningfully ambiguous evidence is a legitimate reason for human escalation.
- Escalation should carry collected evidence/analysis and the unresolved reason so the human does not restart from zero.
- State-changing platform actions should have an explicit confirmation/approval boundary; exact endpoint coverage remains API-dependent.
- Development/final-evaluation leakage must be prevented.
- A stable agent-facing integration contract is desirable; no requirement to over-generalize every possible backend.

See `25-kickoff-evidence-2026-08-13.md` for confidence-aware evidence notes.

## Remaining P0 questions / artifacts

### API contract

- Receive/import the complete OpenAPI/Swagger contract and example payloads.
- What authentication mechanism is used?
- Are there separate environments/credentials per student?
- Are there rate limits or quotas relevant to experiments?

### State and actions

- Which endpoints change platform state?
- Which actions are considered high impact?
- Exactly which mutations require confirmation/approval?
- Can the environment be reset to a known baseline?
- Is snapshot/clone/replay available?
- Are state-changing actions idempotent or protected by an idempotency mechanism?
- Can all relevant state be queried after execution so postconditions can be verified?

### Permissions

- How are user identity, roles and permissions represented?
- Are permissions resource-specific or role-level?
- Is authorization enforced by the API, expected from the agent, or both?
- Are there domain rules not represented in Swagger?

### Probabilistic behavior

- How are partial and inconclusive results represented?
- Does the delivered dataset/API actually contain conflicting-source cases, or should conflict be project-authored adversarial coverage only?
- How is temporary unavailability represented?
- Can randomness be seeded or controlled?
- Are there freshness, timestamp or version fields?

### Industrial semantics

- What are the concrete entities and stable identifiers?
- How is asset criticality represented?
- Which technical-signal fields are exposed and what interpretation is expected?
- What do analysis confidence and limitation fields mean?
- Is there structured ground truth for diagnosis/action in addition to free-text target responses?

### Knowledge

- What knowledge resources are provided?
- Is knowledge entirely exposed through API endpoints or are documents/files supplied too?
- Does knowledge have stable provenance/version metadata?

### Canonical cases / golden set

- What is the exact number of provided cases? The kickoff transcript contains an uncertain recollection of roughly 14–20; do not rely on it.
- What fields/formats contain question, engineer trajectory, reference evidence and target answer/conclusion?
- Are partner-provided cases already split into development/validation/test, or must students create the split?
- Are there hidden evaluation cases?
- Is the engineer trajectory intended as a strict required sequence, a reference path, or supervision for required evidence/tool checks?
- Are all provided use cases guaranteed answerable from the seeded synthetic environment?

### Experiment artifacts

- Which API request/response artifacts may be stored for reproducibility?
- Are any values required to be removed from traces/artifacts?
- May generated scenario fixtures be versioned in the repository?
- Can observations be recorded and replayed for controlled model comparisons?

### Models and compute

The kickoff described a TRACTIAN internal philosophy of using the strongest practical model to prove value before optimizing cost/latency, but this does **not** by itself establish student provider permissions.

- Are external model APIs allowed for students?
- Are partner-provided model endpoints/credits available or required?
- Are fully local/open models preferred, required, or merely suggested?
- Are internet calls allowed in the final demo environment?

### Evaluation expectations

- Does the partner provide any formal scoring/weighting beyond the cases/targets?
- Does the rubric favor endpoint breadth, experiment depth, or a balance?
- Is live API execution required during the final demo?
- Are there minimum scenario/endpoint coverage expectations not written in the TAPI?
- How should customer-facing disclosure of internal implementation details be judged: hard forbidden rules, case-specific annotations, or qualitative evaluation?

## Immediate post-artifact output required

As soon as Swagger and canonical cases are available, convert them into:

1. versioned Swagger/OpenAPI reference + hash;
2. `research/domain-model.md`;
3. `research/api-behavior.md`;
4. dataset/golden-set inventory and provenance report;
5. updated requirement matrix;
6. closed/open dependency table;
7. ScenarioSchema v1 mapping;
8. concrete minimal scenario set for runtime/MCP/client spikes;
9. evaluator oracle map: conclusion, evidence, trajectory, escalation, communication and state mutation.

Do **not** close an item by inference. Record the API/dataset/partner evidence supporting each answer.
