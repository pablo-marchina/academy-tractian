# Research Backlog Before Architecture Freeze

This is the execution queue for the systematic research phase. Items are ordered by expected impact on architecture and experimental validity.

## Scope update — 2026-08-13

The updated TAPI explicitly requires both **Construção de agente** and **Framework de avaliação de agentes**. The previous track-selection ambiguity is resolved.

## P0 — Before / immediately after TRACTIAN onboarding

### R01 — Requirements audit

- [x] Extract explicit TAPI requirements.
- [x] Map rubric to verification evidence.
- [x] Confirm formal handling of the two tracks: both are required by the updated TAPI.
- [ ] Confirm any additional delivery constraints with instructors/partner.

### R02 — API/domain discovery

- [ ] Import/version the OpenAPI/Swagger contract.
- [ ] Enumerate every endpoint by read vs mutate, entity, permission and risk.
- [ ] Build entity/relation map from actual schemas.
- [ ] Identify all fields related to confidence, limitation, quality, freshness and conflict.
- [ ] Confirm reset/snapshot/replay capabilities.
- [ ] Confirm API stochastic behavior and whether seeds/control exist.
- [ ] Document auth/rate limits.

### R03 — Canonical tool boundary

- [ ] Compare generated OpenAPI client vs manual typed client.
- [ ] Define one canonical tool schema independent of agent runtime.
- [ ] Verify Pydantic/JSON Schema fidelity against Swagger.
- [x] Define conceptual transport/fault-injection boundary.
- [x] Establish requirement for read-only vs mutating tool metadata.

### R04 — Evaluation and safety architecture

- [x] Confirm evaluation framework is mandatory under updated TAPI.
- [x] Establish principle: model proposes, deterministic policy authorizes.
- [x] Establish final-state oracle preference for state-changing tasks.
- [ ] Map actual permissions and high-impact actions.
- [ ] Determine which state can actually be queried/reset.
- [ ] Define scenario schema v1 from real API entities.
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
- [ ] Write ADR.

### MCP

- [x] Review current protocol revision and Python SDK direction.
- [ ] Compare native-only vs canonical-tools+MCP-adapter vs MCP-first.
- [ ] Measure schema fidelity and latency/complexity overhead.
- [ ] Write ADR.

### State and memory

- [x] Separate environment state, execution state, conversation state, optional persistent memory, evidence cache, model context and trace log.
- [x] Persistent cross-session memory OFF by default pending real need.
- [ ] Validate persistence/reset semantics against actual API.

### Evidence acquisition and stopping

- [x] Treat stale/conflicting/incomplete evidence as first-class state.
- [ ] Formalize sufficiency from actual API metadata.
- [ ] Compare fixed investigation vs adaptive investigation.
- [ ] Define retry/stopping rules.

## P1 — Benchmark and quantitative method

- [x] Controlled-pair methodology.
- [x] Group split by base scenario/template.
- [x] Locked final test before optimization.
- [x] Repeated trials required.
- [x] Scenario is primary generalization unit.
- [x] Live vs replay vs fault-injection separated.
- [x] Statistical methodology defined provisionally.
- [ ] Define scenario families from real API.
- [ ] Run pilot and freeze exact N/k.
- [ ] Pre-register final baselines and ablations.

## P1 — Observability and reproducibility

- [x] OTel-first principle.
- [x] Project-owned scenario/run/config/policy/evidence/state semantics.
- [x] ScenarioSchema v0 and TraceSchema v0 created.
- [ ] Implement v1 against real API.
- [ ] Define exact replay/reset format.
- [ ] Complete observability backend ADR.

## P2 — Conditional techniques

### Retrieval/RAG

- [x] RAG remains conditional on an actual retrieval problem.
- [ ] Inspect actual knowledge resources.
- [ ] Run retrieval ladder only if needed.

### Models/routing

- [x] Public benchmarks are candidate filters only.
- [x] Project-native Pareto benchmark methodology defined.
- [ ] Run candidate comparison after API/pilot.
- [ ] Test routing only if complementary strengths are observed.

### Optimization

- [ ] Freeze valid objective first.
- [ ] Establish manual baseline.
- [ ] Evaluate automated optimization only on development/validation if useful.

### Demo

- [x] Final framing must visibly demonstrate both mandatory components.
- [ ] Define UI/views that prove agent execution plus per-run and aggregate evaluation evidence.

## Research Gate completion definition

Research phase is complete only when:

1. all P0 questions are resolved;
2. all architecture-changing P1 questions are resolved or experimentally discriminated;
3. remaining P2 choices are either rejected as unnecessary or have a clearly scheduled experiment;
4. ADRs describe final `FROZEN-v1` architecture;
5. no material researchable unknown remains undocumented.

## Immediate execution sequence

1. TRACTIAN onboarding + Swagger/API acquisition.
2. API/domain/action/permission/risk mapping.
3. Canonical typed tool boundary + reset/fault harness.
4. ScenarioSchema v1 + deterministic evaluators.
5. TraceSchema v1 + OTel baseline.
6. Runtime + MCP discriminating spikes.
7. Statistical pilot + model screening.
8. Freeze N/k/splits and run architecture experiments.
9. Conditional RAG/memory/routing experiments only if justified.
10. ADR set → `FROZEN-v1` architecture.
