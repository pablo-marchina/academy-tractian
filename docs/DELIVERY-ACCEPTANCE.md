# Academy × TRACTIAN — Delivery Acceptance

**Status:** ACTIVE / canonical Definition of Done  
**Checkpoint:** 2026-09-02  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**TAPI coverage:** [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md)

This document answers one question: **what must be demonstrably true before the final project can be called complete?**

## 1. Final acceptance rule

```text
TAPI P0 agent behavior covered
+
TAPI evaluation framework covered
+
API/tool/safety/evaluator integrity preserved
+
D01/D02/provider claims bounded by evidence
+
realtime safe observability and frontend demonstrated
+
final outputs/architecture explained in the UI
+
clean reproduction passes
+
README/runbook/results/limitations complete
```

Any uncovered P0 is a blocker unless the final scope is explicitly reduced with an evidence-honest limitation.

## 2. TAPI agent acceptance

The delivered agent must demonstrate:

- contextualize/orient a request with grounded evidence;
- investigate using appropriate TRACTIAN read tools;
- construct valid typed arguments;
- handle complete, partial, inconclusive, conflicting and unavailable data;
- ask clarification when required;
- abstain safely when no justified path exists;
- escalate with a structured human handoff;
- contain unauthorized/invalid consequential actions;
- execute only explicitly governed supplied/test actions where authorized;
- produce customer-safe terminal communication;
- maintain inspectable trajectory/provenance.

Required evidence includes real integrated traces and negative/failure cases, not final text only.

## 3. Evaluation-framework acceptance

The framework must support and demonstrate:

- scenario execution;
- tool-selection evaluation;
- argument validity;
- execution trajectory integrity;
- evidence/provenance use;
- response/terminal outcome quality where evidence supports it;
- safety/containment;
- failure performance;
- repeated-run stability;
- high-impact-action behavior;
- escalation/handoff quality;
- customer-safe communication;
- evaluator/runtime isolation;
- reproducible result identities/configuration.

Private benchmark/gold truth must never enter runtime/model context.

## 4. Provider experiment acceptance

D01 is accepted as historical evidence only if its frozen result remains unchanged:

- 32/32 completed attempts;
- USD0;
- complete resource accounting;
- `NO_SELECTION`;
- no raw provider material recorded;
- 24/24 generic `CLIENT_FAILURE` at exact 512 completion ceiling.

D02 acceptance requires:

- exact prospective 1024-token protocol;
- fresh governed authorization;
- no paid spillover;
- write-ahead custody/no replay;
- complete/explicitly stopped accounting;
- sanitized failure subtypes;
- D01 vs D02 analysis;
- Pareto/hard-gate decision, including `NO_SELECTION` when appropriate.

No architecture change is accepted merely because a provider/model performs poorly.

## 5. Realtime observability acceptance

Browser-visible telemetry must come from a deterministic safe projection, never raw `RunTrace`.

Must prove:

- live run appears without page refresh;
- genuine runtime events update timeline/trace graph/counters;
- event sequence/order is preserved;
- connection state is explicit (`LIVE`, `RECONNECTING`, `CAUGHT_UP`, `HISTORICAL`);
- disconnect/reconnect catches up from persisted events using cursor/event id;
- duplicate delivery is idempotent;
- a slow/disconnected browser cannot block agent execution;
- terminal UI appears only after genuine terminal evidence;
- no fabricated model-thinking/progress animation is presented as telemetry.

If only single-process realtime is tested, the delivery must not claim horizontally scaled realtime.

## 6. Security/privacy acceptance for API/SSE/frontend

The browser/API/SSE must never receive:

- provider credentials/tokens;
- Cloudflare account ID/auth headers;
- runtime identity binding or user ID;
- evaluation seed;
- raw provider request/response;
- raw prompt/system material forbidden by contracts;
- forbidden raw tool response/observation bodies;
- hidden chain-of-thought;
- evaluator-private truth/oracles/gold.

Required tests must prove deny-list behavior rather than relying only on code review.

## 7. Frontend product acceptance

Required product areas:

1. **Mission Control** — runtime/provider/run/outcome/latency/tool/policy/resource overview;
2. **Live Runs** — active executions and connection state;
3. **Run Explorer** — historical searchable/filterable runs;
4. **Timeline/Waterfall** — ordered execution timing;
5. **Trace Graph** — actual trace topology/events;
6. **Tools & Policy** — proposals/execution/blocks/violations/tool metrics;
7. **Quality & Providers** — evaluator/D01/D02/tokens/latency/Neurons/gates/selection;
8. **Dynamic Data Explorer** — allow-listed schema-driven queries/charts;
9. **Architecture Explorer / Explain This Run** — active architecture path + output lineage.

