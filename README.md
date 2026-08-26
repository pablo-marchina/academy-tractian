# Academy × TRACTIAN — Industrial Agent Engineering & Evaluation

Repository central do TAPI individual **Engenharia e Avaliação de Agentes Industriais** (Inteli × TRACTIAN).

## Governance

All material work is governed by [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md):

1. systematic research + controlled comparison before material decisions;
2. production-first, never demo-first;
3. quantitative/adaptive by default with deterministic safety boundaries;
4. eval-driven engineering end to end.

Passing a gate means evidence for that gate. It does **not** automatically mean `PREFERRED`, `FROZEN`, final or production-ready.

## Current canonical status

See:

- [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) — canonical current evidence/status checkpoint;
- [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) — active macro plan through the 2026-09-08 delivery;
- [`docs/PROJECT-PROGRESS-LOG.md`](docs/PROJECT-PROGRESS-LOG.md) — chronological progress/evidence ledger;
- [`research/results/project-progress-checkpoint-2026-08-25.json`](research/results/project-progress-checkpoint-2026-08-25.json) — current machine-readable checkpoint.

### Executive state — reviewed 2026-08-25 22:50 BRT

```text
Benchmark Integrity Gate            COMPLETE
P12 evaluation protocol             FROZEN
P12-C1                              CLOSED / DETERMINISTIC FAIL / NO ARM QUALIFIED
P12-C2                              CONSUMED_OPERATIONAL_FAILURE / 31 OF 36 / NO SCORING
P12-C3                              CONSUMED_TERMINAL_OPERATIONAL_FAILURE / 3 OF 36 / NO SCORING
P12-C4 provider qualification       BLOCKED / SYNTHETIC OPERATIONAL FAIL / 0 OF 36
Cerebras numeric capacity           PASS
Cerebras generation access          FAIL / HTTP 402 PAYMENT_REQUIRED
current QUALIFIED candidate         NONE
current PREFERRED candidate         NONE
FRESH_BLIND                         NO SOURCE AUTHORIZED
LEGACY_LOCKED_TEST                  ACCESS BLOCKED
final architecture                  UNFROZEN
production-readiness claim          NOT AUTHORIZED
```

## Where the project is now

The project has moved beyond the original provider-capacity ADR. Cerebras + `gpt-oss-120b` was selected conditionally for P12-C4 qualification, fresh seeds and pacing were frozen, numeric organization/project capacity passed, and a one-shot synthetic compatibility probe was authorized.

The live synthetic workflow `32901958789` failed on the **first** provider request with HTTP `402 payment_required`. No model output was produced, no benchmark input was loaded, and the second synthetic request was not sent. The one-shot authorization is consumed and may not be rerun or reused.

Canonical closure:

- [`research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json`](research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json)

Therefore **P12-C4 EXPOSED_POOL generation is still blocked**. Current progress is `0/36` common parents, `0/144` fixed outputs, and scoring remains forbidden.

## Macro project phases

```text
1. Benchmark / governance foundation                     COMPLETE
2. Prospective exploration and failure learning C1-C3   COMPLETE
3. P12-C4 provider qualification / readiness             CURRENT
4. Complete candidate qualification (36/36 → 144/144)   PENDING
5. Deterministic + semantic + independent validation     PENDING
6. Production-fit decision + architecture freeze         PENDING
7. Integration, regression, documentation and delivery   PENDING
```

## Immediate critical path

```text
first-party billing / generation-access evidence
        ↓
narrow pre-outcome infrastructure amendment
        ↓
new one-shot synthetic authorization, only if all provider-free gates PASS
        ↓
2 / 2 synthetic calls PASS
        ↓
full provider-free C4 activation
        ↓
live manifest freeze
        ↓
36 / 36 common parents
        ↓
local A00/A10/A01/A11 expansion
        ↓
144 / 144 packet freeze
        ↓
deterministic gates → 20k bootstrap → LOGO → slices/failure analysis
        ↓
semantic child gate for deterministic survivors only
        ↓
production-fit decision + generation freeze
        ↓
authorized FRESH_BLIND measurement
        ↓
architecture freeze → regression → final delivery
```

The same failed synthetic authorization/run must **not** be rerun. No activation, EXPOSED_POOL generation, private scoring, FRESH_BLIND outcome access or architecture-freeze claim is allowed before its respective gate.

## Parallel independent-evidence track

FRESH_BLIND preparation continues independently. Current state remains `NO_SOURCE_AUTHORIZED`; hidden cases, expected paths and outcomes must remain unavailable to candidate development until candidate/evaluator generation is frozen and a separate final authorization exists.

## Retained evidence-backed foundations

Reusable foundations include:

- ScenarioSchema / Canonical ToolSpec / TraceSchema / deterministic replay;
- HarnessRunner / HttpxTransport boundary;
- LangGraph runtime candidate;
- native ToolSpec envelope / MCP-compatible adapter;
- E9 deterministic and semantic evaluator foundations;
- public canonicalization/handoff, identifier-provenance, epistemic serialization and safety/action authorization guards.

These are evidence-backed components, not an automatically frozen final production architecture.

## Project goal

The final project must address both:

1. **Industrial Agent Engineering** — contextualize, investigate, execute and escalate against the supplied industrial API.
2. **Agent Evaluation & Reliability** — quantitatively evaluate tool choice, arguments, trajectory, evidence, conclusion/response, safety, robustness, stability and action behavior.
