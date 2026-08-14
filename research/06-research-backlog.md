# Research Backlog Before Architecture Freeze

This is the execution queue for the systematic research phase. Items are ordered by expected impact on architecture and experimental validity.

## Scope update — 2026-08-13

The updated TAPI explicitly requires both **Construção de agente** and **Framework de avaliação de agentes**. The kickoff further clarified the intended support-resolution workflow and evaluation expectations. See `25-kickoff-evidence-2026-08-13.md`.

## P0 — Immediately after TRACTIAN kickoff

### R01 — Requirements audit

- [x] Extract explicit TAPI requirements.
- [x] Map rubric to verification evidence.
- [x] Confirm formal handling of the two tracks: both are required by the updated TAPI.
- [x] Capture kickoff-derived guidance with confidence labels.
- [ ] Resolve remaining delivery/model/demo constraints from artifacts or follow-up.

### R02 — API/domain discovery

- [ ] Import/version/hash the OpenAPI/Swagger contract.
- [ ] Enumerate every endpoint by read vs mutate, entity, permission and risk.
- [ ] Build entity/relation map from actual schemas.
- [ ] Identify all fields related to confidence, limitation, quality, freshness and conflict.
- [ ] Confirm reset/snapshot/replay capabilities.
- [ ] Confirm API stochastic behavior and whether seeds/control exist.
- [ ] Document auth/rate limits.
- [ ] Verify which use cases are guaranteed answerable from seeded state.

### R03 — Canonical case / golden-set ingestion

- [x] Partner clarified that canonical cases include question/request, engineer reference trajectory and expected final conclusion/output.
- [x] Establish that final conclusion and intermediate process are separate evaluation targets.
- [ ] Inventory exact case count and source format.
- [ ] Determine whether partner supplies official splits.
- [ ] Ingest cases with provenance and immutable hashes.
- [ ] Map reference trajectories to required evidence/tools vs optional equivalent paths.
- [ ] Extract target conclusion facts/decision from free-text gold responses.
- [ ] Identify any hidden-test policy.
- [ ] Group related variants to prevent leakage.

### R04 — Canonical tool boundary

- [ ] Compare generated OpenAPI client vs manual typed client.
- [ ] Define one canonical tool schema independent of agent runtime.
- [ ] Verify Pydantic/JSON Schema fidelity against Swagger.
- [x] Define conceptual transport/fault-injection boundary.
- [x] Establish requirement for read-only vs mutating tool metadata.
- [x] Kickoff strengthens a stable agent-facing integration contract across underlying sources.

### R05 — Evaluation and safety architecture

- [x] Confirm evaluation framework is mandatory under updated TAPI.
- [x] Establish principle: model proposes, deterministic policy authorizes.
- [x] Establish final-state oracle preference for state-changing tasks.
- [x] Add customer-facing conclusion vs communication-quality separation.
- [x] Add escalation-package quality as an evaluation dimension.
- [x] Add safe fallback as a fault/reliability outcome.
- [ ] Map actual permissions and high-impact actions.
- [ ] Determine exact actions requiring requester confirmation.
- [ ] Determine which state can actually be queried/reset.
- [ ] Define ScenarioSchema v1 from real API/canonical cases.
- [ ] Define API-specific evaluators and validation tests.

## P1 — Architecture decisions

### Runtime comparison

Finalists: LangGraph, Pydantic AI/Graph, OpenAI Agents SDK.

- [x] Define framework-neutral state/context/trace requirements.
- [ ] Implement identical minimal contract in finalists.
- [ ] Measure pause/resume and pre-action interception.
- [ ] Measure deterministic testability.
- [ ] Measure normalized trace completeness.
- [ ] Measure model-provider portability.
- [ ] Measure framework overhead/complexity.
- [ ] Measure safe fallback when model/tool execution fails.
- [ ] Write ADR.

### MCP / integration topology

- [x] Review current protocol revision and Python SDK direction.
- [x] Kickoff explicitly supports maintaining one stable agent-facing integration contract.
- [ ] Compare native-only vs canonical-tools+MCP-adapter vs MCP-first.
- [ ] Measure schema fidelity and latency/complexity overhead.
- [ ] Write ADR.

### State and memory

- [x] Separate environment state, execution state, conversation state, optional persistent memory, evidence cache, model context and trace log.
- [x] Persistent cross-session memory OFF by default pending real need.
- [ ] Validate persistence/reset semantics against actual API.

### Evidence acquisition, stopping and escalation

