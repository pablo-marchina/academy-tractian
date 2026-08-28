# Decision Revalidation Addendum 002 — Historical Evidence Audit Reconciliation

**Status:** ACTIVE / prospective override for the master-plan inventory  
**Date:** 2026-08-28  
**Applies to:** `DECISION-REVALIDATION-MASTER-PLAN.md` sections describing the immediate decision inventory and automatic experiment ordering  
**Evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)

## 1. Reason for this addendum

The master plan was intentionally written before the repository-wide historical evidence audit. Its initial inventory therefore contained conservative placeholders such as `RESEARCH_REQUIRED`, `SCREEN_REQUIRED` and prospective experiment ordering.

The completed audit found substantially more reusable evidence, including a prior complete E0→E14v retrospective reclassification and strong later ADR/production evidence. This addendum prevents the pre-audit placeholders from being interpreted as authorization to repeat work.

## 2. Prospective override

From this checkpoint forward, the master plan must be read in this order:

```text
EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md
→ MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md
→ this addendum
→ DECISION-REVALIDATION-MASTER-PLAN.md for general comparison mechanics
```

Where the master plan's initial decision inventory conflicts with the completed audit classification, **the completed audit controls the current decision state**.

## 3. Key corrections to the pre-audit inventory

- provider/model is not blank-slate research; it is `PARTIALLY_ASSESSED` with extensive historical evidence and requires current-fact reconciliation first;
- provider capacity is `EVIDENCE_EXISTS_NEEDS_UPDATE`, not a reason to repeat consumed quota failures;
- agent topology is `PARTIALLY_ASSESSED`: single-agent evidence is strong, multi-agent incremental benefit is missing;
- runtime/orchestration is `PARTIALLY_ASSESSED`, with strong LangGraph and explicit-controller evidence but asymmetric comparator depth;
- native ToolSpec vs MCP is `EVIDENCE_SUFFICIENT` for the current inclusion decision;
- evidence-sufficiency stopping is `EVIDENCE_SUFFICIENT` for the current policy decision;
- RAG/vector/reranking, persistent memory, hosted deployment and richer UI are `EVIDENCE_SUFFICIENT` for **not adding them in the current scope absent a measured trigger**;
- adaptive routing remains `UNASSESSED` but is not currently material enough to experiment on;
- safety, provider-free reliability, deterministic operational evaluation and RunTrace observability are `EVIDENCE_SUFFICIENT` in their bounded current scopes;
- C4 remains `PARTIALLY_ASSESSED` with exact-byte recovery as the only currently authorized continuation;
- the historical ADR-008 live packet is `INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE` for execution under the permanent USD-0 constraint.

## 4. Experiment ordering is conditional, not automatic

The master plan's former sequence of provider → topology → runtime → adaptation is now interpreted as a **dependency order only for gaps that survive evidence audit and materiality screening**.

It does not mean every stage must generate a new experiment.

Current rule:

```text
existing evidence sufficient?
  YES → reuse, no experiment
  NO  → is the remaining gap material now?
          NO  → defer, no experiment
          YES → are prerequisites/control variables ready?
                  NO  → resolve prerequisite first
                  YES → preregister minimum experiment
```

## 5. Current immediate work

The only unblocked decision-revalidation work after this audit is:

1. current first-party fact refresh for the potentially eligible USD-0 provider/model set;
2. reconciliation of those facts with the existing E8/E14/P12/ADR evidence;
3. a decision on whether a minimal prospective provider comparison is still needed;
4. exact C4 artifact recovery in parallel.

No multi-agent, runtime, RAG, memory, routing, deployment or UI implementation is authorized by this addendum.

## 6. Historical evidence remains immutable

This addendum changes current interpretation/work ordering only. It does not rewrite any frozen ADR, consumed experiment, result, scientific gate or acceptance artifact.
