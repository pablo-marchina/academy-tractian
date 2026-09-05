# Academy × TRACTIAN — Consolidated Action Plan

**Status:** ACTIVE / canonical execution plan  
**Checkpoint:** 2026-09-05 corrected production rebaseline  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This plan supersedes the September 2 sequencing around already-completed PRs/experiments. Historical plans remain in Git/evidence history but are not current execution authority.

## 1. Final objective

Deliver a **remote, multi-user, production-oriented, USD-zero TRACTIAN Industrial Agent + Evaluation platform** with:

- actual project cash cost fixed at USD 0;
- no silent paid spillover or paid fallback;
- no local dependency in the production serving path;
- standards-based user identity before production IAM is claimed;
- tenant isolation and safe consequential actions;
- durable remote PostgreSQL-compatible state selected inside the USD0 constraint;
- quantitative/eval-driven model and architecture decisions;
- adaptive behavior only where it beats a simpler baseline;
- live frontend visibility into architecture, runs, evidence, outputs, evaluation and production health;
- remote capacity/recovery evidence;
- human-calibrated semantic evaluation where deterministic truth is insufficient;
- measured operational value before business claims;
- systematic research/ADR evidence for every material technology choice.

## 2. Priority and eligibility rule

Every external/hosted candidate first passes the non-negotiable eligibility filter:

```text
USD 0 actual cash cost
AND remote / no local serving dependency
AND required security/privacy constraints
        ↓
technically eligible candidate
        ↓
quality / safety / reliability / production hard gates
        ↓
quantitative Pareto comparison
        ↓
PROMOTE / KEEP_BASELINE / NO_SELECTION
```

A paid candidate can be used only as research/reference evidence; it cannot be selected while the project USD0 rule applies.

Priority after eligibility:

```text
P0 — hard constraints + production / security / claim blockers
        ↓
P1 — measurable quality / evaluation / operational value
        ↓
P2 — optional architecture challengers after measured gap
```

When tasks compete:

1. hard-constraint violation first;
2. production blocker next;
3. safety/security blocker next;
4. missing evidence for a claim next;
5. measurable value/quality experiment next;
6. sophistication-only change last.

## 3. Phase 0 — repository/governance cleanup

**Priority:** P0  
**State:** in progress on cleanup PR

### Deliver

- one canonical document per question;
- accurate root navigation;
- current architecture/status/plan/principles synchronized;
- USD0 preserved as a hard project constraint everywhere;
- historical research workflows removed from normal product-PR triggers;
- evidence lifecycle documented;
- code domains mapped;
- dead-code removal only after reachability proof;
- no cosmetic movement of frozen/source-pinned evidence.

### Gate

- `final-ci-required` green;
- product PR triggers contain no historical one-shot research suites;
- runtime behavior unchanged;
- no frozen evidence path broken;
- no canonical document treats paid infrastructure/provider usage as selectable.

No feature development starts from a dirty/contradictory baseline.

## 4. Phase 1 — USD0 remote production deployment

**Priority:** P0 / blocker

### Objective

Turn the production-path repository into an actually remote service at **USD 0 actual cash cost**. No developer machine may be required for serving.

### Work

- systematic hosting/database research restricted at selection time to USD0-eligible remote candidates;
- record paid candidates only as external benchmarks when useful;
- evaluate free-tier durability, quotas, sleep/scale-to-zero, billing requirements and paid-spillover risk;
- immutable backend build/container artifact or equivalent;
- remote frontend build/hosting;
- remote durable PostgreSQL-compatible serving state;
- secret/environment management;
- TLS/HTTPS;
- health/readiness endpoints;
- graceful shutdown;
- controlled DB migrations;
- remote API/SSE integration;
- production startup validator that rejects forbidden local dependencies;
- fail-closed cost guard so normal operation cannot silently become paid;
- immutable release metadata: commit SHA, build/image digest or equivalent, schema version.

### Production-mode hard gates

