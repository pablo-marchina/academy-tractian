# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 — material-decision historical evidence audit  
**Audit baseline:** `main@60d1da6d3ef1153d142ea261111300333eff0061`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)  
**Historical evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)  
**Machine audit:** [`../research/results/material-decision-historical-evidence-audit-2026-08-28.json`](../research/results/material-decision-historical-evidence-audit-2026-08-28.json)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts/ADRs remain authoritative for their original scopes; prospective governance does not rewrite them.

## Executive state

```text
Project North Star                           strongest defensible TRACTIAN/Inteli delivery under P1-P4
permanent external service/API cost          USD 0 HARD CONSTRAINT
evidence audit before new experiment         REQUIRED
material-decision historical audit           COMPLETE
material decision rows                       20
EVIDENCE_SUFFICIENT                          11
EVIDENCE_EXISTS_NEEDS_UPDATE                  1
PARTIALLY_ASSESSED                            6
UNASSESSED                                    1
INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE        1
new experiments authorized by audit           0

provider/model final selection               NO
old ADR-008 OpenAI/Gemini packet             INVALID FOR CURRENT USD-0 EXECUTION SCOPE
old packet calls consumed                     0 / 32
credential/account probes                     0
Groq API connection                          USER-REPORTED CONNECTED / NOT PROBED
Gemini API connection                        PENDING USER CONNECTION / NOT PROBED

single-agent controller                      STRONG QUALIFIED BASELINE
single-vs-multi final topology               NOT SELECTED
runtime/orchestration final choice           NOT SELECTED
native ToolSpec + conditional MCP adapter    EVIDENCE SUFFICIENT FOR CURRENT SCOPE
evidence-sufficiency stopping                EVIDENCE SUFFICIENT FOR CURRENT SCOPE
RAG/vector/reranking                         NO MATERIAL CURRENT GAP / NO EXPERIMENT
persistent memory                            NO MATERIAL CURRENT GAP / NO EXPERIMENT
adaptive model routing                       UNASSESSED / NOT CURRENTLY MATERIAL

provider-free safety/reliability             EVIDENCE SUFFICIENT WITH BOUNDED NON-CLAIMS
operational deterministic evaluator          EVIDENCE SUFFICIENT
scientific evaluator / EV-012                PARTIALLY ASSESSED / C4 BLOCKED
observability via RunTrace                   EVIDENCE SUFFICIENT FOR CURRENT SCOPE
hosted deployment                            NOT REQUIRED BY CURRENT DELIVERY SCOPE
richer UI                                    NOT REQUIRED BY CURRENT DELIVERY SCOPE

global final architecture                    UNFROZEN
production-readiness claim                   NOT AUTHORIZED
real customer mutations performed            0
```

## 1. Evidence-audit result controls all next work

The repository is **not** starting architecture research from zero. The audit reused the complete 2026-08-22 E0→E14v reinterpretation and reconciled the evidence added afterward: P12/C4, ADR-001→017, EV-007/008/011, final-delivery reproduction, the 83-row handoff audit and the new USD-0/evidence-first governance.

Permanent prospective sequence:

```text
decision question
→ repository historical evidence audit
→ sufficiency classification
→ exact material gap, if any
→ current external fact refresh only where assumptions can change
→ preregistration only if a minimum experiment is still necessary
→ implementation / experiment
→ evaluation / regression / decision
```

A demonstrated gap is not automatic experiment authorization. Dependency ordering, current-fact refresh, scope screening or artifact recovery may come first.

## 2. Decisions with sufficient evidence — do not create redundant experiments

No new experiment is authorized now for:

- historical Groq/GPT-OSS reasoning-budget/structured-output tuning family — negative E14 evidence closes that family;
- native typed ToolSpec vs MCP-compatible adapter — E7 already provides direct comparison;
- evidence-sufficiency stopping — E5 directly beats the free-loop baseline on the recorded DEV+VALIDATION scope;
- RAG/vector DB/reranking — current direct typed API/tool evidence has no measured retrieval gap and the delivery classifies these as P2 conditional;
- persistent memory — current required scenarios are covered by explicit request state; persistent memory is conditional on an actual case need;
- deterministic safety/authorization/consequential-action boundaries;
- provider-free failure continuity/stability/customer-safe communication;
- operational deterministic evaluator stack;
- normalized RunTrace observability;
- hosted deployment — not a formal requirement for the current delivered scope;
- richer UI — not a formal requirement and no current reviewer/demo task-completion gap is evidenced.

Reopen any of these only on a documented reversal trigger or new measured requirement/gap.

## 3. Provider/model state — delta problem, not blank-slate research

The historical evidence that must be reused includes:

