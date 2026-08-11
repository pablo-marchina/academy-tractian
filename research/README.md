# Systematic Research Hub

Status: **ACTIVE — Research Gate not passed**

This directory is the evidence base for architecture and experiment decisions. Production implementation must not be treated as frozen while a high-impact research question remains unresolved.

## Research questions

| ID | Area | Core question | Status after Wave 3 |
|---|---|---|---|
| R01 | Requirements | What must the final solution prove and deliver? | Formal two-track handling pending partner |
| R02 | Industrial domain | What evidence, entities, risks and actions exist in the TRACTIAN environment? | API-dependent |
| R03 | API/tool engineering | What is the safest/evaluable API→tool boundary? | OpenAPI audit + spike protocol ready; contract pending |
| R04 | Agent runtime | Which orchestrator best fits reliability/control/traceability? | Three finalists deeply reviewed; discriminating spike pre-registered |
| R05 | Planning/reasoning | ReAct, explicit graph, structured loop, hybrid? | Baseline/experiment method defined; API execution pending |
| R06 | Tool use | How should selection/args/order/stopping be engineered/measured? | Advanced; actual tool taxonomy pending |
| R07 | Evidence | When is evidence sufficient/conflicting/stale/incomplete? | Framework ready; API fields pending |
| R08 | Abstention/escalation | When ASK/INVESTIGATE/ACT/ABSTAIN/ESCALATE? | First-class evaluated outcome established |
| R09 | Safety/policy | Which constraints are deterministic outside model? | Threat/action-gate architecture advanced; real permissions pending |
| R10 | State/memory | What persists and what enters model context? | Wave 2 boundary defined; real task persistence pending |
| R11 | Models/routing | Which models are project-Pareto-optimal? | Benchmark method defined; execute after API/pilot |
| R12 | Retrieval/RAG | Does retrieval add measurable value? | Decision ladder defined; corpus pending |
| R13 | Evaluation | What is ground truth for each correctness surface? | `ScenarioSchema v0` now machine-readable; v1 awaits API |
| R14 | Reliability | How repeated trials/faults are evaluated? | Statistical design advanced; pilot pending |
| R15 | Security/red team | Which attacks/capabilities are covered? | Baseline threat model ready; API specialization pending |
| R16 | Observability | What must every run emit? | `TraceSchema v0` now machine-readable; runtime export spike pending |
| R17 | Optimization | What may be optimized after benchmark freeze? | Correctly deferred |
| R18 | Statistics | What inference/uncertainty reporting is valid? | Method advanced; exact N/k pending pilot |
| R19 | Reproducibility | How reset/replay/versioning work? | Manifest/trace requirements defined; API reset semantics pending |
| R20 | Demo/UI | What views prove rubric criteria? | Later |

## Evidence hierarchy

1. Project specification / TRACTIAN API contract and partner clarification.
2. Primary research papers and benchmark papers.
3. Protocol specifications and official standards.
4. Official framework/library documentation and source repositories.
5. Reproducible experiments in this repository.
6. Secondary sources only when no primary source exists.

## Decision rule

A technique/framework is not selected because it is popular or sophisticated. A decision should be backed by:

- explicit project requirement;
- evidence from primary/official sources;
- relevant trade-offs;
- a measurable hypothesis where alternatives are plausible;
- an ADR recording why alternatives were accepted/rejected.

## Current provisional findings after Wave 3

These are **research conclusions, not frozen implementation choices**:

