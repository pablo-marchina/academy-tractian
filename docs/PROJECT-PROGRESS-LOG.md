# Academy × TRACTIAN — Project Progress Ledger

**Purpose:** chronological evidence ledger.  
**Current snapshot:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file explains how the project reached its current state. It does not override frozen experiment manifests, protocols or canonical result artifacts. Failed and consumed attempts remain evidence. It intentionally contains no mutable "current checkpoint" section; current state belongs in `CURRENT-PROJECT-STATUS.md`.

## 1. Benchmark integrity and protocol governance — COMPLETE

BIG-B0–BIG-B4 established benchmark access history, contamination/evidence roles, benchmark-design comparisons and the frozen P12 protocol.

Frozen evidence roles include:

- `EXPOSED_POOL` — adaptive development/comparison;
- `FRESH_BLIND` — independent real-domain evidence;
- `LEGACY_LOCKED_TEST` — supplementary held-out characterization;
- `SYNTHETIC_ADVERSARIAL` — robustness/evaluator qualification.

Canonical foundations include `research/big-b0-benchmark-integrity-audit-2026-08-21.md`, the benchmark access ledger and frozen P12 protocol artifacts.

## 2. Historical implementation reinterpretation — COMPLETE

Historical E-series implementation evidence was reclassified under P12. No historical implementation became automatically project-level `PREFERRED` merely because it had previously passed a narrower gate.

Evidence-backed foundations retained for later comparison include ScenarioSchema, Canonical ToolSpec, TraceSchema, deterministic replay, HarnessRunner/HttpxTransport, runtime/orchestration candidates, tool-protocol adapters and E9/E14 evaluator/provenance/safety foundations.

## 3. P12-C1 — CLOSED / SCIENTIFIC FAIL

C1 completed 36 common parents and 72 fixed C0/C1 outputs. Both arms were scoreable, but neither passed the frozen deterministic acceptance criteria.

```text
QUALIFIED arms   none
PREFERRED arm    none
```

Canonical result: `research/results/p12-c1-deterministic-paired-result-2026-08-23.json`.

## 4. P12-C2 — CONSUMED_OPERATIONAL_FAILURE

Frozen 2×2 design:

```text
A00 = E0 + S0
A10 = E1 + S0
A01 = E0 + S1
A11 = E1 + S1
```

Run `32663659575` completed 31/36 parents and failed five under the recorded rate-limit family. The required 144-output packet was not created and private scoring did not run. No arm-level scientific conclusion is permitted and the attempt remains consumed evidence.

## 5. P12-C3 — CONSUMED_TERMINAL_OPERATIONAL_FAILURE

C3 retained the same factorial candidates and added prospective capacity control. After an infrastructure-only amendment, the live continuation reached only 3/36 completed cells before the preregistered terminal operational state.

```text
completed cells       3
pending cells        33
36/36 freeze       false
144-output packet  absent
private scoring    not executed
```

Canonical closure: `research/results/p12-c3-live-cycle-closure-2026-08-23.json`. C3 cannot be resumed, rerun, partially scored or reinterpreted as complete-case evidence.

## 6. P12-C4 serving-route qualification history

### 6.1 Cerebras — CONSUMED_OPERATIONAL_FAILURE_NO_MODEL_OUTPUT

ADR-001 selected the Cerebras route only for C4 qualification. Numeric capacity/catalog checks passed, but the one-shot synthetic workflow failed on the first provider request with HTTP 402 `payment_required`. No model output or benchmark input was produced. The authorization remains consumed.

Canonical closure: `research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json`.

### 6.2 OpenRouter + OpenInference — CONSUMED_OPERATIONAL_FAILURE_NO_MODEL_OUTPUT

ADR-002 prospectively selected a no-card route. Provider-free qualification passed, but the one-shot live synthetic request failed with HTTP 404 because the frozen free model variant was unavailable. No model output or benchmark input was produced. The authorization remains consumed.

Canonical closure: `research/results/p12-c4-openrouter-synthetic-live-probe-closure-2026-08-26.json`.

### 6.3 NVIDIA NIM — qualification route that enabled C4

ADR-003 selected NVIDIA hosted NIM only as a new C4 provider-qualification candidate, not as a final production-provider decision.

The frozen synthetic compatibility path subsequently passed, the provider-free activation/capacity gate passed, and a separate one-shot live C4 authorization was frozen.

The one-shot NVIDIA live collection then completed:

```text
workflow run       33020748838
job                98350245931
fresh parents      36 / 36
HTTP failures      0
automatic retries  0
warming requests   0
provider fallback  0
model fallback     0
```

