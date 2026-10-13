"""Write the presentation's headline charts from a benchmark run (no model calls).

    python3 scripts/export_frontend_metrics.py
    python3 scripts/export_frontend_metrics.py results/full-v2-merged.jsonl frontend/public/benchmark.json

Every number the frontend charts comes from here, so the presentation never carries
hand-typed results.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = "results/full-v2-merged.jsonl"
TARGET = "frontend/public/benchmark.json"

DECIDERS = [
    ("jev", "Jev", "Jev (TypeSafe)", "decision"),
    ("msft", "MSFT", "Microsoft Decision 1", "decision"),
    ("oai", "OAI", "OpenAI GPT-6 Luna Decisions", "decision"),
    ("claude-haiku-5.5", "Haiku", "Claude Haiku 5.5", "reasoning"),
    ("claude-sonnet-5.5", "Sonnet", "Claude Sonnet 5.5", "reasoning"),
    ("claude-opus-5.5", "Opus", "Claude Opus 5.5", "reasoning"),
    ("fixed", "Fixed", "Fixed sequence (no model)", "fixed"),
]

# A Haiku routing call that stalled for hours swamps its latency averages.
HAIKU = "claude-haiku-5.5"


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def main(source: str = SOURCE, target: str = TARGET) -> None:
    records = [json.loads(line) for line in open(ROOT / source)]
    by = defaultdict(list)
    for r in records:
        by[r["controller"]].append(r)

    def per_decider(fn) -> dict[str, float]:
        return {key: fn(by[key]) for key, *_ in DECIDERS}

    def ms_per_decision(rs: list[dict]) -> float:
        calls = sum(r["stats"]["decision_calls"] for r in rs)
        return sum(r["stats"]["routing_latency_ms"] for r in rs) / calls if calls else 0.0

    slowest = max(s["latency_ms"] or 0 for r in by[HAIKU] for s in r["steps"])
    haiku_note = (f"Haiku 5.5 is left out: one of its routing calls stalled for "
                  f"{slowest / 3_600_000:.1f} hours, which swamps its average.")

    metrics = [
        {"id": "accuracy", "label": "Accuracy", "format": "percent", "better": "higher",
         "max": 1.0,
         "description": "Share of the 50 answers the judge graded correct against the "
                        "accepted variants. Hedged answers do not count.",
         "values": per_decider(lambda rs: mean([r["judge"]["label"] == "correct" for r in rs]))},
        {"id": "cost", "label": "$/run", "format": "usd", "better": "lower",
         "description": "Average total cost of one run: routing plus Haiku writing the "
                        "queries, notes, and answer.",
         "values": per_decider(lambda rs: mean([r["stats"]["total_cost_usd"] for r in rs]))},
        {"id": "route-cost", "label": "Route $", "format": "usd", "better": "lower",
         "description": "The part of each run's cost spent deciding the next step. "
                        "The fixed sequence makes no decisions.",
         "values": per_decider(lambda rs: mean([r["stats"]["routing_cost_usd"] for r in rs]))},
        {"id": "active", "label": "Active seconds", "format": "seconds", "better": "lower",
         "description": "Average seconds per run, excluding time queued behind the "
                        "shared rate limiter.",
         "values": per_decider(lambda rs: mean([r["stats"]["active_ms"] for r in rs]) / 1000),
         "excluded": {HAIKU: haiku_note}},
        {"id": "steps", "label": "Steps", "format": "decimal", "better": "lower",
         "description": "Average actions per run (searches, reads, and the answer) out "
                        "of a budget of eight.",
         "values": per_decider(lambda rs: mean([r["stats"]["steps"] for r in rs]))},
        {"id": "out-of-turns", "label": "Out of turns", "format": "count", "better": "lower",
         "description": "Runs that used all eight steps without answering, so the "
                        "harness forced a final answer.",
         "values": per_decider(lambda rs: sum(bool(r["stats"]["forced_answer"]) for r in rs))},
        {"id": "decision-ms", "label": "ms/decision", "format": "ms", "better": "lower",
         "description": "Average time for one routing decision. The fixed sequence "
                        "makes none.",
         "values": per_decider(ms_per_decision),
         "excluded": {HAIKU: haiku_note}},
    ]
    for m in metrics:
        m["values"] = {k: round(v, 6) for k, v in m["values"].items()}

    out = {
        "source": source,
        "questions": len(by[DECIDERS[0][0]]),
        "runs": len(records),
        "deciders": [{"id": k, "short": s, "name": n, "kind": kind} for k, s, n, kind in DECIDERS],
        "metrics": metrics,
    }
    Path(ROOT / target).write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {target} from {len(records)} runs")


if __name__ == "__main__":
    main(*sys.argv[1:3])
