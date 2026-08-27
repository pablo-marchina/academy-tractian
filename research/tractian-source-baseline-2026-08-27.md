# TRACTIAN source baseline and delivered-package audit — 2026-08-27

**Status:** canonical source audit for project requirements and partner guidance  
**Purpose:** freeze what the project is actually optimizing for before further development decisions  
**Scientific authorization:** none; this document does not open or reinterpret any experimental gate

## 1. Source hierarchy

Use this hierarchy whenever project sources appear to differ:

1. **[UPDATED] TAPI — Engenharia e Avaliação de Agentes Industriais** — formal assignment scope, deliverables and academic criteria;
2. **delivered TRACTIAN project package** — `STUDENT-GUIDE.md`, `agent-input/`, `eval/`, contract/docs and synthetic data as actually delivered;
3. **executable supplied API behavior and tests** — operational truth for the simplified API when prose and implementation differ;
4. **kickoff partner guidance** — product-quality guidance where it does not contradict the written assignment/package;
5. **project research/assumptions/extensions** — hypotheses to test, never a replacement for upstream requirements.

If a lower-priority source conflicts with a higher-priority source, preserve the conflict as evidence and follow the higher-priority requirement for the claim being made.

## 2. External source identities

The reviewed source bundle was identified by SHA-256:

| Source | SHA-256 |
|---|---|
| `inteli-tractian-project.zip` | `37546f7abad4c573ab36384a171161f3ba6c7258024341cc42f0881d9606d134` |
| `[UPDATED] Tapi Inteli  Tractian.pdf` | `3e7048bcdf52da8dda699cc6f68808dea6a37d45c0c7eb531c9d72d6f79500d1` |
| `tractian-kickoff.md` | `1735c73959bf6f6e2fbe672aaca759a494b73fbc3843ab35e526b7a8ecd4b78c` |

These hashes identify the exact materials used for this reconciliation. They do not imply that private/evaluation-only material may be committed or exposed to the agent.

## 3. Delivered-package facts

Observed from the delivered ZIP:

- `agent-input/cases.json`: **17** agent-visible cases;
- `eval/expected-paths.json`: **17** evaluation rows;
- `docs/test-scenarios.md`: **16** narrative scenarios;
- `eval/test-scenarios.md`: identical to `docs/test-scenarios.md` in this package;
- agent-facing OpenAPI authors **18 operations across 17 unique path templates**; the YAML repeats `/assets/{assetId}` as two mapping keys, one for `GET getAsset` and one for `PATCH updateAssetConfig`;
- ordinary YAML mapping loaders may silently overwrite one duplicate path entry and expose an incorrect 17-operation view; duplicate-aware normalization is therefore required before generating the canonical Tool Contract;
- the duplicate-aware normalized 18-operation contract matches the executable FastAPI routes and current `research/e2/tool_registry.py` with zero operation-route mismatches; see `results/tractian-api-contract-conformance-2026-08-27.json`;
- provided API supports contextual/company/user access, asset/analysis/model/knowledge reads, technical data, four mutation/action families and explicit escalation;
- API query behavior supports deterministic/reproducible seed control plus degraded response modes;
- impact actions require authenticated `x-user-id`, permission checks and sufficiently long justification;
- accepted action calls return `accepted=true` and represent execution without a required asynchronous status cycle.

Representative source hashes:

| Package file | SHA-256 |
|---|---|
| `README.md` | `fe7b255db8f0029d61ffbc63b33b203d148ce4bde7d3b657cfe004b47065e46a` |
| `STUDENT-GUIDE.md` | `967e3ea0aac7569246c4e71f421424ea6a1c964d404001b0e12cfb533e5f4696` |
| `agent-input/cases.json` | `804b1269ad5cc6867c6f74d30fb985ff70af52a30ec207f0c60118e1fe677c0d` |
| `agent-input/api-contract.openapi.yaml` | `8b3fdc5da50a8fa2923928a2f5aebcfe5034c622dba222df84f56abcd0b4aabf` |
| `eval/expected-paths.json` | `d6fb6186e4c035effe7dafa44758eaf40948ac334f0a91f8634a5731b7e0cb38` |
| `docs/test-scenarios.md` / `eval/test-scenarios.md` | `c087660173b4b0a03857848f8fe4a1f262e3cbeb57e1d6044a917be07dcb53b9` |
| `api/app/main.py` | `a9bdfb8a5fc85e8f169438984f787ad5fd0db95cdd2dc41a15e05ca363a3ca78` |
| `api/tests/test_api.py` | `b50fbabe2f497290a01984ba0663bb0b787184f0bc1b367e90871d0912326443` |

