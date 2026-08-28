# ADR-017 — Final handoff acceptance audit and gap closure

- **Date:** 2026-08-28
- **Status:** Accepted for freeze after clean-checkout validation
- **Issue:** #60
- **PR:** #61
- **Starting canonical main:** `0366f2214afce5bc54fca255669cd5befa517896`
- **Validated pre-freeze implementation head:** `79101b51c7ff85a2ed08ba229bd54760eab1c226`

## Context

ADR-016 froze the clean provider-free delivery reproduction and exact evidence index, but the final academic/engineering handoff still needed one last requirement-driven audit. In particular, the root README did not yet expose the full reviewer path, no single handoff runbook covered setup/failure/fallback/reversal, and no rubric-to-evidence crosswalk made the strongest evidence and non-claims easy to inspect.

The remaining work therefore was not a reason to add architecture. It was a Class C acceptance audit over the already delivered runtime/evaluator path, followed only by gap closure that improved reviewability without changing frozen experiment semantics.

## Prospective audit population

Issue #60 preregistered one row-level audit. Before inspecting/classifying rows, a counting correction was posted prospectively because the source acceptance matrix contains 13 evaluation-framework rows and 7 benchmark/security rows, not the initially transcribed counts.

The frozen population is exactly 83 rows:

| Group | Scope | Rows |
|---|---|---:|
| A | P0 project | 5 |
| B | Agent construction | 13 |
| C | Evaluation framework | 13 |
| D | Benchmark/security constraints | 7 |
| E | P1 production/quality | 14 |
| F | Demonstration | 10 |
| G | Documentation/package | 13 |
| H | Academic excellence dimensions | 8 |
| **Total** |  | **83** |

Allowed dispositions were fixed before result interpretation:

- `PASS_EVIDENCED` — direct repository evidence satisfies the row;
- `PASS_BOUNDED` — the row is satisfied only within an explicitly narrower evidenced scope;
- `EXTERNALLY_BLOCKED` — the required continuation depends on an unavailable external artifact/prerequisite;
- `UNEXECUTED_GATED` — the governed design exists but execution is intentionally not authorized/provisioned;
- `GAP_ACTION_REQUIRED` — unblocked work remains to close the row.

## Decision

Accept the final handoff only through a machine-readable 83-row audit plus deterministic structural validation. A green audit is valid only if it preserves the existing provider/scientific/action boundaries rather than relabelling gated or blocked work as complete.

The final handoff package adds:

1. reviewer-ready root `README.md` with exact setup, reproduction, demo, evidence and non-claim navigation;
2. `docs/FINAL-HANDOFF-RUNBOOK.md` with setup, monitoring surfaces, failure/fallback rules, provider gate and bounded reversal/rollback guidance;
3. `docs/RUBRIC-TO-EVIDENCE.md` mapping official academic dimensions plus P0/P1 capabilities to exact evidence and explicit limitations;
4. `research/results/final-handoff-acceptance-audit-2026-08-28.json` containing every preregistered row and disposition;
5. `src/academy_tractian/handoff_audit.py` plus validator/tests that reject structural overclaim;
6. a dedicated clean-checkout workflow that reruns production tests, ADR-004, EV-007, EV-008, EV-011, ADR-016 and the final audit validator.

No runtime architecture, provider geometry, scientific score, frozen campaign result or real-customer behavior is changed by this decision.

## Observed pre-freeze result

Clean PR validation on head `79101b51c7ff85a2ed08ba229bd54760eab1c226` produced:

- production tests: **246/246 PASS**;
- ADR-004 controller regression: **12/12 PASS**;
- EV-007 report: `7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9` — PASS;
- EV-008 report: `1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8` — PASS;
- EV-011 report: `cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e` — PASS;
- ADR-016 integrated demo: `43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445` — PASS;
- ADR-016 evidence index: 31 entries / 30 repository-resident / 30 resolved / 0 violations;
- final handoff audit validator: **PASS**;
- all workflows associated with the validated head: **14/14 success**.

Audit disposition:

| Status | Rows |
|---|---:|
| `PASS_EVIDENCED` | 41 |
| `PASS_BOUNDED` | 40 |
| `EXTERNALLY_BLOCKED` | 1 |
| `UNEXECUTED_GATED` | 1 |
| `GAP_ACTION_REQUIRED` | 0 |
| **Total** | **83** |

The two non-pass rows are intentional and mandatory:

- `C-13 / EV-012` remains `EXTERNALLY_BLOCKED` because the exact evaluator-side C4 score-row artifact is unavailable: SHA-256 `b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`, 177350 bytes, 144 rows;
- `E-11 / P1-MODEL-PROVIDER-QUALITY` remains `UNEXECUTED_GATED`: provider comparison is still 0/32 calls, credentials/account probes are zero and no provider/model is selected.

These are not documentation gaps and must not be converted to PASS by wording changes.

## Structural anti-overclaim checks

The audit validator requires:

- exactly 83 unique row IDs and the preregistered group denominators;
- exactly the observed status counts;
- every pass row to resolve repository evidence;
- every bounded/blocked/gated row to state its limitation;
- every future `GAP_ACTION_REQUIRED` row to carry an explicit action;
- zero unresolved gap rows for this freeze;
- exact C4 and provider dispositions;
- exact EV-007/008/011/demo identities;
- provider calls `0/32`, credential/account probes `0`, real-customer mutations `0`;
- science gate still `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`;
- no provider selection, global architecture freeze or unconditional production-readiness authorization;
- exact reviewer-facing README/runbook/crosswalk Git blob identities.

Negative tests deliberately tamper these invariants, including attempts to relabel the provider or C4 rows as PASS.

## Gap closure accepted

Three unblocked handoff gaps were closed without changing runtime semantics:

- root README reviewer setup/run/evaluate navigation;
- handoff runbook for monitoring/failure/fallback/bounded rollback;
- rubric-to-evidence reviewer crosswalk.

The runbook deliberately says that no infrastructure deployment rollback has been exercised. It documents only the code/config/fail-closed reversal controls that are actually evidenced.

## Consequences

After this ADR freezes and reconciles:

- the provider-free project handoff is reviewer-ready and reproducible within its proven scope;
- blocked/gated rows remain visible rather than being hidden by a binary completion claim;
- no optional architecture should be added merely to improve presentation;
- provider issue #44 may advance only when its explicit secret + custody prerequisites are genuinely provisioned;
- C4 may advance only if the exact missing artifact is recovered under the frozen scientific protocol;
- absent those external prerequisites, remaining delivery work is submission/review hygiene rather than new runtime architecture.

## Non-claims

ADR-017 does **not** establish or authorize:

- live provider/model quality, latency or cost;
- a selected provider/model;
- credential/account probing;
- real customer mutation;
- production action enablement in the default `ProductionRuntime`;
- semantic/private/blind evaluation;
- `FRESH_BLIND` or `LEGACY_LOCKED_TEST` access;
- C4 artifact reconstruction, rescoring or substitution;
- completed independent fresh-blind generalization;
- global final architecture freeze;
- an exercised deployment-infrastructure rollback;
- unconditional production readiness.

The accepted claim is narrower: **the final provider-free handoff acceptance audit is reproducible, evidence-linked, gap-closed for all unblocked handoff work, and explicit about its one external blocker and one governed unexecuted gate.**
