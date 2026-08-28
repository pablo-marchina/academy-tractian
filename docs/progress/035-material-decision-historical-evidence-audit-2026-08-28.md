# Progress 035 — Material-decision historical evidence audit

**Date:** 2026-08-28  
**Change class:** documentation/evidence consolidation only  
**New experiments:** 0  
**Provider/model calls:** 0  
**Credential/account probes:** 0  
**Real customer mutations:** 0

## Completed

Executed the repository-wide evidence-first audit required before any new experiment.

Rather than re-auditing E0→E14v from scratch, reused `research/results/p12-historical-candidate-component-reinterpretation-2026-08-22.json` as the historical baseline and reconciled the post-2026-08-22 delta: P12/C4, ADR-001→017, production controller/action/evaluator work, EV-007/008/011, final delivery reproduction, final 83-row acceptance audit and the new USD-0/evidence-first governance.

## Result

Twenty material decision rows were consolidated:

```text
EVIDENCE_SUFFICIENT                         11
EVIDENCE_EXISTS_NEEDS_UPDATE                1
PARTIALLY_ASSESSED                          6
UNASSESSED                                  1
INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE      1
total                                      20
new experiments authorized                  0
```

Key corrections:

- provider/model work is a delta/reconciliation problem, not blank-slate research;
- historical Groq negative task-quality and quota failures remain decision evidence;
- single-agent is a strong qualified baseline, while multi-agent incremental benefit remains unmeasured;
- LangGraph and the explicit controller both have material repository evidence, so runtime is partially assessed rather than unresearched;
- native tools vs MCP and evidence-sufficiency stopping already have direct comparisons sufficient for their current decisions;
- RAG, persistent memory, hosted deployment and richer UI have no demonstrated current delivery gap and therefore do not receive experiments by default;
- adaptive routing is genuinely unassessed but not currently material until multiple viable providers exist;
- C4 remains exact-artifact recovery first;
- ADR-008→011 remain historical protocol engineering, but the old OpenAI/Gemini packet is invalid for current execution under the USD-0 constraint.

## Canonical artifacts

- `docs/MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`;
- `research/results/material-decision-historical-evidence-audit-2026-08-28.json`;
- `docs/DECISION-REVALIDATION-ADDENDUM-002-HISTORICAL-EVIDENCE-AUDIT.md`;
- reconciled `docs/CURRENT-PROJECT-STATUS.md`;
- reconciled `docs/NEXT-STEPS.md`.

## Next

After this audit merges, refresh current first-party USD-0 provider/model eligibility/capability facts only, then reconcile them against the existing E8/E14/P12/ADR evidence. Do not make provider inference calls during the fact refresh.

Continue exact C4 artifact recovery in parallel.
