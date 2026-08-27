# BIG-B3 — Select New Evaluation Protocol

**Status:** COMPLETE — `PREFERRED`, NOT `FROZEN`  
**Date:** 2026-08-21  
**Gate:** BIG-B3 of [`../docs/BENCHMARK-INTEGRITY-GATE.md`](../docs/BENCHMARK-INTEGRITY-GATE.md)  
**Input:** BIG-B0 factual audit + BIG-B1 exposure ledger + BIG-B2 preregistered comparison/Pareto frontier  
**Agent optimization:** remains paused until BIG-B4 closes

## 1. Decision

BIG-B3 selects the following protocol as the best-supported current evaluation design:

> **P12 — Fresh-Blind Hybrid with External-First Source Hierarchy**

Decision state: **`PREFERRED`**.

P12 keeps the common core shared by BIG-B2 frontier families P1 and P2 and treats the source of fresh blind real-domain evidence as a controlled hierarchy:

1. **Tier A / preferred blind source:** partner-held external blind evaluation (`P1` source).
2. **Tier B / fallback blind source:** independently authored **and independently adjudicated** hidden real-domain groups (`P2` source), with explicit insulation from agent development.
3. **Legacy LOCKED_TEST:** qualified supplementary held-out domain characterization, not the primary proof of blind generalization.
4. **Synthetic/adversarial suites:** supplementary robustness/regression evidence, never a substitute for fresh real-domain blind evidence.

BIG-B3 does **not** select P3 as evidentially equivalent. P3 remains an explicitly degraded emergency path that may be activated only through a documented reversal/amendment if no fresh blind source can be operationalized before the delivery-critical cutoff.

## 2. Why P12 is selected

BIG-B2 established that P1 and P2 are non-dominated and share the same evaluation architecture:

```text
7 historically exposed groups
  → prospective group-aware selection/stability
  → candidate freeze
  → fresh blind real-domain measurement
  + synthetic/adversarial robustness
  + qualified legacy LOCKED_TEST
```

Their only material architectural difference is custody/authorship of the fresh blind source.

A post-hoc weighted score is unnecessary and would violate the BIG-B2 decision policy. Instead BIG-B3 applies hard constraints and dominance:

- P3 is weaker on independence and final evidential strength; it survives only on immediate feasibility.
- P1 supplies the strongest organizational blindness when available.
- P2 preserves fresh evidence without requiring partner infrastructure, but independence depends on author/adjudicator insulation.
- Because P1 and P2 have the same core protocol and differ only in source provenance, selecting an external-first source hierarchy preserves the strongest attainable evidence without making the whole protocol contingent on a single external dependency.

This is a **hybrid source-selection policy**, not an averaging of P1/P2 outcomes.

## 3. Fixed role of every existing benchmark group

### 3.1 Exposed development/selection pool

The historical DEV + historical VALIDATION groups are permanently treated as one exposed pool for future agent engineering:

```text
independent groups   7
scenarios           11
tickets             12
```

They may be used for:

- prompt/policy/model/runtime/retrieval/planner/guard development;
- prospective candidate comparison;
- ablation;
- failure analysis;
- deterministic evaluator development subject to evaluator-validity controls;
- group-sensitivity analysis;
- regression testing.

They may **not** support a fresh independent-holdout claim.

Historical VALIDATION is never relabeled as blind merely because the protocol changes.

### 3.2 Legacy LOCKED_TEST

The three historical LOCKED_TEST groups remain protected from candidate execution until the final authorization path defined by BIG-B4.

Their future role is:

> **qualified supplementary held-out domain characterization**

because:

- no committed candidate/task-quality execution was established by BIG-B0/B1;
- but evaluator-v4 private structural alignment included all three groups and changed evaluator implementation;
- therefore the full evaluation stack is not pristine with respect to their structure.

Rules:

- never describe them as `untouched` or `pristine`;
- do not use them for model/prompt/policy/runtime/architecture selection;
- authorize at most one final measurement per frozen candidate generation;
- return no adaptive development feedback before the final decision;
- if a candidate fails a hard safety requirement on legacy LOCKED_TEST, the claim fails; the split must not then be used as an iterative tuning set.

