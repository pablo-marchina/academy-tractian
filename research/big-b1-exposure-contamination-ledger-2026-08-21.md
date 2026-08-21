# BIG-B1 — Exposure / Contamination Ledger

**Status:** COMPLETE — INDEPENDENCE / INFLUENCE CLASSIFICATION  
**Date:** 2026-08-21  
**Gate:** BIG-B1 of [`../docs/BENCHMARK-INTEGRITY-GATE.md`](../docs/BENCHMARK-INTEGRITY-GATE.md)  
**Input:** [`results/big-b0-benchmark-access-ledger-2026-08-21.json`](results/big-b0-benchmark-access-ledger-2026-08-21.json)  
**Agent optimization:** remains paused  
**Benchmark redesign / recoverability decision:** explicitly deferred to BIG-B2

## 1. Purpose

BIG-B1 classifies the independence impact of every BIG-B0 exposure. It answers:

- which historical benchmark exposures were merely public/protocol metadata;
- which exposures directly or transitively informed later candidate/evaluator development;
- which split-derived feedback breaks an independent-holdout claim;
- what the strongest currently supportable independence statement is for DEV, VALIDATION and LOCKED_TEST;
- where uncertainty remains because local/operator-only history is not fully observable.

BIG-B1 does **not** select a replacement split, cross-validation design, new holdout, external benchmark or final-test protocol. Those alternatives must be compared systematically in BIG-B2.

Machine-readable companion: [`results/big-b1-exposure-contamination-ledger-2026-08-21.json`](results/big-b1-exposure-contamination-ledger-2026-08-21.json).

## 2. Governing classification rule

The active Benchmark Integrity Gate already defines the decisive rule:

> For a claimed independent holdout, any split-derived information that materially influences later candidate development breaks independence for that later decision, even when the feedback was aggregate-only.

Therefore:

- row-level expected paths do **not** need to have been exposed for a holdout-independence loss to occur;
- a combined DEV+VALIDATION metric still counts as validation-derived feedback when that metric is used for selection;
- returning to DEV-only execution later does not restore independence if the next hypothesis/component was already shaped by validation feedback;
- public split metadata does not by itself consume hidden outcome information;
- evaluator-only structural inspection is classified separately from candidate/task-quality feedback.

This is an independence accounting rule, not an accusation of historical protocol violation. E3 explicitly assigned VALIDATION a selection/tuning role; early uses can be historically compliant and still make the same split unsuitable as an independent holdout for later descendants.

## 3. Classification vocabulary

| Classification | Meaning |
|---|---|
| `EXPECTED_DEVELOPMENT_EXPOSURE` | DEV use consistent with development/calibration. |
| `DIRECT_ADAPTIVE_SELECTION` | Split outcome directly selected/promoted a candidate/component. |
| `DIRECT_ADAPTIVE_*` | Split-derived outcome shaped model, prompt, policy, runtime, evaluator or architecture development. |
| `DIRECT_ADAPTIVE_REUSE_WITHOUT_NEW_READ` | Prior split-derived feedback was explicitly reused even though no new split execution occurred. |
| `STRUCTURAL_EVALUATOR_ADAPTATION` | Private nonsemantic oracle shape/alignment changed evaluator design. |
| `PUBLIC_METADATA_ONLY` | Public counts/coverage/split structure; no hidden task outcome consumed. |
| `NO_NEW_SPLIT_READ` | No new exposure in the event; prior adaptive influence remains unchanged. |
| `NONE_FROM_THIS_EVENT` | No frozen benchmark split was consumed. |

No single severity score is used. Candidate execution, private-oracle access, information granularity, adaptive influence and confidence remain separate dimensions.

## 4. Event-by-event classification

