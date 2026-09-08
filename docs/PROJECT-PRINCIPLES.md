# Academy × TRACTIAN — Non-Negotiable Project Principles

**Status:** ACTIVE mandatory governance  
**Last rebaseline:** 2026-09-08 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Provider state:** [`PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](PROVIDER-QUALIFICATION-STATUS-2026-09-08.md)  
**Execution plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)

These principles override convenience, novelty, implementation momentum and prior provisional choices.

## North Star

> Deliver the strongest defensible TRACTIAN × Inteli product: a remote, multi-user, production-oriented **Agent + Evaluation** platform whose behavior, architecture, safety, quality and operational value are measurable and observable.

A workstream must map to at least one of:

1. TAPI/delivered-package requirement;
2. academic evaluation criterion;
3. material production/security/reliability risk;
4. measurable user/operational-value requirement;
5. experiment required to choose among credible alternatives for the above.

If it maps to none, defer it.

## P0 — Real production, remote-first, never demo-first

Production serving must not depend on localhost/loopback, a developer laptop/manual process, local model serving, local-file database truth, scripted/mock provider responses or browser-owned tenant/permission authority.

Local/test execution is valid for reproduction and controlled research, not as evidence of the hosted production claim.

## P0 — Cost/paid-spillover boundary is explicit

```text
silent paid spillover / automatic billing → FORBIDDEN
provider/account quota exhausted          → fail/degrade explicitly
eligible candidate + applicable hard gates→ eligible for promotion
no candidate passes                       → NO_SELECTION / explicit blocker
```

Zero-cost constraints are eligibility constraints, not quality evidence. A candidate does not become preferred merely because it is free/available.

## Source hierarchy

When sources conflict:

1. current TAPI;
2. delivered TRACTIAN package/contract;
3. executable supplied API behavior/tests;
4. compatible kickoff/partner guidance;
5. project research/assumptions.

Record discrepancies instead of silently harmonizing them.

## P1 — Systematic research before material choices

```text
decision question / measured gap
→ requirement/risk
→ hard constraints
→ primary-source research
→ baseline + credible eligible alternatives
→ preregistered metrics/hard gates
→ controlled quantitative comparison
→ failure/robustness/production-fit analysis
→ decision + reversal trigger
→ regression protection
```

Do not add technology because it is popular. LangGraph migration, multi-agent, RAG/vector DB, persistent memory, MCP, Redis/Kafka and Kubernetes remain `NO_CHANGE` unless a measured gap and controlled win justify them.

## Decision states

- `UNASSESSED` — insufficient evidence;
- `RESEARCHED` — credible evidence/options mapped;
- `INELIGIBLE` — violates a hard constraint;
- `QUALIFIED` — passes minimum gates;
- `PREFERRED` — best-supported eligible candidate;
- `FROZEN` — accepted for stated evidence scope;
- `REJECTED` — evidence rejects candidate;
- `NO_CHANGE` — current simpler path remains preferred;
- `NO_SELECTION` — no candidate/configuration deserves final promotion;
- `SUPERSEDED` — prospectively replaced by stronger evidence.

A completed negative qualification is valuable evidence. On 2026-09-08 Groq GPT-OSS-120B completed 85/85 and returned `NO_SELECTION`; the correct response is causal diagnosis/new challenger evidence, not redefining success after seeing the result.

## P2 — Quantitative before qualitative

When measurement is valid, prefer rates/distributions, p50/p95/p99, paired deltas, uncertainty/effect sizes, failure/error rates, quota/cost, repeat stability, calibration/agreement and task/value deltas.

Qualitative evidence complements measurement where semantics/user experience cannot safely be reduced to exact checks.

## P3 — Adaptive where valuable; deterministic where safety-critical

Potentially adaptive only after challenger evidence:

- investigation depth;
- evidence/tool ordering;
- stopping;
- clarify/abstain/escalate thresholds;
- provider routing among eligible candidates;
- bounded retry/backoff where protocol semantics allow it;
- contextual resource budgets;
- visualization prioritization.

Always deterministic/hard-gated:

- authentication/tenant binding;
- RLS/authorization/permissions;
- application schema/argument validation;
- action confirmation/custody/idempotency/leases/fencing;
- privacy/field deny-lists;
- evaluator/gold isolation;
- hard resource caps;
- cost/no-hidden-paid-fallback boundary.

Provider `strict:true`, if later used, is an additional structural barrier and never replaces deterministic application/policy validation.

## P4 — Eval-Driven Development

```text
requirement
→ evaluator/metric
→ baseline
→ candidate hypothesis
→ preregistration where material
→ implementation
→ repeated/sliced evaluation
→ diagnosis
→ promote | reject | no-change | no-selection
→ regression guard
```

Rules:

- deterministic truth beats an LLM judge where exact checks exist;
- semantic judges are non-gating until human calibrated;
- preserve failed/consumed attempts;
- distinguish preflight from scored evidence;
- separate infrastructure/admission failure from task-quality failure;
- do not selectively retry/repair failed scored attempts;
- evaluate operational conclusion **and** observable process: tool, arguments, evidence, stopping, escalation/action and safety.

## P5 — Evidence-backed claims only

A source commit, provider marketing page, CI result or successful preflight does not automatically prove a deployed production property.

Claim-specific remote evidence is required for production IAM/tenant safety, provider/TRACTIAN integration, capacity/SLO, backup/restore, RTO/RPO/HA, end-to-end security and operational time savings.

The current provider claim is explicitly **no final winner**. A future challenger must pass unchanged gates, fresh 85/85 and Academy live E2E before production promotion.

## P6 — User experience without sacrificing observability

Current task-driven pattern:

```text
Home
→ contextual Result / Evidence
→ Analyses for persisted history
→ Technical for specialist depth
```

Principles:

- answer/next step before internals;
- progressive disclosure instead of information deletion;
- visible status derives from safe server-owned evidence;
- no fabricated progress;
- no secrets/private evaluator truth/hidden chain-of-thought;
- accessibility and first-time-user comprehension are product requirements;
- lightweight product feedback remains separate from controlled research datasets.

## P7 — Documentation/provenance is part of the product

```text
active docs = current prospectively editable truth
frozen/history = immutable evidence for original scope
```

Rules:

- one mutable owner per question;
- provider selection has its own canonical mutable status;
- document by user task;
- update architecture/runbook/acceptance/security/changelog after material changes;
- preserve accepted ADRs/frozen progress/results;
- supersede prospectively rather than rewrite history;
- negative experiment results remain negative evidence;
- claims/diagrams must match the system that actually exists.

## Completion gate for material work

A workstream is done only when applicable conditions hold:

- [ ] explicit requirement/risk/user objective;
- [ ] baseline + decision question;
- [ ] credible alternatives researched;
- [ ] eligibility/cost boundary verified;
- [ ] metrics/hard gates defined;
- [ ] controlled evaluation exists where selection matters;
- [ ] stochastic uncertainty/repetition measured where relevant;
- [ ] failure/adversarial behavior checked;
- [ ] production fitness measured on the relevant path;
- [ ] no forbidden local production dependency;
- [ ] evaluator/judge validity established for gating metrics;
- [ ] decision/reversal trigger documented;
- [ ] regression protection exists;
- [ ] active documentation synchronized;
- [ ] frozen history unchanged;
- [ ] claims remain bounded by evidence.

If an applicable item is missing, the correct state is research/experimental/pending/non-claim — not a stronger label.
