from pathlib import Path
import tempfile
import unittest

from agentic_tree_rag.benchmark import load_runs, paired_keys, summarize_paired


HEADER = "dataset,question_id,category,f1_score,precision,recall,evidence_accuracy,latency,llm_score\n"


class BenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, rows: str) -> Path:
        path = self.root / name
        path.write_text(HEADER + rows, encoding="utf-8")
        return path

    def test_summary_uses_only_shared_questions(self) -> None:
        first = self.write("first.csv", "d,q1,A,0.2,0.3,0.4,True,10,\nd,q2,B,0.8,0.7,0.6,False,20,\n")
        second = self.write("second.csv", "d,q1,A,0.6,0.5,0.4,True,5,4\n")
        runs = load_runs({"first": first, "second": second})
        self.assertEqual(paired_keys(runs), {("d", "q1", "A")})
        summary = summarize_paired(runs)
        self.assertEqual(summary["paired_n"], 1)
        first_f1 = summary["runs"]["first"]["metrics"]["f1_score"]  # type: ignore[index]
        self.assertEqual(first_f1, {"mean": 0.2, "valid_n": 1})

    def test_invalid_numeric_cells_are_counted_as_missing(self) -> None:
        run = self.write("run.csv", "d,q1,A,ERROR,0.3,0.4,False,ERROR,\n")
        summary = summarize_paired(load_runs({"run": run}))
        f1 = summary["runs"]["run"]["metrics"]["f1_score"]  # type: ignore[index]
        self.assertEqual(f1, {"mean": None, "valid_n": 0})


if __name__ == "__main__":
    unittest.main()
