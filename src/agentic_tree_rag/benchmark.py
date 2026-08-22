from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
from statistics import mean
from typing import Iterable, Mapping


QuestionKey = tuple[str, str, str]
KEY_FIELDS = ("dataset", "question_id", "category")
NUMERIC_METRICS = ("f1_score", "precision", "recall", "latency", "llm_score")


def _key(row: Mapping[str, str]) -> QuestionKey:
    return tuple(row[field].strip() for field in KEY_FIELDS)  # type: ignore[return-value]


def _number(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_run(path: str | Path) -> dict[QuestionKey, dict[str, str]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    missing = [field for field in KEY_FIELDS if rows and field not in rows[0]]
    if missing:
        raise ValueError(f"missing key columns in {path}: {', '.join(missing)}")
    return {_key(row): row for row in rows}


def load_runs(paths: Mapping[str, str | Path]) -> dict[str, dict[QuestionKey, dict[str, str]]]:
    return {name: load_run(path) for name, path in paths.items()}


def paired_keys(runs: Mapping[str, Mapping[QuestionKey, object]]) -> set[QuestionKey]:
    if not runs:
        return set()
    return set.intersection(*(set(run) for run in runs.values()))


def _metric(rows: Iterable[Mapping[str, str]], field: str) -> tuple[float | None, int]:
    values = [_number(row.get(field)) for row in rows]
    valid = [value for value in values if value is not None]
    return (mean(valid), len(valid)) if valid else (None, 0)


def _evidence(rows: Iterable[Mapping[str, str]]) -> tuple[float | None, int]:
    values = [row.get("evidence_accuracy", "").strip().lower() for row in rows]
    valid = [value == "true" for value in values if value in {"true", "false"}]
    return (mean(valid), len(valid)) if valid else (None, 0)


def summarize_paired(
    runs: Mapping[str, Mapping[QuestionKey, Mapping[str, str]]],
) -> dict[str, object]:
    keys = paired_keys(runs)
    run_summaries: dict[str, dict[str, object]] = {}
    for run_name, run in runs.items():
        rows = [run[key] for key in keys]
        metrics: dict[str, object] = {}
        for field in NUMERIC_METRICS:
            value, count = _metric(rows, field)
            metrics[field] = {"mean": value, "valid_n": count}
        value, count = _evidence(rows)
        metrics["evidence_accuracy"] = {"mean": value, "valid_n": count}
        run_summaries[run_name] = {"n": len(rows), "metrics": metrics}

    return {
        "paired_n": len(keys),
        "datasets": dict(sorted(Counter(key[0] for key in keys).items())),
        "categories": dict(sorted(Counter(key[2] for key in keys).items())),
        "runs": run_summaries,
    }
