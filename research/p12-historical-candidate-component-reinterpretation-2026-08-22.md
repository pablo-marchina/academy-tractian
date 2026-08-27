# P12 Historical Candidate / Component Reinterpretation

**Date:** 2026-08-22  
**Status:** COMPLETE — RETROSPECTIVE EVIDENCE RECLASSIFICATION  
**Protocol:** `P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST` (`FROZEN`)  
**Scope:** material decision-bearing candidates/components from E0 through E14v plus unresolved architecture surfaces  
**New provider/model inference:** none  
**New private VALIDATION / LOCKED_TEST / FRESH_BLIND semantic access:** none

## 1. Purpose

BIG-B4 froze a new evidential contract. This record does not rerun history or rewrite historical artifacts. It reinterprets what each material historical result can support **now**, under P12.

The governing rules are:

1. historical DEV + historical VALIDATION are one `EXPOSED_POOL`; historical results on either remain legitimate development/selection evidence but are not independent generalization evidence;
2. a historical hard-gate failure remains a failure — P12 does not promote failed candidates;
3. deterministic/infrastructure evidence may qualify a component only for the property actually demonstrated;
4. synthetic evidence may qualify robustness/evaluator/judge behavior but cannot establish real-domain production generalization;
5. legacy LOCKED_TEST structural exposure limits evaluator/full-stack independence claims and no historical component gains a pristine-final claim;
6. `EXPERIMENT_FROZEN` reproducibility is distinct from project-level `FROZEN` selection;
7. no historical implementation candidate is promoted to `PREFERRED` or project-level `FROZEN` merely by this retrospective review.

## 2. Executive result

The frozen **evaluation protocol P12** is the only project-level technical selection currently at `FROZEN` state.

Historical implementation evidence separates into four buckets:

- **Canonical/immutable factual artifacts:** E0 contract/gold artifacts remain experiment-frozen; E3 split assignments remain immutable history but their old split-role semantics are superseded by P12.
- **`QUALIFIED` components:** ToolSpec/Harness foundations, LangGraph as a research runtime candidate, live `HttpxTransport` integration, native and MCP-compatible tool surfaces, Groq zero-cost transport/provider path, evaluator v4.1/v4.2 direction, qualified Qwen semantic judge, retained deterministic provenance/serializer/safety guard components.
- **`RESEARCHED` but not qualified whole candidates:** current/previous model generations and the E14 evidence-selection line where required quality/evidence gates were not satisfied, including E14t as the strongest retained historical evidence-selection reference.
- **`SUPERSEDED` / closed candidates:** unsafe early boundary baselines, older exact guard bundles, failed E13, failed/operationally invalid E14 generations, E14u rejection, and consumed E14v/E14v-A/E14v-B attempts.

There is **no historical system candidate at `PREFERRED`** under P12. Final runtime/provider/model/topology/agent architecture remains unfrozen.

## 3. Reinterpreted registry

### 3.1 Canonical foundations and benchmark artifacts

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / next evidence |
|---|---|---|---|---|
| F01 | E0 API/behavior contract freeze | `FROZEN` factual artifact (`EXPERIMENT_FROZEN`) | Canonical supplied API/tool behavior facts and reproducibility anchor. | Not an architecture selection. Change only through explicit contract versioning. |
| F02 | E1 evaluator-only gold freeze | `FROZEN` factual artifact (`EXPERIMENT_FROZEN`) | Immutable historical supervision artifact. | Candidate/developer oracle access remains forbidden; not evidence that evaluator implementation is final. |
| F03 | ScenarioSchema / Canonical ToolSpec / TraceSchema / deterministic replay foundation | `QUALIFIED` | Framework-neutral experiment contract, tool registry and trace/replay infrastructure are valid research foundations. | Production fitness and final runtime composition remain unproven. |
| F04 | E3 `benchmark-split-v1` assignment | `SUPERSEDED` role semantics; artifact remains `EXPERIMENT_FROZEN` | Historical group assignment remains immutable provenance. | Old DEV/VALIDATION role semantics are replaced: DEV+VALIDATION => `EXPOSED_POOL`; LOCKED_TEST => qualified supplementary final-only role. |
| F05 | P12 evaluation protocol | `FROZEN` | Governs all new development, selection, uncertainty, candidate freeze and final-access rules. | Does not freeze any candidate architecture/model/provider. |

