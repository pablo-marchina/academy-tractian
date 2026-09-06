# Production Implementation Progress

This directory contains chronological, mutable implementation logs for the final production promotion.

These logs are evidence indexes, not canonical current state. Use:

- `../ACTIVE-PROJECT-STATUS.md` for current truth;
- `../DELIVERY-PLAN.md` for execution order and progress state;
- `../decision-registry.yaml` for material decisions;
- `../ARCHITECTURE.md` and the runtime architecture manifest for architecture;
- frozen historical documents only for their original evidence scope.

Rules:

1. Never place secrets, DSNs, credentials or private evaluator/gold content here.
2. Record only evidence that was actually observed.
3. Separate `PASS`, `BLOCKED`, `NOT READY` and untested claims explicitly.
4. Link commits/platform resources by non-secret identifiers when useful.
5. Do not rewrite frozen/source-pinned history to make current work look cleaner.

## Logs

- [`2026-09-05-production-final.md`](2026-09-05-production-final.md) — final production implementation kickoff, architecture truth, Railway clean service and Neon schema/RLS promotion.
