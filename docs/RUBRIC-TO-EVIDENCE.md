# Academy × TRACTIAN — Rubric-to-Evidence Crosswalk

This is reviewer navigation, not a new source of authorization. Exact current state remains in `CURRENT-PROJECT-STATUS.md`; exact acceptance semantics remain in `DELIVERY-ACCEPTANCE.md`; frozen artifacts/ADRs remain authoritative for their scoped results.

## Fast review path

1. Read [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md) for what is frozen, blocked, gated and forbidden.
2. Run the sequence in [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md).
3. Inspect [`../research/results/final-delivery-evidence-index-2026-08-28.json`](../research/results/final-delivery-evidence-index-2026-08-28.json) for exact evidence identities.
4. Inspect [`../research/results/provider-free-final-delivery-demo-result-2026-08-28.json`](../research/results/provider-free-final-delivery-demo-result-2026-08-28.json) for the five integrated demo traces/results.
5. Use the final machine audit (`../research/results/final-handoff-acceptance-audit-2026-08-28.json`) for all 83 preregistered acceptance dispositions.

## Official academic excellence dimensions

| Dimension | Strongest evidence | What it establishes | Boundary |
|---|---|---|---|
| API integration quality | `research/results/tractian-api-contract-conformance-2026-08-27.json`; `research/e2/tool_registry.py`; `tests/test_runtime.py` | authored OpenAPI, registry and executable implementation agree on 18 normalized operations; strict tool boundary, identity/seed binding and negative action tests | only the production-path `get_asset` route is explicitly recorded as route-tested in the conformance artifact; do not claim live exercise of all 18 operations |
| Technical coherence | ADR-004…ADR-016; `docs/ARCHITECTURE-ROADMAP.md`; `docs/PROJECT-PRINCIPLES.md` | controller/runtime/evaluator/action/provider boundaries were decided prospectively and kept separate; optional complexity is gated by evidence | global final architecture is not frozen |
| Experiment clarity | `research/experiments/`; `docs/BENCHMARK-INTEGRITY-GATE.md`; ADR-013/014/015/016 | preregistered geometry, denominators, falsifications, fixed metrics and change rules | historical exposed data is not independent generalization evidence |
| Result analysis quality | frozen P12-C4 deterministic/bootstrap/LOGO artifacts; EV-007/008/011 results; ADR-016 demo | deterministic scoring, uncertainty/sensitivity, failure slices, repeated-run stability and communication safety are preserved with exact identities | C4 per-group/slice continuation is blocked on the exact unavailable score-row artifact |
| Limitations / risks | `docs/CURRENT-PROJECT-STATUS.md`; `docs/BENCHMARK-INTEGRITY-GATE.md`; `docs/FINAL-HANDOFF-RUNBOOK.md` | provider, blind-evaluation, action, replay, privacy and C4 limits are explicit and fail closed | no provider selection, fresh-blind generalization or production-readiness claim |
| Reproducibility | ADR-016; `.github/workflows/final-delivery-provider-free-reproduction.yml`; `scripts/validate_delivery_reproduction.py`; final handoff validator | clean checkout can install, regress frozen campaigns, rerun the integrated demo and resolve exact evidence | provider-free scope only |
| Documentation | root `README.md`; `docs/REPOSITORY-GUIDE.md`; this crosswalk; final runbook; delivery acceptance matrix | reviewer can navigate source of truth, setup, evidence, operations and non-claims | documentation cannot substitute for externally unavailable evidence |
| Demonstration quality | `research/results/provider-free-final-delivery-demo-result-2026-08-28.json`; EV-007/008/011 | real runtime/evaluator traces cover investigate, clarify, abstain, escalate and one governed supplied/test action, plus failure/reliability/communication campaigns | synthetic/provider-free demonstration; zero real-customer mutations |

## P0 project acceptance

| Requirement | Primary evidence |
|---|---|
| REQ-001 individual project | repository history, source tree and final handoff package |
| REQ-003 technical experiment | BIG-B2/B3/B4 protocol work; frozen P12-C4 analysis; EV-007/008/011 campaigns |
| REQ-004 / REQ-020 document results | root README; ADRs; progress/frozen result artifacts; this crosswalk |
| REQ-021 reproducible handoff | ADR-016 workflow/validator plus `FINAL-HANDOFF-RUNBOOK.md` |
| REQ-017 agent + evaluation framework | `src/academy_tractian/runtime.py`, `src/academy_tractian/evaluation.py`, E2 runner/controller and ADR-016 integrated demo |

## Agent/evaluator capability evidence