### 3.2 E4 guarded-boundary candidates

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / disposition |
|---|---|---|---|---|
| E4-B0 | Unguarded/baseline boundary | `SUPERSEDED` | Historical safety baseline. | Executed invalid and premature actions; cannot be promoted. |
| E4-B1 | Invalid-argument guard sublayer | `SUPERSEDED` exact bundle; invariant retained | Demonstrated containment of invalid action arguments on exposed evidence. | Exact implementation was subsumed by later guard stacks. |
| E4-B2 | Resource/permission guard sublayer | `SUPERSEDED` exact bundle; invariant retained | DEV evidence supported resource/scope safety value. | E4 VALIDATION had no new scope pressure; later guard architecture supersedes exact bundle. |
| E4-B3 | Combined guarded boundary | `SUPERSEDED` exact bundle | Historical exposed-pool evidence showed best B0–B3 safety/task signal and zero E4 uncontained safety failures. | Its promotion was directly informed by historical VALIDATION; later E10–E14 guard stack supersedes exact candidate. No independent-generalization claim. |

### 3.3 E5 evidence acquisition / stopping

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / disposition |
|---|---|---|---|---|
| E5-REF | `fixed_reference_like` | `RESEARCHED` infrastructure anchor | Useful deterministic/reference-like upper-bound and harness check. | Explicitly not agent-quality evidence. |
| E5-FREE | `free_tool_loop` | `SUPERSEDED` behavioral baseline | Historical baseline for premature stopping/unnecessary calls. | Inferior to evidence-sufficiency on exposed evidence. |
| E5-SUFF | evidence-sufficiency/stopping policy | `QUALIFIED` for stopping-policy behavior | On the exposed 11-scenario comparison it improved task success, evidence coverage and call discipline versus free loop. | Does not prove correct evidence-route selection or independent generalization; must remain removable if prospective P12 comparison contradicts it. |

### 3.4 E6 runtime and integration

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / next evidence |
|---|---|---|---|---|
| E6-LG | LangGraph | `QUALIFIED` runtime candidate | Best-supported historical runtime direction for replay/checkpoint/HITL/guard integration; integration path was exercised live. | Scorecard was close and asymmetrical; needs prospective implementation-symmetric P12 comparison plus production metrics before `PREFERRED`. |
| E6-PYD | Pydantic AI/Graph | `RESEARCHED` comparator | Credible typed/schema/observability runtime alternative. | Did not receive equivalent depth of live spike. |
| E6-OAI | OpenAI Agents SDK | `RESEARCHED` comparator | Credible provider-native tracing/guard/HITL/MCP alternative. | Portability concern and no equivalent deep spike; provider choice is unfrozen. |
| E6-LIVE | LangGraph + ToolSpec + HarnessRunner + `HttpxTransport` | `QUALIFIED` research integration stack | 37/37 recorded live API requests succeeded; RunTrace compatibility, external deterministic guard and checkpoint/pause-resume path were demonstrated. | Eight representative exposed cases and one integration context do not establish production reliability, concurrency, SLOs or final architecture. |
| E6-HARNESS | HarnessRunner / `HttpxTransport` boundary | `QUALIFIED` research infrastructure | Valid live execution boundary for controlled experiments. | Production retry/idempotency, persistence, throughput and operational ownership remain open. |

### 3.5 E7 native tools / MCP

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / next evidence |
|---|---|---|---|---|
| E7-NATIVE | Native ToolSpec envelope | `QUALIFIED` | Lower-complexity internal surface with preserved schema/guard/trace behavior. | Internal-default preference remains provisional until production/topology comparison. |
| E7-MCP-ADAPTER | MCP-compatible adapter | `QUALIFIED` | 18/18 tool-schema coverage and equivalent invocation/guard/trace behavior were demonstrated as an interoperability adapter. | This does not qualify a full MCP server/client topology. |
| E7-MCP-TOPOLOGY | MCP as core topology | `RESEARCHED` | A credible architecture option when external integration requires it. | No evidence requires replacing native core execution; not selected/frozen. |

