# TRACTIAN Kickoff Evidence — 2026-08-13

Status: **SOURCE-DERIVED / TRANSCRIPT-NOISE-AWARE**

Source: user-provided automatic transcript of the TRACTIAN kickoff. The transcript is materially noisy, so this file separates strong statements from tentative interpretations. No garbled sentence is treated as a requirement without corroborating context.

## Evidence handling rule

Confidence labels:

- `HIGH`: clearly stated and repeated or strongly contextualized.
- `MEDIUM`: plausible and supported, but wording/transcription is imperfect.
- `LOW`: too noisy to rely on; kept only as a follow-up lead.

When kickoff guidance conflicts with the written TAPI or the eventual API contract, the written project/API evidence wins unless the partner explicitly supersedes it.

## High-confidence partner guidance

### KO-001 — Real target workflow is support/investigation automation

The intended agent mirrors an existing support-resolution workflow: receive a customer question/ticket, inspect the relevant platform/API evidence, identify likely cause, and produce a useful customer-facing resolution without requiring an analyst/engineer whenever the case is safely automatable.

**Project implication:** optimize for dependable ticket resolution and safe escalation, not for a generic autonomous industrial controller.

### KO-002 — The partner will provide evaluation supervision beyond only prompts

The partner states that students will receive a simplified API plus real customer-question-derived cases, including the trajectory followed by an engineer and the expected final output/conclusion.

**Project implication:** the benchmark should ingest partner-provided question, reference trajectory/evidence, and target conclusion as first-class provenance. Reference trajectory is valuable supervision/diagnostic evidence, but should not automatically make one exact read-only call sequence the only valid trajectory unless policy requires it.

### KO-003 — Evaluate the process, not only the final answer

The kickoff explicitly emphasizes that an agent may produce a wrong conclusion because it selected the wrong API/tool, omitted context, experienced an API problem, or took a wrong intermediate step. Therefore the evaluation framework must inspect the path that produced the final answer.

**Project implication:** preserve separate evaluators for final conclusion, tool selection, arguments, evidence coverage, trajectory, failures and policy compliance.

### KO-004 — Final semantic conclusion matters more than exact wording

The partner explains that the “ideal response” is primarily about solving the customer’s doubt and reaching the same conclusion/decision as the engineer; exact tone or wording is secondary.

**Project implication:** do not use exact-string similarity as the primary final-answer metric. Extract/score conclusion facts and decision outcome; separately evaluate communication policy.

### KO-005 — Customer-facing answers must avoid unnecessary internal implementation detail

The partner explicitly says the customer does not need the internal “kitchen” of the service and that exposing unnecessary internal system details can make an otherwise correct answer poor.

**Project implication:** add a customer-safe communication oracle: required conclusion/action facts plus forbidden/unnecessary internal-detail disclosure. This is distinct from factual correctness.

### KO-006 — Conservative escalation on insufficient/ambiguous evidence

A simple partner rule is stated: if there is not enough data to conclude, or the case remains meaningfully ambiguous, send it to human analysis rather than pretending certainty.

**Project implication:** `ESCALATE` is not an exception path; it is a correct target outcome for defined scenarios. The benchmark must include false-action vs false-escalation trade-offs.

### KO-007 — Escalation handoff must minimize human rework

When escalating, the agent should pass the evidence it collected, the analysis already performed, what is contradictory or unresolved, and why a human is needed so that the engineer can continue from that point instead of restarting the investigation.

**Project implication:** add escalation-quality evaluation: evidence package completeness, unresolved-question clarity, reason-for-escalation and absence of unsupported conclusion.

### KO-008 — State-changing actions require explicit confirmation

The partner gives examples such as deleting an insight or changing platform/status data and says they normally request confirmation from the requester before performing actions that change platform data.

**Project implication:** confirmation/approval becomes a hard precondition candidate for mutating actions, independently of LLM confidence. Final API semantics will determine exact action classes.

### KO-009 — Integration should expose a stable agent-facing contract

The partner recommends that the agent should interact through one consistent interface even if underlying sources differ (API, RPC-like service, object/file source, etc.), while warning against over-generalizing the project.

**Project implication:** this strongly supports the existing `Canonical ToolSpec -> runtime adapter / optional MCP adapter` direction. MCP is a possible uniform interface, not automatically required.

### KO-010 — Existing workflow must fail safely when the LLM/agent fails

The partner’s enterprise guidance is that inserting an agent into an existing flow must not break the original process if the LLM fails or makes a mistake; a new feature should not become a new vulnerability.

**Project implication:** design fallback/escalation and bounded failure as production qualities, and measure them in fault-injection scenarios.

### KO-011 — Prevent benchmark leakage

The kickoff explicitly compares agent evaluation to ML validation and warns against using the same cases for development/training and validation/final assessment.

**Project implication:** preserve grouped development/validation/locked-test splits and keep related variants in the same split group.

### KO-012 — Engineering decisions must be explainable by the student

The partner emphasizes understanding why an architectural choice was made, what alternatives existed and what trade-off justified the choice, rather than delegating the project to an AI tool without understanding it.

**Project implication:** ADRs and ablations are not documentation decoration; they are part of demonstrating engineering competence.

