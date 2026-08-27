# Development Operating Contract

This repository is developed against one fixed objective:

> **Deliver the strongest defensible TRACTIAN × Inteli project against the actual assignment, delivered package, partner-quality guidance and official evaluation criteria, while following P1–P4.**

This file defines the **normal operating procedure for development**. It does not replace experiment freezes, project principles or current authorization.

## 1. Read before starting any work

Before changing code, prompts, evaluators, architecture, research, deployment or durable documentation, read in this order:

1. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) — non-negotiable North Star and P1–P4;
2. [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) — current state and authorization;
3. [`docs/NEXT-STEPS.md`](docs/NEXT-STEPS.md) — current execution path;
4. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) — what final delivery must prove;
5. [`docs/ARCHITECTURE-ROADMAP.md`](docs/ARCHITECTURE-ROADMAP.md) — durable architecture direction and decision register;
6. [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) — macro phases and deadline protection;
7. [`docs/REPOSITORY-GUIDE.md`](docs/REPOSITORY-GUIDE.md) — repository/source-of-truth rules;
8. the applicable frozen experiment/decision artifacts for the work being touched.

If a new TAPI/package/API/kickoff/instructor source exists, run the Source / Brief Reconciliation Gate before continuing implementation.

## 2. Start from canonical `main`

`main` is the canonical integration branch.

For new development:

1. start from the current `main` head;
2. use a focused branch for material work;
3. keep one primary decision/workstream per branch/PR when practical;
4. do not continue new development on a stale historical branch merely because old research lives there;
5. preserve frozen/source-pinned historical paths and intentionally historical branches instead of rewriting history to make the repository look cleaner.

A historical branch that is an ancestor of `main` may remain intentionally behind when its name/state is itself useful provenance. A long-lived working branch intended for continued work should instead be explicitly reconciled with current `main` before new development.

Suggested prefixes are `research/`, `feature/`, `fix/`, `docs/`, `eval/`, `prod/` and `refactor/`, chosen by the actual work rather than by desired perception.

## 3. Classify the change before implementation

Every task must declare one class.

### A — navigation/documentation-only

No behavior, experiment semantics, authorization, requirement interpretation or architecture decision changes.

Examples: typo fixes, links, indexes, prose clarification that does not change meaning.

### B — non-semantic engineering

Implementation/infrastructure changes intended to preserve behavior and experiment semantics.

Examples: import-path repair, packaging/repository organization, observability plumbing that does not change agent/evaluator decisions.

This class still requires regression evidence sufficient to prove that behavior was preserved.

### C — material semantic/experimental/product change

Any change to agent behavior, prompts, model/provider, tools, tool schemas, safety policy, evaluator/judge, scoring semantics, retrieval, memory, orchestration, adaptive policy, production architecture, deployment semantics, final scope or claims.

Class C must follow the complete P1–P4 decision loop and may not be disguised as refactoring.

If uncertain, treat the change as Class C until proven otherwise.

## 4. Map the work to the delivery before coding

Every material task must map to at least one of:

- a P0/P1 row in `docs/DELIVERY-ACCEPTANCE.md`;
- an official academic evaluation criterion;
- a material security/reliability/production risk that can block the requested delivery; or
- an experiment required to choose among credible alternatives for one of the above.

Classify the priority:

```text
P0 — required capability / trustworthy evaluation
P1 — production, security, reliability or partner-quality needed to operate P0 well
P2 — optional enhancement that must earn its place quantitatively
```

If a task maps to none, defer it.

## 5. Authorization gate before execution

Before running anything with experimental, private, external-provider or hidden-data consequences, answer explicitly:

- What is the current authorized gate?
- Which frozen artifact/closure authorizes this exact action?
- What inputs are immutable?
- What outputs may be produced?
- What later gates are still forbidden?
- What credentials/private/blind data are allowed in this execution environment?
- What is the fail-closed condition?

**Technical capability is not authorization.** A script/workflow existing in the repository does not authorize running it.

## 6. Material decision workflow

For every Class C decision:

```text
requirement / rubric objective / material risk
→ decision question + hard constraints
→ systematic primary-source research
→ credible materially different alternatives
→ simple/null baseline
→ preregistered comparison
→ quantitative controlled evaluation
→ uncertainty/repeated behavior
→ robustness/failure analysis
→ production/partner-quality fit
→ trade-off/Pareto interpretation
→ ADR + reversal triggers
→ state decision
→ regression protection
```

