# Academy × TRACTIAN — Final Delivery Acceptance

**Status:** ACTIVE final-project Definition of Done  
**Last rebaseline:** 2026-09-08 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Current progress record:** [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md)  
**Original Release 0 acceptance:** [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md)

This document answers: **what must be demonstrably true before the complete project may be called finished?** Current production is live and materially beyond the original read-only V13 release, but the deployed OpenRouter V14 provider migration currently fails the authenticated functional gate.

## 1. Current final-acceptance ledger

| Area | Current state | Final claim boundary |
|---|---|---|
| remote HTTPS product | **PASS** | Railway public frontend/API |
| backend exact identity | **PASS deployment** | `5611687556...`, deployment `542bf459...` |
| frontend exact identity | **PASS deployment** | `436436426...`, deployment `8375d735...` |
| supplied TRACTIAN API | **PASS hosted** | `47561c117...` |
| USD0 + no paid spillover | **PASS policy** | must remain true through final evidence |
| no local/mock production dependency | **PASS** | hosted path only |
| managed browser IAM | **PASS tested scope** | real sign-in/session/protected run creation |
| Neon PostgreSQL/RLS | **PASS tested scope** | final capacity/recovery evidence still open |
| OpenRouter V14 configuration | **PASS provisional** | exact fixed-free model/route, no fallback |
| OpenRouter authenticated functional E2E | **FAIL** | B204 matrix 0/3; `finish_reason=length` |
| TRACTIAN reads under current V14 campaign | **NOT REACHED** | first provider decision failed |
| typed TRACTIAN read contract | **PASS contract / historical sampled live evidence** | final all-read campaign open |
| independent verification | **PASS tested scope** | claim-bounded structural/evidence verification promoted |
| exact duplicate-success suppression | **PASS implementation/regressions** | same-tool/different-args drill-down preserved |
| governed action transport | **PASS 5/5 controlled production smoke** | end-user/security action campaign still open |
| final action safety/adversarial acceptance | **PENDING** | full hosted SECURITY-V1 required |
| 18-operation contract | **PASS contract** | 13 reads + 5 actions |
| task-driven UX | **PASS hosted** | ordinary-user measurement still open |
| broad 13-read live coverage | **PENDING** | no complete coverage claim yet |
| final provider tournament/selection | **NO_SELECTION / PENDING** | only new eligible governed evidence may change it |
| final remote load/capacity/SLO | **PENDING** | no invented capacity/SLO |
| restore/RTO/RPO | **PENDING** | real isolated restore drill required |
| semantic human calibration | **PENDING** | semantic judge non-gating until then |
| operational-value experiment | **PENDING** | no engineer-time-saved claim |
| branch protection enforcement | **FAIL / external control pending** | latest `main.protected=false` |
| production SHA == accepted final SHA | **NO** | functional-closure branch ahead of production |
| final immutable evidence freeze | **PENDING** | only after applicable hard gates close |

## 2. Non-negotiable acceptance rule

Applicable final claims must preserve simultaneously:

```text
actual project cash cost = USD 0
+ no automatic paid spillover
+ real remote serving
+ tenant-safe multi-user identity/state
+ real TRACTIAN integration
+ grounded safe agent behavior
+ trustworthy evaluation
+ observable/reproducible evidence
+ deterministic authority/safety boundaries
+ exact release provenance
+ claim-specific production/security/value proof
```

When evidence is absent or blocked, use `FAIL`, `NOT REACHED`, `PENDING`, `NOT READY`, `INCONCLUSIVE` or `NO_SELECTION`. Never infer a pass from architecture or configuration alone.

## 3. TAPI acceptance

The integrated product must demonstrate both updated TAPI tracks in one solution:

1. **Industrial Agent** — contextualize, investigate and execute/escalate through typed TRACTIAN operations with safe operational outcomes.
2. **Agent Evaluation Framework** — evaluate function/tool selection, arguments, trajectory, evidence, response, safety, failure, stability and high-impact actions with reproducible provenance.

