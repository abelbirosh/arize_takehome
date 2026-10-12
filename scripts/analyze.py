"""Summarize a benchmark run from results/<tag>.jsonl (no model calls).

    uv run python scripts/analyze.py results/full-v1.jsonl
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict

ORDER = ["jev", "msft", "oai", "claude-haiku-5.5", "claude-sonnet-5.5", "claude-opus-5.5",
         "fixed"]
CATEGORIES = ["control", "two_recent", "multi_entity", "arithmetic", "frames", "too_new",
              "unanswerable"]


def load(path: str) -> list[dict]:
    return [json.loads(line) for line in open(path)]


def correct(r: dict) -> bool:
    return r.get("judge", {}).get("label") == "correct"


def table(records: list[dict], title: str) -> None:
    by = defaultdict(list)
    for r in records:
        by[r["controller"]].append(r)
    print(f"\n## {title}")
    print(f"{'controller':20} {'n':>3} {'acc':>5} {'$/run':>8} {'route $':>8} {'active s':>8} "
          f"{'ms/decision':>11} {'steps':>6} {'forced':>6} {'invalid':>7} {'web':>5}")
    for c in ORDER:
        rs = by.get(c)
        if not rs:
            continue
        n = len(rs)
        m = lambda k: sum(r["stats"].get(k) or 0 for r in rs) / n  # noqa: E731
        decisions = sum(r["stats"]["decision_calls"] for r in rs)
        ms_per = (sum(r["stats"]["routing_latency_ms"] for r in rs) / decisions) if decisions else 0
        print(f"{c:20} {n:>3} {sum(map(correct, rs)) / n:>5.0%} {m('total_cost_usd'):>8.4f} "
              f"{m('routing_cost_usd'):>8.4f} {m('active_ms') / 1000:>8.1f} {ms_per:>11.0f} "
              f"{m('steps'):>6.1f} {sum(r['stats']['forced_answer'] for r in rs):>6} "
              f"{sum(r['stats']['invalid_decisions'] for r in rs):>7} "
              f"{sum(r['stats']['used_web_search'] for r in rs) / n:>5.0%}")


def per_question(records: list[dict]) -> None:
    by_q = defaultdict(dict)
    for r in records:
        by_q[r["id"]][r["controller"]] = r
    print("\n## Per question (+ correct, . wrong, ! forced at budget)")
    print(f"{'question':32} " + " ".join(f"{c[:8]:>8}" for c in ORDER))
    spread = 0
    for qid, rs in by_q.items():
        cells = []
        for c in ORDER:
            r = rs.get(c)
            cells.append(" " * 8 if r is None else
                         f"{('+' if correct(r) else '.') + ('!' if r['stats']['forced_answer'] else ''):>8}")
        if len({correct(r) for r in rs.values()}) > 1:
            spread += 1
        print(f"{qid:32} " + " ".join(cells))
    print(f"\n{spread}/{len(by_q)} questions split the controllers (some right, some wrong)")


def calibration(records: list[dict]) -> None:
    for ctrl in ("jev", "msft", "oai"):
        calibration_for(records, ctrl)


def calibration_for(records: list[dict], ctrl: str) -> None:
    jev = [r for r in records if r["controller"] == ctrl]
    if not jev:
        return
    print(f"\n## {ctrl} calibration: final 'notes suffice' probability vs judged correctness")
    buckets = [(0, .25), (.25, .5), (.5, .75), (.75, 1.01)]
    for lo, hi in buckets:
        rs = [r for r in jev if r["stats"].get("final_evidence_sufficient") is not None
              and lo <= r["stats"]["final_evidence_sufficient"] < hi]
        if rs:
            print(f"  evidence_sufficient in [{lo:.2f}, {min(hi, 1):.2f}): {len(rs):>2} runs, "
                  f"{sum(map(correct, rs)) / len(rs):.0%} correct")
    answer_conf = [(s["confidence"], correct(r)) for r in jev for s in r["steps"]
                   if s["action"] == "answer" and s["confidence"] is not None]
    if answer_conf:
        hi = [c for p, c in answer_conf if p >= 0.5]
        lo = [c for p, c in answer_conf if p < 0.5]
        print(f"  chose 'answer' with confidence >= 0.5: {len(hi)} runs, "
              f"{(sum(hi) / len(hi) if hi else 0):.0%} correct")
        print(f"  chose 'answer' with confidence <  0.5: {len(lo)} runs, "
              f"{(sum(lo) / len(lo) if lo else 0):.0%} correct")


def label(r: dict, key: str) -> str | None:
    return (r.get(key) or {}).get("label")


def by_category(records: list[dict]) -> None:
    print("\n## Accuracy by category (unanswerable = correct premise rejection)")
    present = [c for c in CATEGORIES if any(r.get("category") == c for r in records)]
    print(f"{'controller':20} " + " ".join(f"{c[:11]:>11}" for c in present))
    for ctrl in ORDER:
        rs = [r for r in records if r["controller"] == ctrl]
        if not rs:
            continue
        cells = []
        for c in present:
            cs = [r for r in rs if r.get("category") == c]
            cells.append(f"{sum(map(correct, cs)) / len(cs):>11.0%}" if cs else " " * 11)
        print(f"{ctrl:20} " + " ".join(cells))


def outcomes(records: list[dict]) -> None:
    print("\n## Outcomes: correctness label x grounded (did the notes support the answer?)")
    print(f"{'controller':20} {'correct+grnd':>12} {'correct+mem':>11} {'hedged':>7} "
          f"{'wrong':>6} {'no_ans':>7}")
    for ctrl in ORDER:
        rs = [r for r in records if r["controller"] == ctrl]
        if not rs:
            continue
        cg = sum(label(r, "judge") == "correct" and label(r, "grounded") == "supported" for r in rs)
        cm = sum(label(r, "judge") == "correct" and label(r, "grounded") == "unsupported" for r in rs)
        print(f"{ctrl:20} {cg:>12} {cm:>11} "
              f"{sum(label(r, 'judge') == 'hedged' for r in rs):>7} "
              f"{sum(label(r, 'judge') == 'incorrect' for r in rs):>6} "
              f"{sum(label(r, 'judge') == 'no_answer' for r in rs):>7}")


def main(path: str) -> None:
    records = load(path)
    total = sum(r["stats"]["total_cost_usd"] for r in records)
    print(f"{len(records)} runs, agent cost ${total:.2f}")
    table(records, "All questions")
    if any(r.get("category") for r in records):  # v2 suite
        by_category(records)
        outcomes(records)
    else:
        table([r for r in records if r["source"] == "fresh"], "Fresh (post-cutoff, needs web)")
        table([r for r in records if r["source"] == "frames"], "FRAMES (multi-hop Wikipedia)")
    per_question(records)
    calibration(records)


if __name__ == "__main__":
    main(sys.argv[1])
