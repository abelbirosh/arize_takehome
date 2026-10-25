"""Draw a stratified sample of judged runs for blind human grading (no model calls).

    uv run python scripts/sample_validation.py results/full-v2-merged.jsonl

Oversamples the cases a judge is most likely to get wrong (hedges, wrong answers,
declines, unsupported answers). Writes to results/human_validation/:

- grading_sheet.md  the runs to grade: question, gold, prediction, notes; no judge labels
- labels.csv        one row per run for your two labels
- key.csv           the judge's labels and stratum weights; open only after grading
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from itertools import zip_longest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from research_agent.evals import CORRECTNESS_PROMPT, GROUNDED_PROMPT

ROOT = Path(__file__).resolve().parent.parent

# (correctness label, grounded label) -> runs to draw. Hard cases take 38 of 50 slots,
# against 114 of 350 runs in the full grid.
QUOTAS: dict[tuple[str, str], int] = {
    ("correct", "supported"): 12,
    ("correct", "unsupported"): 7,
    ("hedged", "supported"): 6,
    ("hedged", "unsupported"): 5,
    ("incorrect", "supported"): 5,
    ("incorrect", "unsupported"): 5,
    ("no_answer", "not_applicable"): 4,
    ("no_answer", "unsupported"): 3,
    ("no_answer", "supported"): 3,
}
MAX_PER_QUESTION = 2


def stratum(run: dict) -> tuple[str, str]:
    return run["judge"]["label"], (run.get("grounded") or {}).get("label", "")


def _interleave_by_controller(runs: list[dict]) -> list[dict]:
    """Round-robin across deciders so one decider can't fill a stratum."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        groups[r["controller"]].append(r)
    return [r for batch in zip_longest(*groups.values()) for r in batch if r is not None]


def sample(runs: list[dict], seed: int = 0, quotas: dict = QUOTAS) -> list[dict]:
    """Fill each stratum's quota, scarcest first, with at most two runs per question.
    A stratum too small for its quota is taken whole and the total topped up from the
    rest. Returns the picks in a shuffled (blind) order."""
    rng = random.Random(seed)
    pool = runs[:]
    rng.shuffle(pool)
    by_stratum: dict[tuple, list[dict]] = defaultdict(list)
    for r in pool:
        by_stratum[stratum(r)].append(r)

    picked: list[dict] = []
    per_question: Counter = Counter()

    def take(candidates: list[dict], n: int) -> None:
        for r in _interleave_by_controller(candidates):
            if n == 0:
                return
            if r in picked or per_question[r["id"]] >= MAX_PER_QUESTION:
                continue
            picked.append(r)
            per_question[r["id"]] += 1
            n -= 1

    for s in sorted(quotas, key=lambda s: len(by_stratum[s])):
        take(by_stratum[s], quotas[s])
    take(pool, sum(quotas.values()) - len(picked))
    rng.shuffle(picked)
    return picked


def _notes(run: dict) -> str:
    # Same listing the grounded judge saw.
    return "\n\n".join(f"[{n['title']}]\n{n['facts']}" for n in run.get("notes") or []) \
        or "(no notes)"


def blind_rows(picked: list[dict], gold: dict[str, dict]) -> list[dict]:
    """What the grader sees: no judge labels, explanations or decider names."""
    rows = []
    for n, r in enumerate(picked, 1):
        g = gold[r["id"]]
        rows.append({
            "n": n, "question": r["question"], "gold": g["answer"],
            "accepted": "; ".join(g.get("accepted", [])),
            "answerable": "yes" if g.get("answerable", True) else "no",
            "predicted": r["answer"], "notes": _notes(r),
            "human_correctness": "", "human_grounded": "", "comment": "",
        })
    return rows


def key_rows(picked: list[dict], runs: list[dict]) -> list[dict]:
    """The judge's labels per sheet row, and each stratum's weight (runs in the grid
    per sampled run) for re-weighting agreement back to the full grid."""
    population = Counter(stratum(r) for r in runs)
    drawn = Counter(stratum(r) for r in picked)
    return [{
        "n": n, "controller": r["controller"], "id": r["id"], "category": r["category"],
        "forced_answer": r["stats"].get("forced_answer", False),
        "judge_label": r["judge"]["label"], "judge_explanation": r["judge"]["explanation"],
        "grounded_label": stratum(r)[1],
        "grounded_explanation": (r.get("grounded") or {}).get("explanation", ""),
        "weight": population[stratum(r)] / drawn[stratum(r)],
    } for n, r in enumerate(picked, 1)]


def _rubric(prompt: str) -> str:
    body = prompt.split("Choose one label:")[1].split("Reply with JSON")[0]
    return body.strip()


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _sheet(rows: list[dict]) -> str:
    out = ["# Human validation: grading sheet", "",
           ("Grade each run blind. Put your labels in `labels.csv`; leave `key.csv` closed "
            "until you're done."), "",
           "## Correctness labels (same rubric as the judge)", "", _rubric(CORRECTNESS_PROMPT),
           "", "## Grounded labels (same rubric as the judge)", "",
           "Judge only against the notes below, not whether the answer is true.", "",
           _rubric(GROUNDED_PROMPT), ""]
    for r in rows:
        out += ["---", "", f"## {r['n']}. {r['question']}", "",
                f"- **Gold:** {r['gold']}", f"- **Accepted:** {r['accepted'] or '(none)'}",
                f"- **Answerable as asked:** {r['answerable']}",
                f"- **Predicted answer:** {r['predicted'] or '(empty)'}", "",
                "**Research notes**", "", "```", r["notes"], "```", ""]
    return "\n".join(out)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("results", type=Path)
    p.add_argument("--suite", type=Path, default=ROOT / "data/benchmark_v2.jsonl")
    p.add_argument("--out", type=Path, default=ROOT / "results/human_validation")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    runs = [json.loads(line) for line in args.results.open() if line.strip()]
    gold = {q["id"]: q for q in map(json.loads, args.suite.open()) if q}
    picked = sample(runs, seed=args.seed)
    sheet = blind_rows(picked, gold)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "grading_sheet.md").write_text(_sheet(sheet))
    _write_csv(args.out / "labels.csv", sheet,
               ["n", "question", "predicted", "human_correctness", "human_grounded", "comment"])
    key = key_rows(picked, runs)
    _write_csv(args.out / "key.csv", key, list(key[0]))
    strata = Counter(stratum(r) for r in picked)
    print(f"{len(picked)} runs, {len({r['id'] for r in picked})} questions -> {args.out}")
    for s, n in sorted(strata.items()):
        print(f"  {s[0]:>9} / {s[1]:<14} {n}")


if __name__ == "__main__":
    main()