1. Side-effecting tasks should be evaluated against executable/final environment state whenever ground truth exists.
2. Reliability requires repeated trials; scenario is the primary generalization unit.
3. Tool selection, arguments, trajectory, evidence, policy, final state and response are distinct correctness surfaces.
4. `ASK / INVESTIGATE / ACT / ABSTAIN / ESCALATE` are first-class evaluated decisions.
5. High-impact/mutating actions require stronger pre-execution and postcondition verification than reads.
6. Authorization, permissions, schemas and hard policy constraints must not depend solely on prompt compliance.
7. Environment truth, workflow state, session state, optional persistent memory, evidence cache, model context and trace log are distinct planes.
8. Persistent cross-session memory is **off by default** until a real requirement proves need; scenario isolation is mandatory.
9. Model-visible context is a curated projection, never the industrial source of truth.
10. Experiment contracts (`ScenarioSchema`, canonical tools/policy, `TraceSchema`, evaluators) must be more stable than the runtime/model.
11. `ScenarioSchema v0` separates state/policy/evidence/communication oracles from an optional reference trajectory.
12. `TraceSchema v0` records observable decisions/calls/policy/state/evidence and **does not require hidden chain-of-thought**.
13. OpenTelemetry is the interoperability layer; a project-owned `tractian.*` contract remains canonical while GenAI conventions evolve.
14. LangGraph, Pydantic AI and OpenAI Agents SDK all remain credible finalists; documentation alone does not select a winner.
15. Runtime selection has hard gates: pre-side-effect interception, correct pause/resume, deterministic tests, normalized traces, canonical tools, scenario isolation.
16. MCP Python SDK v2 / MCP 2026-07-28 is the current target if MCP is used; old session/legacy-SSE architecture is not the default for new code.
17. The strongest pre-API MCP topology is **canonical tools + optional MCP adapter**; MCP-first requires partner need or experimental evidence.
18. OpenAPI ingestion/audit is separate from code generation; raw contract + normative spec + conformance tests remain authoritative.
19. HTTP methods alone do not determine mutation/high-impact risk; unknown semantics stay `unknown` until contract/partner evidence resolves them.
20. Public model leaderboards filter candidates only; final model selection uses the project benchmark/Pareto analysis.
21. Adaptive routing, RAG, multi-agent and prompt optimization remain conditional hypotheses.
22. Exact scenario/repetition budget is selected after an API-derived variance/cost pilot, not guessed pre-Swagger.

## Files

### Foundation / Wave 1

- `00-research-protocol.md` — methodology and Research Gate.
- `01-requirements-matrix.md` — TAPI requirements mapped to evidence/tests.
- `02-evidence-synthesis-wave-1.md` — first systematic synthesis.
- `03-candidate-stack-matrix.md` — framework and infrastructure shortlist.
- `04-evaluation-safety-reliability.md` — evaluation architecture and threat/reliability findings.
- `05-tractian-open-questions.md` — partner/API dependencies.
- `06-research-backlog.md` — remaining research work before architecture freeze.
- `07-statistical-plan-wave-1.md` — provisional quantitative/statistical protocol.
- `08-tool-use-planning-wave-1.md` — tool-use/planning/clarification evidence.
- `09-openapi-tooling-wave-1.md` — contract-first API/tool research.

### Wave 2

- `10-state-memory-context-wave-2.md`
- `11-observability-trace-wave-2.md`
- `12-security-threat-model-wave-2.md`
- `13-model-benchmark-wave-2.md`
- `14-retrieval-rag-decision-wave-2.md`
- `15-sample-compute-budget-wave-2.md`
- `16-evidence-synthesis-wave-2.md`

### Wave 3 — pre-onboarding

- `17-runtime-deep-dive-wave-3.md` — finalist capabilities, risks and hard runtime gates.
- `18-mcp-python-sdk-wave-3.md` — current MCP revision/SDK v2 and topology experiment.
- `19-scenario-schema-v0-wave-3.md` — scenario semantics and oracle separation.
- `20-trace-schema-v0-wave-3.md` — canonical framework-neutral trace semantics.
- `21-discriminating-spikes-protocol-wave-3.md` — pre-registered runtime/MCP/client/backend spikes.
- `22-swagger-ingestion-audit-pipeline-wave-3.md` — same-day contract audit/inventory pipeline.
- `23-evidence-synthesis-wave-3.md` — Wave 3 synthesis and onboarding readiness.
- `schemas/scenario-v0.schema.json` — machine-readable ScenarioSchema v0.
- `schemas/trace-v0.schema.json` — machine-readable TraceSchema v0.

### Registry / decisions

- `sources.md` — reviewed primary/official source registry.
- `../docs/adr/000-template.md` — architecture decision template.

## Pre-onboarding boundary

Wave 3 closes the useful research that can be done without inventing the partner's API semantics. Remaining high-impact unknowns are now predominantly genuine TRACTIAN dependencies: Swagger/OpenAPI, entities, permissions/tenancy, mutation/high-impact taxonomy, reset/replay/idempotency, stochastic response semantics, freshness/version metadata, rate limits and knowledge corpus.

## Onboarding/API execution sequence

**Acquire/hash contract → OpenAPI audit → resolve P0 semantic questions → API-MAP-v0 → ScenarioSchema v1 → canonical client/ToolSpec → evaluator/reset/fault harness → TraceSchema v1 baseline → runtime/client/MCP spikes → statistical pilot/model screening → ADRs → FROZEN-v1.**
