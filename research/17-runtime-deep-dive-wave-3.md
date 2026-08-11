# Wave 3 — Runtime Deep Dive

Status: **PRE-ONBOARDING / NO WINNER SELECTED**

## Decision to be made

Choose the agent runtime/orchestration layer only after all finalists implement the same canonical TRACTIAN tool contract and are evaluated with the same scenarios, model, policy gate and trace contract.

Finalists retained for the discriminating spike:

1. **LangGraph**
2. **Pydantic AI + Pydantic Graph where explicit graph control is needed**
3. **OpenAI Agents SDK**

Google ADK and AutoGen remain reference candidates, not primary finalists, unless the API or partner requirements reveal a capability the three finalists cannot satisfy cleanly.

## Project requirements that discriminate runtimes

A viable runtime must support, without hidden semantic differences:

- typed tool invocation over a project-owned canonical tool layer;
- interception **before** a mutating/high-impact side effect;
- explicit `ASK / INVESTIGATE / ACT / ABSTAIN / ESCALATE` decisions;
- bounded loops/stopping;
- pause/resume for approval or external information;
- recoverable failures without duplicate mutations;
- deterministic fake-model/fake-tool tests;
- framework-neutral trace export;
- model/provider substitution for project benchmarking;
- isolation between benchmark runs;
- inspectable state sufficient for replay/debugging.

## LangGraph

### Evidence from current official docs

LangGraph has a built-in checkpointing model. With a checkpointer, graph state is saved at execution steps/threads; persistence enables HITL, time-travel/replay, conversational state and fault recovery.

`interrupt()` can pause execution dynamically and persist state until resumed. Critically, the documentation states that a node restarts from its beginning when resumed, so side effects before an interrupt must be idempotent. This is directly relevant to our mutation boundary.

The testing documentation supports fresh checkpointers per test and individual node/edge testing. LangChain's test utilities also expose fake chat models for scripted responses/tool calls.

### Strength hypotheses

- strongest explicit workflow/state-machine control of the finalists;
- natural location for deterministic mutation gates as separate nodes;
- integrated checkpoint history makes failure/resume experiments easy to inspect;
- strong support for explicit branches/loops rather than an opaque agent loop.

### Risks to measure

- graph complexity / implementation overhead for simple tasks;
- coupling to LangChain/LangGraph message/state abstractions;
- checkpoint semantics around nodes that combine decision + side effect;
- normalized OTel export quality without making LangSmith the canonical experiment store;
- provider portability when using non-LangChain-native model integrations.

### Required implementation discipline if selected

A mutating tool must never be executed before a resumable/approval boundary inside the same node. Proposal, authorization and execution should be separated so node replay cannot accidentally repeat an irreversible action.

## Pydantic AI

### Evidence from current official docs

Pydantic AI provides `TestModel` and `FunctionModel` specifically for deterministic testing, plus `Agent.override` and an option to prevent accidental real model calls.

Deferred tools represent approvals and externally executed tools. They can be resolved inline or emitted as `DeferredToolRequests`, then resumed with the original history plus `DeferredToolResults`. Current docs distinguish a follow-up `run_id` while retaining conversation correlation.

Durable execution is supported through integrations with Temporal, DBOS, Prefect and Restate. This means durability is available, but its architecture differs from LangGraph's integrated checkpoint model and must be compared fairly rather than described as equivalent.

Pydantic AI is explicitly model-agnostic and currently documents direct support for many providers, including OpenAI, Anthropic, Gemini, Groq, OpenRouter and others.

### Strength hypotheses

- exceptionally strong typing/schema boundary;
- strongest built-in deterministic model-test ergonomics among current finalists;
- broad native provider coverage is attractive for quantitative model benchmarking;
- deferred tools map cleanly to our proposal → policy → approval/external execution split.

### Risks to measure

- additional durable-execution dependency if we require true restart-safe execution;
- whether Pydantic Graph adds enough value over a structured Pydantic AI loop to justify another abstraction;
- exact semantics of resumed deferred operations vs our trace/run identity requirements;
- API evolution/version pinning because the project is moving quickly.

## OpenAI Agents SDK

### Evidence from current official docs

The current SDK includes tools, MCP integration, sessions, HITL and tracing. HITL tools can require approval; pending approvals surface as interruptions and `RunState` can be serialized and resumed later.

The model layer supports OpenAI directly and also exposes provider interfaces / OpenAI-compatible paths for non-OpenAI providers. Official docs explicitly warn that feature support can vary across provider paths and should be validated for the exact path used.

Tracing is built in, but the SDK exposes custom `TracingProcessor`/trace-provider interfaces. This means we can test whether a project-owned processor can emit our normalized trace contract rather than relying on OpenAI-hosted traces.

### Strength hypotheses

- compact agent-loop abstraction with mature approval/resume primitives;
- good MCP ergonomics if MCP becomes useful;
- serializable run state may satisfy our pause/resume requirement without a graph runtime;
- hook/processor surfaces appear sufficient for instrumentation.

### Risks to measure

- provider feature parity is less uniform than a generic `ModelProvider` interface might imply;
- default tracing is OpenAI-oriented, so OTel normalization must be demonstrated;
- less explicit workflow topology may make fine-grained trajectory control harder than LangGraph;
- need to prove deterministic fake-model testing is as ergonomic as Pydantic AI/LangGraph alternatives.

## Runtime comparison contract

The same canonical tool implementations MUST be wrapped by each runtime. Framework-specific tools may adapt schemas, but they may not change endpoint semantics, policy behavior or evidence returned.

### Hard gates

A finalist is rejected if it cannot demonstrate all of the following:

1. intercept a proposed mutation before execution;
2. resume a paused run without duplicate side effects in the reference spike;
3. run fully deterministic unit tests without network/model calls;
4. export the mandatory normalized trace fields;
5. use the same canonical ToolSpec/HTTP client as the other finalists;
6. enforce the same external deterministic policy gate;
7. keep benchmark scenarios isolated.

### Comparative outcomes

After hard gates:

- task/policy correctness on spike scenarios;
- normalized trace completeness;
- pause/resume correctness;
- restart/failure recovery behavior;
- provider portability on the candidate model set;
- framework-only latency overhead with fake model/API;
- implementation surface: production LOC, adapter LOC, test LOC, dependencies;
- debugging ergonomics recorded qualitatively but not collapsed into an arbitrary weighted score.

## Provisional conclusion

No runtime wins before the API arrives. However, all three finalists are now credible enough that selecting one from documentation alone would be unjustified.

**New architecture constraint:** the canonical tool/policy/evaluation boundary must remain project-owned so the runtime can be swapped during the spike without changing the experiment.

## Primary/official sources

- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- LangGraph testing: https://docs.langchain.com/oss/python/langgraph/test
- Pydantic AI testing: https://pydantic.dev/docs/ai/guides/testing/
- Pydantic AI deferred tools: https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/
- Pydantic AI durable execution: https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/
- Pydantic AI models: https://pydantic.dev/docs/ai/models/overview/
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- OpenAI Agents SDK HITL: https://openai.github.io/openai-agents-python/human_in_the_loop/
- OpenAI Agents SDK models: https://openai.github.io/openai-agents-python/models/
- OpenAI Agents SDK tracing interface: https://openai.github.io/openai-agents-python/ref/tracing/
