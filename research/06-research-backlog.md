# Research Backlog Before Architecture Freeze

This is the execution queue for the systematic research phase. Items are ordered by expected impact on architecture and experimental validity.

## Wave 3 checkpoint

Pre-onboarding work now complete:

- [x] deep-review runtime finalists against project-specific gates;
- [x] review current MCP 2026-07-28 + Python SDK v2 implementation surface;
- [x] define machine-readable `ScenarioSchema v0`;
- [x] define machine-readable `TraceSchema v0`;
- [x] pre-register runtime/MCP/client/observability discriminating spikes;
- [x] define Swagger/OpenAPI ingestion + audit pipeline;
- [x] separate contract audit from generated-client choice.

Remaining blockers are primarily actual API/partner dependencies or experiments that cannot be validly executed until the contract arrives.

## P0 — Before / immediately after TRACTIAN onboarding

### R01 — Requirements audit

- [x] Extract explicit TAPI requirements.
- [x] Map rubric to verification evidence.
- [ ] Confirm formal handling of the two tracks.
- [ ] Confirm any hidden/implicit delivery constraints with instructors/partner.

### R02 — API/domain discovery

- [x] Define version-aware OpenAPI intake/audit methodology and output artifacts.
- [ ] Import/archive/hash the supplied OpenAPI/Swagger contract.
- [ ] Enumerate every endpoint by entity, effective security and semantics.
- [ ] Classify read/mutate/high-impact/idempotency with provenance; do not infer from HTTP method alone.
- [ ] Build entity/relation map from actual schemas.
- [ ] Identify confidence/limitation/quality/freshness/conflict fields.
- [ ] Confirm reset/snapshot/replay/idempotency capabilities.
- [ ] Confirm stochastic behavior and whether seeds/control exist.
- [ ] Document auth/rate limits.

### R03 — Canonical tool boundary

- [x] Establish one project-owned ToolSpec boundary independent of runtime/protocol.
- [x] Define transport/fault-injection boundary.
- [x] Require mutation/high-impact/risk/permission metadata outside generic model descriptions.
- [x] Pre-register generated-client vs project-owned client spike.
- [ ] Derive ToolSpec candidate schemas from actual Swagger.
- [ ] Compare compatible generated clients vs project-owned typed adapter.
- [ ] Verify JSON Schema fidelity against the supplied contract.
- [ ] Write client/tool ADR.

### R04 — Safety/policy model

- [x] Model proposes; deterministic policy authorizes.
- [x] Define layered pre-execution/postcondition architecture.
- [x] Define severity/adversarial families provisionally.
- [x] Define mutation boundary as a hard runtime-spike gate.
- [ ] Map actual permissions/tenancy/high-impact actions.
- [ ] Define API-specific hard invariants.
- [ ] Execute mutation-gated verification experiment.
- [ ] Finalize HITL/escalation policy from real action classes.

### R05 — Evaluation oracle design

- [x] Establish final-state oracle preference for side effects.
- [x] Define `ScenarioSchema v0` separating policy/evidence/state/communication/trajectory oracles.
- [x] Add controlled-pair and split-group semantics.
- [ ] Determine which environment state can be queried/reset.
- [ ] Instantiate `ScenarioSchema v1` with real entities/predicates.
- [ ] Implement tool/argument/trajectory/evidence/policy evaluators.
- [ ] Validate evaluator correctness with golden tests.

## P1 — Architecture decision research

### R06 — Runtime comparison spike

Finalists: **LangGraph, Pydantic AI/Graph, OpenAI Agents SDK**. ADK/AutoGen remain references unless requirements reopen the shortlist.

- [x] Define framework-neutral state/context/trace requirements.
- [x] Deep-review each finalist's current persistence/HITL/testing/provider/trace surfaces.
- [x] Pre-register identical runtime spike scenarios and hard gates.
- [x] Include restart tests immediately before/after mutation boundary.
- [ ] Implement identical minimal contract in finalists after API map.
- [ ] Measure pre-side-effect interception.
- [ ] Measure pause/state persistence/resume and duplicate-side-effect behavior.
- [ ] Measure deterministic fake-model/fake-tool testability.
- [ ] Measure normalized trace completeness.
- [ ] Measure provider portability and framework-only overhead/complexity.
- [ ] Write ADR-001.

