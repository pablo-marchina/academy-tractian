# Academy × TRACTIAN — Delivery Acceptance

**Status:** ACTIVE / canonical Definition of Done  
**Checkpoint:** 2026-09-05 production rebaseline  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**TAPI coverage:** [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md)

This document answers one question: **what must be demonstrably true before the project may be called complete?**

## 1. Final acceptance rule

```text
TAPI Agent behavior covered
+
TAPI Evaluation framework covered
+
real typed TRACTIAN integration
+
remote multi-user production deployment
+
no local dependency in production serving path
+
standards-based user IAM + tenant isolation
+
safe consequential-action execution
+
PostgreSQL durable state + tested recovery semantics
+
production observability + live frontend
+
remote load/capacity evidence + evidence-based SLO
+
backup/restore/recovery evidence for any RTO/RPO/HA claim
+
valid deterministic + human-calibrated semantic evaluation where needed
+
quantitative EDD for material choices
+
operational-value evidence before business claims
+
hosted provider/model decision or explicit NO_SELECTION
+
protected CI/CD + rollback
+
clean reproduction + accurate documentation
```

Any uncovered P0 is a blocker unless the final claim is explicitly narrowed and the limitation remains visible.

## 2. TAPI product acceptance

The final solution must contain both:

1. **Industrial Agent** — interpret requests, use the supplied TRACTIAN API and produce operationally appropriate behavior/actions.
2. **Agent Evaluation Framework** — measure agent quality, reliability, trajectory, evidence use, safety and failure behavior.

The product must visibly support the operational modes:

```text
CONTEXTUALIZE
INVESTIGATE
EXECUTE
```

and the outcomes:

```text
FINAL / ORIENT
CLARIFY
ABSTAIN
ESCALATE
ACTION PROPOSAL / CONFIRMED ACTION
```

## 3. Industrial-agent acceptance

On integrated paths the agent must demonstrate:

- grounded contextualization/orientation;
- investigation through appropriate typed TRACTIAN tools;
- valid function selection and typed arguments;
- handling of complete, partial, inconclusive, conflicting and unavailable evidence;
- clarification when information is required;
- safe abstention when no justified answer/action exists;
- structured human escalation/handoff;
- containment of invalid/unauthorized consequential actions;
- governed consequential action proposal/execution;
- customer-safe terminal communication;
- inspectable structured trajectory/provenance;
- safe behavior under tool/provider/runtime failure.

Correctness should be evaluated by the operational conclusion and observable process, not exact wording alone.

## 4. Remote deployment acceptance

Production is a remotely reachable product, not a local demo.

Must prove:

- stable remote frontend URL;
- stable remote backend/API endpoint;
- managed/durable remote PostgreSQL;
- HTTPS/TLS;
- production environment/secrets management;
- immutable build/release identity (commit + artifact/image digest or equivalent);
- health/readiness/version surfaces;
- controlled migrations;
- graceful restart/shutdown behavior;
- no mock/test decision source in production;
- no serving dependency on developer laptop/process.

Production configuration must reject or otherwise make impossible serving dependencies on:

- `localhost` / loopback services;
- local/open-weight model server;
- SQLite/DuckDB/filesystem as production source of truth;
- development identity bypass;
- mock provider/decision source.

### Remote user proof

From an unrelated fresh device/network, a user must be able to:

1. open the remote product;
2. authenticate;
3. submit a run;
4. observe genuine live progress;
5. reconnect after interruption;
6. recover persisted run state;
7. inspect safe evidence/evaluation/output lineage;
8. do all of the above with no developer machine participating.

## 5. IAM and multi-user acceptance

Before production IAM is claimed, browser/end-user identity must use a standards-based flow such as OIDC/OAuth Authorization Code + PKCE or another systematically selected equivalent.

Must prove:

- login/logout/session lifecycle;
- expiry/refresh or equivalent secure re-authentication semantics;
- server-owned mapping to user/identity/organization/permissions;
- browser cannot assert tenant or privilege authority;
- PostgreSQL RLS remains an independent tenant boundary;
- cross-user/cross-tenant browser/API/SQL negative tests;
- invalid/expired/manipulated identity fails closed;
- privileged access is explicit and audited.

The existing signed bearer runtime envelope may remain as an internal/trusted runtime boundary, but it is not by itself a complete end-user IAM claim.

## 6. Consequential-action acceptance

The production action path must prove:

- proposal is not execution;
- permission/resource/schema/evidence/justification validation is deterministic;
- action payload lives in private server-side custody;
- operator confirms only opaque action identity + consent;
- browser cannot inject arguments, tenant, requester identity, permissions or idempotency material during confirmation;
- current authorization and host kill switch are revalidated before execution;
- persistent idempotency claim precedes transport;
- non-transferable execution lease/fencing prevents another replica from replacing an ambiguous action attempt;
- duplicate confirmation does not produce a duplicate transport attempt;
- ownership loss/staleness converges to `UNCERTAIN`;
- stale late responses cannot overwrite uncertainty with false success/failure;
- no automatic blind replay occurs;
- accepted/failed/uncertain execution receives a distinct auditable trace/evaluation;
- unauthorized requesters cannot enumerate/confirm another requester’s action.

Do not claim distributed exactly-once external side effects unless the external API participates in a compatible idempotency/fencing protocol.

## 7. Evaluation-framework acceptance

Must support and demonstrate:

- scenario execution;
- tool/function selection quality;
- argument validity/semantic correctness where measurable;
- trajectory integrity;
- evidence/provenance use;
- terminal/outcome quality;
- safety/containment;
- degraded/failure behavior;
- repeated-run stability;
- high-impact-action behavior;
- escalation/handoff quality;
- customer-safe communication;
- evaluator/runtime isolation;
- reproducible config/result identities;
- baseline-vs-candidate delta reporting.

Private benchmark/gold/evaluator truth must never enter runtime/model context.

## 8. Semantic-evaluation acceptance

Deterministic checks remain authoritative where exact truth exists.

For dimensions requiring semantic judgment, the project must provide:

- explicit rubric;
- blinded human-labelled calibration sample;
- independent adjudication where required;
- judge-vs-human agreement/error analysis;
- response-mode/evidence-mode slices;
- confusion matrix and relevant precision/recall/F1;
- inter-rater agreement statistic appropriate to the design;
- failure/disagreement examples;
- explicit acceptance/rejection thresholds defined before final judge promotion.

No semantic judge may gate candidates before reliability against real human labels is established.

If real human labels are unavailable, the correct state is `NOT READY`, not synthetic calibration masquerading as human truth.

## 9. Eval-Driven Development acceptance

Every material behavior/architecture/model/provider candidate follows:

```text
requirement / measured gap
→ metric/evaluator
→ baseline
→ preregistered candidate
→ controlled implementation
→ repeated/sliced comparison
→ uncertainty/failure analysis
→ PROMOTE / REJECT / INCONCLUSIVE / NO_CHANGE
→ regression gate
```

Hard integrity gates include as applicable:

- evaluator/gold leakage = 0;
- credential/private-field leakage = 0;
- unauthorized consequential action = 0;
- duplicate replacement consequential action = 0;
- known-tool/schema validity = 100%;
- trace-integrity failures cannot be hidden by aggregate score;
- tenant isolation failures = 0.

A fashionable framework/component is never an acceptance requirement by itself.

## 10. Adaptive-policy acceptance

Adaptation is optional and must remain inside deterministic safety boundaries.

Candidate areas may include:

- investigation depth;
- evidence-sufficiency/marginal-gain stopping;
- tool ordering;
- clarification/abstention/escalation thresholds;
- hosted provider/model routing;
- contextual resource/time budgets.

Always deterministic/hard-gated:

- auth and tenant scope;
- RLS/permissions;
- ToolSpec/schema validation;
- action confirmation/custody/idempotency/lease/fencing;
- privacy controls;
- evaluator partition isolation;
- hard resource/execution caps.

An adaptive candidate enters production only after a controlled locked comparison shows material benefit without critical regression. `NO_CHANGE` is fully acceptable.

## 11. Storage and realtime acceptance

Promoted production state is PostgreSQL.

Must prove:

- no local-file/DuckDB production truth;
- tenant RLS on applicable production data;
- durable run ownership/execution state;
- durable runtime handoff/generation fencing;
- durable action custody/idempotency/leases;
- durable sanitized observability/evaluation rows;
- transactionally correct state transitions for tested concurrent/restart cases.

DuckDB may remain in dev/benchmark compatibility only.

Realtime must prove:

- durable PostgreSQL rows/cursors are authoritative;
- live run appears without refresh;
- genuine runtime events update the UI;
- ordering is preserved;
- reconnect/catch-up works;
- duplicate delivery is logically idempotent;
- event gaps are detected/measured;
- `LISTEN/NOTIFY` or any wake-up mechanism is never used as tenant/auth truth;
- browser disconnect/slow client does not block runtime execution materially;
- terminal UI appears only from genuine terminal evidence;
- no fabricated thinking/progress is shown.

## 12. Production observability acceptance

The product control room must expose safe server-owned live production evidence, including where applicable:

- environment/build/commit/deploy revision;
- API health/request/error/latency;
- DB health/pool/connection behavior;
- provider/model call latency/failure/token or resource accounting;
- tool/policy outcomes;
- run/event persistence latency;
- SSE delivery/reconnect/gap/duplicate behavior;
- action lease/uncertainty state;
- backup/restore-drill status after those controls exist.

A standardized external telemetry layer may be added through a systematic decision, but it must not replace the domain-specific product truth.

Prompts/tool arguments/raw provider material containing sensitive data should not be captured by default.

## 13. Remote load, capacity and SLO acceptance

Repository CI load tests are insufficient for a production-capacity claim.

Run a remote campaign against the deployed path with increasing concurrency until measured saturation/inflexion, then a soak test.

Report at minimum:

- throughput;
- p50/p95/p99 request/run latency;
- error/timeout rate;
- CPU/memory;
- DB pool/connections;
- provider latency/error rate;
- event persistence and SSE-delivery latency;
- reconnect/gap/duplicate rate;
- action throughput/queueing where safely measurable.

SLOs must be derived from measured behavior plus product requirements, not invented post hoc.

No `capacity-tested`, `production SLO` or worker-sizing claim is allowed before this evidence exists.

## 14. Backup, recovery, HA, RTO/RPO acceptance

If the product claims durability/recovery/HA, it must test the deployed path under relevant failures:

- backend restart/instance loss;
- DB connection loss/failover;
- provider timeout/outage;
- SSE disconnect/reconnect;
- deployment during work;
- read-only runtime lease expiry/takeover;
- action ownership loss;
- rollback.

Data protection must include:

- automated backup/PITR or selected equivalent;
- controlled restore drill;
- restored-data integrity verification.

RTO/RPO must be derived from measured recovery/data-loss behavior. Provider SLA alone is not application RTO/RPO evidence.

## 15. Provider/model acceptance

Historical D01/D02 evidence remains immutable and currently concludes `NO_SELECTION`.

A production provider/model decision requires a new hosted-candidate experiment because local model serving is not eligible for the remote production path.

Compare candidates under the same locked workload and hard gates across:

- operational correctness;
- evidence/tool/argument quality;
- clarification/escalation/abstention;
- safety;
- p50/p95/p99;
- reliability/timeouts/malformed-output rate;
- repeated-run stability;
- tokens/resources;
- cost/run.

Use Pareto reasoning. Valid outcomes include `PROMOTE`, `KEEP_BASELINE` and `NO_SELECTION`.

Provider fallback is a separate challenger and must demonstrate net reliability value before adoption.

## 16. Operational-value acceptance

Before any business/value claim, compare the same cases under:

```text
MANUAL
vs
AGENT-ASSISTED
```

Primary metric:

`time to correct operational decision`

Also capture correctness, safety, escalation burden, evidence coverage, tool/retry count and human interventions.

Report paired distributions/deltas and uncertainty (for example bootstrap confidence intervals) where appropriate.

No engineer-minutes-saved/auto-resolution/value claim without real human observations.

## 17. Frontend product acceptance

Required connected areas should include, as applicable to the current product:

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
12. Provider Lab;
13. Dynamic Data Explorer;
14. Production Health;
15. Operational Value once real data exists.

Representative runs must let a reviewer answer:

- what happened;
- which real components participated;
- which safe evidence/tool/policy transitions occurred;
- what became terminal and why at structured reason-code level;
- what evaluation happened afterward;
- what action state exists where relevant;
- which deployed build produced the run.

No hidden chain-of-thought.

## 18. Dynamic visualization acceptance

Dynamic analysis must:

- expose only allow-listed safe datasets/fields;
- support valid global/local filters;
- report semantically valid rates/distributions/quantiles;
- validate chart compatibility deterministically;
- update without full-page reload where live behavior matters;
- drill down to safe source records;
- reject unsupported combinations clearly;
- never execute arbitrary browser SQL.

