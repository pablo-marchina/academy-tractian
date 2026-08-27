# Academy × TRACTIAN — Industrial Agent Engineering & Evaluation

Repository central do TAPI individual **Engenharia e Avaliação de Agentes Industriais** (Inteli × TRACTIAN).

## Project North Star

The repository has one fixed objective:

> **Deliver the strongest defensible version of the actual TRACTIAN × Inteli project by maximizing requested-scope coverage, academic evidence quality, scientific validity and production-path quality — following the repository development principles.**

The project is not optimized for number of experiments, framework novelty or architecture complexity. Optional components only earn a place when they measurably improve a requested capability, official evaluation criterion or material production risk.

The exact reviewed assignment/package/kickoff baseline and source discrepancies are recorded in [`research/tractian-source-baseline-2026-08-27.md`](research/tractian-source-baseline-2026-08-27.md).

## Start here

The repository is governed by four non-negotiable principles:

1. **systematic research + controlled comparison before material decisions**;
2. **production-first, never demo-first**;
3. **quantitative/adaptive by default with deterministic safety boundaries**;
4. **eval-driven engineering end to end**.

Read [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) before making a material project decision, then follow [`CONTRIBUTING.md`](CONTRIBUTING.md) as the normal development operating contract.

Canonical navigation:

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — mandatory development entry/exit procedure for tasks and PRs;
- [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) — sole human-readable source for current evidence-backed state and authorization;
- [`docs/NEXT-STEPS.md`](docs/NEXT-STEPS.md) — current short-horizon execution plan;
- [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) — formal requirements/rubric mapped to final capabilities and evidence;
- [`docs/ARCHITECTURE-ROADMAP.md`](docs/ARCHITECTURE-ROADMAP.md) — integrated agent/evaluator research-to-production architecture roadmap;
- [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) — master phase/deadline-protection map;
- [`docs/PROJECT-PROGRESS-LOG.md`](docs/PROJECT-PROGRESS-LOG.md) — chronological evidence/governance ledger;
- [`docs/REPOSITORY-GUIDE.md`](docs/REPOSITORY-GUIDE.md) — repository structure, source reconciliation and maintenance rules;
- [`docs/adr/`](docs/adr/) — material decision records;
- [`research/01-requirements-matrix.md`](research/01-requirements-matrix.md) — reconciled TAPI/package/kickoff requirement map;
- [`research/README.md`](research/README.md) — research evidence map;
- [`scripts/research/README.md`](scripts/research/README.md) — research executable lifecycle.

The root README intentionally does **not** duplicate the current experiment gate or checkpoint. Use `CURRENT-PROJECT-STATUS.md` for current-state claims.

## Development rule

New material work should start from current canonical `main`, use a focused branch/PR when practical and declare before implementation:

```text
requested requirement / rubric / material risk
→ P0 / P1 / justified P2 priority
→ current gate and authorization
→ change class
→ success/failure evidence
→ baseline/alternatives when material
```

The repository issue and PR templates mirror this contract. Their purpose is to keep development aligned with the plans and principles without adding governance CI.

## Project target

The official project requires one integrated delivery with both:

1. **Industrial Agent Engineering** — contextualize, investigate, request clarification when needed, execute justified actions, escalate safely and handle degraded/conflicting/unavailable information against the supplied industrial API.
2. **Agent Evaluation & Reliability** — evaluate tool choice, arguments, trajectory, evidence, operational conclusion, actions, escalation, safety, robustness and stability while preserving evaluation-only gold isolation.

Partner-quality guidance additionally emphasizes useful operational conclusions over exact wording, inspectable execution paths, safe human fallback, useful escalation handoffs, customer-safe communication and evidence-backed architecture trade-offs.

The final demonstration must exercise the real integrated agent + evaluator path rather than a benchmark-only artifact or scripted mock-only demo. Final delivery remains targeted for **2026-09-08**.

## Repository model

The repository intentionally preserves both active and historical scientific evidence. A file, script or workflow being present does not imply it is currently authorized to run or that its conclusion is current.

Use [`docs/REPOSITORY-GUIDE.md`](docs/REPOSITORY-GUIDE.md) before deleting, moving, rerunning or reinterpreting historical material.