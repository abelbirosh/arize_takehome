"""Re-judge correctness for one question's runs after its gold or accepted answers change.

    uv run python scripts/regrade.py frames-494 results/full-v2-merged.jsonl

Reads the question's current gold, accepted variants and answerability from the suite,
re-asks the correctness judge for every run of it (one paid call per run), and rewrites
the results file in place. Grounding does not depend on the gold answer, so it is kept.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_agent.evals import Judge

ROOT = Path(__file__).resolve().parent.parent


def regrade(rows: list[dict], qid: str, suite: dict[str, dict], judge) -> list[tuple]:
    q = suite[qid]
    changed = []
    for r in rows:
        if r["id"] != qid:
            continue
        old = r["judge"]["label"]
        j = judge.correctness(r["question"], q["answer"], q["accepted"],
                              q.get("answerable", True), r["answer"])
        r["judge"] = {"label": j.label, "explanation": j.explanation, "cost_usd": j.cost_usd}
        changed.append((r.get("controller", r["id"]), old, j.label))
    return changed


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("qid")
    p.add_argument("results", type=Path, nargs="+")
    p.add_argument("--suite", type=Path, default=ROOT / "data/benchmark_v2.jsonl")
    args = p.parse_args()
    suite = {q["id"]: q for q in map(json.loads, args.suite.open())}
    judge = Judge()
    for path in args.results:
        rows = [json.loads(line) for line in path.open() if line.strip()]
        changed = regrade(rows, args.qid, suite, judge)
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        print(path.name)
        for who, old, new in changed:
            print(f"  {who:<20} {old:>10} -> {new}")


if __name__ == "__main__":
    main()
