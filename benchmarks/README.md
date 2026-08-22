# Benchmark data

`questions/` contains the QA specifications used during the capstone. `results/raw/` contains the three complete recorded runs selected for paired analysis.

The source PDFs are not redistributed. To rerun the full notebook, provide local copies with the filenames configured in the notebook:

- `AI_Act.pdf`
- `Top_Generative_AI_Use_Cases_You_Should_Know_About_in_2025.pdf`
- `national-parks-of-europe.pdf`

The result schema contains dataset, question ID, category, latency, token usage, token-level F1/precision/recall, evidence accuracy, generated answer, and ground truth. Optimized runs also contain an LLM-judge score and reason.

Use `python tools/build_benchmark_report.py` to reproduce the paired 107-question summary. Invalid numeric cells such as `ERROR` are counted as missing and their valid sample counts are included in the report.
