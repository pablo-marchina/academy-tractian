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

## 18. P0 Agent Controller runtime decision — FROZEN_FOR_P0_CONTROLLER_SCOPE — 2026-08-27

Issue #15 compared the smallest credible single-agent orchestration baseline against current LangGraph, Pydantic AI and OpenAI Agents SDK capabilities while preserving the already-proven E2 execution boundary.

The selected P0 pattern is the explicit provider-free `AgentController` recorded in:

`docs/adr/004-agent-controller-runtime-2026-08-27.md`

Key invariants frozen for this scope:

- `HarnessRunner.execute_tool()` remains the exclusive real tool-execution path;
- `DecisionSource` never receives runner binding, seed or evaluator/private state;
- tool proposals and terminal `FINAL` / `CLARIFY` / `ESCALATE` / `ABSTAIN` decisions are typed and bounded;
- decision-source, tool-boundary and budget failures terminate fail-closed;
- no model/provider/runtime-orchestration SDK is required by the controller.

Validation history was preserved rather than rewritten. PR #16 first failed CI because of a published test typo, then the corrected head `0cc498342716a8ee631e305d255cfe92725494f6` passed research workflow run `33130472742` (#887). After ADR/matrix registration, final head `3dbebc0172e2f8ba8771f7d8d3968ce53a5ee525` passed run `33131374709` (#888) and was merged to `main` in `fcb88a22d287785cf10831e2a912c80f6396c863`.

This decision is scoped to the P0 controller/runtime pattern. It does not select a production model/provider, persistent-memory layer, RAG, MCP, multi-agent topology or deployment, and it does not change the C4 scientific gate.

## 19. First production Agent runtime vertical slice — MERGED / VALIDATED / READ_ONLY — 2026-08-27

Issue #17 / PR #18 created the first distinct production-path source boundary without duplicating the validated E2 execution kernel.

New production surface:

- `src/academy_tractian/runtime.py` — immutable `ProductionRequest` / `ProductionRuntimeConfig` and `ProductionRuntime` entrypoint;
- `src/academy_tractian/__init__.py` — public production package exports;
- `tests/test_runtime.py` — production runtime unit/contract regressions;
- root `pyproject.toml` — production package/test configuration;
- `.github/workflows/production-runtime.yml` — dedicated production-runtime CI;
- root `README.md` — research/production boundary and local validation path.

The runtime preserves the canonical 18-operation ToolSpec registry and routes tool execution through the accepted `AgentController` + `HarnessRunner` boundary. The first slice is intentionally provider-free and read-only: all five canonical mutating actions remain present for auditability but are deterministically denied at B2 before transport through an empty production action-permission set.

Final validated PR head:

`5c566075b83c27de7a81eb724c0d37acdf8a1023`

Dedicated production validation:

```text
workflow                 production-runtime
run                      33132279628 / #1
production runtime tests success
ADR-004 controller test  success
conclusion               success
```

All 12 workflows triggered against the final PR head completed successfully, including the existing E2–E8 regression path. PR #18 was merged with an expected-head guard into:

`b68dcabe3d2c2474c18e68aec082e77f1e74f3c8`

Boundary evidence:

```text
provider/model calls                         0
evaluator/private/gold accesses              0
semantic/FRESH_BLIND/LEGACY_LOCKED_TEST      0
score mutation/rescoring                     0
canonical ToolSpecs                         18
canonical mutating actions                    5
mutating actions reaching transport           0
production model/provider adapter       absent
integrated production evaluator         absent
production-readiness claim                false
```

The merge materially advances the Agent Runtime Plane but does not complete the requested Agent + Evaluator product. The immediate non-contaminating P0 delivery priority becomes integration of a deterministic production evaluator over the same `RunTrace`, while production action enablement and model/provider selection remain separate governed decisions. The scientific gate remains `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` and is still blocked on recovery of the exact original evaluator-side score artifact.

## 20. Deterministic production trace evaluator — MERGED / VALIDATED / INTEGRATED — 2026-08-27

Issue #20 / PR #21 closed the next structural `REQ-017` gap by integrating deterministic evaluation over the exact trace produced by the first production runtime slice.

New production evaluation surface:

- `src/academy_tractian/evaluation.py` — trace-only deterministic evaluator and integrated runtime/evaluator runner;
- `tests/test_evaluation.py` — healthy-flow, containment, tampering, failure, hashing and import-isolation regressions;
- `src/academy_tractian/__init__.py` — production evaluator exports.

The evaluator accepts only `RunTrace`, the public canonical ToolSpec registry and an explicit provider-free/read-only evaluation policy. It does not accept or import `Scenario`, expected-path/private oracle data, the historical research evaluator suite, semantic judges, model clients or provider clients.

Independent named checks cover:

