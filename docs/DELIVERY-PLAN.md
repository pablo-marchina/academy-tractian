# Academy × TRACTIAN — Delivery Plan

**Status:** ACTIVE execution plan  
**Last rebaseline:** 2026-09-08 BRT  
**Delivery target:** 2026-09-08  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Final DoD:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Current progress record:** [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md)

This plan is dependency-ordered. The highest-value work is no longer broad feature development; it is closing the exact hosted acceptance/evidence gaps on the current architecture without weakening safety or the USD0 constraint.

## North Star

```text
real remote multi-user product
+ real TRACTIAN evidence/actions
+ safe grounded agent behavior
+ trustworthy independent evaluation
+ task-driven live frontend
+ quantitative production/security/value evidence
+ exact release provenance
+ USD0 actual project cash cost
```

## Phase 0 — Original hosted Release 0 — DONE / HISTORICAL

Original minimum promotion established the public Railway product, Neon PostgreSQL, managed IAM, tenant negatives, provisional hosted provider, real typed TRACTIAN read path, evidence/terminal/evaluator persistence and SSE under a read-only boundary.

Do not rewrite that historical evidence to match current production.

## Phase 1 — V13 live grounding/session hardening — DONE / HISTORICAL

Completed through the 2026-09-07 live campaign:

- human asset-label grounding;
- no discoverable-ID request loops;
- nested structured-ID handling;
- condition-evidence and data-quality requirements;
- explicit response-mode semantics;
- managed-session read-burst resilience;
- legitimate asset→point drill-down distinction.

## Phase 2 — Governed actions + verification + duplicate-call invariant — DONE FOR IMPLEMENTED/SMOKED SCOPE

2026-09-08 progress:

- [x] server-owned upstream TRACTIAN action actor architecture;
- [x] five canonical actions executable under governed confirmation configuration;
- [x] controlled production pre-deploy smoke 5/5 accepted HTTP 200;
- [x] no credentials/resource IDs/user IDs/response bodies recorded by the smoke;
- [x] independent verification V1 / claim-bounded verification surfaces;
- [x] preserve ordinary authenticated read access for users without action grants;
- [x] exact-success duplicate-call suppression independent of provider;
- [x] preserve same-tool/different-arguments progressive drill-down.

Still open: full end-user/adversarial action SECURITY-V1 and broader semantic action evaluation.

## Phase 3 — OpenRouter V14 migration — DEPLOYED / FUNCTIONAL GATE FAILING

Production backend `5611687556b3d50c31f20fa85ede794f2500f05c` serves V14:

```text
provider = openrouter
model    = nvidia/nemotron-3-super-120b-a12b:free
route    = openrouter.chat_completions.v1.fixed_free
fallback = disabled
cost     = USD0 hard gate
```

### What already passes

- [x] production deploy success;
- [x] exact release identity;
- [x] managed authentication/session;
- [x] protected run submission;
- [x] provider request accepted at least once with HTTP 200;
- [x] exact pinned model observed in sanitized provider response;
- [x] no raw provider request/response or credentials recorded;
- [x] adapter fails closed on invalid/truncated completion.

### Current blocker

B204 authenticated functional matrix:

```text
F01 condition      run_437a59ba893a96e3f902  FAIL
F02 causal         run_86c832ce46189200b613  FAIL
F03 data quality   run_f081d5d45b0cf4caf4b3  FAIL
```

All three stop before the first TRACTIAN call with `DECISION_SOURCE_FAILURE`.

Sanitized first-call probe:

```text
HTTP 200
exact model served
assistant content present
finish_reason = length
```

A bounded length/reasoning experiment then received HTTP 429 for every variant, so no change is promoted.

## Phase 4 — Immediate P0: close V14 functional acceptance

Do in this exact dependency order:

1. **Measure OpenRouter key-tier/rate-limit state safely.** Use the dedicated safe probe; record no secret or raw provider material.
2. **Wait/retry only under a bounded experimental protocol** when provider eligibility allows; do not introduce runtime retry as a hidden workaround.
3. **Reproduce `finish_reason=length`.** Keep the exact production schema/tool visibility and provider/model pin.
4. **Compare bounded candidates.** Examples already instrumented: current budget, explicit reasoning minimization/exclusion if supported, larger bounded completion budget. Preserve `allow_fallbacks=false`, `require_parameters=true`, strict schema, exact free-model pin and USD0.
5. **Promote only a measured winner.** If all candidates remain unavailable/inconclusive, keep `INCONCLUSIVE` rather than modifying the runtime from intuition.
6. **Add/retain regression tests** for the exact adapter contract and prior V13 semantics.
7. **Run required CI on the exact candidate SHA.**
8. **Deploy exactly that SHA** to `production-api`.
9. **Verify release identity** before user-facing functional testing.
10. **Rerun B204 F01/F02/F03 through real managed authentication.**
11. Require **3/3 PASS** with OpenRouter provenance, real TRACTIAN tool calls, grounded terminal/response mode and persisted evaluation.
12. Only then mark the provider migration functionally accepted and remove PR #222 draft status/merge block.

Explicitly forbidden as shortcuts:

- accepting `finish_reason=length`;
- paid/model/provider fallback;
- silent model substitution;
- disabling structured-output validation without a controlled challenger;
- unbounded retries;
- bypassing managed authentication;
- marking configuration/preflight as functional success.

