# 2026-09-08 — Governed Actions, Verification V1, OpenRouter V14 and Functional Acceptance

**Status:** append-only progress/evidence note  
**Recorded:** 2026-09-08 BRT  
**Production backend at this checkpoint:** `5611687556b3d50c31f20fa85ede794f2500f05c`  
**Production frontend at this checkpoint:** `4364364266c6a88d4affd85cb3a734c774cd42c8`  
**Supplied TRACTIAN API:** `47561c1175181b508139e23e6e39b555c1347d57`  
**Functional-closure PR:** #222, `fix/functional-acceptance-closure`  
**PR head when this note was synchronized:** `37438aa97d49d948a877fb2a433021f7fe2df632`

This note preserves the material production, verification and provider work completed on 2026-09-08. It does not rewrite older Release 0/V13 evidence. Current mutable truth remains in `docs/ACTIVE-PROJECT-STATUS.md`.

## 1. Executive state

The project advanced materially beyond the 2026-09-07 read-only V13 snapshot:

1. governed TRACTIAN writes were wired through server-owned upstream action actors and all five canonical actions passed a production pre-deploy smoke;
2. full-system independent verification V1 and claim-bounded verification surfaces were promoted;
3. normal authenticated read access was preserved for users without consequential-action grants;
4. exact duplicate successful direct measurements became a provider-independent non-progress invariant while same-tool/different-argument drill-down remains allowed;
5. production provider composition was migrated from the provisional Cloudflare route to a fixed-free OpenRouter V14 route;
6. a real authenticated B204 functional campaign traversed managed auth and production run execution but failed before the first TRACTIAN tool because the OpenRouter response ended with `finish_reason=length`;
7. bounded follow-up experiments were added without weakening the USD0, model-pinning, schema, provenance or no-fallback gates.

The current release is therefore **live and production-hosted, but the OpenRouter V14 provider migration is not yet functionally accepted**.

## 2. Production component ledger

| Component | Hosted state | Exact identity / evidence |
|---|---|---|
| public product | `PASS` | Railway HTTPS frontend/API |
| production API | `SUCCESS` | deployment `542bf459-353d-432c-b2ff-b862cedf1574`, SHA `5611687556b3d50c31f20fa85ede794f2500f05c` |
| production frontend | `SUCCESS` | deployment `8375d735-539c-46af-b299-9ee4aca8e505`, SHA `4364364266c6a88d4affd85cb3a734c774cd42c8` |
| supplied TRACTIAN API | `SUCCESS` | deployment `d5593f37-64ec-442f-a168-d82490e58dbb`, SHA `47561c1175181b508139e23e6e39b555c1347d57` |
| managed authentication | `PASS` for tested campaign | real email sign-in, managed cookie/session and protected run requests |
| PostgreSQL/RLS serving | active | server-owned tenant context + durable product/evidence/evaluation state |
| provider | live / provisional | OpenRouter V14 fixed-free route |
| TRACTIAN reads | configured | not reached in the failing V14 B204 campaign because the initial model decision failed |
| governed writes | enabled architecture + production smoke `PASS` | 5/5 canonical action transports accepted in governed-write pre-deploy smoke |
| local production dependency | zero | hosted path only |
| paid spillover | forbidden | USD0 hard gate; no automatic paid fallback |

Component identities are independent. A backend provider promotion does not imply a frontend or supplied-API redeploy.

## 3. Governed consequential actions — promoted transport boundary

Production SHA `d43644d22df8e3ee5bb5a1532bbea3512c3a7ac0` introduced server-owned TRACTIAN action actors and a strict separation between local product authorization and provider-side action identity. That architecture remains part of the current production descendant.

The production pre-deploy governed-write smoke reported:

```text
mode                         GOVERNED_CONFIRMATION
actions                      5
executable_actions           5
governed_action_path_enabled true
status                       PASS
```

All five canonical action calls were accepted by the supplied TRACTIAN boundary with HTTP 200 in the controlled smoke:

```text
reprocess_analysis            accepted
request_specialist_analysis  accepted
update_asset_config          accepted
request_retraining           accepted
escalate_case                accepted
```

The smoke intentionally recorded no credentials, resource IDs, local/upstream user IDs or response bodies.

### Current action authority model

```text
model/browser proposal
→ deterministic ToolSpec/schema/resource checks
→ server-owned authenticated user/organization context
→ server-owned action authorization grant
→ private custody + opaque confirmation
→ fresh tenant-aware authorization + kill switch
→ persistent idempotency claim
→ non-transferable action execution lease/fencing
→ server-owned upstream TRACTIAN actor
→ one bounded external attempt
→ ACCEPTED | NOT_ACCEPTED | BLOCKED | UNCERTAIN
→ action evaluation + safe observability
```

The browser/model never owns canonical permissions, tenant/company authority, TRACTIAN credentials, upstream actor identity, confirmation fingerprints or idempotency material.

