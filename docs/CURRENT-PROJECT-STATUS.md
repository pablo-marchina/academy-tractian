# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 — post zero-cost provider/model fact refresh  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)  
**Historical evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)  
**Provider fact refresh:** [`PROVIDER-ZERO-COST-FACT-REFRESH-2026-08-28.md`](PROVIDER-ZERO-COST-FACT-REFRESH-2026-08-28.md)  
**Provider refresh addendum:** [`DECISION-REVALIDATION-ADDENDUM-003-ZERO-COST-PROVIDER-FACT-REFRESH.md`](DECISION-REVALIDATION-ADDENDUM-003-ZERO-COST-PROVIDER-FACT-REFRESH.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts and ADRs remain authoritative for their exact historical scopes.

## Executive state

```text
Project North Star                           strongest defensible TRACTIAN/Inteli delivery under P1-P4
permanent external service/API cost          USD 0 HARD CONSTRAINT
evidence audit before new experiment         REQUIRED
material-decision historical audit           COMPLETE
provider/model current fact refresh          COMPLETE
provider/model inference calls in refresh    0
credential/account probes in refresh         0
new benchmark authorized by refresh          NO

material decision rows                       20
EVIDENCE_SUFFICIENT                          11
EVIDENCE_EXISTS_NEEDS_UPDATE                  1
PARTIALLY_ASSESSED                            6
UNASSESSED                                    1
INVALIDATED_EVIDENCE_FOR_CURRENT_SCOPE        1

provider/model final selection               NO
provider/model quality                       PARTIALLY_ASSESSED
broad USD-0 provider discovery               CLOSED FOR CURRENT SCOPE
primary hosted feasible set                  GEMINI 3.7 FLASH / CLOUDFLARE FREE / GROQ HISTORICAL CONTROL
conditional baselines                        OLLAMA LOCAL / PINNED OPENROUTER :FREE
old ADR-008 OpenAI/Gemini packet             INVALID FOR CURRENT USD-0 EXECUTION SCOPE
old packet calls consumed                     0 / 32

single-agent controller                      STRONG QUALIFIED BASELINE
single-vs-multi final topology               NOT SELECTED
runtime/orchestration final choice           NOT SELECTED
native ToolSpec + conditional MCP adapter    EVIDENCE SUFFICIENT FOR CURRENT SCOPE
evidence-sufficiency stopping                EVIDENCE SUFFICIENT FOR CURRENT SCOPE
RAG/vector/reranking                         NO MATERIAL CURRENT GAP / NO EXPERIMENT
persistent memory                            NO MATERIAL CURRENT GAP / NO EXPERIMENT
adaptive model routing                       UNASSESSED / NOT CURRENTLY MATERIAL

C4 scientific gate                          REQUIRED_PER_GROUP_AND_SLICE_REPORTING
C4 exact-row artifact                        EXTERNALLY BLOCKED / EXACT-BYTE RECOVERY ONLY
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

## 1. Evidence-first state

The repository is not restarting architecture or provider research from zero.

Permanent sequence:

```text
decision question
→ repository historical evidence audit
→ sufficiency classification
→ current external fact refresh only for changing assumptions
→ reconcile current facts with preserved positive/negative evidence
→ demonstrate exact remaining material gap
→ preregister minimum experiment only if still necessary
→ implementation / execution
→ evaluation / regression / decision
```

A gap does not authorize an experiment automatically.

## 2. Provider/model fact refresh — complete

Current first-party documentation was refreshed without inference calls or credential/account probes for Gemini, Groq, Cloudflare Workers AI, OpenRouter, Ollama, Hugging Face Inference Providers, Cerebras and NVIDIA hosted NIM.

The historical provider decision remains a **delta problem**, not blank-slate research. Binding historical evidence still includes:

- E8 zero-cost candidate discovery and Groq operational/schema/trace evidence;
- E14g→E14l GPT-OSS operational + negative task-quality evidence;
- P12-C2/C3 Groq capacity failures;
- ADR-001 capacity/serving-path comparison;
- ADR-002/003 and later serving probes;
- ADR-006→011 provider-neutral client/executor/custody engineering.

### Current primary hosted feasible set

#### Gemini 3.7 Flash — conditional

`gemini-3.7-flash` is current GA/stable, Free Tier input/output is free, and the model exposes the contract-relevant function-calling/structured-output capabilities. ADR-008 already used this same model ID historically.

The unresolved gate is **data use**: current Free Tier pricing documentation says Free Tier content is used to improve Google products. No Gemini provider call is authorized until the exact intended payload is judged acceptable under that policy.

#### Cloudflare Workers AI Free — eligible

Workers AI currently provides 10,000 neurons/day on Workers Free with a plan-upgrade boundary rather than silent paid spillover. Current screened agentic models include pinned GLM 4.7 Flash, Gemma 4 26B A4B and Nemotron 3 120B A12B routes.

Do **not** automatically benchmark all three. The next planning step must choose only the minimum materially distinct representative(s) needed to test a real quality/capacity gap.

#### Groq Free — historical/control route

Current Groq Free remains contract-feasible for selected production models, but the repository already contains material negative GPT-OSS task-quality and capacity evidence. Groq must therefore be treated as historical/control evidence, not a fresh frontier candidate whose failures can be reset.

Groq Qwen 3.8 is currently Preview and is excluded from final production claims.

### Conditional baselines

- Ollama local only if a no-inference hardware/model feasibility check identifies a realistic model;
- a **fixed** OpenRouter `:free` route only if model/provider identity and no-fallback behavior can be pinned; generic `openrouter/free` is excluded from controlled comparison.

### Screened out of the primary final hosted production set

- NVIDIA hosted free NIM — development/testing positioning;
- Cerebras Free Trial — bounded trial, already historically explored;
- Hugging Face routed free credit — allowance too small for default production selection absent an ultra-low-volume proof;
- Groq Qwen 3.8 Preview — not a clean production lifecycle.

## 3. Exact remaining provider decision gap

D01 stays `PARTIALLY_ASSESSED`, but broad provider discovery is complete enough for the current scope.

Before any inference call:

1. resolve Gemini Free Tier data-use/privacy eligibility for the exact payload;
2. select the minimum pinned Cloudflare representative set by materially different capability/capacity point;
3. decide whether Groq is historical-only or one live control under the current DecisionSource contract;
4. decide whether Ollama is hardware/model feasible using facts only;
5. then determine whether a **minimal prospective live provider comparison** still closes a material gap.

No provider benchmark is currently authorized.

## 4. Decisions with sufficient current evidence

Do not create redundant experiments for:

- historical Groq/GPT-OSS reasoning-budget/structured-output tuning family;
- native typed ToolSpec vs MCP-compatible adapter;
- evidence-sufficiency stopping;
- RAG/vector DB/reranking;
- persistent memory;
- deterministic safety/authorization/consequential-action boundaries;
- provider-free failure continuity/stability/customer-safe communication;
- operational deterministic evaluator stack;
- normalized RunTrace observability;
- hosted deployment;
- richer UI.

Reopen only on a documented reversal trigger or new measured requirement/gap.

## 5. Agent topology and runtime

### Agent topology

ADR-004 + EV-007/008/011 + ADR-016 establish the explicit single-agent controller as a strong qualified baseline. The incremental benefit/cost of planner→executor or critic/reviewer remains unmeasured.

```text
single-agent baseline                  QUALIFIED / STRONG EVIDENCE
multi-agent incremental benefit        NOT ESTABLISHED
topology experiment now                NOT AUTHORIZED
```

Topology work remains downstream of the provider/control basis and requires its own prospective protocol if still material.

### Runtime/orchestration

E6 strongly qualifies LangGraph and ADR-004 strongly qualifies the explicit controller. Evidence remains asymmetric across runtime alternatives. Do not restart runtime research unless provider/topology resolution or an ADR-004 reversal trigger makes the remaining runtime choice material.

## 6. Scientific C4 path — unchanged

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

- deterministic scoring: 144/144 frozen;
- bootstrap 20k: PASS, independent recomputation PASS;
- LOGO sensitivity: 7/7, independent recomputation PASS.

Authorized now: **exact-byte recovery only**. Reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain unauthorized.

## 7. Preserved provider-free delivery evidence

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
UNEXECUTED_GATED                            1   historical live-provider row
GAP_ACTION_REQUIRED                         0
clean-checkout production tests           251 PASS at ADR-017 freeze
```

These prove only their frozen scopes; they do not establish live-provider quality, C4 completion, global architecture optimality, real-customer mutation, hosted-deployment rollback or unconditional production readiness.

## 8. Immediate authorized work

1. freeze/reconcile this provider fact refresh;
2. resolve the Gemini payload data-use gate **without inference**;
3. choose the minimum Cloudflare candidate set by factual capability/capacity differences;
4. decide Groq's historical-control role and optional Ollama factual feasibility;
5. only then decide whether a minimum prospective provider comparison is necessary;
6. continue exact C4 artifact recovery in parallel;
7. keep multi-agent/runtime/adaptive work queued behind the provider basis unless a reversal trigger changes priority.

## 9. Still forbidden

- creating an experiment before the evidence audit and current-fact reconciliation for that exact decision;
- executing the old ADR-008/#44 packet as-is;
- paid provider/service production usage;
- credential/account probing merely to verify connection state;
- provider inference before a separately frozen prospective packet;
- hidden provider retries/fallbacks/warm-ups or uncontrolled provider state in controlled comparisons;
- reconstructing/rescoring/substituting C4 without a separately approved scientific amendment;
- semantic/FRESH_BLIND/LEGACY_LOCKED_TEST access without explicit authorization;
- bypassing `HarnessRunner.execute_tool()` or weakening deterministic safety/authorization/idempotency boundaries;
- treating a historical PASS/freeze as proof of global optimality;
- claiming global architecture freeze or production readiness before unresolved material decisions close.