Every final claim must be tied to actual API integration, an explicit experiment/campaign or deterministic test, and documented results/limitations.

## 4. Current OpenRouter V14 acceptance gate

Configuration/preflight is not functional acceptance. V14 is accepted only when an exact production candidate proves:

```text
real managed login/session
→ POST /api/runs
→ exact provider/model/route provenance
→ valid typed OpenRouter decision (`finish_reason=stop`)
→ AgentController
→ real HarnessRunner TRACTIAN calls
→ grounded evidence
→ valid terminal + response_mode
→ deterministic post-runtime evaluation
→ durable safe projection
```

The current B204 runs are:

```text
run_437a59ba893a96e3f902  F01 condition
run_86c832ce46189200b613  F02 causal
run_f081d5d45b0cf4caf4b3  F03 data quality
```

All currently fail with `DECISION_SOURCE_FAILURE` and zero tool calls. A safe probe observed the exact pinned model and HTTP 200 but `finish_reason=length`. Therefore the adapter is correctly failing closed on incomplete output.

The subsequent bounded length/reasoning experiment received HTTP 429 for every tested variant. No fix is accepted until the comparison can be rerun under eligible provider conditions and wins without violating hard gates.

Forbidden shortcuts include accepting truncated output, enabling paid/model fallback, silent provider/model substitution, blind schema removal and unbounded retry.

## 5. Agent / grounding / evidence acceptance

Before a behavior class is complete, prove as applicable:

- typed tool selection and argument correctness;
- internal IDs originate only from authorized structured observations;
- human asset labels resolve through authenticated fleet discovery;
- discoverable internal IDs are not requested from the customer;
- comparison claims use evidence for every compared resource;
- missing resources fail closed without scope expansion;
- diagnostic answers use condition evidence when required;
- data-quality questions inspect data quality;
- baseline/data quality are not misused as fault proof;
- response modes match evidence/message semantics;
- customer-safe conclusion/clarification/abstention/escalation;
- safe provider/tool/runtime failure behavior;
- evidence lineage/provenance and repeated-run stability where stochasticity matters.

### Non-progress acceptance

Exact successful duplicate calls are forbidden once the same operation + normalized arguments/resource has already contributed the evidence. Same tool with a different point/resource/arguments may remain valid progressive investigation.

## 6. IAM / tenant acceptance

Continue proving:

- managed login/logout/session lifecycle;
- server-owned user/tenant/permission mapping;
- browser cannot assert tenant/privilege;
- independent PostgreSQL RLS boundary;
- cross-user/cross-tenant REST/SSE/storage negatives;
- manipulated/expired session fails closed;
- GET/HEAD cache never stores raw cookie or serves expired stale context;
- POST/non-read uses fresh managed-session validation;
- invalid session 401 vs temporary identity outage 503;
- frontend reconciles session after auth signals/focus/visibility.

Do not claim OAuth/OIDC/enterprise SSO unless actually implemented/tested.

## 7. Governed consequential-action acceptance

The production architecture and controlled transport smoke now exist; final action acceptance is stronger than that smoke.

Required path:

```text
proposal ≠ execution
→ deterministic schema/resource/permission checks
→ private custody
→ explicit opaque-ID confirmation
→ fresh tenant-aware server-owned authorization + kill switch
→ persistent idempotency
→ non-transferable execution lease/fencing
→ server-owned upstream TRACTIAN actor
→ one bounded transport attempt
→ ACCEPTED | NOT_ACCEPTED | BLOCKED | UNCERTAIN
→ action evaluation + safe projection
```

Final campaign must prove, in hosted production or an equivalently governed isolated target as preregistered:

- cross-user/tenant confirmation denied;
- model/browser cannot mint permissions/resource authority/upstream actor identity;
- exact action fingerprint cannot be altered at confirmation;
- stale/lost ownership cannot publish false success;
- ambiguous writes become `UNCERTAIN` and are not auto-retried;
- duplicate confirmation does not produce a second external attempt;
- kill switch blocks new confirmation/execution;
- prompt/tool injection cannot cross deterministic authority boundaries;
- no credential/grant/private custody material reaches browser-safe observability.