## 4. Package discrepancies that must not be silently papered over

The package contains small documentation/implementation inconsistencies. Treat these as source-quality facts, not as permission to rewrite upstream evidence.

1. Package `README.md` states **18 endpoints**. A lossy YAML mapping parse of the delivered agent-facing OpenAPI appears to show **17 operations / 17 paths**, but this is caused by the duplicated `/assets/{assetId}` mapping key: the authored contract contains both `GET getAsset` and `PATCH updateAssetConfig`. The executable API and delivered tests also implement both. Canonical integration must therefore normalize the duplicate path key into one path item carrying both methods, yielding **18 operations across 17 unique path templates**. Never derive the Tool Contract from a duplicate-dropping parser result.
2. `STUDENT-GUIDE.md` describes `eval/README-eval.md` and an example runner, but the reviewed ZIP contains only `eval/expected-paths.json` and `eval/test-scenarios.md` under `eval/`. Do not assume missing evaluation utilities were delivered.
3. There are **17** case/gold rows but **16** narrative scenarios because at least one scenario couples investigation and execution ticket evidence (for example the stale-analysis/reprocess path). Evaluation splitting/grouping must avoid treating coupled evidence as independent merely because ticket IDs differ.
4. The API envelope degradation modes are the technical response modes; `pending` and `stale` also appear as domain/scenario states. Evaluation should not conflate transport/response degradation with domain status.

The duplicate-path correction is independently captured by the sanitized conformance artifact `research/results/tractian-api-contract-conformance-2026-08-27.json`. Raw partner source remains outside Git; the correction changes source interpretation only and does not alter any C4 scientific gate, score, candidate or frozen experimental result.

## 5. Agent/evaluator custody boundary

The delivered package explicitly separates:

```text
agent-input/       -> material allowed to the agent
API over HTTP      -> runtime evidence source

eval/             -> evaluation-only references
case/gold datasets -> evaluator provenance, not prompt context
```

Development must preserve this separation. `expected-paths`, narrative resolutions, private/frozen oracle material or hidden outcomes must never become agent prompt/retrieval/tool context.

## 6. Partner-quality guidance that materially affects the final system

Kickoff guidance is not allowed to override the written TAPI/package, but it should influence quality and production choices when compatible:

- optimize the **operational conclusion and decision**, not exact wording;
- evaluate the **reasoning/process through observable traces**, not only the final answer;
- when evidence is insufficient or materially ambiguous, prefer safe human escalation over unjustified certainty;
- escalation handoff should carry the evidence collected, unresolved contradiction/uncertainty and why human analysis is needed;
- customer-facing responses should avoid unnecessary disclosure of internal implementation details;
- real product flows should consider explicit requester confirmation before consequential state changes, while the supplied benchmark itself treats accepted action calls as execution and does not encode a universal confirmation turn;
- expose a stable agent-facing tool/integration contract instead of forcing the model to reason over heterogeneous backend protocols directly;
- introducing an LLM/agent must not make an existing support workflow less available: provider/agent failure needs a safe fallback/handoff path;
- prove value/quality with a strong model/configuration frontier first, then optimize latency/cost/resource use using evidence rather than prematurely constraining capability;
- material choices must remain explainable by the developer: alternatives, trade-offs and why the chosen path is better for the project.

## 7. Fixed project north star

The repository optimizes for **the strongest defensible final delivery against the requested TRACTIAN/Inteli project**, not for benchmark novelty or architecture complexity.

Every material workstream must therefore map to at least one of:

1. a formal TAPI/package requirement;
2. an academic evaluation criterion;
3. a material partner-quality/production risk compatible with the written scope; or
4. an experiment required by `PROJECT-PRINCIPLES.md` to choose among credible alternatives.

Optional complexity is rejected unless it measurably improves a required capability, a material risk or the production Pareto frontier.

## 8. Non-inferences

This source reconciliation does **not** establish any of the following as final:

- provider/model;
- LangGraph/LangChain/Pydantic AI/custom state machine;
- single-agent vs multi-agent;
- MCP vs native tools/adapters;
- RAG/vector DB/reranking;
- persistent memory;
- semantic judge;
- deployment topology;
- UI technology.

Those remain material decisions subject to the repository's systematic comparison and evidence rules.
