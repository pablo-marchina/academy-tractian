# Tool Use and Planning Research — Wave 1

Status: **PROVISIONAL — techniques are candidates for project experiments**

## 1. Why ReAct is a baseline, not the final architecture by default

ReAct established the useful pattern of interleaving reasoning and environment actions so observations can update subsequent decisions. This maps naturally to industrial investigation where the agent must query evidence before deciding what to do.

For this project, ReAct is an excellent **baseline concept** because it is simple and directly relevant to sequential tool use. But newer reliability evidence shows that long-horizon agents still fail through argument mistakes, constraint loss, unsafe mutations, premature action and failure to abstain. Therefore “use ReAct” is not a complete architecture decision.

Source: https://arxiv.org/abs/2210.03629

## 2. Tool use has multiple independent subproblems

Toolformer’s original framing already separates:

- whether a tool should be called;
- which tool;
- when;
- which arguments;
- how tool results affect subsequent prediction.

Modern BFCL extends function-calling evaluation across single-turn, multi-turn, missing functions/parameters, long context, irrelevance/hallucination, memory and agentic settings.

Implication: we should never report one generic “tool accuracy” metric. The TRACTIAN benchmark must keep tool decision, argument construction, relevance/abstention and multi-step behavior separable.

Sources:
- Toolformer — https://arxiv.org/abs/2302.04761
- BFCL V4 — https://gorilla.cs.berkeley.edu/leaderboard

## 3. Planning itself should be diagnosable

The 2026 Agent Planning Benchmark (APB) isolates planning from execution and explicitly tests planning under extraneous tools, broken tools and unsolvable tasks. This is directly relevant to our API because some observations/tools can be unavailable, insufficient or irrelevant.

Project implication: when an end-to-end scenario fails, we should attempt to distinguish:

1. **planning failure** — wrong goal decomposition/constraints/tool intent before execution;
2. **execution failure** — plan is reasonable but tool/API/argument/result handling fails;
3. **policy failure** — action should not have been attempted;
4. **observation/evidence failure** — correct tool path but evidence is insufficient/conflicting and agent mishandles it.

A lightweight plan-quality diagnostic can be included in selected trace analyses without requiring every agent to emit verbose private reasoning.

Source: Agent Planning Benchmark — https://arxiv.org/abs/2606.04874

## 4. More scaffolding is not automatically more reliable

A 2026 cross-benchmark synthesis reports recurring failure clusters across tool invocation, planning/constraints, long-horizon context accumulation, multi-agent coordination, safety and measurement validity, and notes that additional scaffolding does not consistently improve reliability.

This reinforces the project rule:

> Every extra planner, critic, sub-agent, reflection loop or memory layer needs a measurable hypothesis and ablation.

Source: https://arxiv.org/abs/2607.05775

## 5. Reliability should be tested as a surface, not one clean benchmark point

ReliabilityBench proposes evaluating agent reliability across repeated execution, semantic task perturbations and controlled tool/API faults. Its framing is especially compatible with the TAPI’s probabilistic API behavior.

Candidate project design:

`R(configuration, repetition, request perturbation, API fault profile)`

We do not need to copy the benchmark’s exact implementation. The useful methodological idea is to measure reliability under multiple controlled stress dimensions rather than only a clean validation set.

Source: https://arxiv.org/abs/2601.06112

## 6. Clarification is an active agent behavior

The TAPI explicitly allows requesting additional information. Recent work such as SpeakRL treats proactive clarification as a capability that can improve completion under ambiguous task-oriented dialogue.

For our project, the main lesson is not to adopt SpeakRL training. It is to ensure the benchmark includes cases where **asking the right question is the correct action**, and to penalize both unnecessary questions and premature action.

Source: https://arxiv.org/abs/2512.13159

## 7. Programmatic tool calling is a new candidate worth testing carefully

A very recent 2026 paper, *The Bitter Lesson of Tool Calling*, compares programmatic tool calling (tools exposed as typed Python stubs invoked through generated code) against native JSON function calling on BFCL v4 and reports competitive or improved performance across many tested models, especially for composition/parallelism.

This is potentially relevant if the TRACTIAN task requires complex multi-tool data manipulation, but it introduces an important safety trade-off: arbitrary/generated code is a **much broader capability surface** than constrained JSON tool invocation.

