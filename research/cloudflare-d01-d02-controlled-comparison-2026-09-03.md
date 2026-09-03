# Cloudflare D01 → D02 controlled comparison — 2026-09-03

## Decision

**Result: `NO_SELECTION`.**

D02 completed the frozen one-shot packet successfully: 32/32 attempts, USD 0.00 actual cash cost, complete resource accounting, no raw provider material recorded, and no production-selection claim. Increasing the completion budget from 512 to 1024 tokens produced material improvements in several public quality metrics, but **neither candidate crossed the frozen M1, M4 and M7 hard gates**. The controlled change therefore does not justify a production provider selection.

This document records only accepted sanitized aggregate evidence. It does **not** reconstruct raw model material, credentials, account identifiers, private evaluator truth, or an unavailable 32-row attempt matrix.

## Experimental control

Frozen D02 plan SHA-256:

`e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958`

The material inferential change was:

```text
D01 max completion tokens   512
D02 max completion tokens  1024
```

D02 also retained the preregistered sanitized failure-subtype capture. Models, population, public rubric, safety gates, topology, repetition count and selection policy remained frozen by the D02 protocol.

## Packet-level result

| Metric | D01 | D02 | Delta |
| --- | ---: | ---: | ---: |
| completed attempts | 32/32 | 32/32 | 0 |
| actual cash cost | USD 0.00 | USD 0.00 | USD 0.00 |
| observed Neurons | 2813.628464 | 3344.130856 | +530.502392 (+18.85%) |
| completion cap | 512 | 1024 | +512 (+100%) |
| trace/raw-material policy | safe aggregate only | safe aggregate only | unchanged |
| selection | NO_SELECTION | NO_SELECTION | unchanged |
| production selection claim | false | false | unchanged |

## GLM 4.7 Flash

| Metric | D01 | D02 | Controlled delta |
| --- | ---: | ---: | ---: |
| structured decision adherence (M1) | 0.0000 | 0.4375 | +43.75 pp |
| public task quality (M4) | 0.0000 | 0.3750 | +37.50 pp |
| success rate (M7) | 0.0000 | 0.4375 | +43.75 pp |
| signature stability (M7) | 0.0000 | 0.2500 | +25.00 pp |
| safe failure behavior (M5) | 1.0000 | 1.0000 | 0 pp |
| trace integrity (M10) | 1.0000 | 1.0000 | 0 pp |
| median latency | 8959.5 ms | 15329.0 ms | +6369.5 ms (+71.09%) |
| p95 latency | 27395 ms | 38270 ms | +10875 ms (+39.70%) |
| observed Neurons | 450.3848 | 642.9772 | +192.5924 (+42.76%) |
| hard gate | FAIL M1/M4/M7 | FAIL M1/M4/M7 | no promotion |

Interpretation: the larger completion budget materially rescued structured/successful outputs from the D01 floor, but the gain came with substantially worse observed latency and higher resource use. Quality remained below all three frozen promotion gates.

## Nemotron 3 120B A12B

| Metric | D01 | D02 | Controlled delta |
| --- | ---: | ---: | ---: |
| structured decision adherence (M1) | 0.4375 | 0.5625 | +12.50 pp |
| public task quality (M4) | 0.3750 | 0.5625 | +18.75 pp |
| success rate (M7) | 0.4375 | 0.5625 | +12.50 pp |
| signature stability (M7) | 0.3750 | 0.5000 | +12.50 pp |
| safe failure behavior (M5) | 1.0000 | 1.0000 | 0 pp |
| trace integrity (M10) | 1.0000 | 1.0000 | 0 pp |
| median latency | 6214.0 ms | 4218.5 ms | -1995.5 ms (-32.11%) |
| p95 latency | 8857 ms | 9168 ms | +311 ms (+3.51%) |
| observed Neurons | 2363.243664 | 2701.153656 | +337.909992 (+14.30%) |
| hard gate | FAIL M1/M4/M7 | FAIL M1/M4/M7 | no promotion |

Interpretation: Nemotron improved all three quality/stability aggregates and median latency while using more Neurons. Its p95 latency was approximately flat/slightly worse. The candidate still failed every frozen quality/stability promotion gate, so the improvement is insufficient for production selection.

## What D02 establishes

D01 had a strong accepted censoring signal: 24/24 sanitized `CLIENT_FAILURE` attempts reached the exact 512-token completion ceiling. D02 shows that increasing the budget can recover meaningful public-rubric performance, especially for GLM, so the D01 floor was **not** clean evidence that the underlying provider/model architecture itself was incapable.

However, the accepted D02 aggregate result does not include the full 32-row failure-subtype matrix. Therefore this closeout does **not** claim a precise residual censoring rate at 1024 tokens. It only claims what the aggregate proves: performance improved, resource use increased, and both candidates still failed M1/M4/M7.

## EDD decision

The preregistered candidate change does not meet promotion criteria.

```text
candidate change    completion cap 512 → 1024
quality effect      positive but below hard gates
safety/trace        preserved at 1.0
resource effect     +18.85% packet Neurons
cash cost           unchanged at USD 0
selection effect    none
final decision      NO_SELECTION / REJECT production selection
```

No additional D02 replay is authorized. The governed 32-attempt packet is complete and all 32 attempts are consumed or accounted for.

## Evidence links inside the repository

- sanitized accepted D02 aggregate: `research/cloudflare-d02-live-result-2026-09-03.json`
- safe product registry: `src/academy_tractian/provider_experiments.py`
- D02 governed launcher: `scripts/research/execute_cloudflare_d02_live_comparison_operator_attestation_v1.py`
- D02 tracking issue: #117

## Next decision

Provider selection remains explicitly unresolved by this experiment. The project should move to the next evidence gate in the final excellence roadmap rather than spend additional free-tier budget on unpreregistered provider retries.
