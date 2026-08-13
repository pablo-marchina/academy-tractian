# Systematic Research Hub

Status: **ACTIVE — Research Gate not passed**

This directory is the evidence base for architecture and experiment decisions. Production implementation is not frozen while a high-impact research question remains unresolved.

## TAPI scope update — 2026-08-13

The updated TAPI resolves the previous formal-scope ambiguity: the project must now contain **both**:

1. **Construção de agente**; and
2. **Framework de avaliação de agentes**.

This is now a confirmed requirement. The repository therefore keeps one integrated architecture in which the evaluation framework measures and drives development of the industrial agent. See `24-updated-tapi-impact-2026-08-13.md`.

## Research status

| ID | Area | Status |
|---|---|---|
| R01 | Requirements | Dual-track requirement resolved; minor delivery clarifications remain |
| R02 | Industrial domain | API-dependent |
| R03 | API/tool engineering | Audit + spike protocol ready; Swagger pending |
| R04 | Agent runtime | LangGraph, Pydantic AI/Graph and OpenAI Agents SDK remain finalists; spike pending |
| R05 | Planning/reasoning | Baseline and experiment method defined |
| R06 | Tool use | Method advanced; actual tool taxonomy pending |
| R07 | Evidence | Framework ready; actual metadata pending |
| R08 | Abstention/escalation | ASK / INVESTIGATE / ACT / ABSTAIN / ESCALATE established |
| R09 | Policy/action safety | Deterministic boundary concept established; actual permissions pending |
| R10 | State/memory | State planes separated; real persistence needs pending |
| R11 | Models/routing | Project-native Pareto benchmark defined; execution pending |
| R12 | Retrieval/RAG | Conditional decision ladder defined; corpus pending |
| R13 | Evaluation | ScenarioSchema v0 ready; v1 awaits API |
| R14 | Reliability | Repeated-run/statistical methodology defined; pilot pending |
| R15 | Adversarial testing | Pre-API threat/failure families defined; API specialization pending |
| R16 | Observability | TraceSchema v0 + OTel-first method defined |
| R17 | Optimization | Deferred until benchmark/objective freeze |
| R18 | Statistics | Method advanced; exact N/k pending pilot |
| R19 | Reproducibility | Replay/versioning method defined; reset semantics pending |
| R20 | Demo/UI | Must explicitly demonstrate both mandatory components |

## Current architecture invariants/hypotheses

These are research conclusions, not a frozen final stack:

1. Both agent construction and evaluation are mandatory and must be integrated.
2. State-changing tasks should use executable/final-state ground truth whenever available.
3. Reliability requires repeated trials; scenario is the primary generalization unit.
4. Tool choice, arguments, trajectory, evidence, policy, final state and final response are separate correctness surfaces.
5. ASK / INVESTIGATE / ACT / ABSTAIN / ESCALATE are first-class evaluated outcomes.
6. Model proposals do not replace deterministic schema/permission/policy checks.
7. High-impact/state-changing actions receive stronger pre-execution and postcondition checks.
8. Environment state is authoritative; model context is only a curated projection.
9. Persistent cross-session memory is off by default until the real task proves need.
10. ScenarioSchema, TraceSchema, evaluators and canonical tools should be more stable than model/runtime choices.
11. OpenTelemetry is an interoperability layer; project-owned experiment semantics remain canonical.
12. LangGraph, Pydantic AI/Graph and OpenAI Agents SDK still require the same discriminating spike before selection.
13. MCP remains conditional; canonical tools + optional adapter is the leading pre-API hypothesis.
14. OpenAPI audit is separate from code generation.
15. RAG, adaptive routing, multi-agent and automatic optimization remain conditional on measured value.
16. Exact sample/repetition budget will be selected from an API-derived pilot.

## Files

### Wave 1

- `00-research-protocol.md`
- `01-requirements-matrix.md`
- `02-evidence-synthesis-wave-1.md`
- `03-candidate-stack-matrix.md`
- `04-evaluation-safety-reliability.md`
- `05-tractian-open-questions.md`
- `06-research-backlog.md`
- `07-statistical-plan-wave-1.md`
- `08-tool-use-planning-wave-1.md`
- `09-openapi-tooling-wave-1.md`

### Wave 2

- `10-state-memory-context-wave-2.md`
- `11-observability-trace-wave-2.md`
- `12-security-threat-model-wave-2.md`
- `13-model-benchmark-wave-2.md`
- `14-retrieval-rag-decision-wave-2.md`
- `15-sample-compute-budget-wave-2.md`
- `16-evidence-synthesis-wave-2.md`

### Wave 3 — pre-onboarding

- `17-runtime-deep-dive-wave-3.md`
- `18-mcp-python-sdk-wave-3.md`
- `19-scenario-schema-v0-wave-3.md`
- `20-trace-schema-v0-wave-3.md`
- `21-discriminating-spikes-protocol-wave-3.md`
- `22-swagger-ingestion-audit-pipeline-wave-3.md`
- `23-evidence-synthesis-wave-3.md`
- `schemas/scenario-v0.schema.json`
- `schemas/trace-v0.schema.json`

### Updated TAPI

- `24-updated-tapi-impact-2026-08-13.md` — exact scope delta and consequences.

### Registry / decisions

- `sources.md`
- `../docs/adr/000-template.md`

## Immediate execution sequence after API delivery

**Acquire/hash contract → audit OpenAPI → resolve semantic questions → API-MAP-v0 → ScenarioSchema v1 → canonical client/ToolSpec → evaluator/reset/fault harness → TraceSchema v1 → runtime/client/MCP spikes → statistical pilot/model screening → ADRs → FROZEN-v1.**
