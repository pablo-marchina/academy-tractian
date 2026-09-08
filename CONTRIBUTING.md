# Contributing to Academy × TRACTIAN

This repository is operated as an evidence-driven production project. Contributions must improve the requested product while preserving safety, provenance and explicit provider/cost boundaries.

## Start here

Read the minimum set for your task:

1. [`docs/README.md`](docs/README.md) — documentation map/lifecycle;
2. [`docs/ACTIVE-PROJECT-STATUS.md`](docs/ACTIVE-PROJECT-STATUS.md) — current truth;
3. [`docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md) — current provider-selection truth when provider/model/serving work is relevant;
4. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) — non-negotiable rules;
5. [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) — current execution order;
6. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — promoted architecture and challenger boundaries;
7. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) — final DoD;
8. applicable ADR/frozen experiment evidence.

For documentation changes, also read [`docs/DOCUMENTATION-GUIDE.md`](docs/DOCUMENTATION-GUIDE.md).

`docs/CURRENT-PROJECT-STATUS.md` is frozen historical evidence despite its legacy name. Do not update it.

## Change classes

- **A — documentation/navigation:** no runtime/authorization/frozen-experiment semantics change.
- **B — behavior-preserving engineering:** plumbing/refactor with the same observable contract.
- **C — material product/architecture/experimental:** provider/model, prompt, tools, safety, evaluator, persistence, IAM, deployment, action semantics, requirements or claims.

When uncertain, treat the change as Class C.

## Before coding

A material change must answer:

1. What requirement, user friction, measured risk or evaluation gap does this close?
2. What is the simplest current baseline?
3. What hard constraints apply?
4. What evidence proves success and failure?
5. What current gate authorizes live/provider/private/consequential execution?
6. Which canonical documents change if the result is accepted?

Optional complexity does not get a free pass. RAG, vector DB, multi-agent, memory, MCP, framework migration, Redis/Kafka or similar additions require a measured gap and controlled challenger win.

## Implementation rules

- preserve frozen/consumed/failed evidence;
- never expose benchmark gold/evaluator-private state to runtime;
- distinguish preflight from scored evidence;
- do not selectively retry/repair failed benchmark attempts after observing them;
- do not relabel a single-provider qualification as a comparative tournament;
- keep identity, tenant and authorization outside model control;
- keep real TRACTIAN execution behind `HarnessRunner` + typed `ToolSpec` boundaries;
- deterministic safety checks own auth/RLS/schema/action/cost limits;
- provider constrained decoding never replaces application validation/policy;
- no silent provider/model/route fallback;
- no local production serving dependency;
- no raw secrets/private custody/hidden reasoning in browser or research telemetry;
- claims must remain narrower than the evidence that proves them.

## Current provider-development rule

The current Groq GPT-OSS-120B baseline completed 85/85 and returned `NO_SELECTION`. Do not weaken gates or modify that consumed result.

Provider work should follow:

```text
causal diagnosis
→ canonical challenger
→ small eligibility preflight
→ unchanged-rubric comparison
→ unchanged hard gates
→ winner-only fresh 85/85
→ Academy live E2E
→ explicit production promotion
```

The exact supplied `ActionRequest` must be sourced from the canonical contract before complete strict action-output variants are accepted.

## Definition of Ready

- [ ] requirement/risk/user mapping explicit;
- [ ] scope/non-goals clear;
- [ ] baseline known;
- [ ] success + fail-closed evidence defined;
- [ ] authorization/frozen boundaries known;
- [ ] affected docs/tests/evals identified;
- [ ] deadline impact acceptable.

## Definition of Done

- [ ] intended capability/risk/friction improved;
- [ ] applicable tests/evals pass;
- [ ] failure/negative behavior tested where material;
- [ ] no unauthorized external/private execution occurred;
- [ ] evidence and limitations recorded;
- [ ] ADR added for a durable material decision when needed;
- [ ] `ACTIVE-PROJECT-STATUS.md` updated when current state changes;
- [ ] provider-status doc updated when provider evidence changes;
- [ ] `DELIVERY-PLAN.md` updated when sequencing changes;
- [ ] `ARCHITECTURE.md` updated when promoted/challenger architecture changes;
- [ ] acceptance/TAPI docs updated when requirement coverage changes;
- [ ] runbook updated when operation/promotion/recovery changes;
- [ ] `CHANGELOG.md` updated for notable user/operator/reviewer-visible change;
- [ ] append-only progress/evidence added without rewriting frozen history;
- [ ] claims remain evidence-bounded.

## Pull requests

Use `.github/pull_request_template.md` when present. A material PR should state why the work exists, requirement/risk/user mapping, change class/priority, authorization boundary, baseline/alternatives, tests/evidence, failure cases/limitations and documentation affected.

Do not merge unresolved authorization, hidden-data, cross-tenant, action-safety or scientific-integrity ambiguity.

## CI and promotion

Repository-level regression gates do not automatically promote production.

A green provider research branch, benchmark or preflight does **not** authorize provider promotion. Exact production changes require the promotion path documented in [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md).

Frontend/backend/provider identities may advance independently and must be tracked independently.

## Documentation discipline

Write for the reader's task: tutorial, how-to, reference or explanation. Do not copy mutable facts into many documents. Link to the canonical owner.

Historical/frozen evidence is append-only/immutable; active truth is edited prospectively. Negative evidence remains visible even when a later candidate succeeds.
