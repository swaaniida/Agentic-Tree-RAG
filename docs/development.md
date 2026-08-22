# Development lineage

## Problem framing

The capstone began with MapReduce and refine-style summarization for documents larger than an LLM context window. The central limitation appeared in exhaustive questions: a summary or top-k retriever could answer individual facts but could not guarantee that every repeated document unit had been visited.

## Iteration sequence

| Date | Development step |
|---|---|
| 2026-02-09 | Compared MapReduce, refine, and RAPTOR approaches for long documents |
| 2026-02-10 | Introduced a tree representation to preserve document-wide coverage |
| 2026-02-11 | Added query classification and decomposition into search-friendly subquestions |
| 2026-02-12 | Added agent-guided node grouping, hierarchical traversal, benchmark runs, and presentation diagrams |
| 2026-02-13 | Completed and presented the capstone pipeline at DASU/THU |

## Implementation stages found in the project material

### 1. Flat FAISS RAG

The earliest modular version parses PDFs with `pypdf`, creates overlapping chunks, embeds them, and stores vectors in FAISS with SQLite metadata. It includes citations and an answer verifier but still depends on top-k retrieval.

### 2. Retrieval compression studies

Four document representations were compared in a separate prototype:

- baseline text;
- structure-based pruning;
- embedding-based pruning;
- LLM condensation.

This stage established that reducing context could lower latency, but flat retrieval still struggled with list completeness.

### 3. RAPTOR-style prototype

A hierarchical prototype grouped leaf chunks into parent nodes, embedded summaries, and traversed the tree with a beam-style query router. It exposed a second problem: a tree built from damaged PDF headings preserves the damage.

### 4. StructureAgent v2

The final notebook moved structural repair ahead of indexing. An LLM proposes a restructuring plan from the heading digest; deterministic code then detects repeated boundaries, flattens container nodes, and rebuilds the main units. Bottom-up summaries and section/leaf embeddings are created only after repair.

### 5. Query-dependent agents

The final agent distinguishes local fact retrieval from enumeration and cross-section questions. Enumeration uses complete traversal tools, while complex questions can use planner, searcher, and synthesizer roles. A final verifier checks list coverage, numeric accuracy, and ordering.

## Public repository selection

The final notebook is the reference implementation because it is the only artifact containing StructureAgent v2, the ten-tool interface, adaptive routing, and the evaluation runner in one pipeline. Earlier codebases are described here but are not copied into the public source tree; mixing their incompatible storage and retrieval layers would make the repository harder to run and audit.

The three largest complete result files are retained. Duplicate exports and short pilot runs are excluded from the headline analysis. All reported aggregate values are recomputed from the shared 107-question intersection.
