# Architecture Decision Records

Material decisions are governed by [`../PROJECT-PRINCIPLES.md`](../PROJECT-PRINCIPLES.md). Current architecture is summarized in [`../ARCHITECTURE.md`](../ARCHITECTURE.md); current state/authorization is owned only by [`../CURRENT-PROJECT-STATUS.md`](../CURRENT-PROJECT-STATUS.md).

An ADR records the decision **for its stated scope at that time**. Later evidence may supersede or narrow it, but old ADRs are never rewritten to make history look consistent.

## Index

| ADR | Scope | Current interpretation |
|---|---|---|
| [`000`](000-template.md) | template | use for future material decisions |
| [`001`](001-provider-capacity-serving-path-2026-08-24.md) | Cerebras P12-C4 qualification | historical/consumed qualification route |
| [`002`](002-openrouter-no-card-serving-amendment-2026-08-26.md) | OpenRouter P12-C4 amendment | historical/consumed |
| [`003`](003-nvidia-nim-no-card-serving-amendment-2026-08-26.md) | NVIDIA NIM P12-C4 amendment | qualification evidence only; not production provider selection |
| [`004`](004-agent-controller-runtime-2026-08-27.md) | agent controller/runtime | accepted single-agent controller; `HarnessRunner` exclusive tool boundary |
| [`005`](005-production-action-safety-policy-2026-08-27.md) | consequential-action safety | accepted layered safety; default production actions disabled |
| [`006`](006-provider-neutral-decision-source-2026-08-27.md) | provider-neutral decision source | accepted provider adapter boundary |
| [`007`](007-model-call-trace-provenance-2026-08-27.md) | model-call provenance | accepted sanitized provenance contract |
| [`008`](008-provider-model-comparison-design-2026-08-28.md) | OpenAI/Gemini comparison design | historical; superseded prospectively by Cloudflare USD0 path |
| [`009`](009-provider-http-clients-live-comparison-authorization-2026-08-28.md) | historical OpenAI/Gemini clients | historical implementation; not current execution route |
| [`010`](010-provider-comparison-executor-2026-08-28.md) | provider comparison executor | reusable concepts; historical candidate route superseded |
| [`011`](011-governed-live-provider-execution-wrapper-2026-08-28.md) | governed live wrapper | historical provider execution/custody boundary |
| [`012`](012-controlled-action-execution-profile-2026-08-28.md) | controlled action profile | accepted supplied/test action demonstration only |
| [`013`](013-provider-free-failure-performance-campaign-2026-08-28.md) | EV-007 failure performance | frozen provider-free reliability evidence |
| [`014`](014-provider-free-repeated-run-stability-2026-08-28.md) | EV-008 stability | frozen repeated-run evidence |
| [`015`](015-provider-free-customer-safe-communication-2026-08-28.md) | EV-011 communication | frozen customer-safe communication evidence |
| [`016`](016-provider-free-final-delivery-reproduction-evidence-package-2026-08-28.md) | provider-free reproduction | frozen clean reproduction evidence |
| [`017`](017-final-handoff-acceptance-audit-2026-08-28.md) | August 28 final handoff audit | historical 83-row handoff state; documentation pins relocated prospectively by ADR-028 |
| [`018`](018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md) | Cloudflare D01 preregistration | frozen D01 scientific packet |
| [`019`](019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md) | Cloudflare client | frozen/provider-free implementation foundation |
| [`020`](020-cloudflare-executor-custody-v2-provider-free-implementation-2026-09-01.md) | Cloudflare executor/custody v2 | governed custody/write-ahead execution foundation |
| [`021`](021-cloudflare-live-execution-authorization-protocol-2026-09-01.md) | Cloudflare live authorization | historical authorization protocol foundation |
| [`022`](022-cloudflare-reset-window-neuron-evidence-amendment-2026-09-01.md) | reset-window Neuron evidence | accepted amendment for free-allocation evidence |
| [`023`](023-cloudflare-governed-live-entrypoint-contract-2026-09-01.md) | governed live entrypoint | accepted minimal launcher composition |
| [`024`](024-cloudflare-same-day-zero-use-neuron-evidence-amendment-2026-09-01.md) | same-day zero-use evidence | accepted free-capacity amendment |
| [`025`](025-cloudflare-operator-attestation-source-amendment-2026-09-02.md) | operator-attestation evidence | accepted screenshot-free account-state evidence source |
| [`026`](026-cloudflare-d02-completion-budget-amendment-2026-09-02.md) | D02 1024 completion-budget diagnostic | accepted prospective D02 experiment amendment |
| [`027-A`](027-cloudflare-d02-fresh-reset-live-authorization-2026-09-02.md) | D02 fresh-reset authorization | historical numbering collision; preserve exact filename/record |
| [`027-B`](027-cloudflare-d02-governed-live-authorization-2026-09-02.md) | D02 governed live authorization | historical numbering collision; preserve exact filename/record |
| [`028`](028-historical-handoff-documentation-relocation-2026-09-02.md) | ADR-017 documentation-pin relocation | accepted: preserve v1 bytes in immutable archive; active docs remain current until final freeze |

The duplicated `027` number is retained rather than renumbered because both records are already historical artifacts. Future ADRs continue from 028+ without rewriting those filenames.

## Lifecycle rule

Use labels such as `ACTIVE`, `FROZEN`, `HISTORICAL`, `SUPERSEDED` or `CONSUMED` in current navigation when useful, but do not alter an old ADR's original decision text solely to reflect later state.

## Future ADR checklist

A material ADR should include or link to:

1. decision question/scope;
2. requirement/risk mapping;
3. hard constraints;
4. credible alternatives + simple baseline;
5. comparison/preregistration where applicable;
6. quantitative/repeated results;
7. robustness/failure evidence;
8. production-fit trade-offs;
9. decision and non-claims;
10. reversal triggers;
11. regression obligations.
