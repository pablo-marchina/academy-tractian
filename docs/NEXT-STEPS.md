# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 09:17 BRT  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Mandatory decision-revalidation plan:** [`DECISION-REVALIDATION-MASTER-PLAN.md`](DECISION-REVALIDATION-MASTER-PLAN.md)

This file is the short-horizon execution plan. It does not itself authorize a scientific gate, live provider call, real customer mutation or provider selection.

## 1. Immediate rule — plan before implementation

From this checkpoint forward, **do not start material implementation before the applicable decision is documented and preregistered**.

Required order:

```text
update plan / decision inventory
→ define decision question + requirement/risk
→ freeze hard constraints
→ research credible materially different alternatives
→ preregister comparison / metrics / hard gates / repetitions / robustness
→ only then implement or execute the experiment
```

This applies to provider/model, topology, runtime, retrieval, memory, routing, tools/protocols, evaluators, observability, deployment, UI and any other material decision.

Historical freezes remain immutable evidence; they do not exempt a decision from revalidation if a hard assumption changed or a credible alternative was omitted.

## 2. Permanent production/service hard constraint — USD 0

```text
external API / hosted-service project charge    USD 0
paid subscription required                      NO
purchased credits                               NO
unbounded billable spillover                    FORBIDDEN
```

Within that feasible set, select the strongest evidence-backed quality/production Pareto configuration rather than the first free option.

## 3. Current active workstream — global decision revalidation

The previous instruction to perform “submission/review hygiene only” is superseded by this prospective planning checkpoint because the project principles require proof of best-supported choices, not only acceptance coverage.

Immediate sequence:

1. freeze this governance/planning update before new development;
2. complete the material-decision inventory and current primary-source research;
3. prospectively amend the provider/model comparison around the USD 0 feasible set;
4. preregister controlled topology/runtime experiments before implementation;
5. continue exact C4 artifact recovery in parallel without changing scientific semantics;
6. only after each comparison is preregistered, execute the corresponding implementation/experiment;
7. select by hard gates + quantitative evidence + robustness + production fit + Pareto reasoning;
8. integrate the best-supported configuration and rerun full regression before any final architecture freeze.

## 4. Provider/model comparison — old live packet suspended

Current historical packet:

```text
ADR-008 historical design                   PRESERVED
old candidates                              OpenAI GPT-5.6 Sol / Gemini 3.7 Flash
old max calls                               32
calls consumed                               0
production provider selected                 NO
```

The old packet must **not execute** because OpenAI GPT-5.6 Sol is outside the project's USD 0 production feasible set.

Issue #44 must remain suspended pending a prospective amendment. Do not spend any of the old 32-call budget.

### Connection state

User-reported only; do not probe secrets/accounts:

```text
Groq API     connected
Gemini API   pending user connection
```

A connected credential does not authorize provider calls by itself.

### Candidate discovery before amendment

At minimum screen current zero-cost candidates from:

- Gemini free-tier models;
- Groq free-tier models;
- OpenRouter explicitly free routes/models if identity and cost containment are adequate;
- Cloudflare Workers AI free-tier models if contract fit is adequate;
- feasible local/open-weight baseline;
- any other materially distinct zero-cost candidate found by primary-source research.

Prospective exclusions must be documented before live results are observed.

## 5. Agent-topology decision — revalidate before final selection

Current single-agent explicit controller remains the simple `QUALIFIED_BASELINE`, not the proven final topology.

Preregister a controlled comparison with at least:

```text
A  current single-agent / explicit-controller baseline
B  planner → executor
C  agent → critic/reviewer
```

Hold provider/model, task distribution, ToolSpecs, HarnessRunner, authorization/safety and evaluator definitions constant where possible.

Measure quality, tool/argument correctness, evidence quality, action/escalation/clarification/abstention correctness, safety, stability, latency, quota/token use, coordination failures, unnecessary handoffs, loop amplification, trace clarity, debugging and operational complexity.

Do not implement B/C until their exact comparison protocol is preregistered.

## 6. Runtime/orchestration and other decisions

After provider and topology comparisons are preregistered/executed, review the remaining decision register in this order unless new evidence changes priority:

1. orchestration/runtime;
2. adaptive stopping/planning;
3. model routing;
4. retrieval/evidence routing;
5. memory/state;
6. evaluator/judge scope;
7. observability;
8. deployment;
9. UI/integration.

Tool topology/native tools vs MCP already has comparatively strong historical evidence; retain it provisionally unless current research finds a material new requirement or alternative.

RAG/vector DB/reranking/persistent memory/multi-agent/richer UI are neither automatically required nor automatically deferred. They must be screened under the same rule: implement only when a credible expected benefit maps to a requirement/risk and the comparison can be measured.

## 7. C4 scientific critical path — exact recovery first

Current scientific gate remains `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

Exact missing evaluator-side deterministic score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Authorized now:

- search local/historical/temporary/artifact storage for the exact bytes;
- verify SHA-256, byte count and geometry if found.

Not authorized by this plan:

- reconstruction;
- rescoring;
- substitution;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- downstream survivor/preferred inference.

If exact bytes cannot be recovered, first create a separate prospective scientific amendment defining whether a byte-identical reproduction attempt is admissible. Any produced file must match the exact frozen SHA-256 and byte count or be rejected.

## 8. Development authorization checklist

Before starting each material implementation, confirm:

- [ ] requirement/risk mapping exists;
- [ ] decision question is explicit;
- [ ] hard constraints are frozen;
- [ ] credible alternatives and simple baseline are documented;
- [ ] exclusions are documented prospectively;
- [ ] metrics/hard gates are preregistered;
- [ ] task population and controls are pinned;
- [ ] repetitions/uncertainty plan exists where needed;
- [ ] robustness/failure tests are defined;
- [ ] production-fit measurements are defined;
- [ ] stopping and decision semantics are defined;
- [ ] regression obligations and reversal triggers are defined;
- [ ] provider/service path is guaranteed USD 0 where applicable.

If any applicable box is missing, remain in planning/research.

## 9. Deadline sequence

```text
NOW        merge/freeze governance + revalidation planning update
NEXT       systematic current research + complete decision inventory
NEXT       preregister zero-cost provider amendment
NEXT       preregister topology comparison
PARALLEL   search exact C4 score-row bytes
THEN       execute provider comparison only under amended frozen protocol
THEN       execute topology/runtime comparisons one dimension at a time
THEN       select best-supported zero-cost Pareto configuration
THEN       integrate + full regression + reliability/security validation
FINAL      evidence-honest architecture freeze and submission before 2026-09-08
```

## 10. Preserved provider-free handoff evidence

ADR-017 remains valid within its original scope:

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
```

These facts prove reviewer-ready provider-free acceptance evidence, not global architecture optimality. The new revalidation program builds prospectively on this baseline without rewriting it.

## 11. Still forbidden

- executing the old ADR-008/#44 live provider packet as-is;
- using a paid provider/service in the production feasible set;
- credential/account probing merely to verify connection state;
- hidden provider retries/fallbacks/warm-ups or uncontrolled provider-side state in controlled comparisons;
- reconstructing/rescoring/substituting C4 without a separate prospective scientific amendment;
- semantic/FRESH_BLIND/LEGACY_LOCKED_TEST access without explicit authorization;
- provider-native TRACTIAN tool execution that bypasses the governed tool boundary;
- weakening deterministic safety/authorization/idempotency boundaries;
- treating a historical gate PASS or freeze as proof of global optimality;
- claiming global architecture freeze or production readiness before revalidation closes.
