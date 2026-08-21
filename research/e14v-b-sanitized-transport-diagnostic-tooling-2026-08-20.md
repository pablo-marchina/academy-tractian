# E14v-B sanitized transport diagnostic tooling — structurally qualified (2026-08-20)

The provider-free diagnostic required after the consumed E14v-B public synthetic attempt is now implemented and structurally qualified.

## Implementation

Added:

- `scripts/research/e14v_b_sanitized_transport_diagnostic.py`
- `.github/workflows/research-e14v-b-sanitized-transport-diagnostic.yml`

The diagnostic is specific to the consumed non-dry-run E14v-B artifact. Before aggregation it verifies the frozen E14v-B report identity, provider/model/reasoning configuration, 14-case count, provider-permission-remediation provenance, unchanged E14v-A transport provenance, and the unchanged scientific-candidate markers.

It reads only aggregate-safe fields from each row:

- provider error category;
- HTTP status;
- transport attempt count;
- route-contract validity/reason.

It does not read or print case IDs, selected reads, expected reads, raw model outputs, prompts, private oracle rows, private scorer rows, VALIDATION feedback, or LOCKED_TEST material. It makes no provider call and does not mutate the source artifact.

## Sanitized classification contract

The report classifies the fixed attempt into one of the following aggregate states:

- `PROVIDER_TRANSPORT_FAILURE` — HTTP/network/timeout operational failure;
- `PROVIDER_RESPONSE_CONTRACT_FAILURE` — provider response reached the client but failed JSON/response extraction;
- `PLANNER_OUTPUT_CONTRACT_FAILURE` — provider transport succeeded but the planner output failed the frozen route contract;
- `VALID_ROUTE_CONTRACT_OUTPUTS_PRESENT` — all 14 rows reached valid route-contract output;
- `MIXED_FAILURE_MODES`, `UNCLASSIFIED_FAILURE`, or `INVALID_DIAGNOSTIC_ARTIFACT` when a single clean classification is not justified.

The diagnostic separately reports whether an operational failure is established, whether a planner output-contract failure is established, and whether route quality is fully evaluable. It therefore does not interpret downstream zero route metrics as planner-quality evidence when no valid route-contract output exists.

## Structural validation

```text
commit     8174f32e754a56b1ef4625f0f82d885a4c53dff8
workflow   research-e14v-b-sanitized-transport-diagnostic
run_id     32439458215
job_id     96647059046
conclusion success
```

Passed checks:

- Python compilation;
- self-check for HTTP 403 transport failure;
- self-check for provider JSON/response-contract failure;
- self-check for planner route-contract failure;
- self-check for fully valid route-contract output;
- mixed-failure classification self-check;
- explicit leakage self-check proving source-only case/read markers are not propagated into the report;
- source boundary scan confirming no Groq/API/network call path exists in the diagnostic.

## Fixed-artifact execution remains pending

The consumed E14v-B fixed synthetic output is intentionally not committed, and the cited E14v-B structural workflow run contains no uploaded artifact. Therefore no real E14v-B transport classification is claimed by this checkpoint.

The next authorized local command is:

```bash
python scripts/research/e14v_b_sanitized_transport_diagnostic.py \
  --synthetic-output-file <fixed-e14v-b-output.json>
```

Only the sanitized JSON report from that command may be used to choose the next branch of the preregistered decision tree.

Until that report exists:

- E14v-B remains consumed and must not be rerun;
- no E14v-C operational/scientific amendment is justified yet;
- real E14v DEV remains blocked;
- VALIDATION remains blocked;
- LOCKED_TEST remains untouched/final-only.
