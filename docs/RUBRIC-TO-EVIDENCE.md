# Academy × TRACTIAN — Rubric-to-Evidence Crosswalk

**Status:** ACTIVE reviewer navigation  
**Checkpoint:** 2026-09-05 corrected production rebaseline  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Runbook:** [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md)

This file is reviewer navigation, not a new source of authorization. Exact current state lives in `CURRENT-PROJECT-STATUS.md`; exact Definition of Done lives in `DELIVERY-ACCEPTANCE.md`; non-negotiable rules live in `PROJECT-PRINCIPLES.md`; historical ADRs/results remain authoritative for their original scopes.

## 1. Fast review path

1. Read `PROJECT-PRINCIPLES.md` for hard project constraints, including USD0.
2. Read `CURRENT-PROJECT-STATUS.md` for implemented/blocked/non-claimed state.
3. Read `ARCHITECTURE.md` for the promoted current architecture.
4. Read `TAPI-DELIVERY-COVERAGE-2026-09-02.md` for assignment-vs-project-rule mapping.
5. Run repository reproduction from `FINAL-HANDOFF-RUNBOOK.md`.
6. Inspect frozen evidence/ADRs for historical experiment identities.
7. Distinguish repository-level evidence from remote-production evidence.

## 2. Reviewer hard-constraint envelope

The final project selection must satisfy simultaneously:

```text
actual project cash cost = USD 0
no automatic paid spillover
remote / no local production dependency
multi-user / tenant-safe
technical quality + safety + reliability gates
```

Paid candidates are `INELIGIBLE` for final selection, even if technically strong. Free candidates are only cost-eligible; they still must pass the technical gates.

## 3. Academic excellence dimensions

| Dimension | Strongest current evidence | What it establishes | Current boundary |
|---|---|---|---|
| API integration quality | typed 18-tool registry, HTTP transport, conformance/integration tests | stable typed TRACTIAN tool boundary | no claim that every real route/provider condition is production-proved |
| Technical coherence | architecture/ADRs/PostgreSQL/actions/realtime/required CI | deterministic safety, durable logical state, safe realtime | remote USD0 hosting/IAM/HA/capacity not yet proved |
| Experiment clarity | frozen manifests/results/ADRs | preregistered hypotheses, hard gates, negative outcomes | consumed experiments cannot be replayed to seek a better result |
| Result analysis | provider-free campaigns, D01/D02, wake-up/load/recovery, EDD | quantitative failure/stability/provider/realtime analysis | human semantic/value evidence requires real participants |
| Limitations/risks | status/acceptance/runbook | provider/IAM/capacity/HA/human-data/USD0 boundaries explicit | no remote-production-readiness claim yet |
| Reproducibility | required CI, clean clone, Playwright, lockfile | repository-level product reproduction/browser acceptance | not remote provider/IAM evidence |
| Documentation | canonical docs + preserved history | one current source per question | frozen historical material is evidence, not current truth |
| Demonstration quality | React control room + Playwright + trace/evidence/lineage | real product UI/runtime/persistence/evaluation path | final presentation must use remote USD0 deployed path |

## 4. Core product evidence

| Requirement / capability | Primary current evidence | Scope note |
|---|---|---|
| Agent + Evaluation integrated | runtime/evaluation/product API/TAPI crosswalk | implemented in one product path |
| 18-operation TRACTIAN integration | typed registry + transport/conformance tests | normalized typed contract |
| Contextualize / investigate | controller/runtime scenarios/traces | grounded tool/evidence path |
| Clarify / abstain | deterministic scenario/failure/communication evidence | explicit safe outcomes |
| Escalate / handoff | escalation/communication evidence | structured handoff behavior |
| Consequential action | custody/confirmation/idempotency/lease/fencing tests | governed path; no blanket customer mutation claim |
| Tool selection / arguments | evaluator + schema/policy tests | deterministic validity where exact truth exists |
| Execution trajectory | RunTrace + UI + evaluator | inspectable process, no chain-of-thought claim |
| Evidence use | lineage + degraded evidence cases | complete/partial/conflict/unavailable behavior |
| Failure continuity | EV-007 + recovery tests | safe containment/conservative recovery |
| Stability | EV-008 + repeated-run machinery | repeated behavior evidence |
| Communication | EV-011 + terminal contracts | provider-free communication evidence |
| Realtime observability | PostgreSQL store + wake-up + SSE + frontend | durable rows/cursors are truth |
| Cross-replica read-only handoff | runtime handoff + generation fencing | repository-level distributed correctness |
| Action ownership safety | non-transferable lease + uncertainty/fencing | lost ownership → `UNCERTAIN`, no replacement replay |

## 5. Provider/model evidence

Historical D01/D02 are complete USD0 experiments.

D02 evidence establishes:

```text
actual cash cost                 USD 0.00        PASS
completed attempts               32/32           PASS
safe failure behavior            1.0             PASS
trace integrity                  1.0             PASS
M1 structured-decision gate      failed          FAIL
M4 public-task-quality gate      failed          FAIL
M7 success/stability gate        failed          FAIL
final decision                                   NO_SELECTION
```

