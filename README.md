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
- [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) — reviewed action plan through the 2026-09-08 delivery;
- [`docs/PROJECT-PROGRESS-LOG.md`](docs/PROJECT-PROGRESS-LOG.md) — chronological progress/evidence ledger;
- [`research/results/project-progress-checkpoint-2026-08-24.json`](research/results/project-progress-checkpoint-2026-08-24.json) — current machine-readable checkpoint.

The previous machine checkpoint remains preserved at `research/results/project-progress-checkpoint-2026-08-23.json`. The E14v-era project plan is preserved at [`docs/archive/PROJECT-PLAN-2026-08-20.md`](docs/archive/PROJECT-PLAN-2026-08-20.md).

### Executive state — reviewed 2026-08-24 09:53 BRT

```text
Benchmark Integrity Gate            COMPLETE
P12 evaluation protocol             FROZEN
P12-C1                              CLOSED / DETERMINISTIC FAIL / NO ARM QUALIFIED
P12-C2                              CONSUMED_OPERATIONAL_FAILURE / NO SCORING
P12-C3                              CONSUMED_TERMINAL_OPERATIONAL_FAILURE / NO SCORING
current QUALIFIED candidate         NONE
current PREFERRED candidate         NONE
semantic v4.2                       NOT AUTHORIZED
FRESH_BLIND                         NO SOURCE AUTHORIZED
LEGACY_LOCKED_TEST                  ACCESS BLOCKED
final architecture                  UNFROZEN
production-readiness claim          NOT AUTHORIZED
```

## P12 evidence roles

- **EXPOSED_POOL = historical DEV + VALIDATION:** seven independent asset/story groups for adaptive development, selection, ablation, evaluator work and regression. It cannot support a fresh generalization claim.
- **FRESH_BLIND:** primary independent real-domain generalization evidence. Current state: `NO_BLIND_SOURCE_AUTHORIZED`.
- **LEGACY_LOCKED_TEST:** qualified supplementary held-out characterization; candidate execution remains blocked until separately authorized final access.
- **SYNTHETIC_ADVERSARIAL:** evaluator/judge qualification, robustness and regression only.

## Prospective P12 history

### P12-C1 — scientific comparison completed

36 common parents → 72 fixed C0/C1 outputs → deterministic scoring.

Both arms failed deterministic gates. C1 reduced extra reads but worsened expected-read recall and did not improve decision/action/escalation quality. No arm became `QUALIFIED`.

Canonical result: [`research/results/p12-c1-deterministic-paired-result-2026-08-23.json`](research/results/p12-c1-deterministic-paired-result-2026-08-23.json).

### P12-C2 — provider-capacity operational failure

The 2×2 A00/A10/A01/A11 experiment attempted all 36 common-parent cells, but only 31 completed. Five failed with `rate_limit_long_window`. The 144-output packet was never frozen, so deterministic scoring/LOGO/bootstrap were correctly blocked.

Canonical closure: [`research/results/p12-c2-live-cycle-closure-2026-08-23.json`](research/results/p12-c2-live-cycle-closure-2026-08-23.json).

### P12-C3 — capacity-controlled terminal operational failure

P12-C3 kept A00/A10/A01/A11 scientifically unchanged and prospectively introduced six fixed batches, reset-aware capacity control, immutable checkpoints, pending-only resume and a 72-hour horizon.

Provider-free activation/live infrastructure passed before live execution. The first B1 run stopped before provider access on a retained compatibility assertion; a narrow pre-outcome infrastructure amendment was frozen and provider-free qualified without changing the candidate/evaluator/scientific design.

The continued B1 run `32672167702` then reached live provider execution:

```text
completed cells        3
pending cells         33
transport failures     1
rate-limit events      1
terminal failure    true
horizon expired     false
```

The frozen controller entered a terminal experiment state on the fourth cell. Therefore P12-C3 cannot be resumed, rerun, partially scored or interpreted as a complete-case comparison.

Canonical closure:

- [`research/results/p12-c3-live-cycle-closure-2026-08-23.json`](research/results/p12-c3-live-cycle-closure-2026-08-23.json)
- [`research/p12-c3-live-cycle-closure-2026-08-23.md`](research/p12-c3-live-cycle-closure-2026-08-23.md)