- lifecycle and contiguous event-sequence validity;
- production trace/config identity;
- canonical ToolSpec proposal argument validity;
- model-control isolation for identity/seed fields;
- executed proposal → call → result → observation integrity;
- contained versus uncontained policy denials;
- zero executed mutating actions under the read-only production policy;
- absence of provider/model calls in the provider-free trace;
- terminal decision and safe-failure consistency;
- stable canonical trace hashing.

A final `TOOL_BOUNDARY_FAILURE` is treated as a valid contained failure trace even when the attempted tool call has no result/observation. This preserves failure-continuity evidence without pretending that a failed transport produced a normal result.

The evaluation report intentionally does not copy tool-result/observation bodies. It records structural issue codes, tool names, event sequences, counts and trace provenance only.

Final validated PR head:

`53e4767bffe49162cbc13847ac69164275897275`

Validation evidence:

```text
workflow                 production-runtime
run                      33132937896 / #3
production/evaluator tests success
ADR-004 controller test  success
triggered PR workflows   11 / 11 success
```

PR #21 merged into `main` as:

`fb1b959d7c2c0b185c9764d23f36746e3885dd7d`

Boundary evidence:

```text
provider/model calls                         0
evaluator/private/gold accesses              0
semantic/FRESH_BLIND/LEGACY_LOCKED_TEST      0
score mutation/rescoring                     0
runtime/evaluator same captured trace       true
production mutating actions enabled        false
production model/provider adapter          absent
semantic production evaluation             absent / unauthorized
production reliability campaign            not executed
global final architecture                  unfrozen
production-readiness claim                 false
```

This merge establishes a deterministic, integrated Agent Runtime + Evaluation plumbing baseline. It does **not** prove semantic task correctness, expected-path correctness, evidence-oracle completeness, final model/provider quality, consequential-action readiness or overall production readiness. The next delivery decision is production action safety, with all actions disabled as the null baseline; model/provider selection remains separate and provider calls remain unauthorized.

## 21. Production consequential-action safety policy — FROZEN / ACTIONS STILL DISABLED — 2026-08-27

Issue #23 / PR #24 formalized the production action-safety boundary without authorizing any mutating execution.

The implementation adds:

- `src/academy_tractian/action_safety.py` — runtime-owned authorization context, exact action fingerprinting, independent action-safety checks and deterministic policy decisions;
- updated `src/academy_tractian/runtime.py` — B2 integration of the production action policy while `actions_enabled` remains `Literal[False]` and zero action permissions are granted;
- `tests/test_action_safety.py` — coverage for all five canonical actions, every major denial family, exact confirmation/idempotency binding, duplicate protection, DecisionSource isolation and zero real action transport;
- ADR-005 — `docs/adr/005-production-action-safety-policy-2026-08-27.md`.

Initial implementation head:

`f6d3be0fb26472d18d12ba5df858ac8aa55bc60d`

Initial validation:

```text
workflow                 production-runtime
run                      33133709999 / #5
root production tests    45 / 45 PASS
ADR-004 controller tests 12 / 12 PASS
triggered PR workflows   11 / 11 success
real action transport     0
provider/model calls      0
```

After that implementation evidence passed, ADR-005 froze the P0 action-safety policy on final head:

`4e566d68ccdd2d53f8180d0d31160ebf1fb9ca90`

The final head was revalidated:

```text
workflow                 production-runtime
run                      33133897094 / #6
production tests         success
ADR-004 controller test  success
triggered PR workflows   11 / 11 success
```

PR #24 was merged with an expected-head guard into `main` as:

`f287cc350a7029df441124ece8e7c4be4ff44678`

ADR-005 freezes these independent requirements for the production action-safety protocol:

- declared permission;
- global production execution switch;
- model/runtime authorization-state isolation;
- canonical arguments and justification;
- known resource/company scope, failing closed when unknown;
- same-company scope;
- requester confirmation bound to the exact SHA-256 action fingerprint;
- runtime-owned idempotency key bound to that exact fingerprint;
- rejection of consumed/duplicate idempotency state before transport.

The policy can return `ALLOWED` only in an explicitly enabled hypothetical dry-run context where every gate passes. That capability validates the policy; it is **not** production authorization.

Canonical real-runtime state remains:

```text
ProductionRuntimeConfig.actions_enabled     false
action permissions provisioned                 0
resource/company action bindings               0
requester confirmations                        0
idempotency bindings                            0
durable idempotency store                  absent
mutating action transport calls                 0
provider/model calls                            0
scientific gate changed                     false
production readiness claimed                false
```

Actual action enablement is explicitly deferred to a separate governed decision backed by trusted real authorization/scope/confirmation state, durable idempotency semantics and retry/failure evidence. The immediate delivery priority therefore advances to the production model/provider `DecisionSource` adapter comparison, beginning provider-free; provider calls remain unauthorized.