## 4. Prospective selection protocol on the seven exposed groups

The seven exposed groups are the only internal adaptive selection pool.

BIG-B4 must make the following structure executable:

### 4.1 Group unit

`asset_story_group` is indivisible. No ticket/scenario from one storyline may cross a train/selection fold boundary.

### 4.2 Paired comparisons

Where candidate comparison is possible:

- compare candidates on the same group set;
- use matched seeds/randomness where applicable;
- preserve per-group outcomes rather than only global means;
- preserve modality/risk slices;
- treat deterministic safety constraints as hard constraints, not compensable weighted terms.

### 4.3 Required sensitivity views

The protocol must include:

- full exposed-pool paired result;
- Leave-One-Group-Out (`7` held-out-group views) as a **group-sensitivity diagnostic**;
- modality-sliced reporting, with `contextualize` explicit because only two exposed groups contain that modality;
- failure-family/safety slices;
- uncertainty based on group-level resampling/sensitivity appropriate to small `n`, without presenting naive fold standard error as universally unbiased.

Balanced grouped folds may be added where they answer a specific selection question, but they are not fresh holdouts.

### 4.4 Nested CV boundary

Nested grouped CV is permitted only for a fully automated, reproducible sub-selection procedure whose entire tuning loop can be repeated inside each inner fold. It may not be used to claim that the historical human engineering process has become independent.

## 5. Candidate freeze boundary

Before any fresh blind real-domain measurement:

- candidate code/configuration/prompt/model/provider/runtime/retrieval/guard versions must be frozen;
- evaluator versions and semantic-judge qualification must be frozen for that generation;
- random/seed policy must be frozen;
- primary outcomes, hard safety constraints and uncertainty method must be frozen;
- fresh blind source must remain hidden from developers;
- no result from the fresh blind source may influence candidate development before measurement completion.

A candidate generation is immutable once it enters the blind path.

If blind feedback is viewed and a later candidate is created, that later candidate requires a **new independent blind source/generation** for an independent generalization claim. Reusing the same blind feedback for tuning would consume its independence.

## 6. Fresh blind real-domain source hierarchy

### Tier A — partner-held external blind evaluation

This is preferred because it maximizes separation between developer adaptation and final measurement.

BIG-B4 may instantiate Tier A only if all of the following are operationally confirmed:

- partner/source owner distinct from the agent-development loop;
- hidden case content and expected outcomes unavailable to developers before candidate freeze;
- results returned only after candidate freeze;
- no iterative partial feedback during development;
- asset/story-group independence preserved;
- provenance and adjudication procedure auditable;
- sufficient domain/risk coverage to justify the claims actually made.

### Tier B — independently authored + independently adjudicated hidden groups

Tier B is the preferred fallback if Tier A cannot be operationalized.

It requires separation of roles:

- case author(s) must not use current candidate behavior to tailor cases;
- adjudicator(s) must independently establish expected outcomes/reference supervision;
- hidden semantics remain inaccessible to the developer until candidate freeze;
- the developer may receive only the final frozen measurement, not iterative hints;
- provenance, authoring date, adjudication date and custody must be recorded.

The same person/process should not simultaneously develop the candidate, author the hidden case to exploit known behavior, and adjudicate the expected answer.

### Fresh-blind adequacy

BIG-B4 must tie claim strength to the actual number and diversity of independent fresh groups. It must not convert raw call count into independent sample size.

For a strong real-domain blind claim, the target is to cover all three project modalities across the fresh set and include safety-critical/high-impact behavior. If the available fresh set is narrower, the final claim must be narrowed accordingly.

## 7. Synthetic/adversarial evidence role

Synthetic/adversarial suites are retained because they can cheaply expand failure-mode coverage and support deterministic regression.

They may be used for:

- injection/adversarial behavior;
- malformed/partial tool results;
- evidence insufficiency;
- authorization/safety boundaries;
- provider/runtime fault modes;
- judge/evaluator qualification.

They may not be the sole basis for production-domain generalization.

Any synthetic suite used during adaptive development is development evidence. A final withheld synthetic suite, if desired, must itself be frozen and access-controlled by BIG-B4.

