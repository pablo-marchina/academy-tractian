# Evidence Synthesis — Wave 1

Date: 2026-08-10
Status: **PROVISIONAL — inputs to ADRs, not frozen architecture**

## 1. Problem reframing

The project is not best modeled as “build a chatbot that can call an industrial API”. The API intentionally contains uncertain/failing observations and impactful actions. The engineering problem is therefore closer to a sequential decision system under uncertainty:

`request → collect evidence → decide whether evidence is sufficient → choose/validate action → observe → stop/ask/investigate/act/escalate`

This framing creates separate correctness surfaces: intent, evidence acquisition, tool choice, arguments, trajectory, authorization/policy, state mutation, response and stopping behavior.

## 2. State-based evaluation is the preferred ground truth for side effects

τ-bench evaluates tool-using agents by comparing the database state at the end of the interaction against an annotated goal state and separately introduces `pass^k` to study reliability across repeated trials.

Implication for TRACTIAN: when a scenario changes platform state, **the final environment state should be the canonical task-success signal whenever the API permits inspection/reset**. Natural-language claims of success are not enough.

This does not eliminate trajectory evaluation: an agent can reach a correct final state through an unsafe or forbidden path. Final-state and trajectory/policy evaluators therefore need to coexist.

Source: τ-bench — https://arxiv.org/abs/2406.12045

## 3. Reliability must be evaluated across repeated executions

A stochastic agent can solve a scenario once and still be operationally unreliable. τ-bench’s `pass^k` formalizes consistency across repeated trials; Phoenix and Pydantic Evals also support repeated/multi-run experiment patterns.

Implications:

- report repeated-run results per scenario, not only aggregate single-run accuracy;
- retain run-level traces so variance can be attributed;
- compare configurations on the same scenario families;
- distinguish capability (`can succeed`) from reliability (`succeeds consistently`).

Sources:
- https://arxiv.org/abs/2406.12045
- https://arize.com/docs/phoenix/datasets-and-experiments/how-to-experiments
- https://pydantic.dev/docs/ai/evals/evals/

## 4. Abstention is a first-class capability, not a fallback message

AgentAbstain directly studies whether tool-using agents know when **not** to act. It reports that abstention ability is not simply equivalent to general task-solving ability and identifies “post-hoc abstention” as a dangerous failure mode: an agent recognizes it should abstain only after performing an irreversible action.

Implication: the TRACTIAN policy should explicitly model the action space:

- `ASK` — request missing information;
- `INVESTIGATE` — collect more evidence;
- `ACT` — perform an authorized action;
- `ABSTAIN` — refuse to execute when execution is not justified;
- `ESCALATE` — transfer to human/specialist review.

These outcomes need paired scenarios where small controlled changes flip the correct policy from act to abstain/ask/escalate.

Source: AgentAbstain — https://arxiv.org/abs/2607.10059

## 5. Mutating actions deserve asymmetric safeguards

SABER analyzes tool-agent traces by separating mutating actions from non-mutating actions and reports that deviations in state-changing actions are disproportionately associated with task failure. The paper proposes mutation-gated verification, targeted reflection before mutating steps and context cleaning.

Implication: we should **not** apply the same execution policy to read-only queries and impactful state changes. A candidate experimental architecture is:

`model proposes action → deterministic schema/permission/policy checks → mutation-specific verification → execute`

The verification step itself remains a hypothesis to benchmark; deterministic schema/permission enforcement is a stronger invariant candidate.

Source: SABER — https://arxiv.org/abs/2512.07850

## 6. Prompt instructions cannot be the only security boundary

AgentSecBench frames a key agent-security problem as mixing trusted instructions, untrusted retrieved/tool content and capabilities in the same generative channel. Its results motivate enforcement through capability restriction/projection and output validation rather than only descriptive prompt text.

Implication: the project should treat the LLM as a **proposal generator**, not the final authority for permissions or prohibited high-impact actions. Authorization and hard policy should live in deterministic application code whenever the API contract allows it.

