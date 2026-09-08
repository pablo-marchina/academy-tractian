# GitHub Actions — Workflow Lifecycle

This directory contains current product CI, intentional hosted promotion gates, specialized validation and historical research workflows. **Workflow presence is not execution authorization.**

Current state: [`../../docs/ACTIVE-PROJECT-STATUS.md`](../../docs/ACTIVE-PROJECT-STATUS.md).

## 1. Required product regression

Stable top-level gate:

- `final-ci-required.yml` → `required-gate`

It composes/requires the principal reproduction/browser/distributed-correctness contracts. Branch protection should use the stable required status rather than every historical experiment workflow.

Recent material baselines:

- backend V13 PR #210 passed all 8 required triggered workflows before merge to `08866da60245f58f217981b7ae668b10be45cc67`;
- task-driven frontend PR #209 passed the required frontend/browser/full-product regression surface before merge/deployment to `1bc124a8d4dbd029178ff8129b25452129445de7`.

## 2. Hosted backend promotion

`hosted-production-release0-agent.yml` is intentionally manual (`workflow_dispatch`) and requires an exact expected backend SHA for a full hosted acceptance campaign.

Repository CI and Railway exact-SHA deployment are different evidence classes:

```text
PR/branch regression green
≠ backend production promotion
≠ full hosted acceptance campaign
```

The original Release 0 acceptance remains workflow run `34069562818` at backend `082d6f...`.

The current V13 backend `08866da...` was prospectively validated through required CI, exact-SHA Railway deployment, TRACTIAN predeploy smoke, `/health` and targeted live prompt traces. Do not rewrite the historical workflow run to pretend it tested V13.

`hosted-production-g2-smoke.yml` remains an exact-source release-integrity smoke for intentional promotion use.

## 3. Frontend deployment/regression

Frontend UX can advance independently when build/browser gates pass and backend contract remains compatible. Track frontend deployment SHA separately from backend runtime SHA.

Current hosted task-driven frontend: `1bc124a8d4dbd029178ff8129b25452129445de7`.

## 4. Specialized active validation

Examples:

- production runtime/build checks;
- PostgreSQL operational/RLS/recovery checks;
- observability/realtime checks;
- EDD/provider-free checks;
- Railway IaC contract;
- full-product Playwright;
- targeted hosted smoke gates.

These are evidence for exact scope, not automatic proof of broader SLO/security/value claims.

## 5. Live prompt testing and auth boundary

The public `POST /api/runs` path requires the real managed browser session. Do not add a CI shortcut that bypasses server-owned session/tenant authority simply to make live prompting easy.

If automated hosted semantic/API coverage is required, design a separately authorized test-harness identity/session path with explicit scope and provenance. The Railway `hosted-pilot` service is currently a preflight process, not a second serving agent runtime.

## 6. Historical / experimental workflows

Provider experiment packets, one-shot E/EV/D-series campaigns and older research workflows are retained because frozen results/ADRs/provenance may reference them.

Do not rerun consumed experiments merely because YAML is present. Changed scientific execution requires a new prospective authorization/protocol.

## 7. Workflow lifecycle labels

Every new workflow should fit one class:

- `required` — ordinary product merge regression;
- `promotion` — intentional hosted release acceptance;
- `specialized` — targeted engineering validation;
- `repository-maintenance` — narrow repo operation;
- `experimental` — preregistered/research execution;
- `historical-one-shot` — retained only for provenance.

Prefer reusable scripts/modules + a small number of stable top-level workflows over one YAML file per small path.

## 8. Safety rules

- never print provider/database/auth/evaluator/blind secrets;
- separate provider-free regression from live-provider consumption;
- preserve exact source/protocol identity for frozen campaigns;
- do not silently relax expected SHA, quota, route/model or gold-isolation gates;
- never treat skipped/not-triggered workflow as a pass;
- preserve failed/consumed attempts where scientifically material;
- do not bulk-delete historical YAML before proving it unreferenced;
- do not introduce an auth bypass to automate production prompt tests.

## 9. Cleanup

Physical deletion/rename is allowed only after proving the workflow is not referenced by frozen evidence, ADRs, active workflows, reproduction contracts or Actions provenance. When unsafe to rerun but provenance-sensitive, disable future triggers rather than falsifying history.