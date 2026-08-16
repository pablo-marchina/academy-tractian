# E2 — Wave 2 Execution Report

**Date:** 2026-08-16  
**Status:** ACTIVE  
**Scope:** complete the framework-neutral execution layer without selecting an agent runtime.

## Completed in this wave

### B0 transport boundary

- Added `research/e2/transport.py`.
- Path parameters are serialized from canonical snake_case names to the frozen API camelCase route placeholders.
- `x-user-id` remains runner-bound.
- `seed` is runner-bound only for the stochastic read operations identified by the frozen contract/behavior evidence.
- Unknown and missing declared arguments are rejected at the transport boundary.
- B0 intentionally does not apply B1 strict body semantics, B2 permission/resource policy, or B3 evidence/stopping policy.
- Added `scripts/research/e2_b0_real_api_probe.py` to run a reproducible CEN-01 transport probe against the supplied API without copying partner artifacts into the repository.

### Deterministic B3 foundation

- Added `EvidenceAwareActionGate`.
- The gate composes existing strict validation and resource/permission policy with scenario action/evidence oracles.
- It can block wrong actions, wrong targets and actions attempted before required evidence.
- It does not infer policy from natural-language model output.

### Evaluation layer

- Added `ArgumentEvaluator` for structured schema/required-argument correctness.
- Added `ConclusionEvaluator` for structured fact/claim/uncertainty evaluation; it does not use text similarity.
- Added `EscalationHandoffEvaluator` for human-escalation decision and handoff completeness.

### Replay / trace normalization

- Added deterministic normalization of timestamps, call IDs, request/response IDs and action IDs for cross-run trace comparison.

### Fixtures

Added deterministic pass/fail fixtures for:

- B0 path/query/identity/seed binding;
- action seed exclusion;
- model-controlled identity rejection;
- missing-evidence action blocking;
- evidence-satisfied action allowance;
- invalid argument detection;
- structured conclusion correctness;
- forbidden-claim detection;
- escalation handoff completeness;
- volatile trace normalization.

## Real API probe

The supplied FastAPI handlers were exercised in-process with the supplied synthetic seed source. The environment lacks `pyarrow`, so the probe uses the package's exact `seed_data.py` tables in memory rather than changing the API handlers or inventing replacement data. This is a test-environment adaptation, not a demo path.

The CEN-01 reference path was used only as a transport/conformance fixture:

1. `GET /assets/asset_G501`
2. `GET /assets/asset_G501/baseline`
3. `GET /assets/asset_G501/data-quality`
4. `GET /assets/asset_G501/rms`
5. `POST /cases/case_tkt_inv_04/escalate`

The observed statuses were 200 for all five calls and the action returned `accepted=true`. The probe is intentionally not an agent behavior claim: it verifies only that the canonical transport can execute a representative reference path against the supplied API implementation.

## Methodological boundary

This wave does **not**:

- implement an LLM agent;
- choose a model;
- choose LangGraph, Pydantic AI/Graph or OpenAI Agents SDK;
- choose MCP;
- add RAG, multi-agent routing or persistent memory;
- optimize prompts;
- construct a presentation/demo flow.

Those remain experimental decisions after E2/E3.

## Remaining E2 unlock items

1. Integrate the new evaluators/gate into a single harness runner.
2. Add representative scenario fixtures for investigation, contextualization and execution.
3. Verify registry/contract operation metadata mechanically from the frozen E0 manifest.
4. Complete B0 end-to-end trace emission and replay capture.
5. Run the full E2 test suite and record the result.
6. Then unlock E3 benchmark split freeze.