### 3.6 E8 provider/model evidence

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / disposition |
|---|---|---|---|---|
| E8-GROQ-PROVIDER | Groq zero-cost remote path | `QUALIFIED` for provider operability | Demonstrated USD-0 keyed remote execution, schema-valid output path and trace integration. | Historical provider leadership was based on exposed/proxy evidence; provider selection remains open. |
| E8-LLAMA31 | Groq `llama-3.1-8b-instant` | `SUPERSEDED` as leading model candidate | Historical operational baseline. | E9 private scoring showed substantial task-quality/evidence/action gaps despite proxy pass; later GPT-OSS line replaced it. |
| E8-ALTERNATIVES | Gemini / OpenRouter / Hugging Face / Ollama / no-model baseline | `RESEARCHED` | Credible free/local/provider alternatives were identified. | Execution breadth was not sufficient for a final comparative model/provider decision. |

### 3.7 Evaluator and semantic judge

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / next evidence |
|---|---|---|---|---|
| E9-V3 | E9 v3 private task-quality scorer | `SUPERSEDED` as promotion gate; retained for historical comparability | Demonstrated the critical proxy-vs-real disagreement and enabled historical fixed-output scoring. | Known lexical and supervision-alignment defects prevent treating it as the current final gate. |
| E9-V41 | deterministic evaluator v4.1 direction / selected-ticket supervision | `QUALIFIED` | Public tool-signature supervision and exact selected-ticket alignment resolve known v3/group-union defects. | Evaluator development structurally inspected all 3 legacy LOCKED_TEST groups; exact evaluator hash must be qualified/frozen per future candidate generation. |
| E9-V42 | semantic-groundedness protocol | `QUALIFIED` evaluation component | Frozen synthetic suite/protocol provides a defined semantic-groundedness measurement layer. | Synthetic qualification alone is not blind real-domain proof. |
| JUDGE-QWEN | Groq `qwen/qwen3.6-27b` semantic judge | `QUALIFIED` judge candidate | Historical frozen synthetic qualification supported high support-label/claim-type performance with zero recorded critical false-support failures. | Must be re-qualified/frozen for any future gating generation; broader adversarial/repeatability comparison remains required before project-final judge selection. |

### 3.8 E10–E13 safety / authorization line

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / disposition |
|---|---|---|---|---|
| E10-LEGACY-GUARDS | E10/E10b/E10c/E10d/E10e/E10f/E10g exact guard candidates | `SUPERSEDED` | Preserved historical evidence about action/escalation/safety failure modes and guard behavior. | Multiple iterations were directly influenced by historical VALIDATION aggregate feedback; later E14 deterministic stack supersedes exact implementations. |
| E10H-E12-DIAG | E10h + E12 blocker/root-cause diagnostics | `RESEARCHED` diagnostic evidence, not candidates | Established that the active policy could be over-permissive / wrong authorization class and informed later independent authorization. | Diagnostics themselves are not deployable components and reused exposed feedback. |
| E11-AUTH | independent authorization / hard-gate concept | `SUPERSEDED` exact implementation; principle retained | Established the need for deterministic authorization outside self-attested model intent. | Exact version was later incorporated/refined by E14q/E14q2. |
| E13-REPROCESS | reprocess-specific authorization candidate | `SUPERSEDED` / rejected | Preserved zero premature/unsupported behavior on scoreable DEV calls. | Failed its own DEV gate: action correctness 0, decision 0.4, task quality 0.7714 and one missing parsed output. Must not be revived as-is. |

### 3.9 E14 early full-agent generations and retained deterministic fixes

