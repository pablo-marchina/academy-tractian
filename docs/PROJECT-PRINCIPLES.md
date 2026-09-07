# Academy × TRACTIAN — Non-Negotiable Project Principles

**Status:** ACTIVE mandatory governance  
**Last rebaseline:** 2026-09-06 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Execution plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Documentation contract:** [`DOCUMENTATION-GUIDE.md`](DOCUMENTATION-GUIDE.md)

These principles override convenience, novelty, implementation momentum and prior provisional choices.

## North Star

> Deliver the strongest defensible TRACTIAN × Inteli product: a remote, multi-user, production-oriented **Agent + Evaluation** platform whose behavior, architecture, safety, quality and operational value are measurable and observable, while keeping **actual project cash cost = USD 0**.

A workstream must map to at least one of:

1. TAPI/delivered-package requirement;
2. academic evaluation criterion;
3. material production/security/reliability risk;
4. measurable user/operational-value requirement;
5. experiment required to choose among credible alternatives for the above.

If it maps to none, defer it.

## P0 — Real production, remote-first, never demo-first

The production serving path must not depend on:

- localhost/loopback services;
- a developer laptop/manual process;
- local model serving;
- SQLite/DuckDB/filesystem as production truth;
- test doubles/scripted scenario sources/mock provider responses;
- browser-provided tenant/role/permission authority.

Local execution is valid for tests/reproduction/benchmarks, not as evidence of the hosted production claim.

## P0 — USD0 is a hard eligibility gate

```text
actual project cash cost > USD 0            → INELIGIBLE
silent paid spillover / automatic billing   → FORBIDDEN
USD0 candidate                              → eligible for technical evaluation
USD0 + all applicable hard gates            → eligible for promotion
no eligible candidate passes                → NO_SELECTION / explicit blocker
```

Rules:

1. zero cost is necessary, not sufficient;
2. paid alternatives may be researched only as external references while this constraint applies;
3. quotas/free tiers must be understood and observed;
4. exhaustion must fail/degrade safely rather than spend;
5. no automatic paid fallback is allowed;
6. an explicit limitation is better than silently relaxing the constraint.

## Source hierarchy

When sources conflict:

1. current TAPI;
2. delivered TRACTIAN package/contract;
3. executable supplied API behavior/tests;
4. compatible kickoff/partner guidance;
5. project research/assumptions.

Record discrepancies instead of silently harmonizing them.

## P1 — Systematic research before material choices

Every material decision follows:

```text
decision question / measured gap
→ requirement/risk
→ hard constraints
→ primary-source research
→ simple baseline + credible eligible alternatives
→ preregistered metrics/hard gates
→ controlled quantitative comparison
→ failure/robustness/production-fit analysis
→ Pareto interpretation
→ decision + reversal trigger
→ ADR/registry
→ regression protection
```

Do not add a technology because it is popular or appears in an example.

Current examples of **NO_CHANGE unless evidence demands otherwise** include LangGraph migration, multi-agent, RAG/vector DB, persistent memory, MCP, Redis/Kafka and Kubernetes/microservices.

## Decision states

- `UNASSESSED` — insufficient evidence;
- `RESEARCHED` — credible evidence/options mapped;
- `INELIGIBLE` — violates a hard constraint;
- `QUALIFIED` — passes minimum gates;
- `PREFERRED` — best-supported eligible current candidate;
- `FROZEN` — accepted for the stated evidence scope;
- `REJECTED` — evidence rejects candidate;
- `NO_CHANGE` — current simpler path remains preferred;
- `NO_SELECTION` — no candidate deserves final promotion;
- `SUPERSEDED` — prospectively replaced by stronger evidence.

Release qualification and final selection are not the same thing. Release 0 may use a **provisional** provider while final Provider Tournament state remains `NO_SELECTION`.

## P2 — Quantitative before qualitative

When measurement is valid, prefer:

- rates/distributions;
- p50/p95/p99;
- paired deltas;
- uncertainty/effect sizes;
- failure/error rates;
- resource/quota/cash cost;
- repeat stability;
- calibration/agreement metrics;
- task completion/friction/value deltas.

Qualitative evidence complements measurements where semantics/user experience cannot be reduced safely to exact checks.

## P3 — Adaptive where valuable; deterministic where safety-critical

Potentially adaptive only after challenger evidence:

- investigation depth;
- evidence/tool ordering;
- stopping;
- clarify/abstain/escalate thresholds;
- provider routing among USD0-eligible candidates;
- bounded retry/backoff where semantics permit it;
- contextual resource budgets;
- visualization prioritization.

Always deterministic/hard-gated:

- authentication/tenant binding;
- RLS/authorization/permissions;
- schema validation;
- action confirmation/custody/idempotency/leases/fencing;
- privacy/field deny-lists;
- evaluator/gold isolation;
- hard turn/time/resource caps;
- USD0/no-paid-spillover boundary.

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
→ promote/reject/no-change
→ regression guard
```

- deterministic truth beats an LLM judge where exact checks exist;
- semantic judges are non-gating until human calibrated;
- preserve failed/consumed attempts;
- separate infrastructure failure from task-quality failure;
- evaluate the operational conclusion **and** observable process: tool, arguments, evidence, stopping, escalation/action and safety.

## P5 — Evidence-backed claims only

A source/CI result does not automatically prove deployed production properties.

Claim-specific remote evidence is required for claims such as:

- production IAM/tenant safety;
- provider/TRACTIAN integration;
- capacity/SLO;
- backup/restore;
- RTO/RPO/HA;
- end-to-end security;
- operational time savings.

The current Release 0 hosted evidence proves its exact read-only scope; broader final claims remain open until separately measured.

## P6 — User experience without sacrificing observability

The frontend should make the normal user task simple **and** preserve deep technical evidence for reviewers.

Current pattern:

```text
Results → Evidence → Investigation → Engineering
```

Principles:

- answer/next step before internals;
- progressive disclosure instead of information deletion;
- all visible status derived from safe server-owned evidence;
- no fabricated progress;
- no secrets/private evaluator truth/hidden chain-of-thought;
- accessibility and first-time-user comprehension are product requirements;
- lightweight product feedback must remain separate from controlled research datasets.

## P7 — Documentation/provenance is part of the product

Active docs and historical evidence have different jobs:

```text
active docs = current prospectively editable truth
frozen/history = immutable evidence for original scope
```

Rules:

- one mutable owner per question;
- document by user task (tutorial/how-to/reference/explanation);
- update architecture/runbook/acceptance/security/changelog with material changes;
- preserve accepted ADRs/frozen progress/results;
- supersede prospectively rather than rewriting historical rationale;
- claims and diagrams must match the system that actually exists.

## Completion gate for material work

A material workstream is done only when applicable conditions hold:

- [ ] explicit requirement/risk/user objective;
- [ ] baseline + decision question;
- [ ] credible alternatives researched;
- [ ] USD0/no-paid-spillover eligibility verified;
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

If an applicable item is missing, the correct status is research/experimental/pending/non-claim — not a stronger label.