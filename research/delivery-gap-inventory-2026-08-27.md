# Integrated Agent + Evaluator delivery-gap inventory — 2026-08-27

**Issue:** #13  
**Class:** B — non-semantic delivery/readiness audit  
**Priority:** P0  
**Source state:** `main` after API-contract reconciliation PR #12  
**Scientific state changed by this audit:** no  
**Provider/model calls:** 0  
**Evaluator/private/gold access:** 0

## 1. Purpose and boundary

This audit answers one question: **what does the repository already implement that can be reused for the final TRACTIAN Agent + Evaluator delivery, and what is still missing before the P0/P1 acceptance matrix can be demonstrated end to end?**

It is deliberately implementation-based. A README statement, historical experiment or scripted fixture is not treated as final-delivery evidence unless the current `main` implementation supports the corresponding claim.

This audit does **not**:

- advance or reinterpret the current `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` scientific gate;
- execute reporting, survivor selection, semantic evaluation, FRESH_BLIND or LEGACY_LOCKED_TEST;
- select a provider/model/runtime/framework;
- create the final `src/`, `tests/`, `config/` production boundary before the applicable architecture decision;
- claim that `research/e2` is production-ready merely because its infrastructure tests pass.

## 2. Status vocabulary

| Status | Meaning |
|---|---|
| `REUSABLE_FOUNDATION` | Current code implements and tests a useful boundary/primitive that should inform the final system, but remains research/reference code until deliberately promoted or reimplemented behind the production boundary. |
| `NEEDS_HARDENING` | A relevant implementation exists, but final acceptance requires materially stronger semantics, production integration or end-to-end evidence. |
| `MISSING` | No current `main` implementation/evidence sufficient for the final capability was found. |
| `BLOCKED_BY_DECISION` | Implementation should not be finalized before an explicit architecture/product/provider decision is authorized and recorded. |
| `EVIDENCE_ONLY` | Historical experiment/research evidence is useful for decisions but is not itself the final runtime/evaluator component. |

## 3. Executive verdict

The repository does **not** need a greenfield rewrite. `research/e2` already provides a strong framework-neutral execution/evaluation foundation:

- 18-operation Canonical ToolSpec;
- exact duplicate-aware API-contract reconciliation;
- runner-owned identity and seed binding;
- strict argument-validation foundation;
- permission/resource-scope policy;
- evidence-aware action gate;
- contract-valid HTTP request builder and transport;
- framework-neutral live/replay execution harness;
- structured trace, normalization and replay;
- scenario/oracle schemas;
- deterministic evaluator suite for trajectory, decision, arguments, evidence, policy, action, conclusion, escalation/handoff and identity/seed safety;
- provenance/config hashing;
- real supplied-API transport/trace/replay evidence.

The critical gap is above and around that foundation:

1. **no Agent Controller currently generates tool proposals, reasons over observations, stops, clarifies, escalates or produces the final response**;
2. E2's `HarnessRunner` explicitly executes proposals emitted by an external runtime and is therefore an execution/evaluation boundary, not an autonomous agent;
3. final failure-continuity/provider-fallback behavior is absent;
4. repeated-run stability is not implemented as a current integrated evaluator/acceptance path;
5. customer-safe communication has schema hooks but no dedicated evaluator enforcing internal-disclosure policy;
6. several current evaluators are intentionally minimal and need stronger semantics before final claims;
7. there is no final production boundary, versioned runtime configuration, observability stack, runbook, rollback path or clean-environment end-to-end reproduction;
8. the required 10-scenario real integrated demo has not been demonstrated.

Therefore the shortest defensible delivery path is **promote the proven boundaries, not the historical research architecture wholesale**.

## 4. Current E2 evidence: what it actually proves

`research/e2/README.md` and `research/39-e2-integrated-completion-report.md` correctly frame E2 as framework-neutral experimental infrastructure. The current code confirms that framing.

### 4.1 Strong reusable foundations

