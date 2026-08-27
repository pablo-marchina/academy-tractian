# E5 — Evidence Acquisition / Stopping Preregistration

**Date:** 2026-08-16  
**Status:** PREREGISTERED  
**Scope:** DEV + VALIDATION only  
**LOCKED_TEST:** forbidden

E5 moves from guarded-boundary safety to evidence-acquisition and stopping behavior. E4 promoted the B3 boundary bundle as the current guarded-boundary candidate; E5 does not freeze runtime, model, prompt, MCP, RAG, multi-agent design, memory, observability backend or UI.

## Hypothesis

An explicit evidence-sufficiency and stopping policy should reduce premature stopping and unnecessary tool calls versus a free tool loop, while preserving or improving task success and escalation/action correctness.

## Boundary policy

- Use **B3** as the current guarded-boundary candidate.
- Retain **B0** as an E4 safety baseline where useful.
- Keep B1 and B2 as required B3 sublayers, not as independent architecture decisions.
- Do not access LOCKED_TEST.

## Compared strategies

| Strategy | Role | Agent-quality evidence? |
|---|---|---|
| `fixed_reference_like` | Infrastructure/reference-like anchor | No |
| `free_tool_loop` | Model proposal sequence without explicit evidence stop policy | Yes |
| `evidence_sufficiency_policy` | Model proposal sequence constrained by evidence sufficiency and stop rules | Yes |

## Metrics

Primary:

- premature stopping count;
- unnecessary tool calls;
- required evidence coverage;
- task success;
- escalation/action correctness;
- tool-call efficiency.

Hard constraints:

- LOCKED_TEST access must be false;
- runtime/model/MCP/UI freeze must be false;
- scripted/reference-like strategy must not be counted as agent-quality evidence.

## Artifacts

- Manifest: `research/experiments/e5-evidence-stopping-experiment-manifest.json`
- Runner: `scripts/research/e5_evidence_stopping_runner.py`

## Exit criteria

E5 may promote an evidence/stopping policy only if it improves premature stopping and/or unnecessary calls relative to the free loop without worsening task success or safety. Promotion is still experimental and does not freeze runtime/model/provider/MCP/UI.
