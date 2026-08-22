# Candidate Stack Matrix — Pre-ADR Shortlist

Status: **NO WINNER SELECTED**

The purpose of this file is to define credible candidates and the experiment/criteria that can discriminate among them. Scores are intentionally not invented before the project API and minimal spikes exist.

## 1. Agent runtime / orchestration

### Decision criteria

| Criterion | Why it matters |
|---|---|
| Explicit state/control flow | We must inspect and evaluate decisions, retries, stopping and escalation |
| Typed tools / validation | Argument correctness and high-impact safety are rubric-critical |
| Durable execution | HITL, failures and resumability may matter |
| Model/provider portability | Model selection must be empirical |
| Tool/MCP integration | TAPI explicitly permits native tools/MCP |
| Trace/OpenTelemetry compatibility | Evaluation requires trajectory evidence |
| Testability | Need deterministic component tests and injected faults |
| Complexity/overhead | One-month individual project |
| Stable API | Avoid spending project time fighting experimental framework churn |
| Framework lock-in | Domain evaluator should outlive runtime choice |

### Shortlist

| Candidate | Evidence-backed strengths | Open concerns / experiment |
|---|---|---|
| **LangGraph** | Low-level explicit graph; stateful/long-running runtime; persistence/checkpoints; interrupts/HITL; supports deterministic + agentic flow | More orchestration code; evaluate type/tool ergonomics, model portability, OTel instrumentation and implementation overhead |
| **Pydantic AI + Pydantic Graph** | Type safety; broad provider support; tools/MCP; approvals; OTel; durable execution integrations; graph; first-party Evals | Rapidly evolving large surface; determine whether graph/runtime semantics are as controllable/evaluable as needed and whether one-stack convenience causes coupling |
| **OpenAI Agents SDK** | Small primitive set; function tools with Pydantic; sessions; tracing; guardrails; MCP; HITL approvals | Evaluate provider neutrality, ability to own policy/state semantics, reproducible multi-provider benchmarking and cost/access constraints |
| **Google ADK** | Strong official eval/conformance tooling; agent/tool ecosystem; trajectory evaluation concepts | Evaluate portability, complexity and whether runtime adds value vs using its evaluation ideas only |
| **AutoGen** | Mature single/multi-agent patterns, event-driven Core, tools, state and teams | Multi-agent emphasis may be unnecessary; GraphFlow currently documented as experimental; benchmark only if decomposition becomes justified |

### Proposed discriminating spike

Implement the **same tiny contract** in top 2–3 finalists after Swagger arrives:

Scenario requirements:

1. one read-only tool;
2. one state-mutating tool;
3. typed arguments;
4. deterministic permission check;
5. injected partial result;
6. one retry/recovery branch;
7. one approval/escalation interrupt;
8. persisted state/resume;
9. OpenTelemetry trace;
10. switch between at least two model providers or a provider + test model.

Measure:

- implementation LOC excluding comments/tests;
- test LOC;
- trace completeness;
- number of framework-specific workarounds;
- ability to intercept tool call **before side effect**;
- ability to restore/resume state;
- ability to substitute fake tools/models;
- runtime latency overhead excluding model/API;
- clarity of exported state/trajectory;
- dependency footprint and setup friction.

Framework choice becomes an ADR after this spike; no popularity score.

## 2. Tool integration layer

### Candidate architectures

**A. Native typed Python registry only**

`OpenAPI → typed client → Pydantic schemas → native agent tools`

**B. Canonical typed registry + MCP adapter**

`OpenAPI → typed client → canonical tool registry → native adapter + MCP adapter`

**C. MCP-first**

`OpenAPI → MCP server → agent runtime`

### Current hypothesis

B is the leading candidate because it can preserve a single source of truth while letting MCP be evaluated/demonstrated without forcing all runtime logic through the protocol. This is **not accepted** until we measure duplication, schema fidelity, trace propagation and overhead.

MCP implementation must target the current 2026-07-28 specification/ecosystem rather than legacy session assumptions.

## 3. Schema and validation

Leading candidate: **Pydantic v2 / JSON Schema generated from typed models**, independent of runtime.

Reason:

- explicit validation before side effects;
- easy deterministic evaluator reuse;
- compatible with multiple candidate runtimes;
- tool schema and domain object schema can share types.

Open question: how faithfully the final OpenAPI schemas map into generated/manual Pydantic models, especially unions/enums/nullable/error responses.

## 4. HTTP integration

Leading candidate: **HTTPX** with an API client boundary and test transport/mocking/fault injection.

Selection criteria:

- async support;
- explicit timeout/retry policy;
- testability;
- observability instrumentation;
- no tool logic mixed into transport code.

The final client generation strategy (manual typed wrapper vs generated OpenAPI client) depends on Swagger size/quality.

## 5. Evaluation runner

### Architecture invariant

The **domain ground-truth evaluator must be project-owned**. Generic eval frameworks may execute, organize, visualize or supplement it, but do not define correctness.

### Candidates