## Medium-confidence guidance requiring API/dataset confirmation

### KO-M01 — Provided synthetic entities are constructed around the provided use cases

The transcript strongly suggests that companies/users/assets in the simulation were created so the provided use cases have corresponding data and can be answered from the environment.

**Do not assume:** every adversarial case we invent is answerable from the base environment. Synthetic extensions may need controlled fixtures/fault injection.

### KO-M02 — Severe source contradiction may not be common in the supplied base cases

The partner says real production systems do contain conflicting/legacy-source situations, but the supplied simulation likely will not contain anything “that contradictory”.

**Project implication:** distinguish:

- partner benchmark / natural cases; and
- project-authored adversarial contradiction cases.

Do not claim partner cases contain conflict until dataset inspection confirms it.

### KO-M03 — Partner-provided case count may be roughly 14–20 and may need explicit split

One speaker recalls approximately 14–20 tests/cases and recommends dividing them so some are used for development and others for final validation.

**Confidence:** medium/low because the speaker explicitly says they do not remember the exact packaging.

**Project implication:** do not freeze `N`, `k` or split sizes from this statement. Inspect the delivered dataset first.

### KO-M04 — Strongest model first, optimize cost/latency after value is demonstrated

The partner describes an internal engineering philosophy of first proving that a flow works using the strongest practical models, then optimizing latency/cost once value is demonstrated, with latency constraints depending on synchronous vs offline use cases.

**Project implication:** this is valuable experimental guidance but **not yet a student model-provider permission**. Keep the external-model-access question open until project constraints are explicit.

## Low-confidence / transcript-corrupted details

Do not use the transcript alone to claim:

- exact setup command names;
- exact model names available to students;
- exact token-consumption numbers;
- exact number of dataset splits;
- exact current internal TRACTIAN architecture;
- exact API transport mix;
- exact contradictions/failure probabilities.

These require direct artifact/API evidence or a clarification.

## Benchmark changes unlocked by kickoff

The benchmark should now explicitly model the following outputs/oracles:

1. **Target conclusion** — same operational diagnosis/decision as the gold case, not same prose.
2. **Reference investigation** — engineer trajectory/evidence as supervision and diagnostic comparison.
3. **Customer communication policy** — enough context to resolve the doubt, without unnecessary internal implementation leakage.
4. **Escalation oracle** — insufficient/ambiguous evidence can require human review.
5. **Escalation package oracle** — collected evidence, attempted analysis, unresolved point/contradiction, escalation reason.
6. **Mutation confirmation oracle** — state-changing action requires confirmation where the API/action policy says so.
7. **Fallback oracle** — system fails safely and does not break the existing process when agent/tool/model execution fails.

## Proposed ScenarioSchema v1 additions after dataset/API inspection

Do not change the machine schema solely from a noisy transcript. When the actual cases arrive, validate whether v1 should add explicit fields such as:

```yaml
communication_oracle:
  target_conclusion: []
  required_facts: []
  forbidden_internal_disclosures: []

escalation_oracle:
  required: false
  required_evidence_refs: []
  required_unresolved_points: []
  require_reason: true

policy_oracle:
  confirmation_required_for: []
```

Existing `required_facts`, `forbidden_claims`, `preconditions`, `required_decisions` and evidence fields can already represent these semantics if a schema extension proves unnecessary.

## Questions resolved or narrowed by kickoff

Strongly resolved/narrowed:

- Partner provides canonical/reference cases rather than requiring students to author everything.
- Evaluation must cover intermediate process/trajectory as well as final output.
- Final response target is semantic conclusion/decision, not exact text.
- Ambiguity/insufficient evidence is a legitimate reason to escalate.
- Escalation should contain useful investigation context.
- State-changing actions should have a confirmation boundary.
- A stable agent-facing integration contract is desirable.
- Dataset leakage must be actively prevented.

Still open until artifacts/API arrive:

- exact case count and split packaging;
- exact API/tool catalog and permissions;
- exact mutation/high-impact mapping;
- exact confirmation semantics per endpoint;
- reset/snapshot/idempotency support;
- precise stochastic behavior;
- model/provider constraints for students;
- whether hidden evaluation cases exist;
- exact scoring/weighting expected by the partner.

## Architecture consequences

The kickoff strengthens rather than overturns Waves 1–3:

- `ScenarioSchema` + `TraceSchema` remain the correct stable experiment contracts.
- Canonical tools with optional MCP exposure are more strongly motivated.
- Deterministic authorization/confirmation gates are more strongly motivated.
- `ASK / INVESTIGATE / ACT / ABSTAIN / ESCALATE` remains the correct decision space.
- Evaluation must distinguish conclusion correctness from communication quality.
- Reference engineer trajectories should become a diagnostic/evidence oracle, not blindly an exact-sequence oracle.
- Reliability, regression testing and locked test sets are central partner concerns.
- Safe fallback is a production-facing metric, not only an implementation detail.

## Next evidence boundary

Do not freeze architecture from the kickoff transcript. The next authoritative inputs are the actual Swagger/OpenAPI contract, provided use-case/golden-set artifacts, setup/reset behavior and any written partner guidance.