The exact E14/E14b–E14l candidate generations are historical research outcomes, not qualified whole-agent candidates: every valid real generation in that family failed at least one frozen DEV quality gate, while E14h/i/j produced no valid parsed quality sample. The following component-level findings survive independently of the failed whole generations.

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / disposition |
|---|---|---|---|---|
| E14-E14B | initial E14 / E14b generations | `SUPERSEDED` | Historical full-agent baselines and failure evidence. | Failed DEV gates. |
| E14C-ACTION-NORM | public action-endpoint representation fix | `QUALIFIED` deterministic component | Corrected action-endpoint representation without rewriting model semantics. | Component qualification only; does not qualify its parent generation. |
| E14D-EVIDENCE-NORM | public evidence-resource representation fix | `QUALIFIED` deterministic component | Corrected public evidence-resource representation and helped isolate true boundary failures. | Component qualification only. |
| E14E-ESCALATION | explicit handoff/escalation semantics | `QUALIFIED` deterministic component | Replaced over-broad lexical escalation markers with explicit current handoff semantics. | Component qualification only. |
| E14F-REPAIR | conditional same-model public contradiction repair | `RESEARCHED` | Demonstrated a bounded public-consistency repair mechanism. | Whole E14f generation remained below quality gate; consistency is not benchmark correctness. |
| E14G-120B | E14g GPT-OSS-120B generation | `SUPERSEDED` generation; model family remains `RESEARCHED` | Established operational feasibility of `openai/gpt-oss-120b` on the research path. | 6/6 complete but failed quality gate. |
| E14H-I-J | high-reasoning 1600-token generations | `SUPERSEDED` operational failures | Valuable provider/telemetry failure evidence. | 0/6 parsed outputs; no task-quality conclusion is valid. |
| E14K-L | 4096-token high/medium reasoning generations | `SUPERSEDED`; tuning family closed | Demonstrated that operational completeness can be recovered with 4096 tokens and that further reasoning/budget/format tuning lacked evidence. | Both complete generations still failed task-quality gates; E14l decision/action/escalation collapsed. |

### 3.10 Retained E14 deterministic stack and full-DEV evidence-selection line

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / next evidence |
|---|---|---|---|---|
| E14N | E14n v1.1 identifier-provenance guard | `QUALIFIED` | Retained deterministic identifier/provenance safety invariant. | Must be regression-tested prospectively when candidate stack changes. |
| E14P | E14p deterministic epistemic serializer | `QUALIFIED` | Retained deterministic serializer; prior accepted full-DEV semantic run passed its groundedness layer. | Not a whole-agent qualification; exact version must be frozen per future generation. |
| E14Q-Q2-GUARDS | E14q / E14q2 deterministic safety/action authorization guards | `QUALIFIED` | Full-DEV history supports a clean deterministic safety surface; retained as current guard baseline. | Hard-safety regression remains blocking; guard qualification does not solve evidence completeness. |
| E14Q2-BASE | E14q2 full-DEV candidate baseline | `RESEARCHED` | Useful P12 exposed-pool baseline for evidence selection. | Failed evidence gate: 0.20 evidence correctness, 0.7667 expected-read recall. |
| E14R | visible-case replacement | `SUPERSEDED` / rejected | Demonstrated over-pruning failure mode. | Evidence correctness 0 and recall 0.4. |
| E14S | capped candidate-pool consensus | `SUPERSEDED` / rejected | Directional evidence that bounded consensus can increase recall relative to E14r. | Still below gate: 0.20 evidence correctness, 0.775 recall. |
| E14T | bounded restoration | `RESEARCHED` retained reference baseline | Strongest historical deterministic evidence-selection result: evidence 0.30, recall 0.80, extras 3.40 while decision/action/escalation stayed 0.8 and hard-safety surface clean. | Still fails required evidence >=0.50 and recall >=0.8333; not `QUALIFIED`. |
| E14U | public evidence-decomposition prompt | `SUPERSEDED` / rejected | Demonstrated that increasing evidence-plan surface can worsen actual route selection. | Evidence 0.10, recall 0.7417, extras 4.0; explicitly rejected. |

### 3.11 E14v isolated evidence-route planner

