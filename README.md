# Academy × TRACTIAN

Production-oriented industrial agent and evaluation platform built around the TRACTIAN teaching API.

The repository contains two integrated product capabilities:

- **Industrial agent runtime** — typed TRACTIAN tools, evidence-aware decisions, clarification/abstention/escalation and governed consequential actions.
- **Evaluation system** — deterministic and semantic evaluation, failure/stability campaigns, operational-value measurement and reproducible evidence.

> This README is intentionally a concise entrypoint. Current state, authorization and evidence live in the canonical documents below.

## Start here

| Need | Canonical source |
|---|---|
| Current project state | [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) |
| Documentation index | [`docs/README.md`](docs/README.md) |
| Architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Codebase map | [`docs/CODEBASE-MAP.md`](docs/CODEBASE-MAP.md) |
| Delivery plan | [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) |
| Acceptance / Definition of Done | [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) |
| TAPI coverage | [`docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`](docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md) |
| Development process | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Research/evidence history | [`research/README.md`](research/README.md) |

## Promoted product path

```text
React Operator Control Room
        ↑ REST + SSE
FastAPI Product / Observability API
        ↑ trusted runtime identity
PostgreSQL operational state + tenant RLS
        ↑
RealtimeProductionRuntime
        ↓
provider-neutral DecisionSource
        ↓
AgentController → HarnessRunner
        ↓
18 typed TRACTIAN tools
        ↓
deterministic safety boundaries
        ↓
normalized evidence
        ↓
FINAL | CLARIFY | ABSTAIN | ESCALATE | ACTION_PROPOSAL
        ↓
RunTrace → ProductionEvaluator
        ↓
sanitized PostgreSQL observability/evaluation projection
        ↓
REST / SSE / frontend
```

Consequential actions follow a separate governed path with persistent custody, explicit confirmation, authorization revalidation, idempotency and execution leases. Ambiguous lost ownership converges to `UNCERTAIN`; the product does not blindly replay an external side effect.

## Repository layout

| Path | Purpose |
|---|---|
| `src/academy_tractian/` | production runtime, APIs, storage, observability, evaluation and product controls |
| `frontend/` | React/TypeScript operator control room |
| `tests/` | backend product/regression/integration tests |
| `frontend/e2e/` | browser acceptance tests |
| `research/e2/` | accepted controller/tool/trace/evaluation harness |
| `research/experiments/` | experiment designs/preregistrations |
| `research/frozen/` | immutable evidence contracts and inputs |
| `research/results/` | machine-readable results and closures |
| `scripts/` | thin deterministic CLI/validation/reporting wrappers |
| `docs/` | canonical product documentation + preserved historical evidence |
| `.github/workflows/` | required CI plus preserved experimental/historical workflows |

## Runtime storage

The promoted serving path uses **PostgreSQL** for mutable operational state, tenant isolation and sanitized production observability/evaluation data. DuckDB is retained only as an optional development/benchmark compatibility dependency; it is not part of the promoted production serving path.

## Core stack

### Backend

- Python 3.11+
- FastAPI / Uvicorn
- Pydantic 2.x
- PostgreSQL + psycopg
- custom `AgentController` + `HarnessRunner`
- typed `ToolSpec` registry
- pytest

### Frontend

- React 19
- TypeScript
- Vite
- TanStack Query
- Apache ECharts
- React Flow (`@xyflow/react`)
- Vitest
- Playwright

## Evaluation-driven development

Material changes follow:

```text
requirement / measured gap
→ metric + evaluator
→ baseline
→ hypothesis
→ candidate
→ preregistered comparison
→ repeated/sliced evaluation
→ hard gates + uncertainty
→ PROMOTE / REJECT / INCONCLUSIVE / NO_CHANGE
→ regression protection
```

Complexity is not promoted by convention. Framework swaps, RAG, memory, multi-agent orchestration, new infrastructure components or adaptive policies must first demonstrate a measurable gap and win a controlled comparison.

## Evidence and provenance

This repository intentionally preserves a large research trail. Historical files are not automatically current truth, and their presence does not authorize rerunning a consumed experiment.

Before moving or deleting research, workflow, ADR or frozen evidence paths, follow the cleanup policy in [`docs/README.md`](docs/README.md). Prefer logical classification over breaking source-pinned provenance.

## Required CI

The stable top-level gate is `.github/workflows/final-ci-required.yml`. It composes the current product reproduction/browser/distributed-correctness contracts and exposes `required-gate` as the stable status context.

See [`.github/workflows/README.md`](.github/workflows/README.md) before touching historical one-shot workflows.

## Claim discipline

Do not claim more than the evidence proves. In particular, repository-level correctness tests are not automatically evidence of deployed HA, production capacity, RTO/RPO, enterprise IAM, human semantic calibration or operational-value gains.

The authoritative status of those claims is maintained in [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md).
