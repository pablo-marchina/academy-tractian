# Academy × TRACTIAN — Project Progress Ledger

**Purpose:** chronological evidence ledger.  
**Current snapshot:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This ledger records how the project reached its current state. Frozen manifests/results remain authoritative for exact experimental semantics; failed and consumed attempts remain evidence. Current authorization belongs only in `CURRENT-PROJECT-STATUS.md`.

## 1. Benchmark integrity and protocol governance — COMPLETE

BIG-B0–BIG-B4 established benchmark access history, contamination roles and the frozen P12 protocol. Evidence roles remain `EXPOSED_POOL`, `FRESH_BLIND`, `LEGACY_LOCKED_TEST` and `SYNTHETIC_ADVERSARIAL`, with reserved-data isolation enforced.

## 2. Historical implementation reinterpretation — COMPLETE

Historical E-series evidence was reclassified under P12. Earlier passes do not automatically imply project-level `PREFERRED`. Retained foundations include ScenarioSchema, Canonical ToolSpec, TraceSchema, deterministic replay, harness/transport, tool-protocol adapters and E9/E14 evaluator/provenance/safety work.

## 3. P12-C1 — CLOSED / SCIENTIFIC FAIL

C1 completed 36 common parents and 72 fixed C0/C1 outputs. Both arms were scoreable; neither passed the frozen deterministic acceptance criteria. Canonical result: `research/results/p12-c1-deterministic-paired-result-2026-08-23.json`.

## 4. P12-C2 — CONSUMED_OPERATIONAL_FAILURE

The frozen 2×2 design was `A00=E0+S0`, `A10=E1+S0`, `A01=E0+S1`, `A11=E1+S1`. Run `32663659575` reached 31/36 parents and failed operationally. The required 144-output packet did not exist, private scoring did not run and no scientific arm conclusion is permitted.

## 5. P12-C3 — CONSUMED_TERMINAL_OPERATIONAL_FAILURE

C3 preserved the same factorial candidates and added prospective capacity control. It terminated at 3/36 cells. No 144-output packet or private scoring exists; C3 cannot be resumed, rerun or reinterpreted as complete-case evidence. Canonical closure: `research/results/p12-c3-live-cycle-closure-2026-08-23.json`.

## 6. P12-C4 provider-route qualification history

Cerebras and OpenRouter/OpenInference qualification attempts ended as consumed operational failures before benchmark model output. NVIDIA hosted NIM later passed the separate qualification path. This qualified a C4 execution route only; it did not select a production provider.

The one-shot NVIDIA C4 collection completed in workflow run `33020748838`, job `98350245931`, with 36/36 fresh common parents, 0 HTTP failures, 0 automatic retries, 0 warmups and 0 provider/model fallbacks.

## 7. P12-C4 local factorial expansion — COMPLETE

After three transparent pre-transform infrastructure failures that produced zero arm outputs and zero provider calls, the valid provider-free expansion completed in run `33028989704`, job `98376848407`:

```text
parents            36
fixed outputs     144 / 144
A00/A10/A01/A11    36 each
provider calls       0
validation errors    0
```

## 8. Complete C4 packet freeze — COMPLETE

`research/results/p12-c4-complete-packet-freeze-2026-08-26.json` froze `FROZEN_COMPLETE_C4_PACKET`: 36/36 common parents, 144/144 local factorial outputs, no partial packet, no private scoring/bootstrap at that point and no further provider calls authorized.

## 9. Repository governance and documentation split — COMPLETE

Repository maintenance established:

- `CURRENT-PROJECT-STATUS.md` as the sole current human-readable status/authorization source;
- `NEXT-STEPS.md` as the short-horizon execution plan;
- `ARCHITECTURE-ROADMAP.md` as the research-to-production architecture roadmap;
- `PROJECT-PLAN.md` as the macro phase map;
- `REPOSITORY-GUIDE.md`, `CONTRIBUTING.md`, issue/PR templates and explicit Class A/B/C change governance.

Frozen/failed experiment evidence and stable paths were preserved rather than cleaned away.

## 10. Main requirements/source reconciliation — COMPLETE

PR #2 merged the research/governance foundation into `main` via `9b5a6671176a1635676556ff1b48b4044b897a76`. The TAPI, delivered TRACTIAN package and kickoff were audited together in `research/tractian-source-baseline-2026-08-27.md`.

The project North Star became: maximize the strongest defensible actual TRACTIAN × Inteli delivery under P1–P4. `DELIVERY-ACCEPTANCE.md` now maps required agent capability and trustworthy evaluation evidence to the academic/project acceptance criteria.