The resulting common-parent evidence was independently validated and authorized local factorial expansion only.

## 7. P12-C4 local factorial expansion — COMPLETE

The provider-free local expansion consumed the exact 36 frozen common parents and the frozen C2/C3 factorial semantics.

After three transparent pre-transform infrastructure failures that produced zero arm outputs and zero provider calls, the runtime-only fixes were completed without changing candidate semantics. The valid run was:

```text
workflow run       33028989704
job                98376848407
parents            36
fixed outputs      144 / 144
A00                 36
A10                 36
A01                 36
A11                 36
provider calls       0
validation errors    0
```

The pre-transform infrastructure failures remain retained as operational evidence and are not counted as scientific candidate outputs.

## 8. Complete C4 packet freeze — COMPLETE

On 2026-08-26 the repository froze:

`research/results/p12-c4-complete-packet-freeze-2026-08-26.json`

Status at closure:

```text
FROZEN_COMPLETE_C4_PACKET
fresh common parents           36 / 36
local factorial outputs       144 / 144
partial packet                    false
private scoring executed           false
bootstrap executed                  false
provider calls authorized after      0
next gate          DETERMINISTIC_SCORING
```

This superseded earlier project-status checkpoints that still described C4 as provider-blocked; those older snapshots remain historical evidence of the state at their timestamps.

## 9. Repository governance/organization refresh — 2026-08-26

A repository audit found stale status duplication across `README.md`, `CURRENT-PROJECT-STATUS.md`, `PROJECT-PLAN.md`, `PROJECT-PROGRESS-LOG.md` and research indexes after the successful C4 transition.

The first cleanup pass:

- restored `CURRENT-PROJECT-STATUS.md` as the detailed current human status source;
- rewrote `PROJECT-PLAN.md` around the four non-negotiable project principles;
- added `REPOSITORY-GUIDE.md` with source-of-truth and safe-cleanup rules;
- retained all frozen/consumed/failed experiment evidence and stable paths;
- added a time-specific machine checkpoint rather than overwriting an earlier snapshot.

## 10. Documentation responsibility split and scoring-gate isolation — 2026-08-26

A second repository-wide review found that mutable state was still duplicated in root/research/script/workflow/results README files and that `PROJECT-PLAN.md` mixed current execution, macro project phases and architecture direction.

The repository was updated to:

- make `CURRENT-PROJECT-STATUS.md` the sole human-readable current-state/authorization source;
- add `NEXT-STEPS.md` as the canonical short-horizon execution plan;
- add `ARCHITECTURE-ROADMAP.md` as the canonical general research-to-production/system architecture roadmap;
- reduce `PROJECT-PLAN.md` to the macro phase/milestone map;
- remove mutable current-gate snapshots from root/research/script/workflow/results indexes;
- formalize five manual repository maintenance gates in `REPOSITORY-GUIDE.md` without adding governance CI;
- add `scripts/research/p12_c4_deterministic_private_scoring.py` as a gate-isolated deterministic-scoring runner.

The new C4 scorer was prepared only at that point. No private oracle was provisioned and no deterministic C4 score was executed as part of repository maintenance.

## 11. Main reconciliation and requirements-to-delivery review — 2026-08-27

PR #2 was marked ready and merged into `main` with merge commit:

`9b5a6671176a1635676556ff1b48b4044b897a76`

The merge reconciled the research/governance foundation into the canonical branch while preserving frozen/consumed provenance. It did not itself advance the scientific gate.

A post-merge review strengthened final-delivery planning by:

- adding `DELIVERY-ACCEPTANCE.md` as the requirement → final capability → evidence crosswalk;
- making both agent construction and the evaluation framework explicit P0 deliverables;
- protecting contextualize, investigate, execute, clarify/abstain, escalate, robustness and inspectable-trace coverage;
- requiring real API integration and per-run evaluation in the final demonstration;
- classifying work as P0 required, P1 material production or P2 conditional enhancement;
- forbidding P2 complexity from displacing P0/P1 acceptance work;
- revising `ARCHITECTURE-ROADMAP.md` into coupled Agent Runtime and Evaluation & Reliability planes separated by the gold/private boundary.

## 12. Audited TAPI + delivered-package + kickoff reconciliation — 2026-08-27

The actual project inputs were re-reviewed together:

- `[UPDATED] Tapi Inteli  Tractian.pdf`;
- `inteli-tractian-project.zip`;
- `tractian-kickoff.md`.

The exact reviewed files/hashes and package discrepancies were frozen in `research/tractian-source-baseline-2026-08-27.md`.