| B0 event | Phase | Split(s) | Exposure / granularity | Adaptive influence | Independence impact | Confidence |
|---|---|---|---|---|---|---|
| E001 | E3 | DEV / VALIDATION / LOCKED_TEST | Policy + public metadata | Policy role definition | No outcome-feedback loss from definition itself | High |
| E002 | E4 | VALIDATION | Candidate comparison + private validation scoring + split aggregate | **Direct, documented:** B3 promoted; E5 directed | **First documented adaptive use that prevents VALIDATION from serving as an independent holdout for later descendants** | High |
| E003 | E5 | DEV + VALIDATION | Combined candidate-strategy aggregate | **Direct, documented:** evidence-sufficiency policy promoted | VALIDATION contributes to a selection statistic; independence remains lost even though split effect size is not separable | High |
| E004 | E6 | DEV + VALIDATION | Live runtime/API execution on representative cases | **Direct, documented:** LangGraph live path promoted | Validation-informed architecture/runtime decision | High |
| E005 | E7 | DEV + VALIDATION | Native vs MCP comparison | **Direct, documented:** tool-surface candidates selected | Validation-informed topology decision | High |
| E006 | E8 | DEV + VALIDATION | Real provider/model proxy/schema/latency metrics | **Direct, documented:** Groq prioritized | Validation-informed model/provider prioritization | High |
| E007 | E9 | DEV + VALIDATION | Private scorer; combined task-quality aggregate; local row visibility unknown | **Direct, documented:** development objectives changed | Validation contributed to private-scored feedback used downstream | High |
| E008 | E10d | DEV + VALIDATION | **Split-level** private metrics | **Direct, documented:** VALIDATION premature-action failure motivated E10e | Split-specific adaptive feedback | High |
| E009 | E10e | DEV + VALIDATION | **Split-level** private metrics | **Direct, documented:** persistent pattern motivated E10f | Split-specific adaptive feedback | High |
| E010 | E10g | DEV + VALIDATION | **Split-level** private metrics | **Direct, documented:** repeated failure redirected safety research | Split-specific adaptive feedback | High |
| E011 | E10h | Prior DEV + VALIDATION aggregates | Aggregate reuse; no new candidate run | **Direct, documented reuse:** full pattern used to formulate E11 | Demonstrates transitive influence; no new read is required for independence loss to persist | High |
| E012 | E11 | DEV + VALIDATION | Split-level private metrics | **Direct, documented:** failure led to instrumentation diagnosis | Split-specific adaptive feedback | High |
| E013 | E12 | DEV + VALIDATION | Split-level capture metadata: action class, endpoint, authorization reason | **Direct, documented:** root-cause mechanisms constrained | Additional split-specific behavioral feedback shaped later authorization design | High |
| E014 | E13 | DEV only | DEV private scoring + blocker audit | No new VALIDATION read; later work shaped by preceding authorization lineage | DEV is expected development exposure; **no restoration** of prior VALIDATION independence | Medium-high |
| E015 | Public split audit | DEV / VALIDATION / LOCKED_TEST | Public counts/coverage only | Protocol design only | No hidden semantic/candidate feedback added | High |
| E016 | Policy amendments | DEV / VALIDATION / LOCKED_TEST | Policy only | Changes future rules | Cannot retroactively restore VALIDATION independence; no new LOCKED_TEST exposure | High |
| E017 | Evaluator v4 validity | DEV / VALIDATION / LOCKED_TEST | **Structural private oracle alignment**, nonsemantic aggregate | **Direct, documented on evaluator:** changed alignment implementation | LOCKED_TEST full-stack blindness reduced; candidate execution/task-quality feedback still not established | High |
| E018 | E14 full-DEV line | DEV only | DEV candidate/private deterministic scoring | No new VALIDATION/LOCKED_TEST read; inheritance from earlier stack only partially reconstructable | DEV remains development-exposed; historical validation influence cannot be presumed erased | Medium |
| E019 | E14v public synthetic | None | Public synthetic only | None on frozen splits | No frozen-split impact | High |
| E020 | Benchmark Integrity Gate | None | Governance pause | Prevents new exposure | No benchmark-feedback impact | High |

The JSON companion preserves the complete B1 schema for all 20 records, including `candidate_executed`, `private_oracle_loaded`, `row_level_feedback_observed`, `raw_semantic_oracle_observed`, downstream decisions, confidence and source artifacts.

## 5. Material influence graph

The historical lineage is not a collection of isolated validation checks. Several validation-inclusive decisions were carried forward:

```text
E4 VALIDATION comparison
  └─ B3 guarded boundary promoted
      └─ E5 evidence/stopping
          └─ evidence-sufficiency policy promoted
              └─ E6 live integration / LangGraph candidate
                  └─ E7 native/MCP topology

E8 DEV+VALIDATION provider run
  └─ Groq prioritized
      └─ E9 private task-quality scoring
          └─ later DEV improvement objectives

E10d VALIDATION split failure
  └─ E10e safety direction
      └─ E10f / E10g safety line
          └─ E10h aggregate blocker analysis
              └─ E11 independent authorization
                  └─ E12 split instrumentation/root cause
                      └─ E13 DEV-only authorization line
```

