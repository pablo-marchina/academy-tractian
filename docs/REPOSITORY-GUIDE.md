# Repository Guide — Structure, Sources of Truth and Cleanup Policy

**Status:** canonical repository organization guide  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Development operating contract:** [`../CONTRIBUTING.md`](../CONTRIBUTING.md)  
**Audited project source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)

## 1. Purpose

This repository contains both a scientific evidence trail and the code that executes it. Repository maintenance must improve navigation and correctness without destroying provenance, frozen paths, failed experiments or consumed attempts.

The repository uses **logical cleanup before physical relocation**: index/classify evidence first; move/delete only files proven not to be frozen, referenced, source-pinned or required for reproduction.

The repository must also remain aligned with the actual TRACTIAN/Inteli brief. New upstream project material triggers requirements/plan reconciliation before implementation momentum is allowed to continue unchanged.

`CONTRIBUTING.md` is the normal entry/exit procedure for development. This guide defines repository/source-of-truth policy; the contribution contract defines what a developer must check before starting, merging and reconciling work.

## 2. Two source-of-truth hierarchies

Do not mix **project-requirement truth** with **experiment-state truth**.

### 2.1 Upstream project/source hierarchy

For what the project is supposed to deliver:

1. **[UPDATED] TAPI** — formal scope, deliverables and academic criteria;
2. **delivered TRACTIAN project package** — Student Guide, agent/eval material, contract/docs/data as actually delivered;
3. **executable supplied API behavior/tests** — operational truth for the simplified API when prose and implementation differ;
4. **kickoff partner guidance** — product-quality guidance compatible with written sources;
5. **project-generated research/assumptions/extensions** — hypotheses, never replacements for upstream requirements.

Current audited identities/discrepancies are recorded in `research/tractian-source-baseline-2026-08-27.md`.

### 2.2 Repository/experiment hierarchy

For what is currently true/authorized inside this repository:

1. **Frozen experiment manifests/results/closures** — exact semantics/evidence for that specific experiment/gate.
2. **`docs/PROJECT-PRINCIPLES.md`** — repository-wide development governance and fixed North Star.
3. **`docs/CURRENT-PROJECT-STATUS.md`** — sole canonical human-readable current state/authorization.
4. **latest machine checkpoint linked by current status** — structured snapshot.
5. **`docs/NEXT-STEPS.md`** — short-horizon execution plan.
6. **`docs/DELIVERY-ACCEPTANCE.md`** — requirements/rubric-to-final-evidence coverage map.
7. **`docs/ARCHITECTURE-ROADMAP.md`** — durable integrated agent/evaluator architecture roadmap.
8. **`docs/PROJECT-PLAN.md`** — macro phases/deadline-protection milestones.
9. **`docs/PROJECT-PROGRESS-LOG.md`** — chronological ledger.
10. **ADRs** — material decision context/status for stated scope.
11. **README/index files** — navigation/lifecycle guidance only.
12. **historical research narratives** — evidence/context, not current authorization.

`CONTRIBUTING.md` and GitHub templates are process controls. They do not override experiment truth or current authorization.

A frozen experiment can govern its own semantics without redefining the external assignment. A historical statement is not current state merely because the file exists.

## 3. Repository layout

| Path | Role | Mutation policy |
|---|---|---|
| `README.md` | concise entrypoint/navigation | do not duplicate current gate/checkpoint |
| `CONTRIBUTING.md` | canonical development operating contract | update when normal development entry/exit policy changes; do not redefine experiment truth |
| `.github/ISSUE_TEMPLATE/development-task.md` | governed task-planning prompt | keep aligned with `CONTRIBUTING.md` and P0/P1/P2 mapping |
| `.github/pull_request_template.md` | governed review/merge prompt | keep aligned with `CONTRIBUTING.md`, canonical docs and authorization rules |
| `docs/PROJECT-PRINCIPLES.md` | mandatory project-wide governance/North Star | change only through explicit governance decision/source reconciliation |
| `docs/CURRENT-PROJECT-STATUS.md` | sole current human state/authorization | update on evidence-backed gate/state change |
| `docs/NEXT-STEPS.md` | short-horizon operational plan | update when gate/blocker/source changes; closed steps move to ledger |
| `docs/DELIVERY-ACCEPTANCE.md` | requirement/rubric/final-evidence crosswalk | update when source interpretation, scope or evidence coverage changes |
| `docs/ARCHITECTURE-ROADMAP.md` | durable integrated research-to-production architecture | update when durable architecture direction/decision scope changes |
| `docs/PROJECT-PLAN.md` | macro phases, priorities and deadline protection | keep compact; link rather than duplicate detailed state |
| `docs/PROJECT-PROGRESS-LOG.md` | chronological evidence/governance ledger | append/curate history; no mutable current-state section |
| `docs/adr/` | material decision records and index | supersede with new ADR rather than rewrite history |
| `docs/archive/` | superseded non-binding narrative/planning docs | archive only when path is safe to move |
| `docs/research/` | human handoff/custody docs for protected research tracks | preserve access-boundary semantics |
| `research/` | systematic research/history and audited source baseline | historical numbered records remain stable |
| `research/experiments/` | preregistrations/designs/eligibility artifacts | version; do not mutate after freeze |
| `research/frozen/` | immutable contracts/maps/authorizations/inputs | never rewrite in place after freeze |
| `research/fixtures/` | allowed fixture/public test material | do not mix with private evaluator/blind outcomes |
| `research/results/` | canonical machine-readable results/closures/checkpoints | add new snapshot/version rather than falsify an old one |
| `research/live/` | intentionally committed live evidence | treat committed live evidence as immutable |
| `scripts/research/` | reproducible research/evaluation runners | preserve source-pinned versions; new gate/version for semantic changes |
| `.github/workflows/` | execution wrappers/CI/live experiment plumbing | existence does not imply authorization |

