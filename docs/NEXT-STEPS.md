# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 08:04 BRT  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

This file is the short-horizon execution plan. It does not itself authorize a scientific gate, live provider call, real customer mutation or provider selection.

## 1. Final provider-free handoff — complete

ADR-017 / issue #60 closed the final unblocked P0/P1 acceptance-audit work.

```text
acceptance rows                         83
PASS_EVIDENCED                          41
PASS_BOUNDED                            40
EXTERNALLY_BLOCKED                       1   C4 / EV-012
UNEXECUTED_GATED                         1   live provider quality
GAP_ACTION_REQUIRED                      0
clean-checkout production tests        251 passed
ADR-004 regression                      12 passed
EV-007 / EV-008 / EV-011               PASS / exact frozen SHAs
ADR-016 demo                             5 / 5 / exact 43903731…
evidence index                          30 / 30 resident blobs / 0 violations
provider calls                           0 / 32
credential/account probes               0
real customer mutations                 0
final PR-associated workflows          14 / 14 success
```

Canonical ADR-017 artifacts:

- `docs/adr/017-final-handoff-acceptance-audit-2026-08-28.md`;
- `research/frozen/final-handoff-acceptance-audit-freeze-v1.json`;
- `research/results/final-handoff-acceptance-audit-2026-08-28.json`;
- `docs/FINAL-HANDOFF-RUNBOOK.md`;
- `docs/RUBRIC-TO-EVIDENCE.md`;
- `scripts/validate_final_handoff_audit.py`;
- `.github/workflows/final-handoff-acceptance-audit.yml`.

Do not reinterpret the 81 evidenced/bounded rows as proof for the two deliberately non-pass rows or as unconditional production readiness.

## 2. Immediate unblocked work — submission/review hygiene only

The 83-row audit found **zero unblocked `GAP_ACTION_REQUIRED` rows**. Do not create more runtime architecture merely to increase implementation breadth.

The remaining provider-free work before the 2026-09-08 submission is limited to hygiene:

1. verify that the external submission surface points reviewers to the root README, final runbook, rubric crosswalk and exact evidence/audit files;
2. keep issue/PR/repository references consistent with the reconciled `main`;
3. avoid editing ADR-017 direct frozen artifacts. If one genuinely must change, create a prospective version/amendment and revalidate rather than silently invalidating frozen blob identities;
4. immediately before submission, rerun the canonical clean commands only if `main` changes after reconciliation;
5. preserve explicit non-claims for provider quality, C4, real customer mutation, deployment rollback, global architecture freeze and production readiness.

No new evaluation campaign is authorized merely because time remains.

## 3. Scientific critical path — unchanged and parallel

Current scientific gate: `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

Exact missing evaluator-side deterministic score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
```

The only scientific action is exact artifact recovery/provisioning. Reconstruction, rescoring and substitution are forbidden.

If the exact artifact is recovered:

1. verify SHA-256, byte count, row count and 36-parent × 4-arm geometry before analysis;
2. run only the already authorized per-group/slice reporting;
3. independently validate;
4. freeze/reconcile before any later scientific gate.

If it remains unavailable at handoff, retain `C-13 / EV-012 = EXTERNALLY_BLOCKED`.

## 4. Live provider comparison — implementation complete / execution gated

```text
comparison design                   ADR-008 / FROZEN
clients + authorization             ADR-009 / FROZEN
executor                            ADR-010 / FROZEN
live custody wrapper                ADR-011 / FROZEN
plan SHA-256                        69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
max live calls                      32
calls consumed                       0
provider selected                   NO
```

Issue #44 is the only live execution task. Before attempt 0 it requires **both** explicit OpenAI/Google secrets and one canonical durable custody root. If either is absent:

- remain at 0/32;
- do not probe credentials/accounts;
- do not create an alternative executor or custody root;
- keep `E-11 / P1-MODEL-PROVIDER-QUALITY = UNEXECUTED_GATED`.

If genuinely provisioned, execute the exact frozen envelope once. Freeze either the exact candidate ID or `NO_SELECTION`; do not change M1–M10 or call geometry after observing outcomes.

## 5. Frozen production/reliability foundation

Do not redesign these accepted boundaries unless a newly measured P0/P1 blocker requires a prospective change:

```text
ADR-004  Agent Controller                              FROZEN
ADR-005  production action safety                     FROZEN
ADR-006  provider-neutral DecisionSource              FROZEN
ADR-007  model-call provenance                        FROZEN
ADR-008  provider/model comparison design             FROZEN
ADR-009  concrete provider clients/live authorization FROZEN
ADR-010  provider comparison executor                 FROZEN
ADR-011  governed live execution/custody wrapper      FROZEN
ADR-012  controlled supplied/test action execution    FROZEN
ADR-013  EV-007 failure performance                   FROZEN
ADR-014  EV-008 repeated-run stability                FROZEN
ADR-015  EV-011 customer-safe communication           FROZEN
ADR-016  final-delivery reproduction/evidence         FROZEN
ADR-017  final handoff acceptance audit               FROZEN
```

Key deterministic identities:

```text
EV-007  7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
EV-008  1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
EV-011  cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
DEMO     43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
```

The default `ProductionRuntime` remains action-disabled. ADR-012 remains limited to explicitly controlled supplied/test consequential actions unless a separate real-environment authorization exists.

## 6. Deadline sequence

```text
DONE       ADR-016 clean reproduction + evidence index + integrated demo
DONE       ADR-017 final handoff acceptance audit + unblocked gap closure
NOW        submission/review hygiene only; preserve frozen identities
PARALLEL   issue #44: provision canonical custody + both secrets or remain at 0/32
PARALLEL   recover exact C4 score-row artifact only
IF READY   execute governed provider envelope once; freeze candidate_id or NO_SELECTION
IF FOUND   execute only authorized C4 per-group/slice reporting; validate/freeze
FINAL      reviewer-facing submission links + evidence-honest claims before 2026-09-08
```

## 7. Final pre-submission smoke check

If `main` changes after ADR-017 reconciliation, rerun from a clean checkout:

```bash
python -m pip install -e ".[dev]" -e "research/e2[dev]"
python -m pytest -q tests
python -m pytest -q research/e2/tests/test_controller.py
python scripts/validate_ev007_failure_campaign.py
python scripts/validate_ev008_stability_campaign.py
python scripts/validate_ev011_communication_campaign.py
python scripts/validate_delivery_reproduction.py
python scripts/validate_final_handoff_audit.py
```

Do not update frozen expected SHAs merely to make a changed checkout pass.

## 8. Deferred unless a new measured P0/P1 gap appears

Continue deferring RAG/vector DB/reranking, persistent memory, MCP, multi-agent orchestration, adaptive routing/model selection, rich UI and large shared-core refactors.

The final acceptance audit is the decision rule: **zero unblocked gaps means stop adding architecture**. External blockers/gates must remain visible rather than being replaced by speculative implementation.