Source: AgentSecBench — https://arxiv.org/abs/2605.26269

## 7. Tool output is an adversarial input surface

AgentDojo and modern agent red-team tooling treat indirect prompt injection through tool/retrieval outputs as a realistic failure mode. For an industrial agent, tool results should therefore be treated as data with provenance, not automatically as trusted instructions.

Implications for the threat model:

- tool-output prompt injection;
- malicious/misleading descriptions or metadata;
- privilege escalation / unauthorized resource access;
- unsafe action proposal despite a safe final answer;
- cross-session/context poisoning;
- data leakage.

Sources:
- AgentDojo — https://arxiv.org/abs/2406.13352
- Promptfoo agent red team — https://www.promptfoo.dev/docs/red-team/agents/

## 8. Evaluation must be multidimensional

Google ADK explicitly separates trajectory/tool-use evaluation from final-response evaluation. Pydantic Evals supports custom and span-based evaluators using OpenTelemetry traces, allowing internal behavior to be evaluated separately from output. This matches the TAPI’s nine evaluation objects.

Canonical project dimensions should include at least:

1. task/final-state success;
2. tool selection;
3. argument correctness and schema validity;
4. trajectory constraints/efficiency;
5. evidence provenance and use;
6. response correctness/grounding;
7. safety/policy compliance;
8. robustness under API faults;
9. repeated-run stability;
10. high-impact action correctness and authorization.

Sources:
- https://adk.dev/evaluate/
- https://pydantic.dev/docs/ai/evals/evals/

## 9. LLM-as-a-judge should be a fallback, not universal ground truth

The strongest available project signals are executable: schema checks, permission checks, expected tool/action constraints, state diffs, structured reference fields and replay. These should be used before semantic judges.

Provisional hierarchy:

1. executable/final-state evaluator;
2. deterministic policy/schema evaluator;
3. deterministic/reference evaluator;
4. trace/trajectory evaluator;
5. semantic/LLM evaluator for irreducibly qualitative dimensions;
6. sampled human review for evaluator validation and ambiguous cases.

A semantic judge may be useful for explanation quality or a claim requiring interpretation, but must not override a deterministic unsafe-action failure.

## 10. Observability is part of the experimental method

OpenTelemetry provides shared semantic conventions for telemetry, and GenAI conventions have moved into a dedicated repository that includes model, agent and MCP-related conventions. Phoenix is built around OTel/OpenInference and supports traces, evaluations, datasets and controlled experiments.

Implication: instrumentation should be present in the **first baseline**, with project-specific attributes for scenario/run/config/policy/evidence/action state. This allows later evaluator logic to inspect what actually happened rather than reconstructing behavior from console logs.

Sources:
- https://opentelemetry.io/docs/specs/semconv/
- https://github.com/open-telemetry/semantic-conventions-genai
- https://arize.com/docs/phoenix/

## 11. MCP is an interoperability option, not automatically the core architecture

The current MCP specification (2026-07-28) defines stateless, self-contained requests, per-request capability negotiation, resources/prompts/tools and explicit trust/safety principles. It also says implementations must build robust consent/authorization because MCP itself cannot enforce those principles at the protocol level.

Implication: if MCP is used, use the **current 2026-07-28-compatible ecosystem**, and keep authorization/policy outside protocol trust assumptions. A strong candidate design is a canonical typed Python tool layer with an MCP adapter, but this remains subject to an ADR and a small implementation/overhead comparison.

Source: https://modelcontextprotocol.io/specification/2026-07-28

## 12. Framework selection remains open

Wave 1 finds three especially relevant orchestration candidates:

### LangGraph

Strengths for this problem: explicit low-level stateful orchestration, durable execution/checkpointing, persistence and human-in-the-loop interrupts. This maps naturally to inspectable decisions and conditional safety/escalation gates.

