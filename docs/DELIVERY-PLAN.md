# Academy × TRACTIAN — Delivery Plan

**Status:** ACTIVE execution plan  
**Last rebaseline:** 2026-09-07 BRT  
**Delivery target:** 2026-09-08  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Final DoD:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This plan is dependency-ordered. It separates the already promoted/hardened Release 0 from the remaining evidence required for the strongest defensible final delivery.

## North Star

```text
real remote multi-user product
+ real TRACTIAN evidence
+ safe grounded agent behavior
+ governed consequential actions with explicit confirmation
+ trustworthy evaluation
+ usable task-driven frontend
+ quantitative production/security/value evidence
+ USD0 actual project cash cost
```

## Phase 0 — Release 0 vertical slice — DONE

Original minimum promotion passed on backend `082d6f115c070fdc898df749b4b3018efd9ceeab`, workflow `hosted-production-release0-agent`, run `34069562818`.

That immutable acceptance proved the original read-only Release 0 scope: Railway public product, Neon PostgreSQL, managed IAM + tenant negatives, provisional hosted provider, real typed TRACTIAN reads, controller/evidence/evaluator path, safe terminal states, persistence/SSE, 18-operation capability contract and USD0/no-paid-spillover/no-local dependency.

It is historical evidence and is not rewritten by later governed-action promotion.

## Phase 1 — Production live hardening — DONE FOR DISCOVERED READ/AUTH BLOCKERS

The read orchestration remains V13. Live prompting on 2026-09-07 prospectively fixed discoverable-ID requests, nested ID parsing gaps, redundant reads, premature diagnostic terminal, response-mode ambiguity, managed-session fan-out, explicit asset-label/comparison gaps and repeated completed data-quality reads.

Current merged backend/runtime source after later action work is:

```text
3545d75c00ca30419e0f47e8b1950aa50cbbf462
```

The V13 read behavior remains part of that descendant source.

See [`progress/2026-09-07-release0-live-hardening-v13.md`](progress/2026-09-07-release0-live-hardening-v13.md).

### Guardrail from the retests

Do not optimize tool count by tool name alone. Asset-level → `point_id` RMS/spectrum calls can be legitimate drill-down. Exact-duplicate metrics must include normalized arguments/resource target and evidence contribution.

## Phase 2 — Task-driven first-user UX — PROMOTED / STRUCTURAL SIMPLIFICATION STILL OPEN

Current hosted frontend:

```text
1bc124a8d4dbd029178ff8129b25452129445de7
```

Completed:

- [x] task-first global navigation: Home / Analyses / Technical;
- [x] primary natural-language entry on Home;
- [x] human-readable progress;
- [x] customer-first result + next step;
- [x] contextual evidence instead of evidence as a permanent global destination;
- [x] persisted analysis history;
- [x] Technical sections for analysis/quality/data/system/actions/studies;
- [x] managed-auth unavailable/invalid recovery states;
- [x] full engineering observability retained;
- [x] frontend/Playwright/required regression green before promotion.

The latest user review still finds the frontend visually polluted/difficult to navigate. The stronger design target is now:

> **each screen should have one main question for the user to answer.**

Remaining UX work/evidence:

- reduce cards/panels/borders/eyebrows/statuses/supporting copy visible simultaneously;
- make Evidence contextual from Result, not a competing global navigation concept;
- keep Technical outside the normal flow;
- make History recognition/list based before adding filters/table density;
- aggressively linearize mobile layouts;
- preserve ≥44px targets, keyboard/focus/reduced-motion and semantic accessibility;
- measure first-time-user task completion/friction with real users;
- do not call automated tests human usability validation.

## Phase 3 — Governed consequential actions — ACTIVE P0

This phase advanced materially during this conversation.

### Completed implementation/promotion work

PR #211 merged governed execution support for all five canonical action operations:

```text
merge SHA 1a1e7139bfa0361416120b3f21937c4048b5bb1f
```

The production composition now supports:

```text
action proposal
→ deterministic validation
→ private durable custody
→ explicit confirmation of exact existing action
→ server-owned tenant/resource authorization
→ persistent idempotency
→ non-transferable lease/fencing
→ one exact external attempt
→ ACCEPTED | NOT_ACCEPTED | BLOCKED | UNCERTAIN
```

Canonical permissions:

```text
reprocess_analysis             action_low
request_specialist_analysis    action_low
update_asset_config            action_high
request_retraining             action_high
escalate_case                  escalate
```

Production has booted successfully with the action path enabled and a minimum-scope server-owned grant.

### Auditable live gate

PR #213 added the manual-only five-action production smoke and merged at:

```text
3545d75c00ca30419e0f47e8b1950aa50cbbf462
```

Required-gate run `34164123263` passed the production runtime, action lease/fencing, horizontal runtime, Railway IaC, production image, clean-clone and Chromium product surfaces.

The smoke requires:

```text
5 canonical actions advertised
+ 5 executable actions
+ GOVERNED_CONFIRMATION
+ one real canonical request per action
+ accepted HTTP status
+ accepted=true
```

### Live blocker discovered

A fresh Railway configuration snapshot executed the smoke and correctly failed before promotion:

```text
deployment 5ba36471-776c-4e15-919b-56e2da216b74
update_asset_config -> HTTP 403 / accepted=false
```

The healthy prior deployment remained serving.

Root cause evidence from the immutable supplied TRACTIAN runtime:

- vendor action context is selected by `x-user-id`;
- endpoint permissions are explicit;
- the tested company has different upstream actors for `action_low` and `action_high + escalate`;
- forwarding the local requester ID as the vendor actor cannot satisfy all action families.

### P0 corrective work

Target architecture:

```text
local authenticated product user
→ tenant/resource authorization + custody + confirmation + idempotency + audit

(company_id, required_permission)
→ exactly one server-owned TRACTIAN actor
→ injected only at the final vendor boundary
```

Implementation started on:

```text
fix/server-owned-upstream-action-actors
```

It is not merged or production-proven yet.

### Phase 3 exit criteria

- [ ] finish server-owned upstream actor resolver/transport boundary;
- [ ] reject missing/ambiguous actor mappings;
- [ ] prove browser/model/confirmation payload cannot select/upgrade actor;
- [ ] run focused unit/integration/adversarial tests;
- [ ] pass full required CI;
- [ ] merge exact green head SHA;
- [ ] deploy exact merged SHA with a **fresh Railway snapshot**;
- [ ] pass five-action smoke 5/5 with explicit acceptance;
- [ ] prove failed/uncertain write is never blindly retried;
- [ ] exercise normal product confirmation path and persist/evaluate result;
- [ ] record prospective live evidence.

Do not weaken local authorization to satisfy vendor identity requirements.

## Phase 4 — Broad live prompt/API coverage — ACTIVE P1 AFTER ACTION P0

Current live read evidence is strong for several asset/condition/data-quality paths, but it does **not** prove all 13 read operations or all semantic failure modes.

Priority live matrix:

1. identity/company/fleet context;
2. valid two-asset comparison using two assets actually present in the same authorized fleet;
3. `list_analyses` + `get_analysis`;
4. RMS asset→point drill-down;
5. spectrum asset→point drill-down;
6. baseline comparison;
7. data quality + condition trust;
8. `get_model` when a structured model ID is exposed;
9. `search_knowledge` → `get_knowledge_doc` with exact observed doc ID;
10. unavailable/missing-resource behavior;
11. conflict/inconclusive/partial/complete semantics;
12. anti-hallucination and false-precision prompts;
13. prompt-injection/action challenges that remain inside the governed confirmation boundary.

Measure at minimum:

```text
read-operation coverage / 13
HTTP success rate
tool calls / run
exact duplicate call rate
legitimate drill-down rate
budget exhaustion rate
unnecessary ID request rate
terminal semantic correctness
response_mode semantic correctness
unsupported material claim rate
safe action proposal/refusal rate
```

## Phase 5 — Final provider decision — PENDING

Execute frozen Provider Tournament v3 exactly as preregistered:

```text
17 scenarios × 5 repetitions × 2 candidates = 170 attempts
```

Release 0 Cloudflare qualification is not proof of final superiority. Output remains evidence-backed selection or `NO_SELECTION`.

## Phase 6 — Security, capacity and recovery — PENDING

Order:

1. action-actor confused-deputy/adversarial coverage and 5/5 live acceptance;
2. full hosted SECURITY-V1 campaign;
3. remote auth/session burst and concurrent-user coverage;
4. load staircase to measured saturation/quota boundary;
5. derive SLO from observed distributions/product need;
6. provider/TRACTIAN/DB/backend/SSE/action failure campaign;
7. real backup/export/restore drill;
8. measured RTO/RPO only if supported.

No paid feature may be enabled to manufacture a stronger claim.

## Phase 7 — Human semantic calibration and operational value — PENDING

Use blinded real human labels/adjudication before any semantic LLM judge becomes gating. Include agreement/error analysis and a calibrated confidence vocabulary.

For operational value, compare equivalent cases:

```text
MANUAL vs AGENT-ASSISTED
```

Primary candidate KPI: time to correct operational decision. Do not claim time saved before real observations exist.

## Phase 8 — Adaptive challengers — DEFERRED

Only after a measured bottleneck may adaptive depth/tool ordering/stopping/provider routing compete. Auth, tenant scope, RLS, schemas, action custody/confirmation/idempotency/leases, vendor actor mapping and cost caps remain deterministic.

## Phase 9 — Final evidence freeze — LAST

Freeze/link:

- exact production component identities;
- USD0 evidence;
- TAPI coverage;
- IAM/RLS/security;
- provider decision;
- TRACTIAN read coverage;
- mode/grounding/evaluation results;
- governed action safety + final 5/5 live state or explicit limitation;
- load/SLO and recovery/restore evidence;
- human semantic/usability/value evidence or explicit non-claim;
- current UX evidence;
- runbooks, changelog and reversal triggers.

## Priority rule until delivery

```text
P0 safety/broken production/correctness
→ P0 upstream actor routing + 5/5 action validation
→ P1 live read/grounding/semantic coverage
→ final hard-gate evidence
→ documentation/presentation integration
→ optional polish
```

A late change that cannot be retested does not silently enter the release.

See [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md) for the current dated action/deployment evidence.