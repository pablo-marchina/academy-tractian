# Systematic Research Hub

Status: **ACTIVE — Research Gate not passed**

This directory is the evidence base for architecture and experiment decisions. Production implementation must not be treated as frozen while a high-impact research question remains unresolved.

## Research questions

| ID | Area | Core question | Status |
|---|---|---|---|
| R01 | Requirements | What must the final solution prove and deliver? | Active; formal two-track handling pending partner |
| R02 | Industrial domain | What evidence, entities, risks and actions exist in the TRACTIAN environment? | API-dependent |
| R03 | API/tool engineering | What is the safest and most evaluable way to expose the industrial API as tools? | Method advanced; Swagger-dependent spike pending |
| R04 | Agent runtime | Which orchestration approach gives the best reliability/control/traceability trade-off? | Runtime spike pending API |
| R05 | Planning/reasoning | ReAct, explicit graph, planner-executor, hybrid, or another policy? | Baseline/experiment method defined |
| R06 | Tool use | How should tool selection, arguments, ordering and stopping be engineered and measured? | Advanced; real-tool taxonomy pending |
| R07 | Evidence | When is evidence sufficient, conflicting, stale or incomplete? | Policy method active; API metadata pending |
| R08 | Abstention/escalation | When should the agent ask, investigate, act, abstain, or escalate? | First-class evaluation decision established |
| R09 | Safety/policy | Which constraints must be deterministically enforced outside the model? | Threat model advanced; API permissions/action classes pending |
| R10 | State/memory | What state should persist within and across interactions? | Wave 2 provisional architecture defined; API requirements pending |
| R11 | Models/routing | Which models/configurations are Pareto-optimal on our own benchmark? | Benchmark method defined; execution pending |
| R12 | Retrieval/RAG | Does retrieval add measurable value beyond structured API/knowledge resources? | Decision gate defined; corpus/API pending |
| R13 | Evaluation | What is the canonical source of truth for each dimension of correctness? | Advanced; executable oracle details pending API |
| R14 | Reliability/robustness | How should repeated trials and API fault profiles be evaluated? | Statistical method advanced; pilot pending |
| R15 | Security/red team | Which adversarial capabilities and prompt/tool attacks must be covered? | Wave 2 threat model defined; API specialization pending |
| R16 | Observability | What must every run emit so failures are attributable and reproducible? | OTel-first trace contract defined; backend spike pending |
| R17 | Optimization | What can be optimized only after the benchmark is stable? | Correctly deferred until benchmark freeze |
| R18 | Statistics | What comparisons, confidence intervals and uncertainty reporting are valid? | Method advanced; exact N/k pending pilot |
| R19 | Reproducibility | How do we reset, replay, version and reproduce experiments? | Method advanced; reset/snapshot API semantics pending |
| R20 | Demo/UI | What views best prove correctness, reliability and failure analysis? | Later |

## Evidence hierarchy

Priority order:

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

## Current provisional findings after Wave 2

These are **research conclusions, not frozen implementation choices**:

1. Side-effecting tasks should be evaluated against executable/final environment state whenever ground truth is available, not only against natural-language output.
2. Reliability requires repeated trials; one successful run is not sufficient evidence of dependable behavior.
3. Tool selection, argument correctness, trajectory, evidence use, policy compliance, final state and final response are distinct evaluation dimensions.
4. High-impact/mutating actions deserve stronger pre-execution verification than read-only actions.
5. `ask / investigate / act / abstain / escalate` are first-class outcomes and must be explicitly evaluated.
6. Authorization, permissions, schemas and hard policy constraints must not depend solely on prompt compliance.
7. Environment truth, workflow state, conversation state, optional persistent memory, evidence cache, model-visible context and trace logs are distinct planes.
8. Persistent cross-session memory is **off by default** until a real task requirement justifies it; scenario isolation is mandatory.
9. Model-visible context is a curated projection of state/evidence, not the source of truth.
10. OpenTelemetry-compatible tracing must exist from baseline zero with project-owned run/config/policy/evidence semantics; observability backend remains open.
11. Tool/retrieval outputs are data and do not inherit instruction authority.
12. Public model/tool leaderboards are candidate filters only; final model selection uses the project benchmark and Pareto analysis.
13. Adaptive routing is conditional on complementary model strengths demonstrated by validation data.
14. RAG/vector DB/reranking remain conditional on an actual corpus retrieval problem and project-specific retrieval gains.
15. Exact scenario count/repetition count is selected after an API-derived variance/cost pilot; repeated runs remain nested within scenario.
16. Multi-agent, MCP, prompt optimization and other complexity remain hypotheses until they demonstrate value or satisfy a hard requirement.

## Files

### Foundation / Wave 1

- `00-research-protocol.md` — methodology and Research Gate.
- `01-requirements-matrix.md` — TAPI requirements mapped to evidence/tests.
- `02-evidence-synthesis-wave-1.md` — first systematic synthesis.
- `03-candidate-stack-matrix.md` — framework and infrastructure shortlist.
- `04-evaluation-safety-reliability.md` — evaluation architecture and threat/reliability findings.
- `05-tractian-open-questions.md` — questions that cannot be resolved without partner/API information.
- `06-research-backlog.md` — remaining research work before architecture freeze.
- `07-statistical-plan-wave-1.md` — provisional quantitative/statistical protocol.
- `08-tool-use-planning-wave-1.md` — tool-use, planning, clarification and orchestration evidence.
- `09-openapi-tooling-wave-1.md` — contract-first API/tool boundary research.

### Wave 2

- `10-state-memory-context-wave-2.md` — state taxonomy, benchmark isolation and context policy.
- `11-observability-trace-wave-2.md` — OTel-first trace contract and backend decision method.
- `12-security-threat-model-wave-2.md` — layered capability/action threat model and adversarial families.
- `13-model-benchmark-wave-2.md` — project-native model benchmark and adaptive-routing gate.
- `14-retrieval-rag-decision-wave-2.md` — evidence-driven RAG/retrieval decision ladder.
- `15-sample-compute-budget-wave-2.md` — pilot-driven N/k and staged compute/statistical budget.
- `16-evidence-synthesis-wave-2.md` — consolidated Wave 2 findings and architecture constraints.

### Registry / decisions

- `sources.md` — reviewed primary/official source registry.
- `../docs/adr/000-template.md` — ADR template for architecture freeze decisions.

## Immediate next milestone

The next hard boundary is the TRACTIAN onboarding/API contract. Before then, remaining useful research should focus on refining questions, schemas and discriminating spike protocols—not inventing domain behavior that the project specification says will come from the supplied API.

After Swagger delivery, the priority sequence is: **API/domain mapping → canonical tools → evaluator/reset harness → trace baseline → runtime/MCP spikes → pilot/model screening → freeze statistical budget → architecture ADRs.**
