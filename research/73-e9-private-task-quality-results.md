# E9 Private Task-Quality Results

**Status:** E9_TASK_QUALITY_SCORER_PASS  
**Date:** 2026-08-16  
**Scorer:** `scripts/research/e9_evaluator_side_scorer_v3.py`  
**Oracle adapter:** `expected_paths_asset_mention_adapter_v3_case_safe`  
**Leading free-provider candidate scored:** Groq `llama-3.1-8b-instant`  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## What passed

E9 now runs end-to-end in private/local mode:

1. fixed Groq outputs are consumed after model generation;
2. parsed model outputs are available for all fixed calls;
3. private DEV/VALIDATION expected paths are read only inside the evaluator-side scorer;
4. expected-path rows are mapped to fixed output groups by local asset mentions;
5. output hashes are used for fixed-output integrity;
6. raw private oracle values are not printed or committed;
7. LOCKED_TEST remains blocked.

This is a scorer execution pass, not a final architecture/model-quality approval.

## Sanitized aggregate result

| Metric | Value |
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

## Interpretation

The E8 proxy run was over-optimistic. Groq produced schema-valid fixed outputs and passed the proxy gate, but private expected-path scoring shows substantial task-quality gaps:

- evidence correctness is currently 0.0;
- action correctness is currently 0.25;
- escalation correctness is currently 0.5;
- proxy-vs-real disagreement is 1.0.

The positive result is that the model did not make unsupported final claims, did not claim LOCKED_TEST, and had no premature-action rate in this scorer view. The main failure mode is quality and grounding against the expected path, not leakage or unsafe benchmark access.

## Boundary preserved

The committed result is sanitized. The repository does not include:

- `eval/expected-paths.json`;
- fixed parsed Groq output rows;
- raw expected-path rows;
- expected answers;
- reference trajectories;
- evaluator-only labels;
- API keys or secrets;
- LOCKED_TEST labels or cases.

## Next gate

Use E9 findings to improve the candidate on DEV only:

1. improve prompt/tool policy to require explicit evidence references before a decision;
2. strengthen evidence acquisition from expected required paths without exposing private oracle text;
3. improve action/escalation calibration;
4. rerun fixed Groq output capture;
5. rerun E9 private scorer;
6. do not tune on VALIDATION;
7. do not access LOCKED_TEST;
8. do not freeze final architecture yet.
