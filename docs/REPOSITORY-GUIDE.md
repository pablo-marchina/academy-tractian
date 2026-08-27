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
3. **`docs/CURRENT-PROJECT-STATUS.md`** — latest human-readable project state and currently authorized gate.
4. **latest machine checkpoint linked by current status** — structured project snapshot.
5. **`docs/PROJECT-PLAN.md`** — active future execution plan.
6. **`docs/PROJECT-PROGRESS-LOG.md`** — chronological historical ledger.
7. **ADRs** — decision context/status for their stated scope.
8. **README/index files** — navigation only; they must not independently redefine experiment semantics.
9. **historical research narratives** — evidence/context, not current authorization.

A historical statement is not current state merely because the file still exists.

## 3. Repository layout

| Path | Role | Mutation policy |
|---|---|---|
| `README.md` | concise entrypoint/navigation | keep current; do not duplicate detailed status |
| `docs/PROJECT-PRINCIPLES.md` | mandatory project-wide governance | change only through explicit governance decision |
| `docs/CURRENT-PROJECT-STATUS.md` | one canonical current human status | update when an evidence-backed gate changes |
| `docs/PROJECT-PLAN.md` | one canonical active plan | update prospectively when evidence/constraints change |
| `docs/PROJECT-PROGRESS-LOG.md` | chronological evidence ledger | append/curate without rewriting failed history into success |
| `docs/adr/` | material decision records and index | ADRs are immutable decision history; supersede with a new ADR rather than silently rewriting conclusions |
| `docs/archive/` | superseded non-binding narrative/planning docs | archive only when not needed as a stable frozen/source-pinned path |
| `docs/research/` | human handoff/custody docs for protected research tracks | preserve access-boundary semantics |
| `research/` | systematic research records and historical narrative | historical numbered records remain stable; use `research/README.md` as index |
| `research/experiments/` | preregistrations/designs/eligibility artifacts | version; do not mutate after freeze |
| `research/frozen/` | immutable contracts, maps, authorizations and frozen inputs | never rewrite in place after freeze |
| `research/fixtures/` | allowed fixtures/public test material | do not mix with private evaluator or blind outcomes |
| `research/results/` | canonical machine-readable results/closures/checkpoints | preserve historical snapshots; add new version/checkpoint rather than falsifying an old one |
| `research/live/` | live evidence when intentionally committed | treat committed live evidence as immutable |
| `scripts/research/` | reproducible research/evaluation runners | preserve source-pinned versions; create a new version for material semantic changes |
| `.github/workflows/` | execution wrappers/CI/live experiment plumbing | workflow existence does not imply current authorization |

## 4. Cleanup findings addressed in the 2026-08-26 pass

The audit found four high-impact organization problems:

1. **stale canonical status duplication** — root README, current status, active plan, progress log and research README described different project eras;
2. **navigation ambiguity** — a reader could not reliably distinguish current state from historical E-series/P12 evidence;
3. **flat historical research surface** — many numbered historical records are intentionally retained at `research/` root but lacked a current index explaining that they are history, not authorization;
4. **workflow/script ambiguity** — many historical executables remain for reproducibility, but there was no explicit lifecycle rule distinguishing presence from authorization.

The safe cleanup response is:

- make `CURRENT-PROJECT-STATUS.md` the sole detailed current-state document;
- make root/research/script/workflow READMEs indexes, not competing status documents;
- preserve historical/frozen evidence paths;
- use new time-specific machine checkpoints instead of overwriting older snapshots;
- add ADR and executable lifecycle indexes;
- defer physical moves/deletions until a reference/pin audit proves they are safe.

## 5. What may be deleted or moved

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

## 6. Historical evidence policy

Failed experiments, operational failures and consumed one-shot attempts are evidence. They must not be removed merely because they are obsolete for execution.

Use these lifecycle labels in indexes/ADRs when useful:

- `ACTIVE` — relevant to the current authorized path;
- `FROZEN` — immutable evidence/decision input;
- `CONSUMED` — attempt cannot be reused/rerun but remains evidence;
- `HISTORICAL` — retained for context/reproducibility, not current authorization;
- `SUPERSEDED` — replaced by a better-supported decision while retained in history.

## 7. Current-state documentation rule

Avoid repeating detailed current status in multiple files.

- `CURRENT-PROJECT-STATUS.md` owns the full current state.
- `README.md` carries only a compact snapshot and links to current status.
- `research/README.md` describes research structure and current pointer, not a separate scientific checkpoint.
- `PROJECT-PROGRESS-LOG.md` records history and points forward to current status.

When a major gate changes, update current status + machine checkpoint + progress ledger together.

## 8. Material development-change workflow

Any material change to architecture, model, prompt, evaluator, runtime, retrieval, memory, tools, safety, adaptive policy, deployment or integration follows:

```text
question → requirements → research → alternatives → baseline
→ preregistered comparison → quantitative eval → robustness
→ production-fit → ADR → state decision → regression
```

Do not use cleanup/refactoring as a way to bypass this process. A semantic behavior change hidden inside a rename, dependency update or infrastructure refactor is still a material change.

## 9. Security and evidence boundaries

Never commit secrets, credentials, payment/account identifiers, hidden blind outcomes, private oracle rows or private scorer data that the frozen protocol forbids from repository exposure.

Evaluator/private/blind material remains isolated from candidate-generation/runtime code according to the relevant frozen protocol.

## 10. Recommended future physical cleanup

After the current C4 scoring/selection gates close, perform a dedicated **reference-safe physical cleanup**:

1. build a path/reference graph from workflows, scripts, frozen JSON and Markdown links;
2. identify truly unreferenced generated/transient files;
3. classify historical workflows/scripts as retained vs safely archivable;
4. move only unpinned narrative files into `docs/archive/` or a clearly versioned historical research location;
5. run link/path/reproducibility checks before and after the move;
6. record the cleanup as a non-semantic ADR/change note if it affects reproducibility paths.

Until that audit exists, preserving a seemingly messy frozen path is preferable to breaking scientific provenance.
