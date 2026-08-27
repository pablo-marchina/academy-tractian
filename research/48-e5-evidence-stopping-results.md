# E5 — Evidence Acquisition / Stopping Results

**Date:** 2026-08-16  
**Status:** EXECUTED / DEV+VALIDATION / LOCKED_TEST-BLOCKED  
**Current boundary:** B3 guarded-boundary candidate  
**Runtime/model/MCP/UI freeze:** no

E5 compares evidence-acquisition and stopping behavior after E4 promoted B3 as the current guarded-boundary candidate. This is not an architecture freeze and does not select runtime, model/provider, MCP, RAG, multi-agent design, memory, observability backend or UI.

## Inputs

- Preregistration: `research/47-e5-evidence-stopping-preregistration.md`
- Manifest: `research/experiments/e5-evidence-stopping-experiment-manifest.json`
- Runner: `scripts/research/e5_evidence_stopping_runner.py`
- Summary: `research/results/e5-evidence-stopping-summary-2026-08-16.json`
- CI run: `31947620763`

## Safeguards preserved

- `LOCKED_TEST` was not accessed.
- Only DEV and VALIDATION groups were used.
- B3 remained the current guarded-boundary candidate.
- B0 remained a baseline context, not a preferred boundary.
- The fixed/reference-like strategy is explicitly infrastructure-only and not model-quality evidence.
- No runtime/model/prompt/MCP/RAG/UI decision was frozen.

## Compared strategies

| Strategy | Role | Agent-quality evidence? |
|---|---|---|
| `fixed_reference_like` | Infrastructure/reference-like anchor | No |
| `free_tool_loop` | Model proposal sequence without explicit stopping policy | Yes |
| `evidence_sufficiency_policy` | Model proposal sequence constrained by evidence sufficiency/stop rules | Yes |

## Aggregate results

| Strategy | Scenarios | Task success | Premature stops | Unnecessary calls | Total calls | Avg calls | Required evidence coverage | Action/escalation OK |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `fixed_reference_like` | 11 | 11 | 0 | 0 | 36 | 3.273 | 1.000 | 11/11 |
| `free_tool_loop` | 11 | 7 | 4 | 9 | 36 | 3.273 | 0.786 | 8/11 |
| `evidence_sufficiency_policy` | 11 | 10 | 1 | 2 | 35 | 3.182 | 0.964 | 11/11 |

## Delta vs free loop

| Metric | Evidence-sufficiency policy delta |
|---|---:|
| Task success | +3 |
| Premature stopping | -3 |
| Unnecessary calls | -7 |
| Total tool calls | -1 |

## Interpretation

1. The free tool loop still fails on evidence acquisition: it has four premature stops, nine unnecessary calls and lower required-evidence coverage.
2. The evidence-sufficiency policy improves task success while also reducing premature stopping and unnecessary calls.
3. The fixed/reference-like strategy remains useful as an upper-bound/infrastructure anchor but cannot be used as agent-quality evidence.
4. B3 remains the current guarded-boundary candidate; E5 promotes the evidence-sufficiency/stopping policy as the next candidate policy layer to carry forward.
5. This result does not freeze runtime, model/provider, prompt, MCP, RAG, multi-agent design, memory, observability backend or UI.

## Decision

| Component | Decision |
|---|---|
| B3 guarded boundary | Keep as current boundary candidate for the next experimental stage. |
| B0 | Keep as baseline context where useful. |
| Fixed/reference-like strategy | Retain as infrastructure/reference anchor only. |
| Free tool loop | Retain as behavioral baseline; not preferred. |
| Evidence-sufficiency policy | Promote as current evidence-acquisition/stopping candidate. |

## Next step

The next phase should produce an ADR-ready package for evidence/stopping and then move to runtime/MCP discriminating spikes only after preserving the no-LOCKED_TEST rule:

```text
E5 follow-up / ADR package
├── summarize E5 hypothesis, protocol, results, trade-offs
├── keep B3 + evidence-sufficiency as current candidate policy bundle
├── preserve B0/free-loop as baselines
├── document residual failures, especially CEN-09 style coverage limits
├── keep LOCKED_TEST blocked
└── only then start runtime/MCP spikes without freezing architecture
```
