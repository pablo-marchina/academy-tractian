# BIG-B2 — Evaluate Benchmark-Design Alternatives

**Status:** COMPLETE — COMPARISON / PARETO FRONTIER ONLY  
**Date:** 2026-08-21  
**Gate:** BIG-B2 of [`../docs/BENCHMARK-INTEGRITY-GATE.md`](../docs/BENCHMARK-INTEGRITY-GATE.md)  
**Preregistration:** [`experiments/big-b2-benchmark-design-comparison-preregistration.json`](experiments/big-b2-benchmark-design-comparison-preregistration.json)  
**Selection:** explicitly deferred to BIG-B3  
**Agent optimization:** remains paused

## 1. Question

Given BIG-B1's actual exposure history, only ten independent asset/story groups, the production objective, the 2026-09-08 delivery target, and the requirement for future adaptive optimization, which evaluation-design families are defensible, which are dominated, and which remain on a Pareto frontier?

BIG-B2 does **not** select the future protocol. The comparison criteria and candidate families were preregistered before this comparative conclusion was committed.

## 2. Fixed facts entering B2

From the frozen public split plus BIG-B1:

```text
independent asset/story groups total                 10
historically adaptively exposed groups                7
  DEV                                                  5
  historical VALIDATION                                2
legacy LOCKED_TEST groups                              3
exposed-pool scenarios                                11
exposed-pool tickets                                  12
exposed groups containing contextualize                2
legacy LOCKED_TEST groups containing contextualize     1
```

Current evidential status:

- DEV is development-exposed by design.
- historical VALIDATION is adaptively exposed and not independent for descendant generalization.
- LOCKED_TEST has no committed candidate/task-quality execution established, but it is structurally exposed because evaluator-v4 private alignment included all three locked groups and changed evaluator design.

No new semantic/private inspection of VALIDATION or LOCKED_TEST was performed for B2.

## 3. Methodological evidence synthesis

### 3.1 Adaptive holdout reuse

Dwork et al. formalize adaptive data analysis: analyses/hypotheses chosen after prior results violate the non-adaptive assumptions behind ordinary inference, and repeated holdout reuse can overfit the holdout. That maps directly to the BIG-B1 history: aggregate feedback is enough to create adaptive dependence; row-level oracle exposure is not required.

Reference: Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse* (2015), https://arxiv.org/abs/1506.02629

### 3.2 Model-selection criterion can itself be overfit

Cawley & Talbot show that optimizing a finite-sample model-selection criterion can overfit that criterion and create subsequent performance-selection bias. Low variance of the selection criterion matters, not merely low bias.

Reference: Cawley & Talbot, JMLR 11 (2010), https://www.jmlr.org/papers/v11/cawley10a.html

Consequence here: repeatedly choosing prompts/policies/runtimes against the same small group pool can overfit the **selection process**, even when each candidate is otherwise valid.

### 3.3 Nested CV is useful only when the complete selection procedure is nested

Varma & Simon show that reporting CV performance after selecting parameters on the same CV is optimistic; nested CV greatly reduces the bias when **all selection/tuning steps are repeated inside the nested procedure**.

Reference: Varma & Simon, BMC Bioinformatics 7:91 (2006), https://pubmed.ncbi.nlm.nih.gov/16504092/

For this project that distinction is decisive. Automated subcomponent tuning can potentially be repeated within nested folds. The full historical human agent-engineering process cannot be reset and independently rerun as if the seven exposed groups had never been seen. Therefore nested CV on those seven groups can evaluate an explicitly automated selection algorithm, but it cannot retroactively restore blind independence to the whole project.

### 3.4 Small-sample CV uncertainty is intrinsically difficult

Bengio & Grandvalet prove there is no universal unbiased estimator of k-fold CV variance based only on the fold results; overlapping training sets create correlations that naive variance estimates can miss.

Reference: Bengio & Grandvalet, JMLR 5 (2004), https://www.jmlr.org/papers/v5/grandvalet04a.html

Varoquaux further demonstrates that small samples can produce large CV error bars and that the standard error across folds can substantially understate uncertainty.

Reference: Varoquaux, NeuroImage 180 (2018), https://pubmed.ncbi.nlm.nih.gov/28655633/

Arlot & Celisse survey CV as both risk-estimation and model-selection machinery and emphasize that the best procedure depends on the exact goal and bias/variance regime rather than one universally best k-fold choice.

