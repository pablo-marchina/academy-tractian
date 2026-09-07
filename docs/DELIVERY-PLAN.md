# Academy × TRACTIAN — Delivery Plan

**Status:** ACTIVE execution plan  
**Last rebaseline:** 2026-09-06 BRT  
**Delivery target:** 2026-09-08  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Final DoD:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This plan is dependency-ordered. It separates the **already promoted Release 0** from the remaining work required for the strongest defensible final delivery.

## North Star

```text
real remote multi-user product
+ real TRACTIAN evidence
+ safe agent behavior
+ trustworthy evaluation
+ complete user/reviewer observability
+ quantitative production/security/value evidence
+ USD0 actual project cash cost
```

## Phase 0 — Release 0 vertical slice — DONE

All minimum first-user release gates passed:

- Railway public product;
- Neon PostgreSQL;
- managed IAM + tenant negatives;
- provisional hosted Cloudflare provider;
- real typed TRACTIAN reads;
- genuine provider → controller → evidence → terminal → evaluator path;
- FINAL/CLARIFY/ABSTAIN/ESCALATE;
- persistence + SSE;
- 18-operation capability surface;
- external actions disabled;
- USD0/no-paid-spillover/no-local-dependency.

Evidence anchor: backend/runtime `082d6f115c070fdc898df749b4b3018efd9ceeab`; hosted acceptance run `34069562818`.

## Phase 1 — First-user UX pilot — IN PROGRESS

### Completed

- [x] first-run product orientation;
- [x] guided investigations before capability catalog;
- [x] safe starter examples when server manifest is unavailable;
- [x] human-readable progress stages;
- [x] customer-first outcome and next step;
- [x] mode-specific FINAL/CLARIFY/ABSTAIN/ESCALATE recovery;
- [x] compact evidence summary;
- [x] four-level progressive disclosure: Results / Evidence / Investigation / Engineering;
- [x] keyboard-accessible depth tabs;
- [x] full engineering observability preserved;
- [x] Playwright/clean-clone/required CI green on UX baseline `2ca6215...`;
- [x] frontend baseline `2ca6215...` hosted successfully on Railway.

### Next

#### UX-06 — lightweight run feedback

Create a separate, minimal, tenant-scoped feedback path for ordinary users. Do **not** write casual feedback into the controlled semantic-review or operational-value datasets.

Measure at minimum:

- helpful / not helpful;
- reason category where negative;
- optional short note;
- run ID + safe release/UX identity;
- completion/abandonment rate;
- no raw secret payload or hidden reasoning.

#### UX-07 — first-time-user pilot

Test with users who did not build the system. Capture:

- time to first valid request;
- task completion rate;
- confusion/error rate by layer;
- mode comprehension;
- evidence comprehension;
- feedback rate;
- qualitative notes only as complement to measured friction.

Prioritize P0/P1 defects before visual polish.

## Phase 2 — Final provider decision — PENDING

Execute the frozen Provider Tournament v3 exactly as preregistered:

```text
17 scenarios × 5 repetitions × 2 candidates = 170 attempts
```

Do not use Release 0 provisional qualification as proof of final superiority. Preserve hard gates for USD0, route/model identity, safety, gold isolation and structured validity.

Output: evidence-backed provider selection or `NO_SELECTION`.

## Phase 3 — Security, capacity and recovery — PENDING

Order:

1. full hosted SECURITY-V1 campaign;
2. remote load staircase to measured saturation/quota boundary;
3. derive SLO only from observed distributions and product need;
4. backend/provider/TRACTIAN/DB/SSE/reconnect failure campaign;
5. real backup/export/restore drill;
6. measured RTO/RPO only if evidence supports the claim.

No paid feature may be enabled to manufacture a stronger claim.

## Phase 4 — Governed consequential actions — DISABLED / FUTURE GATE

Only after IAM/provider/TRACTIAN/security evidence is adequate:

```text
action proposal
→ deterministic validation
→ private custody
→ explicit opaque-ID confirmation
→ fresh authorization + kill switch
→ persistent idempotency
→ non-transferable lease/fencing
→ one exact remote attempt
→ SUCCEEDED | FAILED | UNCERTAIN
→ distinct trace/evaluation
```

Hard failure: platform-caused duplicate external side effect.

Release 0 continues deny-all external action execution until this phase is explicitly promoted.

## Phase 5 — Human semantic calibration and operational value — PENDING

### Semantic calibration

Use blinded real human labels/adjudication before any semantic LLM judge becomes gating. Report confusion/error analysis and agreement metrics.

### Operational value

Compare equivalent cases:

```text
MANUAL vs AGENT-ASSISTED
```

Primary candidate KPI: time to correct operational decision. Do not claim time saved before real observations exist.

## Phase 6 — Adaptive challengers — DEFERRED

Only after the static production baseline produces a measured bottleneck may adaptive depth/tool ordering/stopping/provider routing compete.

Auth, tenant scope, RLS, permissions, schemas, action custody/confirmation/idempotency/leases, evaluator isolation and cost caps remain deterministic.

## Phase 7 — Final evidence freeze — LAST

Freeze/link:

- exact production URLs and identities;
- USD0 evidence;
- TAPI coverage;
- IAM/RLS/security;
- provider decision;
- TRACTIAN behavior;
- mode/grounding/evaluation results;
- load/SLO and recovery/restore evidence;
- action state/limitations;
- human/value evidence or explicit non-claim;
- Control Room UX evidence;
- runbooks, changelog and reversal triggers.

## Priority rule until delivery

```text
P0 safety/broken production/correctness
→ P1 evidence/mode/user friction
→ final hard-gate evidence
→ documentation/presentation integration
→ optional polish
```

A late change that cannot be retested does not silently enter the release.