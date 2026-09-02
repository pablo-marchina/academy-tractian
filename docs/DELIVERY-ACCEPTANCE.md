# Academy × TRACTIAN — Delivery Acceptance

**Status:** ACTIVE / canonical Definition of Done  
**Checkpoint:** 2026-09-02 20:20 BRT  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**TAPI coverage:** [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md)

This document answers one question: **what must be demonstrably true before the final project can be called complete?**

## 1. Final acceptance rule

```text
UPDATED TAPI agent behavior covered
+
UPDATED TAPI evaluation framework covered
+
API/tool/action safety and evaluator integrity preserved
+
material stack/architecture choices evidence-backed
+
D01/D02/provider claims bounded by evidence
+
semantic response-quality evaluation valid where needed
+
adaptive behavior either quantitatively promoted or explicitly rejected
+
runtime/HITL and operational-store final choices bounded by evidence
+
genuine realtime safe observability + frontend demonstrated
+
Playwright full-product E2E passes
+
production start/restart + clean reproduction pass
+
README/runbook/results/limitations match actual product
```

Any uncovered P0 is a blocker unless final scope is explicitly reduced with an evidence-honest limitation.

## 2. Updated-TAPI product acceptance

The final solution must include both:

1. **Industrial Agent** — interpret requests, consult the supplied TRACTIAN API and conduct appropriate behavior/actions.
2. **Agent Evaluation Framework** — investigate the quality and reliability of agents using the supplied API.

Every final delivery must also include:

- API integration;
- technical experiment;
- documented results and limitations.

The final product must cover the support modes:

```text
CONTEXTUALIZE
INVESTIGATE
EXECUTE
```

## 3. Agent acceptance

The delivered agent must demonstrate on real integrated paths:

- contextualize/orient using grounded evidence;
- investigate with appropriate TRACTIAN read tools;
- select valid functions;
- construct valid typed arguments;
- handle complete, partial, inconclusive, conflicting and unavailable API evidence;
- ask clarification when required;
- abstain safely when no justified path exists;
- escalate with a structured human handoff;
- contain unauthorized/invalid consequential actions;
- propose and execute only explicitly governed consequential actions;
- produce customer-safe terminal communication;
- preserve inspectable trajectory/provenance;
- fail safely when provider/tool/runtime boundaries fail.

Required evidence includes real traces, negative cases and degraded-response cases, not final text only.

## 4. Consequential-action acceptance

The production action path must prove:

- proposal is not execution;
- permission/resource/schema/justification validation is deterministic;
- action payload is held in private server-side custody;
- operator/browser confirms only an opaque action identity and explicit consent;
- browser cannot inject arguments, permissions, requester identity, scope or idempotency key at confirmation;
- current authorization and host-owned action kill switch are revalidated at execution time;
- idempotency is persistently claimed before transport;
- one logical action cannot execute twice under tested concurrency/restart semantics;
- ambiguous post-claim failure becomes `UNCERTAIN` and is never automatically replayed;
- accepted action produces a separate realtime execution RunTrace;
- action execution has a dedicated trace-only evaluator;
- another requester cannot enumerate or confirm the action.

The frozen read-only ProductionRuntime/ProductionEvaluator must not be weakened to satisfy this.

## 5. Evaluation-framework acceptance

The evaluation framework must support and demonstrate:

- scenario execution;
- function/tool-selection evaluation;
- argument validity/semantic correctness where measurable;
- execution trajectory integrity;
- evidence/provenance use;
- response/terminal outcome quality;
- safety/containment;
- performance under failures/degraded API modes;
- repeated-run stability;
- high-impact-action behavior;
- escalation/handoff quality;
- customer-safe communication;
- evaluator/runtime isolation;
- reproducible result/config identities;
- baseline-vs-candidate delta reporting for material changes.

Private benchmark/gold truth must never enter runtime/model context.

## 6. Semantic response-quality acceptance

Deterministic evaluation remains authoritative wherever exact evidence exists.

Where the TAPI quality dimension cannot be adequately scored deterministically, add a separately identified semantic layer for:

