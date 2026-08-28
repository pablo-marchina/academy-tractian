# Academy × TRACTIAN — Decision Revalidation Master Plan

**Status:** ACTIVE / mandatory pre-implementation planning gate  
**Checkpoint:** 2026-08-28 09:17 BRT  
**Applies from:** this checkpoint forward  
**Canonical governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Short-horizon execution:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)

## 1. Purpose

This plan makes the repository-wide P1–P4 rules operational for **all development from this checkpoint forward**.

No material implementation change may start merely because a component is already implemented, historically frozen, popular, convenient or sufficient to pass an acceptance gate. Historical artifacts remain immutable evidence, but final project choices must be revalidated prospectively against the current project objective, hard constraints and all credible materially different alternatives within the defined search scope.

The required order is:

```text
requirement / decision question
→ hard constraints
→ systematic research
→ credible alternative set + simple/null baseline
→ preregistered comparison
→ controlled implementation / experiment
→ quantitative evaluation
→ repeated-run / uncertainty analysis
→ robustness / failure analysis
→ production-fit analysis
→ Pareto / trade-off analysis
→ decision record + reversal triggers
→ regression confirmation
→ PREFERRED / FROZEN only when justified
```

If this sequence has not been completed for a material decision, the correct state is `UNASSESSED`, `RESEARCHED` or `QUALIFIED`; not final.

## 2. Permanent hard constraints

### 2.1 Monetary project cost

The project must remain **monetarily free**.

```text
external API / hosted-service project charge    USD 0
paid subscription required                      NO
purchased API credits                           NO
unbounded paid spillover                        FORBIDDEN
```

A provider/model/tool is production-eligible only if its intended project usage can be executed at USD 0 through a documented free tier, free route or local execution without requiring paid spillover.

Free credits count as eligible only when paid spillover can be deterministically prevented for the project run. A candidate that can silently become billable is not eligible until a fail-closed zero-cost boundary exists.

This hard constraint narrows the feasible frontier; it does not permit choosing the first free option. Within the zero-cost feasible set, compare the strongest credible quality frontier and materially different alternatives.

### 2.2 Safety and evaluation integrity

The following remain hard constraints and cannot be traded away for quality:

- no evaluator-private/gold leakage into agent/model context;
- no semantic/FRESH_BLIND/LEGACY_LOCKED_TEST access without explicit gate authorization;
- `HarnessRunner.execute_tool()` remains the exclusive tool-execution boundary unless a prospectively validated replacement preserves or improves the same guarantees;
- deterministic action authorization/idempotency/safety boundaries cannot be weakened by model/provider/topology changes;
- hidden provider retries, fallbacks, warm-ups or uncontrolled provider-side state are forbidden in controlled comparisons unless preregistered;
- real customer mutation remains separately authorized and is not implied by test/supplied action capability.

## 3. Mandatory pre-implementation gate

Before any new material code change, issue or experiment begins, record at minimum:

1. decision question;
2. mapped TAPI/delivered-package/rubric requirement or material risk;
3. hard constraints;
4. current baseline;
5. credible materially different alternatives;
6. why each alternative is included or excluded;
7. metrics and hard gates;
8. task/case population and controls;
9. repetitions/uncertainty plan where stochasticity matters;
10. robustness/failure tests;
11. production-fit measurements;
12. stopping rule and decision semantics;
13. regression obligations;
14. reversal triggers.

No implementation is authorized by this document alone. The applicable experiment/issue must be preregistered before changing the candidate under evaluation.

## 4. Existing evidence semantics

Historical freezes remain immutable and continue to prove exactly what they proved at the time. They are not erased or rewritten.

From this checkpoint forward, distinguish:

- **historically frozen evidence** — exact prior result/protocol remains immutable;
- **current final-choice status** — must be interpreted under this revalidation plan;
- **prospective supersession** — a later better-supported decision may supersede an older choice without rewriting old evidence.

A prior ADR marked `FROZEN` does not by itself prove global optimality if its original search scope omitted a currently credible material alternative or a hard assumption has changed.

## 5. Immediate decision inventory

