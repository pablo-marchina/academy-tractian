# E14d DEV-only Public Evidence-Resource Canonicalization

**Date:** 2026-08-17  
**Scope:** DEV only  
**Status:** preregistered candidate; structural validation required before real measurement

## Motivation

E14c fixed the action-endpoint representation mismatch and improved real DEV quality while preserving evidence, escalation and safety gates, but action correctness remained below threshold. A sanitized fixed-capture boundary diagnostic then isolated three E10g downgrades, all with reason:

```text
balanced_guard_handoff_without_minimum_visible_evidence
```

A second sanitized diagnostic showed the historical literal-template evidence counter saw those three blocked handoffs as 0 / 0 / 1 distinct public evidence families. That result alone did not justify lowering the E10g threshold of two.

The final shape diagnostic then compared the same fixed evidence plans against only the same ten public GET families already accepted by E10e/E10g, while allowing a concrete frozen public route to map to its canonical template family. The three blocked handoffs became:

```text
2 / 5 / 8 distinct existing public evidence families
```

All three therefore meet the **existing threshold of two** once equivalent concrete route representation is recognized. No blocked handoff remains below threshold after representation normalization.

## Root cause

The E10e `evidence_marker_count()` implementation counts only literal strings such as:

```text
GET /assets/{asset_id}
GET /analyses/{analysis_id}
GET /knowledge/{doc_id}
```

The frozen public ToolSpec registry defines those resources as parameterized routes. A model-visible plan containing, for example, a concrete public route can therefore be semantically within an already-accepted evidence family but receive zero credit from the historical literal-template comparison.

This is the same class of deterministic representation mismatch previously confirmed for action endpoints in E14c.

## Single candidate change

E14d changes only the comparison/counting view used by E10e/E10g:

- preserve exactly the existing ten E10e public evidence families;
- derive concrete-route equivalence from the frozen public ToolSpec source;
- count canonical-template or equivalent concrete-path representation as the same distinct family;
- leave the stored model `evidence_plan` unchanged;
- leave the E10e state-change evidence threshold unchanged;
- leave the E10g human-handoff threshold at **two distinct public evidence families**;
- reject wrong methods, unrelated routes and longer unknown route suffixes;
- preserve E14c action-endpoint canonicalization;
- make no prompt/model/provider/reasoning/completion/scorer/acceptance-threshold change.

## Methodological boundary

E14d uses no private oracle or scorer row in policy. VALIDATION feedback is forbidden. LOCKED_TEST remains forbidden. The diagnostic evidence motivating E14d is aggregate public-contract shape evidence only.

No real model call is authorized until the E14d structural dry-run passes. After structural validation, only a complete DEV-only capture followed by the unchanged E9 v3 private scorer may determine whether the candidate passes the E14 gate.

## Acceptance gate

Unchanged from E14:

| Target | Required |
|---|---:|
| Parsed outputs | 6 |
| Scoreable calls | 6 |
| Real task quality | >= 0.8571 |
| Decision correctness | >= 0.75 |
| Evidence correctness | 1.0 |
| Action correctness | >= 0.75 |
| Escalation correctness | 1.0 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| LOCKED_TEST accessed | false |

VALIDATION remains blocked unless all DEV requirements pass simultaneously.
