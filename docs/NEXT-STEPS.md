# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 06:21 BRT  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

This file is the short-horizon execution plan. It does not itself authorize a scientific gate, live provider call, real customer mutation or provider selection.

## 1. Scientific critical path — unchanged and parallel

Current scientific gate: `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

Exact missing evaluator-side deterministic score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
```

Immediate scientific work is exact artifact recovery/provisioning only. Reconstruction, rescoring and substitution are forbidden. If recovered, run only the already authorized per-group/slice reporting, independently validate and freeze before any later scientific gate.

## 2. Live provider comparison — implementation complete / execution separately gated

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

Issue #44 is the only live execution task. Before attempt 0 it requires both explicit OpenAI/Google secrets and one canonical durable custody root. If either is absent, stay at 0/32 calls; credential/account probing is forbidden.

## 3. Frozen production/reliability foundation

Do not redesign the accepted boundaries before final handoff unless a measured P0/P1 blocker requires a prospective change.

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
```

Key deterministic identities:

```text
EV-007  7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
EV-008  1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
EV-011  cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
DEMO     43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
```

The default `ProductionRuntime` remains action-disabled. ADR-012 is limited to explicitly controlled supplied/test consequential actions unless a separate real-environment authorization exists.

## 4. ADR-016 package — complete

Issue #57 / PR #58 completed the previously highest-value unblocked provider-free work.

```text
clean-checkout production tests              237 passed
ADR-004 regression                            12 passed
EV-007 / EV-008 / EV-011                     PASS
integrated provider-free scenarios             5 / 5
exact integrated traces evaluated              5 / 5
evidence-index entries                        31
repository-resident evidence                  30
resident Git blobs resolved                   30 / 30
index violations                               0
provider calls                                 0
credential/account probes                      0
real customer mutations                        0
semantic/private/blind access                  0
triggered workflows                           12 / 12 success
```

Canonical artifacts:

- `docs/adr/016-provider-free-final-delivery-reproduction-evidence-package-2026-08-28.md`;
- `research/frozen/provider-free-final-delivery-reproduction-evidence-freeze-v1.json`;
- `research/results/provider-free-final-delivery-demo-result-2026-08-28.json`;
- `research/results/final-delivery-evidence-index-2026-08-28.json`;
- `scripts/validate_delivery_reproduction.py`;
- `.github/workflows/final-delivery-provider-free-reproduction.yml`.

Do not reinterpret the package as live-provider, real-customer, C4 or production-readiness evidence.

## 5. NEXT provider-free P0/P1 — final handoff acceptance audit + gap closure

The remaining unblocked work should now be driven directly by [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md), especially Sections 4–12. Do not add optional architecture merely to increase implementation breadth.

Create one final acceptance audit that maps every material P0/P1 requirement to one of:

- `PASS_EVIDENCED` — exact repository evidence exists and resolves;
- `PASS_BOUNDED` — required behavior is demonstrated under an explicitly limited supplied/provider-free scope;
- `EXTERNALLY_BLOCKED` — completion requires an unavailable external artifact/prerequisite;
- `UNEXECUTED_GATED` — implementation exists but execution is separately authorized/gated;
- `GAP_ACTION_REQUIRED` — an unblocked repository/documentation gap remains and must be closed before delivery.

### Required audit dimensions

At minimum audit and resolve:

1. P0 project-level rows REQ-001, REQ-003, REQ-004/020, REQ-021 and REQ-017;
2. all P0 agent-construction rows in `DELIVERY-ACCEPTANCE.md`;
3. all EV-001 through EV-012 evaluation-framework rows;
4. benchmark/security integrity constraints REQ-018/019 and PC-001 through PC-006;
5. applicable P1 production-quality rows;
6. all ten final demonstration requirements;
7. final documentation/package requirements;
8. official eight academic excellence dimensions.

Every PASS must name the strongest concrete repository artifact, command or frozen result. Do not infer PASS from intent or architecture prose alone.

### Gap-closure priority

For each `GAP_ACTION_REQUIRED`, prefer the smallest change that closes an actual P0/P1 acceptance row. Likely high-value final-package gaps to inspect first are:

- root README navigation/setup/run/evaluate instructions;
- exact dependency/runtime prerequisites;
- one concise real handoff/runbook covering failure/fallback/rollback within implemented scope;
- rubric-to-evidence navigation for reviewers;
- limitations/non-claims and external blocker presentation;
- one final documented clean regression command/result.

Do not fabricate latency, resource or cost measurements. Record them only where actual evidence exists.

### Final audit acceptance

```text
all P0/P1 rows classified                     YES
all PASS rows linked to exact evidence          YES
all unblocked GAP_ACTION_REQUIRED rows closed   YES
provider/C4 blockers honestly labeled           YES
clean provider-free reproduction                PASS
full production regression                      PASS
live provider calls consumed                    0 unless #44 separately becomes executable
credential/account probes                       0
real customer mutations                         0
claims beyond evidence                          0
```

Freeze the final audit only after gaps are closed and the final regression passes.

## 6. Parallel provider execution

If issue #44 becomes executable, run the exact ADR-009/010/011 envelope once and freeze either an exact candidate ID or `NO_SELECTION`. Do not create a new executor/custody root to evade existing evidence.

After a valid provider result exists, rerun compatible EV-007/008/011 definitions against that governed result without changing metric definitions after seeing the live outcomes.

If #44 remains blocked at handoff, mark provider/model selection as `UNEXECUTED_GATED`; do not convert provider-free evidence into a selected-provider claim.

## 7. Parallel C4 recovery

Recover the exact score-row artifact only. If it remains unavailable at handoff, preserve the exact SHA/bytes/rows identity and mark per-group/slice reporting as `EXTERNALLY_BLOCKED` rather than reconstructing or fabricating completeness.

## 8. Deadline sequence

```text
DONE       ADR-016 clean reproduction + evidence index + integrated demo
NEXT       final handoff acceptance audit + unblocked gap closure
PARALLEL   issue #44: provision canonical custody + both secrets or remain at 0/32 calls
PARALLEL   recover exact C4 score-row artifact only
WHEN READY execute exact live provider envelope once; freeze candidate_id or NO_SELECTION
FINAL      full regression + handoff package + evidence-honest claims before 2026-09-08
```

## 9. Deferred unless measured P0/P1 gap

Continue deferring RAG/vector DB/reranking, persistent memory, MCP, multi-agent orchestration, adaptive routing/model selection and rich UI. Avoid a large shared-core refactor before the final acceptance audit demonstrates a concrete need.