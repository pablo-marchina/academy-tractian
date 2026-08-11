# Reviewed Source Registry

This registry contains primary research, specifications and official documentation reviewed during the systematic research phase. Presence here means “reviewed/relevant”, **not automatically selected for implementation**.

## Benchmarking, tool use, planning and reliability

- **ReAct: Synergizing Reasoning and Acting in Language Models** — https://arxiv.org/abs/2210.03629
- **Toolformer: Language Models Can Teach Themselves to Use Tools** — https://arxiv.org/abs/2302.04761
- **τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains** — https://arxiv.org/abs/2406.12045
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
- **LangGraph Memory** — https://docs.langchain.com/oss/python/langgraph/add-memory
- **Anthropic — Effective context engineering for AI agents** — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory** — https://arxiv.org/abs/2410.10813
- **MemGPT: Towards LLMs as Operating Systems** — https://arxiv.org/abs/2310.08560
- **LoCoMo: Evaluating Very Long-Term Conversational Memory of LLM Agents** — https://arxiv.org/abs/2402.17753
- **MOSAIC** — https://arxiv.org/abs/2607.16211 — recent preprint retained as provisional evidence only

## Agent security

- **AgentSecBench: Measuring Prompt Injection, Privacy Leakage, and Tool-Use Integrity in LLM Agents** — https://arxiv.org/abs/2605.26269
- **AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents** — https://arxiv.org/abs/2406.13352
- **NetInjectBench** — https://arxiv.org/abs/2607.10490 — useful network-operations analogue; source-specific results must not be assumed to transfer
- **OWASP Excessive Agency** — https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- **MCP Security Best Practices** — https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- **Anthropic agent containment/security engineering material** — official Anthropic source reviewed for blast-radius/containment design; conclusions treated as engineering guidance rather than project-specific evidence

## Agent runtimes / orchestration candidates

- **LangGraph official documentation** — https://langchain-ai.github.io/langgraph/
- **Pydantic AI official documentation** — https://pydantic.dev/docs/ai/overview/
- **OpenAI Agents SDK official documentation** — https://openai.github.io/openai-agents-python/
- **Google Agent Development Kit (ADK) official documentation** — https://adk.dev/
- **Microsoft AutoGen official documentation** — https://microsoft.github.io/autogen/

## Evaluation frameworks / infrastructure

- **Pydantic Evals** — https://pydantic.dev/docs/ai/evals/evals/
- **Google ADK Evaluation** — https://adk.dev/evaluate/
- **Arize Phoenix** — https://arize.com/docs/phoenix/
- **Langfuse documentation** — https://langfuse.com/docs
- **Promptfoo Agent Red Teaming** — https://www.promptfoo.dev/docs/red-team/agents/

## API contracts, protocols and telemetry

- **OpenAPI Specification 3.1.x** — https://spec.openapis.org/oas/latest.html
- **OpenAPI Generator — Python** — https://openapi-generator.tech/docs/generators/python/
- **Pydantic JSON Schema** — https://docs.pydantic.dev/latest/concepts/json_schema/
- **Model Context Protocol specification — 2026-07-28** — https://modelcontextprotocol.io/specification/2026-07-28
- **MCP 2026-07-28 release notes/blog** — https://blog.modelcontextprotocol.io/posts/2026-07-28/
- **OpenTelemetry Semantic Conventions** — https://opentelemetry.io/docs/specs/semconv/
- **OpenTelemetry GenAI Semantic Conventions repository** — https://github.com/open-telemetry/semantic-conventions-genai

## Current model/tool-calling provider documentation

These sources are for capability/access verification and must be re-checked immediately before benchmark execution because model catalogs and quotas change.

- **Groq Models** — https://console.groq.com/docs/models
- **Groq Tool Use** — https://console.groq.com/docs/tool-use
- **Groq Rate Limits** — https://console.groq.com/docs/rate-limits
- **Gemini Function Calling** — https://ai.google.dev/gemini-api/docs/function-calling
- **Gemini API Pricing / free-tier availability** — https://ai.google.dev/gemini-api/docs/pricing

## Retrieval / RAG

- **BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models** — https://arxiv.org/abs/2104.08663
- **RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation** — https://arxiv.org/abs/2408.08067
- **Blended RAG** — https://arxiv.org/abs/2404.07220

## Statistics and experimental inference

- **SciPy bootstrap** — https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- **statsmodels proportion confidence intervals** — https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html
- **statsmodels McNemar test** — https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html
- **statsmodels Cochran's Q** — https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.cochrans_q.html
- **statsmodels multiple-testing corrections** — https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html

## Optimization candidates

- **DSPy** — https://dspy.ai/
- **GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning** — https://arxiv.org/abs/2507.19457
- **Optuna** — https://optuna.readthedocs.io/

## Industrial/domain sources

- **TRACTIAN official product/solution material** — https://tractian.com/

Important: the real project API is explicitly synthetic/simplified. Public TRACTIAN product material is used only to understand the industrial reasoning context; it must not be used to invent endpoint behavior or entities not present in the supplied API contract.

## Source policy

For any final ADR:

- prefer the project/API contract over generic framework guidance;
- prefer primary papers/specifications over secondary summaries;
- record version/date for fast-moving frameworks/protocols;
- never infer that a benchmark result transfers directly to the TRACTIAN task distribution;
- validate important framework claims with a minimal repository spike before architecture freeze;
- label very recent preprints as provisional evidence and avoid promoting them to architecture invariants without replication/project-specific tests;
- use provider docs for capability/availability facts, then re-verify immediately before execution;
- distinguish framework capability from project fitness: a feature existing in documentation is not evidence that the project needs it.
