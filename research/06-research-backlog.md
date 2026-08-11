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
- [x] Define conceptual transport/fault-injection boundary.
- [x] Establish requirement for read-only vs mutating tool metadata.

### R04 — Safety/policy model

- [x] Establish provisional principle: model proposes, deterministic policy authorizes.
- [x] Define layered pre-execution/postcondition security architecture conceptually.
- [x] Define severity model and adversarial scenario families provisionally.
- [ ] Map actual permissions and high-impact actions.
- [ ] Define API-specific hard invariants.
- [ ] Define mutation-gated verification experiment against real tools.
- [ ] Define HITL/escalation policy if relevant.

### R05 — Evaluation oracle design

- [x] Establish final-state oracle preference for side-effect tasks.
- [ ] Determine which state can actually be queried/reset.
- [ ] Define scenario schema v1 from real API entities.
- [ ] Define tool/argument/trajectory/evidence/policy evaluators against actual API.
- [ ] Define evaluator validation tests.

## P1 — Architecture decision research

### R06 — Runtime comparison spike

Finalists after documentation review: LangGraph, Pydantic AI/Graph, OpenAI Agents SDK; Google ADK/AutoGen retained as references/candidates if requirements justify.

- [x] Define framework-neutral state/context/trace requirements for the spike.
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
- [x] Review current security requirements (token passthrough, audience validation, least privilege, SSRF considerations).
- [ ] Review current Python SDK v2 implementation surface.
- [ ] Compare native-only vs canonical-tools+MCP-adapter vs MCP-first.
- [ ] Measure schema fidelity and latency/complexity overhead.
- [ ] Verify trace propagation/security boundaries in spike.
- [ ] Write ADR-002.

### R08 — Single vs multi-agent

- [x] Evidence review indicates multi-agent should not be assumed.
- [ ] Define failure condition that would justify decomposition.
- [ ] Establish strong single structured baseline first.
- [ ] Only run planner/executor or specialist experiment if failure analysis motivates it.
- [ ] Write ADR when evidence exists.

### R09 — State and memory

- [x] Distinguish environment state, execution state, conversation state, persistent memory, evidence cache, model context and trace log.
- [x] Establish persistent cross-session memory OFF by default pending task requirement.
- [x] Establish explicit per-scenario namespaces/reset to prevent contamination.
- [x] Research long-context/context-cleaning strategies and define curated-context hypothesis.
- [x] Define stale evidence/cache provenance and invalidation requirements conceptually.
- [ ] Determine what the real TRACTIAN tasks actually require to persist.
- [ ] Validate reset/freshness/version semantics against the API.
- [ ] Run context strategy experiment only if long interactions justify it.
- [ ] Write state/memory ADR.

### R10 — Evidence acquisition / stopping

- [x] Establish that evidence sufficiency must use observable metadata/rules before learned confidence.
- [x] Establish stale/conflicting evidence as first-class state.
- [ ] Formalize evidence sufficiency from actual API metadata.
- [ ] Compare fixed investigation vs adaptive investigate-until-sufficient policy.
- [ ] Define API-specific conflict handling policy.
- [ ] Define retry limits and stopping rule.
- [ ] Study calibrated uncertainty/risk predictor only after rule baseline.

## P1 — Benchmark and quantitative method

### R11 — Gold dataset methodology

- [x] Establish controlled pair methodology (act vs abstain, complete vs partial, authorized vs non-authorized, etc.).
- [x] Establish group split by base scenario/template to prevent leakage.
- [x] Establish locked final test before optimization.
- [ ] Define scenario families from real endpoint/action taxonomy.
- [ ] Define scenario QA checklist against API semantics.
- [ ] Define versioning and change log implementation.

### R12 — Reliability protocol

- [x] Repeated trials required.
- [x] Establish scenario as primary generalization/clustering unit.
- [x] Establish live vs replay vs fault-injection as separate experiment modes.
- [x] Define that exact `k` is chosen from pilot variability + budget rather than guessed now.
- [ ] Run pilot and select `k`.
- [ ] Define final success/reliability aggregation precisely from real scenario structure.
- [ ] Finalize denominator treatment of infrastructure failures.

### R13 — Statistical plan

- [x] Review binomial confidence-interval options; Wilson preferred for ordinary proportions, conservative exact/binomial bound for zero severe events.
- [x] Review paired binary comparison; exact McNemar candidate for small discordant counts.
- [x] Review paired/cluster-aware bootstrap; scenario-level resampling principle established.
- [x] Define effect-size families for latency/tool calls and binary outcomes.
- [x] Define multiple-comparison principle; pre-register primary family and use correction such as Holm when interpreted jointly.
- [x] Define staged sample/compute-budget selection procedure.
- [x] Define scenario macro/micro/per-family sensitivity reporting.
- [x] If risk prediction is used: calibration curves, Brier/log score and selective-risk evaluation required.
- [ ] Run API-derived pilot and freeze exact N/k/precision targets.

### R14 — Baselines and ablations

