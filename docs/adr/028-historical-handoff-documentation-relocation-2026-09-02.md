# ADR-028 — Historical Handoff Documentation Relocation and Active-Docs Supersession

**Date:** 2026-09-02  
**Status:** ACCEPTED  
**Scope:** documentation/evidence lifecycle only; no runtime, evaluator, provider or customer-action semantic change  
**Related:** ADR-017, issue #126, PR #127

## Context

ADR-017 froze the final provider-free handoff audit on 2026-08-28. Its v1 freeze intentionally pinned exact Git blobs for reviewer-facing artifacts including:

- root `README.md`;
- `docs/FINAL-HANDOFF-RUNBOOK.md`;
- `src/academy_tractian/handoff_audit.py`;
- the audit/test/workflow artifacts.

That freeze was valid evidence for the state at that time. It also recorded the then-correct provider state as `0/32`, provider not selected, and other August 28 boundaries.

After ADR-017:

- D01 executed 32/32 governed Cloudflare attempts;
- the provider result became `NO_SELECTION` with measured live resource/quality evidence;
- D02 was defined prospectively;
- TAPI stack/technique/output coverage was expanded;
- realtime observability/frontend became P0 delivery work;
- active repository documentation required factual consolidation.

Keeping the August 28 README/runbook bytes at their original mutable paths would therefore make the current documentation materially false. Updating them directly made the ADR-017 exact-blob regression fail, correctly revealing that the historical handoff proof and current documentation lifecycle had been conflated.

## Decision

### 1. Preserve ADR-017 and its v1 freeze unchanged

The following remain historical evidence and are not rewritten:

- `docs/adr/017-final-handoff-acceptance-audit-2026-08-28.md`;
- `research/frozen/final-handoff-acceptance-audit-freeze-v1.json`.

Their claims remain scoped to the 2026-08-28 handoff state.

### 2. Relocate exact historical mutable-path bytes

Exact historical bytes that can no longer occupy active mutable paths are preserved at immutable archive locations:

| Original v1 path | Historical archive path | Git blob |
|---|---|---|
| `README.md` | `docs/archive/final-handoff-v1/README.md` | `7298d2b4d7546b4ea93b64021faf95fb24958b0f` |
| `docs/FINAL-HANDOFF-RUNBOOK.md` | `docs/archive/final-handoff-v1/FINAL-HANDOFF-RUNBOOK.md` | `c7df131f555e3b07161fd1d518965958d245555c` |
| `src/academy_tractian/handoff_audit.py` | `docs/archive/final-handoff-v1/handoff_audit.py` | `db5e851a93f72421c6135c7dda207615858fd8b6` |

The machine-readable relocation contract is:

`research/frozen/final-handoff-documentation-relocation-v2.json`

### 3. Keep the 83-row audit historical

`final-handoff-acceptance-audit-2026-08-28.json` remains an 83-row historical audit. Its provider row is not retroactively changed from `0/32` to the later D01 outcome.

The current `handoff_audit.py` continues validating that historical packet but resolves the three mutable reviewer-document pins through the archive paths defined above.

This is a storage/lifecycle adaptation, not a rescore.

### 4. Active documentation becomes intentionally mutable until final freeze

Current truth is owned by the consolidated active documentation hierarchy, especially:

- `docs/CURRENT-PROJECT-STATUS.md`;
- `docs/DELIVERY-PLAN.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DELIVERY-ACCEPTANCE.md`;
- `docs/FINAL-HANDOFF-RUNBOOK.md`.

These documents must remain factually current through implementation/testing. They are not exact-blob frozen on 2026-09-02.

A new exact final-documentation freeze is required **after** hard visual/feature freeze and clean reproduction, when the final active docs are actually ready to become immutable delivery evidence.

## Alternatives considered

### Restore old README/runbook to satisfy ADR-017

Rejected. It would make the current repository claim `0/32` after D01 completed, intentionally preserving false current state for the sake of a historical path pin.

### Modify ADR-017/v1 freeze in place

Rejected. That would destroy historical evidence and rewrite the conditions under which the August 28 handoff passed.

### Delete/disable the ADR-017 regression

Rejected. The freeze detected a real lifecycle design flaw. Historical integrity must remain tested.

### Copy the entire August 28 repository snapshot

Rejected as unnecessarily large. Only mutable direct pins that must change are relocated; unchanged direct pins remain validated in place, while Git history retains the full repository snapshot.

## Validation obligations

Tests must prove:

1. the ADR-017 v1 freeze file retains its exact Git blob;
2. each relocated historical blob is byte-exact at its archive path;
3. unchanged v1 direct pins remain byte-exact in place;
4. the historical 83-row audit still validates with zero failures;
5. active README/runbook may differ from the v1 bytes;
6. current documentation does not claim that ADR-017's historical `0/32` provider state is current.

## Boundaries

This ADR does **not**:

- alter agent/controller/tool behavior;
- alter evaluator scoring semantics;
- alter D01/D02 experiment semantics;
- authorize provider inference;
- authorize customer mutation;
- authorize paid spillover;
- make the August 28 audit current again;
- authorize a final production-readiness claim.

## Reversal trigger

If a stronger repository-wide immutable snapshot mechanism is introduced before final delivery, it may supersede this relocation mechanism prospectively, but ADR-017/v1 and the archived exact bytes remain historical evidence.
