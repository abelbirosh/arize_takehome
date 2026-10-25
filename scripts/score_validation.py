"""Compare the human labels with the judges' (no model calls).

    uv run python scripts/score_validation.py

Reads results/human_validation/labels.csv (from the grading page) and key.csv (from
sample_validation.py), and writes agreement.md beside them: raw agreement, Cohen's kappa,
agreement re-weighted to the full grid, the confusion of labels, and every disagreement.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "results/human_validation"


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    """Chance-corrected agreement; None when it is undefined (both raters used one label)."""
    if len(a) != len(b):
        raise ValueError("raters labelled different numbers of items")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in ca) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def _compare(pairs: list[tuple[str, str, float]]) -> dict:
    """pairs: (judge, human, weight) per graded row."""
    judge, human, weight = zip(*pairs) if pairs else ((), (), ())
    agree = [j == h for j, h in zip(judge, human)]
    return {
        "n": len(pairs), "agree": sum(agree),
        "kappa": cohen_kappa(list(judge), list(human)) if pairs else None,
        "weighted_agreement": (sum(w for w, ok in zip(weight, agree) if ok) / sum(weight)
                               if pairs else None),
        "confusion": Counter(zip(judge, human)),
    }


def score(labels: list[dict], keys: list[dict]) -> dict:
    key_by_n = {k["n"]: k for k in keys}
    rows = [(lab, key_by_n[lab["n"]]) for lab in labels]
    graded = [(lab, k) for lab, k in rows if lab["human_correctness"] and lab["human_grounded"]]

    def pairs(judge_field: str, human_field: str, as_binary: str | None = None):
        out = []
        for lab, k in graded:
            j, h = k[judge_field], lab[human_field]
            if as_binary:
                j, h = str(j == as_binary), str(h == as_binary)
            out.append((j, h, float(k["weight"])))
        return out

    disagreements = [{
        "n": int(lab["n"]), "question": lab["question"], "controller": k["controller"],
        "judge": (k["judge_label"], k["grounded_label"]),
        "human": (lab["human_correctness"], lab["human_grounded"]),
        "judge_explanation": k["judge_explanation"],
        "grounded_explanation": k["grounded_explanation"], "comment": lab["comment"],
    } for lab, k in graded
        if (k["judge_label"], k["grounded_label"]) != (lab["human_correctness"], lab["human_grounded"])]

    return {
        "correctness": _compare(pairs("judge_label", "human_correctness")),
        "counts_as_correct": _compare(pairs("judge_label", "human_correctness", "correct")),
        "grounded": _compare(pairs("grounded_label", "human_grounded")),
        "disagreements": sorted(disagreements, key=lambda d: d["n"]),
        "ungraded": [int(lab["n"]) for lab, _ in rows if (lab, _) not in graded],
    }


def _fmt(x: float | None, pct: bool = False) -> str:
    if x is None:
        return "—"
    return f"{x:.0%}" if pct else f"{x:.2f}"


def report(out: dict) -> str:
    lines = ["# Human validation: agreement with the judges", "",
             "| Check | Graded | Agree | Raw | Weighted to the grid | Cohen's κ |",
             "|---|---|---|---|---|---|"]
    for name, title in [("correctness", "Correctness (4 labels)"),
                        ("counts_as_correct", "Counts as correct (yes/no)"),
                        ("grounded", "Grounded (3 labels)")]:
        m = out[name]
        lines.append(f"| {title} | {m['n']} | {m['agree']} | {_fmt(m['agree'] / m['n'], True)} | "
                     f"{_fmt(m['weighted_agreement'], True)} | {_fmt(m['kappa'])} |")
    for name, title in [("correctness", "Correctness"), ("grounded", "Grounded")]:
        conf = out[name]["confusion"]
        labels = sorted({j for j, _ in conf} | {h for _, h in conf})
        lines += ["", f"## {title}: judge (rows) against human (columns)", "",
                  "| Judge \\ Human | " + " | ".join(labels) + " |",
                  "|---" * (len(labels) + 1) + "|"]
        for j in labels:
            lines.append(f"| {j} | " + " | ".join(str(conf.get((j, h), 0) or "")
                                                    for h in labels) + " |")
    lines += ["", f"## Disagreements ({len(out['disagreements'])})", ""]
    for d in out["disagreements"]:
        lines += [f"### {d['n']}. {d['question']}", "",
                  f"- Decider: {d['controller']}",
                  f"- Judge: {d['judge'][0]} / {d['judge'][1]}; human: {d['human'][0]} / {d['human'][1]}",
                  f"- Correctness judge: {d['judge_explanation']}",
                  f"- Grounded judge: {d['grounded_explanation']}"]
        if d["comment"]:
            lines.append(f"- Your comment: {d['comment']}")
        lines.append("")
    if out["ungraded"]:
        lines.append(f"Ungraded rows left out: {', '.join(map(str, out['ungraded']))}")
    return "\n".join(lines)


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--labels", type=Path, default=DIR / "labels.csv")
    p.add_argument("--key", type=Path, default=DIR / "key.csv")
    p.add_argument("--out", type=Path, default=DIR / "agreement.md")
    args = p.parse_args()
    text = report(score(_read(args.labels), _read(args.key)))
    args.out.write_text(text + "\n")
    print(text.split("\n## ")[0])
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
