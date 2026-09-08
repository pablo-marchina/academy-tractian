# Academy × TRACTIAN — Delivery Plan

**Status:** ACTIVE execution plan  
**Last rebaseline:** 2026-09-08 BRT  
**Delivery target:** 2026-09-08  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Provider state:** [`PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](PROVIDER-QUALIFICATION-STATUS-2026-09-08.md)  
**Final DoD:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This plan is dependency-ordered. Release 0 is already hosted; remaining work maximizes the strongest defensible final claim without retroactively rewriting failed experiments or weakening hard gates.

## North Star

```text
real remote multi-user product
+ real TRACTIAN evidence
+ safe grounded agent behavior
+ trustworthy deterministic-first evaluation
+ usable task-driven frontend
+ provider reliability proven quantitatively
+ claim-specific security/capacity/recovery evidence
+ USD0/no-paid-spillover boundary
```

## Phase 0 — Release 0 vertical slice — DONE

Immutable Release 0 acceptance already proved the hosted minimum: Railway product, managed IAM, Neon PostgreSQL/RLS, provisional hosted provider, typed TRACTIAN reads, provider→controller→evidence→terminal→evaluator flow, persistence/SSE, 18-operation capability surface, external actions disabled and USD0/no-local-production boundary.

## Phase 1 — V13 production live hardening — DONE FOR DISCOVERED BLOCKERS

The 2026-09-07 prompt-driven hardening addressed discoverable-ID requests, nested resource parsing, post-fleet metadata loops, missing condition evidence, response-mode semantics, managed-session fan-out, explicit asset grounding/comparisons and completed data-quality repetition.

See [`progress/2026-09-07-release0-live-hardening-v13.md`](progress/2026-09-07-release0-live-hardening-v13.md).

Guardrail: same-name RMS/spectrum calls are not loops by name alone; compare normalized arguments/resource/evidence contribution.

## Phase 2 — Task-driven first-user UX — DONE / USER EVIDENCE REMAINS

Hosted UX is Home / Analyses / Technical with contextual result/evidence. First-time-user task/friction/accessibility measurement remains useful but is no longer the current blocking engineering path.

## Phase 3 — Final provider path — ACTIVE P0/P1

### 3.1 Paired V4 attempt — CLOSED WITHOUT COMPARATIVE RESULT

V4 prepared Cloudflare and Groq serving paths for GPT-OSS-120B on the same frozen 17×5 population. Cloudflare was quota-blocked during preflight, and the user explicitly removed Cloudflare from the requested path. No paired comparative winner may be claimed.

### 3.2 Groq-only qualification — DONE / FAILED HARD GATES

Groq `openai/gpt-oss-120b` completed the full 85/85 single-provider qualification.

Official result: **`NO_SELECTION`**.

```text
rubric pass       69/85 = 81.18%
reliability       70/85 = 82.35%
contract failures 9
repeat stability  11/17 = 64.71%
p50               1.154 s
p95               2.904 s
```

This run does not authorize production promotion.

### 3.3 Causal failure diagnosis — ACTIVE

Current hypotheses:

- 512 tokens contribute to some finish failures;
- 512 is not the sole cause of invalid payloads;
- 2048 alone does not solve the structural failure class;
- `strict:false` is strongly implicated in relationally invalid decision objects;
- reasoning effort materially changes output size/latency/stability;
- low reasoning is promising but not yet proven superior.

Current planned diagnostic:

```text
7 failure-prone/control scenarios × 3 configs = 21 calls
B0 best-effort / medium / 512
B1 best-effort / medium / 2048
B2 best-effort / low / 2048
```

Partial matrices affected by overlapping Railway deployments or admission throttling are not accepted as a completed 21/21 result.

### 3.4 Rate/admission characterization — ACTIVE prerequisite

Benchmark-shaped 2048-token Groq calls showed 429 behavior not adequately predicted by the earlier emitted-token pacing formula. Before re-running 21/21, measure the provider's effective request-admission behavior with the frozen one-shot diagnostic:

- diagnostic `8cec9f8d7e596bda27a4459ac4130319547d2f5e`;
- bootstrap `0ecc8365f3908f6ddc8521998436a30eee2d5507`.

Do not treat a provider-capacity rejection as model-quality evidence.

### 3.5 Recover canonical `ActionRequest` — PENDING

Recover the exact supplied TRACTIAN OpenAPI component used by the five action request bodies. Do not guess it. Strict action-output variants cannot be declared complete until this contract is available.

### 3.6 Build canonical `strict:true` challenger — PENDING AFTER 3.3/3.5

Generate closed output variants from existing ToolSpecs/OpenAPI/Release 0 contracts:

```text
TOOL::<canonical tool> | FINAL | CLARIFY | ESCALATE | ABSTAIN
```

Keep `ProviderDecisionPayload`, argument validation, controller policy and action safety as deterministic post-generation barriers.

### 3.7 Strict eligibility preflights — PENDING

Run only small compatibility probes before exposing the frozen evaluation population. Eligibility must prove that the provider accepts the generated schema and produces application-valid decisions without repair.

### 3.8 Freeze causally justified challengers — PENDING

Expected set, only if evidence supports it:

```text
B0 original: best-effort / medium / 512
B1 budget:   best-effort / medium / 2048
C1 strict:   strict / medium / 2048
C2 strict:   strict / low / 2048
```

C1/C2 are not automatically eligible merely because Groq advertises structured outputs.

### 3.9 Controlled challenger comparison — PENDING

Use the same rubric and same safety/contract semantics. No post-hoc gate relaxation.

Original hard gates:

```text
private/binding attempts = 0
unknown tools = 0
invalid known-tool args = 0
schema/contract failures = 0
trace/provenance failures = 0
reliability >= 93.75%
```

### 3.10 Winner-only fresh 85/85 — PENDING

Only a challenger that wins the controlled comparison and passes hard gates receives a new full 17×5 qualification. Failed attempts remain denominator; no selective rerun.

### 3.11 Academy live E2E before production — PENDING

A qualification winner must still pass:

- Academy live end-to-end behavior;
- causal/RMS regression;
- auth/tenant/persistence/SSE smoke;
- provider failure behavior;
- action-safety gate if actions are ever enabled.

Only then may an explicit production provider promotion be considered.

## Phase 4 — Broader live prompt/API coverage — P1

Continue recent live coverage across canonical reads and semantic failure modes, including:

1. identity/company/fleet;
2. two real in-fleet assets for bilateral comparison;
3. analyses/detail;
4. RMS asset→point;
5. spectrum asset→point;
6. baseline;
7. data quality;
8. model;
9. knowledge search/doc;
10. unavailable/conflict/inconclusive/partial/complete;
11. anti-hallucination/false precision;
12. action/prompt-injection challenges with zero execution.

Measure read coverage, tool/argument correctness, duplicate vs drill-down rate, terminal semantics, response-mode correctness, unsupported-claim rate and action refusal.

## Phase 5 — Security, capacity and recovery — PENDING

Order:

1. full hosted SECURITY-V1;
2. auth/session burst and concurrent-user coverage;
3. load staircase / saturation / quota boundary;
4. evidence-derived SLO;
5. provider/TRACTIAN/DB/backend/SSE failure campaign;
6. known-state backup/export and isolated restore;
7. measured RTO/RPO only if supported.

Do not enable paid features merely to manufacture stronger delivery evidence.

## Phase 6 — Consequential external actions — DISABLED / FUTURE GATE

Release 0 remains proposal/read-only. If actions are ever promoted, require deterministic validation, private custody, explicit opaque-ID confirmation, fresh authorization/kill switch, persistent idempotency, lease/fencing and `UNCERTAIN` handling for ambiguous ownership.

## Phase 7 — Human semantic calibration and operational value — PENDING

Semantic LLM judges remain non-gating until calibrated against blinded human labels. Operational-value claims require a real MANUAL vs AGENT-ASSISTED comparison; do not claim time saved from intuition.

## Phase 8 — Adaptive/framework challengers — DEFERRED

LangGraph, multi-agent, RAG/vector DB, MCP, persistent memory, Redis/Kafka/Kubernetes or adaptive stopping/routing require a measured gap and controlled win. Provider/schema work does not justify unrelated architecture migration.

## Phase 9 — Final evidence freeze — LAST

Freeze/link only after the applicable gates settle:

- exact production component identities;
- provider decision and qualification evidence;
- TAPI/read coverage;
- IAM/RLS/security;
- evaluation/stability/failure evidence;
- capacity/SLO/recovery;
- action state/limitations;
- human/value evidence or explicit non-claim;
- task-driven UX evidence;
- runbooks/changelog/reversal triggers.

## Priority rule until delivery

```text
P0 safety / broken production / tenant / action / cost
→ P0 provider causal diagnosis + hard-gate qualification
→ P1 live read/semantic coverage
→ P1 security/capacity/recovery evidence
→ documentation/presentation integration
→ optional polish
```

A late change that cannot be retested does not silently enter production.
