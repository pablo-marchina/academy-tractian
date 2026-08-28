# Decision Revalidation Addendum 001 — Evidence First

**Status:** ACTIVE / prospective amendment to `DECISION-REVALIDATION-MASTER-PLAN.md`  
**Date:** 2026-08-28  
**Detailed gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)

## Amendment

The mandatory sequence in the Decision Revalidation Master Plan is amended prospectively so that **repository evidence audit precedes new research and preregistration**.

Where the earlier master-plan wording could be read as moving directly from a decision question into new systematic research or a new experiment, this addendum takes precedence.

The required sequence is now:

```text
requirement / decision question
→ audit all relevant existing repository evidence
→ classify evidence sufficiency
→ reuse evidence when sufficient
→ refresh only changed external facts/assumptions where needed
→ identify the exact material evidence gap, if one remains
→ systematic research only for that gap
→ credible alternatives for that gap
→ preregister the minimum controlled experiment only if necessary
→ implement
→ evaluate
→ reconcile with historical evidence
→ decision / regression / freeze
```

## Hard rule

> **No new experiment may be created until the repository has been checked for evidence sufficient to answer that decision.**

A new experiment requires an explicit `PARTIALLY_ASSESSED`, `UNASSESSED`, `EVIDENCE_EXISTS_NEEDS_UPDATE`, or otherwise documented current-scope evidence gap. `EVIDENCE_SUFFICIENT` forbids a redundant new experiment unless a separate regression/robustness obligation explicitly requires one.

## Why

The repository already contains substantial historical evidence across provider/model, tooling, runtime, evaluation, safety and other areas. Repeating valid work wastes the remaining delivery window and can weaken provenance by creating unnecessary duplicate evidence. The project should consolidate and reuse before generating more evidence.

This amendment changes no historical experiment, ADR, scientific result or frozen artifact.