- operational conclusion quality;
- groundedness/evidence support;
- unsupported claims;
- escalation/handoff usefulness;
- customer-safe communication;
- relevant completeness/clarity.

Any LLM/semantic judge used as a gate must first be calibrated against a human-labelled sample.

Required evidence:

- explicit rubric;
- blind human-labelled calibration rows;
- judge-vs-human agreement/error analysis;
- response-mode slices;
- disagreement/failure examples;
- no judge promotion if calibration is insufficient;
- deterministic and semantic Eval Lab outputs visually separated.

## 7. Eval-Driven Development acceptance

For every material behavior/architecture candidate:

```text
requirement
→ metric/evaluator
→ frozen baseline
→ preregistered hypothesis/candidate
→ controlled implementation
→ repeated/sliced comparison
→ uncertainty/failure analysis
→ PROMOTE / REJECT / INCONCLUSIVE
→ regression gate
```

The comparison must be group-aware for the delivered 16 narrative scenarios / 17 coupled rows and must not treat coupled rows as independent evidence.

Hard gates include:

- gold leakage = 0;
- credential/private-field leakage = 0;
- unauthorized action = 0;
- duplicate consequential action = 0;
- known-tool validity = 100%;
- trace integrity = 100% for accepted runs;
- no safety/integrity regression hidden by an aggregate score.

## 8. Adaptive-policy acceptance

Adaptation is allowed only inside deterministic safety boundaries.

Candidate dimensions:

- adaptive investigation budget;
- evidence-sufficiency/marginal-gain stopping;
- calibrated clarification/abstention/escalation from risk × uncertainty × contradiction.

The system must keep deterministic:

- authentication/authorization;
- identity/evaluation seed;
- ToolSpec/schema validation;
- permissions/resource scope;
- action confirmation/idempotency/no-replay;
- privacy/leakage controls;
- hard maximum execution/resource limits.

An adaptive candidate enters production only if it materially improves at least one required quality/reliability/efficiency dimension without critical regression. Otherwise the fixed/simple baseline remains final and the negative experiment remains documented.

## 9. Runtime/HITL architecture acceptance

The original custom AgentController remains the baseline.

Because the final product now includes pending-action custody + human confirmation/resume, final architecture freeze must prospectively revalidate whether the current runtime remains preferable to a durable-checkpoint/HITL orchestration alternative.

Minimum comparison when material:

```text
A — current custom controller + action custody
B — LangGraph-compatible persistent checkpoint/HITL adapter
```

Hold provider, tools, HarnessRunner, safety, cases and evaluators constant.

Evaluate:

- task/trace equivalence;
- pause/resume correctness;
- restart recovery;
- duplicate action rate;
- failure containment;
- latency/resource overhead;
- implementation/dependency complexity;
- clean reproduction;
- debug/trace clarity.

`NO_CHANGE` is accepted and preferred if the current runtime remains on the best-supported Pareto frontier.

## 10. Operational storage acceptance

DuckDB remains the analytics baseline.

Final mutable operational state must be bounded by the production claim actually demonstrated.

If the product claims only a tested single-process/single-node action executor, current DuckDB custody/idempotency may be accepted after restart/concurrency tests.

If a broader multi-process durable claim is made, compare against a production-appropriate local operational store such as PostgreSQL before freeze.

Acceptance measurements:

- concurrent claims;
- duplicate-action rate;
- restart/crash recovery;
- atomicity/transaction behavior;
- p50/p95 state latency where meaningful;
- setup/migration complexity;
- resource footprint;
- clean reproduction;
- USD0 compliance.

Do not claim multi-process mutation/realtime durability unless tested.

## 11. Provider experiment acceptance

D01 historical evidence remains immutable:

- 32/32 completed attempts;
- USD0;
- complete resource accounting;
- `NO_SELECTION`;
- no raw provider material recorded;
- 24/24 generic `CLIENT_FAILURE` at exact 512 completion ceiling.

D02 acceptance requires:

- exact prospective 1024-token protocol;
- fresh post-reset governed authorization;
- no paid spillover;
- write-ahead custody/no replay;
- complete or explicitly stopped accounting;
- sanitized failure subtypes;
- D01 vs D02 controlled analysis;
- frozen hard-gate/Pareto decision, including `NO_SELECTION` when appropriate.

No architecture change is accepted merely because a provider performs poorly.

## 12. Realtime observability acceptance

Browser-visible telemetry must derive from the deterministic safe projection, never raw RunTrace.

Must prove:

- live run appears without refresh;
- genuine runtime events update timeline/trace graph/architecture/counters;
- event order is preserved;
- connection state is explicit (`LIVE`, `RECONNECTING`, `CAUGHT_UP`, `HISTORICAL`);
- persisted cursor/Last-Event-ID catch-up works;
- duplicate delivery is logically idempotent;
- event gaps are detected/measured;
- slow/disconnected browser cannot materially block runtime;
- terminal UI appears only after genuine terminal evidence;
- no fabricated thinking/progress is presented as telemetry;
- realtime/action/health metrics are derived from real instrumentation.

## 13. Security/privacy acceptance

Browser/API/SSE must never receive:

- provider credentials/tokens;
- account IDs/auth headers;
- runtime identity binding/user ID;
- evaluation seed;
- raw provider request/response;
- forbidden raw prompt/system material;
- forbidden raw tool/observation bodies;
- raw action custody payload/idempotency key;
- hidden chain-of-thought;
- evaluator-private truth/oracles/gold.

Required tests must prove deny-list behavior.

## 14. Frontend product acceptance

Required connected product areas:

1. Mission Control;
2. Live Run Cockpit;
3. Run Explorer;
4. Timeline/Waterfall;
5. Trace Graph;
6. Architecture Explorer;
7. Evidence Explorer;
8. Output Lineage / Explain This Run;
9. Action Control;
10. Tools & Policy analytics;
11. Eval Lab;
12. Provider D01/D02 Lab;
13. Dynamic Data Explorer;
14. Production Health.

Every semantically meaningful KPI/chart/aggregate must drill toward underlying safe run/event/evidence records.

For representative runs, the UI must answer:

- what happened;
- which actual architecture components participated;
- what each component produced;
- what safe evidence/input fed it;
- what happened next;
- which output became terminal;
- what evaluation happened afterward;
- which action/confirmation state exists where relevant.

Origin vocabulary:

```text
MODEL
CONTROLLER
POLICY
TOOL
OBSERVATION
EVALUATOR
SYSTEM
```

No hidden chain-of-thought.

## 15. Dynamic visualization acceptance

The Data Explorer must:

- expose only allow-listed safe datasets/fields;
- support global run scope plus compatible local filters;
- support semantically valid rates/p50/p95/distributions;
- validate chart compatibility deterministically;
- provide table/bar/line/scatter/heatmap/histogram where applicable;
- update without full-page reload;
- permit drill-down to safe source records;
- reject unsupported combinations clearly;
- never execute arbitrary browser SQL.

Required ready-made analysis includes:

- outcomes over time;
- runtime/API p50/p95;
- tools/policy blocks;
- failure subtypes;
- output tokens vs outcome where measured;
- D01/D02 comparison;
- Neuron/resource accounting;
- evaluator pass/bounded rates;
- production-health instrumentation.

## 16. Quantitative production acceptance

Use measured provider-free baselines to preregister targets before looking at final candidate/rehearsal results.

Report at minimum:

- startup/readiness time;
- runtime request/execution p50/p95;
- API/query p50/p95;
- observability publish/persistence overhead;
- runtime-event → persistence p50/p95;
- persistence → browser/SSE p50/p95;
- reconnect recovery rate/time;
- detected event-gap rate;
- logical duplicate rate;
- executor utilization/concurrency pressure;
- process CPU/load/RSS;
- passive provider failure/latency observations;
- TRACTIAN HTTP status distribution;
- forbidden-field leakage.

Do not invent post-hoc thresholds from final results.

## 17. Browser/E2E acceptance

The final dependency graph must be frozen with a committed frontend lockfile and deterministic lockfile install (`npm ci` or equivalent).

