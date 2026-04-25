# Task Plan - Pro-Grade RAG Implementation

## Goal
Transform the basic RAG into a robust Hybrid RAG system (Vector + Lexical) with Query Rewriting (HyDE) and optimized chunking.

## Phases

### Phase 1: Database Upgrade (Hybrid Search)
- [ ] Update `VectorDB` to initialize an FTS5 table alongside the vector table.
- [ ] Implement `insert_hybrid` to populate both FTS5 and Vector indices.
- [ ] Implement `search_hybrid` using Reciprocal Rank Fusion (RRF).

### Phase 2: Orchestration Upgrade (HyDE)
- [ ] Add `query_rewriter_node` in `orchestrator.py` to generate expanded queries/hypothetical answers.
- [ ] Update `rag_node` to use the rewritten query for hybrid retrieval.

### Phase 3: Chunking Strategy Optimization
- [ ] Update `chunker.py` to support `overlap` (e.g., 10-20%) to prevent loss of context at boundaries.
- [ ] Implement Header-aware chunking for Markdown files.

### Phase 4: Validation & Benchmarking
- [ ] Use the GraphCast "trick questions" as a benchmark.
- [ ] Compare "Pure Vector" vs "Hybrid" performance.

## Decisions
| Decision | Rationale |
|----------|-----------|
| SQLite FTS5 | Native, low overhead, perfectly compatible with the existing SQLite-vec stack. |
| RRF (Reciprocal Rank Fusion) | Robust way to combine lexical and semantic ranks without requiring normalized scores. |
| HyDE | Helps when user queries are short or use different terminology than the documentation. |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| | | |
