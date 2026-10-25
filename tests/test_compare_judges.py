"""Running several judges on the human-graded sample and scoring them (no API calls)."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from compare_judges import run_judge, summarize


class FakeJudge:
    def __init__(self, label="correct", grounded="supported"):
        self.calls = 0
        self.label, self.grounded_label = label, grounded

    def correctness(self, question, gold, accepted, answerable, predicted):
        self.calls += 1
        return SimpleNamespace(label=self.label, explanation="e", cost_usd=0.002, latency_ms=100.0)

    def grounded(self, question, predicted, notes):
        self.calls += 1
        return SimpleNamespace(label=self.grounded_label, explanation="e", cost_usd=0.001,
                               latency_ms=50.0)


def task(n):
    return {"n": n, "question": f"Q{n}?", "gold": "g", "accepted": ["g"], "answerable": True,
            "predicted": "g", "notes": []}


def test_run_judge_writes_each_grade_and_resumes_without_paying_twice(tmp_path):
    cache = tmp_path / "judges.jsonl"
    judge = FakeJudge()
    rows = run_judge("fake", judge, [task(1), task(2)], cache)
    assert judge.calls == 4 and len(rows) == 2
    assert rows[0] == {"judge": "fake", "n": 1, "correctness": "correct", "grounded": "supported",
                       "cost_usd": 0.003, "latency_ms": 150.0}
    again = FakeJudge()
    rows = run_judge("fake", again, [task(1), task(2), task(3)], cache)
    assert again.calls == 2 and [r["n"] for r in rows] == [1, 2, 3]
    assert len(cache.read_text().splitlines()) == 3


def test_run_judge_records_a_failed_call_as_an_error_and_retries_it_later(tmp_path):
    class Broken(FakeJudge):
        def grounded(self, *a):
            raise RuntimeError("503")
    cache = tmp_path / "judges.jsonl"
    rows = run_judge("b", Broken(), [task(1)], cache)
    assert rows[0]["grounded"] == "error"
    assert json.loads(cache.read_text())["grounded"] == "error"
    fixed = FakeJudge()
    rows = run_judge("b", fixed, [task(1)], cache)
    assert fixed.calls == 2 and rows[0]["grounded"] == "supported"


def test_summarize_scores_each_judge_against_the_human():
    human = {1: ("correct", "supported"), 2: ("hedged", "unsupported"),
             3: ("incorrect", "unsupported"), 4: ("correct", "supported")}
    rows = [
        {"judge": "a", "n": 1, "correctness": "correct", "grounded": "supported", "cost_usd": 0.01, "latency_ms": 100},
        {"judge": "a", "n": 2, "correctness": "incorrect", "grounded": "unsupported", "cost_usd": 0.01, "latency_ms": 300},
        {"judge": "a", "n": 3, "correctness": "incorrect", "grounded": "supported", "cost_usd": 0.01, "latency_ms": 200},
        {"judge": "a", "n": 4, "correctness": "correct", "grounded": "error", "cost_usd": 0.01, "latency_ms": 200},
    ]
    (s,) = summarize(rows, human)
    assert s["judge"] == "a" and s["n"] == 4
    assert s["correctness_agree"] == pytest.approx(3 / 4)
    assert s["counts_as_correct_agree"] == 1.0
    assert s["grounded_n"] == 3  # the error is left out
    assert s["grounded_agree"] == pytest.approx(2 / 3)
    assert s["cost_per_grade"] == pytest.approx(0.005)  # two checks per run
    assert s["latency_per_grade_ms"] == pytest.approx(100)
