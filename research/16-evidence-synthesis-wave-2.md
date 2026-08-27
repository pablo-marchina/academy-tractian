# Evidence Synthesis — Wave 2

Status: **COMPLETE FOR PRE-API RESEARCH SCOPE; API-dependent questions remain open**

This wave deepens the architecture-changing topics that can be researched before the TRACTIAN Swagger/onboarding: state/context, observability, security, model-selection methodology, retrieval gating and statistical/compute budgeting.

## 1. Executive findings

### F2.1 — State is not memory, and context is not state

The project should explicitly separate:

- industrial environment state;
- execution/workflow state;
- conversation/session state;
- optional persistent memory;
- evidence cache;
- model-visible context;
- immutable trace/evaluation records.

The environment/API remains authoritative for mutable industrial facts. Model-visible context is a temporary projection, never a source of truth.

**Decision impact:** persistent cross-session memory should be off by default and enabled only when an actual scenario requirement proves it necessary.

### F2.2 — Benchmark isolation is an architectural requirement

Every scenario must start in an explicit namespace/state boundary. Cross-scenario memory/cache reuse can invalidate reliability results and create stale-state/security failures.

**Decision impact:** runtime finalists must support controllable/resettable state, not merely a convenient “memory” abstraction.

### F2.3 — Context should be curated rather than accumulated

Long-context capacity does not remove the context-engineering problem. Current first-party guidance and memory research support selecting high-signal current state/evidence, progressive retrieval and bounded compaction/structured notes rather than injecting all historical traces into every model call.

**Decision impact:** the agent should construct context explicitly from typed state/evidence. Raw traces remain outside prompts unless retrieved for a specific purpose.

### F2.4 — OTel-first tracing should be framework-neutral

OpenTelemetry provides the interoperability layer needed to compare runtimes and downstream observability backends. Current GenAI semantic conventions are still evolving, so the project must pin versions and retain a project-owned telemetry namespace for experiment-critical fields.

**Decision impact:** runtime selection requires equivalent OTel-compatible trace coverage. Observability backend is downstream and remains open.

### F2.5 — Phoenix and Langfuse are both viable backend candidates; neither is canonical

Both have current open-source/self-host/OTel-oriented workflows. Phoenix has strong experiment/evaluation concepts; Langfuse also supports OTel and experiment/dataset workflows. Rapid product evolution means exact versions must be pinned.

**Decision impact:** implement one normalized trace contract first, then export the same test traces to both candidates before ADR selection.

### F2.6 — Agent security must protect capabilities, not merely instructions

AgentSecBench/AgentDojo and current OWASP/first-party security guidance support treating tool outputs and retrieved text as potentially untrusted input, while authorization/capability enforcement lives outside the LLM.

**Decision impact:** `model proposes → deterministic validation/policy → execute` remains a strong architecture constraint. Prompt-only safety is a baseline to beat, not the production boundary.

### F2.7 — Mutation safety deserves a separate layer

Read-only and state-mutating operations have asymmetric consequences. The threat model now requires mutation metadata, preconditions, permission/policy checks, controlled retries/idempotency and postcondition verification where observable.

**Decision impact:** safety metrics distinguish dangerous model proposals from actual system-level execution. A blocked unsafe proposal is an agent failure but containment success.

### F2.8 — MCP, if selected, introduces concrete authorization/security obligations

The MCP 2026-07-28 security guidance forbids token passthrough and emphasizes token/audience validation, least-privilege scopes and SSRF protections.

**Decision impact:** MCP cannot be added as a cosmetic adapter without its own security/test boundary. Native-only vs adapter vs MCP-first remains an ADR experiment.

### F2.9 — Public function-calling leaderboards are filters, not selectors

BFCL can identify candidates with relevant function-calling capability, but it does not reproduce TRACTIAN tools, policies, state changes, faults or abstention/escalation semantics.

**Decision impact:** model selection must use our canonical project benchmark and repeated-run protocol.

### F2.10 — Adaptive model routing is conditional

Routing adds another policy/model layer. It is justified only if project validation data reveals complementary model strengths that create a measurable Pareto improvement.

**Decision impact:** strongest single-model configuration is the baseline. Static or learned routing is tested only later.

### F2.11 — RAG is conditional on an actual unstructured retrieval problem

The project should first inspect the real knowledge resources. If retrieval is needed, test structured/direct access, BM25, dense, hybrid, and only then reranking. Component retrieval metrics must be paired with end-to-end task metrics.

**Decision impact:** no vector database, embedding model or reranker is selected in advance.

### F2.12 — Exact sample size/repetition count must come from an API-derived pilot

Repeated runs are nested within scenarios; they do not create independent task diversity. Statistical analysis should preserve scenario clustering and use paired comparisons across configurations.

**Decision impact:** Wave 2 freezes the *procedure* for selecting `N` and `k`, not arbitrary numbers.

## 2. Source evidence reviewed in Wave 2

### State, memory and context

