# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 — post historical-evidence audit  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Historical evidence audit:** [`MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`](MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)

This file is the short-horizon execution plan. It authorizes no scientific gate, provider call, credential probe, real-customer mutation or new experiment by itself.

## 1. Immediate rule

The historical evidence audit is complete. Therefore the next step is **not** broad new experimentation.

```text
existing evidence audit          DONE
material decision matrix         DONE
new experiments authorized       0
```

For every future decision:

```text
decision question
→ existing repository evidence
→ sufficiency/gap classification
→ current external fact refresh only where needed
→ minimum preregistration only if a material gap still requires an experiment
→ implementation / experiment only after that
```

## 2. NOW — reconcile provider/model facts against existing evidence

Provider/model quality is `PARTIALLY_ASSESSED`, not unresearched.

Reuse before any new call:

- E8 zero-cost candidate discovery;
- real E8 Groq operational evidence;
- E14g→E14l Groq GPT-OSS operational + negative task-quality evidence;
- P12-C2/C3 capacity failures;
- ADR-001 serving-capacity analysis;
- ADR-002/003 and C4 provider-serving probes;
- ADR-006→011 provider-neutral production comparison infrastructure.

The only immediate provider work is **current first-party fact refresh** for potentially eligible USD-0 candidates:

- current free-tier/route eligibility and billable-spillover behavior;
- current model identities relevant to the task;
- structured-output/tool-use contract compatibility;
- current quotas/capacity only for candidates that survive eligibility screening;
- operational constraints that materially affect this project.

Do not make inference calls during this refresh. Do not probe credentials/accounts merely to verify user-reported connection state.

After the fact refresh, reconcile each candidate as:

```text
covered by historical evidence
needs only factual update
has a precise missing quality/production measurement
not currently eligible/material
```

Only then decide whether a new provider comparison is needed and what the minimum prospective packet would be.

## 3. Agent topology — gap recorded, implementation not yet authorized

Current state:

```text
single-agent explicit controller     strong QUALIFIED baseline
controlled single-vs-multi result    absent
multi-agent incremental benefit      unresolved
topology implementation now          NOT AUTHORIZED
```

The missing comparison is real, but topology must be isolated from provider/model effects. Do not implement planner→executor or agent→critic/reviewer until:

1. the provider/model basis is controlled enough for a fair architecture comparison;
2. the topology alternative remains materially credible for the assignment after screening;
3. the exact task population, metrics, hard gates, repetitions, cost/quota and complexity measures are prospectively preregistered.

## 4. Runtime/orchestration — preserve existing evidence, do not restart research

Current classification: `PARTIALLY_ASSESSED`.

Already known:

- E6 scorecard considered LangGraph, Pydantic AI/Graph and OpenAI Agents SDK;
- LangGraph was implemented and validated for trace, deterministic replay, checkpoint/pause-resume and supplied-API integration;
- ADR-004 later implemented a smaller explicit controller and froze it for the P0 controller scope;
- LangGraph remains the first qualified upgrade path under ADR-004 reversal triggers.

Do not create a fresh runtime survey or experiment now. Revisit only if provider/topology resolution or an ADR-004 reversal trigger makes the asymmetry material.

## 5. Decisions explicitly closed to new experiments in the current scope

No new experiment is authorized for these unless a documented reversal trigger appears:

- historical Groq/GPT-OSS reasoning-budget/response-format tuning family;
- native ToolSpec vs MCP adapter;
- evidence-sufficiency stopping;
- RAG/vector DB/reranking;
- persistent memory;
- deterministic safety/authorization/action custody;
- provider-free failure/stability/communication campaigns;
- operational deterministic evaluator stack;
- normalized RunTrace observability;
- hosted deployment topology;
- richer UI.

The reason is not that these technologies are universally bad or globally solved. The repository already has sufficient evidence for the **current inclusion decision** or no material current requirement/gap that would justify a new experiment.

## 6. Adaptive model routing — unassessed but not current work

Adaptive routing is `UNASSESSED`, but it is not experiment-ready.

It becomes material only if the provider work leaves multiple viable, characterized provider/model candidates and there is a concrete context-sensitive reason to route among them. Until then, creating a routing experiment would test a hypothetical problem.

## 7. C4 — exact recovery in parallel

Scientific gate remains:

`REQUIRED_PER_GROUP_AND_SLICE_REPORTING`

Required missing artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

Authorized now:

- search local/historical/temporary/workflow storage for the exact bytes;
- verify hash, byte count, row count and geometry if a candidate is found.

Not authorized:

- reconstruction;
- rescoring;
- substitution;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- downstream survivor/preferred inference.

## 8. Ordered work queue

```text
NOW       merge/freeze material-decision historical evidence audit
NEXT      current first-party USD-0 provider/model fact refresh only
NEXT      reconcile current facts with existing E8/E14/P12/ADR evidence
DECIDE    whether a minimal provider comparison is still necessary
IF YES    preregister that minimum provider comparison before any calls
PARALLEL  exact C4 artifact recovery
LATER     topology preregistration only after controlled provider/model basis
LATER     runtime/adaptive-planning only if still material
FINAL     integrate best-supported configuration + full regression + evidence-honest architecture freeze
```

## 9. Development authorization checklist

Before a new experiment or material candidate implementation:

- [ ] exact decision question exists;
- [ ] repository-wide evidence audit for that question is recorded;
- [ ] existing evidence classification is explicit;
- [ ] a material remaining gap is demonstrated;
- [ ] current external assumptions were refreshed only where necessary;
- [ ] existing negative/failed evidence is preserved and incorporated;
- [ ] no existing artifact adequately answers the gap;
- [ ] the proposed experiment is the minimum controlled work needed;
- [ ] hard constraints, especially USD 0 and safety/evaluation boundaries, are preserved;
- [ ] task population, metrics, hard gates, repetitions and robustness are preregistered;
- [ ] regression and reversal obligations are defined.

If any applicable box is false, do not create the experiment.

## 10. Still forbidden

- executing ADR-008/#44 as currently frozen;
- treating a connected API key as evaluation evidence or call authorization;
- paid provider/service production usage;
- credential/account probing merely to confirm connection state;
- redundant reruns of historical negative/failed experiments;
- multi-agent implementation before topology preregistration and controlled basis;
- RAG/memory/routing/deployment/UI experiments without a new material trigger;
- reconstructing/rescoring/substituting C4 without a separately authorized scientific amendment;
- weakening `HarnessRunner`/authorization/idempotency/private-truth boundaries;
- claiming provider selection, C4 completion, global architecture freeze or unconditional production readiness before the evidence supports them.
