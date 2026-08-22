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

## Why `fixed_calls_consumed = 0` is expected with the public summary

The sanitized Groq E8 result stored in the repository does not include the full `calls[*].parsed_output` rows. It intentionally preserves aggregate evidence without committing parsed model outputs or private scoring material. Therefore, when E9 is run against only that public summary, the correct status is:

```text
E9_SCORER_CONTRACT_PASS_PRIVATE_ORACLE_OR_OUTPUTS_REQUIRED
```

and `fixed_calls_consumed` may be zero. This is not an E9 failure. It means the scorer needs a local/private fixed-output capture file.

## Added bridge for real E9 scoring

E9 now includes a local/private capture bridge:

```text
scripts/research/e8_capture_fixed_groq_outputs.py
research/69-e9-fixed-groq-output-capture-instructions.md
```

This bridge reruns the leading free Groq candidate, stores fixed parsed model outputs under `parsed_output`, hashes them, and produces the local file that E9 can score against private DEV/VALIDATION oracles. The generated capture file must not be committed.

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

First produce the fixed parsed Groq output file:

```powershell
python scripts/research/e8_capture_fixed_groq_outputs.py `
  --manifest research/experiments/e8-free-anywhere-real-candidate-run-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json"
```

Then run E9 with the private oracle file:

```powershell
python scripts/research/e9_evaluator_side_scorer.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --fixed-output-file "$env:TEMP\e8-fixed-groq-parsed-outputs-for-e9.json" `
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

Run the fixed-output capture locally, then run the scorer locally against fixed parsed Groq outputs and private DEV/VALIDATION oracles. Record only a sanitized aggregate summary in the repo. Do not commit private oracle files, parsed local run files, or raw secrets.