Do not select a technology because it is already implemented, fashionable, free, expensive, familiar or mentioned as an example in the TAPI.

For optional complexity — RAG, vector DB, reranking, multi-agent, persistent memory, MCP, adaptive routing, richer UI, extra backend simulations — the burden of proof is on the complexity.

## 7. Implementation rules

During implementation:

- do not mutate frozen artifacts in place;
- do not expose evaluator-only gold/private/blind material to the agent runtime;
- keep identity/authorization and evaluation seed outside model control where required;
- preserve source, configuration and artifact provenance;
- keep agent/runtime and evaluator supervision separated;
- use deterministic checks where deterministic truth exists;
- preserve failed/consumed attempts as evidence;
- do not silently repair incomplete scientific packets;
- keep the stable agent-facing tool contract explicit;
- do not let provider/model/tool failure silently become an unsafe action or unsupported conclusion;
- prefer operationally correct conclusions over brittle exact wording when the evaluator contract supports that distinction;
- make observable traces sufficient to diagnose tool, evidence, action, escalation and response failures.

## 8. Definition of Ready for a material task

A material task is ready to implement only when:

- [ ] requirement/rubric/risk mapping is explicit;
- [ ] priority is P0, P1 or justified P2;
- [ ] current project gate/authorization has been checked;
- [ ] scope and non-goals are explicit;
- [ ] success/failure evidence is defined;
- [ ] a simple baseline exists when a comparison is material;
- [ ] hidden/private/frozen boundaries are understood;
- [ ] affected canonical documents are identified;
- [ ] deadline impact is acceptable under `PROJECT-PLAN.md`.

## 9. Definition of Done for a change

A change is not done because the code runs.

Before merge, verify all applicable items:

- [ ] requested capability/risk/criterion is actually improved or closed;
- [ ] applicable tests/evals/regressions pass;
- [ ] quantitative evidence supports any improvement claim;
- [ ] failure/robustness behavior was checked when material;
- [ ] no unauthorized partition/provider/gate was accessed;
- [ ] no frozen/source-pinned artifact was silently changed;
- [ ] trade-offs and limitations are documented;
- [ ] ADR exists for a material decision;
- [ ] `DELIVERY-ACCEPTANCE.md` is updated if coverage changed;
- [ ] `ARCHITECTURE-ROADMAP.md` is updated if durable architecture direction changed;
- [ ] `PROJECT-PLAN.md` is updated if phase/deadline allocation changed;
- [ ] `CURRENT-PROJECT-STATUS.md`, machine checkpoint and progress ledger are updated if state/authorization changed;
- [ ] `NEXT-STEPS.md` is updated if the current execution path/blocker changed;
- [ ] claims remain no stronger than the evidence.

## 10. Pull-request rule

Use the repository PR template. A material PR should make review possible without reconstructing the entire project history.

The PR must state:

- why the work exists;
- which requirement/risk/rubric row it serves;
- current gate and authorization boundary;
- change class and P0/P1/P2 priority;
- baseline/alternatives for material choices;
- evidence produced;
- regressions/risks;
- canonical docs updated or explicitly unaffected.

Do not merge a material PR with unresolved ambiguity about authorization, hidden-data access, experiment semantics or the final claim it supports.

## 11. After merge

After a material merge into `main`:

1. verify `main` contains the intended result;
2. record the evidence/decision in the appropriate canonical location;
3. update status/checkpoint/ledger if state changed;
4. update `NEXT-STEPS.md` if the execution path changed;
5. update acceptance/architecture/plan only when their responsibilities changed;
6. reconcile any long-lived working branch that is intentionally kept alive;
7. start the next task from current `main`, not from a stale pre-merge state.

## 12. Deadline discipline

The final delivery target is 2026-09-08.

As the deadline approaches, evidence-backed P0/P1 closure, integration, regression, reproducibility, documentation and real-path demonstration outrank speculative P2 work.

A late change that cannot be re-evaluated/regression-tested should not silently enter the final release.

## 13. Rule of thumb

Before every material change, be able to answer in one sentence each:

1. **What requested outcome does this improve?**
2. **What evidence will prove it?**
3. **What simpler alternative are we comparing against?**
4. **What gate allows this work now?**
5. **What must be updated after it succeeds or fails?**

If any answer is unclear, the next action is planning/research — not implementation.
