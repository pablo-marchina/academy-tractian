# Updated TAPI Impact — 2026-08-13

## Executive conclusion

The updated TAPI materially changes the formal project scope.

Previous wording required developing a solution in **one of two tracks**. The updated objective now requires a solution **containing both**:

1. Construção de agente; and
2. Framework de avaliação de agentes.

This resolves the largest formal-scope ambiguity in the Research Gate and validates the repository's integrated agent + evaluation direction as a requirement rather than an optional extension.

## Confirmed delta

### Previous objective

The previous document framed the project as choosing one of two tracks.

### Updated objective

The updated document states that the project must develop a solution containing both agent construction and an agent-evaluation framework.

No other substantive change was identified in the supplied six-page text: the context of use, API behavior, deliverable examples, reference architecture, suggested technologies, rubric criteria and dates remain materially unchanged.

## Architecture consequences

### 1. Evaluation is no longer optional framing

The evaluation framework must be treated as a first-class production/research subsystem, not an auxiliary extension.

Canonical relationship:

```text
Industrial Agent
      ↓
Canonical Trace / State / Tool Events
      ↓
Evaluation Framework
      ↓
Metrics + Failure Attribution + Robustness + Reliability + Safety
      ↓
Architecture/Policy/Model Improvement
```

This makes eval-driven development the natural unifying architecture.

### 2. Shared contracts become more important

`ScenarioSchema`, `TraceSchema`, `Canonical ToolSpec`, state oracles and policy oracles now serve both mandatory components. This strengthens the Wave 3 decision that experiment contracts should be more stable than runtime/model choices.

### 3. The final demo must prove both systems

The demonstration should not merely show a successful agent interaction. It must also expose evaluation evidence for that run and aggregate experiment results.

Minimum demonstration target:

- user request;
- agent trajectory/tool execution;
- evidence and policy decisions;
- state before/after where relevant;
- evaluation result for the run;
- repeated-run reliability;
- robustness/fault case;
- high-impact safety case;
- comparison against at least one baseline/configuration.

### 4. Evaluation coverage maps directly to the TAPI objects

The framework should explicitly cover:

- function choice;
- argument accuracy;
- execution trajectory;
- evidence use;
- response quality;
- safety;
- performance under failures;
- stability across executions;
- high-impact action behavior.

### 5. Research hypothesis should compare integrated agent designs

The central experiment should compare agent configurations/architectures while using the same evaluation framework and scenario distribution.

The evaluation framework itself should also be validated: deterministic evaluators and executable oracles where possible, semantic/LLM-based assessment only when deterministic ground truth is unavailable.

## Requirement interpretation

The updated objective is mandatory. Within each deliverable section, wording such as `poderá explorar` and `exemplos` still indicates flexibility in the exact implementation form. Therefore:

- both major components are mandatory;
- every illustrative framework/tool is not automatically mandatory;
- every evaluation object explicitly listed should be mapped to evidence in the final framework because covering them directly maximizes alignment with the rubric;
- optional complexity such as RAG, multi-agent, MCP topology, adaptive routing and automatic prompt optimization remains evidence-gated.

## Research Gate changes

### Closed

- Whether one track must be selected.
- Whether evaluation can be treated only as an optional extension.

### Still open / API-dependent

- complete Swagger/OpenAPI contract;
- concrete entities and identifiers;
- authentication and authorization semantics;
- state reset/snapshot/replay capabilities;
- mutation/high-impact taxonomy;
- idempotency semantics;
- probabilistic return representation and controllability;
- knowledge corpus shape;
- rate limits/quotas;
- evaluation cases/hidden cases supplied by partner.

## Immediate action

1. Update requirement matrix with mandatory dual-track requirement.
2. Remove formal one-track ambiguity from project framing.
3. Preserve unified agent+evaluation architecture.
4. During onboarding, spend questions on API/experimental unknowns rather than track-selection ambiguity.
5. After Swagger delivery, continue the pre-registered sequence:
   - contract archive/audit;
   - domain/risk mapping;
   - canonical tools;
   - scenario/evaluator harness;
   - normalized traces;
   - runtime/MCP spikes;
   - statistical pilot/model screening;
   - architecture ADRs and `FROZEN-v1`.

## Impact on project strategy

This update is favorable to the existing research direction. The repository had already been intentionally designed to cover both tracks as one integrated system. The new TAPI removes the need to justify that breadth as an optional extension and makes quantitative evaluation a direct requirement of the project objective.