- LangGraph Persistence — https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph Memory — https://docs.langchain.com/oss/python/langgraph/add-memory
- Anthropic, *Effective context engineering for AI agents* — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- LongMemEval — https://arxiv.org/abs/2410.10813
- MemGPT — https://arxiv.org/abs/2310.08560
- LoCoMo — https://arxiv.org/abs/2402.17753

### Observability

- OpenTelemetry Semantic Conventions — https://opentelemetry.io/docs/specs/semconv/
- OpenTelemetry GenAI semantic conventions — https://github.com/open-telemetry/semantic-conventions-genai
- Phoenix documentation — https://arize.com/docs/phoenix/
- Langfuse documentation — https://langfuse.com/docs

### Security

- AgentSecBench — https://arxiv.org/abs/2605.26269
- AgentDojo — https://arxiv.org/abs/2406.13352
- OWASP Excessive Agency — https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- MCP Security Best Practices — https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- Anthropic, *How we contain Claude* — official Anthropic engineering/research material reviewed as a containment-design source

### Model/tool calling

- Berkeley Function-Calling Leaderboard / Gorilla — https://gorilla.cs.berkeley.edu/leaderboard.html
- Groq Models — https://console.groq.com/docs/models
- Groq Tool Use — https://console.groq.com/docs/tool-use
- Groq Rate Limits — https://console.groq.com/docs/rate-limits
- Gemini Function Calling — https://ai.google.dev/gemini-api/docs/function-calling
- Gemini API pricing/model availability — https://ai.google.dev/gemini-api/docs/pricing

### Retrieval

- BEIR — https://arxiv.org/abs/2104.08663
- RAGChecker — https://arxiv.org/abs/2408.08067
- Blended RAG — https://arxiv.org/abs/2404.07220

### Statistics

- SciPy `bootstrap` — https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- statsmodels proportion intervals — https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html
- statsmodels McNemar — https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html
- statsmodels multiple testing — https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html

## 3. New architecture constraints after Wave 2

These are not full technology selections, but any candidate architecture must now satisfy them unless later evidence overturns them:

1. **Canonical environment truth stays outside the LLM.**
2. **Per-scenario state isolation/reset is mandatory for valid evaluation.**
3. **Persistent memory is opt-in, not default.**
4. **Model context is explicitly curated from typed state/evidence.**
5. **OTel-compatible traces exist from baseline zero.**
6. **Project-owned run IDs/config hashes/state/evidence semantics remain backend-neutral.**
7. **Authorization/hard policy/schema checks do not depend on prompt compliance.**
8. **Mutation proposals and actual executions are distinct trace/evaluation events.**
9. **Tool/retrieval outputs do not inherit instruction authority.**
10. **Model selection is project-native and repeated-run.**
11. **Routing/RAG/long-term memory remain conditional.**
12. **Exact statistical budget comes from a pilot, with scenario as primary generalization unit.**

## 4. What remains impossible to close before onboarding

The following are deliberately blocked by the actual API/partner:

- complete domain/entity relation model;
- exact read vs mutation endpoint taxonomy;
- permission/tenancy model;
- high-impact actions;
- reset/snapshot/replay semantics;
- idempotency;
- stochastic API behavior/seed controls;
- freshness/version metadata;
- knowledge corpus structure;
- whether long-term memory is required;
- retrieval/RAG need;
- exact tool similarity/count/dependency depth;
- final scenario-family distribution;
- exact `N`/`k` and provider budget.

These are not research omissions; they are explicit external dependencies.

## 5. Next discriminating experiments after API delivery

Order matters:

1. import/version Swagger and map every endpoint/action/permission/risk;
2. create typed canonical API/tool boundary;
3. create resettable scenario harness and deterministic evaluators;
4. implement baseline-zero trace contract;
5. run identical runtime spike (LangGraph vs Pydantic AI/Graph vs OpenAI Agents SDK finalists);
6. compare native tools vs MCP adapter/topology;
7. run pilot for scenario variability + model/tool candidate screening;
8. freeze `N/k` and benchmark split;
9. evaluate mutation gate and evidence-stopping policy;
10. only then test optional memory/RAG/routing/optimization where failure analysis justifies them.

## 6. Research Gate status after Wave 2

### Strongly advanced / mostly resolved methodologically

- state/context taxonomy;
- benchmark isolation principles;
- trace/observability contract principles;
- layered threat model;
- model benchmark method;
- retrieval decision gate;
- statistical/sample-budget selection method.

### Still requires discriminating experiment

- runtime framework;
- observability backend;
- MCP topology;
- exact API client generation strategy;
- evidence-stopping implementation;
- mutation verification design;
- model/configuration winner.

### Still blocked on API/partner

- domain model;
- permissions/high-impact semantics;
- reset/snapshot/replay;
- knowledge corpus/RAG requirement;
- exact gold-scenario design;
- final N/k/compute allocation.

Wave 2 therefore reduces the space of valid architectures substantially without prematurely selecting tools whose value must be demonstrated on the real API.
