# Documentation Best-Practices Research — 2026-09-06

**Status:** research record / applied  
**Question:** How should the project documentation be structured and maintained so users, reviewers and developers can find current truth quickly without damaging historical evidence?

## Sources reviewed

### Diátaxis

Official source: https://diataxis.fr/

Relevant principle: documentation serves four distinct needs — **tutorials, how-to guides, reference and explanation**. Mixing them indiscriminately makes documents harder to use.

Applied here:

- tutorial → `GETTING-STARTED.md`;
- how-to → runbook + contributing + acceptance procedures;
- reference → active status, acceptance, TAPI, codebase map;
- explanation → architecture, security model, ADRs/principles.

### GitHub documentation practices

Official sources:

- https://docs.github.com/en/contributing/writing-for-github-docs/best-practices-for-github-docs
- https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories
- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors

Relevant principles:

- align content to audience/user goal;
- structure by priority and reading order;
- use plain language and scannable headings;
- provide README/contribution/security guidance;
- protect important branches with required checks.

Applied here:

- root README reduced to current product/use/navigation;
- docs hub organized by task/audience;
- `SECURITY.md` added;
- contributing rules updated to current active status and docs lifecycle;
- progressive disclosure reflected in docs and product UX.

### C4 model

Official sources:

- https://c4model.com/diagrams
- https://c4model.com/diagrams/system-context
- https://c4model.com/diagrams/container
- https://c4model.com/diagrams/notation

Relevant principles:

- system context + container views are sufficient for most teams;
- add dynamic/deployment views where useful;
- name elements, label directional relationships/protocols and technology choices;
- diagrams should stand on their own and fit audience/detail level.

Applied here:

- `ARCHITECTURE.md` now starts with current System Context and Containers;
- a dynamic investigation sequence documents the important cross-boundary flow;
- trust boundaries and current versus future claims are explicit;
- outdated candidate topology language was removed.

### Architectural Decision Records

Official/community reference: https://adr.github.io/

Relevant principle: material decisions should preserve context, rationale, consequences and reversal/supersession rather than silently editing historical reasoning.

Applied here:

- accepted/frozen ADRs remain immutable;
- active docs may supersede their current role prospectively;
- material future decisions require evidence + reversal trigger;
- Release 0 provisional provider status does not rewrite final provider `DP-004`/frozen tournament evidence.

### OWASP Threat Modeling

Official source: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html

Relevant four-question loop:

1. What are we working on?
2. What can go wrong?
3. What are we going to do about it?
4. Did we do a good enough job?

Applied here:

- new active `SECURITY-MODEL.md` maps assets, trust boundaries, threats, current mitigations and open evidence;
- threat model update triggers are explicit;
- full SECURITY-V1 remains a non-claim until hosted campaign evidence exists.

### Keep a Changelog

Official source: https://keepachangelog.com/

Relevant principles:

- changelog is for humans, not an automatic Git log;
- keep `Unreleased` at the top;
- use meaningful change categories and ISO dates.

Applied here:

- root `CHANGELOG.md` added with Release 0 and UX milestones plus `Unreleased`.

## Project-specific adaptation

Generic documentation guidance alone is insufficient because this repository is also a scientific/evaluation evidence archive. Therefore the project adds a stronger rule:

```text
active documentation = prospectively editable current truth
historical/frozen evidence = immutable truth for its original scope
```

When current reality changes, active docs are updated and a new progress/evidence record is added; old frozen bytes are not rewritten.

## Audit findings before rebaseline

The 2026-09-06 audit found:

- root README still claimed remote deployment/IAM/provider topology was unproved;
- `ARCHITECTURE.md` still described Neon Auth/Railway/provider/TRACTIAN as candidate or pending;
- `DELIVERY-PLAN.md` still sequenced gates that Release 0 had already passed;
- `DELIVERY-ACCEPTANCE.md` did not clearly separate Release 0 acceptance from final-project DoD;
- TAPI crosswalk still said final remote topology was unselected;
- runbook still used placeholder future-production language;
- `NEXT-STEPS.md` duplicated mutable priorities despite being designated a compatibility path;
- Playwright docs described the old UI rather than current Results/Evidence/Investigation/Engineering tasks;
- no curated changelog/security reporting policy/current threat model/first-user tutorial existed;
- post-release UX progress through `2ca6215...` was not documented.

## Decision

Adopt the task-oriented docs architecture and anti-drift lifecycle in `DOCUMENTATION-GUIDE.md`, update all active/canonical documentation to the current hosted Release 0 + UX state, and preserve frozen/date-stamped historical evidence unchanged.