The current 5/5 HTTP-200 smoke proves the configured controlled transport path only. Do not claim distributed exactly-once side effects unless the external API participates in compatible idempotency/fencing.

## 8. Evaluation acceptance

Deterministic checks remain authoritative where structural truth exists. Final framework should cover:

- scenario/trace execution;
- tool/function selection and arguments;
- trajectory and stopping;
- evidence completeness/provenance;
- terminal/response-mode correctness;
- action/safety behavior;
- failure/degraded paths;
- repeated-run stability;
- evaluator/runtime isolation;
- exact provider/model/route/release identity;
- independent verification of claims and evaluator behavior.

Private benchmark/gold/adjudication truth must never enter runtime/model context.

## 9. Human semantic calibration

No semantic judge becomes a hard gate until real blinded human labels establish reliability. Required evidence includes rubric, independent labels, adjudication, inter-rater agreement, confusion/error analysis and justified precision/recall/F1 or equivalent metrics.

Confidence/causal wording must be calibrated rather than treated as reliable because it sounds plausible.

## 10. Eval-Driven Development

Material challengers follow:

```text
measured requirement/gap
→ eligibility hard gates
→ metric/evaluator
→ frozen baseline
→ preregistered candidate
→ controlled implementation
→ repeated/sliced comparison
→ failure + uncertainty analysis
→ PROMOTE | REJECT | INCONCLUSIVE | NO_CHANGE | NO_SELECTION
→ regression guard
```

Hard gates include USD0, no paid spillover, zero credential/gold leakage, zero unauthorized action and zero tenant escape.

The current OpenRouter length-fix work is correctly `INCONCLUSIVE` after HTTP 429; it must not be promoted from intuition.

## 11. Production hardening acceptance

Final production claims require hosted evidence for:

- broad canonical read coverage;
- auth/session/concurrent-user stress;
- load staircase and short soak with success/error, p50/p95/p99, provider/DB/auth/TRACTIAN/SSE contribution, pool/quota/saturation;
- capacity and SLO derived only after measurement;
- provider/TRACTIAN/DB/backend/SSE failure campaigns;
- known-state backup/export + isolated restore + integrity/app smoke;
- measured RTO/RPO only;
- full current-topology SECURITY-V1;
- external uptime monitoring separate from deployment-time health checks where required by the final operational claim.

Do not enable paid infrastructure merely to manufacture a stronger claim under the USD0 project rule.

## 12. Operational value acceptance

Compare equivalent industrial tasks under `MANUAL` vs `AGENT-ASSISTED` conditions. Measure at least time to correct decision/completion, correctness, missing information, human steps and specialist escalation. No time-saved/productivity claim without real observations.

## 13. UX / observability acceptance

A first-time user must be able to sign in, ask a normal equipment question, understand live progress, interpret result/uncertainty, see next action, inspect supporting evidence and reopen persisted analyses without needing internal IDs or technical internals.

A technical reviewer must additionally inspect safe tool/policy/evidence transitions, trace topology, evaluator/verification output, architecture/capability state, action mode and exact release/provider provenance. Do not expose secrets, private gold, grant material or hidden reasoning.

## 14. Final exact-SHA rule

Before final freeze:

```text
required CI on candidate SHA = PASS
production deploy SHA        = candidate SHA
release identity endpoint    = candidate SHA
hosted functional campaign   = PASS
security/acceptance evidence = linked to candidate/topology
frontend/supplied API SHAs   = explicitly recorded
```

Source/PR success alone does not authorize a production claim.

## 15. Final acceptance decision

The project is final only when every applicable hard row is `PASS` or explicitly documented as an accepted limitation/non-goal consistent with the assignment. Historical Release 0/V13 evidence remains immutable and additive; current failures are not retroactively hidden.