Every KPI/chart must support drill-down to the underlying safe run/event evidence where semantically applicable.

## 8. Architecture and output explanation acceptance

For every representative run, the UI must answer:

- what happened;
- which delivered architecture components participated;
- which component produced each output;
- what safe evidence/input fed that output;
- what happened next;
- what became terminal output;
- which evaluation occurred afterward.

Origin labels:

```text
MODEL
CONTROLLER
POLICY
TOOL
OBSERVATION
EVALUATOR
SYSTEM
```

Runtime-time and evaluator-time information must be visually separated.

## 9. Dynamic visualization acceptance

Data Explorer must:

- expose only allow-listed safe datasets/fields;
- support filters by relevant run/provider/tool/policy/error/experiment/time dimensions;
- support semantically valid aggregations including rates/p50/p95 where defined;
- validate chart compatibility deterministically;
- provide line/bar/scatter/heatmap/histogram/table families as applicable;
- update without full-page reload;
- permit drill-down to source safe records;
- reject unsupported combinations with a clear message;
- never execute arbitrary browser SQL against private data.

Required ready-made views include outcome over time, latency p50/p95, tool/policy behavior, failure subtypes, output tokens vs outcome, D01 vs D02 matrix and Neuron/resource accounting.

## 10. Required outcome/state test matrix

At minimum test/demonstrate:

- success/orient;
- investigate/tool use;
- ask clarification;
- abstain/unavailable evidence;
- human escalation + handoff;
- policy/action blocked;
- tool/provider error;
- partial/inconclusive/conflict;
- live run in progress;
- SSE reconnect/catch-up;
- loading;
- empty;
- long/overflow content;
- invalid dynamic query/chart combination;
- trace validation failure representation;
- D01/D02 experiment state.

## 11. QA acceptance

Backend/core:

- existing pytest/runtime/evaluator/campaign regressions green;
- observability sanitizer tests for every event/output class;
- API schema/contract tests;
- event sink fail-isolation/order/idempotency tests;
- persistence/reconnect tests;
- security field-deny tests.

Frontend:

- TypeScript build/typecheck;
- Vitest/Testing Library component/state tests;
- Playwright E2E for core flows and realtime reconnect;
- chart-spec compatibility tests;
- presentation viewport/overflow test;
- clean frontend build from lockfile.

## 12. Reproduction/documentation acceptance

From a clean checkout, a reviewer must be able to:

- install backend dependencies;
- reproduce provider-free runtime/evaluator tests/campaigns;
- install/build/start observability backend/frontend once implemented;
- execute provider-independent demo;
- inspect traces/evaluation/architecture/output lineage;
- follow documented D02/live-provider boundary without secrets in docs;
- understand exact models/configuration/stack/techniques;
- find experiment results, limitations and non-claims;
- navigate rubric → evidence.

The README, `docs/README.md`, this acceptance document and runbook must not contradict `CURRENT-PROJECT-STATUS.md`.

## 13. Freeze acceptance

By end of 2026-09-05:

- feature set frozen;
- information hierarchy/visual system frozen;
- runtime→safe telemetry→UI contracts frozen;
- no open P0 frontend/observability defect;
- remaining P1 explicitly bounded.

After freeze, only delivery-blocking fixes are permitted and each requires targeted regression.

## 14. Final demo acceptance

The final demo must visibly show the real integrated path:

```text
request
→ live run
→ architecture activation
→ model/decision metadata
→ typed tool proposal
→ validation/policy
→ TRACTIAN call metadata
→ safe observation/evidence
→ terminal outcome
→ completed trace
→ post-runtime evaluation
→ output lineage
→ dynamic analytics
→ D01/D02 evidence
```

It must include more than one outcome/failure class and preserve a provider-independent fallback demonstration.

## 15. Evidence-honest non-claims

The project may remain complete with `NO_SELECTION` if provider hard gates are not met. It may not compensate by inventing a winner, adding unmeasured architecture, or hiding limitations.

The missing exact C4 evaluator artifact remains an external blocker for claims that require that exact material; it must not be reconstructed.