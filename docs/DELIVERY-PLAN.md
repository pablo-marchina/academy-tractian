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
+ trustworthy evaluation
+ usable task-driven frontend
+ quantitative production/security/value evidence
+ USD0 actual project cash cost
```

## Phase 0 — Release 0 vertical slice — DONE

Original minimum promotion passed on backend `082d6f115c070fdc898df749b4b3018efd9ceeab`, workflow `hosted-production-release0-agent`, run `34069562818`.

That immutable acceptance proved:

- Railway public product;
- Neon PostgreSQL;
- managed IAM + tenant negatives;
- provisional hosted Cloudflare provider;
- real typed TRACTIAN read path;
- provider → controller → evidence → terminal → evaluator;
- safe terminal states;
- persistence + SSE;
- 18-operation capability surface;
- external actions disabled;
- USD0/no-paid-spillover/no-local-dependency.

## Phase 1 — Production live hardening — DONE FOR DISCOVERED BLOCKERS

Current backend/runtime: `08866da60245f58f217981b7ae668b10be45cc67` (V13).

Live prompting on 2026-09-07 found and prospectively fixed:

- discoverable-ID requests;
- nested asset/analysis ID parsing gaps;
- redundant post-fleet `get_asset` loops;
- premature terminal before condition evidence;
- ambiguous `response_mode` semantics;
- managed-session fan-out causing `managed_session_unavailable`;
- explicit asset-label grounding/comparison gaps;
- repeated completed single-asset data-quality reads.

Final V13 retests passed the targeted behaviors. See [`progress/2026-09-07-release0-live-hardening-v13.md`](progress/2026-09-07-release0-live-hardening-v13.md).

### Guardrail from the retests

Do not optimize tool count by tool name alone. Asset-level → `point_id` RMS/spectrum calls can be legitimate drill-down. Exact-duplicate metrics must include normalized arguments/resource target and evidence contribution.

## Phase 2 — Task-driven first-user UX — DONE / PILOT EVIDENCE NEXT

Current hosted frontend: `1bc124a8d4dbd029178ff8129b25452129445de7`.

Completed:

- [x] task-first global navigation: Home / Analyses / Technical;
- [x] single primary natural-language entry on Home;
- [x] human-readable progress;
- [x] customer-first result + next step;
- [x] contextual evidence instead of permanent evidence-first navigation;
- [x] persisted analysis history;
- [x] Technical sections for analysis/quality/data/system/actions/studies;
- [x] managed-auth unavailable/invalid recovery states;
- [x] full engineering observability retained;
- [x] frontend/Playwright/required regression green before promotion.

Next UX evidence:

- lightweight ordinary run feedback isolated from controlled research datasets;
- first-time-user task completion/friction measurement;
- accessibility/responsive regression on the current task-driven navigation.

## Phase 3 — Broad live prompt/API coverage — ACTIVE P1

The current live evidence is strong for several asset/condition/data-quality paths, but it does **not** yet prove all 13 read operations or all semantic failure modes.

Priority live matrix:

1. identity/company/fleet context;
2. valid two-asset comparison using **two assets actually present in the same authorized fleet**;
3. `list_analyses` + `get_analysis`;
4. RMS asset→point drill-down;
5. spectrum asset→point drill-down;
6. baseline comparison;
7. data quality + condition trust;
8. `get_model` when a structured model ID is exposed;
9. `search_knowledge` → `get_knowledge_doc` with exact observed doc ID;
10. unavailable/missing-resource behavior;
11. conflict/inconclusive/partial/complete response-mode semantics;
12. anti-hallucination and false-precision prompts;
13. action/prompt-injection challenges with zero action execution.

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
safe action refusal rate
```

### Automation boundary

`POST /api/runs` requires the real managed browser session. Do not bypass auth merely to automate a prompt battery. The existing `hosted-pilot` Railway service is a preflight process, not a second live agent runtime. If fully automated hosted prompt execution is needed, create a separately authorized test-harness identity/session path that preserves the same production trust boundary and is explicitly scoped as test infrastructure.

## Phase 4 — Final provider decision — PENDING

Execute frozen Provider Tournament v3 exactly as preregistered:

```text
17 scenarios × 5 repetitions × 2 candidates = 170 attempts
```

Release 0 Cloudflare qualification is not proof of final superiority. Output remains evidence-backed selection or `NO_SELECTION`.

## Phase 5 — Security, capacity and recovery — PENDING

Order:

1. full hosted SECURITY-V1 campaign;
2. remote auth/session burst and concurrent-user coverage;
3. load staircase to measured saturation/quota boundary;
4. derive SLO from observed distributions/product need;
5. provider/TRACTIAN/DB/backend/SSE failure campaign;
6. real backup/export/restore drill;
7. measured RTO/RPO only if supported.

No paid feature may be enabled to manufacture a stronger claim.

## Phase 6 — Governed consequential actions — DISABLED / FUTURE GATE

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
```

Hard failure: platform-caused duplicate external side effect.

Release 0 remains deny-all for external action execution.

## Phase 7 — Human semantic calibration and operational value — PENDING

### Semantic calibration

Use blinded real human labels/adjudication before any semantic LLM judge becomes gating. Include agreement/error analysis and a calibrated confidence vocabulary.

The live R310 causal run is a useful future calibration example: the response mode was correctly `partial`, but wording such as “grau de certeza alto” should be judged against a defined evidence-based rubric before being treated as calibrated.

### Operational value

Compare equivalent cases:

```text
MANUAL vs AGENT-ASSISTED
```

Primary candidate KPI: time to correct operational decision. Do not claim time saved before real observations exist.

## Phase 8 — Adaptive challengers — DEFERRED

Only after a measured bottleneck may adaptive depth/tool ordering/stopping/provider routing compete. Auth, tenant scope, RLS, schemas, action custody/confirmation/idempotency/leases, evaluator isolation and cost caps remain deterministic.

## Phase 9 — Final evidence freeze — LAST

Freeze/link:

- exact production component identities;
- USD0 evidence;
- TAPI coverage;
- IAM/RLS/security;
- provider decision;
- TRACTIAN behavior/read coverage;
- mode/grounding/evaluation results;
- load/SLO and recovery/restore evidence;
- action state/limitations;
- human/value evidence or explicit non-claim;
- current task-driven UX evidence;
- runbooks, changelog and reversal triggers.

## Priority rule until delivery

```text
P0 safety/broken production/correctness
→ P1 live read/grounding/semantic coverage
→ final hard-gate evidence
→ documentation/presentation integration
→ optional polish
```

A late change that cannot be retested does not silently enter the release.