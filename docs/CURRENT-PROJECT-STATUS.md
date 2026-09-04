# Academy × TRACTIAN — Current Project Status

**Status:** `READY_FOR_HARD_FREEZE` candidate / sole canonical human-readable state  
**Checkpoint:** 2026-09-04 BRT  
**Scheduled hard feature/visual/architecture freeze:** end of 2026-09-05  
**Final delivery:** 2026-09-08  
**Freeze decision:** [`../research/final-freeze-decision-2026-09-04.md`](../research/final-freeze-decision-2026-09-04.md)

## 1. Executive status

```text
updated TAPI scope                         Agent + Evaluation in one solution
external API/hosted-service cash cost     USD 0 hard constraint
production agent runtime                  IMPLEMENTED
production deterministic evaluator        IMPLEMENTED
TRACTIAN typed tool registry              18 operations
safe realtime observability               IMPLEMENTED
React operator control room               IMPLEMENTED
full-product Playwright E2E                PASS / gated
frontend lockfile + npm ci                 PASS / gated
current clean-clone reproduction           PASS / gated
stable final required CI                   PASS / required-gate

production consequential actions          IMPLEMENTED
custody + explicit confirmation            IMPLEMENTED
persistent idempotency/no blind replay     IMPLEMENTED

request authentication                    SIGNED BEARER HMAC-SHA256 V1
enterprise OIDC/SSO claim                  FALSE
mutable operational state                 PostgreSQL
analytics/read model                       DuckDB
PostgreSQL tenant RLS                      IMPLEMENTED / tested

human semantic-review collector            IMPLEMENTED
VALIDATION source generation               IMPLEMENTED
human semantic calibration claim           NOT READY — real labels required

operational-value collector                IMPLEMENTED
frozen paired time analysis                IMPLEMENTED
engineer-minutes-saved business claim      NOT READY — real human data required

adaptive stopping replay diagnostic        IMPLEMENTED / evaluator-only
adaptive runtime stopping promoted         NO

load/concurrency campaign                  MEASURED / descriptive only
production capacity claim                  FALSE
restart/recovery campaign                  VERIFIED safety contract
RTO/RPO/availability claim                 FALSE

D01/D02 provider comparison                COMPLETE
D01/D02 cash cost                          USD 0.00
provider selection                         NO_SELECTION

main branch CI contract                    READY / one required-gate
GitHub branch-protection enforcement       PENDING EXTERNAL
last observed main.protected               false
last observed repository rulesets          []

final evidence bundle                      CURRENT P0 / READY candidate
hard freeze effective now                  NO — scheduled end 2026-09-05
```

## 2. Exact current integration evidence

Repository-side final CI is integrated on merged `main` commit:

`b86b15ef32762e5bc3cd474421c177eaa3f56787`

Post-merge `final-ci-required` run `33834299439` completed successfully on that exact SHA:

```text
clean-clone / reproduce-current-product     success
full-product-browser / chromium-full-product success
required-gate                               success
```

`required-gate` is the stable, always-triggered status context intended for branch protection. It runs on every PR and push to `main` and succeeds only if current clean-clone reproduction and Chromium full-product acceptance both succeed.

GitHub enforcement is a separate external control. Until GitHub reports protection active, the project must not claim that direct pushes/merges are technically blocked by a ruleset.

## 3. Promoted product path

```text
browser request
→ signed RuntimeContextProvider
→ organization/user/identity/permissions
→ FastAPI product API
→ PostgreSQL ownership + tenant RLS
→ RealtimeProductionRuntime.prepare()
→ provider-neutral DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ deterministic B1/B2/B3 boundaries
→ normalized evidence
→ FINAL / CLARIFY / ABSTAIN / ESCALATE / action proposal
→ RunTrace
→ ProductionEvaluator
→ safe projection
→ DuckDB analytics/read model
→ REST/SSE
→ React operator control room
```

Consequential action path:

```text
agent proposes exact action
→ deterministic scope/schema/permission validation
→ private PostgreSQL custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ authorization + kill switch revalidated
→ atomic persistent idempotency claim
→ exact custodied action executes
→ separate action execution/run trace
→ ProductionActionEvaluator
→ safe REST/SSE/frontend projection
```

Ambiguous post-claim outcomes become `UNCERTAIN`. Restart is never permission to automatically replay a runtime execution or retry a consequential action.

## 4. Identity and tenant isolation

The promoted entrypoint uses the project-owned `academy-runtime-v1` signed bearer envelope with HMAC-SHA256 verification, issuer/audience/lifetime checks and explicit organization/user/identity/permission claims. Browser payloads cannot provide tenant, identity, role, permissions or benchmark seed.

This is deliberately **not** described as OAuth/OIDC/JWT or enterprise SSO.

PostgreSQL provides an independent tenant boundary. Scoped reads use a non-superuser, non-`BYPASSRLS`, non-owner role and transaction-local `academy.organization_id`; direct SQL integration proves tenant B cannot read a known tenant-A ownership row.

## 5. Operational storage decision

`OPS-STORE-001` selected `PROMOTE_POSTGRES_OPERATIONAL` after PostgreSQL passed every hard gate while the previous DuckDB operational-state baseline produced concurrent operational errors.

The promoted split is:

```text
PostgreSQL  mutable ownership/execution/action custody/idempotency
DuckDB      sanitized observability/evaluation/analytics read model
```

This supports the tested authenticated multi-user durable single-node product. Horizontal multi-instance execution, distributed queues and shared cross-instance SSE are not claimed.

## 6. Evaluation and human evidence state

Delivered:

- deterministic structural/safety/trajectory evaluation;
- operational-conclusion/value contract;
- blinded operational-value collection + server-owned timing;
- frozen paired MANUAL × ASSISTED analysis;
- semantic rubric + frozen calibration protocol v2;
- blinded semantic review A/B + independent adjudication custody;
- trusted VALIDATION source generation from sanitized read model;
- evaluator-only adaptive evidence/stopping replay.

Still human-dependent and therefore **not ready**:

- real semantic labels/adjudication;
- measured judge-vs-human agreement/error profile;
- real manual vs assisted engineer-time observations;
- Engineer Minutes Saved per Ticket;
- useful auto-resolution/business-value claim.

These values must not be fabricated. `LOCKED_TEST` remains excluded from tuning/calibration.

## 7. Adaptive/runtime topology state

The merged adaptive stopping work is DEV-only and evaluator-only. It may quantify replay headroom but cannot authorize a runtime policy change; no oracle-free adaptive challenger has won EDD.

The P0 topology therefore remains **`NO_CHANGE`**:

`custom AgentController + HarnessRunner + PostgreSQL durable action custody/idempotency + conservative restart recovery`.

Current evidence does not identify a LangGraph/multi-agent/RAG/memory/MCP topology bottleneck. Any LangGraph comparison is P1 and must demonstrate a material Pareto improvement without bypassing application-owned safety/tool boundaries.

## 8. Load/concurrency and recovery evidence

### Load

The provider-free authenticated PostgreSQL campaign exercised concurrency 1 and 4 with 12 synthetic measured requests. All completed without errors and higher concurrency visibly saturated the two-worker executor. Latency/throughput/persistence/resource values are preserved in the aggregate artifact.

Interpretation remains `descriptive_only`; CI data is not a production capacity/SLO/worker-sizing claim.

### Restart/recovery

Integrated PostgreSQL recovery proves:

```text
2 orphan runtime executions       → interrupted
1 orphan action execution         → uncertain
1 custody EXECUTING row           → UNCERTAIN
1 ledger CLAIMED row              → UNCERTAIN
PENDING_CONFIRMATION              preserved
completed / failed                preserved
provider/action replay            0
second-start new recoveries       0
```

A fresh authenticated run completes after recovery and remains tenant-isolated. This is a repository safety contract, not RTO/RPO/HA/uptime evidence.

## 9. Provider state

D01 and D02 are complete governed USD-zero experiments. D02 improved multiple public metrics after the 512→1024 completion-budget change, but neither candidate crossed frozen M1/M4/M7 promotion gates.

Final provider state remains:

**`NO_SELECTION` / no production provider claim.**

The consumed governed D02 packet must not be replayed merely to seek a preferable result.

## 10. Reproduction and browser acceptance

Current clean-clone reproduction proves from one fresh checkout:

```text
PostgreSQL 18
→ complete Python suite with Postgres enabled
→ identity/RLS + load + recovery P0 checks
→ ADR-004 controller regression
→ frozen EV-007 / EV-008 / EV-011
→ historical delivery/evidence validation
→ final handoff audit
→ final freeze-bundle validation
→ npm ci from committed package-lock
→ TypeScript typecheck / Vitest / production build
→ zero tracked repository mutation
```

Full Chromium acceptance remains a separate reusable workflow and proves genuine backend/frontend/PostgreSQL execution, SSE reconnect/catch-up, post-runtime evaluation, action confirmation/follow-run, tenant isolation, safe browser projections and responsive product behavior.

The historical final-delivery reproduction workflow remains immutable evidence and is intentionally distinct from the current-product reproduction contract.

## 11. External blockers / explicit bounded state

### Branch protection

Repository CI is branch-protection-ready, but enforcement remains external. Last observed state on 2026-09-04:

```text
main.protected = false
repository rulesets = []
```

Required settings and verification procedure are documented in `docs/BRANCH-PROTECTION.md`.

### Historical C4 exact artifact

The required evaluator-side artifact with SHA-256
`b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`
remains externally unavailable. Reconstruction, substitution or rescoring is forbidden. The blocker remains visible in final handoff and does not become resolved because current product CI is green.

## 12. Critical path to delivery

```text
1. merge final freeze/evidence bundle candidate       CURRENT P0
2. 2026-09-05 integrated test/fix only                scheduled
3. hard feature/visual/architecture freeze            end 2026-09-05
4. apply + verify GitHub branch protection            external control
5. final rehearsal/evidence inspection                2026-09-06/07
6. delivery                                           2026-09-08
```

Human semantic/value collection can proceed when reviewers/operators are available, but absent real data the final delivery must preserve `NOT READY` rather than manufacture a claim.

P1 work — LangGraph comparison, additional provider/model benchmark, adaptive routing, OpenTelemetry standardization or frontend consolidation — must not displace the final P0 freeze/rehearsal path and requires measured materiality.

## 13. Current non-claims

Do not claim:

- a production provider has been selected;
- human semantic calibration is complete;
- engineer minutes saved without real human observations;
- adaptive stopping improves runtime behavior before an oracle-free challenger wins;
- CI load measurements establish production capacity/SLOs;
- restart safety establishes deployment RTO/RPO, HA, multi-region failover or uptime;
- enterprise IAM/SSO is implemented;
- LangGraph or another framework is needed/superior before a controlled comparison;
- GitHub branch protection is enforced before GitHub reports it active;
- RAG/GraphRAG/vector DB/Kubernetes/Kafka/Redis/multi-agent/Temporal/MCP migration is justified without a measured gap and challenger win.

## 14. State update rule

This file is the mutable current-state summary. Accepted changes update it. Historical ADRs, frozen experiment evidence, prior campaign artifacts and the historical delivery reproduction workflow remain immutable and authoritative for their original scopes.