Observed package facts include 17 agent-visible cases, 17 expected-path evaluation rows, 16 narrative scenarios and the then-observed 17-operation lossy OpenAPI parse. A later duplicate-aware conformance audit (section 17) corrected the API interpretation to 18 authored operations across 17 unique path templates without rewriting the upstream source. The audit also records that narrative package documentation contains small mismatches with the actual delivered files/contract; executable package behavior is used where appropriate without rewriting upstream evidence.

This reconciliation established a fixed repository North Star:

> maximize the quality of the **actual requested TRACTIAN × Inteli delivery** using P1–P4, rather than maximizing research volume or architecture complexity.

The repository was updated to:

- embed the North Star and upstream source hierarchy in `PROJECT-PRINCIPLES.md`;
- reconcile `research/01-requirements-matrix.md` against the actual package and kickoff;
- strengthen `DELIVERY-ACCEPTANCE.md` around the eight official academic criteria;
- encode partner-quality targets: operational conclusion over exact wording, inspectable process, safe human fallback, useful escalation handoff, customer-safe communication and stable tool contract;
- separate official benchmark action semantics from a possible real-product requester-confirmation policy;
- update model/provider strategy so a strong quality frontier is evaluated before premature cost-only optimization;
- revise `ARCHITECTURE-ROADMAP.md` and `PROJECT-PLAN.md` around the integrated agent + evaluator product actually requested;
- add a Source/Brief Reconciliation Gate to `REPOSITORY-GUIDE.md`;
- protect the final calendar window from speculative P2 complexity.

This was a requirements/governance/planning reconciliation only. It did not execute deterministic scoring, authorize new provider calls, access FRESH_BLIND/LEGACY_LOCKED_TEST or freeze a final architecture.

## 13. Development operating contract and review gates — 2026-08-27

A lightweight development-governance layer was added without introducing governance CI:

- `CONTRIBUTING.md` defines the development operating contract;
- changes are classified A documentation-only, B non-semantic engineering or C material semantic/experimental/product work;
- material work must map to P0/P1 acceptance, an official rubric criterion, a material delivery risk or a required comparison;
- `.github/ISSUE_TEMPLATE/development-task.md` and `.github/pull_request_template.md` require gate, evidence, custody and canonical-document checks;
- Class C work requires a focused branch + planning record + governed PR.

The intended normal loop became:

```text
current main + canonical docs
→ requirement/rubric/risk mapping
→ gate/authorization check
→ change classification
→ evidence/baseline plan
→ focused implementation
→ regression/evaluation
→ PR governance checklist
→ merge to main
→ canonical reconciliation
```

## 14. P12-C4 deterministic private scoring — FROZEN — 2026-08-27

Task #3 opened the scoring work as a P0/Class C gate-isolated task on `eval/c4-deterministic-scoring`.

The evaluator-side oracle provenance was resolved from existing repository history rather than reconstructed from public fixtures:

- historical commit `38adcfa0ca81fec7b1e5a9fe1097441ae5208741` identifies the TRACTIAN package `eval/expected-paths.json` as the evaluator-side oracle source;
- audited external bundle SHA-256: `37546f7abad4c573ab36384a171161f3ba6c7258024341cc42f0881d9606d134`;
- oracle source SHA-256: `d6fb6186e4c035effe7dafa44758eaf40948ac334f0a91f8634a5731b7e0cb38`.

To harden custody, the scorer did not load the full 17-row private file. A temporary evaluator-side 12-row EXPOSED_POOL subset was derived solely by exact public ticket IDs from the frozen C4 packet. The derived subset was not committed and has SHA-256 `fcb7bb6a9b722d2f07e483407934d46d5402a372eb56f9a41cb6549e81e1b768`.

The handoff was frozen in:

`research/frozen/p12-c4-deterministic-private-scoring-handoff-v1.json`

The exact source stack was exported provider-free by workflow run `33075507040`, artifact `9647662051`, digest `sha256:ee82917efa37859486b718ccb0617bb18ebe12bf740fa77be5ea40c411679284`.

Preflight result:

```text
fixed outputs verified          144
unique exposed tickets           12
exact unique alignments          12
normalization failures            0
scores computed                   0
provider credentials              0
fresh blind accesses              0
legacy locked accesses            0
```

The authorized deterministic scorer then produced:

```text
status                PASS_144_OF_144_DETERMINISTIC_SCORES
scoreable outputs                                  144 / 144
provider calls                                           0
model calls                                              0
bootstrap executed                                    false
LOGO executed                                         false
slice analysis executed                               false
semantic stage executed                               false
FRESH_BLIND accesses                                      0
LEGACY_LOCKED_TEST accesses                               0
```