Therefore:

- Cloudflare was **cost-eligible**;
- Cloudflare was **not technically promoted** for the tested D01/D02 candidates;
- zero cost is necessary but not sufficient;
- consumed D01/D02 packets must not be replayed;
- a materially new Cloudflare candidate can be considered only through a new preregistered USD0 experiment;
- a paid provider cannot be selected as fallback under current project rules.

Current provider state is **`NO_SELECTION`**.

## 6. Evaluation/human-data boundary

Implemented:

- deterministic structural/safety/trajectory evaluation;
- baseline/candidate EDD machinery;
- failure/stability/communication campaigns;
- semantic-review collector/rubric/protocol/source generation;
- operational-value collection + paired analysis;
- evaluator-only adaptive-stopping replay diagnostic.

Not claimable yet:

- human semantic calibration;
- judge-vs-human reliability metrics;
- real manual-vs-assisted engineer-time savings;
- business-value/auto-resolution claims.

## 7. Production-quality evidence: implemented vs missing

| Area | Current evidence | Disposition |
|---|---|---|
| USD0 provider experiments | D01/D02 at USD0 | cost eligibility proved for tested packets, provider still `NO_SELECTION` |
| PostgreSQL logical product state | integration/concurrency/recovery tests | implemented in repository |
| Tenant RLS | non-owner/non-bypass role + cross-tenant tests | implemented/tested |
| Realtime SSE/catch-up | rows/cursor + wake-up + browser tests | implemented/tested |
| Cross-replica ownership | lease/generation-fencing tests | implemented/tested algorithmically |
| Action ownership | custody/idempotency/non-transferable lease/fencing | implemented/tested algorithmically |
| Frontend lock/build/E2E | lockfile + `npm ci` + Vitest/Playwright | implemented/gated |
| Stable product CI | `final-ci-required / required-gate` | implemented; branch protection pending |
| Remote USD0 deployment | none proved yet | P0 blocker |
| USD0 standards-based IAM | signed runtime bearer only | P0 blocker |
| Branch protection | `main.protected=false` in latest read | P0 control blocker |
| Remote capacity/SLO | CI load descriptive only | P0 evidence missing |
| Backup/restore/RTO/RPO/HA | repository recovery tests only | P0 deployed evidence missing |
| Human semantic calibration | framework only | P1 human evidence missing |
| Operational value | framework only | P1 human evidence missing |
| Production provider/model | `NO_SELECTION` | P1 new hosted USD0 tournament required |

## 8. Realtime/frontend evidence

Product surfaces include Mission Control, Live Run Cockpit, Run Explorer, Timeline/Waterfall, Trace Graph, Architecture Explorer, Evidence Explorer, Output Lineage, Action Control, Tools & Policy analytics, Eval Lab, Provider Lab, Dynamic Data Explorer and Production Health.

The frontend consumes safe server-owned projections and must not receive private action custody, evaluator gold, secrets, raw sensitive provider material or chain-of-thought.

Final production acceptance adds remote build/deploy identity, USD0/quota boundary health, IAM, capacity/recovery and operational-value evidence where available.

## 9. Security/integrity evidence

Reviewer should verify server-owned identity/tenant/permissions; independent PostgreSQL RLS; evaluator/gold isolation; sensitive-field exclusion; explicit consequential-action confirmation; persistent idempotency; non-transferable action leases; `UNCERTAIN` on ambiguous ownership loss; no blind replay; safe provider/evaluator failure; and fail-closed USD0/no-paid-spillover behavior.

The signed runtime bearer is not an enterprise IAM/SSO claim.

## 10. Reproduction evidence

Current gate:

```text
final-ci-required
  ├── clean-clone-full-product-reproduction
  ├── full-product-playwright
  ├── horizontal-runtime-handoff
  └── action-execution-lease
       ↓
  required-gate
```

Local/CI reproduction is distinct from the future remote USD0 production operations path. Historical research workflows remain provenance/manual-reproduction surfaces, not ordinary product-PR gates.

## 11. Historical C4 boundary

The exact evaluator-side score-row artifact with SHA-256 `b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c` remains externally unavailable for claims requiring that exact material. Reconstruction/rescoring/substitution is forbidden.

## 12. Reviewer rule

Treat every claim only within the exact evidence scope:

- USD0 eligibility ≠ technical promotion;
- provider-free acceptance ≠ live production provider quality;
- repository cross-replica tests ≠ deployed HA/RTO/RPO;
- signed runtime identity ≠ OIDC/SSO;
- safe supplied/test action ≠ blanket customer mutation authorization;
- semantic collection machinery ≠ human calibration;
- operational-value analysis code ≠ measured business value;
- historical D01/D02 completion ≠ production provider selection;
- green CI ≠ protected branch until GitHub enforcement is active.

Negative outcomes such as `NO_SELECTION`, `NO_CHANGE`, `REJECT`, `INELIGIBLE` and `NOT READY` are valid evidence-backed results and must not be replaced by invented winners or paid fallbacks.