Reference: Arlot & Celisse, Statistics Surveys 4 (2010), https://projecteuclid.org/journals/statistics-surveys/volume-4/issue-none/A-survey-of-cross-validation-procedures-for-model-selection/10.1214/09-SS054.pdf

### 3.5 Group-level splitting remains mandatory

The unit of independence is asset/story group, not ticket/scenario. GroupKFold/LeaveOneGroupOut are appropriate implementation families because they keep groups non-overlapping between train/test partitions.

References:

- https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
- https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html

This is implementation evidence, not a claim that sklearn's default k is optimal for this project.

## 4. Provider-free public geometry analysis

Executable analysis:

[`../scripts/research/big_b2_benchmark_design_geometry.py`](../scripts/research/big_b2_benchmark_design_geometry.py)

Frozen result:

[`results/big-b2-public-benchmark-geometry-2026-08-21.json`](results/big-b2-public-benchmark-geometry-2026-08-21.json)

The analysis reads only `research/frozen/benchmark-split-v1.json` public metadata.

### 4.1 Seven exposed groups

The exposed development/selection pool has 7 groups, 11 scenarios and 12 tickets. Only two groups contain `contextualize`:

```text
asset_M101
asset_B204
```

This creates a structural concentration that any group-aware CV design must expose rather than hide.

### 4.2 Balanced two-fold geometry

There are 35 unique balanced 3/4 group partitions.

```text
partitions with contextualize in both test folds     20 / 35 = 57.14%
minimum scenario-count imbalance                      1
```

A constrained two-fold split can put one contextualize group in each fold, giving both train and test contextualize coverage. But two outer folds provide very few independent group partitions and therefore weak uncertainty characterization.

### 4.3 Balanced three-fold geometry

There are 105 unique balanced 3/2/2 partitions.

```text
partitions with contextualize in every training fold  80 / 105 = 76.19%
partitions with contextualize in every test fold        0 / 105 = 0%
best test scenario counts                               3 / 4 / 4
```

No three-fold partition can include contextualize in every test fold because only two independent exposed groups contain that modality. A constrained three-fold design can, however, keep the two contextualize groups in different folds so that every training fold still contains contextualize.

Consequence: a three-fold overall score must not be interpreted as three equally representative modality-complete test folds. Modality-sliced and group-level reporting is mandatory.

### 4.4 Leave-One-Group-Out

```text
outer folds                                      7
training folds retaining contextualize           7 / 7
test folds containing contextualize               2 / 7
```

LOGO has a useful property here: every training fold still has at least one contextualize group. It is attractive as a **group-sensitivity diagnostic** because every group becomes the held-out unit once. It is not a fresh/blind estimate after all seven groups have already been adaptively exposed.

### 4.5 Leave-Two-Groups-Out

```text
unique held-out group pairs                     21
training folds retaining contextualize          20 / 21
test folds containing contextualize             11 / 21
```

This provides broader stress testing of group combinations but is computationally heavier and the fold estimates are highly dependent because training sets overlap.

### 4.6 Legacy LOCKED_TEST concentration

The 3-group LOCKED_TEST contains 5 scenarios and 5 tickets. Only `asset_V301` contains contextualize. Therefore a final contextualize conclusion from that split is effectively supported by one independent storyline group.

This does not make the group useless; it limits the precision and breadth of the claim.

### 4.7 Illustrative small-n precision

For intuition only, if each independent group were reduced to a Bernoulli pass/fail variable and every group passed, a 95% Wilson lower bound would be approximately:

```text
2 groups → 0.342
3 groups → 0.439
5 groups → 0.566
7 groups → 0.646
```

These are **not** final metric confidence intervals: real group outcomes are heterogeneous and need not be IID Bernoulli. The illustration simply shows why 2–3 independent groups cannot support a high-precision population claim merely because all of them pass.

## 5. Candidate-family comparison

No weighted score is used. Hard constraints are applied first; remaining trade-offs are reported directly.

