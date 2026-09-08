# Academy × TRACTIAN — Final Delivery Acceptance

**Status:** ACTIVE final-project Definition of Done  
**Last rebaseline:** 2026-09-07 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Original Release 0 acceptance:** [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md)

This document answers: **what must be demonstrably true before the complete project may be called finished?**

Current production is Release 0 V13, but Release 0 promotion/hardening does not mean every final research/production claim is complete.

## 1. Current final-acceptance ledger

| Area | Current state | Final claim boundary |
|---|---|---|
| remote HTTPS product | **PASS** | Railway public frontend/API |
| current backend exact identity | **PASS** | V13 `08866da...` deployed SUCCESS |
| current frontend exact identity | **PASS** | task-driven `1bc124a...` deployed SUCCESS |
| USD0 + no paid spillover | **PASS Release 0 policy** | must remain true through delivery |
| no local/mock production dependency | **PASS** | remote serving path |
| managed browser IAM | **PASS hardened scope** | 401/503 semantics + bounded read cache; broader SLO pending |
| Neon PostgreSQL/RLS | **PASS Release 0** | broader recovery/capacity pending |
| real hosted provider | **PASS provisional** | final tournament still `NO_SELECTION` |
| real typed TRACTIAN reads | **PASS sampled paths** | all-read coverage not yet complete |
| response-mode semantics | **PASS targeted V11/V13 live cases** | broad semantic calibration pending |
| explicit asset grounding | **PASS targeted V13 cases** | larger prompt/property coverage pending |
| condition-evidence gate | **PASS targeted live cases** | broader read-path coverage pending |
| data-quality gate | **PASS targeted V13 run** | broader resource coverage pending |
| safe missing-resource behavior | **PASS targeted R420 case** | not a true bilateral comparison proof |
| evidence/lineage/evaluator/persistence/SSE | **PASS Release 0 + V13 regressions** | final evidence quality remains measurable |
| 18-operation contract | **PASS contract** | 13 reads + 5 action operations represented |
| task-driven first-user UX | **PASS current hosted UX** | real-user usability study pending |
| consequential external action execution | **DISABLED / PENDING** | not a Release 0 claim |
| Provider Tournament v3 | **PENDING** | 170 attempts or explicit final `NO_SELECTION` |
| full SECURITY-V1 | **PENDING** | no broad final security claim yet |
| remote load/capacity/SLO | **PENDING** | no invented SLO |
| restore/RTO/RPO | **PENDING** | require real drill |
| semantic human calibration | **PENDING** | semantic judge non-gating until then |
| operational-value experiment | **PENDING** | no time-saved claim |
| adaptive challenger | **NO_CHANGE / OPTIONAL** | only after measured gap |
| final evidence freeze | **PENDING** | last step |

## 2. Non-negotiable final rule

Applicable final claims must simultaneously preserve:

```text
actual cash cost = USD 0
+ no automatic paid spillover
+ real remote serving
+ tenant-safe multi-user identity/state
+ real TRACTIAN integration
+ grounded safe agent behavior
+ trustworthy evaluation
+ observable/reproducible evidence
+ claim-specific production/security/value proof
```

If evidence is unavailable, use `PENDING`, `NOT READY`, `NO_SELECTION` or an explicit limitation — never infer a pass.

## 3. TAPI product acceptance

The integrated product must demonstrate:

1. **Industrial Agent** — contextualize/investigate industrial requests with typed TRACTIAN operations and safe operational outcomes/proposals.
2. **Agent Evaluation Framework** — evaluate observable tool/argument/trajectory/evidence/terminal/safety/failure/stability behavior with reproducible provenance.

Operational conclusion and observable process matter more than exact wording.

## 4. Agent / grounding / evidence acceptance

Before claiming a behavior class complete, prove as applicable:

- correct typed tool selection/arguments;
- internal IDs originate only from authorized structured observations;
- human asset labels resolve through authenticated company/fleet discovery;
- customer is not asked for discoverable internal IDs;
- comparison claims require evidence for every compared resource;
- missing resources fail closed without cross-tenant speculation;
- diagnostic terminal answers have condition evidence when required;
- data-quality questions inspect data quality before conclusion;
- baseline/data quality are not misused as substitutes for condition evidence;
- complete/partial/inconclusive/conflict/unavailable semantics match the message/evidence;
- grounded customer-safe conclusion;
- clarification only when genuinely required;
- safe abstention/unavailability instead of fabrication;
- structured evidence lineage/provenance;
- safe provider/tool/runtime failure behavior;
- repeated-run stability where stochasticity matters.

