# Academy × TRACTIAN — Evidence Audit Before New Experiments

**Status:** MANDATORY / repository-wide pre-experiment gate  
**Effective:** 2026-08-28  
**Applies to:** every material decision, experiment, benchmark, architecture comparison, provider/model comparison, prompt/configuration test, runtime/topology evaluation, retrieval/memory/adaptation test and any other work intended to generate new decision evidence.

## 1. Non-negotiable rule

> **No new experiment may be created until the repository has been audited for existing evidence sufficient to answer the same decision question.**

The repository is the first evidence source. Historical research, frozen results, failed experiments, ADRs, workflow artifacts, progress records, tests and implementation evidence must be reused before new experimental work is authorized.

The purpose is not to avoid experimentation. It is to avoid redundant experimentation, preserve the value of already-consumed evidence, protect the deadline and ensure that new experiments exist only to close a demonstrated evidence gap.

## 2. Mandatory order

For every material decision, use this sequence:

```text
decision question
→ repository-wide historical evidence audit
→ evidence map + provenance
→ sufficiency assessment
→ decision state
    ├─ EVIDENCE_SUFFICIENT
    │      → reuse existing evidence; no new experiment
    ├─ EVIDENCE_EXISTS_NEEDS_UPDATE
    │      → verify only facts/assumptions that changed
    ├─ PARTIALLY_ASSESSED
    │      → define the exact missing evidence only
    └─ UNASSESSED
           → systematic research + prospective experiment
→ only when a gap is demonstrated:
   preregister the minimum experiment that closes it
→ implement
→ evaluate
→ reconcile with all prior evidence
```

A new experiment is therefore a **last-mile evidence action**, not the default response to uncertainty.

## 3. What must be audited before declaring a gap

The audit must search, as applicable:

- `research/results/`;
- `research/frozen/`;
- `research/experiments/`;
- `scripts/research/` and associated tests;
- `docs/adr/`;
- `docs/progress/` and `PROJECT-PROGRESS-LOG.md`;
- current and historical project plans/status records;
- Git history, removed/superseded files and prior branches/PRs when relevant;
- GitHub Actions runs and preserved artifacts when repository files reference them;
- production tests and reliability/evaluation campaigns;
- existing implementation code when it provides contract/capability evidence.

The audit should prefer exact artifact identities, hashes, commit/blob identities, frozen protocols and reproducible outputs over narrative summaries.

## 4. Required evidence-audit record

Before authorizing a new experiment, document:

1. exact decision question;
2. repository searches performed;
3. relevant historical experiments/artifacts found;
4. what each artifact actually proves and does not prove;
5. whether its assumptions and environment remain valid;
6. whether the decision population/metrics/constraints match the current question;
7. existing failed/negative evidence;
8. current evidence classification;
9. exact evidence gap, if any;
10. why existing evidence cannot answer that gap;
11. smallest prospective experiment capable of closing the gap.

A statement such as “we should test X” is not sufficient authorization.

## 5. Evidence classifications

Use these classifications consistently:

### `EVIDENCE_SUFFICIENT`
Existing repository evidence is adequate for the current decision scope. Do not rerun merely for freshness, convenience or a cleaner result. Reuse it and advance the decision process.

### `EVIDENCE_EXISTS_NEEDS_UPDATE`
The repository contains adequate historical evidence structure, but a material external fact or hard assumption changed. Update only the changed portion; do not repeat unaffected work.

### `PARTIALLY_ASSESSED`
Historical evidence answers part of the decision but leaves a concrete material gap. New work must target that gap only.

### `UNASSESSED`
No adequate repository evidence exists for the material decision. A new systematic research/experiment cycle may be preregistered.

### `INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE`
The evidence remains historically valid but cannot support the current decision because a hard constraint, population, contract or decision question changed. Preserve it; do not delete or relabel the original result.

## 6. No rerun by default

Do not repeat an existing experiment simply because:

- the code is easy to rerun;
- a newer model/framework exists but is irrelevant to the current decision;
- the old result is inconvenient;
- the old result failed;
- the artifact is historical rather than recent;
- a cleaner benchmark would be easier to explain;
- the implementation has since changed in unrelated dimensions.

A rerun requires a documented reason that maps to a current evidence gap, changed assumption, regression obligation or required robustness confirmation.

## 7. New-candidate rule

Discovery of a credible new alternative does not automatically invalidate existing experiments. First determine whether existing evidence already covers the alternative's material behavior or whether a new controlled comparison is actually required.

If a new experiment is required, preserve the previous baseline and change the minimum number of dimensions necessary to isolate the new candidate's effect.

## 8. Failed evidence is evidence

Failed, incomplete and negative experiments remain part of the evidence base. Do not silently rerun, erase or exclude them merely because they do not support the preferred hypothesis.

Operational failure and scientific/task-quality failure must remain distinguishable.

## 9. Relationship to the Decision Revalidation Master Plan

This gate occurs **before** the preregistration step in `DECISION-REVALIDATION-MASTER-PLAN.md`.

The prospective sequence is therefore:

```text
requirement / decision question
→ historical repository evidence audit              ← THIS GATE
→ sufficiency/gap classification
→ hard constraints + current external-source refresh only where needed
→ credible alternative set
→ preregistered comparison only for demonstrated gaps
→ controlled implementation / experiment
→ quantitative evaluation
→ robustness / production fit
→ decision / regression / freeze
```

The master plan's decision inventory should be updated from audit findings rather than from assumptions about what has or has not been tested.

## 10. Current application

Before opening new experiments for provider/model, agent topology, orchestration/runtime, adaptive policies, retrieval, memory, observability, deployment or UI, first consolidate the repository's existing evidence for each area.

Examples already known at this checkpoint:

- Groq/provider work has historical E8 evidence and must not be treated as unresearched;
- native typed tools vs MCP has historical comparative evidence and should not be blindly repeated;
- agent topology requires verification of whether any controlled single-vs-multi comparison exists before a new topology experiment is authorized;
- LangGraph/runtime has historical implementation/research evidence that must be consolidated before deciding what additional comparison is actually missing;
- C4 is an artifact-recovery problem and existing scientific artifacts must be exhausted before any prospective recovery experiment/amendment.

## 11. Authorization test

A new experiment is authorized only if all are true:

- [ ] the decision maps to a formal requirement, rubric criterion, material risk or necessary material-choice comparison;
- [ ] the repository evidence audit is complete enough for the decision scope;
- [ ] existing evidence is classified;
- [ ] no existing artifact already answers the question adequately;
- [ ] the remaining evidence gap is explicit and material;
- [ ] the new experiment is the minimum controlled work needed to close that gap;
- [ ] hard constraints and evaluation boundaries are preserved;
- [ ] the experiment is prospectively preregistered before implementation.

If any item is false, **do not create the experiment**.

## 12. Permanent operating statement

```text
REUSE BEFORE RESEARCH
AUDIT BEFORE EXPERIMENT
GAP BEFORE PREREGISTRATION
EVIDENCE BEFORE IMPLEMENTATION
```

This rule remains in force for the rest of the project unless an explicit later governance amendment supersedes it.