| Component | Current evidence | Status | Final-use implication |
|---|---|---|---|
| Canonical ToolSpec | `research/e2/tool_registry.py`; 18 operations / 17 unique paths, exact duplicate-path invariants | `REUSABLE_FOUNDATION` | Preserve the normalized method/path/operation/parameter semantics behind the final runtime tool boundary. |
| API conformance | `scripts/research/audit_tractian_api_contract.py`; sanitized `research/results/tractian-api-contract-conformance-2026-08-27.json` | `REUSABLE_FOUNDATION` | Use as source-of-truth conformance evidence; do not republish raw partner source. |
| Identity/seed binding | `research/e2/binding.py`, `transport.build_b0_request`, E2 tests | `REUSABLE_FOUNDATION` | Final runtime must retain runner-owned `x-user-id` and evaluation seed; never expose them as model-controlled tool arguments. |
| Strict argument boundary | `research/e2/validation.py`; E2 tests reject invalid enums/unknown/model-controlled arguments | `REUSABLE_FOUNDATION` | Promote deterministic schema validation ahead of any tool execution. |
| Resource/permission policy | `research/e2/policy.py`; negative cross-company tests | `REUSABLE_FOUNDATION` | Keep project policy distinct from backend permission enforcement. |
| Evidence-aware action gate | `research/e2/action_gate.py`; tests block action before required evidence | `REUSABLE_FOUNDATION` | Retain as a deterministic safety boundary around consequential actions. |
| HTTP boundary | `research/e2/transport.py`; real supplied-API probe | `NEEDS_HARDENING` | Request construction is reusable; production transport still needs lifecycle/error/retry/telemetry/fallback policy. |
| Trace model | `research/e2/models.py`, `trace.py`, `trace_normalize.py` | `REUSABLE_FOUNDATION` | Preserve separate proposal/call/result/observation/final events and normalized trace semantics. |
| Replay | `research/e2/replay.py`; deterministic replay tests | `REUSABLE_FOUNDATION` | Useful for evaluation/reproduction; final storage/custody policy still required. |
| Scenario/oracle schema | `research/e2/models.py` | `REUSABLE_FOUNDATION` | Supports decision/evidence/action/conclusion/communication evaluation without exact-string primary scoring. |
| Evaluation suite | `research/e2/evaluation_suite.py` | `NEEDS_HARDENING` | Strong deterministic base, but does not yet close all EV-001..EV-012 requirements. |
| Provenance/config hashing | `research/e2/provenance.py`, `hash.py` | `REUSABLE_FOUNDATION` | Carry into final run manifests/config provenance. |
| E2 CI/probe history | `research/39-e2-integrated-completion-report.md` | `EVIDENCE_ONLY` | 24 tests + real API probe validate infrastructure, explicitly not agent quality. |

### 4.2 The decisive runtime gap

`research/e2/runner.py` states that `HarnessRunner` **does not implement agent reasoning**. Its responsibility is to execute a named tool proposal with arguments, bind immutable runtime context, apply B1/B2/B3 deterministic boundaries, call live/replay transport and record the resulting trace.

There is no current production-capable component in `main` that performs the missing loop:

```text
request
→ interpret context
→ choose decision / next tool / clarification / escalation / stop
→ construct proposal
→ consume observation
→ update evidence state
→ repeat or terminate
→ construct customer-safe final response/handoff
```

That missing controller is the primary blocker for `REQ-017` Agent + Evaluator acceptance.

## 5. P0 project-level acceptance inventory

| Requirement | Status | Current evidence | Exact remaining gap |
|---|---|---|---|
| REQ-001 — individual project | `EVIDENCE_ONLY` | repository/project history | Final self-contained handoff still occurs at delivery. |
| REQ-003 — technical experiment | `EVIDENCE_ONLY` | frozen C4 chain and historical experiments | Current scientific chain must finish its authorized reporting/selection path before final experimental claims are frozen. |
| REQ-004 / REQ-020 — documentation/results | `NEEDS_HARDENING` | extensive canonical research/governance docs | Final README must describe the actually selected runtime/provider/architecture, final quantitative results, limitations and reproduction path. |
| REQ-021 — reproducible handoff | `MISSING` | research package has local pyproject and replay/provenance primitives | No final clean-environment setup/build/run of the integrated production path exists yet. |
| REQ-017 — Agent + evaluation framework | `MISSING` | evaluator/execution foundation exists; no autonomous Agent Controller | Build and demonstrate one operational agent path integrated with capture + evaluation without gold leakage. |

## 6. P0 agent-construction inventory

