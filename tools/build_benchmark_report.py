from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_tree_rag.benchmark import load_runs, paired_keys, summarize_paired  # noqa: E402


RUN_FILES = {
    "baseline": ROOT / "benchmarks/results/raw/baseline.csv",
    "optimized_v1": ROOT / "benchmarks/results/raw/optimized_v1.csv",
    "optimized_v2": ROOT / "benchmarks/results/raw/optimized_v2.csv",
}


def metric(summary: dict[str, object], run: str, name: str) -> tuple[float | None, int]:
    data = summary["runs"][run]["metrics"][name]  # type: ignore[index]
    return data["mean"], data["valid_n"]  # type: ignore[index,return-value]


def subset_runs(runs: dict, dataset: str) -> dict:
    return {
        name: {key: row for key, row in run.items() if key[0] == dataset}
        for name, run in runs.items()
    }


def write_tables(summary: dict[str, object], runs: dict) -> None:
    output_dir = ROOT / "benchmarks/results"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "paired_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with (output_dir / "paired_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["run", "paired_n", "f1", "precision", "recall", "evidence_accuracy", "latency_seconds", "llm_score"]
        )
        for run in RUN_FILES:
            writer.writerow(
                [
                    run,
                    summary["paired_n"],
                    metric(summary, run, "f1_score")[0],
                    metric(summary, run, "precision")[0],
                    metric(summary, run, "recall")[0],
                    metric(summary, run, "evidence_accuracy")[0],
                    metric(summary, run, "latency")[0],
                    metric(summary, run, "llm_score")[0],
                ]
            )

    datasets = sorted({key[0] for key in paired_keys(runs)})
    with (output_dir / "paired_by_dataset.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dataset", "run", "paired_n", "f1", "evidence_accuracy", "latency_seconds"])
        for dataset in datasets:
            current = summarize_paired(subset_runs(runs, dataset))
            for run in RUN_FILES:
                writer.writerow(
                    [
                        dataset,
                        run,
                        current["paired_n"],
                        metric(current, run, "f1_score")[0],
                        metric(current, run, "evidence_accuracy")[0],
                        metric(current, run, "latency")[0],
                    ]
                )


def plot(summary: dict[str, object], runs: dict) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    labels = list(RUN_FILES)
    colors = ["#4869a8", "#de7c36", "#4b9b78"]
    quality_metrics = ["f1_score", "precision", "recall", "evidence_accuracy"]
    quality_labels = ["F1", "Precision", "Recall", "Evidence accuracy"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.7), constrained_layout=True)
    x = np.arange(len(quality_metrics))
    width = 0.24
    for index, (run, color) in enumerate(zip(labels, colors)):
        values = [metric(summary, run, name)[0] or 0 for name in quality_metrics]
        axes[0].bar(x + (index - 1) * width, values, width, label=run, color=color)
    axes[0].set_title(f"Paired quality metrics (n={summary['paired_n']})")
    axes[0].set_xticks(x, quality_labels, rotation=18, ha="right")
    axes[0].set_ylim(0, 0.75)
    axes[0].set_ylabel("Score")
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y", alpha=0.25)

    latency = [metric(summary, run, "latency")[0] or 0 for run in labels]
    axes[1].bar(labels, latency, color=colors)
    axes[1].set_title("Mean latency on valid rows")
    axes[1].set_ylabel("Seconds")
    axes[1].tick_params(axis="x", rotation=18)
    axes[1].grid(axis="y", alpha=0.25)

    datasets = sorted({key[0] for key in paired_keys(runs)})
    short_names = {
        "ai_act_qa.json": "AI Act",
        "gen_ai_usecases_qa.json": "GenAI use cases",
        "national_parks_qa.json": "National parks",
    }
    x = np.arange(len(datasets))
    for index, (run, color) in enumerate(zip(labels, colors)):
        values = []
        for dataset in datasets:
            current = summarize_paired(subset_runs(runs, dataset))
            values.append(metric(current, run, "f1_score")[0] or 0)
        axes[2].bar(x + (index - 1) * width, values, width, label=run, color=color)
    axes[2].set_title("F1 by document set")
    axes[2].set_xticks(x, [short_names.get(name, name) for name in datasets], rotation=18, ha="right")
    axes[2].set_ylim(0, 0.5)
    axes[2].set_ylabel("F1")
    axes[2].grid(axis="y", alpha=0.25)

    fig.suptitle("Agentic Tree RAG benchmark — shared question set", fontsize=14, fontweight="bold")
    fig.savefig(ROOT / "assets/benchmark-comparison.png", dpi=180)
    plt.close(fig)


def main() -> None:
    runs = load_runs(RUN_FILES)
    summary = summarize_paired(runs)
    write_tables(summary, runs)
    plot(summary, runs)
    print(f"paired questions: {summary['paired_n']}")
    print("wrote benchmark tables and assets/benchmark-comparison.png")


if __name__ == "__main__":
    main()
