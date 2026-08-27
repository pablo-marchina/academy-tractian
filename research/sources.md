# Reviewed Source Registry

This registry contains primary research, specifications and official documentation reviewed during the systematic research phase. Presence here means “reviewed/relevant”, **not automatically selected for implementation**.

## Benchmarking, tool use, planning and reliability

- **ReAct: Synergizing Reasoning and Acting in Language Models** — https://arxiv.org/abs/2210.03629
- **Toolformer: Language Models Can Teach Themselves to Use Tools** — https://arxiv.org/abs/2302.04761
- **τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains** — https://arxiv.org/abs/2406.12045
- **tau2/tau3 current repository/evaluation materials** — https://github.com/sierra-research/tau2-bench
- **Berkeley Function-Calling Leaderboard (BFCL)** — https://gorilla.cs.berkeley.edu/leaderboard.html
- **Agent Planning Benchmark (APB)** — https://arxiv.org/abs/2606.04874
- **ReliabilityBench: Evaluating LLM Agent Reliability Under Repetition, Perturbation, and Faults** — https://arxiv.org/abs/2601.06112
- **Beyond the Leaderboard: Failure Modes and Reliability of LLM Agents** — https://arxiv.org/abs/2607.05775
- **AgentAbstain: Do LLM Agents Know When Not to Act?** — https://arxiv.org/abs/2607.10059
- **SABER: Small Actions, Big Errors — Safeguarding Mutating Steps in LLM Agents** — https://arxiv.org/abs/2512.07850
- **SpeakRL: Proactive Clarification in Task-Oriented Agents** — https://arxiv.org/abs/2512.13159
- **The Bitter Lesson of Tool Calling** — https://arxiv.org/abs/2608.06370

## State, memory and context management

- **LangGraph Persistence** — https://docs.langchain.com/oss/python/langgraph/persistence
- **LangGraph Interrupts** — https://docs.langchain.com/oss/python/langgraph/interrupts
- **LangGraph Testing** — https://docs.langchain.com/oss/python/langgraph/test
- **LangGraph Memory** — https://docs.langchain.com/oss/python/langgraph/add-memory
- **Anthropic — Effective context engineering for AI agents** — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **LongMemEval** — https://arxiv.org/abs/2410.10813
- **MemGPT** — https://arxiv.org/abs/2310.08560
- **LoCoMo** — https://arxiv.org/abs/2402.17753
- **MOSAIC** — https://arxiv.org/abs/2607.16211 — recent preprint retained as provisional evidence only

## Agent security

- **AgentSecBench** — https://arxiv.org/abs/2605.26269
- **AgentDojo** — https://arxiv.org/abs/2406.13352
- **NetInjectBench** — https://arxiv.org/abs/2607.10490 — network-operations analogue; results must not be assumed to transfer
- **OWASP Excessive Agency** — https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- **MCP Security Best Practices** — https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices

## Agent runtimes / orchestration candidates

### LangGraph

- Overview/documentation — https://docs.langchain.com/oss/python/langgraph/overview
- Persistence — https://docs.langchain.com/oss/python/langgraph/persistence
- Interrupts — https://docs.langchain.com/oss/python/langgraph/interrupts
- Testing — https://docs.langchain.com/oss/python/langgraph/test

### Pydantic AI / Graph

- Overview — https://pydantic.dev/docs/ai/overview/
- Testing / `TestModel` / `FunctionModel` — https://pydantic.dev/docs/ai/guides/testing/
- Deferred tools / HITL — https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/
- Durable execution — https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/
- Model/provider support — https://pydantic.dev/docs/ai/models/overview/
- Graph documentation — https://pydantic.dev/docs/ai/graph/

### OpenAI Agents SDK

- Overview — https://openai.github.io/openai-agents-python/
- Human-in-the-loop / serializable RunState — https://openai.github.io/openai-agents-python/human_in_the_loop/
- Models/providers — https://openai.github.io/openai-agents-python/models/
- Tracing interfaces/processors — https://openai.github.io/openai-agents-python/ref/tracing/
- Sessions — https://openai.github.io/openai-agents-python/sessions/

### Other reference candidates

