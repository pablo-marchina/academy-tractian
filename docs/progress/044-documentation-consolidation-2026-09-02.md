# Documentation Consolidation Freeze — 2026-09-02

**Status:** HISTORICAL / documentation-governance record

## What changed

The active documentation surface was consolidated after:

- D01 completed live with 32/32 attempts and `NO_SELECTION`;
- D02 provider-free/governed implementation was prepared with 1024 completion cap;
- TAPI coverage was explicitly reviewed for stack, techniques, frameworks and outputs;
- realtime observability/control-room frontend became a P0 final-delivery workstream.

## Canonical surface after consolidation

- root `README.md` — concise entrypoint;
- `docs/README.md` — documentation index/lifecycle;
- `docs/CURRENT-PROJECT-STATUS.md` — current state/authorization;
- `docs/DELIVERY-PLAN.md` — unified plan/schedule;
- `docs/ARCHITECTURE.md` — architecture/stack/techniques/framework decisions;
- `docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md` — TAPI technical/output crosswalk;
- `docs/DELIVERY-ACCEPTANCE.md` — final Definition of Done;
- `docs/FINAL-HANDOFF-RUNBOOK.md` — operational reproduction/demo/fallback;
- `docs/RUBRIC-TO-EVIDENCE.md` — reviewer evidence navigation;
- `docs/PROJECT-PRINCIPLES.md` — governance.

## Superseded mutable paths

The following previously mutable documents were reduced to compatibility/navigation shims:

- `PROJECT-PLAN.md`;
- `NEXT-STEPS.md`;
- `ARCHITECTURE-ROADMAP.md`;
- `REPOSITORY-GUIDE.md`;
- `FINAL-DELIVERY-OUTPUT-INVENTORY-2026-09-02.md`.

Their previous full content remains available in Git history.

## What was deliberately not moved/rewritten

- accepted/frozen ADRs;
- frozen experiment artifacts/results;
- date-stamped audits/preflight/revalidation evidence;
- consumed/uncertain custody evidence;
- historical progress records.

Reason: the repository's evidence policy prefers logical cleanup when physical relocation could break pinned paths, references or scientific provenance.

## Anti-drift rule

Future state changes update only the document that owns that question. Historical details go to progress/evidence rather than being copied into README/plan/architecture simultaneously.