The last chain is especially important. E10h explicitly states that the repeated E10d/E10e/E10g full pattern was used to reject the self-attested-safety assumption and specify the next E11 design. Therefore a later `DEV-only` implementation can avoid **new** validation exposure while still remaining a descendant of validation-informed development.

For E14, committed records establish that new execution was DEV-only/full-DEV after the policy change. They do not fully prove which prior validation-selected components/hypotheses persisted unchanged into every E14 variant. B1 therefore records transitive influence as possible/partially documented rather than inventing a stronger edge.

## 6. Current split independence status

### DEV — `DEVELOPMENT_EXPOSED_BY_DESIGN`

**Classification:** not an independent holdout.

Evidence:

- candidate development and repeated comparisons were performed on DEV;
- private evaluator/oracle material was repeatedly used scorer-side;
- DEV-only diagnostics and full-DEV optimization continued through E14.

This is not a defect: DEV exists to support development.

**Strongest claim supportable now:**

> DEV is a development/calibration pool. It may participate in future tuning, resampling or model-selection procedures only under the protocol selected/frozen by BIG-B2→B4; it cannot supply an independent final-generalization claim.

**Confidence:** high.

Human inspection of local private scorer rows remains `UNKNOWN_LOCAL_ONLY`, but this does not affect the conclusion that DEV is development-exposed.

### VALIDATION — `ADAPTIVELY_EXPOSED / NOT INDEPENDENT FOR CURRENT OR FUTURE CANDIDATE GENERALIZATION`

**Classification:** candidate holdout independence is not preserved for post-E4 development and descendants.

The conclusion does **not** depend on unknown row-level exposure. The committed aggregate history is sufficient:

- E4 directly used VALIDATION to compare/promote B3;
- E5–E8 used validation-inclusive outcomes in evidence-policy, runtime, tool-topology and provider/model decisions;
- E9 exposed private-scored DEV+VALIDATION aggregate task-quality results and redirected development;
- E10d/E10e/E10g/E11 exposed split-level validation performance;
- E10h reused prior full aggregates to formulate E11;
- E12 exposed split-level authorization metadata and constrained the next design.

Counts from the B0/B1 ledger:

```text
documented candidate-execution events involving VALIDATION      10
documented private-oracle scoring events before v4 structural    6
documented adaptive result/diagnostic events E4→E12            >=12
```

The original E3 policy intentionally used VALIDATION for selection/tuning, so these facts do not imply historical rule-breaking. They mean the split has already fulfilled a development-selection role and cannot simultaneously be treated as an independent holdout for descendants selected with its feedback.

**Strongest claim supportable now:**

> Historical VALIDATION results remain useful descriptive evidence about historical candidates, but VALIDATION is not an independent holdout for current/future candidate, policy, runtime, provider or architecture generalization claims. A 2026-08-18 policy change to “measurement-only” prevents new direct tuning but cannot erase already incorporated adaptive influence.

**Confidence:** high for loss of candidate independence; medium for the total exposure extent because operator-local row inspection is unknown.

**Recoverability:** deliberately not decided here.

### LOCKED_TEST — `STRUCTURALLY_EXPOSED / CANDIDATE-UNEXECUTED IN COMMITTED RECORD`

LOCKED_TEST requires two independent dimensions.

#### Candidate/task-quality dimension

B0/B1 found no committed evidence of:

- candidate/model/prompt/policy execution on LOCKED_TEST;
- task-quality scoring of a candidate on LOCKED_TEST;
- split-level candidate outcome feedback from LOCKED_TEST;
- semantic expected-path content committed or fed to a candidate.

Therefore B1 does **not** claim candidate-level contamination from observed task outcomes.

#### Evaluator-design dimension

Evaluator-v4 validity work loaded private oracle structure for all frozen groups and reported:

```text
DEV:         5 / 5 selected tickets with exact single-row alignment
VALIDATION:  2 / 2
LOCKED_TEST: 3 / 3
```

That structural result changed evaluator-v4 implementation from group-level oracle union to exact selected-ticket alignment.

Therefore:

- the phrase `LOCKED_TEST untouched` is unsupported literally;
- the split was structurally inspected using private oracle information;
- that split-derived structural information influenced evaluator design;
- the evaluation stack is no longer fully blind/pristine with respect to LOCKED_TEST structure.

This is materially different from exposing expected paths or evaluating a candidate. B1 does **not** collapse those categories.

**Strongest claim supportable now:**

> No committed evidence establishes candidate execution or task-quality feedback on LOCKED_TEST, but LOCKED_TEST is structurally exposed for evaluator design and therefore cannot be described as a completely untouched/pristine holdout for the full evaluation stack. Whether that structural exposure still permits a defensible final-holdout role must be evaluated in BIG-B2.

**Confidence:** high for structural exposure; medium-high for the statement that no committed candidate execution exists; broader uncommitted/operator-local history remains a bounded unknown.

## 7. Exposure dimensions by split

| Dimension | DEV | VALIDATION | LOCKED_TEST |
|---|---|---|---|
| Public metadata exposed | Yes | Yes | Yes |
| Candidate execution | Yes, extensive | **Yes, repeated** | Not established |
| Private oracle loaded by evaluator | Yes | **Yes, repeated** | **Yes, structural diagnostic** |
| Aggregate outcome feedback | Yes | **Yes, repeated** | No candidate outcome established |
| Split-level outcome feedback | Yes | **Yes** | No candidate outcome established |
| Row-level semantic feedback human-observed | Unknown local-only | Unknown local-only | No evidence; bounded unknown |
| Raw semantic oracle candidate-visible | No evidence / prohibited by protocol | No evidence / prohibited by protocol | No evidence |
| Adaptive candidate influence | Expected | **Direct + transitive, documented** | Not established |
| Adaptive evaluator influence | Yes | Yes | **Yes, structural** |
| Independent final-holdout claim | No | **No for descendants** | **Unresolved; pristine claim unsupported** |

## 8. Unknowns and confidence bounds

BIG-B1 does not convert missing records into negative facts. The following remain unresolved:

1. whether operator-local `--include-rows` scorer output was manually inspected before sanitization;
2. whether uncommitted local benchmark runs existed;
3. whether any pre-v4 structural diagnostic exposed additional private semantics;
4. exact persistence of each historical validation-selected component/hypothesis into every E14 variant.

These unknowns can increase exposure magnitude; they are not needed to reach the high-confidence conclusion about VALIDATION, because aggregate adaptive influence is already documented.

For LOCKED_TEST, the unknowns matter more. B1 therefore uses the narrower claim `candidate execution not established in committed evidence` rather than `never accessed` or `fully independent`.

## 9. What BIG-B1 changes — and does not change

BIG-B1 changes the evidence-status language:

```text
DEV
  development-exposed; not an independent holdout

VALIDATION
  adaptively exposed; not independent for current/future descendant generalization

LOCKED_TEST
  no committed candidate/task-quality execution established
  BUT structurally exposed for evaluator design
  pristine/untouched full-stack holdout claim unsupported
  final-holdout eligibility unresolved
```

BIG-B1 does **not**:

- move any group between splits;
- declare VALIDATION recoverable or unrecoverable;
- declare LOCKED_TEST usable or unusable as final test;
- select cross-validation, nested CV, a new blind set, external evaluation or any hybrid;
- reopen hidden benchmark content;
- resume agent optimization.

Those are BIG-B2/BIG-B3/BIG-B4 responsibilities.

## 10. BIG-B1 exit assessment

- [x] every BIG-B0 event has a BIG-B1 ledger record;
- [x] candidate execution and evaluator/private-oracle access remain separate;
- [x] aggregate-only adaptive feedback is treated as capable of breaking holdout independence;
- [x] direct and transitive influence chains are recorded;
- [x] every material historical decision in the reconstructed chain is linked to preceding benchmark evidence;
- [x] DEV current independence status classified;
- [x] VALIDATION current independence status classified;
- [x] LOCKED_TEST candidate-vs-evaluator independence classified separately;
- [x] uncertainty/confidence preserved;
- [x] no recoverability or benchmark redesign decision made;
- [x] no new private benchmark inspection performed.

**BIG-B1 status: COMPLETE.**

The next active gate is **BIG-B2 — Evaluate Benchmark-Design Alternatives**. It must compare credible evaluation designs systematically and quantitatively using only information permitted by the gate before any protocol is selected.
