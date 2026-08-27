# Retrieval / RAG Decision Method — Wave 2

Status: **CONDITIONAL TECHNIQUE — no RAG stack selected**

Research questions: R07 (evidence), R12/R20 (retrieval/RAG)

## 1. Research conclusion

RAG is not a project requirement. The TAPI explicitly presents RAG, hybrid search and reranking as optional complements when they contribute to the experiment. Therefore the default architecture should not contain a vector database merely because RAG is common in agent systems.

Retrieval enters `FROZEN-v1` only if the actual TRACTIAN knowledge resources create a retrieval problem that cannot be solved adequately through structured API access/direct lookup.

## 2. First question: is there a retrieval problem?

After Swagger/resources are provided, classify knowledge access into:

1. **Structured lookup** — exact entities/fields accessible by API identifiers/filters.
2. **Small bounded knowledge** — compact enough for deterministic/direct lookup or controlled context.
3. **Unstructured corpus** — documents/procedures/glossary needing semantic or lexical retrieval.
4. **Mixed evidence** — structured industrial state plus unstructured support knowledge.

Only categories 3–4 clearly justify a retrieval experiment.

## 3. Evidence from retrieval research

### BEIR

BEIR remains a useful heterogeneous retrieval benchmark reference. Its results show that sparse BM25 is a strong robust baseline and that denser/late-interaction or reranking methods can improve particular settings at additional computational complexity. The project should therefore retain a simple lexical baseline instead of assuming dense retrieval wins.

### RAGChecker

RAGChecker argues for diagnosing retrieval and generation components separately. This is important for our project: if an agent answer fails, we need to know whether required evidence was never retrieved or whether the model misused evidence that was available.

### Hybrid retrieval evidence

Published work such as Blended RAG shows hybrid lexical+dense retrieval can improve some datasets. That is evidence to include hybrid retrieval as a candidate, not proof that it helps the TRACTIAN corpus.

## 4. Retrieval experiment ladder

If an unstructured corpus is present, test techniques incrementally:

```text
R0 structured API/direct lookup only
 ↓
R1 sparse lexical baseline (e.g. BM25)
 ↓
R2 dense retrieval
 ↓
R3 sparse + dense hybrid
 ↓
R4 hybrid + reranking ONLY if analysis shows ranking errors remain
```

Do not skip directly to R4.

At each step ask whether the added component provides a statistically/operationally meaningful gain in evidence recall or end-to-end agent quality relative to latency/resource complexity.

## 5. Canonical corpus and evidence units

Before selecting embeddings/vector storage, define what a retrievable unit actually is.

Potential units after corpus inspection:

- procedure section;
- glossary entry;
- model limitation/requirement;
- support instruction;
- asset-class knowledge;
- troubleshooting step.

Chunking should preserve semantically meaningful boundaries and metadata. Arbitrary fixed-token chunks are only a baseline.

Each evidence unit should carry provenance:

```yaml
evidence_id:
source_resource:
source_version:
section_or_record_id:
created_or_updated_at: null
entity_scope: null
permission_scope: null
text_or_content_ref:
```

## 6. Retrieval security and authorization

Retrieval cannot expand authority. Filtering by company/user/resource permission must occur before or as part of retrieval if the knowledge source is permissioned.

Never use an embedding/vector index that mixes resource scopes and relies on the LLM to ignore inaccessible results.

Retrieved natural-language content is data, not trusted system instruction; indirect prompt-injection tests apply to it.

## 7. Retrieval ground truth

For gold scenarios, identify required/acceptable evidence IDs or semantic evidence sets where feasible.

This allows component metrics such as:

- Recall@k of required evidence;
- Precision@k when gold relevance is sufficiently annotated;
- MRR for single/ordered relevant evidence;
- nDCG@k when graded relevance exists;
- retrieval latency;
- evidence duplication/diversity;
- permission-filter correctness.

Do not force nDCG/MRR if the gold structure does not support graded/ranked relevance.

## 8. End-to-end metrics

Retrieval only matters if it improves the agent. Pair component metrics with:

- final task/state success;
- unsupported-claim rate;
- evidence coverage;
- correct conflict handling;
- tool-call count;
- tokens/context size;
- latency;
- robust success under partial/conflicting evidence.

A retrieval method with higher Recall@k but no task benefit and substantially more overhead may be rejected.

## 9. Dense embedding selection rule

If dense retrieval enters the experiment, do not select an embedding model solely from generic leaderboard rank.

Shortlist models by:

- accessible/local/free serving;
- language coverage needed by corpus/user requests;
- embedding dimension/resource cost;
- licensing;
- official/documented availability;
- retrieval performance on a **project-specific labeled query/evidence set**.

Then select empirically.

## 10. Reranking gate

A reranker is justified only when error analysis shows:

- relevant evidence appears in a larger candidate set but is ranked too low;
- the retrieval candidate set has enough recall to make reranking useful;
- added latency/compute is acceptable.

If required evidence is absent from the initial candidate pool, reranking cannot solve the root problem.

## 11. Query strategy experiment

If retrieval is needed, compare at least:

- raw user query;
- task-aware/structured query derived from known entities;
- optional query expansion only if necessary.

Avoid letting free-form query rewriting silently hallucinate entity IDs or authorization scope.

## 12. Evidence acquisition vs retrieval

The agent may need two qualitatively different evidence channels:

```text
STRUCTURED, CURRENT STATE
  → industrial API tools

PROCEDURAL / EXPLANATORY KNOWLEDGE
  → direct knowledge endpoint or retrieval layer
```

Do not put live mutable state into a RAG index when the API can provide fresher authoritative data directly.

## 13. Stopping and adaptive retrieval

If retrieval is used, the agent should not always retrieve a fixed large `k`. Candidate experiment:

A. fixed retrieval budget;

B. adaptive retrieval when required evidence is missing/ambiguous;

C. evidence-driven stop when required fields/provenance are sufficient.

The adaptive policy must be based on observable evidence state, not vague self-confidence alone.

## 14. Storage/backend decision comes last

Vector/search backend selection is downstream of retrieval strategy.

Do not choose Qdrant/FAISS/pgvector/Elasticsearch/etc. before we know:

- corpus size;
- sparse/dense/hybrid need;
- persistence requirement;
- metadata-filtering requirement;
- local resource budget;
- whether vector search is needed at all.

## 15. Decision criteria

RAG enters `FROZEN-v1` only if all are true:

1. an actual unstructured/mixed knowledge retrieval need exists;
2. direct/structured baseline is insufficient;
3. retrieval has project-specific labeled evaluation;
4. chosen strategy improves evidence/task metrics;
5. permission/provenance semantics are preserved;
6. latency/resource cost is justified;
7. added complexity is reproducible within the deadline.

## 16. Open dependency

This research cannot close until we inspect the actual TRACTIAN knowledge resources/corpus and endpoint semantics. Until then the correct status is **RAG: conditional, not selected**.