| ID | Candidate/component | P12 state | Defensible claim now | Limitation / next evidence |
|---|---|---|---|---|
| E14V-CONCEPT | isolated public evidence-route planner architecture | `RESEARCHED` | Scientifically motivated response to the E14t selection bottleneck; isolates route selection and has a frozen public synthetic qualification design. | No valid synthetic qualification has passed; no real EXPOSED_POOL planner call is justified from historical evidence alone. |
| E14V-1 | original E14v synthetic attempt | `SUPERSEDED` / consumed | Operational failure evidence only. | 14/14 provider errors, zero valid contracts; attempt lock remains consumed. |
| E14V-A | transport-contract amendment attempt | `SUPERSEDED` / consumed | Isolated HTTP 403 provider-access failure. | No planner-quality conclusion; attempt lock remains consumed. |
| E14V-B | permission-remediation attempt | `SUPERSEDED` / consumed | Workflow/transport characterization artifact. | Aggregate failed with 0 valid outputs; route quality remained unresolved. Never silently rerun. |

### 3.12 Architecture surfaces that were repeatedly left undecided

| ID | Candidate/component | P12 state | Current conclusion |
|---|---|---|---|
| ARCH-RAG | RAG / vector DB / reranking architecture | `UNASSESSED` for final selection | No project-final comparative evidence. Add only if a P12 hypothesis predicts measurable gain over simpler retrieval. |
| ARCH-MULTI | multi-agent decomposition | `UNASSESSED` for final selection | No evidence yet that multi-agent complexity is necessary. Compare against single-agent baseline before adoption. |
| ARCH-MEM | persistent memory | `UNASSESSED` for final selection | No production requirement/evidence justifies project-final persistent memory yet. |
| ARCH-OBS | observability backend | `UNASSESSED` for final selection | TraceSchema exists, but backend/SLO/alerting/ownership choice is open. |
| ARCH-UI | UI/demo architecture | `UNASSESSED` for final selection | Demo surface cannot determine agent-quality architecture. |
| ARCH-FINAL | whole production architecture | `RESEARCHED`, not `PREFERRED` | Multiple qualified building blocks exist, but production reliability/security/operability and fair component comparison remain incomplete. |

## 4. What P12 changes — and what it does not

### Historical VALIDATION

E4 explicitly selected/promoted B3 from VALIDATION performance; E5–E8 also used DEV+VALIDATION. Under P12 those observations are retained as `EXPOSED_POOL` development evidence, **not deleted**. What disappears is the independent-validation interpretation.

Therefore:

- B3/E5/LangGraph/native/Groq historical comparisons may support `RESEARCHED`/`QUALIFIED` component claims;
- they may not support a fresh-generalization or final-production claim;
- a later DEV-only run does not erase earlier adaptive influence in the lineage.

### Historical hard-gate failures

P12 does not lower historical gates. E13 remains rejected. E14 real candidate generations that failed quality/evidence gates remain unqualified whole candidates. E14t remains the strongest retained evidence-selection reference, not a promoted winner.

### Artifact freeze vs project freeze

Historical manifests labelled frozen remain immutable reproducibility artifacts. That does not mean the corresponding runtime/model/evaluator/system is project-final. Examples:

- E0/E1 contract/gold: canonical frozen factual artifacts;
- E3 benchmark split: frozen historical assignment, but role semantics superseded;
- evaluator amendment/synthetic suites: experiment-frozen measurement definitions;
- P12: current **project-level frozen evaluation protocol**;
- runtime/provider/model/overall architecture: not project-frozen.

## 5. Current P12 decision-state inventory

At the end of this reinterpretation:

```text
project-level FROZEN
  P12 evaluation protocol only

QUALIFIED building blocks
  framework-neutral ToolSpec/trace/replay foundation
  evidence-sufficiency stopping behavior (limited claim)
  LangGraph runtime candidate
  HarnessRunner + HttpxTransport research integration
  native ToolSpec surface
  MCP-compatible adapter
  Groq zero-cost provider path (operability claim only)
  evaluator v4.1 direction / selected-ticket alignment
  v4.2 semantic-groundedness protocol
  Qwen semantic judge candidate
  E14c/E14d/E14e deterministic normalization/semantics
  E14n provenance guard
  E14p serializer
  E14q/E14q2 deterministic safety authorization guards

PREFERRED historical implementation candidates
  NONE

RESEARCHED active references
  Pydantic AI/Graph
  OpenAI Agents SDK
  provider/model alternatives
  GPT-OSS-120B model family
  E14q2 baseline
  E14t strongest historical evidence-selection reference
  E14v isolated planner concept
  whole architecture

SUPERSEDED / rejected / consumed
  unsafe E4 baseline and exact old boundary bundles
  free-loop baseline as active policy
  llama-3.1-8b-instant as leading model
  E9 v3 as current promotion gate
  E10 exact guard sequence
  E11 exact implementation
  E13
  failed exact E14/E14b–l generations
  E14r/E14s/E14u
  E14v / E14v-A / E14v-B consumed attempts

UNASSESSED for final selection
  RAG/vector DB
  multi-agent decomposition
  persistent memory
  observability backend
  UI architecture
```

