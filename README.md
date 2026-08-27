# Academy × TRACTIAN — Industrial Agent Engineering & Evaluation

Repository central do TAPI individual **Engenharia e Avaliação de Agentes Industriais** (Inteli × TRACTIAN).

## Start here

The repository is governed by four non-negotiable principles:

1. **systematic research + controlled comparison before material decisions**;
2. **production-first, never demo-first**;
3. **quantitative/adaptive by default with deterministic safety boundaries**;
4. **eval-driven engineering end to end**.

Read [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) before making a material project decision.

Canonical navigation:

- [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) — current evidence-backed state and current authorized gate;
- [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) — active plan from the current gate through production delivery;
- [`docs/PROJECT-PROGRESS-LOG.md`](docs/PROJECT-PROGRESS-LOG.md) — chronological evidence ledger;
- [`docs/REPOSITORY-GUIDE.md`](docs/REPOSITORY-GUIDE.md) — repository structure, source-of-truth rules and cleanup policy;
- [`docs/adr/`](docs/adr/) — material decision records;
- [`research/README.md`](research/README.md) — research evidence map;
- [`scripts/research/README.md`](scripts/research/README.md) — research executable lifecycle.

## Current canonical state

As of the 2026-08-26 22:51 BRT checkpoint:

```text
Benchmark Integrity Gate             CLOSED
P12 protocol                         FROZEN
P12-C1                               CLOSED / DETERMINISTIC FAIL
P12-C2                               CONSUMED_OPERATIONAL_FAILURE
P12-C3                               CONSUMED_TERMINAL_OPERATIONAL_FAILURE
P12-C4 common parents                PASS / 36 OF 36
P12-C4 local factorial outputs       PASS / 144 OF 144
P12-C4 complete packet               FROZEN_COMPLETE_C4_PACKET
current authorized gate              DETERMINISTIC_SCORING
provider calls authorized now        0
project-level PREFERRED candidate    NONE
final architecture                   UNFROZEN
production-readiness claim           NOT AUTHORIZED
```

The authoritative C4 packet freeze is [`research/results/p12-c4-complete-packet-freeze-2026-08-26.json`](research/results/p12-c4-complete-packet-freeze-2026-08-26.json). It records the successful 36/36 NVIDIA common-parent collection, 144/144 provider-free factorial expansion and the transition to deterministic scoring.

Passing or completing an experimental gate does **not** automatically make a component `PREFERRED`, `FROZEN`, final or production-ready.

## Project target

The final system must address both:

1. **Industrial Agent Engineering** — contextualize, investigate, execute and escalate against the supplied industrial API.
2. **Agent Evaluation & Reliability** — quantitatively evaluate tool choice, arguments, trajectory, evidence, conclusion/response, safety, robustness, stability and action behavior.

The target is a real production-path delivery, not a benchmark-only artifact or scripted demo. Final delivery remains targeted for **2026-09-08**.
