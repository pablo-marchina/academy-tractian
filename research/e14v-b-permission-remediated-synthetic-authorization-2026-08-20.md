# E14v-B permission-remediated synthetic authorization — 2026-08-20

E14v-B is the provider-permission-remediation-only continuation of the E14v-A public synthetic qualification. The scientific planner candidate and E14v-A transport contract remain unchanged.

## External remediation

Manual confirmation was received on 2026-08-20 that `openai/gpt-oss-120b` is allowed at the relevant Groq organization/project permission layers.

The prior E14v-A attempt remains consumed and preserved. Its aggregate diagnostic was 14/14 HTTP 403 provider errors with zero valid route-contract rows, so it remains operationally invalid for planner-quality qualification.

## Final structural gate

```text
workflow   research-e14v-b-provider-permission-remediation
run_id     32373474815
job_id     96439178694
conclusion success
```

All steps passed:

- compile E14v-B wrapper;
- E14v-B self-check;
- zero-provider synthetic dry-run;
- active amendment-boundary verification;
- verification that E14v-A `_provider_call_amended` is reused rather than reimplemented;
- forbidden private-selector scan.

A prior post-activation run failed only because the wrapper still accepted the pre-activation manifest status; that state-machine assertion was corrected without changing model, prompt, fixture, thresholds, route catalog, provider, response schema, retry policy, pacing, temperature, reasoning effort, or transport implementation.

## Authorization

Exactly one real-provider E14v-B **public synthetic qualification** attempt is authorized using a new output path and a new attempt lock. E14v and E14v-A outputs/locks must remain untouched.

Real DEV, VALIDATION, and LOCKED_TEST remain blocked. If E14v-B synthetic passes, the aggregate PASS must be recorded before explicitly activating one real DEV planner attempt. If it fails, preserve the lock and do not run DEV or inspect private rows.