| Coverage | Status | What exists now | Final blocker / hardening required |
|---|---|---|---|
| REQ-002 / REQ-009 — real API + technical reads | `NEEDS_HARDENING` | 18-tool contract, HTTP builder/transport, real CEN-01 probe | Integrate the selected Agent Controller with the real adapter in the final production path and demonstrate representative reads. |
| REQ-005 — contextualize | `MISSING` | scenario/conclusion evaluation schema only | Agent must generate grounded contextual response from actual request + API evidence. |
| REQ-006 / AG-003 / AG-005 — investigate, tool selection, planning/stopping | `MISSING` | Harness executes externally supplied proposals; trajectory/evidence evaluators observe them | Implement controller policy that chooses tools/evidence/stopping from observations; prove on real scenarios. |
| REQ-007 / REQ-011 / REQ-014 / REQ-015 — execute justified actions | `NEEDS_HARDENING` | deterministic validation, policy, evidence gate, action ToolSpecs, accepted-event semantics, ActionEvaluator | Agent must make correct action decisions/arguments; add idempotency/duplicate protection and production confirmation-policy decision where applicable. |
| REQ-008 / REQ-010 — clarification / additional information | `MISSING` | `Decision.ASK_CLARIFICATION` and `ABSTAIN` exist in schema | No controller currently emits justified clarification/abstention based on evidence insufficiency. |
| REQ-012 / AG-012 — escalation | `NEEDS_HARDENING` | escalation ToolSpec, `ESCALATE_HUMAN`, handoff evaluator | Agent must detect when escalation is required, execute/handoff correctly and construct useful evidence/uncertainty/reason content. |
| REQ-013 / AG-006 — complete/partial/inconclusive/conflict/unavailable | `NEEDS_HARDENING` | `ResponseMode` schema + research controlled evidence | No selected agent runtime/fallback loop has demonstrated all five modes end to end. |
| AG-004 — arguments | `NEEDS_HARDENING` | strict schema validation + required-argument completeness | Current integrated ArgumentEvaluator is predominantly structural/schema validation; semantic argument correctness and target/context consistency require final coverage. |
| AG-007 — evidence grounding | `NEEDS_HARDENING` | required evidence-source coverage + C4 research scoring | Final integrated evaluator must check evidence correctness/provenance/unsupported conclusions, not only source IDs. |
| AG-009 — decision policy | `MISSING` | decision enum + deterministic DecisionEvaluator | No controller currently makes the decision autonomously from the request/evidence state. |
| REQ-016 / AG-010 — inspectable trace | `REUSABLE_FOUNDATION` | proposal/call/result/observation/final trace + normalization | Promote to final runtime and attach evaluator result/run manifest/production telemetry. |
| AG-011 — customer-safe response | `NEEDS_HARDENING` | `CommunicationOracle.forbidden_internal_disclosures` exists; conclusion evaluator checks facts/claims/uncertainty | No dedicated evaluator currently enforces the communication oracle's internal-disclosure/source-citation policy, and no agent response generator is selected. |
| AG-013 — fail safely when model/provider/tool path fails | `MISSING` | Harness surfaces deterministic tool/transport outcomes; no model/runtime fallback | Implement explicit provider/model/tool failure handling that preserves support via safe response or human handoff. |

## 7. EV-001..EV-012 evaluation-framework inventory

| EV | Capability | Status | Current implementation | Exact gap before final acceptance |
|---|---|---|---|---|
| EV-001 | Function/tool choice | `NEEDS_HARDENING` | `TrajectoryEvaluator` required/forbidden method/path coverage | Add allowed/necessity/efficiency semantics as appropriate and run over actual agent proposals, not scripted paths. |
| EV-002 | Argument accuracy | `NEEDS_HARDENING` | `ArgumentEvaluator` + deterministic schema validation | Add semantic argument/target/context correctness beyond structural validity. |
| EV-003 | Execution trajectory | `NEEDS_HARDENING` | `TrajectoryEvaluator`; TraceSchema | Current evaluator uses required/forbidden call sets; `ordering_constraints` and efficiency are not currently enforced as final metrics. |
| EV-004 | Evidence use | `NEEDS_HARDENING` | `EvidenceEvaluator` checks required evidence source coverage | Add evidence correctness/provenance/recall, unsupported inference and uncertainty/conflict behavior to final integrated path. |
| EV-005 | Response quality | `REUSABLE_FOUNDATION` | structured `ConclusionEvaluator` on required facts, forbidden claims and uncertainty | Populate validated scenario truth and evaluate actual agent outputs; do not use exact-string primary scoring. |
| EV-006 | Safety | `NEEDS_HARDENING` | runner-owned binding; policy/action gates; `PolicyEvaluator`; `SafetyEvaluator` | Integrate deterministic safety metrics with actual runtime faults/actions and prove no private/gold leakage. |
| EV-007 | Failure performance | `MISSING` | no dedicated current integrated failure-performance evaluator found | Add deterministic tool/data/provider/model fault injection plus task/fallback outcome metrics. |
| EV-008 | Stability | `MISSING` | no current integrated stability evaluator or current `research/e2/tests` stability test exists | Run repeated controlled executions and report decision/tool/action/conclusion stability with explicit denominators. |
| EV-009 | High-impact actions | `NEEDS_HARDENING` | `ActionEvaluator`, argument/policy/evidence guards | Add exact target/semantic-argument/justification/accepted-event/no-unnecessary-action integration; current ActionEvaluator alone does not close the full row. |
| EV-010 | Escalation | `REUSABLE_FOUNDATION` | `EscalationHandoffEvaluator` | Populate reliable handoff requirements and evaluate actual runtime escalation path. |
| EV-011 | Customer-safe communication | `MISSING` | schema contains `forbidden_internal_disclosures`; no dedicated evaluator uses it | Implement deterministic checks where possible plus validated semantic/human assessment only where needed. |
| EV-012 | Evaluation integrity | `NEEDS_HARDENING` | scenario provenance/hashing + project-level benchmark-integrity/frozen-evaluator work | Wire evaluator-only inputs into final integrated evaluator with explicit custody; expose scorer/config provenance; calibrate any semantic judge before use; prevent tuning leakage. |

