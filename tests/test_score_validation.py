"""Agreement between the human labels and the judges (no API calls)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from score_validation import cohen_kappa, score


def test_kappa_perfect_and_textbook_values():
    assert cohen_kappa(["a", "b", "a"], ["a", "b", "a"]) == 1.0
    # po = .75, pe = .5*.25 + .5*.75 = .5 -> (.75 - .5) / .5
    assert cohen_kappa(["y", "y", "n", "n"], ["y", "n", "n", "n"]) == pytest.approx(0.5)


def test_kappa_undefined_when_both_raters_use_one_label():
    assert cohen_kappa(["y", "y"], ["y", "y"]) is None


def test_kappa_rejects_unequal_lengths():
    with pytest.raises(ValueError):
        cohen_kappa(["y"], ["y", "n"])


def key(n, judge, grounded, weight=1.0):
    return {"n": str(n), "judge_label": judge, "grounded_label": grounded,
            "weight": str(weight), "controller": "jev", "id": f"q{n}",
            "judge_explanation": "j", "grounded_explanation": "g"}


def human(n, correctness, grounded, comment=""):
    return {"n": str(n), "question": f"Q{n}?", "human_correctness": correctness,
            "human_grounded": grounded, "comment": comment}


def test_score_counts_agreement_weights_and_disagreements():
    keys = [key(1, "correct", "supported", 10), key(2, "hedged", "unsupported", 2),
            key(3, "incorrect", "supported", 2), key(4, "correct", "supported", 10)]
    labels = [human(1, "correct", "supported"), human(2, "incorrect", "unsupported", "a guess"),
              human(3, "incorrect", "unsupported"), human(4, "correct", "supported")]
    out = score(labels, keys)
    c, g = out["correctness"], out["grounded"]
    assert (c["n"], c["agree"]) == (4, 3)
    assert c["weighted_agreement"] == pytest.approx((10 + 2 + 10) / 24)
    assert c["confusion"][("hedged", "incorrect")] == 1
    # Counted as correct or not, the hedged/incorrect split does not matter.
    assert out["counts_as_correct"]["agree"] == 4
    assert (g["agree"], g["n"]) == (3, 4)
    assert [d["n"] for d in out["disagreements"]] == [2, 3]
    assert out["disagreements"][0]["comment"] == "a guess"


def test_score_skips_rows_left_ungraded():
    out = score([human(1, "correct", "supported"), human(2, "", "")],
                [key(1, "correct", "supported"), key(2, "correct", "supported")])
    assert out["correctness"]["n"] == 1 and out["ungraded"] == [2]