Visualizations must be driven by real data, not static presentation fixtures in production.

## 19. Security and privacy acceptance

Browser/API/SSE/artifacts must not expose:

- provider credentials/tokens/auth headers;
- signing secrets;
- evaluator/gold seeds/private truth;
- raw sensitive provider prompt/response material;
- forbidden raw tool/observation bodies;
- private action arguments/idempotency keys;
- hidden chain-of-thought.

Security testing must also cover:

- tenant spoofing/cross-tenant access;
- token replay/expiry/manipulation;
- privilege escalation;
- prompt/tool-argument injection;
- confirmation bypass;
- duplicate/replayed action attempts;
- DB role/RLS bypass;
- unauthorized SSE access.

Supply-chain controls should include dependency/secret/static/deploy-artifact scanning appropriate to the selected production stack.

## 20. Browser/E2E acceptance

Playwright or equivalent browser acceptance must exercise real product contracts, including:

- remote or staging-compatible authenticated run submission;
- genuine SSE events and ordering;
- reconnect/catch-up/idempotency;
- trace/architecture/evidence/lineage;
- success, clarify, abstain, escalation and failure states;
- pending/confirmed/blocked action profiles where safe;
- evaluator post-runtime ordering;
- forbidden-field absence;
- loading/empty/long/error states;
- multi-user/tenant negative cases once IAM is deployed.

Provider-free deterministic acceptance remains useful for reproducibility but is not evidence that a production model/provider works remotely.

## 21. CI/CD and repository-governance acceptance

Before production completion:

- `main` is protected by ruleset/branch protection;
- PR is required for production changes;
- stable `final-ci-required / required-gate` is required;
- direct/force push behavior is appropriately restricted;
- staging deploy/smoke precedes production promotion;
- production smoke exists;
- build/release provenance is recorded;
- rollback target exists and rollback is tested;
- historical research workflows are not ordinary product-PR gates.

## 22. Reproduction acceptance

A clean checkout must still be able to reproduce repository-level evidence locally/CI with pinned dependencies and no secrets where provider-free evidence is intended.

This local reproduction path is **not the production serving path**.

The runbook must clearly distinguish:

- local/CI deterministic reproduction;
- remote staging/production operation;
- historical experiment reproduction.

Frozen historical workflow/result identities must not be rewritten to make later gates pass.

## 23. Final evidence bundle

The final production freeze must capture or link to:

- production URL(s);
- release/build/commit identity;
- selected deployment/IAM/database decisions and ADRs;
- final architecture;
- dataset/evaluator identities;
- baseline/candidate results;
- provider/model decision or `NO_SELECTION`;
- remote load/SLO evidence;
- backup/restore/recovery/RTO/RPO evidence where claimed;
- auth/RLS/action-safety evidence;
- semantic calibration result or explicit `NOT READY` limitation;
- operational-value result or explicit `NOT READY` limitation;
- live frontend evidence;
- reproduction/operations/rollback runbook;
- limitations and reversal triggers.

## 24. Final presentation acceptance

The presentation must use the normal deployed product path, not a separate demo implementation.

It should visibly demonstrate:

```text
authenticated user
→ remote request
→ live run
→ architecture activation
→ decision/tool/policy/evidence transitions
→ final / clarify / abstain / escalation / governed action
→ completed trace
→ post-runtime evaluation
→ output lineage
→ production health
→ quantitative analytics/evidence
```

Provider/model or external failure must not make the entire support workflow unavailable; safe abstention/escalation/fallback behavior should remain demonstrable.

## 25. Evidence-honest non-claims

Negative decisions strengthen the project when evidence-backed. It is acceptable to end with:

- `NO_SELECTION` for provider/model;
- `NO_CHANGE` for LangGraph/multi-agent/RAG/memory/MCP;
- `REJECT` for an adaptive policy;
- `NOT READY` for human semantic/business-value claims when real data is unavailable.

It is **not** acceptable to claim:

- remote production readiness from local CI alone;
- enterprise IAM from the signed runtime bearer alone;
- capacity/SLO/HA/RTO/RPO from repository tests alone;
- a model/provider winner that did not cross the frozen gates;
- value/human calibration that was not measured;
- local/DuckDB serving as the final production topology under the current remote-production requirement.

The missing exact historical C4 evaluator artifact remains an external blocker for claims requiring that exact material and must not be reconstructed or substituted.
