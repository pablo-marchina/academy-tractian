# Academy × TRACTIAN — Delivery Acceptance

**Status:** ACTIVE / canonical Definition of Done  
**Checkpoint:** 2026-09-05 corrected production rebaseline  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**TAPI coverage:** [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md)

This document answers one question: **what must be demonstrably true before the project may be called complete?**

## 1. Final acceptance rule

```text
USD 0 actual project cash cost + no paid spillover
+
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
remote durable PostgreSQL-compatible serving state
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
hosted USD0 provider/model decision or explicit NO_SELECTION
+
protected CI/CD + rollback
+
clean reproduction + accurate documentation
```

All hard constraints apply simultaneously. A production-quality requirement never authorizes relaxing USD0, and USD0 never authorizes relaxing quality/safety/production gates. If no candidate satisfies all applicable hard gates, the correct state is `NO_SELECTION`, `NOT READY` or an explicit blocker.

## 2. Zero-cost acceptance

USD 0 actual project cash cost is a hard project constraint, not a weighted metric.

Before any external/hosted component can be selected it must prove:

- expected normal-path cash cost = USD 0;
- observed project cash cost = USD 0;
- no silent/automatic paid spillover;
- no required paid upgrade for the selected normal production path;
- quotas/limits are explicitly known and observable;
- exhaustion degrades/fails safely rather than charging money.

Paid alternatives may be documented as external benchmarks but are `INELIGIBLE` for project selection.

## 3. TAPI product acceptance

The final solution must contain both:

1. **Industrial Agent** — interpret requests, use the supplied TRACTIAN API and produce operationally appropriate behavior/actions.
2. **Agent Evaluation Framework** — measure agent quality, reliability, trajectory, evidence use, safety and failure behavior.

The product must visibly support `CONTEXTUALIZE`, `INVESTIGATE` and `EXECUTE`, with outcomes such as `FINAL/ORIENT`, `CLARIFY`, `ABSTAIN`, `ESCALATE` and governed action proposal/confirmation.

## 4. Industrial-agent acceptance

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

## 5. Remote deployment acceptance

Production is a remotely reachable USD0 product, not a local demo.

Must prove:

- stable remote frontend URL;
- stable remote backend/API endpoint;
- remote durable PostgreSQL-compatible serving store;
- HTTPS/TLS;
- production environment/secrets management;
- immutable build/release identity;
- health/readiness/version surfaces;
- controlled migrations;
- graceful restart/shutdown behavior;
- no mock/test decision source in production;
- no serving dependency on developer laptop/process;
- no paid-spillover path.

Production configuration must reject or make impossible:

- actual cash cost > USD 0;
- automatic billing upgrade/spillover;
- `localhost` / loopback services;
- local/open-weight model serving;
- SQLite/DuckDB/filesystem as production source of truth;
- development identity bypass;
- mock provider/decision source.

From an unrelated fresh device/network, a user must be able to open, authenticate, submit a run, observe genuine live progress, reconnect, recover persisted state and inspect safe evidence/evaluation/output lineage with no developer machine participating.

## 6. IAM and multi-user acceptance

Before production IAM is claimed, browser/end-user identity must use a systematically selected **USD0-eligible standards-based** flow such as OIDC/OAuth Authorization Code + PKCE or equivalent.

Must prove:

- login/logout/session lifecycle;
- expiry/refresh or secure re-authentication semantics;
- server-owned mapping to user/identity/organization/permissions;
- browser cannot assert tenant or privilege authority;
- PostgreSQL RLS remains an independent tenant boundary;
- cross-user/cross-tenant browser/API/SQL negative tests;
- invalid/expired/manipulated identity fails closed;
- privileged access is explicit and audited.

The existing signed bearer runtime envelope may remain as an internal/trusted runtime boundary, but it is not by itself a complete end-user IAM claim.

## 7. Consequential-action acceptance

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

## 8. Evaluation-framework acceptance

Must support scenario execution; tool/function selection; argument validity; trajectory integrity; evidence/provenance use; terminal quality; safety; degraded/failure behavior; repeated-run stability; action behavior; escalation/handoff; customer-safe communication; evaluator/runtime isolation; reproducible config/result identities; and baseline-vs-candidate deltas.

Private benchmark/gold/evaluator truth must never enter runtime/model context.

## 9. Semantic-evaluation acceptance

Deterministic checks remain authoritative where exact truth exists. Semantic dimensions require:

- explicit rubric;
- blinded human-labelled calibration sample;
- independent adjudication where required;
- judge-vs-human agreement/error analysis;
- response/evidence slices;
- confusion matrix and relevant precision/recall/F1;
- appropriate inter-rater agreement statistic;
- failure/disagreement examples;
- preregistered acceptance/rejection thresholds.

No semantic judge may gate candidates before reliability against real human labels is established. If real labels are unavailable, the correct state is `NOT READY`.

## 10. Eval-Driven Development acceptance

Every material behavior/architecture/model/provider candidate follows:

```text
requirement / measured gap
→ hard-constraint eligibility (USD0 included)
→ metric/evaluator
→ baseline
→ preregistered candidate
→ controlled implementation
→ repeated/sliced comparison
→ uncertainty/failure analysis
→ PROMOTE / REJECT / INCONCLUSIVE / NO_CHANGE / NO_SELECTION
→ regression gate
```

Hard integrity gates include as applicable:

- project cash cost = USD 0;
- paid spillover = 0;
- evaluator/gold leakage = 0;
- credential/private-field leakage = 0;
- unauthorized consequential action = 0;
- duplicate replacement consequential action = 0;
- known-tool/schema validity = 100%;
- tenant isolation failures = 0.

## 11. Adaptive-policy acceptance

Adaptation is optional and must remain inside deterministic safety and USD0 boundaries.

Potential adaptive areas include investigation depth, evidence stopping, tool ordering, clarification/abstention/escalation thresholds, provider routing among eligible free candidates, and contextual resource/quota budgets.

Always deterministic/hard-gated: auth/tenant scope, RLS/permissions, schema validation, action confirmation/custody/idempotency/leases/fencing, privacy controls, evaluator isolation, hard execution/resource caps and the no-paid-spillover boundary.

## 12. Storage and realtime acceptance

Promoted logical production state is PostgreSQL. The selected remote serving topology must be USD0-eligible.

Must prove durable tenant-scoped run/action/observability/evaluation state and tested concurrency/restart semantics. DuckDB may remain in dev/benchmark compatibility only.

Realtime must prove durable PostgreSQL rows/cursors are authoritative; live updates without refresh; ordering; reconnect/catch-up; logical idempotency; gap detection; no auth dependence on wake-up payload; no fabricated progress; and terminal UI only from genuine terminal evidence.

## 13. Production observability acceptance

The control room must expose safe server-owned evidence such as build/deploy identity, API/DB/provider health, request/error/latency distributions, event/SSE behavior, tool/policy outcomes, action uncertainty and quota/free-tier boundary health.

Any selected hosted telemetry backend must also satisfy USD0. Prompts/tool arguments/raw sensitive provider material should not be captured by default.

## 14. Remote load, capacity and SLO acceptance

Repository CI load tests are insufficient for a production-capacity claim.

Run a remote campaign on the selected USD0 path with increasing concurrency until measured saturation or free-tier quota boundary, then a soak test where feasible.

Report throughput, p50/p95/p99, error/timeout rate, resource/quota consumption, DB/provider behavior, event/SSE latency/reconnect/gaps/duplicates and actual cash cost (= USD0).

SLOs must come from measured behavior plus product requirements. If the USD0 tier limits capacity, report that limit instead of paying to exceed it.

## 15. Backup, recovery, HA, RTO/RPO acceptance

Test the deployed USD0 topology under relevant backend, DB, provider, SSE, deployment, lease and rollback failures.

Use the strongest selected free backup/PITR/export mechanism, execute a controlled restore drill and derive RTO/RPO only from measured evidence. If a desired HA/backup feature is paid-only, it is an explicit limitation, not an authorized purchase.

## 16. Provider/model acceptance

Historical D01/D02 evidence remains immutable and concludes `NO_SELECTION`.

D02 proves an important distinction:

```text
USD0 eligibility                         PASS
32/32 governed attempts                 PASS
safe failure behavior / trace integrity PASS
M1 structured decision gate             FAIL
M4 task-quality gate                     FAIL
M7 success/stability gate                FAIL
final decision                           NO_SELECTION
```

Therefore Cloudflare was not rejected for cost; it was **eligible on cost but failed technical promotion gates**.

A future production provider/model decision requires a new hosted **USD0-eligible** candidate experiment. Compare operational correctness, evidence/tool/argument quality, clarification/escalation/abstention, safety, p50/p95/p99, reliability, repeated-run stability and resource/quota efficiency.

