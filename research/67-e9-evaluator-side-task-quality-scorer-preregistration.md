# E9 Evaluator-Side Task-Quality Scorer Preregistration

**Status:** E9_PREREGISTERED  
**Date:** 2026-08-16  
**Prerequisite:** E8 Groq free model pass  
**LOCKED_TEST:** blocked until final evaluation

## Purpose

E8 proved that a real zero-cost remote model candidate can produce schema-valid, trace-complete outputs on DEV and VALIDATION. However, E8 task success is still a proxy because the model prompt does not include evaluator-only expected outputs or private oracles.

E9 adds an evaluator-side scorer that maps already-produced model outputs to private oracles after generation, without leaking gold into prompts.

## Core rule

The model never sees:

- expected answers;
- reference trajectories;
- private scoring labels;
- evaluator-only gold;
- `eval/expected-paths.json`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST cases.

The scorer may read private DEV/VALIDATION oracles only after model outputs are fixed and hashed.

## Inputs

Allowed model-side inputs:

- agent-visible case packet;
- tool contract / ToolSpec names and schemas;
- runtime observations gathered through allowed tools;
- B3/evidence policy instructions.

Allowed scorer-side inputs:

- frozen DEV + VALIDATION private oracles;
- fixed model outputs and output hashes;
- RunTrace events;
- action/escalation proposals;
- evidence-plan/tool-intent outputs.

Forbidden before final evaluation:

- LOCKED_TEST cases or labels;
- training against validation answers;
- prompt updates based directly on private gold;
- merging proxy success with real task-quality score.

## Metrics

E9 will report:

- real task-quality score;
- decision-class correctness;
- required evidence coverage;
- evidence-plan correctness;
- action/escalation correctness;
- unsafe or premature action rate;
- unsupported final-claim rate;
- trace completeness;
- schema validity;
- provider latency and cost;
- disagreement between proxy success and real scorer result.

## Constants preserved

- B3 guarded boundary.
- Evidence-sufficiency policy.
- Adaptive evidence planning.
- LangGraph current runtime candidate.
- HarnessRunner execution boundary.
- HttpxTransport live API path.
- Native ToolSpec internal default.
- MCP-compatible adapter as optional external interoperability surface.
- Groq as current leading free-provider candidate.
- OpenAI/Anthropic disabled.
- Final architecture not frozen.

## Execution order

1. Build scorer on DEV only.
2. Validate scorer behavior against known DEV cases.
3. Run on fixed Groq E8 DEV outputs.
4. If DEV scorer is coherent, run on fixed Groq E8 VALIDATION outputs.
5. Keep LOCKED_TEST blocked.
6. Produce an ADR deciding whether Groq remains leading candidate or more optional comparators are needed.

## Success criteria

E9 passes if:

- scorer can evaluate fixed model outputs without prompting the model with gold;
- scorer separates proxy metrics from real task-quality metrics;
- action/escalation and evidence correctness are explicitly measured;
- no LOCKED_TEST material is accessed;
- model/provider and final architecture remain unfrozen.
