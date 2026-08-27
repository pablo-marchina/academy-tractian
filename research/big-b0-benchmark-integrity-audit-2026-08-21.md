# BIG-B0 — Benchmark Integrity Audit: Chronological Split-Use Reconstruction

**Status:** COMPLETE — FACTUAL RECONSTRUCTION ONLY  
**Date:** 2026-08-21  
**Gate:** BIG-B0 of [`../docs/BENCHMARK-INTEGRITY-GATE.md`](../docs/BENCHMARK-INTEGRITY-GATE.md)  
**Agent optimization:** remains paused  
**Independence / contamination / recoverability classification:** explicitly deferred to BIG-B1/BIG-B2

## 1. Purpose and non-conclusions

BIG-B0 reconstructs what benchmark information was actually accessed, measured, exposed, reused or structurally inspected from the E3 split freeze onward. It does **not** decide whether DEV, VALIDATION or LOCKED_TEST is independent, contaminated, recoverable or unrecoverable.

The audit uses committed reports, manifests, workflows, sanitized aggregate results, repository chronology and Git metadata. It deliberately avoids reopening private benchmark contents merely to obtain stronger retrospective certainty.

Absence of a committed artifact is not treated as proof that no local/operator-only inspection occurred. Such cases are recorded as `UNKNOWN` where relevant.

Machine-readable companion ledger: [`results/big-b0-benchmark-access-ledger-2026-08-21.json`](results/big-b0-benchmark-access-ledger-2026-08-21.json).

## 2. Exposure vocabulary used by B0

B0 records factual access types without assigning an independence impact:

- `POLICY_DEFINITION` — a split role or access rule was defined.
- `PUBLIC_METADATA_INSPECTION` — public split/group/scenario metadata only.
- `CANDIDATE_EXECUTION` — an agent/runtime/model/policy candidate ran on benchmark cases.
- `PRIVATE_ORACLE_SCORING` — evaluator-side private expected-path/oracle material was loaded after outputs were fixed.
- `AGGREGATE_RESULT_OBSERVATION` — sanitized task/safety/latency/etc. metrics became visible.
- `AGGREGATE_RESULT_REUSE` — an already observed aggregate result was reused in a later diagnosis.
- `CAPTURE_METADATA_INSPECTION` — non-raw metadata from a fixed capture was inspected.
- `STRUCTURAL_PRIVATE_ORACLE_INSPECTION` — private oracle structure/alignment was inspected without exposing semantic expected values.
- `DOWNSTREAM_DECISION_RECORDED` — the report itself records a subsequent candidate, policy, or experimental direction.
- `PUBLIC_SYNTHETIC_BENCHMARK_ONLY` — experiment did not use DEV, VALIDATION or LOCKED_TEST.

Every record remains `DEFER_TO_BIG_B1` for independence/contamination classification.

## 3. Historical policy baseline — E3

E3 froze the benchmark on 2026-08-16 with ten independent asset/story groups:

| Split | Groups | Scenarios | Original purpose |
|---|---:|---:|---|
| DEV | 5 | 8 | Build/debug and early experiments |
| VALIDATION | 2 | 3 | **Select/tune candidate approaches** without touching locked test |
| LOCKED_TEST | 3 | 5 | Final withheld evaluation |

Therefore early use of VALIDATION for candidate selection was consistent with the policy that existed at that time. B0 does not retroactively substitute the later measurement-only policy for the original E3 rule.

E3 allowed pre-final LOCKED_TEST use only for public metadata/counting and leakage assertions. Candidate/model/prompt/runtime/policy optimization and evaluator-only gold inspection were forbidden.

## 4. Chronological benchmark-access inventory