The full evaluator-side row artifact remains uncommitted and is frozen by SHA-256:

`b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`

Independent validation recomputed all 144 rows using the exact pinned scorer stack and found **0 score mismatches**. A privacy audit found 0 exact private expected-step strings and 0 complete private oracle rows serialized in the scoring result.

Canonical closure:

`research/results/p12-c4-deterministic-scoring-freeze-2026-08-27.json`

Status:

`FROZEN_C4_DETERMINISTIC_SCORING`

This closure does **not** assert any arm-level aggregate gate result, factorial effect, confidence interval, semantic eligibility, PREFERRED state, independent generalization or production readiness.

It opens only the preregistered next gate:

```text
BOOTSTRAP_20000
resamples        20,000
seed             20260822
confidence       95%
resampling unit  asset_story_group
```

LOGO, slices, semantic evaluation, FRESH_BLIND, LEGACY_LOCKED_TEST, new provider calls and candidate regeneration remain unauthorized.

## 15. P12-C4 group-cluster bootstrap 20k — FROZEN — 2026-08-27

Task #5 isolated the statistical uncertainty gate on `eval/c4-bootstrap-20000`. The gate consumed only the exact frozen deterministic score-row artifact and never loaded the private oracle.

Frozen inputs and protocol:

```text
deterministic score rows SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
rows                              144
parents                            36
arms                                4
groups                              7
resamples                       20,000
seed                         20260822
confidence                         95%
resampling unit      asset_story_group
```

The bootstrap-only runner reproduced the historical C2 nested aggregation and paired-factorial comparison semantics without executing LOGO, slices or semantic evaluation. The full evaluator-side bootstrap artifact remains uncommitted and is frozen by SHA-256:

`08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526`

A separate validator recomputed the aggregate arm metrics, primary paired contrasts and factorial main effects/interactions using the frozen historical C2 statistical helpers and found **0 mismatch sections**. The exact branch source stack also passed provider-free compile/source verification in GitHub Actions run `33077803636`; artifact `9648626660`; digest `sha256:88580339838aec30ac38111717b82c6b2ef83d57bd84c287cecc03f89b07fccd`.

Measured C4 bootstrap evidence includes:

- `A10 − A00` evidence correctness effect `-0.047619`, CI95 `[-0.285714, 0.142857]`;
- `A10 − A00` expected-read recall effect `-0.079371`, CI95 `[-0.238105, 0.039875]`;
- `A10 − A00` extra-public-read effect `-0.261905`, CI95 `[-0.714286, 0.142857]`;
- `A10 − A00` task/reference quality effect `-0.006805`, CI95 `[-0.040829, 0.020414]`;
- all preregistered `A01 − A00` primary effects are exactly zero;
- the frozen safety main effect is zero on all report metrics;
- preregistered interaction metrics are zero.

All reported E1 confidence intervals above include zero. These measurements do not constitute a survivor/PREFERRED decision. All four frozen arm aggregates also retain nonzero confirmed hard-safety violations; formal candidate selection remains deferred until the required robustness/reporting gates close.

Privacy/boundary validation:

```text
provider calls                     0
model calls                        0
private oracle loaded          false
score recomputation/change     false
LOGO executed                  false
slice analysis executed        false
semantic stage executed        false
FRESH_BLIND accesses               0
LEGACY_LOCKED_TEST accesses        0
```

Canonical closure:

`research/results/p12-c4-bootstrap-20000-freeze-2026-08-27.json`

Status:

`FROZEN_C4_BOOTSTRAP_20000`

The closure opens only:

`LEAVE_ONE_GROUP_OUT_SENSITIVITY`

Slices, semantic evaluation, FRESH_BLIND, LEGACY_LOCKED_TEST, candidate regeneration, survivor/PREFERRED decision, final architecture freeze and production-readiness claims remain unauthorized until explicitly opened by a later frozen gate.

## 16. P12-C4 leave-one-group-out sensitivity — FROZEN — 2026-08-27

Task #7 opened `LEAVE_ONE_GROUP_OUT_SENSITIVITY` on `eval/c4-logo-sensitivity` from the post-bootstrap `main` commit. The execution reused the exact frozen score rows and exact frozen bootstrap result; it did not load private oracle content or alter scores.

Exact LOGO semantics reproduce the historical C2 `logo_effects(...)`: omit one whole `asset_story_group` and average the paired group effects over the six retained groups. Seven groups were evaluated:

`asset_B204`, `asset_C710`, `asset_G501`, `asset_M101`, `asset_M102`, `asset_M208`, `asset_S420`.

Source verification passed in GitHub Actions run `33079763796`; artifact `9649478087`; digest `sha256:c4535c3b91c5a7af97a9eea9bafaa1f462963958c308cc92ad201462b2a85a59`.

Exact evaluator-side LOGO result:

`sha256:bc62cc45b4e3344861a152825096a8a1b28f41f2d831f86fd81de35964363f8c`

Independent validation returned `PASS_INDEPENDENT_LOGO_RECOMPUTATION`, with 0 mismatch sections and validation SHA-256 `cb6ccce3cbdbffe61a01ade8e121d977b6f6ca7d9552684a311cf1ba59d8d3cb`.

Robustness observations:

- E1 expected-read recall remains negative under all seven omissions;
- E1 extra-public-read count remains negative under all seven omissions;
- E1 evidence correctness and task/reference quality are not sign-robust and become positive when `asset_M102` is omitted;
- S1 remains exactly zero on every preregistered primary safety contrast under every omission;
- A11 follows the E1 pattern on evidence metrics and stays zero on decision/action/escalation/safety contrast metrics.

Privacy/boundary checks: 0 provider/model calls, private oracle not loaded, scores unchanged, 0 slice/semantic/FRESH_BLIND/LEGACY_LOCKED_TEST execution and no survivor/PREFERRED decision.

Canonical closure:

`research/results/p12-c4-logo-sensitivity-freeze-2026-08-27.json`

Status:

`FROZEN_C4_LEAVE_ONE_GROUP_OUT_SENSITIVITY`

The closure opens only the staged `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` gate covering still-unexecuted preregistered reporting requirements: all per-group outcomes, `investigate`/`execute`/`contextualize` modality slices, safety/failure-family slices, and operational failure counts/denominators. Survivor selection, semantic evaluation and blind partitions remain blocked.

## 17. Duplicate-aware TRACTIAN API contract conformance — COMPLETE — 2026-08-27

Task #11 re-audited the exact delivered agent-facing API source because the canonical baseline had interpreted the OpenAPI as 17 operations / 17 paths while the historical Tool Registry contained 18 tools.

The exact source identities were re-verified without committing raw partner material:

```text
package ZIP SHA-256       37546f7abad4c573ab36384a171161f3ba6c7258024341cc42f0881d9606d134
OpenAPI SHA-256           8b3fdc5da50a8fa2923928a2f5aebcfe5034c622dba222df84f56abcd0b4aabf
api/app/main.py SHA-256   a9bdfb8a5fc85e8f169438984f787ad5fd0db95cdd2dc41a15e05ca363a3ca78
api/tests/test_api.py     b50fbabe2f497290a01984ba0663bb0b787184f0bc1b367e90871d0912326443
```

A duplicate-aware audit found that `agent-input/api-contract.openapi.yaml` authors the YAML mapping key `/assets/{assetId}` twice:

- first occurrence: `GET` / `getAsset`;
- second occurrence: `PATCH` / `updateAssetConfig`.

Ordinary YAML mapping loaders can overwrite the first occurrence and incorrectly expose only 17 operations. The source-authored contract actually contains **18 operations across 17 unique path templates**.

The correction was validated against two independent operational sources:

- executable FastAPI implementation: 18 matching method/path routes;
- delivered API tests: explicit `GET /assets/asset_M101` success and 404 coverage.

The canonical `research/e2/tool_registry.py` already represented both operations. Its invariants were hardened to require 18 unique method/path signatures, 18 operation IDs, 17 unique path templates and the exact GET/PATCH duplicate-path pair.

Sanitized conformance result:

`research/results/tractian-api-contract-conformance-2026-08-27.json`

Status:

`PASS_NORMALIZED_18_OPERATIONS_17_UNIQUE_PATHS`

Conformance result:

```text
authored OpenAPI ↔ Tool Registry        exact match
OpenAPI routes ↔ FastAPI implementation exact match
Tool Registry ↔ FastAPI implementation  exact match
mismatch sections                       0
raw partner source committed            false
evaluation/gold material accessed        false
provider/model calls                     0
C4 scientific state changed              false
```

`research/tractian-source-baseline-2026-08-27.md` and `research/01-requirements-matrix.md` were reconciled to preserve the upstream duplicate-key defect as evidence while using duplicate-aware normalization for the canonical Tool Contract. This work changes source interpretation only; it does not mutate frozen C4 artifacts, scores, candidates, authorization or the current `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` gate.
