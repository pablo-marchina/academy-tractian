## Purpose

<!-- What problem does this PR solve? Keep this tied to the actual TRACTIAN × Inteli delivery. -->

## Delivery mapping

- **Requirement / rubric / material risk:**
- **Priority:** P0 / P1 / justified P2
- **Change class:** A documentation-only / B non-semantic engineering / C material semantic-experimental-product
- **Current project gate:**
- **Authorization source (if applicable):**

## Scope

### In scope

-

### Explicitly out of scope

-

## Decision / implementation rationale

<!-- For Class C: list the simple baseline and credible alternatives. For A/B: explain why semantics are preserved. -->

- **Simple/null baseline:**
- **Alternatives considered:**
- **Why this change is currently justified:**

## Evidence

<!-- Link exact tests, evals, artifacts, hashes, experiment results or reproducible commands. Do not make claims stronger than this evidence. -->

- **Tests / regression:**
- **Quantitative evidence:**
- **Robustness / failure evidence:**
- **Production / partner-quality evidence:**

## Safety, custody and provenance

- **Frozen/source-pinned artifacts touched:** none / list and justify
- **Private/evaluator-only material accessed:** none / authorized source
- **FRESH_BLIND or LEGACY_LOCKED_TEST accessed:** no / authorized source
- **External provider/model calls:** none / authorized source and budget
- **Secrets/credentials added to repository:** no

## Canonical documentation impact

Mark each as updated or explicitly not affected:

- [ ] `docs/CURRENT-PROJECT-STATUS.md` — state/authorization changed
- [ ] latest machine checkpoint — project snapshot changed materially
- [ ] `docs/NEXT-STEPS.md` — current gate/blocker/path changed
- [ ] `docs/DELIVERY-ACCEPTANCE.md` — requirement/evidence coverage changed
- [ ] `docs/ARCHITECTURE-ROADMAP.md` — durable architecture direction changed
- [ ] `docs/PROJECT-PLAN.md` — macro phase/deadline allocation changed
- [ ] `docs/PROJECT-PROGRESS-LOG.md` — completed material evidence/decision recorded
- [ ] ADR — material decision made
- [ ] none of the above are affected

## Review checklist

### Development premises

- [ ] I started from current canonical `main` or explicitly reconciled my branch first.
- [ ] I reviewed `PROJECT-PRINCIPLES`, `CURRENT-PROJECT-STATUS`, `NEXT-STEPS`, `DELIVERY-ACCEPTANCE`, `ARCHITECTURE-ROADMAP` and the applicable frozen artifacts.
- [ ] This work maps to an explicit requirement, official rubric criterion, material delivery risk or required comparison.
- [ ] P0/P1 work was not displaced by unjustified P2 complexity.

### Governance / authorization

- [ ] The current gate explicitly permits every consequential action taken by this PR.
- [ ] No script/workflow was treated as authorized merely because it exists.
- [ ] No frozen artifact was silently mutated.
- [ ] No evaluator/private/blind material leaked into the agent/runtime path.
- [ ] Failed/consumed evidence was preserved rather than hidden or rerun silently.

### Evidence quality

- [ ] Class C choices include a simple baseline and materially credible alternatives.
- [ ] Improvement claims are backed by quantitative evidence where measurable.
- [ ] Robustness/failure behavior was evaluated where material.
- [ ] Production-fit trade-offs were considered where material.
- [ ] Any evaluator/judge used as a gate has appropriate validity evidence.
- [ ] Claims are bounded by the actual evidence and known limitations.

### Merge readiness

- [ ] Applicable regression/tests/evals pass.
- [ ] Repository navigation/provenance remains intact.
- [ ] Canonical docs above were updated where required.
- [ ] The PR is focused enough to review without reconstructing unrelated project history.
- [ ] The post-merge next step is clear and does not cross an unopened gate.

## Reviewer focus

<!-- What should the reviewer try hardest to falsify? Examples: requirement mapping, leakage, semantic drift, unsupported claim, missing baseline, deadline risk. -->

1.
2.
3.