A future production code boundary (`src/`, `tests/`, deployment/config surfaces, etc.) should be created only after the applicable architecture decision supports it. Do not rename `scripts/research/` into production code.

## 4. Documentation responsibilities

Use one document per question:

```text
How do I start/review/merge development?     CONTRIBUTING.md
What did TRACTIAN/Inteli actually give/ask?  research/tractian-source-baseline-*.md + requirements matrix
Where are we?                               CURRENT-PROJECT-STATUS.md
What do we do next?                         NEXT-STEPS.md
What must final delivery prove?             DELIVERY-ACCEPTANCE.md
Where must the system go?                   ARCHITECTURE-ROADMAP.md
What are the project phases/deadline?       PROJECT-PLAN.md
How did we get here?                        PROJECT-PROGRESS-LOG.md
Why was a decision made?                    docs/adr/*
How is the repo maintained?                 REPOSITORY-GUIDE.md
```

README/index files point to these documents and describe directory semantics. They should not carry mutable experiment snapshots.

## 5. Manual maintenance and development gates

Repository governance remains lightweight and does **not** require adding governance CI for ordinary synchronization. The gates below are manual, but they are mandatory for the applicable event.

### 5.1 Source / Brief Reconciliation Gate

Use whenever a new/updated TAPI, partner package, API contract, kickoff clarification or instructor requirement is received.

Required sequence:

1. preserve/identify the exact upstream source and hash where feasible;
2. inspect delivered files/executable behavior rather than relying on summary prose alone;
3. record source discrepancies without silently rewriting upstream evidence;
4. update `research/01-requirements-matrix.md`;
5. update `DELIVERY-ACCEPTANCE.md` if final evidence obligations change;
6. update `PROJECT-PRINCIPLES.md` only when the durable North Star/governance interpretation changes;
7. review `NEXT-STEPS.md`, `ARCHITECTURE-ROADMAP.md` and `PROJECT-PLAN.md` for impact;
8. record the reconciliation in `PROJECT-PROGRESS-LOG.md`.

The source reconciliation itself does not advance scientific experiment gates unless a frozen protocol explicitly says otherwise.

### 5.2 Development Entry Gate

Use before every new material task or PR.

Required sequence:

1. start from/reconcile against current canonical `main`;
2. read `PROJECT-PRINCIPLES.md`, `CURRENT-PROJECT-STATUS.md`, `NEXT-STEPS.md`, `DELIVERY-ACCEPTANCE.md`, `ARCHITECTURE-ROADMAP.md` and applicable frozen artifacts;
3. classify the change as A documentation-only, B non-semantic engineering or C material semantic/experimental/product change;
4. map it to a P0/P1 acceptance row, official rubric dimension, material risk or required comparison;
5. verify current gate/authorization and forbidden downstream work;
6. define success/failure evidence before implementation where feasible;
7. for Class C, identify the simple/null baseline and credible alternatives before selecting a solution;
8. identify canonical documents that would need updating if the work succeeds/fails;
9. verify the deadline impact under `PROJECT-PLAN.md`.

Use `.github/ISSUE_TEMPLATE/development-task.md` when planning a tracked task and `.github/pull_request_template.md` when reviewing/merging a change.

If the task cannot answer the five questions in the final section of `CONTRIBUTING.md`, the next step is planning/research, not implementation.

### 5.3 Structure Gate

Use when introducing a new top-level category, durable artifact family or production code surface.

Check:

- is the new path's responsibility distinct from an existing path?;
- is its mutation/freeze policy clear?;
- are navigation/source-of-truth docs updated?;
- does the change preserve frozen/source-pinned paths?;
- does it simplify navigation rather than add another competing source of truth?

### 5.4 Status Gate

Use whenever an evidence-backed project gate/state changes.

Update together:

1. new immutable result/freeze/closure;
2. `CURRENT-PROJECT-STATUS.md`;
3. a new machine checkpoint when the project snapshot changes materially;
4. `PROJECT-PROGRESS-LOG.md`.

Do not update README/index files with copied current-state snapshots.

### 5.5 Next-Steps Gate

Immediately after a status transition, source reconciliation or material blocker change:

- remove completed operational instructions from `NEXT-STEPS.md`;
- replace them with the newly authorized short-horizon sequence;
- ensure no step crosses a gate not opened by the new freeze;
- prioritize P0/P1 delivery acceptance over optional P2 complexity;
- preserve deadline-protection windows;
- move historical details to the progress ledger instead of accumulating them in the plan.

### 5.6 Architecture Gate

Use when research/source evidence changes a durable material architecture decision or decision scope.

Update, as applicable:

- `ARCHITECTURE-ROADMAP.md` for durable direction/decision-register changes;
- `DELIVERY-ACCEPTANCE.md` if requirement coverage/claim changes;
- a new ADR for an actual material decision;
- `PROJECT-PLAN.md` only if macro phases/priorities/deadline allocation change;
- `CURRENT-PROJECT-STATUS.md` only if current state/claims changed.

Every final architecture component must map to a delivery requirement, official rubric dimension, material risk or evidence showing it improves a required capability over a simpler baseline.

Do not rewrite old ADRs to make history consistent with later evidence.

### 5.7 Phase Closure Gate

Before declaring a macro phase complete:

- verify required evidence/closures exist;
- verify all applicable security/evaluator boundaries;
- verify literal state terminology (`QUALIFIED`, `PREFERRED`, `FROZEN`, etc.);
- verify the next phase has explicit entry conditions;
- review `DELIVERY-ACCEPTANCE.md` for newly closed/still-open P0/P1 gaps;
- verify official rubric evidence is accumulating, not deferred entirely to final documentation;
- before final delivery, require every applicable P0 row to have evidence or an explicit evidence-honest scope limitation;
- update status, ledger, next steps, acceptance map and project plan coherently when affected.

## 6. What may be deleted or moved

A file may be physically moved/deleted only when all applicable checks are true:

```text
not frozen
AND not referenced by a frozen artifact
AND not source-pinned by Git blob/path
AND not a canonical result/closure/source audit
AND not required to reproduce a consumed/failed experiment
AND not referenced by an active workflow/plan/ADR
AND replacement/navigation has been updated
```

If any condition is uncertain, keep the path stable and classify it through an index instead.

## 7. Historical evidence policy

Failed experiments, operational failures and consumed one-shot attempts are evidence. They must not be removed merely because they are obsolete for execution.

Use these lifecycle labels when useful:

- `ACTIVE` — relevant to current authorized path;
- `FROZEN` — immutable evidence/input/decision;
- `CONSUMED` — attempt cannot be reused/rerun but remains evidence;
- `HISTORICAL` — retained for reproducibility/context;
- `SUPERSEDED` — replaced by stronger evidence/decision.

## 8. Material development-change workflow

Any material change to architecture, model, prompt, evaluator, runtime, retrieval, memory, tools, safety, adaptive policy, deployment or integration follows:

```text
upstream requirement / rubric objective / material risk
→ decision question → constraints → systematic research
→ credible alternatives + simple baseline
→ preregistered comparison → quantitative eval → robustness
→ production/partner-quality fit → ADR → state decision → regression
```

Do not use cleanup/refactoring as a way to bypass this process. A semantic behavior change hidden inside a rename, dependency update or infrastructure refactor is still material.

## 9. Security and evidence boundaries

Never commit secrets, credentials, hidden blind outcomes, private oracle rows or private scorer data that the frozen protocol forbids from repository exposure.

Evaluator/private/blind material remains isolated from candidate-generation/runtime code according to the relevant frozen protocol and the delivered agent/eval boundary.

A new scorer/workflow may define an evaluator-side file interface without committing or reconstructing private truth. Custody/provisioning must be explicitly established before execution.

## 10. Environment/configuration convention

Local secret files remain ignored. When a production configuration surface is introduced, a non-secret template such as `.env.example` may be versioned while real `.env*` files remain excluded.

Do not create production packaging/deployment files merely to signal maturity before the production architecture is evidence-backed.

## 11. Future reference-safe physical cleanup

After the current evaluation/selection path closes, perform a dedicated **reference-safe physical cleanup**:

1. build a path/reference graph from workflows, scripts, frozen JSON and Markdown links;
2. identify truly unreferenced generated/transient files;
3. classify historical workflows/scripts as retained vs safely archivable;
4. move only unpinned narrative files into `docs/archive/` or a clearly versioned historical research location;
5. run link/path/reproducibility checks before and after the move;
6. record the cleanup if it affects reproducibility paths.

Until that audit exists, preserving a seemingly messy frozen path is preferable to breaking scientific provenance.