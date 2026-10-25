"""Stratified sample of judged runs for blind human grading (no API calls)."""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from sample_validation import (
    QUOTAS,
    blind_rows,
    grader_payload,
    key_rows,
    sample,
    stratum,
    write_grading_csv,
)


def run(i: int, judge: str, grounded: str, qid: str | None = None, ctrl: str = "jev") -> dict:
    return {"controller": ctrl, "id": qid or f"q{i}", "category": "frames",
            "question": f"Question {i}?", "answer": f"answer {i}", "full_answer": "",
            "stats": {"forced_answer": False}, "steps": [],
            "notes": [{"title": "T", "url": "https://x", "facts": "- fact"}],
            "judge": {"label": judge, "explanation": "judge says"},
            "grounded": {"label": grounded, "explanation": "grounded says"}}


def population(per_stratum: int = 30) -> list[dict]:
    rows, i = [], 0
    for judge, grounded in QUOTAS:
        for _ in range(per_stratum):
            rows.append(run(i, judge, grounded, ctrl=["jev", "msft", "oai"][i % 3]))
            i += 1
    return rows


GOLD = {f"q{i}": {"answer": f"gold {i}", "accepted": [f"gold {i}"], "answerable": True}
        for i in range(1000)}


def test_fills_every_quota_and_totals_twenty_five():
    picked = sample(population(), seed=1)
    assert len(picked) == 25 == sum(QUOTAS.values())
    assert Counter(stratum(r) for r in picked) == Counter(QUOTAS)


def test_same_seed_same_sample_and_order():
    rows = population()
    ids = lambda s: [(r["controller"], r["id"]) for r in s]
    assert ids(sample(rows, seed=7)) == ids(sample(rows, seed=7))
    assert ids(sample(rows, seed=7)) != ids(sample(rows, seed=8))


def test_every_run_is_a_different_question():
    rows = [run(i, j, g, qid=f"q{i % 40}") for i, (j, g) in
            enumerate([k for k in QUOTAS for _ in range(30)])]
    picked = sample(rows, seed=3)
    assert len(picked) == 25
    assert max(Counter(r["id"] for r in picked).values()) == 1


def test_small_stratum_is_taken_whole_and_total_topped_up():
    rows = [r for r in population() if stratum(r) != ("incorrect", "supported")]
    rows += [run(900 + i, "incorrect", "supported") for i in range(2)]
    picked = sample(rows, seed=1)
    assert len(picked) == 25
    assert Counter(stratum(r) for r in picked)[("incorrect", "supported")] == 2


def test_blind_sheet_hides_judge_labels_and_decider():
    picked = sample(population(), seed=1)
    sheet = blind_rows(picked, GOLD)
    text = repr(sheet)
    assert "judge says" not in text and "grounded says" not in text
    assert all("controller" not in row and "judge_label" not in row for row in sheet)
    assert [row["n"] for row in sheet] == list(range(1, 26))
    assert sheet[0]["gold"].startswith("gold ") and sheet[0]["human_correctness"] == ""


def test_one_csv_holds_everything_to_read_and_answer(tmp_path):
    picked = sample(population(), seed=1)
    path = tmp_path / "grading.csv"
    write_grading_csv(path, blind_rows(picked, GOLD))
    rows = list(csv.DictReader(path.open()))
    assert len(rows) == 25
    assert {"question", "gold", "accepted", "predicted", "notes",
            "human_correctness", "human_grounded", "comment"} <= set(rows[0])
    assert rows[0]["notes"] == "[T]\n- fact" and rows[0]["human_correctness"] == ""


def test_key_lines_up_with_sheet_and_carries_weights():
    rows = population()
    picked = sample(rows, seed=1)
    key = key_rows(picked, rows)
    assert [k["n"] for k in key] == list(range(1, 26))
    assert key[0]["judge_label"] == picked[0]["judge"]["label"]
    k = next(k for k in key if (k["judge_label"], k["grounded_label"]) == ("correct", "supported"))
    assert k["weight"] == 30 / QUOTAS[("correct", "supported")]


def test_grader_payload_carries_rows_and_rubric_but_no_judge_labels(tmp_path):
    picked = sample(population(), seed=1)
    payload = grader_payload(blind_rows(picked, GOLD))
    assert len(payload["rows"]) == 25
    assert [o["label"] for o in payload["rubric"]["correctness"]] == [
        "correct", "hedged", "incorrect", "no_answer"]
    assert [o["label"] for o in payload["rubric"]["grounded"]] == [
        "supported", "unsupported", "not_applicable"]
    assert all(o["definition"] for group in payload["rubric"].values() for o in group)
    assert "judge says" not in json.dumps(payload)
    again = grader_payload(blind_rows(sample(population(), seed=1), GOLD))
    other = grader_payload(blind_rows(sample(population(), seed=2), GOLD))
    assert payload["sample_id"] == again["sample_id"] != other["sample_id"]