## 11. P12-C4 deterministic private scoring — FROZEN — 2026-08-27

Task #3 isolated deterministic scoring. Evaluator-side oracle provenance was resolved from historical package evidence, not reconstructed. The scorer materialized only the exact 12-row EXPOSED_POOL ticket subset evaluator-side; the subset and full private oracle were not committed.

The scoring-only gate produced 144/144 scoreable deterministic rows with 0 provider/model calls and no bootstrap/LOGO/slices/semantic/blind execution. Independent validation recomputed all 144 rows with **0 mismatches**.

Canonical closure: `research/results/p12-c4-deterministic-scoring-freeze-2026-08-27.json`, status `FROZEN_C4_DETERMINISTIC_SCORING`.

Exact uncommitted evaluator-side score-row artifact:

`sha256:b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`

## 12. P12-C4 group-cluster bootstrap 20k — FROZEN — 2026-08-27

Task #5 consumed only the exact frozen deterministic rows. The bootstrap-only runner reproduced the historical C2 nested aggregation and paired factorial semantics:

```text
resamples          20,000
seed               20260822
confidence         95%
resampling unit    asset_story_group
groups             7
```

Exact evaluator-side bootstrap result:

`sha256:08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526`

Independent validation found 0 mismatch sections. Source verification passed in Actions run `33077803636`, artifact `9648626660`, digest `sha256:88580339838aec30ac38111717b82c6b2ef83d57bd84c287cecc03f89b07fccd`.

Measured effects included E1 lower extra reads but negative point estimates for recall/evidence/quality, with the reported 95% intervals including zero; S1 was zero on all frozen report metrics. No survivor decision was made.

Canonical closure: `research/results/p12-c4-bootstrap-20000-freeze-2026-08-27.json`, status `FROZEN_C4_BOOTSTRAP_20000`.

PR #6 merged the closure into `main` via `14a175d3797bb117a223dc4bf6bf75257e6fa4a0`; issue #5 closed as completed.

## 13. P12-C4 leave-one-group-out sensitivity — FROZEN — 2026-08-27

Task #7 opened `LEAVE_ONE_GROUP_OUT_SENSITIVITY` on `eval/c4-logo-sensitivity` from the post-bootstrap `main` commit. The execution reused the exact frozen score rows and exact frozen bootstrap result; it did not load private oracle content or alter scores.

Exact LOGO semantics reproduce the historical C2 `logo_effects(...)`: omit one whole `asset_story_group` and average the paired group effects over the six retained groups. Seven groups were evaluated:

`asset_B204`, `asset_C710`, `asset_G501`, `asset_M101`, `asset_M102`, `asset_M208`, `asset_S420`.

Source verification passed in GitHub Actions run `33079763796`; artifact `9649478087`; digest `sha256:c4535c3b91c5a7af97a9eea9bafaa1f462963958c308cc92ad201462b2a85a59`.

Exact evaluator-side LOGO result:

`sha256:bc62cc45b4e3344861a152825096a8a1b28f41f2d831f86fd81de35964363f8c`

Independent validation:

`PASS_INDEPENDENT_LOGO_RECOMPUTATION`, 0 mismatch sections, validation SHA-256 `cb6ccce3cbdbffe61a01ade8e121d977b6f6ca7d9552684a311cf1ba59d8d3cb`.

Robustness observations:

- E1 expected-read recall remains negative under all seven omissions;
- E1 extra-public-read count remains negative under all seven omissions;
- E1 evidence correctness and task/reference quality are not sign-robust and become positive when `asset_M102` is omitted;
- S1 remains exactly zero on every preregistered primary safety contrast under every omission;
- A11 follows the E1 pattern on evidence metrics and stays zero on decision/action/escalation/safety contrast metrics.

Privacy/boundary checks: 0 provider/model calls, private oracle not loaded, scores unchanged, 0 slice/semantic/FRESH_BLIND/LEGACY_LOCKED_TEST execution and no survivor/PREFERRED decision.

Canonical closure: `research/results/p12-c4-logo-sensitivity-freeze-2026-08-27.json`, status `FROZEN_C4_LEAVE_ONE_GROUP_OUT_SENSITIVITY`.

The closure opens only the staged `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` gate covering still-unexecuted preregistered reporting requirements: all per-group outcomes, `investigate`/`execute`/`contextualize` modality slices, safety/failure-family slices, and operational failure counts/denominators. Survivor selection, semantic evaluation and blind partitions remain blocked.
