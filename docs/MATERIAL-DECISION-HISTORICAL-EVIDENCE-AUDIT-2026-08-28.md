# Academy × TRACTIAN — Material-Decision Historical Evidence Audit

**Status:** COMPLETE / evidence-consolidation checkpoint  
**Date:** 2026-08-28  
**Audit baseline:** `main@60d1da6d3ef1153d142ea261111300333eff0061`  
**Governance:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md) and [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Machine-readable result:** [`../research/results/material-decision-historical-evidence-audit-2026-08-28.json`](../research/results/material-decision-historical-evidence-audit-2026-08-28.json)

## 1. Decision question

What material architecture/product/evaluation decisions are already adequately answered by repository evidence, which historical evidence only needs a targeted update, and which decisions still contain a concrete evidence gap?

This audit creates **no new experiment**. Its purpose is to prevent redundant experimentation by consolidating what the repository already proves before any new preregistration.

## 2. Method

The audit reused the repository's existing 2026-08-22 retrospective reclassification, `p12-historical-candidate-component-reinterpretation-2026-08-22.json`, as the baseline for E0→E14v rather than reinterpreting those experiments from scratch. It then reconciled evidence added after that checkpoint: P12/C4 work, ADR-001→017, production controller/action/evaluator evidence, EV-007/008/011, final-delivery reproduction, the 83-row final handoff audit, and the 2026-08-28 USD-0/evidence-first governance amendments.

Sources audited include `research/results/`, `research/frozen/`, `research/experiments/`, `scripts/research/`, tests, ADRs, progress/current-state documents, relevant Git/PR history, and the delivery-acceptance matrix.

The classifications are exactly those defined by the evidence-first gate:

- `EVIDENCE_SUFFICIENT`;
- `EVIDENCE_EXISTS_NEEDS_UPDATE`;
- `PARTIALLY_ASSESSED`;
- `UNASSESSED`;
- `INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE`.

`EVIDENCE_SUFFICIENT` always means **sufficient for the stated current decision scope**, not mathematical or global optimality.

## 3. Audit summary

| Classification | Decisions |
|---|---:|
| `EVIDENCE_SUFFICIENT` | 11 |
| `EVIDENCE_EXISTS_NEEDS_UPDATE` | 1 |
| `PARTIALLY_ASSESSED` | 6 |
| `UNASSESSED` | 1 |
| `INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE` | 1 |
| **Total material decision rows** | **20** |

**New experiments authorized by this audit: 0.**

A demonstrated evidence gap is not automatically an experiment authorization. The next action may be external-fact refresh, scope screening, exact artifact recovery, dependency ordering, or preregistration. An experiment is allowed only after the remaining gap is both material and the minimum controlled experiment is defined prospectively.

## 4. Consolidated material-decision matrix

| ID | Decision area | Existing evidence actually proves | Classification | Exact remaining gap / action |
|---|---|---|---|---|
| D01 | Production provider/model quality | Broad zero-cost discovery; real Groq operability; real negative task-quality evidence for historical Groq models; provider-serving compatibility/capacity history; provider-neutral production boundary exists | `PARTIALLY_ASSESSED` | Current fair quality/reliability/latency comparison across the **currently eligible USD-0 provider/model set** is not present. Refresh only current external eligibility/capability facts first; do not run a provider experiment yet. |
| D02 | Provider serving capacity / quota feasibility | Groq C2/C3 rate-limit failures are preserved; ADR-001 compared Groq/Cerebras/local/dedicated serving paths and quantified quota/capacity risks; later OpenRouter/NVIDIA/C4 serving work adds operational evidence | `EVIDENCE_EXISTS_NEEDS_UPDATE` | Capacity facts are provider/account/time dependent. Recheck only current first-party limits for candidates that survive D01 screening. Do not repeat historical capacity failures. |
| D03 | GPT-OSS/Groq reasoning-budget/structured-output tuning family | E14g→E14l established operational feasibility and then hard task-quality failure; E14l explicitly closes the reasoning-budget/response-format tuning family for that historical candidate | `EVIDENCE_SUFFICIENT` | Do not rerun that tuning family. A different future selected provider/model may require its own configuration qualification, but that is not a reason to revive E14g→l. |
| D04 | Agent topology: single vs multi-agent | Current explicit single-agent controller has strong deterministic P0, failure, stability, action and communication evidence. Historical E6/E7 explicitly left `multi_agent_freeze=false`; no repository artifact located a controlled single-vs-multi quality comparison | `PARTIALLY_ASSESSED` | Incremental benefit/cost of planner→executor or critic/reviewer over the qualified single-agent baseline is not established. Do not experiment until a controlled provider/model basis exists and topology remains material after screening. |
| D05 | Runtime/orchestration | E6 compared LangGraph, Pydantic AI/Graph and OpenAI Agents SDK; LangGraph was implemented, replay/checkpoint/HITL tested and integrated live. ADR-004 later implemented and heavily regressed a smaller explicit controller while retaining LangGraph as qualified upgrade path | `PARTIALLY_ASSESSED` | Evidence is asymmetric: LangGraph and explicit controller have repository implementation evidence, while retained comparators do not have implementation-symmetric depth. A new runtime comparison is justified only if runtime choice remains material after provider/topology consolidation or an ADR-004 reversal trigger is observed. |
| D06 | Tool protocol/topology: native ToolSpec vs MCP | E7 directly showed 18/18 coverage, schema/invocation/guard/trace equivalence; native has lower envelope complexity, MCP higher portability; delivery has no core-MCP requirement | `EVIDENCE_SUFFICIENT` | Keep native typed tools internally and MCP-compatible adapter as conditional interoperability path. Reopen only on a concrete partner/deployment/evaluator interoperability requirement. |
| D07 | Evidence-sufficiency stopping | E5 directly compared free tool loop vs evidence-sufficiency policy: task success 7→10/11, premature stops 4→1, unnecessary calls 9→2, evidence coverage .786→.964; later runtime/tests preserve the policy | `EVIDENCE_SUFFICIENT` | No new stopping experiment now. Reopen only if task distribution/policy materially changes or regression shows a stopping failure. |
| D08 | Adaptive evidence planning beyond stopping | Adaptive planning from missing-evidence requirements appears as a preserved constant in later E7/E8 work, but this audit found no equally controlled ablation against a simple fixed evidence plan | `PARTIALLY_ASSESSED` | The incremental value of the adaptive planner itself is not isolated. Do not test it until it becomes a material remaining architecture dimension after provider/topology/runtime ordering. |
| D09 | Retrieval/RAG/vector DB/reranking | The required domain evidence is already exposed through the supplied typed API/tools and current integrated path covers all unblocked acceptance rows. Delivery explicitly classifies RAG/vector/reranking as P2 conditional complexity | `EVIDENCE_SUFFICIENT` | Current decision is **do not add retrieval infrastructure without a measured retrieval/evidence gap**. No such gap is evidenced. Reopen only on measured evidence recall/correctness failure that direct tools cannot address. |
| D10 | Persistent memory/state | Current request-local/explicit state supports the accepted scenarios. Delivery acceptance explicitly says persistent memory only if cases/evidence justify it; no current P0/P1 gap requires cross-session memory | `EVIDENCE_SUFFICIENT` | Keep explicit request state. Reopen only if a real required scenario demonstrates cross-turn/cross-process state loss that changes task quality or workflow continuity. |
| D11 | Adaptive model routing | No adequate controlled routing comparison exists | `UNASSESSED` | Not currently material because no production provider/model set is selected/characterized. Do not create a routing experiment before D01 closes enough to establish multiple viable candidates and a real routing trade-off. |
| D12 | Safety / authorization / consequential actions | ADR-005/012 plus ADR-004 controller boundaries, negative tests and controlled supplied/test actions establish deterministic authorization, exact confirmation/fingerprint binding, durable idempotency, replay containment and default read-only production behavior | `EVIDENCE_SUFFICIENT` | Sufficient for the bounded supplied/test delivery scope. Real-customer mutation remains a separate non-claim, not a reason to redo the safety architecture. |
| D13 | Failure continuity / provider-free reliability | EV-007: 11/11 safety expectations across 11 failure families; EV-008: 30/30 runs, 66/66 stability checks; EV-011: 60/60 objective communication predicates; integrated demo preserves clarify/abstain/escalate/fail-safe paths | `EVIDENCE_SUFFICIENT` | Do not rerun provider-free reliability campaigns. Live-provider reliability remains part of D01 and should reuse the frozen metric definitions if/when a provider comparison is authorized. |
| D14 | Operational deterministic evaluator stack | ProductionEvaluator/ControlledActionEvaluator plus trace, failure, stability, action and communication campaigns are integrated and repeatedly reproduced; final 83-row audit has zero unblocked evaluator-delivery gaps outside C4 | `EVIDENCE_SUFFICIENT` | Preserve/regress existing deterministic evaluators. Do not add LLM judging where deterministic truth exists. |
| D15 | Scientific evaluator / semantic judge / EV-012 integrity | Historical E9 v4.1/v4.2 and Qwen judge work are qualified only within their exact exposed/synthetic scopes; C4 deterministic scoring/bootstrap/LOGO are frozen, but required per-group/slice continuation is blocked on exact rows | `PARTIALLY_ASSESSED` | Do not start a new judge experiment. First resolve the C4 exact-artifact path. Semantic/private/blind work remains gated separately. |
| D16 | Observability / trace surface | Canonical RunTrace separates proposal/call/result/observation/terminal; E6/E7 and ADR-004→017 repeatedly validate trace completeness, provenance, leakage controls and evaluator consumption | `EVIDENCE_SUFFICIENT` | Richer OTel/backend telemetry is not required for current delivery. Reopen only if a concrete diagnostic/operations requirement is not representable by the normalized trace. |
| D17 | Deployment topology | Clean-checkout reproduction, versioned config, runbook/fallback/reversal and local supplied-API execution satisfy the current delivered-project scope; ADR-017 explicitly does **not** claim an exercised infrastructure rollback | `EVIDENCE_SUFFICIENT` | Hosted deployment is not a formal requirement by itself. Do not create a deployment experiment unless the delivered scope changes or deployment becomes necessary for the final demo/handoff. |
| D18 | UI/integration richness | Final acceptance requires a real integrated path and reviewer-visible evidence, not a rich UI; ADR-016/017 demonstrate the integrated path and close all unblocked handoff rows. Rich UI is P2 conditional | `EVIDENCE_SUFFICIENT` | No UI experiment now. Reopen only if reviewer/demo task completion is measurably limited by the current interface. |
| D19 | C4 per-group/slice scientific reporting | 144/144 deterministic scoring frozen; bootstrap 20k PASS; LOGO 7/7 PASS; independent recomputations pass; sanitized artifacts preserve aggregate/group sensitivity evidence | `PARTIALLY_ASSESSED` | Exact 144-row evaluator-side artifact (`b1c877…`, 177350 bytes) is still missing, so modality/failure-family reporting cannot be honestly completed. Continue exact-byte recovery only; no reconstruction/rescoring is authorized. |
| D20 | ADR-008 OpenAI Sol × Gemini live comparison packet | The historical design/executor/custody evidence remains valid as protocol engineering, and no live call was consumed | `INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE` | The candidate set violates the current USD-0 hard constraint because the OpenAI Sol API path is not eligible. Preserve ADR-008→011 historically; do not execute #44 as frozen. Any future live packet must be prospective and based on D01's current feasible set. |

## 5. What the audit changes

The main change is **not more experimentation**. It is a narrower, evidence-backed work queue.

### No new experiment needed now

The repository already has enough evidence for the current inclusion/architecture decision on:

- native ToolSpec + conditional MCP adapter;
- evidence-sufficiency stopping;
- direct tool/API evidence instead of speculative RAG;
- request-local explicit state instead of speculative persistent memory;
- deterministic safety/authorization boundaries;
- provider-free failure continuity/stability;
- deterministic operational evaluator stack;
- normalized RunTrace observability;
- reproducible local delivery rather than mandatory hosted deployment;
- current real-path interface rather than richer UI;
- closure of the historical Groq/GPT-OSS reasoning-budget tuning family.

Creating new experiments for those decisions without a new reversal trigger would violate the evidence-first rule.

### Concrete gaps exist, but experiments are not yet authorized

- **Provider/model quality:** first refresh current USD-0 candidate facts and map them against already-consumed evidence.
- **Agent topology:** a single-vs-multi comparison gap exists, but a fair controlled provider/model basis must exist first.
- **Runtime/orchestration:** current evidence is asymmetric; revisit only after higher-priority dimensions or an ADR-004 reversal trigger make the gap material.
- **Adaptive evidence planning:** component effect is not isolated, but it is downstream of more material unresolved choices.
- **Scientific evaluator/C4:** exact artifact recovery comes before any new evaluator work.

### Not currently material

Adaptive model routing is unassessed but **not experiment-ready**. It becomes material only if multiple viable provider/model candidates survive characterization and context-sensitive routing has a concrete expected advantage.

## 6. Provider-specific historical evidence that must not be discarded

The provider decision is not a blank slate:

- E8 identified zero-cost Groq, Gemini, OpenRouter, Hugging Face, Ollama and no-model candidates while blocking paid OpenAI/Anthropic paths under the original free constraint.
- E8 executed Groq `llama-3.1-8b-instant` successfully as an operational/schema/trace path at USD 0, but later quality evidence superseded that model as a production candidate.
- E14g→l exercised Groq `openai/gpt-oss-120b`; operational completeness could be restored, but task quality/decision/action/escalation gates failed. Those negative results are evidence and must not be silently rerun away.
- P12-C2/C3 preserved Groq capacity failures; ADR-001 quantified the quota/capacity problem and explored alternative same-model serving paths.
- ADR-002/003 and C4 provider probes preserve additional OpenRouter/NVIDIA serving compatibility evidence. These are serving/compatibility facts, not a production quality ranking.

Therefore the future provider step is a **delta comparison problem**, not provider research from zero.

## 7. C4 boundary

The audit does not change the scientific gate.

```text
required exact artifact SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
required bytes                      177350
required rows                       144
required geometry                   36 parents × 4 arms
current gate                        REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

Exact-byte recovery remains the only currently authorized C4 action. Existing bootstrap/LOGO evidence may support aggregate interpretation, but it cannot manufacture the missing modality/failure-family rows.

## 8. Immediate order after this audit

```text
1. freeze/merge this evidence audit
2. update canonical decision inventory from audit findings
3. provider/model: refresh current first-party USD-0 eligibility/capability facts only
4. reconcile those facts with existing E8/E14/P12/ADR provider evidence
5. only then decide whether a minimal prospective provider comparison is still required
6. topology: retain single-agent as qualified baseline; do not implement multi-agent until a controlled basis/protocol is ready
7. continue exact C4 artifact recovery in parallel
8. leave runtime/adaptive-planning gaps queued behind higher-priority unresolved dimensions
9. do not create RAG/memory/routing/deployment/UI experiments absent a new material trigger
```

## 9. Non-claims

This audit does not claim:

- final provider/model selection;
- final single-vs-multi topology selection;
- globally optimal runtime/orchestration;
- C4 completion;
- fresh-blind/legacy locked-test authorization;
- real-customer mutation evidence;
- unconditional production readiness;
- global final architecture freeze.

It claims only that the repository's historical evidence has been consolidated sufficiently to distinguish reusable evidence, changed assumptions, partial gaps and genuinely unassessed decisions **before** creating any new experiment.
