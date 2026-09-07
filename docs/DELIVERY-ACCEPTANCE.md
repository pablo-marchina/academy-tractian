# Academy × TRACTIAN — Final Delivery Acceptance

**Status:** ACTIVE final-project Definition of Done  
**Last rebaseline:** 2026-09-07 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Original Release 0 acceptance:** [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md)

This document answers: **what must be demonstrably true before the complete project may be called finished?**

Current production is a V13 read-path descendant with governed actions enabled in production configuration. That does not mean every final research/production claim — especially five-action vendor acceptance — is complete.

## 1. Current final-acceptance ledger

| Area | Current state | Final claim boundary |
|---|---|---|
| remote HTTPS product | **PASS** | Railway public frontend/API |
| current backend source identity | **PASS** | `3545d75c...` merged/deployed healthy |
| current frontend exact identity | **PASS** | task-driven `1bc124a...` deployed SUCCESS |
| USD0 + no paid spillover | **PASS Release 0 policy** | must remain true through delivery |
| no local/mock production dependency | **PASS** | remote serving path |
| managed browser IAM | **PASS hardened scope** | 401/503 semantics + bounded read cache; broader SLO pending |
| Neon PostgreSQL/RLS | **PASS Release 0** | broader recovery/capacity pending |
| real hosted provider | **PASS provisional** | final tournament still `NO_SELECTION` |
| real typed TRACTIAN reads | **PASS sampled paths** | all-read coverage not yet complete |
| response-mode semantics | **PASS targeted live cases** | broad semantic calibration pending |
| explicit asset grounding | **PASS targeted live cases** | larger prompt/property coverage pending |
| condition-evidence gate | **PASS targeted live cases** | broader read-path coverage pending |
| data-quality gate | **PASS targeted live run** | broader resource coverage pending |
| safe missing-resource behavior | **PASS targeted R420 case** | not a true bilateral comparison proof |
| evidence/lineage/evaluator/persistence/SSE | **PASS Release 0 + regressions** | final evidence quality remains measurable |
| 18-operation contract | **PASS contract** | 13 reads + 5 governed actions |
| task-driven first-user UX | **PASS automated/current hosted UX** | structural simplification + real-user usability evidence pending |
| governed action local safety architecture | **PASS implementation/CI** | custody/confirmation/grants/idempotency/lease/uncertainty |
| governed action production composition | **PASS enabled/booted** | five executable actions advertised |
| five-action upstream acceptance | **NOT READY** | live smoke currently blocked by `update_asset_config` HTTP 403 |
| upstream vendor actor routing | **IN PROGRESS** | must be server-owned by company+permission and live-proven |
| failed-deploy containment | **PASS observed** | failed write smoke left healthy production serving |
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
+ governed consequential-action safety
+ trustworthy evaluation
+ observable/reproducible evidence
+ claim-specific production/security/value proof
```

If evidence is unavailable, use `PENDING`, `NOT READY`, `NO_SELECTION` or an explicit limitation — never infer a pass.

## 3. TAPI product acceptance

The integrated product must demonstrate:

1. **Industrial Agent** — contextualize/investigate industrial requests with typed TRACTIAN operations and safe operational outcomes/proposals/actions under explicit confirmation.
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
- cross-user/cross-tenant REST/SSE/storage/action-confirmation negatives;
- invalid/manipulated session fails closed;
- read-burst cache never stores raw cookie or serves expired stale context;
- non-read requests receive fresh managed-session validation;
- invalid session (`401`) is distinct from temporary identity-service outage (`503`);
- browser reconciles auth after invalid/unavailable signals and focus/visibility return.

Do not claim OAuth/OIDC/enterprise SSO unless actually implemented/tested.

## 6. Consequential-action acceptance

The local governed action architecture is now promoted. Final action readiness requires proving all of these, not merely enabling the kill switch:

### Local deterministic boundary

- proposal ≠ execution;
- exact private custody of tool + arguments + fingerprint;
- confirmation accepts only the existing action decision, not replacement arguments/permissions;
- fresh tenant-aware server-owned authorization;
- canonical ToolSpec permission;
- exact resource/company binding;
- persistent idempotency before I/O;
- non-transferable lease/generation fencing;
- host-owned kill switch;
- no browser/model authority over grants, idempotency or vendor identity;
- duplicate confirmation/claim fails closed;
- `UNCERTAIN` never auto-retries.

### Vendor action identity boundary

The supplied TRACTIAN runtime uses a vendor actor (`x-user-id`) with endpoint-specific permissions. The local authenticated product user must remain the audit/authorization principal while the vendor actor is selected server-side only after local authorization.

Final invariant:

```text
(company_id, required_permission)
→ exactly one server-owned upstream actor
```

Missing/ambiguous mappings must block. Browser/model/confirmation payloads must not select or upgrade actor identity.

### Live five-action acceptance

The auditable production smoke must pass all five canonical actions:

```text
reprocess_analysis
request_specialist_analysis
update_asset_config
request_retraining
escalate_case
```

For each action:

```text
HTTP ∈ {200, 201, 202}
AND accepted == true
```

The current live smoke does **not** satisfy this gate: `update_asset_config` returned HTTP 403 / `accepted=false` and the validation deployment failed safely.

After actor-routing correction, require:

1. full required CI green;
2. exact-SHA fresh Railway deployment/config snapshot;
3. 5/5 smoke pass;
4. normal product confirmation-path hosted evidence;
5. action state/evaluation persistence;
6. duplicate/uncertain/failure regressions intact.

Do not claim distributed exactly-once side effects unless the external API supports a compatible protocol. The product can prove its own one-shot/idempotent execution boundary, not control arbitrary external infrastructure forever.

## 7. Evaluation acceptance

Deterministic exact checks remain authoritative where structural truth exists. The framework should cover scenario/trace execution, tool/argument quality, trajectory, evidence/provenance, terminal outcome, action behavior, degraded paths, stability, evaluator/runtime isolation and config/result identity.

PR #213 required-gate run `34164123263` passed action lease/fencing, horizontal runtime, production image, Railway IaC, clean-clone full product reproduction and Chromium browser acceptance for its source scope.

Provider-free/browser CI is not a substitute for vendor action acceptance; the failed hosted 403 is the stronger evidence for that specific external boundary.

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

- live read coverage across the canonical surface;
- five-action live acceptance after correct vendor actor routing;
- action duplicate/uncertain/permission/actor failure campaigns;
- auth/session/concurrency stress at final topology;
- load staircase/soak → throughput, p50/p95/p99, errors, quotas and saturation;
- SLO derived after measurement;
- provider/TRACTIAN/DB/backend/SSE/deployment failure campaigns;
- real known-state backup/export + isolated restore + integrity check;
- measured RTO/RPO only;
- full hosted SECURITY-V1.

## 11. UX / observability acceptance

A first-time user should be able to:

1. understand what the product can do without runtime jargon;
2. submit a normal equipment question from Home;
3. use human asset labels without internal IDs;
4. understand progress;
5. interpret the terminal/result and uncertainty;
6. see what to do next;
7. inspect supporting evidence contextually;
8. reopen persisted runs through Analyses;
9. open Technical only for specialist depth;
10. understand consequential action impact before confirmation;
11. never see fabricated progress, raw secrets, private grants/vendor actors or hidden reasoning.

Current automated/browser acceptance proves functional/accessibility-oriented invariants for the tested UI. It does **not** prove human usability. Final strong UX claims require representative-user evidence such as task completion, time-to-correct-conclusion, interpretation errors/help requests and an appropriate usability measure.

Current structural UX north star:

> one main question and one obvious primary action per screen; specialist detail only when needed.

## 12. Final acceptance decision

The project is final only when all applicable hard rows are PASS or explicitly documented as accepted non-goals/limitations consistent with the assignment.

Original Release 0 acceptance remains immutable evidence for its historical scope. Later V13/action hardening is additive prospective evidence, not a retroactive rewrite.

See [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md) for the current action/deployment evidence.