| Capability | Strongest evidence | Scope note |
|---|---|---|
| Industrial API / tool contract | `research/results/tractian-api-contract-conformance-2026-08-27.json`; `research/e2/tool_registry.py` | 18 normalized operations; one stable typed agent-facing registry |
| Investigate/read | DEMO-01; runtime/controller tests | supplied/local `get_asset` evidence path |
| Clarify / abstain | DEMO-02/03; EV-011 | deterministic missing-context/no-safe-path behavior |
| Escalate | DEMO-04; EV-011 COMM-09/other escalation cases | provider-free handoff behavior |
| Consequential action | DEMO-05; ADR-012; controlled action tests | supplied/test authorized action only; default ProductionRuntime remains disabled |
| Failure continuity | EV-007; runtime fault tests | deterministic faults, safe containment, no hidden retry |
| Stability | EV-008 | 30/30 runs; 66/66 stability dimensions |
| Customer-safe communication | EV-011 | 60/60 applicable predicates; COMM-07 remains evaluator FAIL by design |
| Per-run evaluator / trace | `src/academy_tractian/evaluation.py`; `research/e2/models.py`; ADR-016 demo | same trace object is evaluated without runtime access to private gold |
| Evaluation integrity | `docs/BENCHMARK-INTEGRITY-GATE.md`; BIG-B0…B4 artifacts | contamination/exposure roles and blind-access rules are frozen; fresh blind remains unavailable |

## P1 production/quality evidence

| Area | Evidence | Disposition boundary |
|---|---|---|
| Contracts | API conformance result + registry + runtime tests | evidenced provider-free contract; not all routes live-exercised |
| Authorization | ADR-005, ADR-012, action safety tests | deterministic local/supplied boundary; no blanket customer authorization |
| Consequential actions | ADR-012 + DEMO-05 + idempotency tests | exactly controlled action profile; uncertain post-claim attempts are non-replayable |
| Failure continuity | EV-007 + EV-011 + runtime transport-failure tests | safe fallback/handoff in deterministic/provider-free campaign |
| Escalation handoff | DEMO-04 + EV-011 | provider-free evidence |
| Customer communication | EV-011 | provider-free evidence; no subjective claim beyond frozen predicates |
| State/context | controller/runtime trace models | explicit per-request trace lifecycle; no persistent memory claimed |
| Configuration | `pyproject.toml`, `research/e2/pyproject.toml`, frozen config/result hashes | Python/dependency constraints and deterministic identities; no deployment platform lock |
| Secrets/privacy | provider authorization tests, EV-007/011 sentinels, benchmark-integrity guard | zero real credential probes and no private/blind access in handoff campaigns |
| Observability | `RunTrace`, evaluators, failure/stability/communication reports | structured inspectable events/metrics; no external observability backend claimed |
| Model/provider quality | ADR-008…011 and issue #44 | **UNEXECUTED_GATED**: 0/32 live calls, no provider selected |
| Performance | controller limits + EV-007/008 no hidden retry/replay evidence | bounded loops/reliability only; live latency, cost and provider resource behavior unmeasured |
| Reproducibility | ADR-016 + clean workflow + runbook | provider-free clean-checkout evidence |
| Rollback | `FINAL-HANDOFF-RUNBOOK.md` + fail-closed runtime/action/custody rules | code/config/reversal path documented; no exercised deployment-infrastructure rollback claimed |

## Demonstration coverage

The five-scenario ADR-016 demo is intentionally compact. Additional frozen campaigns provide the remaining demonstration dimensions rather than adding a second runtime path.

| Final demo requirement | Evidence |
|---|---|
| Contextualize | DEMO-01 + evaluator-supported final orientation |
| Investigate | DEMO-01 tool proposal/call/result/observation trace |
| Execute | DEMO-05 controlled accepted `reprocess_analysis` |
| Clarify / insufficient evidence | DEMO-02 and DEMO-03 |
| Escalate | DEMO-04 |
| Conflict / uncertainty | EV-007 failure profiles and EV-011 partial/unavailable/uncertain cases |
| Failure / robustness | EV-007 |
| Customer-safe response | EV-011 |
| Per-run evaluation | all ADR-016 demo traces are evaluated |
| Reliability view | EV-008 + EV-007 aggregate campaigns |

## Benchmark/security integrity

The key source is [`BENCHMARK-INTEGRITY-GATE.md`](BENCHMARK-INTEGRITY-GATE.md), backed by BIG-B0→BIG-B4 machine artifacts and workflow guards. Important review facts:

- historical DEV + VALIDATION are an exposed development/selection pool;
- legacy LOCKED_TEST is not described as pristine/untouched;
- no fresh blind source is currently authorized;
- private gold is evaluation-only and never runtime prompt material;
- identity and seed are runner/runtime-owned;
- API permissions and project/system policy are separate;
- accepted action-event semantics are used instead of false final-state equality;
- grouping unit for scientific generalization is `asset_story_group` to prevent split leakage.

## External/gated items reviewers should not mistake for completed work

### Live provider selection

Issue #44 has a frozen 32-attempt comparison plan, clients, executor and custody wrapper. It remains **unexecuted** at 0/32 because explicit secrets plus a canonical durable custody root are required. No provider/model is selected; no live latency/cost/quality result exists.

### C4 continuation

The exact evaluator-side score-row artifact required for per-group/slice reporting is externally unavailable:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Reconstruction, rescoring or substitution is forbidden. This blocks the next C4 reporting step; it does not invalidate already frozen deterministic/bootstrap/LOGO evidence.

## Final reviewer rule

Treat a row as satisfied only within the scope of the exact linked evidence. A green provider-free validator does not imply live-provider quality, a safe supplied/test action does not authorize real customer mutation, and benchmark-integrity controls do not create fresh-blind evidence that does not exist.