### R07 — MCP ADR

- [x] Review MCP 2026-07-28 specification/security changes.
- [x] Review current Python SDK v2 stable-line semantics.
- [x] Reject legacy-session/SSE assumptions for new-path architecture.
- [x] Establish canonical-tools + optional MCP adapter as leading pre-API topology hypothesis.
- [x] Pre-register native-vs-MCP adapter spike.
- [ ] Measure schema/result/policy equivalence and overhead.
- [ ] Verify W3C trace propagation/security boundary in live spike.
- [ ] Promote MCP-first only if partner requirement/evidence justifies it.
- [ ] Write ADR-002.

### R08 — Single vs multi-agent

- [x] Evidence review indicates multi-agent must not be assumed.
- [ ] Establish strong single structured baseline first.
- [ ] Define failure-analysis trigger that would justify decomposition.
- [ ] Only test planner/executor/specialists if failures motivate it.
- [ ] Write ADR if decomposition is evaluated.

### R09 — State and memory

- [x] Separate environment state, workflow state, session state, optional persistent memory, evidence cache, model context and trace.
- [x] Persistent cross-session memory OFF by default.
- [x] Per-scenario namespaces/reset required.
- [x] Curated-context/staleness principles defined.
- [ ] Determine actual task persistence needs.
- [ ] Validate reset/freshness/version semantics against API.
- [ ] Run context-memory experiment only if required.
- [ ] Write ADR.

### R10 — Evidence acquisition / stopping

- [x] Observable metadata/rules before learned confidence.
- [x] Stale/conflicting evidence first-class.
- [ ] Formalize sufficiency/conflict rules from actual API metadata.
- [ ] Compare fixed investigation vs adaptive investigate-until-sufficient.
- [ ] Freeze retry/stopping rule.
- [ ] Test calibrated risk predictor only after rule baseline if justified.

## P1 — Benchmark and quantitative method

### R11 — Gold dataset methodology

- [x] Controlled-pair methodology.
- [x] Group split by base scenario/template.
- [x] Locked final test before optimization.
- [x] Encode pair/split metadata in ScenarioSchema v0.
- [ ] Define families from actual endpoint/action taxonomy.
- [ ] Finalize scenario QA checklist/versioning after API map.

### R12 — Reliability protocol

- [x] Repeated trials mandatory.
- [x] Scenario is primary clustering/generalization unit.
- [x] Live vs replay vs fault-injection are distinct modes.
- [x] Exact `k` selected from pilot variability + budget.
- [ ] Run pilot and select `k`.
- [ ] Freeze final aggregation/infra-failure denominator policy.

### R13 — Statistical plan

- [x] Wilson interval for ordinary proportions; conservative bound for zero severe events.
- [x] Exact McNemar candidate for paired binary comparison.
- [x] Scenario-level/cluster-aware bootstrap principle.
- [x] Effect-size, multiple-comparison, macro/micro/per-family reporting principles.
- [x] Staged sample/compute-budget selection procedure.
- [ ] Run API-derived pilot and freeze exact N/k/precision.

### R14 — Baselines and ablations

- [ ] Minimal direct/native tool-calling baseline.
- [ ] ReAct-style baseline if genuinely distinct.
- [ ] Structured-state candidate.
- [ ] + deterministic gates.
- [ ] + mutation-specific verification.
- [ ] + adaptive evidence/abstention policy.
- [ ] routing/RAG/prompt optimization only later if justified.
- [ ] Pre-register final ablation matrix after API mapping.

## P1 — Security / red team

### R15 — Threat model

- [x] Prompt/tool-output injection recognized.
- [x] Capability/permission enforcement not prompt-only.
- [x] Protected assets/trust boundaries/severity defined provisionally.
- [x] Memory poisoning, trace leakage, boundedness and MCP surfaces included.
- [x] Proposal vs unsafe execution separated in evaluation.
- [ ] Map threats to actual API resources/tenants/actions.
- [ ] Finalize safe trace redaction from actual payloads.

