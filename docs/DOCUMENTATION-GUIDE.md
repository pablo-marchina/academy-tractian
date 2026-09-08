# Documentation Guide

**Status:** ACTIVE docs-as-code governance  
**Last reviewed:** 2026-09-07 BRT  
**Research record:** [`research/2026-09-06-documentation-best-practices.md`](research/2026-09-06-documentation-best-practices.md)

The documentation system is optimized for **finding the right answer quickly without destroying scientific provenance**.

## 1. Organize by user need

Use four primary documentation purposes:

| Need | Type | Project examples |
|---|---|---|
| learn | tutorial / quickstart | `GETTING-STARTED.md` |
| accomplish a task | how-to | `FINAL-HANDOFF-RUNBOOK.md`, `CONTRIBUTING.md` |
| look up exact facts | reference | active status, acceptance, TAPI crosswalk, codebase map |
| understand why | explanation | architecture, security model, ADRs, principles |

Do not force one document to be tutorial, API reference, architecture essay and progress log simultaneously.

## 2. One mutable owner per question

Mutable facts must have one canonical owner. Other docs link to it instead of copying a second version.

Examples:

- current state → `ACTIVE-PROJECT-STATUS.md`;
- sequence/priorities → `DELIVERY-PLAN.md`;
- architecture → `ARCHITECTURE.md`;
- final DoD → `DELIVERY-ACCEPTANCE.md`;
- operations → `FINAL-HANDOFF-RUNBOOK.md`;
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

Do not add fake owner names, fake review dates or precision that is not maintained.

Lifecycle values:

- **ACTIVE** — prospectively maintained truth;
- **FROZEN/HISTORICAL** — immutable evidence for a past scope;
- **SUPERSEDED** — old navigation path pointing to a replacement;
- **EXPERIMENTAL/PREREGISTERED** — protocol, not a result;
- **NON-CLAIM/PENDING** — evidence does not yet permit promotion.

## 4. Write for scannability

- start with the answer/current state;
- use meaningful headings;
- keep paragraphs focused;
- use tables for state matrices, not prose walls;
- use checklists for procedures/gates;
- use code blocks for exact state machines/commands;
- place advanced detail after basic information;
- prefer links over duplicate explanations.

The frontend follows the same principle through a **task-driven hierarchy**: Home for the question, contextual Result/evidence for the answer, Analyses for history and Technical for specialist depth. Documentation should mirror the current product task model rather than preserving obsolete UI taxonomy.

## 5. Architecture documentation

Use C4-inspired levels only when they add value:

1. **System Context** — users + external systems, technology-light;
2. **Containers** — major applications/data stores, technologies and communication;
3. **Dynamic/Deployment** — only for flows/deployment claims that are hard to understand statically;
4. component/code diagrams only when they materially improve understanding.

Every architecture diagram should be understandable on its own: state scope, name elements, label directional relationships/protocols, identify technologies where relevant, and explain trust boundaries.

## 6. ADR rules

Create an ADR for a durable material architecture/semantic decision, not every code edit.

An ADR should capture decision/status/date, context/problem, hard constraints, alternatives/baseline, decision/evidence, consequences/trade-offs and reversal trigger.

Accepted/frozen ADRs are historical decision records. If a decision changes, supersede prospectively rather than rewriting original rationale.

## 7. Changelog rules

`CHANGELOG.md` is curated for humans:

- keep `Unreleased` at the top;
- use ISO dates for release/milestone entries;
- group notable changes by Added / Changed / Fixed / Security;
- do not dump every commit;
- include changes that matter to user/operator/reviewer behavior or security/compatibility.

## 8. Security documentation

Maintain both:

- root `SECURITY.md` — vulnerability reporting and supported security target;
- `SECURITY-MODEL.md` — assets, trust boundaries, threats, controls and open evidence.

Update the threat model after material feature, architecture/infrastructure or security-boundary changes. A live incident such as the managed-session fan-out issue requires prospective security-model/runbook updates even when no confidentiality boundary was crossed.

## 9. Evidence versus documentation

Evidence answers **what happened** under an exact protocol/identity. Active documentation answers **what is true now**.

Never rewrite consumed experiment packets, locked/frozen inputs/results, committed historical progress notes, hash-pinned artifacts or old ADR rationale.

Instead:

```text
new evidence
→ prospective active-doc update
→ new progress/ADR/result record if material
→ old evidence unchanged
```

A later production hardening SHA must therefore be documented **alongside**, not substituted into, an older immutable acceptance campaign.

## 10. Production identity discipline

Track these independently when they differ:

- repository/source branch head;
- backend runtime SHA/deployment;
- frontend SHA/deployment;
- supplied-API SHA/deployment;
- exact historical acceptance/evidence SHA.

A docs/source merge does not imply backend promotion. A frontend deploy does not rewrite backend identity. A later hardened backend does not retroactively change the original Release 0 acceptance SHA.

## 11. Documentation Definition of Done

For a material code/product change:

- [ ] current state owner updated;
- [ ] architecture updated if durable topology/responsibility changed;
- [ ] runbook updated if operation/recovery changed;
- [ ] acceptance/TAPI updated if requirement state changed;
- [ ] Getting Started/Playwright updated if user flow changed;
- [ ] security model updated if trust boundary changed;
- [ ] changelog updated if human-visible;
- [ ] presentation pack updated if current hosted UI/claims changed;
- [ ] ADR/decision record added if a durable decision requires it;
- [ ] append-only progress evidence added when historically material;
- [ ] frozen evidence left untouched;
- [ ] links remain relative where repository-local;
- [ ] no claim exceeds evidence.

## 12. Drift audit after a material sync

Before merging documentation-only reconciliation:

1. compare against current hosted backend/frontend/API identities;
2. search active docs for superseded SHAs/UI vocabulary;
3. check that historical/frozen files are not in the diff;
4. ensure current-state facts have one owner and secondary docs link/qualify them;
5. verify presentation instructions match the actual hosted navigation;
6. run repository docs/link/regression gates that trigger for the PR;
7. do not deploy application services merely because documentation changed.

## 13. Source research baseline

This guide was derived from official/current guidance captured in the research note, including Diátaxis, GitHub documentation practices, C4, ADR practices, OWASP threat modeling and Keep a Changelog. External guidance is adapted to this repository's stronger scientific-provenance constraints rather than copied mechanically.