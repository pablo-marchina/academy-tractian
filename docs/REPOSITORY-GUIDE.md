# Repository Guide — Structure, Sources of Truth and Cleanup Policy

**Status:** canonical repository organization guide  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

## 1. Purpose

This repository contains both a scientific evidence trail and the code that executes it. Cleanup must improve navigation and correctness without destroying provenance, frozen paths, failed experiments or consumed attempts.

The repository therefore uses **logical cleanup before physical relocation**: index and classify evidence first; move/delete only files proven not to be frozen, referenced, source-pinned or needed for reproduction.

## 2. Source-of-truth hierarchy

When documents appear to conflict, use this order:

1. **Frozen experiment manifests/results/closures** — exact semantics and evidence for the specific experiment/gate.
2. **`docs/PROJECT-PRINCIPLES.md`** — repository-wide development governance.
3. **`docs/CURRENT-PROJECT-STATUS.md`** — sole canonical human-readable current state and current authorization.
4. **latest machine checkpoint linked by current status** — structured project snapshot.
5. **`docs/NEXT-STEPS.md`** — canonical short-horizon execution plan from the current state.
6. **`docs/DELIVERY-ACCEPTANCE.md`** — active requirements-to-final-evidence coverage map.
7. **`docs/ARCHITECTURE-ROADMAP.md`** — canonical general research-to-production/system architecture roadmap.
8. **`docs/PROJECT-PLAN.md`** — macro phases and delivery milestones.
9. **`docs/PROJECT-PROGRESS-LOG.md`** — chronological historical ledger.
10. **ADRs** — material decision context/status for their stated scope.
11. **README/index files** — navigation/lifecycle guidance only; they must not independently redefine current state or experiment semantics.
12. **historical research narratives** — evidence/context, not current authorization.

A historical statement is not current state merely because the file still exists.

## 3. Repository layout

| Path | Role | Mutation policy |
|---|---|---|
| `README.md` | concise entrypoint/navigation | do not duplicate current gate/checkpoint |
| `docs/PROJECT-PRINCIPLES.md` | mandatory project-wide governance | change only through explicit governance decision |
| `docs/CURRENT-PROJECT-STATUS.md` | sole current human state/authorization | update on evidence-backed gate/state change |
| `docs/NEXT-STEPS.md` | short-horizon operational plan | update when gate/blocker changes; closed steps move to ledger |
| `docs/DELIVERY-ACCEPTANCE.md` | requirement/capability/final-evidence crosswalk | update when requirement interpretation, intended final scope or evidence coverage changes |
| `docs/ARCHITECTURE-ROADMAP.md` | macro research-to-production/system architecture | update only when durable architecture direction/decision scope changes |
| `docs/PROJECT-PLAN.md` | macro phases and milestones | keep compact; link to status/next steps/acceptance/architecture instead of duplicating them |
| `docs/PROJECT-PROGRESS-LOG.md` | chronological evidence ledger | append/curate history; no mutable current-state section |
| `docs/adr/` | material decision records and index | supersede with new ADR rather than silently rewriting historical conclusions |
| `docs/archive/` | superseded non-binding narrative/planning docs | archive only when not needed as a stable frozen/source-pinned path |
| `docs/research/` | human handoff/custody docs for protected research tracks | preserve access-boundary semantics |
| `research/` | systematic research records and historical narrative | historical numbered records remain stable; use `research/README.md` as index |
| `research/experiments/` | preregistrations/designs/eligibility artifacts | version; do not mutate after freeze |
| `research/frozen/` | immutable contracts, maps, authorizations and frozen inputs | never rewrite in place after freeze |
| `research/fixtures/` | allowed fixtures/public test material | do not mix with private evaluator or blind outcomes |
| `research/results/` | canonical machine-readable results/closures/checkpoints | preserve snapshots; add new version/checkpoint rather than falsifying an old one |
| `research/live/` | live evidence when intentionally committed | treat committed live evidence as immutable |
| `scripts/research/` | reproducible research/evaluation runners | preserve source-pinned versions; create new gate/version for semantic changes |
| `.github/workflows/` | execution wrappers/CI/live experiment plumbing | workflow existence does not imply authorization |

A future production code boundary (`src/`, `tests/`, deployment/config surfaces, etc.) should be created only after the applicable architecture decision supports it. Do not rename `scripts/research/` into production code.

## 4. Documentation responsibilities

Use one document per question:

```text
Where are we?                     CURRENT-PROJECT-STATUS.md
What do we do next?               NEXT-STEPS.md
What must final delivery prove?   DELIVERY-ACCEPTANCE.md
Where must the system go?         ARCHITECTURE-ROADMAP.md
What are the project phases?      PROJECT-PLAN.md
How did we get here?              PROJECT-PROGRESS-LOG.md
Why was a decision made?          docs/adr/*
How is the repo maintained?       REPOSITORY-GUIDE.md
```

README/index files point to these documents and describe directory semantics. They should not carry mutable experiment snapshots.

## 5. Manual maintenance gates

Repository maintenance is intentionally lightweight and does **not** require adding governance CI for ordinary documentation synchronization.

Apply these checks manually whenever the corresponding event occurs.

### 5.1 Structure Gate