Valid outcomes include `PROMOTE`, `KEEP_BASELINE` and `NO_SELECTION`. Paid candidates are `INELIGIBLE`, not fallback options. Cloudflare can compete again only through a new preregistered experiment with a materially new eligible hypothesis/configuration/model; consumed D01/D02 packets are not replayed.

## 17. Operational-value acceptance

Before any business/value claim, compare the same cases under `MANUAL` vs `AGENT-ASSISTED` with primary metric `time to correct operational decision` and secondary correctness/safety/escalation/evidence/tool/retry/human-intervention measures.

No engineer-minutes-saved/auto-resolution/value claim without real human observations.

## 18. Frontend product acceptance

Required connected areas should include, as applicable: Mission Control, Live Run Cockpit, Run Explorer, Timeline/Waterfall, Trace Graph, Architecture Explorer, Evidence Explorer, Output Lineage, Action Control, Tools & Policy analytics, Eval Lab, Provider Lab, Dynamic Data Explorer, Production Health and Operational Value once real data exists.

Representative runs must let a reviewer answer what happened, which components participated, which evidence/tool/policy transitions occurred, why the run stopped, what evaluation occurred, what action state exists and which deployed build produced it. Never expose hidden chain-of-thought.

## 19. Security and privacy acceptance

Browser/API/SSE/artifacts must not expose provider credentials, signing secrets, evaluator/gold truth, sensitive raw provider/tool material, private action arguments/idempotency keys or chain-of-thought.

Security testing must cover tenant spoofing/cross-tenant access, token replay/expiry/manipulation, privilege escalation, prompt/tool injection, confirmation bypass, duplicate/replayed actions, RLS bypass, unauthorized SSE access and attempts to bypass the zero-cost/no-paid-spillover boundary.

## 20. Browser/E2E acceptance

Browser acceptance must exercise real product contracts: authenticated remote/staging-compatible run submission, genuine SSE ordering, reconnect/catch-up, trace/architecture/evidence/lineage, terminal modes, action profiles, evaluator ordering, forbidden-field absence, UI edge states and multi-user/tenant negatives once IAM is deployed.

Provider-free deterministic acceptance remains useful for reproducibility but is not evidence that a production provider works remotely.

## 21. CI/CD and repository-governance acceptance

Before production completion:

- `main` is protected;
- PR is required;
- `final-ci-required / required-gate` is required;
- direct/force pushes are appropriately restricted;
- staging precedes production;
- production smoke exists;
- build provenance exists;
- rollback is tested;
- selected CI/CD path remains USD0;
- historical research workflows are not ordinary product-PR gates.

## 22. Reproduction acceptance

A clean checkout must reproduce repository-level evidence locally/CI with pinned dependencies and no secrets where provider-free evidence is intended. This local reproduction path is not production serving.

The runbook must distinguish local/CI deterministic reproduction, remote USD0 staging/production operation and historical experiment reproduction.

## 23. Final evidence bundle

The final freeze must capture/link:

- production URL(s);
- build/release identity;
- evidence that actual project cash cost is USD0 and no paid spillover is possible on the selected path;
- deployment/IAM/database decisions and ADRs;
- architecture;
- dataset/evaluator identities;
- baseline/candidate results;
- provider decision or `NO_SELECTION`;
- load/SLO evidence;
- recovery/backup/RTO/RPO evidence where claimed;
- auth/RLS/action-safety evidence;
- semantic calibration result or explicit limitation;
- operational-value result or explicit limitation;
- live frontend evidence;
- operations/reproduction/rollback runbook;
- limitations/reversal triggers.

## 24. Final presentation acceptance

The presentation must use the normal remote USD0 product path, not a separate demo implementation. It should visibly demonstrate authenticated user → remote request → live run → architecture/tool/policy/evidence transitions → safe terminal/action behavior → post-runtime evaluation → output lineage → production health → quantitative evidence.

## 25. Evidence-honest non-claims

Valid evidence-backed end states include `NO_SELECTION`, `NO_CHANGE`, `REJECT` and `NOT READY`.

It is not acceptable to claim:

- remote production readiness from local CI alone;
- enterprise IAM from the signed runtime bearer alone;
- capacity/SLO/HA/RTO/RPO from repository tests alone;
- Cloudflare selection merely from USD0 eligibility;
- a paid fallback as compatible with the current project constraint;
- a model/provider winner that failed hard gates;
- value/human calibration that was not measured;
- local/DuckDB serving as the final production topology.

The missing exact historical C4 evaluator artifact remains an external blocker for claims requiring that exact material and must not be reconstructed or substituted.