## 8. P1 production/quality inventory

| Area | Status | Current foundation | Remaining final-delivery work |
|---|---|---|---|
| Stable contracts | `REUSABLE_FOUNDATION` | normalized 18-operation ToolSpec + conformance audit | Promote behind final agent-facing runtime boundary. |
| Authorization | `NEEDS_HARDENING` | deterministic identity/permission/resource/evidence boundaries | Add production lifecycle/audit integration and negative regression over actual agent path. |
| Consequential action idempotency | `MISSING` | duplicate action can be evaluated; supplied API uses accepted-event semantics | Define/implement duplicate-request/idempotency policy at controller/runtime boundary. |
| Requester confirmation policy | `BLOCKED_BY_DECISION` | benchmark explicitly does not require a universal confirmation turn | Decide interactive production policy separately without changing benchmark semantics. |
| Failure continuity | `MISSING` | none sufficient for model/provider failure | Safe fallback/human handoff path is a release blocker. |
| Escalation handoff | `NEEDS_HARDENING` | evaluator/schema foundation | Integrate with real agent/controller output and escalation action. |
| Customer communication | `NEEDS_HARDENING` | structured conclusion schema | Add response policy + EV-011 enforcement. |
| State/context lifecycle | `BLOCKED_BY_DECISION` | per-run scenario/binding models | Decide minimal state model; persistent memory remains P2 unless evidence requires it. |
| Versioned config/dependencies | `NEEDS_HARDENING` | E2 `pyproject.toml`, research hashes | Final root/production dependency and non-secret runtime configuration do not exist. |
| Secrets/privacy | `NEEDS_HARDENING` | strong governance/custody rules | Enforce in selected runtime/logging/deployment path. |
| Observability | `NEEDS_HARDENING` | normalized structured trace | Add production logs/metrics, evaluator attachment, latency/failure visibility and retention policy. |
| Provider/model quality | `BLOCKED_BY_DECISION` | historical provider/model experiments are evidence only | Select final quality/Pareto point only through authorized comparison and ADR. |
| Performance | `MISSING` | isolated research timings only | Measure final end-to-end latency, reliability, resource/cost over representative scenarios. |
| Clean reproducibility | `MISSING` | research replay/provenance primitives | Provide clean install/config/start/run/evaluate path from documented inputs. |
| Rollback/fallback | `MISSING` | no selected release topology | Define fallback/reversal path after architecture/runtime selection. |

## 9. Final-demo inventory

| Required demo scenario | Current status | Why |
|---|---|---|
| Contextualize | `MISSING` | no operational Agent Controller/final response path |
| Investigate | `MISSING` | real transport exists, but current probes follow scripted proposals |
| Execute | `NEEDS_HARDENING` | action boundary exists; no actual selected agent decides/executes end to end |
| Clarify / insufficient evidence | `MISSING` | schema only |
| Escalate | `NEEDS_HARDENING` | action/evaluator foundation exists; actual agent handoff path absent |
| Conflict/uncertainty | `MISSING` | research oracle semantics exist; final agent behavior not demonstrated |
| Failure/robustness | `MISSING` | no production model/provider/tool fallback path |
| Customer-safe response | `MISSING` | no selected response generator + EV-011 enforcement |
| Per-run evaluator without leakage | `NEEDS_HARDENING` | evaluator suite exists; not yet attached to same final production-path agent run with custody proof |
| Reliability view | `MISSING` | no current integrated repeated-run stability output for final agent |

No scripted fixture or E2 probe should be relabeled as one of these final demo rows.

