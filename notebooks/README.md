# Capstone notebook

`capstone_pipeline.ipynb` contains the final end-to-end implementation developed for the 2026 AICOSS–THU capstone:

1. configuration and document definitions;
2. Markdown tree construction and StructureAgent v2;
3. Mistral, embedding, and ChromaDB adapters;
4. bottom-up summarization;
5. ten retrieval tools and single-agent loop;
6. planner/searcher/synthesizer and adaptive routing;
7. indexing and evaluation;
8. benchmark visualization cells.

Notebook outputs and execution counts are cleared. Configure credentials through environment variables and keep local documents under an ignored data directory.

The notebook expects the hierarchical Docling postprocessor used in the original THU/DASU environment. The package name appears as `hierarchical` in the import cell; obtain the corresponding `docling-hierarchical-pdf` implementation through its authorized distribution channel.
