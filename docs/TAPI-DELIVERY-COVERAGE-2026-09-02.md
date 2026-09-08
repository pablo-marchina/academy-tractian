# TAPI Delivery Coverage — Active Crosswalk

**Status:** ACTIVE assignment/output reference  
**Original filename checkpoint:** 2026-09-02  
**Current rebaseline:** 2026-09-08 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Provider evidence:** [`PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](PROVIDER-QUALIFICATION-STATUS-2026-09-08.md)

This crosswalk separates TAPI/delivered-package expectations from project-added production and quality constraints.

## 1. Integrated deliverable

The project delivers both required tracks:

1. **Industrial Agent** — contextualizes/investigates industrial requests using typed TRACTIAN operations and produces safe grounded outcomes/proposals.
2. **Agent Evaluation Framework** — evaluates observable tool selection, arguments, trajectory, evidence, terminal behavior, safety, failures and stability through reproducible controlled experiments.

Consequential external execution remains disabled in the promoted Release 0 scope.

## 2. TAPI expectations mapped to current evidence

| Expectation | Current evidence / boundary |
|---|---|
| functional agent | hosted provider→controller→tool→evidence→terminal path |
| supplied TRACTIAN API use | canonical 18-operation contract; real read paths proven |
| function/tool selection | ToolSpec proposals + deterministic/rubric evaluation |
| argument validity | typed schema/B1 validation + resource constraints |
| resource grounding | authenticated identity/company/fleet + observed IDs |
| observable process/trajectory | RunTrace + persisted Technical analysis |
| evidence use | normalized evidence IDs/lineage |
| response quality | terminal + explicit response-mode semantics |
| clarification/abstention/escalation | promoted terminal behavior + frozen provider scenarios |
| unavailable/conflicting evidence | explicit failure scenarios in provider population |
| high-impact behavior | action-governance scenarios + external execution disabled |
| failure behavior | provider/tool/auth/evidence failure semantics |
| stability | 17 scenarios × 5 repetitions in provider qualification |
| technical experiment | provider V4/Groq qualification + causal serving diagnosis |
| results/limitations | machine-readable frozen manifests/results + current canonical status |
| reproducibility | exact source/population/runner/bootstrap identities |
| documentation | active docs + append-only 2026-09-08 progress evidence |
| demonstration | normal hosted task-driven product + Technical depth |

## 3. Provider/evaluation evidence added 2026-09-08

The final provider work materially strengthens the TAPI evaluation track.

### Frozen population

```text
17 industrial decision scenarios × 5 repetitions
= 85 attempts per candidate
```

Population SHA-256:

`4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9`

It covers normal reads, arguments, clarification/failure cases, conflicting/unavailable evidence and action governance.

### Groq-only full qualification

After Cloudflare was quota-blocked and explicitly removed from the requested path, Groq GPT-OSS-120B completed 85/85 under the frozen rubric/gates.

Result: **`NO_SELECTION`**.

```text
rubric pass       69/85 = 81.18%
reliability       70/85 = 82.35%
contract failures 9
repeat stability  11/17 = 64.71%
p50 latency       1.154 s
p95 latency       2.904 s
```

This negative result is useful evaluation evidence: the framework detects a provider/model that often selects correct reads but fails structural/terminal stability requirements.

### Failure-analysis experiment

The subsequent causal diagnostic separates:

- completion-budget/finish effects;
- best-effort structured-output conformance;
- reasoning-effort effects.

Observed evidence refutes “512 tokens are the only problem”: a call can finish normally with valid JSON and still violate the application decision contract.

## 4. Evaluation quality / integrity boundary

The project does **not** make the benchmark easier after a failure.

Current hard provider gates remain:

```text
private/identity-material attempts = 0
unknown-tool proposals = 0
invalid known-tool arguments = 0
schema/adapter contract failures = 0
trace/provenance failures = 0
reliability >= 93.75%
```

No automatic repair/fallback/selective rerun may hide scored failures.

This supports the TAPI requirement that the full observable process, failure behavior and stability matter rather than just final prose quality.

## 5. Current stack/state

| Layer | Current choice/state |
|---|---|
| language | Python 3.11+ |
| API | FastAPI + Uvicorn |
| schemas | Pydantic 2.x |
| orchestration | custom `AgentController` promoted baseline |
| production provider wrapper | Release 0 V13 line; provider remains provisional |
| real tool boundary | `HarnessRunner` + canonical ToolSpec registry |
| TRACTIAN transport | direct typed HTTPS adapter |
| durable state | Neon PostgreSQL + RLS |
| browser IAM | Neon managed session; server-owned scope |
| hosting | Railway production services |
| provider final selection | **NO WINNER**; Groq-only 85/85 = `NO_SELECTION` |
| evaluation | deterministic-first production evaluator + frozen research campaigns |
| realtime | durable Postgres cursor + LISTEN/NOTIFY wake-up + authenticated SSE |
| frontend | React/TypeScript/Vite/Caddy, Home / Analyses / Technical |

## 6. 18-operation contract

```text
18 total canonical operations
13 READ  → promoted read surface when provider + transport are enabled
5 ACTION → represented/proposal-only; external execution disabled
```

Contract coverage and recent live user-prompt coverage remain distinct metrics.

## 7. Strict structured-output experiment

The current provider failure analysis justifies testing stricter structured decision generation, not weakening the controller contract.

Any `strict:true` challenger must derive closed per-tool/terminal variants from the canonical ToolSpecs/supplied OpenAPI, with `ProviderDecisionPayload` and deterministic argument/policy validation retained afterward.

The exact supplied `ActionRequest` schema must be recovered before strict action variants are complete.

## 8. Current agent behavior relevant to TAPI

- discover authorized resources instead of asking users for internal IDs when discoverable;
- inspect evidence classes appropriate to the question;
- preserve uncertainty through response modes;
- fail closed for missing authorized resources;
- keep actions proposal-only in the promoted product;
- expose safe trace/evaluation evidence for review.

## 9. Deliberately not promoted

- Groq GPT-OSS-120B production use;
- strict structured-output serving;
- LangGraph migration;
- multi-agent topology;
- RAG/vector DB;
- persistent memory;
- MCP;
- Redis/Kafka/Kubernetes;
- adaptive stopping/routing.

Each requires a measured gap and controlled promotion evidence.

## 10. Remaining final-delivery evidence

- clean isolated 21/21 provider causal matrix;
- exact `ActionRequest` recovery;
- strict-schema eligibility/preflight if justified;
- unchanged-rubric challenger comparison;
- fresh 85/85 for a hard-gate winner;
- Academy live E2E before provider promotion;
- broader recent canonical read/semantic coverage;
- true bilateral in-fleet comparison;
- full SECURITY-V1;
- load/capacity + evidence-derived SLO;
- restore/recovery;
- human semantic calibration;
- operational-value study or explicit non-claim;
- final evidence freeze.

## 11. Demonstration contract

Demonstrate the normal hosted product:

```text
sign in
→ Home: real equipment question
→ Result: conclusion + response mode + evidence
→ Analyses: persisted alternate run
→ Technical: trace / evaluator / architecture / actions
→ exact provider/production limitations
```

A truthful final presentation may say the provider framework rejected Groq GPT-OSS-120B under the current configuration; it must not call that run a production promotion or a comparative Cloudflare victory/loss.