- [x] Treat stale/conflicting/incomplete evidence as first-class state.
- [x] Kickoff supports conservative escalation when evidence remains insufficient or meaningfully ambiguous.
- [ ] Formalize sufficiency from actual API metadata/canonical cases.
- [ ] Compare fixed investigation vs adaptive investigation.
- [ ] Define retry/stopping rules.
- [ ] Define exact escalation package schema/evaluator from provided cases.

### Mutation confirmation

- [x] Kickoff indicates platform-changing actions should have an explicit requester-confirmation boundary.
- [ ] Map confirmation requirements to actual actions/endpoints.
- [ ] Implement deterministic confirmation gate.
- [ ] Test missing/ambiguous/withdrawn confirmation and duplicate-replay cases.

## P1 — Benchmark and quantitative method

- [x] Controlled-pair methodology.
- [x] Group split by base scenario/template.
- [x] Locked final test before optimization.
- [x] Repeated trials required.
- [x] Scenario is primary generalization unit.
- [x] Live vs replay vs fault-injection separated.
- [x] Statistical methodology defined provisionally.
- [x] Kickoff explicitly reinforces leakage prevention/regression testing.
- [ ] Define scenario families from real API and partner case taxonomy.
- [ ] Run pilot and freeze exact N/k.
- [ ] Pre-register final baselines and ablations.
- [ ] Decide conclusion-scoring method for free-text gold responses.
- [ ] Decide whether/how to score reference trajectory deviations without over-penalizing equivalent valid reads.

## P1 — Customer communication evaluation

- [x] Exact wording/tone is not the primary target; operational conclusion is.
- [x] Unnecessary exposure of internal implementation/service details is undesirable.
- [ ] Derive required conclusion facts from canonical gold answers.
- [ ] Define deterministic forbidden-disclosure patterns where possible.
- [ ] Determine where semantic/LLM judging is unavoidable and validate the judge.
- [ ] Separate `conclusion_correctness` from `communication_policy_compliance` in reports.

## P1 — Observability and reproducibility

- [x] OTel-first principle.
- [x] Project-owned scenario/run/config/policy/evidence/state semantics.
- [x] ScenarioSchema v0 and TraceSchema v0 created.
- [ ] Implement v1 against real API/cases.
- [ ] Define exact replay/reset format.
- [ ] Complete observability backend ADR.
- [ ] Preserve reference engineer trajectory/evidence provenance without requiring hidden chain-of-thought.

## P2 — Conditional techniques

### Retrieval/RAG

- [x] RAG remains conditional on an actual retrieval problem.
- [ ] Inspect actual knowledge resources.
- [ ] Run retrieval ladder only if needed.

### Models/routing

- [x] Public benchmarks are candidate filters only.
- [x] Project-native Pareto benchmark methodology defined.
- [x] Kickoff partner philosophy favors proving value/quality before later cost/latency optimization, but student provider permissions remain unconfirmed.
- [ ] Confirm student model/provider constraints.
- [ ] Run candidate comparison after API/pilot.
- [ ] Test routing only if complementary strengths are observed.

### Optimization

- [ ] Freeze valid objective first.
- [ ] Establish manual baseline.
- [ ] Evaluate automated optimization only on development/validation if useful.

### Demo

- [x] Final framing must visibly demonstrate both mandatory components.
- [ ] Define UI/views that prove agent execution plus per-run and aggregate evaluation evidence.
- [ ] Include at least one successful autonomous resolution, one correct escalation/handoff, one blocked/unconfirmed mutation and one fault/fallback example.

## Research Gate completion definition

Research phase is complete only when:

1. all P0 questions are resolved;
2. all architecture-changing P1 questions are resolved or experimentally discriminated;
3. remaining P2 choices are either rejected as unnecessary or have a clearly scheduled experiment;
4. ADRs describe final `FROZEN-v1` architecture;
5. no material researchable unknown remains undocumented.

## Immediate execution sequence

1. Acquire Swagger/API + canonical case/golden-set artifacts.
2. Hash/audit API contract and inventory dataset.
3. Map domain/actions/permissions/risk/confirmation semantics.
4. Canonical typed tool boundary + reset/fault harness.
5. ScenarioSchema v1 + conclusion/evidence/trajectory/escalation/communication/state evaluators.
6. TraceSchema v1 + OTel baseline.
7. Runtime + MCP/client discriminating spikes.
8. Statistical pilot + model screening.
9. Freeze N/k/splits and run architecture experiments.
10. Conditional RAG/memory/routing experiments only if justified.
11. ADR set → `FROZEN-v1` architecture.
