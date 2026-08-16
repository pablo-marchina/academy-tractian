# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT RECORDED; E10b NEXT  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 15:48 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan after the real TRACTIAN package was audited and after the first real free-provider and private scorer cycles. The plan separates frozen evidence/contracts from experimental architecture decisions, explicitly forbids demo-first development, preserves the USD 0 provider constraint, and treats private task-quality score as the acceptance signal instead of proxy/schema success.

## 1. Current state

### Frozen / complete

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` and gold/evaluator boundary frozen.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E2 framework-neutral ToolSpec/Trace/Replay/Evaluator harness complete.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- E5 evidence acquisition/stopping comparison executed.
- E6 LangGraph + ToolSpec + HarnessRunner + HttpxTransport live path passed.
- E7 topology ADR recorded: native ToolSpec calls internally, MCP-compatible adapter externally.
- E8 Groq `llama-3.1-8b-instant` passed DEV + VALIDATION as a real zero-cost remote model candidate under proxy/schema gates.
- E8 optional comparators registered: OpenRouter free / `:free`, Gemini key-visible models, Hugging Face free credits, Ollama fallback.
- E9 evaluator-side private scorer implemented and run locally with fixed Groq outputs plus private DEV/VALIDATION expected paths.
- E9 private task-quality result recorded as sanitized aggregate only.
- E10 DEV-only quality-improvement loop implemented, dry-run CI passed, and first real DEV-only scorer result recorded.

### Current candidate bundle

- Boundary: B3 guarded boundary.
- Evidence/stopping: evidence-sufficiency policy.
- Evidence planning: adaptive from missing evidence requirements.
- Runtime: LangGraph current candidate.
- Execution boundary: HarnessRunner.
- Transport: HttpxTransport live API path.
- Internal tool surface: native ToolSpec calls.
- External interoperability surface: MCP-compatible adapter.
- Leading free-provider candidate: Groq `llama-3.1-8b-instant`.
- Paid providers: OpenAI/Anthropic disabled under the USD 0 project constraint.

### Still not frozen

- final model/provider choice;
- MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent memory;
- observability backend;
- UI/demo flow;
- final architecture.

## 2. E8 Groq proxy/schema result

| Metric | DEV | VALIDATION | Aggregate |
|---|---:|---:|---:|
| Provider | Groq | Groq | Groq |
| Model | `llama-3.1-8b-instant` | `llama-3.1-8b-instant` | `llama-3.1-8b-instant` |
| Total calls | 6 | 6 | 12 |
| Successful calls | 6 | 6 | 12 |
| Task-success proxy | 1.0 | 1.0 | 1.0 |
| Schema-valid rate | 1.0 | 1.0 | 1.0 |
| No LOCKED_TEST claim rate | 1.0 | 1.0 | 1.0 |
| Trace completeness | true | true | true |
| Avg latency ms | 8974.732 | 9766.9 | 9370.816 |
| P95 latency ms | 30724.136 | 50841.424 | 50841.424 |
| Cost USD | 0.0 | 0.0 | 0.0 |

Interpretation: E8 proved that a real free remote model path is available and can satisfy schema/proxy constraints, but E8 did not prove real task quality.

## 3. E9 private task-quality result

E9 converted the benchmark from proxy/schema-only to evaluator-side private scoring. It consumed fixed Groq outputs after generation, mapped them to private DEV/VALIDATION expected paths inside the local scorer, and committed only sanitized aggregate results.

| Metric | E9 full DEV+VALIDATION |
|---|---:|
| Fixed calls consumed | 12 |
| Parsed model outputs available | 12 |
| Private oracles loaded | 5 |
| Calls with matching private oracle | 12 |
| Scoreable calls | 12 |
| Real task quality | 0.631 |
| Decision correctness | 0.6667 |
| Evidence correctness | 0.0 |
| Action correctness | 0.25 |
| Escalation correctness | 0.5 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| Proxy success rate | 1.0 |
| Proxy-vs-real disagreement rate | 1.0 |
| LOCKED_TEST accessed | false |

Interpretation: E8 proxy success was over-optimistic. The current main gaps are evidence grounding and action/escalation calibration, not leakage or unsafe benchmark access.

## 4. E10 DEV-only improvement result

E10 was intentionally restricted to DEV groups only:

- `asset_G501`;
- `asset_C710`;
- `asset_S420`.

VALIDATION was not used for tuning, VALIDATION did not run, and LOCKED_TEST remained blocked. The E10 policy change forced evidence-first behavior: concrete API/resource-level evidence before decisions, action only with visible endpoint support, escalation only with safety/severity/uncertainty/permission/specialist rationale, and incomplete evidence should become `investigate_only` or `insufficient_evidence`.

| Metric | E9 DEV-only baseline | E10 DEV-only | Delta |
|---|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | +0.1428 |
| Decision correctness | 0.3333 | 0.3333 | 0.0 |
| Evidence correctness | 0.0 | 1.0 | +1.0 |
| Action correctness | 0.0 | 0.0 | 0.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 0.0 |

Decision: E10 is a partial improvement, not a promotable candidate. Evidence grounding improved strongly, but action and escalation calibration did not improve. Do not run full DEV+VALIDATION for this candidate yet.

## 5. Immediate next gate — E10b DEV-only action/escalation calibration

E10b must keep the E10 evidence-first gains while adding an explicit DEV-only action/escalation decision rubric.

### E10b goals

- Preserve evidence correctness materially above the E9 DEV baseline.
- Improve action correctness above 0.0 on DEV-only private scoring.
- Improve escalation correctness above 0.0 on DEV-only private scoring.
- Improve decision correctness if possible without overfitting.
- Keep premature action rate at 0.0.
- Keep unsupported final-claim rate at 0.0.
- Keep LOCKED_TEST inaccessible.
- Keep private expected paths scorer-only.

### E10b design direction

- Separate `needs_more_evidence`, `safe_to_act`, and `needs_human_escalation` as explicit internal decision checks before filling final JSON.
- Require a concrete action endpoint only when the visible packet supports that endpoint and there is no blocking missing evidence.
- Require escalation when visible evidence indicates safety/severity/specialist-needed uncertainty, but avoid claiming escalation for generic uncertainty alone.
- Keep `should_take_action_now=false` when evidence is still incomplete, unless the visible packet clearly supports an action endpoint.
- Add post-output self-checks for action/escalation consistency, without using private oracle text.

### E10b acceptance target before full remeasurement

Do not promote E10b to full DEV+VALIDATION unless a DEV-only private scorer run shows all of the following:

- evidence correctness remains materially above the E9 DEV baseline;
- action correctness improves above 0.0;
- escalation correctness improves above 0.0;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible;
- no raw private oracles or fixed parsed outputs are committed.

## 6. Optional comparator policy

OpenRouter is registered as the next optional free comparator through the free-only policy. It only permits `openrouter/free` or specific models ending in `:free` and blocks non-free model ids plus `openrouter/auto` / `openrouter/auto:free`.

Gemini remains optional only after a key-visible `generateContent` model is listed. Hugging Face remains low priority because free-credit exhaustion must not become a paid run. Ollama remains fallback only.

Optional comparators do not block E10b.

## 7. Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- Optional provider comparators are useful but must not delay scorer-driven DEV improvements.
- No final architecture freeze yet.

## 8. Current action checklist

- [x] E8 real free remote model path established with Groq.
- [x] E9 private scorer implemented and run against fixed Groq outputs.
- [x] E10 DEV-only evidence-first iteration run and scored.
- [x] E10 result recorded as partial improvement only.
- [ ] Build E10b DEV-only action/escalation calibration runner.
- [ ] Run E10b real DEV-only Groq capture locally.
- [ ] Score E10b with E9 v3 private scorer.
- [ ] Compare E10b against E9 DEV baseline and E10 DEV result.
- [ ] Promote to full DEV+VALIDATION only if E10b meets acceptance target.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
