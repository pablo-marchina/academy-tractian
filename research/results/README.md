# Research Results and Checkpoints

This directory contains canonical machine-readable results, closures, gate records and time-specific project checkpoints.

## Result policy

- result/closure artifacts are historical evidence and must not be rewritten to make later outcomes look cleaner;
- add a new version/result when evidence changes;
- preserve failed, incomplete and consumed attempts with their actual status;
- exact claims must be supported by the corresponding artifact, not by filename inference;
- private/blind data must remain excluded whenever the governing protocol requires isolation.

## Project checkpoints

Project checkpoints are snapshots at a timestamp, not mutable global truth. Older snapshots remain valid descriptions of the project at their recorded time even after later evidence supersedes their current-state conclusions.

The latest checkpoint is linked from `docs/CURRENT-PROJECT-STATUS.md`.

Current C4 packet freeze:

- `p12-c4-complete-packet-freeze-2026-08-26.json`
- status `FROZEN_COMPLETE_C4_PACKET`
- next gate `DETERMINISTIC_SCORING`.

See `docs/REPOSITORY-GUIDE.md` for the full source-of-truth hierarchy.