| ID | Design family | Historical independence | Selection efficiency | Blind evidence | Small-n / stability | Production/domain evidence | Operational feasibility | B2 assessment |
|---|---|---|---|---|---|---|---|---|
| A | Keep current DEV / VALIDATION / LOCKED_TEST roles | **Fails if VALIDATION is called independent** | Wastes 2 exposed groups if kept out of development | LOCKED_TEST only, structurally exposed | Weak | Existing domain cases | Very high | **Dominated as a truthful future design** |
| B | Reclassify historical VALIDATION into exposed development pool | Honest about exposure | **7 groups available** | No new blind validation; legacy locked remains qualified | Better development coverage, no independence restoration | Existing domain cases | Very high | **Strong building block, insufficient alone for strongest final claim** |
| C | Grouped repeated/rotating CV on 7 exposed groups | Does not restore blindness | Uses all 7 repeatedly | Requires separate final path | **Good for group sensitivity/paired comparison**; correlated folds remain | Existing domain cases | High | **Strong selection/stability layer, not final holdout** |
| D | Nested grouped CV on 7 exposed groups | Cannot erase historical human exposure | Data-hungry inner/outer loops | Requires separate final path | High variance with 7 groups; modality sparsity | Existing domain cases | Medium/low for full system | **Useful only for automated repeatable sub-selection; not whole-project independence solution** |
| E | New blind validation groups | **High if genuinely unseen and labels hidden** | Leaves exposed 7 for development | Fresh blind validation; final source still needed/defined | Precision depends on new group count | Can be highly domain-representative | Medium | **Non-dominated fresh-evidence family** |
| F | Partner-held blind evaluation | **Very high** if developer receives no adaptive feedback | Leaves exposed 7 for development | Strong external blind measurement | Precision depends on partner-held group count | Potentially strongest real-domain evidence | External dependency | **Non-dominated if available** |
| G | Independently authored/adjudicated new cases | Medium-high to high depending separation | Leaves exposed 7 for development | Fresh blind evidence if author/adjudicator insulated | Precision depends on group count | Domain quality depends on authorship | Medium/high | **Non-dominated self-contained fresh-evidence path** |
| H | Frozen synthetic/adversarial supplement | Synthetic independence can be high | Efficient targeted stress testing | **Not sufficient as real-domain final evidence** | Can cheaply increase failure-mode count | Lower ecological validity | Very high | **Valuable supplement; fails as standalone replacement** |
| I | Hybrid: exposed-pool group CV + fresh blind source(s) + qualified legacy locked | **Highest attainable separation when fresh source is truly held out** | Uses all 7 exposed groups | Fresh blind measurement plus legacy characterization | Best ability to separate selection stability from final measurement | Can combine domain + adversarial coverage | Medium | **Non-dominated hybrid family; exact variant deferred to B3** |

## 6. Why several tempting solutions are insufficient

### 6.1 Simply renaming VALIDATION

Renaming the two historical VALIDATION groups as a new validation set does nothing. BIG-B1 already documents adaptive influence. This family fails the independence hard constraint.

### 6.2 Cross-validation as an independence repair

Group-aware CV over the seven exposed groups is highly useful for prospective comparison, ablation, stability and sensitivity to individual storylines. It does **not** make those groups unseen again.

Accordingly, future claims must distinguish:

```text
selection/stability evidence on exposed groups
vs
blind generalization evidence on fresh/appropriately protected groups
```

### 6.3 Nested CV as a universal fix

Nested CV is principled when the complete model-selection algorithm can be rerun inside the inner loop. For automated hyperparameter/model/router selection this can be appropriate.

For whole-project agent engineering, the historical human hypothesis-generation path cannot be nested retrospectively. Therefore D is not a standalone cure for historical exposure.

### 6.4 Legacy LOCKED_TEST as pristine final proof

The legacy locked groups have not been shown to have candidate/task-quality execution in committed evidence, which preserves meaningful value. But evaluator-v4 structural private alignment included those groups and changed evaluator design. Calling the complete evaluation stack pristine is therefore too strong.

B2 treats legacy LOCKED_TEST as potentially valuable **qualified held-out domain evidence**, not automatically as either unusable or pristine. Its exact future role is a B3 choice.

### 6.5 Synthetic benchmark as final production evidence

Synthetic/adversarial suites are excellent for failure-mode coverage, judge/evaluator qualification and deterministic regression. They cannot alone establish production-domain generalization. H therefore remains supplementary.

## 7. Pareto frontier

BIG-B2 identifies a frontier rather than a winner.

### Frontier family P1 — external-blind hybrid

```text
7 exposed groups
  → group-aware repeated comparison / group sensitivity
  → candidate freeze
  → partner-held fresh blind measurement
  + synthetic/adversarial robustness suite
  + legacy LOCKED_TEST retained with qualified role
```

Strength: strongest separation from developer adaptation and strongest auditability if partner data are truly held.  
Trade-off: external dependency and uncertain availability before delivery.

### Frontier family P2 — independently-authored blind hybrid

```text
7 exposed groups
  → group-aware repeated comparison / group sensitivity
  → candidate freeze
  → independently authored + independently adjudicated hidden new groups
  + synthetic/adversarial robustness suite
  + qualified legacy LOCKED_TEST
```

