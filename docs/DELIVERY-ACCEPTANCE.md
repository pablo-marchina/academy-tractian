# Academy × TRACTIAN — Final Delivery Acceptance

**Status:** ACTIVE final-project Definition of Done  
**Last rebaseline:** 2026-09-08 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Provider state:** [`PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](PROVIDER-QUALIFICATION-STATUS-2026-09-08.md)  
**Original Release 0 acceptance:** [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md)

This document answers: **what must be demonstrably true before the complete project may be called finished?** Release 0 production remains live, but final provider/security/capacity/recovery/value claims are separate gates.

## 1. Current final-acceptance ledger

| Area | Current state | Final claim boundary |
|---|---|---|
| remote HTTPS product | **PASS** | Railway public frontend/API |
| no local/mock production dependency | **PASS** | remote serving path |
| managed browser IAM | **PASS hardened scope** | broader capacity/security evidence pending |
| Neon PostgreSQL/RLS | **PASS Release 0** | restore/capacity claims pending |
| real typed TRACTIAN reads | **PASS sampled live paths** | broad recent read coverage still incomplete |
| response-mode semantics | **PASS targeted live cases** | human semantic calibration pending |
| explicit asset grounding | **PASS targeted live cases** | broader property/prompt coverage pending |
| condition-evidence gate | **PASS targeted live cases** | broader read-path coverage pending |
| data-quality gate | **PASS targeted live case** | broader resource coverage pending |
| safe missing-resource behavior | **PASS targeted R420 case** | not a bilateral-comparison proof |
| evidence/lineage/evaluator/persistence/SSE | **PASS Release 0 + regressions** | final evidence quality remains measurable |
| 18-operation contract | **PASS contract** | 13 reads + 5 action operations represented |
| task-driven first-user UX | **PASS current hosted UX** | real-user usability evidence pending |
| consequential external action execution | **DISABLED** | no production-readiness claim |
| paired Cloudflare/Groq V4 | **CLOSED WITHOUT COMPARATIVE RESULT** | Cloudflare quota-blocked then removed by explicit user choice |
| Groq-only 85/85 qualification | **COMPLETE — NO_SELECTION** | 81.18% rubric pass; 82.35% reliability; 9 contract failures |
| provider causal diagnosis | **ACTIVE** | clean 21/21 still required |
| canonical strict-output challenger | **PENDING** | exact `ActionRequest` + strict preflight required |
| final provider selection | **PENDING / NO WINNER** | challenger must pass unchanged hard gates + fresh 85/85 + E2E |
| full SECURITY-V1 | **PENDING** | no broad final security claim yet |
| remote load/capacity/SLO | **PENDING** | no invented SLO |
| restore/RTO/RPO | **PENDING** | real drill required |
| semantic human calibration | **PENDING** | semantic judge non-gating until calibrated |
| operational-value experiment | **PENDING** | no time-saved claim |
| final evidence freeze | **PENDING** | last step |

## 2. Non-negotiable final rule

Applicable final claims must simultaneously preserve:

```text
actual project cash-cost policy / no hidden paid fallback
+ real remote serving
+ tenant-safe multi-user identity/state
+ real TRACTIAN integration
+ grounded safe agent behavior
+ trustworthy evaluation
+ observable/reproducible evidence
+ claim-specific production/security/value proof
```

If evidence is unavailable, use `PENDING`, `NOT READY`, `NO_SELECTION`, `INCONCLUSIVE` or an explicit limitation. Never infer a pass from availability or provider marketing.

## 3. Provider acceptance — current hard contract

A provider/serving configuration may become a production candidate only after the following sequence:

```text
causal diagnosis
→ canonical challenger definition
→ small eligibility preflight
→ controlled comparison with unchanged rubrics
→ original hard gates
→ fresh 85/85 winner-only qualification
→ Academy live E2E
→ explicit production promotion decision
```

Original hard gates remain:

```text
private/identity-material attempts = 0
unknown-tool proposals = 0
invalid known-tool arguments = 0
schema/adapter contract failures = 0
trace/provenance failures = 0
reliability >= 93.75%
```

Retries, fallback and JSON repair may not be used to erase model/provider failures from the scored denominator.

### Groq qualification evidence

`openai/gpt-oss-120b` via Groq completed 85/85 and returned `NO_SELECTION`:

- rubric pass 69/85 = 81.18%;
- reliability 70/85 = 82.35%;
- contract failures 9;
- repeat stability 11/17 = 64.71%;
- p50 1.154 s;
- p95 2.904 s.

This is a completed negative qualification, not an incomplete tournament and not authorization to lower gates.

### Causal challenger acceptance

Before C1/C2 strict challengers exist as valid candidates:

- complete a clean 21/21 causal matrix;
- recover the exact supplied `ActionRequest` schema;
- derive strict closed variants from canonical ToolSpecs/OpenAPI/Release 0 contracts;
- prove Groq accepts the schema in a small preflight;
- keep `ProviderDecisionPayload`, argument validation and policy/safety checks as deterministic barriers.

## 4. TAPI product acceptance

The integrated product must demonstrate both:

1. **Industrial Agent** — contextualize/investigate requests through typed TRACTIAN operations and produce safe grounded outcomes/proposals.
2. **Agent Evaluation Framework** — evaluate observable function choice, arguments, trajectory, evidence, response quality, safety, failure behavior, stability and high-impact behavior with reproducible provenance.

The observable process is part of the product claim, not merely the final wording.

## 5. Agent / grounding / evidence acceptance

Before claiming a behavior class complete, prove as applicable:

- correct typed tool selection/arguments;
- authorized structured origin for internal IDs;
- human labels resolved through authenticated company/fleet discovery;
- no unnecessary request for discoverable internal IDs;
- evidence for every compared resource;
- fail-closed missing resource behavior;
- appropriate condition/data-quality evidence before conclusions;
- `complete|partial|inconclusive|conflict|unavailable` semantics aligned with evidence;
- safe clarification/abstention/escalation;
- structured lineage/provenance;
- safe provider/tool/runtime failure behavior;
- repeated-run stability where stochasticity matters.

Tool-name repetition is not itself a failure. Compare normalized arguments/resource target and incremental evidence; asset→point RMS/spectrum refinement can be legitimate.

## 6. IAM / tenant acceptance

Current managed-session architecture must preserve:

- server-owned user/tenant/permission mapping;
- browser cannot assert privilege;
- independent PostgreSQL RLS boundary;
- cross-user/cross-tenant REST/SSE/storage negatives;
- manipulated/invalid session fail closed;
- bounded read-cache behavior without raw-cookie storage or stale-on-error;
- fresh non-read validation;
- `401` invalid session distinct from retryable identity-service `503`;
- browser auth reconciliation after invalid/unavailable signals.

Do not claim OAuth/OIDC/enterprise SSO unless implemented and tested.

## 7. Consequential-action acceptance

External action execution is not part of the promoted Release 0 claim. Before enabling it, prove proposal ≠ execution, deterministic validation, private custody, explicit opaque-ID confirmation, fresh authorization/kill switch, persistent idempotency, non-transferable lease/fencing, no duplicate transport and `UNCERTAIN` semantics for ambiguous ownership.

## 8. Evaluation acceptance

Deterministic checks remain authoritative where structural truth exists. Evaluation should cover tool/argument quality, trajectory, evidence/provenance, terminal outcome, safety/action behavior, failure/degraded paths, stability, evaluator/runtime isolation and exact config/result identities.

Private benchmark/gold/evaluator truth must never enter model/runtime context.

The 2026-09-08 provider episode strengthens this rule: a syntactically valid JSON response with HTTP 200/`stop` still fails if `ProviderDecisionPayload` relational invariants fail.

## 9. Production hardening acceptance

Final production claims require claim-specific hosted evidence for:

- recent canonical read coverage;
- auth/session/concurrency stress at final topology;
- load staircase/soak → throughput, p50/p95/p99, error/quota/saturation behavior;
- evidence-derived SLO;
- provider/TRACTIAN/DB/backend/SSE failure campaigns;
- known-state backup/export + isolated restore + integrity/tenant check;
- measured RTO/RPO only;
- full hosted SECURITY-V1.

## 10. UX / observability acceptance

A first-time user should be able to understand the read-only boundary, ask a normal equipment question, use human asset labels, understand progress/result/uncertainty, inspect support when useful, reopen history and reach Technical depth without seeing fabricated progress, raw secrets or hidden reasoning.

A reviewer should additionally inspect tool/policy/evidence transitions, evaluation output, architecture/capability contracts and exact release/provider evidence.

## 11. Final acceptance decision

The project is final only when applicable hard rows are PASS or explicitly documented as accepted non-goals/limitations consistent with the assignment.

Original Release 0 and older provider experiments remain immutable historical evidence. Negative provider qualification results are evidence and must not be rewritten into passes.
