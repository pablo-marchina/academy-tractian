# Research Backlog Before Architecture Freeze

This is the execution queue for the systematic research phase. Items are ordered by expected impact on architecture and experimental validity.

## P0 — Before / immediately after TRACTIAN onboarding

### R01 — Requirements audit

- [x] Extract explicit TAPI requirements.
- [x] Map rubric to verification evidence.
- [ ] Confirm formal handling of the two tracks.
- [ ] Confirm any hidden/implicit delivery constraints with instructors/partner.

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
- [ ] Define transport/fault-injection boundary.
- [ ] Define read-only vs mutating tool metadata.

### R04 — Safety/policy model

- [x] Establish provisional principle: model proposes, deterministic policy authorizes.
- [ ] Map actual permissions and high-impact actions.
- [ ] Define hard invariants.
- [ ] Define mutation-gated verification experiment.
- [ ] Define HITL/escalation policy if relevant.

### R05 — Evaluation oracle design

- [x] Establish final-state oracle preference for side-effect tasks.
- [ ] Determine which state can actually be queried/reset.
- [ ] Define scenario schema v1 from real API entities.
- [ ] Define tool/argument/trajectory/evidence/policy evaluators.
- [ ] Define evaluator validation tests.

## P1 — Architecture decision research

### R06 — Runtime comparison spike

Finalists after documentation review: LangGraph, Pydantic AI/Graph, OpenAI Agents SDK; Google ADK/AutoGen retained as references/candidates if requirements justify.

- [ ] Implement identical minimal contract in finalists.
- [ ] Measure pre-side-effect interception.
- [ ] Measure state persistence/resume.
- [ ] Measure fake-tool/fake-model testability.
- [ ] Measure OTel trace completeness.
- [ ] Measure model-provider portability.
- [ ] Measure framework overhead/complexity.
- [ ] Write ADR-001.

### R07 — MCP ADR

- [x] Review current 2026-07-28 specification.
- [ ] Review current Python SDK v2 implementation surface.
- [ ] Compare native-only vs canonical-tools+MCP-adapter vs MCP-first.
- [ ] Measure schema fidelity and latency/complexity overhead.
- [ ] Verify trace propagation/security boundaries.
- [ ] Write ADR-002.

### R08 — Single vs multi-agent

- [x] Evidence review indicates multi-agent should not be assumed.
- [ ] Define failure condition that would justify decomposition.
- [ ] Establish strong single structured baseline first.
- [ ] Only run planner/executor or specialist experiment if failure analysis motivates it.
- [ ] Write ADR when evidence exists.

### R09 — State and memory

- [ ] Distinguish transient step state, conversation state, user/session state, cached evidence and long-term memory.
- [ ] Determine what the task actually requires to persist.
- [ ] Research stale-context/context-cleaning strategies.
- [ ] Define reset semantics for evaluation.
- [ ] Prevent cross-scenario contamination.

### R10 — Evidence acquisition / stopping

- [ ] Formalize evidence sufficiency from API metadata.
- [ ] Compare fixed investigation vs adaptive investigate-until-sufficient policy.
- [ ] Define conflict handling policy.
- [ ] Define retry limits and stopping rule.
- [ ] Study whether a calibrated uncertainty/risk predictor is justified beyond rule-based policy.

## P1 — Benchmark and quantitative method

### R11 — Gold dataset methodology

- [ ] Define scenario families from real endpoint/action taxonomy.
- [ ] Define pairwise controlled perturbations (act vs abstain, full vs partial, authorized vs unauthorized, etc.).
- [ ] Define scenario QA checklist.
- [ ] Define versioning and change log.
- [ ] Group split by base scenario/template to prevent leakage.
- [ ] Lock final test set before optimization.

### R12 — Reliability protocol

- [x] Repeated trials required.
- [ ] Select `k` using compute/statistical budget.
- [ ] Define success/reliability aggregation precisely.
- [ ] Define treatment of infrastructure failures.
- [ ] Define scenario-level vs run-level uncertainty.

### R13 — Statistical plan