Strength: can be executed without requiring partner infrastructure while adding genuinely fresh evidence if authoring/adjudication are insulated.  
Trade-off: weaker independence than a partner-held source when the same organization controls case generation; representativeness and label quality require explicit QA.

### Frontier family P3 — deadline-minimal qualified legacy path

```text
7 exposed groups
  → honest development/selection pool
  → constrained group-aware repeated comparisons
  → candidate freeze
  → one authorized legacy LOCKED_TEST measurement
  + synthetic/adversarial robustness
```

Strength: maximum feasibility and no need for new case acquisition.  
Trade-off: final claim must be explicitly weaker because the locked evaluator structure is no longer pristine and only 3 independent final groups exist, with contextualize concentrated in one group.

This remains on a practical feasibility frontier, but it is **not** evidentially equivalent to P1/P2.

### Component-level technique — nested CV

Nested grouped CV remains a valid component inside P1/P2/P3 when optimizing a fully automated, reproducible subprocedure (for example model/router parameters) and when every selection step is truly repeated within the inner loop. It is not a separate whole-system frontier solution to historical human adaptive exposure.

## 8. Dominance findings

The following dominance relationships are sufficiently strong to record before B3:

1. **A is dominated by B for future development accounting.** Both inherit the same historical exposure, but B truthfully uses all seven exposed groups instead of pretending the two historical validation groups can supply blind evidence.
2. **H cannot dominate any real-domain blind source** because it fails the preregistered hard constraint against synthetic-only production generalization.
3. **D does not dominate C for whole-system engineering.** It adds computational complexity but cannot restore the historical human-process independence that C openly does not claim. D is valuable only for nested automated subprocedures.
4. **P1 and P2 are not mutually dominated**: P1 has stronger organizational blindness; P2 has lower external dependency and potentially higher feasibility.
5. **P3 is not evidentially competitive with P1/P2 but remains non-dominated on immediate feasibility** if no fresh blind source can be acquired by the deadline.

## 9. Requirements that any B3-selected protocol must inherit

Regardless of which frontier variant BIG-B3 selects, the evidence says the protocol should preserve these properties:

- historical DEV + VALIDATION are treated as exposed data, never as fresh holdout;
- all splitting occurs at asset/story-group level;
- prospective candidate comparisons are paired on the same groups/seeds where possible;
- fold/group distributions are retained, not only means;
- contextualize coverage is tracked as a separate slice because only two exposed groups contain it;
- no naive fold standard error is advertised as an unbiased uncertainty estimate;
- nested CV is used only where the full tuning process is actually nested;
- final/blind data return no adaptive feedback before candidate freeze;
- synthetic/adversarial suites supplement but do not replace real-domain evidence;
- LOCKED_TEST's structural exposure is documented in any final claim;
- a breach-response rule must exist in B4 if fresh blind data are accidentally exposed;
- final claims must scale with the actual number and diversity of independent blind groups rather than with raw call/repeat counts.

## 10. Fresh-group count sensitivity — no minimum selected here

B2 deliberately does not invent a universal minimum number of new groups. It records the trade-off:

- 2 fresh groups are materially better than zero but provide extremely weak group-level precision;
- 3 fresh groups match the legacy locked group count but remain statistically sparse;
- 5+ fresh groups materially improve diversity/precision but increase authoring/acquisition cost;
- external partner-held groups can be more valuable than the same count of internally authored groups when organizational blindness and production representativeness are higher.

The B3 decision should therefore select a target fresh-group count from an explicit feasibility/coverage analysis rather than an arbitrary threshold.

## 11. BIG-B2 exit gate

- [x] candidate space includes materially different retain/reclassify/CV/nested/fresh/external/synthetic/hybrid strategies;
- [x] comparison dimensions and hard constraints were preregistered before comparative conclusion;
- [x] public group geometry was quantified reproducibly;
- [x] methodological evidence was synthesized from primary/authoritative sources;
- [x] no private benchmark semantics were reopened;
- [x] no new candidate/provider inference was performed;
- [x] dominated alternatives were identified with explicit reasons;
- [x] a Pareto frontier was identified without selecting a winner;
- [x] uncertainty and small-sample limitations were preserved;
- [x] BIG-B3, not BIG-B2, retains protocol-selection authority.

**BIG-B2 status: COMPLETE.**

Next active gate: **BIG-B3 — Select New Evaluation Protocol**.