### R16 — Red-team tooling

- [x] Hand-authored project adversarial gold cases are canonical; generated attacks complementary.
- [x] Promptfoo retained as leading complementary candidate.
- [ ] Verify local integration after target exists.
- [ ] Build project assertions for forbidden tools/args/policy.

## P1 — Observability and reproducibility

### R17 — Trace schema

- [x] OTel-first principle.
- [x] Current GenAI conventions reviewed; project namespace/version pinning required.
- [x] Define `TraceSchema v0` and machine-readable schema.
- [x] Explicitly exclude hidden chain-of-thought from canonical trace requirements.
- [x] Define canonical operation taxonomy and trace-completeness concept.
- [x] Define metadata-first redaction policy.
- [ ] Instantiate `TraceSchema v1` after real payload review.
- [ ] Make all runtime finalists export equivalent normalized traces.
- [ ] Validate cardinality/redaction/storage on real payloads.

### R18 — Observability backend ADR

- [x] Phoenix and Langfuse retained as serious candidates.
- [x] Backend is downstream/non-canonical.
- [x] Pre-register same-trace backend comparison.
- [ ] Export same normalized traces and compare fidelity/footprint/UX/exportability.
- [ ] Write ADR.

### R19 — Replay/reproducibility

- [x] Required run/version manifest defined in TraceSchema v0.
- [x] No false determinism claims for providers.
- [x] API observation replay separated from live mode.
- [x] Per-scenario isolation required.
- [ ] Implement configuration hash/manifest.
- [ ] Define observation replay format after Swagger.
- [ ] Define actual environment reset semantics.
- [ ] Container/environment ADR.

## P2 — Conditional techniques

### R20 — Retrieval/RAG

- [x] RAG conditional on actual unstructured/mixed retrieval need.
- [x] Experiment ladder: structured/direct → sparse → dense → hybrid → rerank if diagnostics justify.
- [ ] Inspect actual knowledge resources and execute ladder only if needed.
- [ ] Choose backend only after strategy wins.

### R21 — Model benchmark / routing

- [x] Public benchmark/provider docs are filters only.
- [x] Fair project-native/Pareto selection protocol defined.
- [x] Routing tested only if complementary model strengths appear.
- [ ] Re-verify accessible tool-capable candidates immediately before experiment.
- [ ] Run project benchmark and Pareto analysis.
- [ ] Test routing only if justified.

### R22 — Prompt/policy optimization

- [ ] Freeze valid objective first.
- [ ] Establish manual baseline.
- [ ] Evaluate DSPy/GEPA only on development/validation if useful.
- [ ] Evaluate Optuna only if parameter search warrants it.
- [ ] Keep hard safety constraints outside optimizer control.

### R23 — Demo research

- [ ] Define minimal visualization proving every rubric criterion.
- [ ] Compare Streamlit/Gradio/custom only if needed.
- [ ] Show state before/after, trace, reliability and fault/adversarial comparisons.

## Research Gate completion definition

Research phase is complete only when:

1. all P0 questions are resolved;
2. all architecture-changing P1 questions are resolved or discriminating experiments completed;
3. remaining P2 choices are rejected as unnecessary or experimentally scheduled;
4. ADRs describe final `FROZEN-v1` architecture;
5. no material researchable unknown remains undocumented.

## Immediate execution sequence after API arrival

1. Archive/hash/validate Swagger and generate `API-MAP-v0` reports.
2. Resolve permission/mutation/reset/stochasticity P0 questions with TRACTIAN.
3. Instantiate ScenarioSchema v1 + real evaluators/reset/fault harness.
4. Implement canonical typed client/ToolSpec.
5. Implement baseline-zero TraceSchema v1/OTel adapter.
6. Run client + runtime + MCP discriminating spikes.
7. Run API-derived statistical pilot + model screening.
8. Freeze N/k/splits and architecture experiment matrix.
9. Run conditional RAG/memory/routing/multi-agent experiments only if failures/requirements justify them.
10. ADR set → `FROZEN-v1`.
