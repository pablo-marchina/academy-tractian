# E10 DEV-only Quality Improvement Loop

**Status:** READY_FOR_LOCAL_DEV_ONLY_ITERATION  
**Date:** 2026-08-16  
**Purpose:** improve evidence grounding and action/escalation calibration using DEV only  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Starting point

E9 private/local scoring produced a real scorer execution pass but exposed a major gap between proxy/schema success and real task quality:

| Metric | E9 baseline |
|---|---:|
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

Interpretation: E8 proved Groq can return valid JSON under zero-cost constraints, but E9 showed that current answer quality is not good enough. The largest failure is not benchmark leakage; it is weak evidence grounding and poor action/escalation calibration.

## E10 rules

E10 is a DEV-only loop:

1. tune only on DEV groups: `asset_G501`, `asset_C710`, `asset_S420`;
2. do not inspect or optimize against VALIDATION rows;
3. do not access LOCKED_TEST;
4. do not put `eval/expected-paths.json` or expected-path text into prompts;
5. capture fixed Groq outputs locally;
6. score locally with E9 v3 and private expected paths;
7. commit only sanitized aggregate findings.

## Candidate policy change

E10 adds an evidence-first prompt/policy layer:

- evidence plans must name concrete API/resource evidence;
- decisions should remain `investigate_only` or `insufficient_evidence` when evidence is incomplete;
- actions require a concrete supported endpoint and visible evidence;
- escalations require safety, severe fault, unresolved ambiguity, permission issue, or specialist-needed uncertainty;
- no raw expected-path values are used in model prompts.

## DEV-only capture command

```powershell
cd "C:\Users\Inteli\Documents\Projetos\academy-tractian"
git checkout research/systematic-foundation
git pull
$env:PYTHONPATH = "."

$TRACTIAN_PACKAGE = "C:\Users\Inteli\Documents\Projetos\academy-tractian\inteli-tractian-project\inteli-tractian-project"

$env:GROQ_API_KEY = "SUA_CHAVE_GROQ_AQUI"
$env:E8_ENABLE_GROQ = "1"
$env:E8_CONFIRM_ZERO_COST = "1"
$env:E8_GROQ_MODEL = "llama-3.1-8b-instant"
$env:E8_MODEL_TEMPERATURE = "0"
$env:E8_MAX_OUTPUT_TOKENS = "600"
$env:E8_PROVIDER_MAX_ATTEMPTS = "5"
$env:E8_PROVIDER_RETRY_BASE_SECONDS = "5"
$env:E8_BETWEEN_CALL_DELAY_SECONDS = "8"
$env:E8_HTTP_USER_AGENT = "academy-tractian-e10-dev-quality/1.0"

python scripts/research/e10_dev_only_groq_quality_capture.py `
  --manifest research/experiments/e10-dev-only-quality-improvement-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --agent-input-cases "$TRACTIAN_PACKAGE\agent-input\cases.json" `
  --timeout-seconds 90 `
  --out "$env:TEMP\e10-dev-only-groq-quality-capture.json"

Get-Content "$env:TEMP\e10-dev-only-groq-quality-capture.json"
```

Expected capture shape:

```json
{
  "status": "E10_DEV_ONLY_GROQ_QUALITY_CAPTURE_PASS",
  "total_calls": 6,
  "parsed_model_outputs_available": 6,
  "validation_ran": false
}
```

## DEV-only E9 scoring command

```powershell
$PRIVATE_ORACLE = "$TRACTIAN_PACKAGE\eval\expected-paths.json"

python scripts/research/e9_evaluator_side_scorer_v3.py `
  --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json `
  --split-manifest research/frozen/benchmark-split-v1.json `
  --fixed-output-file "$env:TEMP\e10-dev-only-groq-quality-capture.json" `
  --oracle-file $PRIVATE_ORACLE `
  --out "$env:TEMP\e10-dev-only-e9-private-score.json" `
  --include-rows

Get-Content "$env:TEMP\e10-dev-only-e9-private-score.json"
```

Interpret only DEV rows. Do not use VALIDATION for prompt/policy tuning.

## Advancement rule

A DEV candidate may advance to a frozen candidate only if the DEV-only E9 v3 result improves real task quality without violating safety invariants:

- DEV real task quality increases;
- DEV evidence correctness increases;
- DEV action/escalation correctness improves or does not regress materially;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains blocked.

Only after a DEV candidate is selected should a fresh full fixed-output capture and private E9 score be run over DEV + VALIDATION for measurement. VALIDATION metrics must not be used for iterative tuning.
