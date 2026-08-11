# Reviewed Source Registry

This registry contains primary research, specifications and official documentation reviewed during the systematic research phase. Presence here means “reviewed/relevant”, **not automatically selected for implementation**.

## Benchmarking, tool use and reliability

- **ReAct: Synergizing Reasoning and Acting in Language Models** — https://arxiv.org/abs/2210.03629
- **Toolformer: Language Models Can Teach Themselves to Use Tools** — https://arxiv.org/abs/2302.04761
- **τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains** — https://arxiv.org/abs/2406.12045
- **Berkeley Function-Calling Leaderboard (BFCL)** — https://gorilla.cs.berkeley.edu/leaderboard.html
- **AgentAbstain: Do LLM Agents Know When Not to Act?** — https://arxiv.org/abs/2607.10059
- **SABER: Small Actions, Big Errors — Safeguarding Mutating Steps in LLM Agents** — https://arxiv.org/abs/2512.07850

## Agent security

- **AgentSecBench: Measuring Prompt Injection, Privacy Leakage, and Tool-Use Integrity in LLM Agents** — https://arxiv.org/abs/2605.26269
- **AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents** — https://arxiv.org/abs/2406.13352

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
- **Promptfoo Agent Red Teaming** — https://www.promptfoo.dev/docs/red-team/agents/

## Protocols and telemetry

- **Model Context Protocol specification — 2026-07-28** — https://modelcontextprotocol.io/specification/2026-07-28
- **OpenTelemetry Semantic Conventions** — https://opentelemetry.io/docs/specs/semconv/
- **OpenTelemetry GenAI Semantic Conventions repository** — https://github.com/open-telemetry/semantic-conventions-genai

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
- validate important framework claims with a minimal repository spike before architecture freeze.
