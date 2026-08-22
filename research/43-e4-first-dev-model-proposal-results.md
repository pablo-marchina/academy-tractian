# E4 — First DEV Model-Proposal Boundary Run

**Date:** 2026-08-16  
**Status:** EXECUTED / DEV-ONLY / BOUNDARY-METRICS-ONLY  
**Split:** DEV  
**Proposal source class:** `model_agent`

This report records the first DEV model-proposal plan executed through the E4 B0-B3 boundary adapter. It is not a final task-success result and does not use evaluator-only gold.

## Inputs

- Proposal plan: `research/experiments/e4-dev-model-proposal-plan-gpt-5-5-thinking-2026-08-16.json`
- Adapter: `scripts/research/e4_model_proposal_adapter.py`
- Split manifest: `research/frozen/benchmark-split-v1.json`
- CI run: `31945464765`
- Uploaded artifact: `e4-dev-model-proposal-boundary`
- Artifact id: `9263151483`
- Summary JSON: `research/results/e4-dev-model-proposal-boundary-summary-2026-08-16.json`

## Safeguards preserved

- `LOCKED_TEST` was not accessed.
- The adapter accepted only `DEV` groups.
- Identity and seed remained runner-bound.
- The proposal source was explicitly labeled `model_agent`.
- The adapter did not call an LLM provider itself.
- The adapter did not load private/evaluator-only gold.
- The output is boundary evidence only, not full task/conclusion success.

## DEV coverage

The proposal plan contains 8 DEV runs:

- `CEN-01` / `asset_G501`
- `CEN-10` / `asset_G501`
- `CEN-02` / `asset_C710`
- `CEN-14` / `asset_C710`
- `CEN-03` / `asset_S420`
- `CEN-16` / `asset_S420`
- `CEN-04` / `asset_M208`
- `CEN-11` / `asset_M101`

## Aggregate boundary metrics

| Variant | Proposals | Executed calls | Blocked calls | Invalid arg executions | Permission/scope executions | Premature action executions | Required action executions | Contained unsafe proposals | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 27 | 27 | 0 | 0 | 1 | 0 | 5 | 0 | 1 |
| B1 | 27 | 27 | 0 | 0 | 1 | 0 | 5 | 0 | 1 |
| B2 | 27 | 26 | 1 | 0 | 0 | 0 | 4 | 1 | 0 |
| B3 | 27 | 26 | 1 | 0 | 0 | 0 | 4 | 1 | 0 |

## Initial interpretation

1. **B1 had no effect in this first plan** because the generated tool arguments were structurally valid.
2. **B2 contained one unsafe permission/resource-scope proposal** that B0/B1 would execute.
3. **B3 did not add new blocking beyond B2** in this first plan because action proposals were placed after the declared evidence requirements.
4. The required-action execution count drops from 5 to 4 under B2/B3 because one required action in the proposal plan targeted a resource outside the user's company scope. This is an agent-layer proposal failure that the system boundary contained.
5. This result is useful for the guarded-boundary hypothesis, but it does **not** yet prove task/conclusion correctness.

## Methodological status

This is the first non-scripted DEV boundary run, not architecture selection. It may be used to debug the E4 experiment and identify candidate boundary value, but it cannot freeze runtime, model, prompt, MCP topology, RAG, multi-agent decomposition or final UI.

The next step is to combine these DEV traces with the private DEV evaluator so task/conclusion success can be measured without committing evaluator-only gold to the public repository.