- E8 zero-cost candidate discovery: no-model, Groq, Gemini, OpenRouter, Hugging Face and Ollama; paid OpenAI/Anthropic blocked under the original free constraint;
- real E8 Groq `llama-3.1-8b-instant` operational/schema/trace evidence at USD 0;
- later evidence superseding that model for task quality;
- E14g→E14l Groq `openai/gpt-oss-120b` operational and negative task-quality evidence;
- P12-C2/C3 Groq capacity failures;
- ADR-001 capacity/serving-path comparison;
- OpenRouter/NVIDIA/C4 serving compatibility evidence;
- ADR-006→011 provider-neutral client/executor/custody engineering.

Current classification:

```text
production provider/model quality       PARTIALLY_ASSESSED
provider serving capacity               EVIDENCE_EXISTS_NEEDS_UPDATE
old ADR-008 live packet                 INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE
```

The next provider action is **current first-party USD-0 eligibility/capability refresh only** and reconciliation against this existing evidence. Do not call a provider merely to repeat historical evidence. Any future live comparison requires a new prospective candidate set/protocol after that refresh.

## 4. Agent topology and runtime

### Agent topology

ADR-004 + EV-007/008/011 + ADR-016 prove a strong single-agent baseline. Historical records explicitly left multi-agent unfrozen, and this audit found no controlled single-vs-multi quality comparison.

```text
single-agent baseline                  QUALIFIED / STRONG EVIDENCE
multi-agent incremental benefit        NOT ESTABLISHED
topology experiment now                NOT AUTHORIZED YET
```

The exact gap is real, but a topology experiment must wait until there is a controlled provider/model basis and the topology remains material after screening. Do not implement planner→executor or critic/reviewer merely because the gap exists.

### Runtime/orchestration

E6 strongly qualifies LangGraph and ADR-004 strongly qualifies the explicit controller, but evidence depth is asymmetric across retained runtime alternatives. Runtime therefore remains `PARTIALLY_ASSESSED`, not blank-slate.

Reopen a runtime experiment only after higher-priority unresolved dimensions or a documented ADR-004 reversal trigger makes the remaining asymmetry material.

## 5. Scientific C4 path — unchanged

Current gate:

`REQUIRED_PER_GROUP_AND_SLICE_REPORTING`

Exact missing evaluator-side score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Preserved evidence:

- deterministic scoring: 144/144, frozen;
- bootstrap 20k: PASS, independent recomputation PASS;
- LOGO sensitivity: 7/7, independent recomputation PASS.

Authorized now: **exact-byte recovery only**. Reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain unauthorized.

## 6. Preserved provider-free delivery evidence

```text
ADR-004 controller regression              12 / 12 PASS
EV-007 safety expectations                 11 / 11
EV-008 runs / stability checks             30 / 30; 66 / 66
EV-011 communication predicates            60 / 60
ADR-016 integrated demo                     5 / 5
ADR-017 acceptance rows                    83
PASS_EVIDENCED                             41
PASS_BOUNDED                               40
EXTERNALLY_BLOCKED                          1   C4 / EV-012
UNEXECUTED_GATED                            1   historical live provider row
GAP_ACTION_REQUIRED                         0
clean-checkout production tests           251 PASS at ADR-017 freeze
```

These facts remain historical evidence within their frozen scopes. They do not establish live-provider quality, C4 completion, global architecture optimality, real-customer mutation, hosted-deployment rollback or unconditional production readiness.

## 7. Immediate authorized work

1. merge/freeze the historical evidence audit and this reconciliation;
2. refresh current first-party facts only for the zero-cost provider/model candidates potentially relevant to D01/D02;
3. reconcile those facts with existing E8/E14/P12/ADR evidence before deciding whether any new provider experiment is necessary;
4. continue exact C4 artifact recovery in parallel;
5. keep the single-agent controller as the topology baseline, but do not implement multi-agent until provider/control prerequisites and a prospective topology protocol exist;
6. leave runtime/adaptive-planning gaps queued behind higher-priority unresolved dimensions;
7. do not create RAG/memory/routing/deployment/UI experiments absent a new material trigger.

## 8. Still forbidden

- creating an experiment before the repository evidence audit for that exact decision is complete;
- executing the old ADR-008/#44 packet as-is;
- paid provider/service production usage;
- credential/account probing merely to verify connection state;
- hidden provider retries/fallbacks/warm-ups or uncontrolled provider state in controlled comparisons;
- reconstructing/rescoring/substituting C4 without a separately approved prospective scientific amendment;
- semantic/FRESH_BLIND/LEGACY_LOCKED_TEST access without explicit authorization;
- bypassing `HarnessRunner.execute_tool()` or weakening deterministic safety/authorization/idempotency boundaries;
- treating historical evidence sufficiency as global mathematical optimality;
- claiming global architecture freeze or production readiness before the unresolved material decisions close.