Use when introducing a new top-level category, durable artifact family or production code surface.

Check:

- is the new path's responsibility distinct from an existing path?;
- is its mutation/freeze policy clear?;
- are navigation/source-of-truth docs updated?;
- does the change preserve frozen/source-pinned paths?

### 5.2 Status Gate

Use whenever an evidence-backed project gate/state changes.

Update together:

1. new immutable result/freeze/closure;
2. `CURRENT-PROJECT-STATUS.md`;
3. a new machine checkpoint when the project snapshot changes materially;
4. `PROJECT-PROGRESS-LOG.md`.

Do not update README/index files with a copied current-state snapshot.

### 5.3 Next-Steps Gate

Immediately after a status transition or material blocker change:

- remove completed operational instructions from `NEXT-STEPS.md`;
- replace them with the newly authorized short-horizon sequence;
- ensure no step crosses a gate not opened by the new freeze;
- re-check whether the next work prioritizes P0/P1 delivery acceptance rather than optional P2 complexity;
- move historical details into the progress ledger instead of accumulating them in the plan.

### 5.4 Architecture Gate

Use when research changes a durable material architecture decision or decision scope.

Update, as applicable:

- `ARCHITECTURE-ROADMAP.md` for durable direction/decision register changes;
- `DELIVERY-ACCEPTANCE.md` if requirement coverage/claim changes;
- a new ADR for the actual material decision;
- `PROJECT-PLAN.md` only if macro phases/milestones change;
- `CURRENT-PROJECT-STATUS.md` only if the current project state/claims changed.

Every final architecture component must map to a delivery requirement, a material risk or evidence showing it improves a required capability over a simpler baseline.

Do not rewrite old ADRs to make history consistent with later evidence.

### 5.5 Phase Closure Gate

Before declaring a macro phase complete:

- verify required evidence/closures exist;
- verify all applicable security/evaluator boundaries;
- verify state terminology (`QUALIFIED`, `PREFERRED`, `FROZEN`, etc.) is used literally;
- verify the next phase has explicit entry conditions;
- review `DELIVERY-ACCEPTANCE.md` for newly closed or still-open P0/P1 gaps;
- before final delivery, require every applicable P0 row to have evidence or an explicit evidence-honest scope limitation;
- update status, ledger, next steps, acceptance map and project plan coherently when affected.

## 6. What may be deleted or moved

A file may be physically moved/deleted only when all applicable checks are true:

```text
not frozen
AND not referenced by a frozen artifact
AND not source-pinned by Git blob/path
AND not a canonical result/closure
AND not required to reproduce a consumed/failed experiment
AND not referenced by an active workflow/plan/ADR
AND replacement/navigation has been updated
```

If any condition is uncertain, keep the path stable and classify it through an index instead.

## 7. Historical evidence policy

Failed experiments, operational failures and consumed one-shot attempts are evidence. They must not be removed merely because they are obsolete for execution.

Use these lifecycle labels in indexes/ADRs when useful:

- `ACTIVE` — relevant to the current authorized path;
- `FROZEN` — immutable evidence/decision input;
- `CONSUMED` — attempt cannot be reused/rerun but remains evidence;
- `HISTORICAL` — retained for context/reproducibility, not current authorization;
- `SUPERSEDED` — replaced by a better-supported decision while retained in history.

## 8. Material development-change workflow

Any material change to architecture, model, prompt, evaluator, runtime, retrieval, memory, tools, safety, adaptive policy, deployment or integration follows:

```text
acceptance requirement / material risk
→ question → requirements → research → alternatives → simple baseline
→ preregistered comparison → quantitative eval → robustness
→ production-fit → ADR → state decision → regression
```

Do not use cleanup/refactoring as a way to bypass this process. A semantic behavior change hidden inside a rename, dependency update or infrastructure refactor is still a material change.

## 9. Security and evidence boundaries

Never commit secrets, credentials, payment/account identifiers, hidden blind outcomes, private oracle rows or private scorer data that the frozen protocol forbids from repository exposure.

Evaluator/private/blind material remains isolated from candidate-generation/runtime code according to the relevant frozen protocol.

A new scorer/workflow may define an evaluator-side file interface without committing or reconstructing the private oracle. The private material's custody/provisioning mechanism must be explicitly established before execution.

## 10. Environment/configuration convention

Local secret files remain ignored. When a production configuration surface is eventually introduced, a non-secret template such as `.env.example` may be versioned while real `.env*` files remain excluded.

Do not create production packaging/deployment files merely to signal maturity before the production architecture is evidence-backed.

## 11. Future reference-safe physical cleanup

After the current evaluation/selection path closes, perform a dedicated **reference-safe physical cleanup**:

1. build a path/reference graph from workflows, scripts, frozen JSON and Markdown links;
2. identify truly unreferenced generated/transient files;
3. classify historical workflows/scripts as retained vs safely archivable;
4. move only unpinned narrative files into `docs/archive/` or a clearly versioned historical research location;
5. run link/path/reproducibility checks before and after the move;
6. record the cleanup as a non-semantic ADR/change note if it affects reproducibility paths.

Until that audit exists, preserving a seemingly messy frozen path is preferable to breaking scientific provenance.