Playwright must exercise the real provider-free product path:

1. submit a production request;
2. observe genuine SSE events;
3. validate ordering and logical idempotency;
4. disconnect/reconnect and catch up;
5. inspect trace + architecture;
6. inspect evidence + lineage;
7. use global scope/cross-filter/drill-down;
8. observe real Production Health values;
9. cover success, clarify, abstain, escalation, error and blocked action;
10. confirm a pending action in an authorized test profile and follow its separate live execution run;
11. verify terminal output timing;
12. verify evaluator remains post-runtime;
13. verify forbidden data is absent;
14. test loading/empty/long/unsupported-query states and presentation viewport.

## 18. Production deployment/recovery acceptance

From a clean checkout a reviewer must be able to:

- install pinned backend dependencies;
- install frontend from lockfile;
- start the whole product through one documented production path (`docker compose` or equivalent);
- validate environment/config before serving;
- inject secrets only through environment/secret mechanisms;
- obtain truthful `/health`, `/ready`, version/config state;
- gracefully shut down and restart;
- preserve/recover applicable persistent state according to the bounded production claim;
- execute the provider-independent product path;
- run the complete backend/frontend/eval/E2E suite;
- inspect final results/architecture/lineage/limitations.

No demo-only service/path may be required.

## 19. Required outcome/state matrix

At minimum test and visibly support:

- success/orient;
- investigate/tool use;
- ask clarification;
- abstain/unavailable evidence;
- human escalation + handoff;
- pending consequential action;
- confirmed action execution;
- policy/action blocked;
- tool/provider error;
- partial/inconclusive/conflict;
- live run in progress;
- SSE disconnected/reconnecting/caught-up;
- loading;
- empty;
- long/overflow content;
- invalid dynamic query/chart;
- trace validation failure representation;
- D01/D02 experiment state;
- production health degraded state.

## 20. Documentation/reproduction acceptance

README and canonical docs must accurately state:

- updated-TAPI integrated Agent + Evaluation scope;
- current real architecture;
- exact stack/versions or authoritative dependency sources;
- installation/start/restart;
- models/providers/configuration;
- EDD methodology;
- D01/D02 results;
- adaptive/runtime/storage decision results;
- semantic evaluator calibration result;
- production measurements;
- limitations/non-claims;
- opportunities/reversal triggers;
- rubric → evidence navigation.

No canonical document may still call already implemented frontend/observability work merely `planned`.

## 21. Freeze acceptance

By end of 2026-09-05:

- feature set frozen;
- visual/information hierarchy frozen;
- runtime→telemetry→frontend contracts frozen;
- production action contract frozen;
- semantic-eval gating decision frozen;
- adaptive policy either promoted or rejected;
- runtime/HITL choice frozen or explicitly bounded `NO_CHANGE`;
- operational store/deployment claim frozen;
- no open unbounded P0 defect;
- remaining P1 explicitly bounded.

After freeze, only delivery-blocking fixes are allowed and each requires targeted regression.

## 22. Final presentation acceptance

The final presentation operates the normal product path and visibly shows:

```text
request
→ live run
→ architecture activation
→ model/decision metadata
→ typed tool proposal
→ deterministic policy/safety
→ TRACTIAN call metadata
→ safe evidence
→ next decision
→ final / clarify / abstain / escalation / governed action
→ completed RunTrace
→ post-runtime evaluation
→ output lineage
→ production health
→ dynamic quantitative analytics
→ D01/D02 + final architecture-decision evidence
```

It must include multiple outcome/failure classes and preserve a provider-independent fallback.

## 23. Evidence-honest non-claims

The final project may legitimately contain:

- `NO_SELECTION` for provider;
- `REJECT` for adaptive policy;
- `NO_CHANGE` for custom controller vs LangGraph;
- `NO_CHANGE` for DuckDB operational baseline if only single-process production is claimed.

Negative decisions backed by controlled evidence strengthen the project. They must never be replaced by invented winners or fashionable complexity.

The missing exact C4 evaluator artifact remains an external blocker for claims requiring that exact material and must not be reconstructed or substituted.