Source: https://langchain-ai.github.io/langgraph/

### Pydantic AI / Pydantic Graph

Strengths: model-agnostic provider support, strong typed validation, tools/MCP, human tool approval, OpenTelemetry-compatible observability, durable execution integrations, graph support and a first-party code-first evaluation framework. This creates potential architectural coherence with fewer libraries.

Source: https://pydantic.dev/docs/ai/overview/

### OpenAI Agents SDK

Strengths: relatively small primitive set, Pydantic-based function tools, sessions, tracing, guardrails, MCP and HITL approval. Main research question: whether provider/runtime coupling and abstraction/control trade-offs are suitable for a model-comparative, free/low-cost academic benchmark.

Source: https://openai.github.io/openai-agents-python/

AutoGen and Google ADK remain comparison/reference candidates. AutoGen’s own docs recommend starting with a single agent and moving to teams only when needed; its GraphFlow remains experimental. This reinforces our rule that multi-agent complexity needs empirical justification.

Sources:
- https://microsoft.github.io/autogen/
- https://adk.dev/

## 13. Evaluation framework selection also remains open

A likely architecture is **custom domain ground truth + reusable evaluation runner + observability UI**, rather than delegating truth to one generic LLM-eval package.

Candidates:

- **Pydantic Evals**: code-first datasets/cases/experiments, custom evaluators, span-based evaluation and multi-run support.
- **Phoenix**: OTel/OpenInference tracing, datasets, evaluations and repeated experiments; useful as observability/analysis plane.
- **Promptfoo**: strong complementary adversarial/red-team and trajectory-aware security testing.
- **Google ADK evaluation**: useful reference implementation for tool/trajectory evaluation and conformance testing even if ADK is not selected as runtime.

No tool above should replace project-specific final-state, API-policy and safety evaluators.

## 14. RAG is not yet justified

The TAPI allows RAG/hybrid search/reranking only when they contribute to the experiment. Until the actual API and knowledge corpus are known, there is no evidence that a vector database improves the task.

Decision rule:

- if required knowledge is already structured and accessible through API tools, prefer that source of truth;
- if a substantial unstructured corpus exists, compare no-RAG vs candidate retrieval strategies on evidence/task metrics;
- only retain retrieval complexity if it improves outcomes or is required by the use case.

Status: `TRACTIAN_DEPENDENCY` + later experiment.

## 15. Multi-agent is not yet justified

A multi-agent design can add specialization but also more messages, state surfaces, coordination failures, cost and attribution difficulty. AutoGen’s own guidance recommends a single agent for simpler tasks and teams only when a single optimized agent proves inadequate.

Research plan: establish a strong single structured baseline first. Only test planner-executor/specialists if a defined failure cluster suggests decomposition could solve it.

## 16. Optimization must come after evaluation validity

DSPy/GEPA and Optuna are promising candidates for prompt/policy/routing optimization, but optimization before a stable metric can overfit the wrong objective. Therefore:

1. define gold scenarios and evaluator validity;
2. freeze development/validation/test separation;
3. establish baseline;
4. optimize only on development/validation;
5. evaluate once on locked test;
6. preserve hard safety constraints separately from quality/efficiency objectives.

## Wave 1 conclusion

The strongest architecture-independent findings are:

- executable state is the preferred truth for state-changing scenarios;
- repeated trials are mandatory for reliability claims;
- act/abstain/ask/escalate must be measured explicitly;
- mutating actions need asymmetric safeguards;
- hard policy/permission/schema enforcement should be deterministic;
- tool outputs must be treated as potentially untrusted data;
- evaluation must cover the whole trajectory, not only the final answer;
- tracing is a first-class experimental primitive;
- MCP, RAG, multi-agent, routing and optimization remain conditional choices;
- framework and model selection must be settled by project-specific comparison rather than generic rankings.

Next: convert these conclusions into candidate matrices, explicit hypotheses, API questions and minimal discriminating spikes.