- [ ] Minimal direct tool-calling baseline.
- [ ] ReAct-style baseline if distinct from native loop.
- [ ] Structured-state candidate.
- [ ] Add deterministic gates.
- [ ] Add mutation-specific verification.
- [ ] Add adaptive evidence/abstention policy.
- [ ] Only later test routing/prompt optimization.
- [ ] Pre-register final ablation matrix after API mapping.

## P1 — Security / red team

### R15 — Threat model

- [x] Prompt/tool-output injection recognized.
- [x] Capability/permission enforcement must not be prompt-only.
- [x] Define pre-API protected assets, trust boundaries and attack surfaces.
- [x] Define provisional security severity categories.
- [x] Add memory poisoning, trace leakage, boundedness and optional MCP/programmatic-tool surfaces.
- [x] Define prompt-only vs deterministic-gate vs mutation-verification experiment structure.
- [ ] Map attack surface to actual API resources/tenants.
- [ ] Add API-specific cross-user/company/resource access cases if supported.
- [ ] Add API-specific high-impact mutation cases.
- [ ] Finalize safe trace redaction from actual payloads.

### R16 — Red-team tooling

- [x] Promptfoo identified as leading complementary candidate.
- [x] Establish hand-authored project-specific adversarial gold cases as canonical, generated attacks only complementary.
- [ ] Verify local Promptfoo target integration.
- [ ] Verify OTel trajectory evidence.
- [ ] Build project-specific assertions for forbidden tool/args/policy.
- [ ] Compare generated attacks vs hand-authored adversarial gold cases.

## P1 — Observability and reproducibility

### R17 — Trace schema

- [x] OTel-first principle established.
- [x] Review current GenAI semantic conventions; note active-development status and require version pinning.
- [x] Define project-owned identifiers/semantics for scenario, run, config, policy, mutation, evidence, state and fault profiles.
- [x] Define metadata-first sensitive-content/redaction principles.
- [x] Define canonical trace-completeness test for runtime finalists.
- [ ] Implement normalized trace schema v1.
- [ ] Ensure all runtime finalists export equivalent traces in spike.
- [ ] Validate cardinality/redaction on real payloads.

### R18 — Observability backend ADR

- [x] Phoenix identified as strong candidate.
- [x] Langfuse added as serious comparison candidate.
- [x] Establish backend as downstream/non-canonical; project-owned experiment artifacts remain source of truth.
- [ ] Export same normalized test traces to Phoenix and Langfuse.
- [ ] Compare local self-host footprint, OTel fidelity, experiment UX, exportability and replay/debug value.
- [ ] Select backend in ADR.

### R19 — Replay/reproducibility

- [x] Define required configuration/version manifest fields conceptually.
- [x] Define no false determinism claim when providers lack guaranteed determinism.
- [x] Establish API observation replay as separate mode for isolating agent/model reasoning.
- [x] Establish per-scenario state isolation requirement.
- [ ] Implement configuration hash.
- [ ] Define exact API observation recording/replay format after Swagger.
- [ ] Define environment reset from actual API semantics.
- [ ] Container/environment strategy ADR.

## P2 — Conditional techniques

### R20 — Retrieval/RAG

- [x] Establish RAG as conditional on an actual unstructured/mixed retrieval problem.
- [x] Define experiment ladder: structured/direct → sparse → dense → hybrid → rerank only if diagnostics justify it.
- [x] Define retrieval component metrics plus end-to-end task metrics.
- [x] Establish permission/provenance requirements and “live mutable state stays in API” principle.
- [ ] Inspect actual knowledge resources.
- [ ] If needed, construct labeled retrieval query/evidence set.
- [ ] Run retrieval ladder only if direct/structured baseline is insufficient.
- [ ] Choose vector/search backend only after strategy wins.

### R21 — Model benchmark / routing

- [x] Define public benchmark/provider docs as candidate filters only.
- [x] Define fair project-native model comparison contract.
- [x] Define staged screening/development/validation/locked-test process.
- [x] Define Pareto vector: quality/reliability/safety/latency/resource use.
- [x] Define routing gate: test only if validation reveals complementary model strengths.
- [x] Define model/version drift recording requirement.
- [ ] Re-verify current accessible tool-capable model shortlist immediately before experiment.
- [ ] Run same scenarios across candidates.
- [ ] Build project Pareto frontier.
- [ ] Test adaptive routing only if justified.

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

## Immediate execution sequence

1. TRACTIAN onboarding + Swagger/API acquisition.
2. API/domain/action/permission/risk mapping.
3. Canonical typed tool boundary + fault/reset harness.
4. Deterministic evaluator/scenario schema v1.
5. Normalized OTel trace implementation.
6. Runtime + MCP discriminating spikes.
7. API-derived pilot + model screening + compute estimate.
8. Freeze N/k/splits and run validation architecture experiments.
9. Conditional RAG/memory/routing experiments only if real failures/requirements justify them.
10. ADR set → `FROZEN-v1` architecture.