Reject/invalidate a production candidate when configuration or operation requires:

- actual project cash cost > USD 0;
- automatic paid spillover;
- localhost/loopback;
- local model server;
- SQLite/DuckDB/filesystem serving truth;
- mock/test decision source;
- development identity bypass.

### Acceptance

From a fresh unrelated device/network:

1. open the product URL;
2. authenticate;
3. create a run;
4. observe it live;
5. reconnect;
6. recover persisted state;
7. do all of the above without any developer laptop/process;
8. demonstrate that the selected serving path remains USD0 and cannot silently spill into paid usage.

If no USD0 remote candidate satisfies the required production gates, the phase ends with an explicit blocker/`NO_SELECTION`, not a paid fallback.

## 5. Phase 2 — USD0 real IAM and multi-user product

**Priority:** P0

### Objective

Replace “signed internal runtime identity is enough” with a standards-based browser/user identity using a USD0-eligible path.

### Work

- systematic IAM comparison with USD0 as an eligibility gate;
- OIDC/OAuth Authorization Code + PKCE or equivalent standards-based flow;
- login/logout/session lifecycle;
- token expiry/refresh semantics;
- server-owned mapping to `user_id`, `identity_id`, `organization_id`, role and permissions;
- preserve PostgreSQL RLS as independent enforcement;
- cross-user/cross-tenant browser/API/SQL acceptance.

### Hard gates

- actual cash cost = USD 0;
- frontend never owns tenant authorization;
- organization B cannot observe organization A;
- privilege escalation/token manipulation fails closed;
- expired/invalid identities fail closed.

## 6. Phase 3 — repository protection and USD0 CI/CD

**Priority:** P0

### Work

- protect `main` with ruleset/branch protection;
- require PRs;
- require stable `final-ci-required / required-gate`;
- block force/direct pushes as appropriate;
- staging deployment after merge using USD0-eligible infrastructure;
- remote smoke/E2E before production promotion;
- production smoke;
- rollback target and tested rollback procedure;
- release/build provenance;
- ensure CI/CD additions do not require paid add-ons.

### Gate

Intentionally bad candidate must be stopped before production or safely rolled back in a controlled test, with actual project cash cost remaining USD0.

## 7. Phase 4 — production observability

**Priority:** P0

### Preserve

The domain-specific PostgreSQL observability/control-room model remains product truth.

### Add/compare

Use a systematic decision for external/platform telemetry. OpenTelemetry is a technical baseline candidate, but any selected hosted telemetry backend must itself be USD0-eligible; a paid backend cannot be selected.

### Correlation contract

Every production request/run should be correlatable through:

- request ID;
- run ID;
- trace ID where external telemetry is used;
- user/organization scope in safe server-side telemetry;
- build/deploy revision;
- provider/model/tool identifiers where safe.

### Frontend Production Health

Expose live safe state such as:

- environment/build/commit;
- API/database/provider health;
- request/error/latency distributions;
- SSE lag/reconnect/gaps;
- action uncertainty/lease state;
- last backup/restore-drill status once available;
- quota/free-tier/cost-boundary health where relevant without exposing secrets.

## 8. Phase 5 — remote load, capacity and SLO

**Priority:** P0

### Method

Run on the selected USD0 deployed path with increasing concurrency until saturation/inflexion, respecting free-tier limits and without enabling paid spillover.

```text
1 → 5 → 10 → 25 → 50 → 100 → ... only while the eligible platform safely supports it
```

Stop based on measured saturation, quota boundaries or hard constraints, not an arbitrary target.

### Measure

- throughput;
- p50/p95/p99;
- error/timeout rate;
- CPU/memory or provider-exposed resource proxies;
- DB pool/connections;
- provider latency/errors;
- event persistence/SSE delivery lag;
- reconnect/duplicate/gap rate;
- action throughput where safe;
- quota/resource consumption;
- actual cash cost, which must remain USD 0.

Then run a soak campaign within the same hard constraints.

### Gate

