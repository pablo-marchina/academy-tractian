# E6 Continuation — Live API Integration Contract

**Date:** 2026-08-16  
**Status:** CONTRACT PASS / LIVE ENDPOINT REQUIRED  
**Runtime candidate:** LangGraph  
**Execution boundary:** HarnessRunner  
**Transport surface:** `HttpxTransport`  
**LOCKED_TEST:** blocked  
**Model/MCP/RAG/UI freeze:** no

This report records the first continuation after the adaptive real ToolSpec LangGraph spike. The requested implementation path was added, but the public CI cannot execute the private supplied TRACTIAN API package because the package is intentionally not committed to the public research branch.

## What changed

- Added `scripts/research/e6_live_api_langgraph_runner.py`.
- Added `research/experiments/e6-live-api-integration-manifest.json`.
- Added a CI contract gate for the live API integration path.
- Added `research/results/e6-live-api-integration-contract-summary-2026-08-16.json`.

## Implemented live path

The live mode now supports:

```text
LangGraph
  ↓
model/proposal generation boundary
  ↓
adaptive evidence planning
  ↓
evidence-sufficiency policy node
  ↓
HarnessRunner
  ↓
HttpxTransport against supplied API
  ↓
B3 deterministic action gate
  ↓
RunTrace-compatible trace
```

## Gold leakage guard

Proposal generation is allowed to use only agent-visible information:

- `agent-input/cases.json`;
- OpenAPI/tool contract;
- runtime observations from the live API.

It explicitly rejects evaluator-only sources:

- `eval/expected-paths.json`;
- `eval/test-scenarios.md`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- `LOCKED_TEST` cases.

## CI result

- CI run: `31949759607`
- Artifact: `e6-live-api-integration-summary`
- Artifact id: `9264308984`
- CI status: success

The CI executed the contract gate and verified:

| Check | Result |
|---|---:|
| Live API transport configured | true |
| Transport class | `HttpxTransport` |
| Live API executed | false |
| ToolSpec registry size | 18 |
| HarnessRunner path configured | true |
| B3 preserved | true |
| Evidence-sufficiency explicit | true |
| Adaptive evidence planning | true |
| Model/proposal generation connected | true |
| Proposal gold leakage blocked | true |
| LOCKED_TEST accessed | false |
| Comparators retained | Pydantic AI/Graph + OpenAI Agents SDK |

## Important limitation

This is not yet a live task-success result because no `--api-base-url` was available inside CI and the private TRACTIAN package is not in the repo. The live runner is ready, but the actual supplied API run must be executed where the package is available.

## Live command

```bash
PYTHONPATH=. python scripts/research/e6_live_api_langgraph_runner.py \
  --transport-mode live \
  --api-base-url http://localhost:8000 \
  --agent-input-cases <TRACTIAN_PACKAGE>/agent-input/cases.json \
  --manifest research/experiments/e6-live-api-integration-manifest.json \
  --split-manifest research/frozen/benchmark-split-v1.json \
  --out /tmp/e6-live-api-integration-summary.json \
  --require-live
```

## Decision

Do not mark E6 live integration as final task-success evidence yet. Mark the implementation path and CI guard as complete, and keep the next active task as the real live API run in an environment where the supplied API package is running.

## Next step

```text
E6 live execution
├── start supplied TRACTIAN API locally
├── run e6_live_api_langgraph_runner.py in live mode
├── record DEV + VALIDATION live metrics
├── verify RunTrace-compatible traces
├── inspect any 4xx/5xx/action policy failures
├── update results from CONTRACT_PASS to LIVE_PASS or LIVE_NEEDS_REVIEW
└── keep LOCKED_TEST blocked
```
