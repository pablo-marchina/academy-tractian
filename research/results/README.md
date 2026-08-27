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

The latest canonical human state and the current machine-readable checkpoint are linked from `docs/CURRENT-PROJECT-STATUS.md`.

This README intentionally does **not** restate the latest experiment status, packet identity or next gate.

## Using result files safely

Before treating a result as current or executable authorization:

1. verify its timestamp/version and lifecycle state;
2. check whether a later closure/freeze supersedes its current-state implication;
3. consult `docs/CURRENT-PROJECT-STATUS.md` for current authorization;
4. preserve the old result even when superseded;
5. never infer authorization from a filename alone.

See `docs/REPOSITORY-GUIDE.md` for the full source-of-truth hierarchy and cleanup rules.