Production capacity/SLO claims are forbidden until derived from remote evidence. If free-tier ceilings are the limiting factor, report the measured ceiling honestly instead of paying to exceed it.

## 9. Phase 6 — HA, backup, recovery, RTO/RPO

**Priority:** P0

### Failure campaign

Test deployed behavior under capabilities available in the selected USD0 topology:

- backend instance restart/failure;
- DB connection loss/failover where supported;
- provider timeout/outage;
- SSE disconnect/reconnect;
- deployment during execution;
- read-only runtime lease expiry/takeover;
- action lease ownership loss;
- rollback.

### Data protection campaign

- use the strongest USD0-eligible backup/PITR/export mechanism available;
- controlled restore drill;
- integrity verification.

### Derive from evidence

- measured recovery time → basis for RTO;
- observed possible data-loss window → basis for RPO.

Do not invent RTO/RPO from provider marketing. If a desired HA/backup feature exists only on a paid plan, it is ineligible and must be reported as a limitation rather than purchased.

## 10. Phase 7 — human semantic calibration

**Priority:** P1

### Dataset

Stratified cases across:

- complete/partial/conflicting/unavailable evidence;
- clarification;
- escalation;
- abstention;
- action proposal.

### Process

- independent blinded human labels;
- adjudication where required;
- compare automated semantic evaluator/judge to humans.

### Metrics

- agreement;
- Cohen's kappa or appropriate multi-rater statistic;
- confusion matrix;
- precision/recall/F1 by verdict/slice;
- false-safe and missed-escalation rates.

### Gate

A semantic judge cannot gate promotions until its reliability is measured and accepted.

## 11. Phase 8 — operational-value study

**Priority:** P1 / high partner value

### Comparison

Same cases, paired conditions:

```text
MANUAL investigation
vs
AGENT-ASSISTED investigation
```

### Primary metric

`time to correct operational decision`

### Secondary metrics

- correctness;
- unsafe-action rate;
- escalation precision/burden;
- evidence coverage;
- tool count;
- retries;
- human interventions.

### Analysis

Report distributions, median paired delta, bootstrap confidence interval and effect size where meaningful.

No engineer-time/business-value claim before real human data exists.

## 12. Phase 9 — hosted USD0 provider/model tournament

**Priority:** P1

Production candidates must be **remotely hosted and USD0-eligible**. Local model serving and paid APIs are not selectable production candidates.

### Eligibility filter

Before task-quality comparison, candidate must prove:

- expected and observed project cash cost = USD 0;
- no automatic paid spillover;
- usable remote API/runtime path;
- quotas sufficient for the preregistered experiment;
- required privacy/security conditions.

Candidates failing this filter are `INELIGIBLE`, not low-scoring alternatives.

### Controlled workload

Use the same locked workload/evaluator boundaries across eligible candidates.

### Compare

- operational correctness;
- evidence/tool/argument quality;
- clarification/escalation/abstention;
- safety hard gates;
- p50/p95/p99;
- token/resource use;
- quota headroom;
- timeout/error/malformed-output rate;
- repeated-run stability;
- actual cash cost (= USD0 hard gate).

### Decision

Among eligible candidates use Pareto reasoning:

`quality × safety × latency × reliability × resource/quota efficiency`

Valid results include `PROMOTE`, `KEEP_BASELINE` and `NO_SELECTION`.

**Cloudflare status:** D01/D02 proved cost eligibility (USD0) but the tested candidates failed M1/M4/M7, therefore `NO_SELECTION`. A new Cloudflare model/configuration may compete only under a new preregistered experiment; consumed D01/D02 packets are not replayed.

Provider fallback is a separate challenger. Every fallback candidate must independently satisfy USD0 and the technical gates; there is no paid emergency fallback.

## 13. Phase 10 — adaptive agent challengers

**Priority:** P1

Potential isolated experiments:

- adaptive evidence/stopping;
- tool ordering;
- clarification threshold;
- escalation threshold;
- provider/model routing among eligible USD0 candidates;
- contextual time/resource/quota budget.