### Repetition acceptance

Do not fail a trajectory merely because the same tool name appears more than once. Compare normalized arguments/resource target and incremental evidence. Asset-level → point-specific RMS/spectrum reads are a validated legitimate pattern; exact same-resource/args reads without new evidence remain candidates for redundancy failure.

## 5. IAM / tenant acceptance

Current managed-session architecture must continue proving:

- login/logout/session lifecycle;
- server-owned mapping to user/tenant/permissions;
- browser cannot assert tenant/privilege;
- independent PostgreSQL RLS boundary;
- cross-user/cross-tenant REST/SSE/storage negatives;
- invalid/manipulated session fails closed;
- read-burst cache never stores raw cookie or serves expired stale context;
- non-read requests receive fresh managed-session validation;
- invalid session (`401`) is distinct from temporary identity-service outage (`503`);
- browser reconciles auth after invalid/unavailable signals and focus/visibility return.

Do not claim OAuth/OIDC/enterprise SSO unless actually implemented/tested.

## 6. Consequential-action acceptance

External action execution is not part of Release 0. Before enabling it, prove proposal ≠ execution, deterministic validation, server-side custody, explicit opaque-ID confirmation, fresh authorization/kill switch, persistent idempotency, non-transferable lease/fencing, no duplicate transport, `UNCERTAIN` semantics for ambiguous ownership and cross-user/tenant denial.

Do not claim distributed exactly-once side effects unless the external API supports a compatible protocol.

## 7. Evaluation acceptance

Deterministic exact checks remain authoritative where structural truth exists. The framework should cover scenario/trace execution, tool/argument quality, trajectory, evidence/provenance, terminal outcome, safety/action behavior, degraded paths, stability, evaluator/runtime isolation and config/result identity.

Current V13 live runs passed the persisted structural blocking checks for their scope, including execution-chain integrity, model-call provenance, production trace identity, proposal contract validity, read-only action safety and terminal consistency.

Private benchmark/gold/evaluator truth must never enter model/runtime context.

## 8. Semantic-evaluation acceptance

Semantic judges cannot gate candidates until real blinded human labels establish acceptable reliability. Required evidence should include rubric, independent labels/adjudication, agreement/error analysis, confusion matrix and justified metrics.

Confidence language (“baixo/médio/alto”, causal certainty, exact percentages) must be calibrated against evidence before it becomes a trusted product contract.

## 9. Eval-Driven Development acceptance

For each material challenger:

```text
requirement / measured gap
→ eligibility hard gates
→ metric/evaluator
→ baseline
→ preregistered candidate
→ controlled implementation
→ repeated/sliced comparison
→ failure + uncertainty analysis
→ PROMOTE | REJECT | INCONCLUSIVE | NO_CHANGE | NO_SELECTION
→ regression guard
```

Hard gates include USD0, no paid spillover, zero gold/credential leakage, zero unauthorized action and zero tenant escape.

## 10. Production hardening acceptance

Final production claims require claim-specific hosted evidence:

- live read coverage across the canonical Release 0 surface;
- auth/session/concurrency stress at final topology;
- load staircase/soak → throughput, p50/p95/p99, errors, quotas and saturation;
- SLO derived after measurement;
- provider/TRACTIAN/DB/backend/SSE/deployment failure campaigns;
- real known-state backup/export + isolated restore + integrity check;
- measured RTO/RPO only;
- full hosted SECURITY-V1.

## 11. UX / observability acceptance

A first-time user should be able to:

1. understand the product/read-only boundary;
2. submit a normal equipment question from Home;
3. use human asset labels without internal IDs;
4. understand progress;
5. interpret the terminal/result and response-mode uncertainty;
6. see what to do next;
7. inspect supporting evidence contextually;
8. reopen persisted runs through Analyses;
9. open Technical only for specialist depth;
10. never see fabricated progress, raw secrets or hidden reasoning.

A technical reviewer should additionally inspect tool/policy/evidence transitions, trace topology, evaluator output, architecture/capability contracts and exact release provenance.

## 12. Final acceptance decision

The project is final only when all applicable hard rows are PASS or explicitly documented as accepted non-goals/limitations consistent with the assignment.

Original Release 0 acceptance remains immutable evidence for its scope. Later V13 hardening is additive prospective evidence, not a retroactive rewrite.