### Claim boundary

The 5/5 production smoke proves the **configured governed transport path** for the controlled bindings used by the smoke. It does not by itself close the final end-user action security campaign, broad adversarial coverage, or a distributed exactly-once external-side-effect claim.

## 4. Independent verification V1 and runtime hardening

The 2026-09-08 production sequence also promoted:

- claim-bounded independent verification and Verification UX;
- independent functional/evidence oracles and evaluator meta-evaluation;
- supply-chain/release identity auditing;
- strict read-capable fallback for ordinary authenticated users without action grants;
- provider-independent prevention of an exact successful read executing twice in one run;
- preservation of legitimate same-tool/different-argument progressive drill-down.

This distinction is now a runtime/evaluation invariant:

```text
same tool + same normalized arguments/resource + already successful
→ suppress as non-progress duplicate

same tool + different normalized arguments/resource
→ may remain valid progressive investigation
```

## 5. OpenRouter V14 production provider

Production backend `5611687556b3d50c31f20fa85ede794f2500f05c` switched the serving factory to V14.

Current exact provider contract:

```text
provider_id   openrouter
model_id      nvidia/nemotron-3-super-120b-a12b:free
route_id      openrouter.chat_completions.v1.fixed_free
endpoint      https://openrouter.ai/api/v1/chat/completions
```

V14 preserves the accepted V13 grounding/response semantics while changing only the hosted provider adapter.

Hard request/acceptance properties:

- exact `:free` model pin;
- `temperature=0`, `n=1`, non-streaming;
- strict JSON Schema generated from the currently visible tool surface;
- OpenRouter provider fallback explicitly disabled;
- required parameter support enabled;
- no retry, output repair, provider-side tool execution or hidden credential lookup;
- served model, when returned, must match the pin;
- exactly one assistant choice;
- `finish_reason` must equal `stop`;
- provider `tool_calls` / legacy `function_call` are rejected;
- assistant content must be non-empty;
- USD0 hard gate and real TRACTIAN transport are configuration prerequisites.

This keeps authority in `AgentController` + `HarnessRunner`; OpenRouter only proposes the next typed decision.

## 6. Authenticated real B204 functional campaign

The immediate gate was a real managed-session execution through:

```text
managed authentication
→ POST /api/runs
→ production worker/runtime
→ OpenRouter V14 DecisionSource
→ AgentController
→ TRACTIAN tools
→ terminal
→ evaluation
```

Three cases were submitted against the fleet-valid asset label `B204`:

| Case | Run | Result |
|---|---|---|
| F01 explicit asset condition | `run_437a59ba893a96e3f902` | `FAIL` |
| F02 causal investigation | `run_86c832ce46189200b613` | `FAIL` |
| F03 data quality | `run_f081d5d45b0cf4caf4b3` | `FAIL` |

Campaign-level result:

```text
total              3
passed             0
failed             3
all_pass           false
```

Observed common trajectory:

```text
authentication             PASS
release identity           PASS
run submission             PASS (202 Accepted)
execution worker           PASS
OpenRouter DecisionSource  FAIL
TRACTIAN tool calls        0
terminal reason            DECISION_SOURCE_FAILURE
evaluation/trace           failure recorded
```

This localizes the failing gate before the first TRACTIAN read. It is not evidence of a TRACTIAN API, B204 ownership, tenant isolation or tool-transport failure.

## 7. Sanitized root-cause localization

A dedicated safe response-shape probe reproduced the initial V14 request without recording raw request/response or credentials.

Observed response:

```text
http_status       200
served_model      nvidia/nemotron-3-super-120b-a12b:free
choices_count     1
message_role      assistant
content_present   true
finish_reason     length
```

Therefore the original V14 functional failure is currently localized to the provider returning a truncated completion. The adapter correctly rejects it through the fail-closed `finish_reason != stop` path instead of parsing partial model output.

The correct diagnosis is now:

```text
OpenRouter request accepted
→ exact pinned free model served
→ assistant content returned
→ completion exhausted its output budget
→ finish_reason=length
→ V14 rejects incomplete decision
→ DECISION_SOURCE_FAILURE
→ no tool authority granted
```

Do not weaken this gate by accepting truncated JSON or ignoring `finish_reason`.

## 8. Bounded length-fix experiment and 429 state

A preregistered/bounded diagnostic compared:

1. control — 1024 output tokens, default model reasoning behavior;
2. 1024 output tokens with reasoning explicitly minimized/excluded;
3. 4096 output tokens with default reasoning behavior.

The subsequent calls all returned HTTP 429 before a decision payload could be compared. Thus **no length-fix variant has been promoted or demonstrated superior**.

Current result:

```text
control-1024-default-reasoning     HTTP 429
minimize-reasoning-1024            HTTP 429
default-reasoning-4096             HTTP 429
comparative conclusion             INCONCLUSIVE / blocked by provider availability/quota
```