Keep auth/RLS/permissions/action confirmation/custody/idempotency/leases/privacy and zero-cost boundaries deterministic.

Every adaptive challenger must beat the static/simple baseline on locked quantitative evaluation without weakening safety or USD0 eligibility.

## 14. Phase 11 — frontend as live production control room

**Priority:** P1

The frontend should expose real server-owned data for:

- Mission Control;
- Live Run Cockpit;
- Run Explorer;
- Timeline/waterfall;
- Trace/Architecture graph;
- Evidence Explorer;
- Output Lineage;
- Action Control;
- Eval Lab;
- Provider Lab;
- Production Health;
- Operational Value.

Architecture visualization should identify active components, path, latency, provider/tool usage and safe health state live.

Show structured provenance and reason codes; never expose hidden chain-of-thought.

## 15. Phase 12 — security hardening

**Priority:** P1

Test at minimum:

- tenant spoofing/cross-tenant access;
- token replay/expiry/manipulation;
- privilege escalation;
- prompt/tool-argument injection;
- confirmation bypass;
- duplicate/replayed actions;
- DB role/RLS bypass;
- unauthorized SSE subscriptions;
- secret/dependency/container vulnerabilities;
- cost-boundary bypass / accidental paid-spillover paths.

Supply-chain checks should use USD0-eligible tooling and include dependency, secret, static and deploy-artifact scanning appropriate to the selected stack.

## 16. Phase 13 — optional architecture challengers

**Priority:** P2

Only after P0/P1 gaps are measured:

- LangGraph/durable workflow framework;
- multi-agent topology;
- RAG/document retrieval;
- persistent memory;
- MCP;
- Redis/Kafka/event bus;
- microservices/Kubernetes.

Each must solve a measured problem, satisfy USD0 eligibility for the selected project path and beat the current simpler baseline.

## 17. Final production freeze

Freeze only after evidence is sufficient.

Final bundle should include:

- production URL and release/build identity;
- proof that the selected production path remains USD 0 and has no paid spillover;
- final architecture + ADRs;
- deployment/IAM/storage decisions;
- dataset/evaluator hashes;
- baseline/candidate results;
- provider decision or `NO_SELECTION`;
- load/SLO evidence;
- recovery/backup/RTO/RPO evidence where claimed;
- auth/RLS/action-safety evidence;
- semantic-calibration result or explicit limitation;
- operational-value result or explicit limitation;
- live frontend evidence;
- reproducible runbook and rollback.

## 18. Definition of Done

The project is not finished until all applicable statements are true:

- [ ] actual project cash cost remains USD 0;
- [ ] selected external components cannot silently spill into paid usage;
- [ ] remote product URL exists;
- [ ] production serving depends on no local machine/service/model/store;
- [ ] multiple users can operate concurrently;
- [ ] tenant isolation is enforced server-side/RLS;
- [ ] USD0-eligible standards-based user auth is deployed before IAM claims;
- [ ] protected CI/CD controls production changes;
- [ ] durable state survives tested restart/recovery scenarios;
- [ ] consequential actions remain confirmation/custody/lease/fencing safe;
- [ ] remote capacity is measured and SLOs are evidence-based;
- [ ] backup/restore is tested before data-protection claims;
- [ ] production health is observable;
- [ ] architecture/runs/evidence/evals/outputs are visible live in the frontend;
- [ ] semantic evaluator is human-calibrated before semantic promotion gates;
- [ ] operational value is measured before business-value claims;
- [ ] hosted provider/model decision is experiment-backed and USD0-eligible, or explicitly `NO_SELECTION`;
- [ ] material technology decisions have systematic research + ADRs;
- [ ] unused components are removed only when proven safe;
- [ ] claims never exceed evidence.

If no candidate can satisfy both USD0 and the technical production gates, document the unresolved blocker; never solve it by silently changing a user-specified hard constraint.