## 8. Final evidence interpretation

Under P12, evidence is intentionally layered:

```text
Layer 1 — 7 exposed groups
selection, ablation, sensitivity, regression
NOT blind generalization

Layer 2 — fresh blind real-domain source
PRIMARY independent generalization evidence
Tier A partner-held preferred; Tier B independently authored/adjudicated fallback

Layer 3 — legacy LOCKED_TEST
qualified supplementary held-out domain evidence
structural evaluator exposure disclosed

Layer 4 — synthetic/adversarial
robustness and failure-mode evidence
NOT a real-domain substitute
```

No single layer may be described as proving more than its independence and coverage support.

## 9. Reversal triggers

Reversal triggers are operational safeguards, not weighted evidence scores.

### R1 — Tier A availability trigger

By **2026-08-25 23:59 America/Sao_Paulo**, Tier A must have an operationally credible path: named source owner/custodian, blind-custody rule, expected delivery window, and confirmation that no adaptive feedback will be returned before candidate freeze.

If this is not established, the fresh-blind source automatically moves to **Tier B** for B4 planning. This does not require re-running BIG-B2 because P2 is already on the frozen Pareto frontier.

### R2 — Tier B insulation trigger

By **2026-08-28 23:59 America/Sao_Paulo**, Tier B must have an auditable author/adjudicator separation plan and a feasible hidden real-domain case-generation/custody path.

If neither Tier A nor Tier B is operationally feasible by this cutoff, **do not silently weaken P12**. Create a BIG-B3 amendment that activates the P3 degraded path explicitly.

### R3 — degraded P3 consequences

If P3 must be activated:

- final evidence becomes exposed-pool selection + one qualified legacy LOCKED_TEST measurement + synthetic/adversarial robustness;
- claims must be downgraded to `qualified benchmark performance under a structurally exposed legacy final set`;
- no claim of strong independent production-domain generalization is authorized;
- the reason for fallback and missing fresh blind evidence must be prominent in the final report.

### R4 — blind-source breach

Any semantic leak, iterative partial feedback, candidate inspection of hidden labels, or author/adjudicator adaptation to candidate outputs before freeze invalidates the fresh source for an independent claim. The source is then reclassified as exposed and a new source/generation is required.

### R5 — evaluator/judge change after blind access

A material evaluator/judge change made in response to blind outcomes consumes the blind measurement for that evaluation-stack generation. A new final measurement source is required for a fresh independent claim.

## 10. Rejected selections

### P3 as preferred protocol — rejected

P3 is not selected because it is dominated by P1/P2 on independence and evidential strength. Its only advantage is immediate feasibility. That makes it an emergency degraded path, not the best-supported default protocol.

### P1 only — rejected as the entire protocol

Selecting P1 without a predeclared fallback would make the evaluation protocol unnecessarily brittle to partner availability despite P2 already being non-dominated and architecturally compatible.

### P2 only — rejected as the entire protocol

Selecting P2 as the default would give up the stronger organizational blindness available from P1 before availability is tested.

### Nested CV as the whole-system protocol — rejected

It cannot retroactively nest the historical human adaptation process and therefore cannot replace a fresh blind path.

## 11. Decision state and B3 exit

BIG-B3 has now:

- applied the BIG-B2 hard constraints;
- selected a single protocol architecture rather than an arbitrary weighted winner;
- defined the seven exposed groups as the adaptive pool;
- selected fresh blind real-domain evidence as the primary final path;
- selected external partner custody first and independent author/adjudicator custody second;
- retained legacy LOCKED_TEST only as qualified supplementary evidence;
- retained synthetic/adversarial evaluation as supplementary robustness evidence;
- defined explicit no-feedback and re-use rules;
- defined reversal/breach triggers;
- kept P3 only as an explicit degraded contingency.

**BIG-B3 status: COMPLETE.**

**Selected protocol:** `P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST`  
**Decision state:** `PREFERRED`  
**Not yet:** `FROZEN`

The active gate becomes **BIG-B4 — Freeze Evaluation Protocol**. Agent optimization remains paused until B4 makes this preferred design executable, auditable, access-controlled and regression-protected.