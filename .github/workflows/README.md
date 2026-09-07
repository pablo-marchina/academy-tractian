# GitHub Actions — Workflow Lifecycle

This directory contains current product CI, intentional hosted promotion gates, specialized validation and historical research workflows. **Workflow presence is not execution authorization.**

Current state: [`../../docs/ACTIVE-PROJECT-STATUS.md`](../../docs/ACTIVE-PROJECT-STATUS.md).

## 1. Required product regression

Stable top-level gate:

- `final-ci-required.yml` → `required-gate`

It composes/requires the principal reproduction/browser/distributed-correctness contracts. Branch protection should use the stable required status rather than every historical experiment workflow.

Current UX baseline `2ca6215...` passed `final-ci-required`, clean clone and full Playwright.

## 2. Hosted production promotion

`hosted-production-release0-agent.yml` is intentionally **manual (`workflow_dispatch`)** and requires:

```text
expected_sha = exact backend/runtime Git SHA intentionally promoted
```

It proves the exact hosted backend Release 0 read-only path and required modes. It must not auto-run merely because a large PR contains old backend diffs or a frontend/docs commit advances the branch.

This distinction is important:

```text
PR/branch regression green
≠ backend production promotion
```

Backend promotion remains an explicit operational decision with exact-SHA evidence.

`hosted-production-g2-smoke.yml` remains the hosted release-integrity smoke; exact expected SHA is used for intentional promotion, while ordinary integrity checks need not pretend every branch SHA is already serving.

## 3. Frontend deployment/regression

Frontend UX can advance independently when its build/browser gates pass and the backend contract remains compatible. Record frontend deployment SHA separately from the immutable promoted backend runtime SHA.

## 4. Specialized active validation

Examples include:

- production runtime/build checks;
- PostgreSQL operational/RLS/recovery checks;
- observability/realtime checks;
- EDD/provider-free checks;
- Railway IaC contract;
- targeted hosted smoke gates.

These are evidence for their exact scope, not automatic proof of broader production SLO/security/value claims.

## 5. Historical / experimental workflows

Provider experiment packets, one-shot E/EV/D-series campaigns and older research workflows are retained because frozen results/ADRs/provenance may reference them.

Do not rerun consumed experiments simply because YAML is present. Changed scientific execution requires a new prospective authorization/protocol.

## 6. Workflow lifecycle labels

Every new workflow should clearly fit one class:

- `required` — ordinary product merge regression;
- `promotion` — intentional hosted release acceptance;
- `specialized` — targeted engineering validation;
- `repository-maintenance` — narrow repo operation;
- `experimental` — preregistered/research execution;
- `historical-one-shot` — retained only for provenance.

Prefer reusable scripts/modules + a small number of stable top-level workflows over one YAML file per small code path.

## 7. Safety rules

- never print provider/database/auth/evaluator/blind secrets;
- separate provider-free regression from live-provider consumption;
- preserve exact source/protocol identity for frozen campaigns;
- do not silently relax expected SHA, quota, route/model or gold-isolation gates;
- never treat a skipped/not-triggered workflow as a pass;
- preserve failed/consumed attempts where scientifically material;
- do not bulk-delete historical YAML before proving it is unreferenced.

## 8. Cleanup

Physical deletion/rename is allowed only after proving the workflow is not referenced by frozen evidence, ADRs, active workflows, reproduction contracts or Actions provenance. When unsafe to rerun but provenance-sensitive, disable future triggers rather than falsifying history.