| Candidate | Best use in this project | Risk |
|---|---|---|
| **Pydantic Evals** | Code-first datasets/cases/experiments; custom + span-based evaluators; multi-run patterns | Potential overlap with our custom scenario runner; verify hooks/setup/reset behavior |
| **pytest + custom runner** | Deterministic invariant checks, unit/integration tests, simplest canonical logic | Need to build experiment/report ergonomics ourselves |
| **Google ADK eval** | Reference for trajectory/tool conformance; potential runner if ADK runtime chosen | Runtime ecosystem coupling |
| **DeepEval** | Secondary ready-made semantic/agent metrics | Avoid allowing LLM-judge metrics to become canonical ground truth |
| **Inspect AI** | External research-grade evaluation/sandbox runner | Potentially too broad/heavy for domain-specific API project |

### Leading research direction

`project-owned scenario/evaluator models + pytest deterministic checks + experiment runner (Pydantic Evals candidate)`.

No final selection yet.

## 6. Observability

### Hard requirement

OpenTelemetry-compatible instrumentation from baseline 0.

### Candidate backends

| Candidate | Strengths | Questions |
|---|---|---|
| **Phoenix** | Open source; OTel/OpenInference; traces + evals + datasets + experiments; self-hostable | Measure local setup/resource use and fit with custom evaluator artifacts |
| **Langfuse** | Open-source observability/evals/prompt/dataset ecosystem | Compare local setup, OTel support, experiment UX and storage footprint |
| **Pydantic Logfire** | Deep Pydantic/Pydantic AI integration; OTel | Potential vendor/ecosystem coupling if Pydantic runtime not selected |
| **LangSmith** | Tight LangGraph/LangChain tooling | Free/usage constraints and runtime ecosystem coupling |

Provisional preference: an **OTel-first application schema** with Phoenix as the first backend spike, so replacing the UI does not change the project’s telemetry contract.

## 7. Adversarial / security evaluation

Leading complementary candidate: **Promptfoo**, because current tooling can use OTel trajectories and distinguish safe text from unsafe intermediate tool execution.

Canonical security truth remains deterministic project policy + state/tool traces.

Use cases to validate:

- permission escalation;
- forbidden tool/action;
- prompt injection through tool result;
- unsafe arguments;
- side effect before guardrail;
- cross-context contamination;
- context poisoning;
- excessive agency.

## 8. Experiment storage

Candidates:

- immutable JSONL/Parquet artifacts in `artifacts/` (gitignored for large outputs, summarized/versioned metadata committed);
- SQLite for simplest local run registry;
- PostgreSQL if durable agent/runtime or concurrent experiment needs justify it;
- Phoenix backend for trace/experiment UI, not sole source of truth.

Decision rule: do not introduce PostgreSQL simply because the architecture is “production-like”. Select storage based on actual durability/concurrency/query needs.

## 9. Retrieval/RAG

No technology shortlist is accepted until we see the supplied knowledge resources.

If unstructured retrieval is needed, compare at minimum:

1. structured API/knowledge endpoint only;
2. lexical/sparse retrieval;
3. dense retrieval;
4. hybrid retrieval;
5. reranking only if candidate retrieval has recall but poor ordering.

Measure evidence recall, task success, unsupported claims, latency and resource use. Vector database selection comes **after** retrieval strategy demonstrates value.

## 10. Model selection

No fixed production LLM yet.

Protocol:

1. shortlist models/providers that support required tool calling and fit access/compute constraints;
2. run identical locked validation scenarios with identical tools/policies;
3. compare task success, reliability, tool/argument correctness, safety, latency and resource/cost proxy;
4. inspect Pareto frontier;
5. only then test static/adaptive model routing.

Generic function-calling leaderboards (e.g. BFCL) may prioritize candidates but cannot choose the final model.

## 11. Optimization

Candidates after benchmark validity:

- **DSPy / GEPA** for prompt/instruction optimization;
- **Optuna** for discrete/continuous runtime parameters, thresholds and multi-objective search.

Hard rule: optimization cannot see the locked final test set, and safety constraints are not traded away through arbitrary weighted objectives.

## 12. UI/demo

Candidates later: Streamlit or Gradio for fastest evidence-oriented demo; a custom frontend is unjustified unless the demonstration requires interactions these tools cannot express.

The UI must expose experiment evidence, not just chat:

- run/trace timeline;
- API/tool calls and arguments;
- evidence/provenance;
- state before/after;
- policy decisions;
- repeat-run reliability;
- fault profile;
- configuration comparison;
- failure taxonomy.

## Current non-decisions

The following remain deliberately **unselected**:

- LangGraph vs Pydantic AI vs OpenAI Agents SDK;
- MCP-first vs adapter;
- single agent vs planner/executor vs multi-agent;
- Phoenix vs alternative telemetry UI;
- Pydantic Evals vs custom experiment runner as primary runner;
- any RAG/vector database;
- any production LLM;
- any adaptive routing/learned risk model;
- any prompt optimizer.

This is intentional: uncertainty is being made explicit instead of hidden inside premature stack choices.