- [ ] Review binomial confidence-interval options.
- [ ] Review paired binary comparison methods for same scenarios.
- [ ] Review cluster/repeated-run bootstrap options.
- [ ] Define effect sizes for latency/tool calls.
- [ ] Define multiple-comparison policy across models/configurations.
- [ ] Define minimum sample/compute budget.
- [ ] Define sensitivity analysis for scenario weighting.
- [ ] If confidence/risk prediction is used: calibration curve, Brier/log score, ECE limitations and threshold-selection protocol.

### R14 — Baselines and ablations

- [ ] Minimal direct tool-calling baseline.
- [ ] ReAct-style baseline if distinct from native loop.
- [ ] Structured-state candidate.
- [ ] Add deterministic gates.
- [ ] Add mutation-specific verification.
- [ ] Add adaptive evidence/abstention policy.
- [ ] Only later test routing/prompt optimization.
- [ ] Pre-register ablation matrix.

## P1 — Security / red team

### R15 — Threat model

- [x] Prompt/tool-output injection recognized.
- [x] Capability/permission enforcement must not be prompt-only.
- [ ] Map attack surface to actual API resources.
- [ ] Add cross-user/company/resource access cases if API supports it.
- [ ] Add high-impact mutation cases.
- [ ] Define safe trace redaction.
- [ ] Define security severity categories.

### R16 — Red-team tooling

- [x] Promptfoo identified as leading complementary candidate.
- [ ] Verify local target integration.
- [ ] Verify OTel trajectory evidence.
- [ ] Build project-specific plugins/assertions for forbidden tool/args/policy.
- [ ] Compare generated attacks vs hand-authored adversarial gold cases.

## P1 — Observability and reproducibility

### R17 — Trace schema

- [x] OTel-first principle established.
- [ ] Review current GenAI/MCP semantic conventions in detail.
- [ ] Define project-specific attributes: scenario_id, run_id, config_hash, policy_decision, evidence_ids, state_version, mutation flag, fault profile.
- [ ] Define sensitive-content recording/redaction policy.
- [ ] Ensure all runtime finalists can export equivalent traces.

### R18 — Observability backend ADR

- [x] Phoenix identified as first candidate.
- [ ] Compare Phoenix vs Langfuse vs framework-native options on local self-host, experiment UX, OTel support, storage, replay and resource footprint.
- [ ] Select backend only after trace schema is framework-neutral.

### R19 — Replay/reproducibility

- [ ] Define configuration hash.
- [ ] Record model/provider/version/parameters/prompt/tool contract/API contract.
- [ ] Define random seed where providers support it; do not claim determinism when they do not.
- [ ] Define API observation recording/replay policy.
- [ ] Define environment state reset and experiment isolation.
- [ ] Container/environment strategy ADR.

## P2 — Conditional techniques

### R20 — Retrieval/RAG

- [ ] Inspect actual knowledge resources.
- [ ] If needed, define no-RAG baseline.
- [ ] Compare sparse/dense/hybrid retrieval using evidence-recall and task metrics.
- [ ] Add reranker only if retrieval evidence shows need.
- [ ] Choose vector/search backend only after strategy wins.

### R21 — Model benchmark / routing

- [ ] Shortlist tool-capable accessible models after API complexity is known.
- [ ] Use BFCL/official capability docs only for candidate filtering.
- [ ] Run same validation scenarios across candidates.
- [ ] Build Pareto frontier: quality/reliability/safety/latency/resource use.
- [ ] Test adaptive routing only if heterogeneous model strengths create opportunity.

### R22 — Prompt/policy optimization

- [ ] Freeze valid objective first.
- [ ] Establish manual baseline.
- [ ] Evaluate DSPy/GEPA only on development/validation.
- [ ] Evaluate Optuna for thresholds/routing/runtime parameters if search space warrants it.
- [ ] Preserve hard safety constraints outside optimization objective.

### R23 — Demo research

- [ ] Define the minimal visualization that proves every rubric criterion.
- [ ] Compare Streamlit/Gradio vs custom UI only if needed.
- [ ] Ensure demo includes state before/after, trace, reliability and fault/adversarial comparison.

## Research Gate completion definition

Research phase is complete only when:

1. all P0 questions are resolved;
2. all architecture-changing P1 questions are resolved or have completed discriminating experiments;
3. remaining P2 choices are either rejected as unnecessary or have a clearly scheduled experiment;
4. ADRs describe final `FROZEN-v1` architecture;
5. no material researchable unknown remains undocumented.
