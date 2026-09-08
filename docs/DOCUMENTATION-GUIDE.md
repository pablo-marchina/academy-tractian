# Documentation Guide

**Status:** ACTIVE docs-as-code governance  
**Last reviewed:** 2026-09-08 BRT  
**Research record:** [`research/2026-09-06-documentation-best-practices.md`](research/2026-09-06-documentation-best-practices.md)

The documentation system is optimized for **finding the right answer quickly without destroying scientific provenance**.

## 1. Organize by user need

Use four primary documentation purposes:

| Need | Type | Project examples |
|---|---|---|
| learn | tutorial / quickstart | `GETTING-STARTED.md` |
| accomplish a task | how-to | `FINAL-HANDOFF-RUNBOOK.md`, `CONTRIBUTING.md` |
| look up exact facts | reference | active status, provider status, acceptance, TAPI crosswalk, codebase map |
| understand why | explanation | architecture, security model, ADRs, principles |

Do not force one document to be tutorial, API reference, architecture essay and progress log simultaneously.

## 2. One mutable owner per question

Mutable facts must have one canonical owner. Other docs link to it instead of maintaining an independent second version.

Examples:

- overall current state → `ACTIVE-PROJECT-STATUS.md`;
- provider selection / qualification → `PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`;
- sequence/priorities → `DELIVERY-PLAN.md`;
- architecture → `ARCHITECTURE.md`;
- final DoD → `DELIVERY-ACCEPTANCE.md`;
- operations/promotion/rollback → `FINAL-HANDOFF-RUNBOOK.md`;
- notable human-visible evolution → `CHANGELOG.md`.

This is the primary anti-drift rule.

## 3. Lifecycle metadata

At the top of active docs, include only useful metadata such as:

```text
Status
Audience/goal when useful
Last verified/rebaseline date
Current evidence anchor when claim-sensitive
Canonical related document
```

Do not add fake owner names, fake review dates or unsupported precision.

Lifecycle values:

- **ACTIVE** — prospectively maintained truth;
- **FROZEN/HISTORICAL** — immutable evidence for a past scope;
- **SUPERSEDED** — old navigation path pointing to a replacement;
- **EXPERIMENTAL/PREREGISTERED** — protocol, not a result;
- **NON-CLAIM/PENDING** — evidence does not yet permit promotion.

A completed negative experiment is not `PENDING`: record the result (`NO_SELECTION`, `REJECT`, etc.) and separately mark the next research step as pending.

## 4. Write for scannability

- start with the answer/current state;
- use meaningful headings;
- keep paragraphs focused;
- use tables for state matrices;
- use checklists for procedures/gates;
- use code blocks for exact state machines/commands;
- place advanced detail after basic information;
- prefer links over duplicate mutable facts.

The frontend follows the same principle through a task-driven hierarchy: Home for the question, contextual Result/evidence for the answer, Analyses for history and Technical for specialist depth.

## 5. Architecture documentation

Use C4-inspired levels only when they add value:

1. System Context;
2. Containers;
3. Dynamic/Deployment;
4. component/code diagrams only when materially useful.

Architecture docs must distinguish **promoted production topology** from **research/challenger topology**. A provider experiment branch, benchmark runner or QA job is not automatically a production component.

## 6. ADR rules

Create an ADR for a durable material architecture/semantic decision, not every code edit. Capture decision/status/date, problem, constraints, alternatives/baseline, evidence, consequences and reversal trigger.

Accepted/frozen ADRs are historical records. Supersede prospectively rather than rewriting original rationale.

## 7. Changelog rules

`CHANGELOG.md` is curated for humans:

- keep `Unreleased` at the top;
- use ISO dates for milestones;
- group meaningful changes;
- do not dump every commit;
- record negative qualification outcomes when they materially change the technical path.

## 8. Security documentation

Maintain root `SECURITY.md` for vulnerability reporting/supported target and `SECURITY-MODEL.md` for assets, boundaries, threats, controls and open evidence.

Update security docs only when a trust/security boundary changes. A research provider failure with no production topology/authority change does not by itself require inventing a new production threat model.

## 9. Evidence versus documentation

Evidence answers **what happened under an exact protocol/identity**. Active documentation answers **what is true now**.

Never rewrite consumed experiment packets, locked/frozen inputs/results, committed historical progress notes, hash-pinned artifacts or old ADR rationale.

```text
new evidence
→ prospective active-doc update
→ new append-only progress/result record if material
→ old evidence unchanged
```

A failed provider qualification remains failed evidence even if a later challenger passes.

## 10. Identity discipline

Track independently when they differ:

- repository/source branch HEAD;
- backend runtime SHA/deployment;
- frontend SHA/deployment;
- supplied-API SHA/deployment;
- production provider/model/route identity;
- provider-research branch/manifest/population identity;
- frozen runner/bootstrap identity;
- exact historical acceptance/evidence identity.

A docs/source merge does not imply backend promotion. A provider-research commit does not imply provider promotion. A later challenger does not retroactively change a prior `NO_SELECTION` result.

## 11. Provider evidence discipline

For provider/model experiments:

- freeze population/rubric/gates before scored evidence;
- distinguish preflight from scored attempts;
- distinguish transport/account-capacity failures from model-quality failures;
- record retries/fallback/repair policy explicitly;
- do not remove failures from denominator after observing them;
- do not call a single-provider qualification a comparative tournament;
- do not call `NO_SELECTION` a winner;
- require post-selection E2E before production promotion;
- document provider account/admission limitations without publishing secrets.

## 12. Documentation Definition of Done

For a material code/product/research state change:

- [ ] current state owner updated;
- [ ] provider-status owner updated when provider evidence changed;
- [ ] execution plan updated when dependency order changed;
- [ ] architecture updated if promoted/challenger responsibility changed materially;
- [ ] runbook updated if operation/promotion/recovery changed;
- [ ] acceptance/TAPI updated if requirement/evidence state changed;
- [ ] Getting Started/Playwright updated only if user/browser behavior changed;
- [ ] security model updated only if trust boundary changed;
- [ ] changelog updated if human/reviewer-visible;
- [ ] presentation pack claim discipline updated;
- [ ] ADR/decision record added if a durable decision requires it;
- [ ] append-only progress evidence added when historically material;
- [ ] frozen evidence left untouched;
- [ ] links remain relative where repository-local;
- [ ] no claim exceeds evidence.

## 13. Drift audit after a material sync

Before merging documentation reconciliation:

1. compare against current production identities and current research branch identity;
2. search active docs for stale provider states such as “tournament pending”, stale candidate counts or superseded winners;
3. check that historical/frozen files are not modified;
4. ensure current-state/provider facts have one mutable owner and secondary docs link/qualify them;
5. verify presentation instructions match actual hosted navigation and current provider non-claims;
6. confirm negative results remain represented as negative results;
7. run docs/link/regression gates that apply;
8. do not deploy application services merely because documentation changed.

## 14. Source research baseline

This guide derives from the repository's captured documentation research and adapts Diátaxis, GitHub docs practices, C4, ADR practices, OWASP threat modeling and Keep a Changelog to the project's stronger scientific-provenance constraints.