| Time | Phase | Split(s) | Factual access/use | Recorded downstream consequence |
|---|---|---|---|---|
| 2026-08-16 04:17 | E3 | DEV / VALIDATION / LOCKED_TEST | Split roles and public metadata frozen | Established original policy: VALIDATION could select/tune; LOCKED_TEST final withheld |
| 2026-08-16 12:30 | E4 | VALIDATION | B0–B3 boundary candidates executed; private validation evaluator used; sanitized aggregate published | B1/B2/B3 promoted, especially B3; E5 directed |
| 2026-08-16 12:39 | E5 | DEV + VALIDATION | Evidence/stopping strategies compared | Evidence-sufficiency policy promoted and carried forward |
| 2026-08-16 14:12 | E6 | DEV + VALIDATION | LangGraph live API path executed on representative cases | LangGraph live integration path promoted as current candidate; E7 directed |
| 2026-08-16 14:27 | E7 | DEV + VALIDATION | Native vs MCP-compatible surfaces compared | Native internal default candidate + MCP interoperability candidate recorded |
| 2026-08-16 16:43 | E8 | DEV then VALIDATION | Groq `llama-3.1-8b-instant` executed; proxy/schema/latency metrics observed | Groq became current leading free-provider candidate; E9 private scorer introduced |
| 2026-08-16 18:31 | E9 | DEV + VALIDATION | Fixed outputs scored against private DEV/VALIDATION expected paths; sanitized aggregate published | Proxy-vs-real disagreement identified; subsequent improvement work redirected to DEV |
| 2026-08-16 20:31 | E10d | DEV + VALIDATION | Candidate remeasured; private scorer loaded 5 oracles; split aggregate exposed | Report recorded VALIDATION-side premature-action failure and explicitly proposed E10e targeting premature-action safety |
| 2026-08-16 21:16 | E10e | DEV + VALIDATION | Candidate remeasured; same split-level pattern observed | Report explicitly proposed E10f, a stricter general visible-output safety guard |
| 2026-08-16 22:29 | E10g | DEV + VALIDATION | Candidate remeasured; private scoring repeated | Report redirected work to a non-validation-tuned blocker analysis/general safety redesign |
| 2026-08-16 22:33 | E10h | prior DEV + VALIDATION aggregates | No new candidate run; sanitized aggregate history reused | Diagnosed self-attested action safety as insufficient and proposed E11 independent authorization using DEV/public invariants |
| 2026-08-17 00:50 | E11 | DEV + VALIDATION | Independent authorization candidate remeasured; private scoring repeated | Same split-level safety pattern recorded; next step became instrumentation/design diagnosis |
| 2026-08-17 01:05 | E12 | DEV + VALIDATION capture metadata | No new candidate; 6 DEV + 6 VALIDATION authorization rows summarized by split | Root-cause class recorded; future change mechanisms constrained |
| 2026-08-17 01:46 | E13 | DEV only | Candidate + private scorer + DEV-only blocker audit | Full DEV+VALIDATION eligibility blocked; explicit `VALIDATION calls read: 0` |
| 2026-08-18 13:55 | Public split audit | DEV / VALIDATION / LOCKED_TEST public metadata | Public overlap/coverage inspection only | Historical representative DEV gate found to cover 3/5 groups; full-DEV prerequisite added |
| 2026-08-18 13:51–13:56 | Policy amendments | all split roles | New evaluator-validity, full-DEV and measurement-only validation policy registered | Future VALIDATION requires frozen candidate + evaluator validity + full-DEV pass; LOCKED_TEST final-only |
| 2026-08-18 14:21–23:15 | Evaluator v4 validity | DEV / VALIDATION / LOCKED_TEST | Aggregate/private structural oracle shape and exact selected-ticket alignment inspected | Evaluator v4 changed from group-level oracle union to exact selected-ticket alignment |
| 2026-08-19–20 | E14 full-DEV line | DEV only | Candidate generation/private deterministic scoring/full-DEV work | E14n→E14u evidence/safety line developed while VALIDATION remained blocked |
| 2026-08-19–20 | E14v | no frozen benchmark split | Public synthetic route-planner qualification only | Three synthetic attempts consumed; no real E14v DEV/VALIDATION/LOCKED_TEST planner run authorized |
| 2026-08-21 | Benchmark Integrity Gate | no new benchmark semantics | Governance gate created | Agent optimization paused pending BIG-B0→BIG-B4 |

## 5. Split-specific factual exposure map

### DEV

Observed uses include candidate development, private scorer execution, repeated DEV-only tuning/diagnosis, representative early experiments and later full-DEV evaluation. This matches DEV's original development role. BIG-B0 makes no claim about the statistical adequacy of DEV for future selection.

Historical representative hard gates did not initially cover all DEV groups: the public 2026-08-18 audit established 3/5 group coverage (60%), 6/8 scenarios and 6/8 tickets (75%), omitting the `contextualize` modality. Later policy required all five DEV groups before future validation.

### VALIDATION

The repository records multiple distinct factual uses:

1. direct candidate comparison/selection under the original E3 policy (E4–E8);
2. evaluator-side private scoring of fixed outputs (E9);
3. repeated full DEV+VALIDATION measurement cycles (E10d, E10e, E10g, E11);
4. visibility of split-level sanitized metrics, including the repeated `premature_action_rate` pattern;
5. reuse of aggregate full-measurement information in E10h and split-specific capture metadata in E12;
6. a later policy change on 2026-08-18 making future VALIDATION measurement-only.

