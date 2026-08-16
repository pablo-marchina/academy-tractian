# E9 Evaluator-Side Task-Quality Scorer Results

**Status:** E9_SCORER_CONTRACT_PASS_PRIVATE_ORACLE_OR_OUTPUTS_REQUIRED  
**Date:** 2026-08-16  
**Leading model candidate:** Groq `llama-3.1-8b-instant`  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## What was implemented

E9 adds `scripts/research/e9_evaluator_side_scorer.py`, an evaluator-side scorer that runs after model generation. It can consume fixed Groq E8 outputs, load private DEV/VALIDATION oracles locally, and compute real task-quality metrics without ever putting private gold into the model prompt.

The scorer supports two modes:

1. **Contract/public CI mode**
   - consumes the public sanitized Groq E8 result summary when available;
   - validates split/LOCKED_TEST boundaries;
   - validates the scorer/oracle separation contract;
   - does not claim semantic task-quality when private oracles or parsed model outputs are absent.

2. **Private/local score mode**
   - consumes fixed model outputs with parsed JSON outputs;
   - loads private DEV/VALIDATION oracle data only inside the scorer;
   - scores model outputs after output hashes are fixed;
   - reports real task-quality metrics and proxy-vs-real disagreement.

## Boundary rule

The model must never see:

- expected answers;
- reference trajectories;
- private scoring labels;
- evaluator-only gold;
- `eval/expected-paths.json`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST cases or labels.

The scorer may read private DEV/VALIDATION oracle material only after outputs are fixed and hashed.

## Metrics implemented

The scorer reports:

| Metric | Implemented |
|---|---:|
| Real task-quality score | yes, private mode |
| Decision-class correctness | yes |
| Evidence-plan correctness | yes |
| Required evidence coverage | yes |
| Action correctness | yes |
| Escalation correctness | yes |
| Premature action rate | yes |
| Unsupported final-claim rate | yes |
| Proxy success rate | yes |
| Proxy-vs-real disagreement | yes |
| LOCKED_TEST access flag | yes |

## Current public result

The public repository cannot store private oracles, and the sanitized Groq E8 summary should not be treated as semantic task-quality evidence if it contains only hashes and aggregate metrics. Therefore the public result is a scorer-contract pass, not a final model-quality pass:

```text
E9_SCORER_CONTRACT_PASS_PRIVATE_ORACLE_OR_OUTPUTS_REQUIRED
```

This is intentional. It avoids the common benchmark error of either leaking gold into prompts or pretending that proxy/schema metrics are real task-quality metrics.

## Private/local command

After producing a fixed Groq output file that includes parsed model outputs, run:

```powershell
python scripts/research/e9_evaluator_side_scorer.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --fixed-output-file "<fixed-groq-output-with-parsed-model-outputs.json>" `
  --oracle-file "<private-dev-validation-oracle.json>" `
  --out "$env:TEMP\e9-private-task-quality-summary.json" `
  --include-rows
```

The private oracle file must contain only DEV/VALIDATION material. Any LOCKED_TEST path or LOCKED_TEST row remains forbidden before final evaluation.

## Constants preserved

- B3 guarded boundary.
- Evidence-sufficiency policy.
- Adaptive evidence planning.
- LangGraph current runtime candidate.
- HarnessRunner execution boundary.
- HttpxTransport live API path.
- Native ToolSpec internal default.
- MCP-compatible adapter as optional external interoperability surface.
- Groq as current leading free-provider candidate.
- OpenAI/Anthropic disabled.
- Final architecture not frozen.

## Next step

Run the scorer locally against fixed parsed Groq outputs and private DEV/VALIDATION oracles, then record only a sanitized aggregate summary in the repo. Do not commit private oracle files or raw secrets.
