# Development Operating Contract

This repository has one fixed objective:

> **Deliver the strongest defensible TRACTIAN × Inteli project against the actual assignment, delivered package, partner-quality guidance and official evaluation criteria, while preserving evidence integrity.**

This file defines the normal development procedure. It does not override frozen experiments, ADRs, `PROJECT-PRINCIPLES.md` or current authorization.

## 1. Read before material work

Read in this order:

1. [`docs/README.md`](docs/README.md) — documentation/source-of-truth map;
2. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) — non-negotiable governance;
3. [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) — current state and authorization;
4. [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) — active path/deadline;
5. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — architecture/stack/techniques;
6. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) — Definition of Done;
7. applicable frozen experiment/ADR artifacts.

For assignment interpretation, also use [`docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`](docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md).

If a new TAPI/package/API/kickoff/instructor source appears, reconcile requirements before continuing implementation momentum.

## 2. Start from canonical `main`

- start from current `main`;
- use a focused branch for material work;
- do not continue new work on stale historical branches;
- preserve frozen/source-pinned paths and consumed/failed evidence;
- do not rewrite history merely to make the repository look cleaner.

Change classes:

- **A — documentation/navigation only:** no behavior, authorization, requirement or architecture semantics change;
- **B — non-semantic engineering:** plumbing/refactor intended to preserve agent/evaluator behavior;
- **C — material semantic/experimental/product:** model/provider, prompt, tools/schemas, safety, evaluator, retrieval, memory, orchestration, deployment semantics, final scope or claims.

Class C requires a focused branch + tracked planning record + full evidence loop. When uncertain, treat the change as C.

## 3. Map work to delivery before coding

Every material task must map to at least one of:

- a P0/P1 row in `docs/DELIVERY-ACCEPTANCE.md`;
- a TAPI/academic criterion;
- a material security/reliability/production risk;
- an experiment required to choose among credible alternatives.

Priority:

```text
P0 — requested capability + trustworthy evaluation
P1 — production/security/reliability/quality required to operate P0 well
P2 — optional complexity that must earn its place with evidence
```

If it maps to none, defer it.

## 4. Authorization gate

Before experimental/private/external-provider/consequential execution, answer:

- What current gate permits this exact action?
- Which frozen artifact/ADR defines it?
- Which inputs are immutable?
- What outputs/custody are allowed?
- What downstream work remains forbidden?
- Which credentials/private data are permitted in the environment?
- What is the fail-closed condition?

**Code existing is not authorization to run it.**

## 5. Material decision workflow

For Class C:

```text
requirement/risk
→ decision question + hard constraints
→ primary-source research
→ credible alternatives + simple baseline
→ preregistered comparison
→ quantitative/repeated evaluation
→ robustness/failure analysis
→ production-fit trade-offs
→ Pareto interpretation
→ ADR/reversal trigger
→ state decision
→ regression protection
```

Do not add a technology because it is popular or appears as a TAPI example. Optional RAG, vector DB, multi-agent, memory, MCP, adaptive routing or orchestration migration carries the burden of proof.

## 6. Implementation rules

- never mutate frozen evidence in place;
- never expose evaluator-private/gold/blind material to runtime;
- keep identity/seed/authorization outside model control where required;
- preserve source/config/artifact provenance;
- keep runtime and evaluator supervision separated;
- use deterministic checks when deterministic truth exists;
- preserve failed/consumed attempts;
- do not silently repair incomplete scientific packets;
- keep the agent-facing tool contract explicit;
- provider/model/tool failure must not silently become an unsafe action or unsupported conclusion;
- traces must diagnose model/tool/evidence/policy/action/escalation/output failures;
- observability/browser plumbing must not change agent/evaluator decisions;
- raw sensitive trace/provider/evaluator material must not cross the browser boundary.

## 7. Definition of Ready

A material task is ready only when:

- [ ] requirement/rubric/risk mapping is explicit;
- [ ] P0/P1/P2 is justified;
- [ ] current status/gate is checked;
- [ ] scope/non-goals are explicit;
- [ ] success/fail-closed evidence is defined;
- [ ] simple baseline exists when comparison matters;
- [ ] frozen/private boundaries are understood;
- [ ] affected canonical docs are identified;
- [ ] deadline impact is acceptable under `docs/DELIVERY-PLAN.md`.

## 8. Definition of Done for a change

Before merge:

- [ ] capability/risk/criterion is actually improved or closed;
- [ ] applicable tests/evals/regressions pass;
- [ ] quantitative evidence supports measurable claims;
- [ ] robustness/failure behavior was checked where material;
- [ ] no unauthorized gate/provider/private partition was accessed;
- [ ] frozen/source-pinned evidence was not silently changed;
- [ ] limitations/trade-offs are recorded;
- [ ] ADR exists for a material architecture/semantic decision;
- [ ] `CURRENT-PROJECT-STATUS.md` updated if state/authorization changed;
- [ ] `DELIVERY-PLAN.md` updated if priority/path/deadline changed;
- [ ] `ARCHITECTURE.md` updated if durable architecture/stack changed;
- [ ] `DELIVERY-ACCEPTANCE.md` / TAPI crosswalk updated if requirements/DoD changed;
- [ ] runbook updated if executable commands/recovery changed;
- [ ] progress/evidence record added when historically material;
- [ ] claims remain no stronger than evidence.

## 9. Pull-request rule

Use `.github/pull_request_template.md`. A material PR must state:

- why the work exists;
- requirement/risk/rubric mapping;
- change class and priority;
- current gate/authorization;
- baseline/alternatives for material choices;
- evidence/tests;
- regressions/limitations;
- canonical docs affected.

Do not merge with unresolved authorization, hidden-data, experiment-semantic or claim ambiguity.

## 10. After merge

1. verify `main` contains the intended result;
2. record immutable evidence/ADR/result where applicable;
3. update only the canonical document that owns the changed question;
4. add history to progress/evidence rather than duplicating status everywhere;
5. start the next task from current `main`.

## 11. Deadline discipline

Final delivery is 2026-09-08. Near the deadline:

```text
P0/P1 closure
→ integration
→ regression/security
→ reproduction
→ documentation
→ real-path demonstration
→ optional polish
```

A late change that cannot be properly retested should not silently enter the final release.

## 12. Five-question check

Before every material change, answer:

1. What requested outcome does this improve?
2. What evidence will prove it?
3. What simpler alternative is the baseline?
4. What gate allows it now?
5. Which canonical document changes afterward?

If any answer is unclear, the next action is planning/research rather than implementation.