# Systematic Research Hub

Status: **ACTIVE — Research Gate not passed**

This directory is the evidence base for architecture and experiment decisions. Production implementation must not be treated as frozen while a high-impact research question remains unresolved.

## Research questions

| ID | Area | Core question | Status |
|---|---|---|---|
| R01 | Requirements | What must the final solution prove and deliver? | Active |
| R02 | Industrial domain | What evidence, entities, risks and actions exist in the TRACTIAN environment? | Active; API-dependent |
| R03 | API/tool engineering | What is the safest and most evaluable way to expose the industrial API as tools? | Active |
| R04 | Agent runtime | Which orchestration approach gives the best reliability/control/traceability trade-off? | Active |
| R05 | Planning/reasoning | ReAct, explicit graph, planner-executor, hybrid, or another policy? | Active |
| R06 | Tool use | How should tool selection, arguments, ordering and stopping be engineered and measured? | Active |
| R07 | Evidence | When is evidence sufficient, conflicting, stale or incomplete? | Active |
| R08 | Abstention/escalation | When should the agent ask, investigate, act, abstain, or escalate? | Active |
| R09 | Safety/policy | Which constraints must be deterministically enforced outside the model? | Active |
| R10 | State/memory | What state should persist within and across interactions? | Active |
| R11 | Models/routing | Which models/configurations are Pareto-optimal on our own benchmark? | Pending benchmark |
| R12 | Retrieval/RAG | Does retrieval add measurable value beyond structured API/knowledge resources? | Pending API/corpus |
| R13 | Evaluation | What is the canonical source of truth for each dimension of correctness? | Active |
| R14 | Reliability/robustness | How should repeated trials and API fault profiles be evaluated? | Active |
| R15 | Security/red team | Which adversarial capabilities and prompt/tool attacks must be covered? | Active |
| R16 | Observability | What must every run emit so failures are attributable and reproducible? | Active |
| R17 | Optimization | What can be optimized only after the benchmark is stable? | Active |
| R18 | Statistics | What comparisons, confidence intervals and uncertainty reporting are valid? | Active |
| R19 | Reproducibility | How do we reset, replay, version and reproduce experiments? | Active; API-dependent |
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

## Current provisional findings

These are **research conclusions, not frozen implementation choices**:

1. Side-effecting tasks should be evaluated against executable/final environment state whenever ground truth is available, not only against natural-language output.
2. Reliability requires repeated trials; one successful run is not sufficient evidence of dependable behavior.
3. Tool selection, argument correctness, trajectory, evidence use, policy compliance, final state and final response are distinct evaluation dimensions.
4. High-impact/mutating actions deserve stronger pre-execution verification than read-only actions.
5. `ask / investigate / act / abstain / escalate` should be first-class outcomes and explicitly evaluated.
6. Safety boundaries such as authorization, permissions, schemas and prohibited actions should not depend solely on prompt compliance.
7. Observability must exist from the first executable baseline; adding logs after development loses experimental evidence.
8. Multi-agent, MCP, RAG, adaptive routing and prompt optimization remain hypotheses until they demonstrate value or satisfy a hard requirement.

## Files

- `00-research-protocol.md` — methodology and Research Gate.
- `01-requirements-matrix.md` — TAPI requirements mapped to evidence/tests.
- `02-evidence-synthesis-wave-1.md` — first systematic synthesis.
- `03-candidate-stack-matrix.md` — framework and infrastructure shortlist.
- `04-evaluation-safety-reliability.md` — evaluation architecture and threat/reliability findings.
- `05-tractian-open-questions.md` — questions that cannot be resolved without partner/API information.
- `06-research-backlog.md` — remaining research work before architecture freeze.
- `sources.md` — reviewed primary/official source registry.
