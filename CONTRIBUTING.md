# Contributing to Academy × TRACTIAN

This repository is operated as an evidence-driven production project. Contributions must improve the requested product while preserving safety, provenance and the USD0 hard constraint.

## Start here

Read the minimum set for your task:

1. [`docs/README.md`](docs/README.md) — documentation map and lifecycle;
2. [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) — current truth;
3. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) — non-negotiable rules;
4. [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) — current execution order;
5. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — promoted architecture and trust boundaries;
6. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) — final DoD;
7. applicable ADR/frozen experiment evidence.

For documentation changes, also read [`docs/DOCUMENTATION-GUIDE.md`](docs/DOCUMENTATION-GUIDE.md).

`docs/CURRENT-PROJECT-STATUS.md` is frozen historical evidence despite its legacy name. **Do not update it.** Current mutable state lives in `ACTIVE-PROJECT-STATUS.md`.

## Change classes

- **A — documentation/navigation:** no runtime/authorization/experiment semantics change.
- **B — behavior-preserving engineering:** plumbing/refactor with the same observable contract.
- **C — material product/architecture/experimental:** provider/model, prompt, tools, safety, evaluator, persistence, IAM, deployment, action semantics, requirements or claims.

When uncertain, treat the change as Class C.

## Before coding

A material change must answer:

1. What requirement, user friction, measured risk or evaluation gap does this close?
2. What is the simplest current baseline?
3. What hard constraints apply, including USD0/no-paid-spillover?
4. What evidence will prove success and failure?
5. What current gate authorizes any live/provider/private/consequential execution?
6. Which canonical documents will change if the result is accepted?

Optional complexity does not get a free pass. RAG, vector DB, multi-agent, memory, MCP, framework migration, Redis/Kafka or similar additions require a measured gap and a controlled challenger win.

## Implementation rules

- preserve frozen/consumed/failed evidence;
- never expose benchmark gold/evaluator-private state to runtime;
- keep identity, tenant and authorization outside model control;
- keep real TRACTIAN execution behind `HarnessRunner` + typed `ToolSpec` boundaries;
- deterministic safety checks own auth/RLS/schema/action/cost limits;
- no silent provider/model/route fallback;
- no local production serving dependency;
- no raw secrets/private custody/hidden reasoning in browser telemetry;
- claims must remain narrower than the evidence that proves them.

## Definition of Ready

- [ ] requirement/risk/user mapping is explicit;
- [ ] scope and non-goals are clear;
- [ ] baseline is known;
- [ ] success + fail-closed evidence is defined;
- [ ] authorization/frozen boundaries are known;
- [ ] affected docs/tests/evals are identified;
- [ ] deadline impact is acceptable.

## Definition of Done

- [ ] intended capability/risk/friction improved;
- [ ] applicable tests/evals pass;
- [ ] failure/negative behavior tested where material;
- [ ] no unauthorized external/private execution occurred;
- [ ] evidence and limitations recorded;
- [ ] ADR added for a durable material decision when needed;
- [ ] `ACTIVE-PROJECT-STATUS.md` updated when current state changes;
- [ ] `DELIVERY-PLAN.md` updated when sequencing changes;
- [ ] `ARCHITECTURE.md` updated when promoted architecture changes;
- [ ] acceptance/TAPI docs updated when requirement coverage changes;
- [ ] runbook updated when operational procedure changes;
- [ ] `CHANGELOG.md` updated for notable user/operator/reviewer-visible change;
- [ ] historical progress/evidence added without rewriting frozen history;
- [ ] claims remain evidence-bounded.

## Pull requests

Use `.github/pull_request_template.md` when present. A material PR should state:

- why the work exists;
- requirement/risk/user mapping;
- change class and priority;
- authorization boundary;
- baseline/alternatives for material choices;
- tests/evidence;
- failure cases and limitations;
- documentation affected.

Do not merge unresolved authorization, hidden-data, cross-tenant, action-safety or scientific-integrity ambiguity.

## CI and promotion

`final-ci-required / required-gate` is the stable repository-level regression gate. See [`.github/workflows/README.md`](.github/workflows/README.md) for workflow lifecycle.

A green PR does **not** automatically promote the backend runtime. Hosted Release 0 acceptance is an intentional promotion workflow and requires an explicit backend `expected_sha`.

Current Release 0 user-facing UX can evolve independently of the immutable promoted backend runtime when its own frontend/regression gates pass.

## Documentation discipline

Write for the reader's task, not for the repository author's chronology:

- tutorial/quickstart → help someone learn the product;
- how-to/runbook → help someone perform an operation;
- reference → provide exact facts/contracts;
- explanation → explain architecture/decisions/trade-offs.

Do not copy the same mutable fact into many documents. Link to the document that owns it. Historical evidence is append-only/frozen; active truth is edited prospectively.