# Progress 034 — systematic decision revalidation governance

**Date:** 2026-08-28 09:17 BRT  
**Change class:** planning/governance only  
**Scientific state changed:** NO  
**Provider/model calls executed:** 0  
**Credential/account probes:** 0  
**Real customer mutations:** 0

## Why this checkpoint exists

The project principles already required systematic comparison and stated that passing a gate proves qualification rather than optimality. A review of the current state found two prospective inconsistencies:

1. the short-horizon plan had narrowed future work to submission/review hygiene despite the global architecture still being explicitly unfrozen and several material choices not having broad comparative evidence;
2. the frozen ADR-008 live provider packet included OpenAI GPT-5.6 Sol even though the project had historical USD 0/free-provider constraints and the user reaffirmed that the project must remain free.

This checkpoint corrects the **prospective planning interpretation** without rewriting any historical ADR, experiment or freeze.

## Governance changes

From this checkpoint forward:

- every material development cycle updates plans/decision inventory before implementation;
- a decision question, hard constraints, alternatives, preregistered comparison, robustness/production-fit plan and reversal triggers are required before material code changes;
- external API/hosted-service project cost is a USD 0 hard constraint;
- historical freezes remain immutable evidence but may be prospectively revalidated/superseded when an assumption changes or a credible alternative was omitted;
- final architecture remains unfrozen until all applicable material choices are reviewed under the new operational revalidation plan.

## Provider/model consequence

The old ADR-008/#44 OpenAI Sol × Gemini Flash live packet is suspended before attempt 0.

```text
old live calls consumed      0 / 32
first live attempt            NO
production provider selected  NO
```

A prospective zero-cost provider-comparison amendment is required before any live provider execution.

Minimum discovery scope starts with Gemini, Groq, OpenRouter explicitly free routes, Cloudflare Workers AI free-tier candidates, a feasible local/open-weight baseline and any other materially distinct current zero-cost provider found by primary-source research.

User-reported operational context only:

```text
Groq API     connected
Gemini API   pending user connection
```

No secret/account probe was performed to verify either statement.

## Architecture consequence

The existing single-agent explicit controller remains the tested simple baseline but is no longer interpreted as the final topology without comparison. At minimum, prospectively compare it against planner→executor and agent→critic/reviewer patterns when feasible, holding provider/model, task distribution, ToolSpecs, HarnessRunner, safety and evaluator definitions controlled.

Other material decisions — runtime/orchestration, adaptive policies, retrieval, memory, evaluator scope, observability, deployment and UI — enter systematic screening/revalidation before final freeze.

Native typed tools vs MCP retains comparatively strong historical evidence and stays provisional unless current research changes the trade-off.

## C4 consequence

No scientific authorization changed.

The current reporting gate remains blocked on the exact original score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
```

Exact recovery search is the first action. Reconstruction/rescoring/substitution remains unauthorized. If exact bytes are unavailable, any byte-identical recovery attempt must first receive a separate prospective scientific amendment; mismatched bytes cannot substitute for the original artifact.

## Documentation changed

- `docs/PROJECT-PRINCIPLES.md`;
- `docs/DECISION-REVALIDATION-MASTER-PLAN.md`;
- `docs/PROJECT-PLAN.md`;
- `docs/ARCHITECTURE-ROADMAP.md`;
- `docs/CURRENT-PROJECT-STATUS.md`;
- `docs/NEXT-STEPS.md`;
- this progress entry;
- machine checkpoint `research/results/project-progress-checkpoint-2026-08-28-0917-brt.json`.

## Next action after this planning change is merged

Do not start implementation immediately. First perform current primary-source research, finalize the decision inventory, and preregister the prospective zero-cost provider comparison and first topology comparison. Only then may their corresponding implementation/experiments begin.