## Phase 5 — Broad live read/trajectory coverage — NEXT AFTER V14 GREEN

Once V14 is 3/3, execute the canonical read/behavior matrix on the exact accepted production SHA.

Priority surface:

1. identity/company/fleet context;
2. two-asset same-fleet comparison;
3. analyses list/detail;
4. RMS asset→point drill-down;
5. spectrum asset→point drill-down;
6. baseline comparison;
7. data quality + condition trust;
8. model detail with observed model ID;
9. knowledge search → document detail with observed ID;
10. unavailable/missing-resource behavior;
11. complete/partial/inconclusive/conflict/unavailable semantics;
12. anti-hallucination/false-precision prompts;
13. provider/TRACTIAN malformed/failure paths.

Measure at minimum:

```text
read coverage / 13
HTTP/tool success rate
tool calls / run
exact duplicate-success rate
legitimate drill-down rate
budget exhaustion rate
provider failure rate
unnecessary ID-request rate
terminal correctness
response_mode correctness
unsupported material claim rate
p50/p95/p99 end-to-end and provider/tool latency
```

## Phase 6 — Full governed-action SECURITY-V1 — P0/P1 AFTER V14 GREEN

Now that real governed write transport exists, complete the adversarial campaign rather than describing actions as future-only.

Required scenarios include:

- cross-user confirmation attempt;
- cross-tenant/resource-binding attempt;
- forged permissions/resource authority in browser/model payload;
- altered confirmation arguments/fingerprint;
- duplicate confirmation;
- stale/lost execution lease;
- ambiguous transport → `UNCERTAIN` with no auto-retry;
- kill-switch denial;
- prompt/tool-output injection attempting policy escape;
- credential/grant/private-custody leakage checks;
- exact release/action actor provenance.

Hard failure: platform-caused unauthorized or duplicate external side effect.

## Phase 7 — Capacity, failure and recovery evidence

After the exact functional candidate is stable:

1. auth/session concurrent-user stress;
2. load staircase (for example 1→2→5→10→20→40… until an evidence-based stop); measure throughput, success/errors, p50/p95/p99 and component saturation/quota;
3. short soak at sustainable load;
4. derive capacity/SLO only from the observed distribution and product need;
5. provider/TRACTIAN/DB/backend/SSE degraded/failure campaigns;
6. continuous external availability monitoring if needed for the final operational claim, separate from deploy-time health checks;
7. known-state backup/export + controlled mutation + isolated restore + row/schema/hash/app smoke;
8. record measured RTO/RPO only.

Do not add paid HA/replicas merely to strengthen a claim under the USD0 rule. If the production topology remains single-replica, state that limitation.

## Phase 8 — Human semantic calibration

Use real blinded labels before semantic judges become gating:

- ~30–50 representative outputs if available;
- two independent raters where feasible;
- adjudication;
- agreement statistic (e.g. Cohen κ/Krippendorff α when appropriate);
- confusion/error analysis;
- precision/recall/F1 or task-appropriate metrics;
- explicit confidence/causal-language rubric.

No fabricated labels or agreement statistics.

## Phase 9 — Operational value experiment

Compare equivalent `MANUAL` vs `AGENT-ASSISTED` tasks. Measure time to correct decision/completion, correctness, missing information, human steps and escalation. Keep task/order assignment controlled or randomized where possible.

Candidate primary KPI:

```text
ΔT = T_manual - T_agent
relative reduction = (T_manual - T_agent) / T_manual
```

Report uncertainty/CI when sample size supports it. Do not claim time saved before real observations.

## Phase 10 — Provider/tournament final decision

The current OpenRouter migration is a provisional production route, not final superiority evidence. Frozen historical tournaments remain historical. Any new comparison must use a new preregistered experiment/eligibility packet and respect provider availability/free-tier eligibility.

Output must be evidence-backed selection or explicit `NO_SELECTION`.

## Phase 11 — Branch protection / release governance

Latest observed GitHub state still reports:

```text
main.protected = false
required status-check enforcement = off
```

Apply branch protection/ruleset using the stable required gate if account/repository controls permit it. Verify by reading the branch metadata after configuration. Do not claim enforcement until GitHub reports it.

## Phase 12 — Final evidence freeze — LAST

Freeze only after all applicable hard gates on the exact candidate topology are resolved:

- backend/frontend/supplied-API SHAs and deployment IDs;
- provider/model/route/cost evidence;
- authenticated V14 functional 3/3 evidence;
- canonical read coverage;
- governed-action security evidence;
- IAM/RLS/security;
- evaluation/verification and semantic calibration or explicit limitation;
- capacity/SLO and recovery/restore evidence or bounded non-claim;
- operational value or explicit no-data limitation;
- TAPI coverage;
- runbooks/changelog/presentation;
- branch-protection state;
- final reproduction/required CI;
- rollback/reversal triggers.

## Priority rule until final delivery

```text
P0 broken hosted functionality / safety / tenant / action / cost
→ exact functional acceptance
→ security/read/capacity/recovery hard evidence
→ human semantic/value evidence
→ documentation/presentation freeze
→ optional challengers/polish
```

Do not start a LangGraph/multi-agent/RAG/Redis/Kafka/Kubernetes rewrite to solve the current provider completion/rate-limit blocker. The current architecture remains `NO_CHANGE` unless a measured architectural gap appears.