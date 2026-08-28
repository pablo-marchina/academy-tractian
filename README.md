# Academy × TRACTIAN

This repository is the governed individual TRACTIAN × Inteli project: a production-path agent runtime, deterministic evaluation framework, controlled reliability/safety campaigns, and reproducible delivery evidence.

## Start here

The repository deliberately separates **what is implemented** from **what is authorized or proven**.

- [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) — sole canonical human-readable current state and authorization boundary.
- [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) — final P0/P1 acceptance matrix.
- [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md) — setup, reproduce, demo, monitoring, failure/fallback and rollback instructions.
- [`docs/RUBRIC-TO-EVIDENCE.md`](docs/RUBRIC-TO-EVIDENCE.md) — reviewer navigation from the academic rubric to exact evidence.
- [`research/results/final-delivery-evidence-index-2026-08-28.json`](research/results/final-delivery-evidence-index-2026-08-28.json) — machine-readable frozen evidence inventory.
- [`docs/adr/016-provider-free-final-delivery-reproduction-evidence-package-2026-08-28.md`](docs/adr/016-provider-free-final-delivery-reproduction-evidence-package-2026-08-28.md) — frozen clean-checkout reproduction decision.

Do not infer authorization from the presence of code, old branches, workflows or historical experiment artifacts.

## Delivered architecture

The production path reuses the accepted ADR-004 controller and the E2 `HarnessRunner` tool boundary rather than duplicating research execution logic. The canonical tool registry normalizes the supplied industrial API into 18 operations (17 path templates), with strict argument validation and explicit action permissions. The default `ProductionRuntime` keeps mutating actions disabled. ADR-012 separately demonstrates supplied/test controlled action execution with authorization and durable idempotency custody; it is not blanket real-customer authorization.

The repository is organized as:

- `src/academy_tractian/` — production-path runtime, evaluator, provider adapters, controlled actions and delivery helpers;
- `research/e2/` — framework-neutral controller, typed tool contracts, trace model and evaluation harness;
- `research/` — controlled research/evaluation evidence, benchmark-integrity records and frozen artifacts;
- `tests/` — production-path and frozen-regression tests;
- `scripts/` — deterministic validators and governed utilities;
- `docs/` — source-of-truth status, acceptance, ADRs, runbook and review navigation.

## Prerequisites

- Python **3.11 or newer**.
- Project dependency: `pydantic>=2.6,<3`.
- Development/test dependency: `pytest>=8`.
- No provider secret is required for the canonical provider-free reproduction.

From a clean checkout:

```bash
python -m pip install -e ".[dev]" -e "research/e2[dev]"
```

## Canonical provider-free reproduction

Run this exact sequence from the repository root:

```bash
python -m pytest -q tests
python -m pytest -q research/e2/tests/test_controller.py
python scripts/validate_ev007_failure_campaign.py
python scripts/validate_ev008_stability_campaign.py
python scripts/validate_ev011_communication_campaign.py
python scripts/validate_delivery_reproduction.py
python scripts/validate_final_handoff_audit.py
```

ADR-016 froze the upstream sequence through `validate_delivery_reproduction.py`; issue #60 appends only the final handoff-audit validator. The dedicated GitHub Actions workflows start from a clean checkout and require no live-provider credential.

Frozen upstream identities that must not move to make the handoff pass:

- EV-007: `7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9`
- EV-008: `1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8`
- EV-011: `cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e`
- integrated provider-free demo: `43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445`

## Integrated demo

The frozen provider-free demo executes five real runtime/evaluator traces through existing boundaries:

1. read/investigate → `ORIENT`;
2. missing context → `ASK_CLARIFICATION`;
3. no safe path → `ABSTAIN`;
4. human review → `ESCALATE_HUMAN`;
5. one fully authorized supplied/test `reprocess_analysis` action with one local transport and one durable local idempotency claim.

Run:

```bash
python scripts/validate_delivery_reproduction.py
```

The demo is synthetic/provider-free delivery evidence. It performs **0 real customer mutations**.

## Current external/gated boundaries

At the canonical handoff baseline:

- live provider comparison: **0/32 calls**, no provider/model selected, issue #44 separately gated on explicit secrets plus durable custody;
- credential/account probes: **0** and forbidden as a readiness shortcut;
- real customer mutations: **0**;
- scientific gate: `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`;
- exact C4 evaluator-side score-row artifact remains unavailable (`b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`, 177350 bytes, 144 rows);
- semantic, `FRESH_BLIND` and `LEGACY_LOCKED_TEST` access remains unauthorized;
- global architecture freeze and unconditional production-readiness claims remain unauthorized.

See the runbook for failure/fallback/rollback behavior and the rubric crosswalk for the strongest evidence behind each review dimension.

## Development governance

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) before changing experiment semantics, evaluation, runtime behavior, provider geometry, production architecture or canonical project state. Frozen evidence remains immutable; later delivery work must bound claims rather than rewrite earlier results.