# Documentation Guide

**Status:** ACTIVE docs-as-code governance  
**Last reviewed:** 2026-09-06 BRT  
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

The frontend follows the same principle through Results → Evidence → Investigation → Engineering progressive disclosure.

## 5. Architecture documentation

Use C4-inspired levels only when they add value:

1. **System Context** — users + external systems, technology-light;
2. **Containers** — major applications/data stores, technologies and communication;
3. **Dynamic/Deployment** — only for flows/deployment claims that are hard to understand statically;
4. Component/code diagrams only when they materially improve understanding.

Every architecture diagram should be understandable on its own: state scope, name elements, label directional relationships/protocols, identify technologies where relevant, and explain trust boundaries.

## 6. ADR rules

Create an ADR for a durable material architecture/semantic decision, not every code edit.

An ADR should capture:

- decision/status/date;
- context/problem;
- hard constraints;
- considered alternatives/baseline;
- decision + evidence/rationale;
- consequences/trade-offs;
- reversal trigger.

Accepted/frozen ADRs are historical decision records. If a decision changes, supersede prospectively rather than rewriting the original rationale.

## 7. Changelog rules

`CHANGELOG.md` is curated for humans:

- keep `Unreleased` at the top;
- use ISO dates for release/milestone entries;
- group notable changes by Added / Changed / Fixed / Security (and Deprecated/Removed when applicable);
- do not dump every commit;
- include changes that matter to user/operator/reviewer behavior or security/compatibility.

## 8. Security documentation

Maintain both:

- root `SECURITY.md` — how to report vulnerabilities;
- `SECURITY-MODEL.md` — what the system protects, trust boundaries, threats, controls and open evidence.

Update the threat model after material feature, architecture/infrastructure or security-boundary changes.

## 9. Evidence versus documentation

Evidence answers **what happened** under an exact protocol/identity. Active documentation answers **what is true now**.

Never rewrite:

- consumed experiment packets;
- locked/frozen inputs/results;
- accepted historical progress notes;
- hash-pinned artifacts;
- old ADR rationale.

Instead:

```text
new evidence
→ prospective active-doc update
→ new progress/ADR/result record if material
→ old evidence unchanged
```

## 10. Documentation Definition of Done

For a material code/product change:

- [ ] current state owner updated;
- [ ] architecture updated if durable topology/responsibility changed;
- [ ] runbook updated if operation/recovery changed;
- [ ] acceptance/TAPI updated if requirement state changed;
- [ ] Getting Started/Playwright updated if user flow changed;
- [ ] security model updated if trust boundary changed;
- [ ] changelog updated if human-visible;
- [ ] ADR/decision record added if material decision;
- [ ] frozen evidence left untouched;
- [ ] links remain relative where repository-local;
- [ ] no claim exceeds evidence.

## 11. Source research baseline

This guide was derived from official/current guidance captured in the research note, including Diátaxis, GitHub documentation practices, C4, ADR practices, OWASP threat modeling and Keep a Changelog. External guidance is adapted to this repository's stronger scientific-provenance constraints rather than copied mechanically.