| Decision area | Historical/current baseline | Revalidation state now | Required next action |
|---|---|---|---|
| Provider/model | ADR-008 OpenAI Sol vs Gemini Flash design; no live calls | `INVALIDATED_ASSUMPTION` for execution because project cost hard constraint is USD 0 and OpenAI Sol is not a free API candidate | prospectively amend provider comparison before any live call |
| Groq provider | historical E8 zero-cost live evidence; user reports API already connected | `QUALIFIED_CANDIDATE` / credential presence not probed | include in free-provider candidate discovery/comparison |
| Gemini provider | free-tier candidate; user will connect API | `PENDING_USER_CONNECTION` / credential presence not probed | include prospectively after user connection; no credential/account probe |
| OpenRouter free routes | historically registered candidate | `RESEARCH_REQUIRED` | re-check current free-route capability, determinism and zero-cost containment before inclusion |
| Cloudflare Workers AI | not yet compared in current production decision | `UNASSESSED` | research current free-tier/model/tool/JSON capabilities before inclusion/exclusion |
| Local/open-weight execution | optional historical baseline | `RESEARCH_REQUIRED` | include at least one feasible local/simple baseline if hardware/runtime constraints allow |
| Agent topology | single-agent explicit controller | `QUALIFIED_BASELINE`, not proven final | compare against at least planner→executor and agent→critic/reviewer if materially feasible |
| Orchestration/runtime | explicit controller + existing LangGraph research history | `NEEDS_REVALIDATION` for final choice | compare materially distinct runtime patterns under same task/provider controls |
| Tool topology | native typed tools preferred in E7; MCP equivalent but more complex | `EVIDENCE_STRONG / CONFIRM_SCOPE` | retain unless new requirements/credible alternatives materially change the trade-off |
| Retrieval/evidence routing | direct API/tool evidence baseline | `SCREEN_REQUIRED` | test RAG/vector/reranking only if a measured evidence gap or credible expected benefit exists |
| Memory/state | request-local/explicit state | `SCREEN_REQUIRED` | compare persistent memory only if actual scenarios require measurable cross-turn benefit |
| Adaptive stopping/planning | evidence-sufficiency/adaptive research history | `NEEDS_REVALIDATION` | compare adaptive vs static/simple policy quantitatively |
| Model routing | static provider selection baseline | `UNASSESSED` | evaluate adaptive routing only after provider candidates are independently characterized |
| Safety/authorization | deterministic ADR-005/012 boundaries | `PRESERVE_HARD_BOUNDARY` | only prospective changes that preserve/improve safety with evidence |
| Evaluator/judge stack | deterministic-first with semantic gates restricted | `NEEDS_SCOPE_REVALIDATION` | deterministic where possible; semantic/human only where necessary and validated |
| Observability | normalized `RunTrace` | `SCREEN_REQUIRED` | richer telemetry only if diagnostic/rubric/production benefit is measurable |
| Deployment | local/reproducible path | `UNASSESSED_FOR_FINAL` | compare free deployment options only if deployment is required for final delivery |
| UI/integration | minimal real-path interface | `SCREEN_REQUIRED` | richer UI only if it improves task completion/demo/rubric value enough to justify complexity |
| C4 reporting | blocked on exact 144-row artifact | `RECOVERY_REQUIRED` | search exact bytes first; only a separately approved prospective byte-identical recovery amendment may be considered if exact artifact is unavailable |

## 6. Provider/model revalidation rule

The previous live provider packet must **not execute as currently frozen**.

Until a prospective amendment is frozen:

```text
ADR-008 historical evidence                 PRESERVED
issue #44 live execution                     SUSPENDED_PENDING_AMENDMENT
provider live calls under old packet         0 / 32
credential/account probing                   0
production provider selected                 NO
```

The amended comparison must first perform current primary-source candidate discovery across the credible zero-cost set. At minimum screen:

- Gemini free-tier models suitable for the required structured decision/tool contract;
- Groq free-tier models suitable for the same contract;
- OpenRouter explicitly free routes/models if zero-cost and model identity can be bounded strongly enough;
- Cloudflare Workers AI free-tier candidates if contract fit is adequate;
- at least one feasible local/open-weight baseline when project hardware allows;
- other materially distinct zero-cost providers discovered by the systematic search.

