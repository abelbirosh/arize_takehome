"""Re-judging one question's runs after its accepted answers change (no API calls)."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from regrade import regrade


class FakeJudge:
    def __init__(self):
        self.seen = []

    def correctness(self, question, gold, accepted, answerable, predicted):
        self.seen.append(accepted)
        return SimpleNamespace(label="correct", explanation="now accepted", cost_usd=0.001)


def test_regrade_rejudges_only_that_question_with_the_new_variants():
    rows = [{"id": "q1", "question": "Q1?", "answer": "9", "judge": {"label": "incorrect"}},
            {"id": "q2", "question": "Q2?", "answer": "x", "judge": {"label": "incorrect"}}]
    suite = {"q1": {"answer": "11", "accepted": ["11", "9"], "answerable": True}}
    judge = FakeJudge()
    changed = regrade(rows, "q1", suite, judge)
    assert judge.seen == [["11", "9"]]
    assert rows[0]["judge"] == {"label": "correct", "explanation": "now accepted",
                                "cost_usd": 0.001}
    assert rows[1]["judge"]["label"] == "incorrect"
    assert changed == [("q1", "incorrect", "correct")]
