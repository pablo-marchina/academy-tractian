# Progress 037 — Provider Pre-Benchmark Factual Gates

**Date:** 2026-08-28

Closed the four no-inference provider facts required after the zero-cost provider refresh.

## Decisions

- Gemini Free Tier: public/synthetic evaluation payload is acceptable, but the general production provider request is `INELIGIBLE_BY_DEFAULT` because it may contain verbatim user requests/tool observation bodies and the current Free Tier uses content to improve Google products.
- Cloudflare minimum set: retain GLM 4.7 Flash + Nemotron 3 120B A12B; exclude Gemma 4 26B from the minimum first comparison.
- Groq: `HISTORICAL_CONTROL_ONLY`; no new live call justified by current evidence.
- Ollama: `qwen3:4b` is a spec-feasible local baseline; host performance remains unverified.

## D01

A precise evidence gap remains: no existing repository evidence selects between the retained production-eligible Cloudflare models on project-specific decision quality/reliability/latency.

Therefore minimum prospective comparison **preregistration is justified next**, but inference remains unauthorized until that packet is frozen.

## Boundaries

- provider/model inference calls: 0
- credential/account probes: 0
- real customer mutations: 0
- C4 state changed: no
- frozen historical evidence rewritten: no
- old ADR-008 execution authorized: no