- Google ADK — https://adk.dev/
- Microsoft AutoGen — https://microsoft.github.io/autogen/

## Evaluation frameworks / infrastructure

- **Pydantic Evals** — https://pydantic.dev/docs/ai/evals/evals/
- **Google ADK Evaluation** — https://adk.dev/evaluate/
- **Arize Phoenix** — https://arize.com/docs/phoenix/
- **Langfuse documentation** — https://langfuse.com/docs
- **Promptfoo Agent Red Teaming** — https://www.promptfoo.dev/docs/red-team/agents/

## API contracts and code generation

- **OpenAPI specification versions / schemas** — https://spec.openapis.org/oas/
- **OpenAPI 3.2.0 normative specification** — https://spec.openapis.org/oas/v3.2.0.html
- **OpenAPI Generator project** — https://github.com/OpenAPITools/openapi-generator
- **OpenAPI Generator Python generator docs** — https://openapi-generator.tech/docs/generators/python/
- **openapi-python-client** — https://github.com/openapi-generators/openapi-python-client
- **Pydantic JSON Schema** — https://docs.pydantic.dev/latest/concepts/json_schema/

Important Wave 3 conclusion: validator/code-generator output is derived evidence. The raw partner contract plus the normative specification and live conformance tests remain authoritative.

## MCP and telemetry

- **Model Context Protocol specification — 2026-07-28** — https://modelcontextprotocol.io/specification/2026-07-28
- **MCP 2026-07-28 release** — https://blog.modelcontextprotocol.io/posts/2026-07-28/
- **MCP Python SDK** — https://github.com/modelcontextprotocol/python-sdk
- **MCP Python SDK v2 changes** — https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/whats-new.md
- **OpenTelemetry Semantic Conventions** — https://opentelemetry.io/docs/specs/semconv/
- **OpenTelemetry GenAI Semantic Conventions repository** — https://github.com/open-telemetry/semantic-conventions-genai
- **OpenTelemetry agent/framework spans** — https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md
- **OpenTelemetry semantic-conventions releases** — https://github.com/open-telemetry/semantic-conventions/releases

## Current model/tool-calling provider documentation

These sources are for capability/access filtering and must be re-checked immediately before benchmark execution because catalogs and quotas change.

- **Groq Models** — https://console.groq.com/docs/models
- **Groq Tool Use** — https://console.groq.com/docs/tool-use
- **Groq Rate Limits** — https://console.groq.com/docs/rate-limits
- **Gemini Function Calling** — https://ai.google.dev/gemini-api/docs/function-calling
- **Gemini API pricing/free tier** — https://ai.google.dev/gemini-api/docs/pricing

## Retrieval / RAG

- **BEIR** — https://arxiv.org/abs/2104.08663
- **RAGChecker** — https://arxiv.org/abs/2408.08067
- **Blended RAG** — https://arxiv.org/abs/2404.07220

## Statistics and experimental inference

- **SciPy bootstrap** — https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- **statsmodels proportion confidence intervals** — https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html
- **statsmodels McNemar test** — https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html
- **statsmodels Cochran's Q** — https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.cochrans_q.html
- **statsmodels multiple-testing corrections** — https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html

## Optimization candidates

- **DSPy** — https://dspy.ai/
- **GEPA** — https://arxiv.org/abs/2507.19457
- **Optuna** — https://optuna.readthedocs.io/

## Industrial/domain sources

- **TRACTIAN official product/solution material** — https://tractian.com/

The project API is synthetic/simplified. Public TRACTIAN material is context only and must not be used to invent endpoint behavior or entities absent from the supplied contract.

## Source policy

For any final ADR:

- prefer the project/API contract over generic framework guidance;
- prefer primary papers/specifications over secondary summaries;
- record version/date for fast-moving frameworks/protocols;
- never infer that a benchmark result transfers directly to the TRACTIAN task distribution;
- validate important framework claims with a minimal repository spike before architecture freeze;
- label very recent preprints as provisional evidence;
- use provider docs for capability/availability facts, then re-verify immediately before execution;
- distinguish framework capability from project fitness;
- distinguish reference trajectory from task/policy ground truth;
- preserve raw API contracts and experiment artifacts so derived tooling can be replaced without losing provenance.