Research decision:

- add programmatic tool calling as a **conditional experimental candidate**, not the default;
- only evaluate it in a sandbox with a capability-limited tool namespace;
- never allow generated code to bypass deterministic permission/policy/mutation gates;
- compare against native structured function calling on the project benchmark;
- reject it if gains are absent or if complexity/security cost dominates.

Source: https://arxiv.org/abs/2608.06370

## 8. Tool catalog size/relevance needs explicit testing if the API is large

BFCL includes relevance/irrelevance and missing-function/missing-parameter cases, and APB tests extraneous tools. These findings suggest that exposing every API operation at every turn may not be optimal when a tool catalog is large or semantically overlapping.

Conditional strategies after Swagger inspection:

1. expose all tools;
2. deterministic routing by task/resource class;
3. semantic/dynamic tool search;
4. hierarchical tool namespace;
5. planner selects a restricted tool subset.

We should not build tool retrieval if the actual endpoint catalog is small. If it is large, compare selection accuracy, missed-tool rate, latency/context tokens and final task success.

## 9. Parallel tool calls need side-effect awareness

Parallel calls can improve latency for independent read-only evidence collection, but mutating/stateful calls can create ordering and concurrency hazards. AutoGen’s official documentation, for example, explicitly warns about parallel execution with stateful agent/team tools.

Candidate invariant:

- read-only independent queries may be parallelized if the API permits it;
- mutating/high-impact calls are serialized unless the contract proves concurrency safety;
- agent runtime must not autonomously parallelize dependent mutations.

This is a system-level execution policy, not a prompt preference.

Reference: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html

## 10. Candidate architecture ladder for experiments

Rather than jumping directly to the most complex system, evaluate an increasing ladder:

### B0 — Native tool loop

Model + structured tools + minimal instructions.

Purpose: measure raw model/tool capability.

### B1 — ReAct-style investigation

Explicit observation/action loop and clear stopping behavior.

Purpose: establish standard agentic baseline.

### A1 — Structured state/policy orchestration

Explicit state fields and decision transitions.

Purpose: isolate benefit of deterministic workflow structure.

### A2 — + deterministic tool/schema/permission gate

Purpose: measure hard-safety/control benefit.

### A3 — + mutation-specific verification

Purpose: test SABER-inspired asymmetric safeguards.

### A4 — + explicit ask/abstain/escalate policy

Purpose: test controlled non-action behavior.

### A5 — + adaptive evidence/recovery policy

Purpose: test partial/conflicting/unavailable API handling.

### Conditional A6 — tool subset/search, programmatic calls, multi-agent decomposition, model routing

Only activated if earlier failure analysis creates a concrete hypothesis.

## 11. Planning/evidence stopping candidate policy

The agent should not “reason forever”. Candidate stop conditions must be explicit and measurable.

Potential signals:

- user goal already satisfied;
- required evidence set complete;
- no unresolved critical conflict;
- no missing mandatory action parameters;
- additional read has diminishing/zero expected value;
- retry budget reached;
- action forbidden/unauthorized;
- uncertainty remains above allowed action threshold → ASK/ESCALATE/ABSTAIN.

The exact evidence sufficiency rules depend on the API fields and are a P0 onboarding dependency.

## 12. What is *not* selected yet

- ReAct as final runtime;
- planner-executor split;
- reflection/critic loop on every step;
- multi-agent team;
- dynamic tool search;
- parallel tool use;
- programmatic tool calling;
- learned planner/risk model.

Each becomes an experiment only if the actual API/task distribution makes it relevant.

## Sources

- ReAct — https://arxiv.org/abs/2210.03629
- Toolformer — https://arxiv.org/abs/2302.04761
- BFCL V4 — https://gorilla.cs.berkeley.edu/leaderboard
- Agent Planning Benchmark — https://arxiv.org/abs/2606.04874
- Beyond the Leaderboard synthesis — https://arxiv.org/abs/2607.05775
- ReliabilityBench — https://arxiv.org/abs/2601.06112
- SpeakRL — https://arxiv.org/abs/2512.13159
- The Bitter Lesson of Tool Calling — https://arxiv.org/abs/2608.06370