A safe production-key-tier probe was added next so eligibility/rate-limit state can be measured without exposing the key. As of this synchronization, that latest probe had not yet produced a newer QA deployment result.

## 9. Functional-closure PR state

PR #222 remains deliberately draft and must not be merged until hosted functional acceptance is green.

Current work on the branch includes:

- real authenticated functional campaign tooling;
- safe OpenRouter model-call diagnosis;
- initial-call response-shape probe;
- bounded V14 length-fix experiment;
- safe OpenRouter key-tier probe;
- exact-call argument fingerprint observability;
- provider-independent duplicate-success suppression;
- controlled production action/controller/runtime improvements;
- cross-provider tournament infrastructure and eligibility gates;
- corresponding regression tests/workflows.

Current acceptance rule for V14 is not “provider configured”. It is:

```text
real managed auth
+ exact production SHA
+ OpenRouter model provenance
+ valid typed model decision
+ real TRACTIAN tool calls
+ valid grounded terminal
+ persisted post-runtime evaluation
+ no tenant/action/cost/provenance regression
```

The B204 matrix must reach 3/3 before the migration is considered functionally accepted.

## 10. Branch/release governance

The repository has a stable required CI gate, but the latest GitHub branch metadata still reports:

```text
main.protected = false
required status-check enforcement = off
```

This remains a P0 governance gap. CI being green is not equivalent to GitHub preventing direct or unchecked mutation of the branch.

The current production SHA also differs from the functional-closure PR head by design; do not claim `PRODUCTION_SHA == ACCEPTED_SHA` until the final candidate is tested and promoted exactly.

## 11. Current final-gate ledger

| Gate | State at this checkpoint |
|---|---|
| remote product | `PASS` |
| managed multi-user auth | `PASS` tested scope |
| tenant/RLS boundary | `PASS` tested scope |
| no local production dependency | `PASS` |
| USD0/no paid fallback | `PASS` policy / must remain monitored |
| governed action transport | `PASS` 5/5 controlled smoke |
| OpenRouter V14 config/preflight | `PASS` |
| OpenRouter authenticated functional E2E | `FAIL` |
| TRACTIAN tools under V14 B204 campaign | `NOT REACHED` |
| V14 valid terminal/evaluation | `NOT READY` |
| branch protection | `FAIL / external control pending` |
| broad 13-read live coverage | `PENDING` |
| action SECURITY-V1 adversarial campaign | `PENDING` |
| final load staircase/soak/capacity | `PENDING` |
| evidence-derived production SLO | `PENDING` |
| real restore drill + measured RTO/RPO | `PENDING` |
| human semantic calibration | `PENDING` |
| MANUAL vs AGENT-ASSISTED value study | `PENDING` |
| final provider selection/tournament | `NO_SELECTION / PENDING new eligible evidence` |
| final immutable evidence freeze | `PENDING` |

## 12. Immediate next gate

Dependency order:

```text
1. measure OpenRouter key tier / rate-limit eligibility safely
2. reproduce the `finish_reason=length` issue under eligible quota
3. compare only bounded fixes without relaxing model/cost/schema/provenance safety
4. add the winning bounded behavior + regression tests only if evidence supports promotion
5. run required CI on the exact candidate SHA
6. deploy that exact SHA to production
7. verify release identity
8. rerun B204 F01/F02/F03 through the real managed session
9. require real TRACTIAN tool calls and valid terminal/evaluation for 3/3
10. only then close the V14 functional migration gate
```

No fallback to a paid model/provider, silent model substitution, acceptance of `finish_reason=length`, unbounded retry loop or schema bypass is authorized as a shortcut.

## 13. Architecture decision remains NO_CHANGE

The failures observed here are provider-adapter/availability issues, not evidence that orchestration needs a rewrite.

Promoted architecture remains:

```text
FastAPI + managed auth
+ PostgreSQL/RLS/durable runtime state
+ custom AgentController
+ HarnessRunner hard tool boundary
+ typed TRACTIAN transport
+ deterministic safety/evaluation
+ REST/SSE + PostgreSQL durable cursor/LISTEN-NOTIFY wakeup
+ React/TanStack Query/React Flow/ECharts
+ Railway/Neon hosted production
```

LangGraph, multi-agent, RAG/vector DB, persistent memory, MCP, Redis/Kafka/Kubernetes remain `NO_CHANGE` unless a measured gap and controlled challenger demonstrate material advantage.

## 14. Documentation integrity rule

This progress note is additive. Historical date-stamped audits, frozen experiment artifacts, Release 0 acceptance and prior progress notes remain unchanged even where their once-current claims are now obsolete. Mutable owners (`README`, `ACTIVE-PROJECT-STATUS`, `ARCHITECTURE`, `DELIVERY-PLAN`, `DELIVERY-ACCEPTANCE`, `SECURITY-MODEL`, codebase/documentation maps and runbooks) must point to the 2026-09-08 state instead of rewriting history.