Exclude a candidate prospectively only with a documented reason such as: not actually USD 0, no required structured/tool contract, unacceptable availability/quota, uncontrolled billable spillover, materially dominated capability, or operational incompatibility with hard safety/trace requirements.

The comparison must keep task distribution and controller/tool/evaluator boundaries controlled so provider effects are not confounded with topology/runtime changes.

## 7. Agent-topology revalidation

Use the current single-agent explicit controller as the simple baseline. Compare at least the following materially different patterns when feasible:

```text
A  single agent / explicit controller baseline
B  planner → executor
C  agent → critic/reviewer
```

Keep constant where possible:

- model/provider;
- task/case population;
- ToolSpecs and HarnessRunner;
- authorization/safety policy;
- evaluator definitions;
- repetition geometry;
- prompt information access.

Measure at minimum task/decision quality, tool and argument correctness, evidence quality, action/escalation/clarification/abstention correctness, safety, stability, latency, token/quota use, coordination failures, unnecessary handoffs, loop amplification, implementation/operational complexity, trace clarity and debugging burden.

A multi-agent design is adopted only if its measurable benefit survives overhead and robustness analysis; a single-agent design remains final only if it remains on the best-supported zero-cost quality/production Pareto frontier.

## 8. Controlled experiment order

Avoid changing multiple major dimensions simultaneously.

Recommended order:

```text
0. governance + decision inventory
1. zero-cost provider/model candidate discovery and preregistration
2. provider/model comparison with architecture held constant
3. agent-topology comparison using one controlled provider/model basis
4. orchestration/runtime comparison with topology held constant
5. adaptive stopping/planning/routing comparisons
6. retrieval/memory only when screening finds credible benefit
7. observability/deployment/UI production-fit comparisons where applicable
8. integrated Pareto selection
9. full regression + final architecture freeze
```

Interactions may be evaluated later with a factorial design when evidence suggests a material interaction; do not confound the initial main-effect comparisons.

## 9. C4 recovery track

C4 remains scientifically separate from provider/product revalidation.

First priority is exact recovery of the original evaluator-side score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Search historical/local/temporary/artifact storage for exact bytes before any scientific amendment.

If the exact artifact cannot be recovered, do **not** silently reconstruct or rescore. A separate prospective recovery decision must explicitly define whether a byte-identical reproduction attempt is scientifically admissible. Any reproduced file must match the exact frozen SHA-256 and byte count or be rejected; a mismatch does not substitute for the original evidence.

Until such an amendment exists, issue #9 remains blocked and no downstream scientific gate is inferred.

## 10. Credential and connection state

User-supplied connection state at this checkpoint:

```text
Groq API     user reports connected
Gemini API   user intends to connect
```

Repository policy:

- do not read, list or probe secrets merely to verify this statement;
- do not make provider calls until the amended comparison explicitly authorizes them;
- connection/credential availability is an operational prerequisite, not evaluation evidence;
- never store raw secrets in repository artifacts, traces or documentation.

## 11. Documentation-before-development rule

For every future material development cycle:

```text
update decision inventory / plan
→ create or update preregistered issue/experiment
→ review hard constraints and alternatives
→ only then implement
```

If implementation begins before the decision question, alternatives, comparison protocol and hard constraints are documented, stop and return to planning.

## 12. Exit condition for revalidation program

Global architecture may be called final only when:

- every applicable material decision has been reviewed under this plan;
- no credible material alternative remains unassessed inside the declared search scope;
- zero-cost feasibility is proven for the selected production path;
- controlled comparisons and robustness evidence support the selected Pareto configuration;
- safety/evaluation integrity boundaries remain intact;
- applicable P0/P1 delivery rows remain covered;
- full regression succeeds after the selected configuration is integrated;
- final ADRs state both evidence and reversal triggers.

Until then:

```text
provider/model final selection    NO
single-vs-multi topology final     NO
final architecture                 UNFROZEN
production-readiness claim         NOT AUTHORIZED
```