## 10. What may proceed now without crossing the scientific gate

The following work is compatible with the current parallel P0/P1 allowance and does not require the missing `b1c877…` score artifact:

1. freeze the delivery-gap inventory (this document);
2. define explicit product/architecture decision questions and acceptance evidence for the Agent Controller/runtime boundary;
3. define a production vertical-slice contract/test plan using the proven ToolSpec/binding/trace/evaluator interfaces as requirements, without yet creating the final production boundary;
4. strengthen provider-free evaluator primitives that are unambiguously required regardless of runtime choice, especially EV-007, EV-008 and EV-011, if done as research/reference work and without changing frozen scientific evidence;
5. define clean reproducibility, config, observability and failure-continuity acceptance tests before implementation;
6. maintain PR #10 as blocked until the exact frozen score artifact is provisioned; never replace that artifact through rescoring.

## 11. What must wait for an explicit decision/gate

Do **not** yet:

- create a final production `src/` stack and call it the chosen architecture;
- select LangGraph/Pydantic AI/custom controller/OpenAI Agents SDK or another runtime as final by preference;
- select a final model/provider from historical convenience alone;
- introduce RAG/vector DB/reranking/multi-agent/persistent memory/MCP without a measured requirement/bottleneck;
- run semantic or blind evaluation;
- infer a survivor/PREFERRED candidate from the unfinished C4 reporting state.

## 12. Minimum next vertical slice after architecture authorization

The first production slice should be intentionally narrow and use the strongest already-proven boundaries:

```text
real request
  ↓
external identity/context binding
  ↓
Agent Controller baseline
  ↓
Canonical ToolSpec proposal
  ↓
strict argument validation
  ↓
resource/permission/evidence guard
  ↓
real TRACTIAN HTTP adapter
  ↓
observation
  ↺ controller until stop / clarify / escalate / act
  ↓
structured customer-safe final result
  ↓
normalized trace + run manifest
  ↓
integrated deterministic EvaluationSuite
```

First-slice acceptance should require at minimum:

- one contextualize/investigate case;
- one justified action case;
- one insufficient-evidence clarification/escalation case;
- one degraded/tool failure case;
- no gold/private reference in runtime imports/context;
- runner-owned identity/seed;
- real API calls through the normalized 18-operation contract;
- structured trace from request through final result;
- same-run deterministic evaluator output;
- safe failure rather than uncaught model/provider/tool breakage.

This is deliberately smaller than the final 10-scenario demo, but it exercises every architectural boundary that matters.

## 13. Recommended implementation order

### Immediate, provider-free

1. merge this inventory after review;
2. open a Class C architecture/product decision task for the **Agent Controller/runtime boundary**, with a simple single-agent explicit-controller baseline and credible alternatives;
3. preregister decision criteria: required behavior coverage, tool-schema integration, traceability, deterministic guard compatibility, failure/fallback controllability, testability, latency/resource footprint and implementation complexity;
4. separately harden runtime-independent evaluator gaps EV-007/EV-008/EV-011 as research/reference components if they do not depend on the architecture winner;
5. specify production config/observability/reproducibility acceptance before coding the final boundary.

### After architecture/runtime decision

6. create `src/`, `tests/`, `config/` production boundary;
7. implement the minimal real vertical slice above by promoting/reimplementing proven E2 interfaces, not by copying research code blindly;
8. integrate selected model/provider only through the chosen controller abstraction;
9. close fault-injection/fallback and idempotency gaps;
10. run the required real 10-scenario demo/regression portfolio;
11. measure reliability/latency/resource/cost and perform clean-environment reproduction;
12. finalize README/runbook/ADRs/rubric-to-evidence index.

### Scientific chain remains separate

When the original `b1c877…` artifact becomes available, resume PR #10 independently:

```text
provision exact evaluator-side rows
→ reporting runner
→ independent validator
→ reporting freeze
→ canonical scientific-state update
→ only then consider the explicitly authorized next scientific gate
```

Do not couple product-development progress to unauthorized reconstruction of that artifact.

## 14. Final audit conclusion

The project is **not blocked overall** by the missing reporting artifact. It is blocked only on that specific scientific gate. The final delivery still has substantial P0 work that can proceed safely in parallel.

The strongest existing asset is the E2 **execution/evaluation boundary**. The strongest missing asset is the **actual Agent Controller integrated with that boundary**. The correct next product-development move is therefore not to add optional architecture complexity; it is to make the runtime/controller decision explicit and then build the smallest real Agent → API → trace → Evaluator vertical slice that closes the uncovered P0 rows.