## Reviewed critical path

The next step is **not** another P12-C3 trigger and P12-C4 is **conditional**, not automatic.

```text
provider-capacity alternatives ADR ─────────────── FRESH_BLIND readiness (parallel)
              │                                   production-fit research (parallel)
              ▼
       ADR GO decision?
         ┌────┴────┐
         │         │
       NO-GO       GO
         │         │
         ▼         ▼
 honest scope   P12-C4 preregistration + provider-free activation
 reassessment                     │
                                  ▼
                         complete prospective packet only
                                  │
                                  ▼
                    deterministic gate + 20k bootstrap + LOGO
                                  │
                                  ▼
                    semantic child gate for survivors only
                                  │
                                  ▼
                     production-fit / generation freeze
                                  │
                                  ▼
                      authorized FRESH_BLIND evidence
                                  │
                                  ▼
                    architecture freeze + regression + delivery
```

Hard schedule checkpoints:

- provider-capacity ADR: **2026-08-24**;
- Tier A FRESH_BLIND target: **2026-08-25 23:59 BRT**;
- complete prospective EXPOSED_POOL packet or scope reassessment: **end of 2026-08-27**;
- Tier B FRESH_BLIND fallback deadline: **2026-08-28 23:59 BRT**;
- preserve **2026-09-03 onward** primarily for integration, regression, documentation and delivery.

Full reviewed plan: [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md).

## Main current risks

1. **Provider capacity — CRITICAL:** P12-C2 failed at 31/36; P12-C3 became terminal at 3/36.
2. **No FRESH_BLIND source — CRITICAL:** independent generalization evidence is not yet available.
3. **No qualified current candidate — HIGH:** C1 failed scientifically; C2/C3 failed before complete scoring.
4. **Schedule — HIGH:** final target remains **2026-09-08** and the next 72 hours are decision-critical.
5. **Architecture decision debt — HIGH:** retrieval, reranking, multi-agent, memory, observability and final deployment/UI choices remain unfrozen.

## Frozen/retained foundations

Historical evidence supports several reusable foundations, including:

- ScenarioSchema / Canonical ToolSpec / TraceSchema / deterministic replay;
- HarnessRunner / HttpxTransport boundary;
- LangGraph runtime candidate;
- native ToolSpec envelope / MCP-compatible adapter;
- E9 v4.1 deterministic evaluator;
- E9 v4.2 semantic protocol;
- E14c/d/e public canonicalization/handoff semantics;
- E14n v1.1 identifier-provenance guard;
- E14p epistemic serializer;
- E14q/E14q2 safety/action authorization guards.

These are evidence-backed components, not an automatically frozen final architecture.

## Frozen TRACTIAN facts

- 17 agent-input cases and 16 narrative evaluation scenarios;
- 10 primary asset/story groups, so random ticket splitting is unsafe;
- evaluator-only gold separated from agent-visible input;
- 18 operations across 17 path templates;
- reference trajectories are not mandatory scripts;
- actions are accepted events and do not persist mutation state in the supplied environment;
- `x-user-id` and evaluation `seed` are runner-bound;
- response modes are reproducible through deterministic seeds/overrides;
- raw OpenAPI contains a duplicate `/assets/{assetId}` mapping;
- raw action validation is permissive and backend company/resource isolation is coarse;
- knowledge API exposes the supplied corpus directly.

## Project goal

The final project must address both:

1. **Industrial Agent Engineering** — contextualize, investigate, execute and escalate against the supplied industrial API.
2. **Agent Evaluation & Reliability** — quantitatively evaluate tool choice, arguments, trajectory, evidence, conclusion/response, safety, robustness, stability and action behavior.

The evaluation framework is part of the engineering loop, not a disconnected QA layer.

## Development rule

No component remains because it looks sophisticated. RAG, reranking, multi-agent routing, persistent memory, prompt optimization, model selection, judge selection and similar techniques require an explicit hypothesis/requirement, credible alternatives and controlled evidence. Optional complexity remains removable until supported.

Final delivery/presentation target: **2026-09-08**.
