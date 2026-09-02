---
name: Development task
description: Plan a governed project task before implementation
title: "[TASK] "
labels: []
assignees: []
---

## Objective

<!-- What requested outcome should improve? -->

## Source / delivery mapping

- **Requirement / acceptance row:**
- **TAPI / rubric criterion(s):**
- **Material risk, if applicable:**
- **Priority:** P0 / P1 / justified P2

## Current project boundary

- **Current gate from `docs/CURRENT-PROJECT-STATUS.md`:**
- **Does this task require explicit authorization?** yes / no
- **Authorization/frozen artifact if yes:**
- **Forbidden downstream work that must remain untouched:**

## Change classification

- [ ] A — navigation/documentation-only
- [ ] B — non-semantic engineering
- [ ] C — material semantic/experimental/product change

If Class C:

- **Decision question:**
- **Hard constraints:**
- **Simple/null baseline:**
- **Credible alternatives:**
- **Planned quantitative comparison:**
- **Robustness/failure checks:**
- **Production/partner-quality criteria:**

## Scope

### In scope

-

### Out of scope

-

## Acceptance evidence

- **Success condition:**
- **Failure / fail-closed condition:**
- **Tests/evals/artifacts expected:**
- **Claim this evidence would support:**

## Security / custody / provenance

- **Frozen/source-pinned paths affected:**
- **Private/evaluator/blind data involved:**
- **Provider/model calls involved:**
- **Secrets/credentials involved:**
- **Browser/API/SSE sensitive fields affected, if applicable:**

## Canonical docs potentially affected

- [ ] `docs/CURRENT-PROJECT-STATUS.md`
- [ ] `docs/DELIVERY-PLAN.md`
- [ ] `docs/ARCHITECTURE.md`
- [ ] `docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`
- [ ] `docs/DELIVERY-ACCEPTANCE.md`
- [ ] `docs/FINAL-HANDOFF-RUNBOOK.md`
- [ ] `docs/RUBRIC-TO-EVIDENCE.md`
- [ ] progress/evidence record
- [ ] ADR
- [ ] none

## Definition of Ready

- [ ] Requirement/rubric/risk mapping is explicit.
- [ ] P0/P1/P2 priority is justified.
- [ ] Current gate and authorization boundary were checked.
- [ ] Scope and non-goals are explicit.
- [ ] Evidence required for success/failure is defined.
- [ ] Simple baseline exists for a material comparison.
- [ ] Hidden/private/frozen boundaries are understood.
- [ ] Deadline impact is acceptable under `docs/DELIVERY-PLAN.md`.

## Definition of Done

- [ ] Intended evidence exists and is reproducible.
- [ ] Applicable tests/evals/regressions pass.
- [ ] No unauthorized gate/partition/provider access occurred.
- [ ] No frozen/source-pinned evidence was silently mutated.
- [ ] Material decisions have ADR/trade-offs/reversal triggers when applicable.
- [ ] Canonical docs were updated only where their responsibility changed.
- [ ] Claims remain bounded by evidence and limitations.
- [ ] Next step after completion is explicit and authorized.