BIG-B0 records these uses only. Their effect on current independence is a BIG-B1 question.

### LOCKED_TEST

No committed record examined by BIG-B0 establishes a candidate/model/prompt/policy execution or task-quality scoring run on LOCKED_TEST.

However, the stronger historical phrase `LOCKED_TEST untouched` is not literally accurate across all forms of access. Factual pre-final accesses include:

- public split metadata/count/coverage inspection allowed by E3; and
- the evaluator-v4 structural private-oracle alignment diagnostic, whose sanitized aggregate reports exact-single-row alignment for `LOCKED_TEST: 3/3` alongside DEV and VALIDATION.

That diagnostic explicitly states it was structural, aggregate-only, not candidate feedback, and did not commit expected-path text, ticket/group IDs, endpoints, per-row semantic results, hashes or raw model outputs.

Whether this structural exposure affects final-test independence is **not classified in BIG-B0**.

## 6. Private-oracle / row-level visibility boundary

Several local scorer commands used `--include-rows`, and private expected paths were loaded locally after fixed outputs existed. The committed repository consistently states that raw score rows, expected paths and fixed parsed outputs were not committed.

The repository evidence does **not** prove whether an operator manually opened every local row-level scorer output before sanitization. Therefore BIG-B0 records this as:

`UNKNOWN_LOCAL_ONLY`

rather than silently converting lack of committed raw rows into proof of no human exposure.

## 7. Historical policy timeline

```text
2026-08-16 E3
DEV = development
VALIDATION = selection/tuning
LOCKED_TEST = final withheld, with public metadata/leakage checks allowed

2026-08-16 → 2026-08-17
candidate execution, private scoring and repeated measurements occur on VALIDATION under evolving local safeguards

2026-08-17
E13 explicitly returns to DEV-only and reports VALIDATION calls read = 0

2026-08-18
public coverage audit + evaluator-validity amendment + full-DEV prerequisite + measurement-only VALIDATION policy

2026-08-18
structural private-oracle alignment diagnostic spans DEV / VALIDATION / LOCKED_TEST for evaluator validity

2026-08-19 → 2026-08-20
E14 development recorded as DEV-only/full-DEV; VALIDATION blocked

2026-08-21
Benchmark Integrity Gate pauses agent optimization pending BIG-B0→BIG-B4
```

## 8. Documentation / chronology contradiction

`research/experiments/validation-measurement-only-usage-amendment.json`, dated 2026-08-18, carries the status string:

`REGISTERED_BEFORE_ANY_VALIDATION_RUN`

The committed chronology records multiple VALIDATION executions on 2026-08-16 and 2026-08-17 (E4 through E12-related work). Therefore the status string cannot be literally true if interpreted as “before any validation run in project history.”

BIG-B0 records the contradiction without inferring intent or rewriting the historical artifact. A narrower intended meaning such as “before any future validation under the amended protocol” is possible but is not asserted as historical fact.

## 9. Bounded unresolved questions

BIG-B0 cannot answer the following from committed evidence without inventing facts:

1. Which local private scorer row outputs, if any, were manually opened by the operator during E4/E9/E10/E11 runs?
2. Are there operator-local benchmark executions that were never represented by committed sanitized results/workflows?
3. Did any earlier private structural diagnostic expose split-specific semantic information not represented in sanitized reports?
4. For a few early E4–E9 substeps, would finer-than-file-timestamp ordering materially change which result preceded a particular implementation decision?

These remain explicit `UNKNOWN`s. Absence of evidence is not treated as evidence of absence.

## 10. BIG-B0 exit assessment

- [x] chronological benchmark-access inventory;
- [x] historical policy timeline;
- [x] split-specific exposure map;
- [x] candidate execution vs evaluator/private-oracle access separated;
- [x] LOCKED_TEST candidate execution distinguished from structural/private metadata inspection;
- [x] explicit documentation/chronology contradiction recorded;
- [x] unresolved exposure questions bounded rather than guessed;
- [x] machine-readable event ledger added;
- [x] no new private benchmark inspection performed for this audit;
- [x] no independence, contamination or recoverability classification made.

**BIG-B0 status: COMPLETE.**

The next active gate is **BIG-B1 — Exposure / Contamination Ledger**. BIG-B1 must classify influence, independence impact and confidence for every B0 event while preserving this factual reconstruction unchanged.