## 6. Authorized next experimental surface

The old `PROJECT-PLAN.md` must no longer be interpreted as authorizing its historical `DEV → VALIDATION` sequence. Under P12, the next agent work is constrained to `EXPOSED_POOL` and must be prospective.

The strongest justified starting point is **not** an automatic E14v-C rerun. It is a new P12 preregistration that treats historical results as priors and compares a small set of materially credible evidence-selection candidates against retained baselines.

Minimum next experiment requirements:

1. **Baseline:** carry E14t (strongest historical evidence-selection reference) and the retained deterministic E14n → E14p → E14q → E14q2 stack.
2. **Candidate family:** include E14v-style isolated route planning only if a new public synthetic qualification variant is scientifically/operationally justified; consumed E14v/A/B attempts are never rerun.
3. **Alternative:** include at least one materially simpler route-selection baseline so the planner is not promoted merely because it is new/complex.
4. **Partition:** `EXPOSED_POOL` only; no FRESH_BLIND or LEGACY_LOCKED_TEST access.
5. **Unit:** all 7 asset/story groups, with full-pool result + LOGO sensitivity + modality/safety slices.
6. **Stochastic runs:** minimum 3 repetitions/scenario; paired candidates use matched seeds where supported.
7. **Outcomes:** P12 primary quality metrics + existing evidence-completeness metrics; hard safety remains non-compensable.
8. **Uncertainty:** 95% group-cluster percentile bootstrap, 20,000 resamples, seed `20260822` for the 7-group pool.
9. **Evaluator/judge:** exact qualified evaluator/judge versions declared before the comparison; outputs fixed before private exposed-pool scoring.
10. **Decision:** `QUALIFIED` means passes its preregistered gates; `PREFERRED` requires comparative superiority/robustness and production fit. No candidate reaches final `FROZEN` from exposed-pool performance alone.

## 7. Production-readiness consequence

This reinterpretation does not authorize a production-readiness claim. The repository still lacks adequate evidence for several production dimensions, including load/concurrency, SLOs, long-run reliability, persistent production state, retry/idempotency semantics, deploy/rollback, observability/alerting ownership, secrets rotation, disaster recovery, provider failover, broad security red-team coverage, postcondition verification and privacy/data-retention controls.

Therefore:

- evaluation protocol: `FROZEN`;
- candidate optimization on `EXPOSED_POOL`: authorized;
- final architecture: not `PREFERRED` and not `FROZEN`;
- FRESH_BLIND: no source authorized;
- LEGACY_LOCKED_TEST: blocked pending final authorization;
- production-readiness claim: not authorized.

## 8. Sources

Primary reinterpretation anchors include:

- `research/frozen/big-b4-evaluation-protocol-v1.json`
- `research/big-b4-evaluation-protocol-freeze-2026-08-22.md`
- `research/46-e4-validation-boundary-results.md`
- `research/48-e5-evidence-stopping-results.md`
- `research/50-e6-runtime-spike-results-adr.md`
- `research/56-e6-live-api-integration-live-results.md`
- `research/58-e7-native-tools-vs-mcp-results.md`
- `research/59-e7-topology-adr.md`
- `research/65-e8-groq-free-anywhere-model-run-results.md`
- `research/73-e9-private-task-quality-results.md`
- `research/evaluator-v4-validity-status.md`
- `research/evaluator-v4-visible-case-alignment-result.md`
- `research/103-e13-dev-only-private-score-results.md`
- `research/README.md`
- `research/141-e14l-real-dev-measurement-result.md`
- `docs/PROJECT-PLAN.md`

Historical artifacts remain immutable; this file changes only their present-day evidential interpretation.