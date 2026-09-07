# Academy × TRACTIAN — Final Delivery Acceptance

**Status:** ACTIVE final-project Definition of Done  
**Last rebaseline:** 2026-09-06 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Release 0 acceptance:** [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md)

This document answers: **what must be demonstrably true before the complete project may be called finished?**

Release 0 being promoted does not mean every final research/hardening claim is complete.

## 1. Current final-acceptance ledger

| Area | Current state | Final claim boundary |
|---|---|---|
| remote HTTPS product | **PASS** | Railway public frontend/API |
| USD0 + no paid spillover | **PASS for Release 0 path** | must remain true through final delivery |
| no local/mock production dependency | **PASS** | remote serving path |
| managed browser IAM | **PASS Release 0** | hosted two-user/tenant negatives passed |
| Neon PostgreSQL/RLS | **PASS Release 0** | broader recovery/capacity still pending |
| immutable backend release identity | **PASS** | exact promoted SHA |
| real hosted provider | **PASS provisional** | final tournament still `NO_SELECTION` |
| real typed TRACTIAN reads | **PASS** | canonical remote read observed |
| agent FINAL/CLARIFY/ABSTAIN/ESCALATE | **PASS Release 0** | broader semantic correctness remains to measure |
| evidence/lineage/evaluator/persistence/SSE | **PASS Release 0** | full final evidence quality still measurable |
| 18 operation coverage | **PASS contract** | 13 live reads + 5 proposal-only actions |
| first-user UX progressive disclosure | **PASS current UX** | hosted + Playwright green |
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
+ safe agent behavior
+ trustworthy evaluation
+ observable/reproducible evidence
+ claim-specific production/security/value proof
```

If evidence is unavailable, the correct status is `PENDING`, `NOT READY`, `NO_SELECTION` or an explicit limitation — not an inferred pass.

## 3. TAPI product acceptance

The integrated product must demonstrate both:

1. **Industrial Agent** — interpret industrial requests and use the supplied TRACTIAN operations safely.
2. **Agent Evaluation Framework** — assess tool/argument/trajectory/evidence/terminal/safety/failure/stability/action behavior with reproducible provenance.

Required operating semantics include Contextualize / Investigate / Execute intent, with customer-safe FINAL/ORIENT, CLARIFY, ABSTAIN, ESCALATE and governed action proposal behavior.

## 4. Agent/evidence acceptance

Before claiming a behavior class complete, prove as applicable:

- correct typed tool selection/arguments;
- complete/partial/inconclusive/conflicting/unavailable evidence handling;
- grounded customer-safe conclusion;
- clarification only when information is genuinely required;
- safe abstention rather than fabrication;
- useful escalation/handoff;
- structured evidence lineage/provenance;
- safe provider/tool/runtime failure behavior;
- repeated-run stability where stochasticity matters.

Operational conclusion and observable process matter more than exact wording.

## 5. IAM / tenant acceptance

Current Release 0 managed-session architecture has passed its hosted release campaign. Final regression must continue proving:

- login/logout/session lifecycle;
- server-owned mapping to user/tenant/permissions;
- browser cannot assert tenant/privilege;
- independent PostgreSQL RLS boundary;
- cross-user/cross-tenant REST/SSE/storage negatives;
- invalid/manipulated session fails closed.

Do not claim OAuth/OIDC/enterprise SSO unless it is actually implemented and tested; the current managed session is the claimed product boundary.

## 6. Consequential-action acceptance

External action execution is not part of the promoted Release 0 boundary. Before it can be enabled, prove:

- proposal ≠ execution;
- deterministic permission/resource/schema/evidence/justification validation;
- server-side private custody;
- opaque-ID explicit operator confirmation;
- browser cannot replace args/tenant/identity/permissions/idempotency material;
- fresh authorization + kill switch before transport;
- persistent idempotency before attempt;
- non-transferable execution lease/fencing;
- duplicate confirmation does not duplicate transport;
- ambiguous ownership loss converges to `UNCERTAIN`;
- no blind replay after ambiguous external side-effect ownership;
- separate auditable trace/evaluation;
- cross-user/tenant confirmation denied.

Do not claim distributed exactly-once side effects unless the external API supports a compatible protocol.

## 7. Evaluation acceptance

Deterministic exact checks remain authoritative where structural truth exists. The framework should cover:

- scenario/trace execution;
- tool and argument quality;
- trajectory integrity;
- evidence/provenance;
- terminal outcome;
- safety/action behavior;
- degraded/failure paths;
- stability/repetition;
- evaluator/runtime isolation;
- config/result identity;
- baseline-vs-candidate deltas.

Private benchmark/gold/evaluator truth must never enter model/runtime context.

## 8. Semantic-evaluation acceptance

Semantic judges cannot gate candidates until real blinded human labels establish acceptable reliability. Required evidence should include rubric, independent labels/adjudication where appropriate, agreement/error analysis, confusion matrix and relevant precision/recall/F1 or another justified metric.

Until then: **NOT READY**, not an invented judge score.

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

- load staircase/soak → throughput, p50/p95/p99, errors, quotas and saturation;
- SLO → derived after measurement, not declared first;
- recovery → provider/TRACTIAN/DB/backend/SSE/deployment failures;
- restore → real known-state backup/export + isolated restore + integrity check;
- RTO/RPO → measured outputs only;
- security → hosted SECURITY-V1, not source tests alone.

## 11. UX / observability acceptance

A first-time user should be able to:

1. understand the product and read-only boundary;
2. submit a useful request;
3. understand progress;
4. interpret FINAL/CLARIFY/ABSTAIN/ESCALATE;
5. see what to do next;
6. inspect supporting evidence;
7. go deeper into runtime/engineering only when needed;
8. recover persisted history;
9. never be shown fabricated progress, raw secrets or hidden reasoning.

A technical reviewer should additionally be able to inspect tool/policy/evidence transitions, trace topology, evaluator output, architecture/capability contracts and exact release provenance.

## 12. Final acceptance decision

The project is final only when all **applicable** hard rows are PASS or explicitly documented as accepted non-goals/limitations consistent with the assignment.

Release 0 acceptance is already immutable evidence for its scope; remaining gates must be closed prospectively rather than retroactively editing that evidence.