# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT RECORDED; E10b DEV-ONLY STRONG IMPROVEMENT WITH ESCALATION GAP; E10c NEXT  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 16:24 BRT  
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
- E10b DEV-only action/escalation calibration manifest, capture runner, documentation and dry-run CI added.
- E10b real DEV-only Groq capture and private scorer run completed and sanitized aggregate recorded.

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

## 5. E10b DEV-only action/escalation result

E10b kept the E10 evidence-first gains and added explicit action/escalation calibration. It ran DEV-only real Groq capture and private scoring.

| Metric | E9 DEV baseline | E10 DEV | E10b DEV | Delta E10b vs E10 |
|---|---:|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | 0.8571 | +0.2381 |
| Decision correctness | 0.3333 | 0.3333 | 1.0 | +0.6667 |
| Evidence correctness | 0.0 | 1.0 | 1.0 | 0.0 |
| Action correctness | 0.0 | 0.0 | 1.0 | +1.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 1.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 0.0 |

Decision: E10b is a strong DEV-only improvement, but it still fails the preregistered acceptance target because escalation correctness remains 0.0. Do not run full DEV+VALIDATION yet.

## 6. Immediate next gate — E10c DEV-only escalation calibration

E10c must preserve E10b's evidence, decision and action improvements while targeting escalation specifically.

### E10c goals

- Preserve evidence correctness at 1.0 or materially above the E9 DEV baseline.
- Preserve decision correctness and action correctness gains from E10b as much as possible.
- Improve escalation correctness above 0.0 on DEV-only private scoring.
- Keep premature action rate at 0.0.
- Keep unsupported final-claim rate at 0.0.
- Keep LOCKED_TEST inaccessible.
- Keep private expected paths scorer-only.
- Keep VALIDATION unused for tuning.

### E10c design direction

- Add a narrower escalation-specific rubric instead of further strengthening action.
- Distinguish `request-specialist` versus `case escalation` versus direct action.
- Make escalation positive only when the visible packet supports risk, severity, specialist uncertainty, missing permission, or material impact.
- Avoid escalation for generic uncertainty alone.
- Avoid regressing action correctness by preserving the E10b endpoint-selection rules.

### E10c acceptance target before full remeasurement

Do not promote E10c to full DEV+VALIDATION unless a DEV-only private scorer run shows all of the following:

- evidence correctness remains materially above the E9 DEV baseline;
- action correctness remains above 0.0;
- escalation correctness improves above 0.0;
- real task quality does not regress materially from E10b;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible;
- no raw private oracles or fixed parsed outputs are committed.

## 7. Optional comparator policy

OpenRouter is registered as the next optional free comparator through the free-only policy. It only permits `openrouter/free` or specific models ending in `:free` and blocks non-free model ids plus `openrouter/auto` / `openrouter/auto:free`.

Gemini remains optional only after a key-visible `generateContent` model is listed. Hugging Face remains low priority because free-credit exhaustion must not become a paid run. Ollama remains fallback only.

Optional comparators do not block E10c.

## 8. Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- Optional provider comparators are useful but must not delay scorer-driven DEV improvements.
- No final architecture freeze yet.

## 9. Current action checklist

- [x] E8 real free remote model path established with Groq.
- [x] E9 private scorer implemented and run against fixed Groq outputs.
- [x] E10 DEV-only evidence-first iteration run and scored.
- [x] E10 result recorded as partial improvement only.
- [x] Build E10b DEV-only action/escalation calibration runner.
- [x] Add E10b dry-run CI guard.
- [x] Run E10b real DEV-only Groq capture locally.
- [x] Score E10b with E9 v3 private scorer.
- [x] Compare E10b against E9 DEV baseline and E10 DEV result.
- [x] Record E10b as strong DEV-only improvement with remaining escalation gap.
- [ ] Build E10c DEV-only escalation calibration runner.
- [ ] Run E10c real DEV-only Groq capture locally.
- [ ] Score E10c with E9 v3 private scorer.
- [ ] Compare E10c against E10b and acceptance target.
- [ ] Promote to full DEV+VALIDATION only if E10c meets acceptance target.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
