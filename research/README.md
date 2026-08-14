# Systematic Research Hub

Status: **ACTIVE — Research Gate not passed**

This directory is the evidence base for architecture and experiment decisions. Production implementation is not frozen while a high-impact research question remains unresolved.

## TAPI + kickoff update — 2026-08-13

The updated TAPI requires both **Construção de agente** and **Framework de avaliação de agentes**. The kickoff then clarified the intended workflow and evaluation philosophy. Because the automatic transcript is noisy, kickoff claims are stored with confidence labels in `25-kickoff-evidence-2026-08-13.md`; Swagger/canonical-case artifacts remain more authoritative for exact semantics.

High-confidence kickoff guidance now incorporated:

- target workflow is customer-support investigation/resolution automation with safe human fallback;
- partner cases are expected to include customer-question-derived input, engineer reference trajectory/accesses and target final output/conclusion;
- evaluate intermediate tool/process behavior as well as final response;
- semantic conclusion/decision matters more than exact wording;
- customer-facing answers should avoid unnecessary internal implementation detail;
- insufficient/meaningfully ambiguous evidence can correctly require human escalation;
- escalation should carry evidence, attempted analysis and the unresolved reason;
- state-changing actions should have an explicit requester-confirmation boundary;
- one stable agent-facing integration contract is desirable;
- agent failure must not break the pre-existing workflow;
- development/final-evaluation leakage must be prevented.

## Research status

| ID | Area | Status |
|---|---|---|
| R01 | Requirements | Dual-track + kickoff workflow/eval guidance captured; artifact-specific constraints remain |
| R02 | Industrial domain | API-dependent |
| R03 | API/tool engineering | Canonical-interface direction strengthened; Swagger/client spike pending |
| R04 | Agent runtime | LangGraph, Pydantic AI/Graph and OpenAI Agents SDK remain finalists; spike pending |
| R05 | Planning/reasoning | Baseline and experiment method defined |
| R06 | Tool use | Reference engineer trajectories expected; actual tool taxonomy pending |
| R07 | Evidence | Conservative escalation under unresolved ambiguity partner-backed; actual metadata pending |
| R08 | Abstention/escalation | ASK / INVESTIGATE / ACT / ABSTAIN / ESCALATE established; handoff-quality evaluator now required |
| R09 | Policy/action safety | Deterministic boundary + mutation confirmation direction established; action mapping pending |
| R10 | State/memory | State planes separated; real persistence needs pending |
| R11 | Models/routing | Project-native Pareto benchmark defined; student provider constraints/execution pending |
| R12 | Retrieval/RAG | Conditional decision ladder defined; corpus pending |
| R13 | Evaluation | ScenarioSchema v0 ready; canonical cases will drive v1 |
| R14 | Reliability | Repeated-run/statistical methodology defined; partner explicitly reinforces regression testing |
| R15 | Adversarial testing | Pre-API threat/failure families defined; safe fallback strengthened |
| R16 | Observability | TraceSchema v0 + OTel-first method defined; path-level evaluation partner-backed |
| R17 | Optimization | Deferred until objective/benchmark freeze; kickoff favors prove-value-before-optimization |
| R18 | Statistics | Method advanced; exact N/k pending case inventory/pilot |
| R19 | Reproducibility | Replay/versioning + grouped split method defined; reset semantics pending |
| R20 | Demo/UI | Must prove agent + eval, including success, escalation, blocked/unconfirmed mutation and fallback |

## Current architecture invariants/hypotheses

These are research conclusions, not a frozen final stack:

1. Both agent construction and evaluation are mandatory and integrated.
2. State-changing tasks should use executable/final-state ground truth whenever available.
3. Reliability requires repeated trials; scenario is the primary generalization unit.
4. Tool choice, arguments, trajectory, evidence, policy, final state, semantic conclusion and communication policy are separate correctness surfaces.
5. ASK / INVESTIGATE / ACT / ABSTAIN / ESCALATE are first-class evaluated outcomes.
6. Model proposals do not replace deterministic schema/permission/policy/confirmation checks.
7. High-impact/state-changing actions receive stronger pre-execution and postcondition checks.
8. Human escalation is a valid correct outcome under insufficient/ambiguous evidence; handoff completeness is measurable.
9. Environment state is authoritative; model context is only a curated projection.
10. Persistent cross-session memory is off by default until the real task proves need.
11. ScenarioSchema, TraceSchema, evaluators and canonical tools should be more stable than model/runtime choices.
12. OpenTelemetry is an interoperability layer; project-owned experiment semantics remain canonical.
13. LangGraph, Pydantic AI/Graph and OpenAI Agents SDK still require the same discriminating spike before selection.
14. MCP remains conditional; canonical tools + optional adapter is the leading pre-API hypothesis and now aligns with partner guidance for one stable agent-facing interface.
15. OpenAPI audit is separate from code generation.
16. Exact gold wording is not the primary target; conclusion/decision facts should be scored separately from customer-safe communication.
17. The system should fail safely back into the existing support process when model/tool execution fails.
18. RAG, adaptive routing, multi-agent and automatic optimization remain conditional on measured value.
19. Exact sample/repetition budget will be selected from canonical-case inventory plus an API-derived pilot.
20. Reference engineer trajectories are valuable supervision/diagnostics, but an equivalent valid read-only path should not be rejected solely for sequence mismatch unless policy requires it.

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

### 2026-08-13 evidence updates
- `24-updated-tapi-impact-2026-08-13.md` — written TAPI scope delta.
- `25-kickoff-evidence-2026-08-13.md` — confidence-aware kickoff extraction and consequences.

### Registry / decisions
- `sources.md`
- `../docs/adr/000-template.md`

## Immediate execution sequence after artifact delivery

**Acquire/hash Swagger + canonical cases → audit/inventory both → resolve remaining P0 semantics → API-MAP-v0 + GOLD-MAP-v0 → ScenarioSchema v1 → canonical client/ToolSpec → evaluator/reset/fault harness → TraceSchema v1 → runtime/client/MCP spikes → statistical pilot/model screening → ADRs → FROZEN-v1.**
