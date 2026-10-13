"""Write the presentation's charts, test suite and per-test results (no model calls).

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
SUITE = "data/benchmark_v2.jsonl"
MAX_STEPS = 8

# Display order and one-line description for each question category.
TIERS = [
    ("control", "Controls", "Easy post-cutoff facts every decider should get."),
    ("two_recent", "Two recent facts", "Chain two post-cutoff facts to reach the answer."),
    ("multi_entity", "Multi-entity", "Compare or count across several people or events."),
    ("arithmetic", "Arithmetic", "Look up facts, then compute the answer."),
    ("too_new", "Too new for Wikipedia", "October 2026 releases that only the web covers."),
    ("unanswerable", "Unanswerable", "False premise; the correct answer rejects it."),
    ("frames", "Multi-hop (FRAMES)", "Chain 2–4 Wikipedia articles (google/frames-benchmark)."),
]

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

    def cost_per_decision(rs: list[dict]) -> float:
        calls = sum(r["stats"]["decision_calls"] for r in rs)
        return sum(r["stats"]["routing_cost_usd"] for r in rs) / calls if calls else 0.0

    slowest = max(s["latency_ms"] or 0 for r in by[HAIKU] for s in r["steps"])
    haiku_note = f"Haiku 5.5 excluded: one routing call stalled {slowest / 3_600_000:.1f} h, skewing the mean."

    metrics = [
        {"id": "accuracy", "label": "Accuracy", "scale": ["More accurate", "Less accurate"], "format": "percent", "better": "higher",
         "max": 1.0,
         "description": "Judge-graded correct answers over 50 questions; hedges count as wrong.",
         "values": per_decider(lambda rs: mean([r["judge"]["label"] == "correct" for r in rs]))},
        {"id": "cost", "label": "Cost per run", "scale": ["Cheaper", "More expensive"], "format": "usd", "better": "lower",
         "description": "Mean total spend per run: routing + generation.",
         "values": per_decider(lambda rs: mean([r["stats"]["total_cost_usd"] for r in rs]))},
        {"id": "route-cost", "label": "Cost per decision", "scale": ["Cheaper routing", "Costlier routing"], "format": "cents", "better": "lower",
         "description": "Mean routing spend per decision call.",
         "values": per_decider(cost_per_decision)},
        {"id": "active", "label": "Time per run", "scale": ["Faster", "Slower"], "format": "seconds", "better": "lower",
         "description": "Mean wall time per run, minus rate-limiter queueing.",
         "values": per_decider(lambda rs: mean([r["stats"]["active_ms"] for r in rs]) / 1000),
         "excluded": {HAIKU: haiku_note}},
        {"id": "decision-ms", "label": "Time per decision", "scale": ["Faster decisions", "Slower decisions"], "format": "ms", "better": "lower",
         "description": "Mean latency per routing call.",
         "values": per_decider(ms_per_decision),
         "excluded": {HAIKU: haiku_note}},
        {"id": "steps", "label": "Steps taken", "scale": ["Fewer steps", "More steps"], "format": "decimal", "better": "lower",
         "description": "Mean actions per run against an 8-step budget.",
         "values": per_decider(lambda rs: mean([r["stats"]["steps"] for r in rs]))},
        {"id": "out-of-turns", "label": "Reached turn limit", "scale": ["Rarely ran out", "Often ran out"], "format": "count", "better": "lower",
         "description": "Runs that hit the 8-step budget and were forced to answer.",
         "values": per_decider(lambda rs: sum(bool(r["stats"]["forced_answer"]) for r in rs))},
    ]
    for m in metrics:
        m["values"] = {k: round(v, 8) for k, v in m["values"].items()}

    suite = [json.loads(line) for line in open(ROOT / SUITE)]
    tier_order = [t for t, *_ in TIERS]
    suite.sort(key=lambda q: tier_order.index(q["category"]))
    ran = {name: {json.loads(line)["id"] for line in open(ROOT / "results" / name)}
           for name in ("full-v2.jsonl", "pilot-v2.jsonl")}
    labels = {(r["id"], r["controller"]): r["judge"]["label"] for r in records}

    out = {
        "source": source,
        "questions": len(suite),
        "runs": len(records),
        "counts": {"questions": len(suite), "deciders": len(DECIDERS), "runs": len(records),
                   "main": len(ran["full-v2.jsonl"]), "pilot": len(ran["pilot-v2.jsonl"]),
                   "max_steps": MAX_STEPS},
        "deciders": [{"id": k, "short": s, "name": n, "kind": kind} for k, s, n, kind in DECIDERS],
        "metrics": metrics,
        "tiers": [{"id": t, "name": name, "description": desc,
                   "count": sum(q["category"] == t for q in suite)} for t, name, desc in TIERS],
        "tests": [{"n": i, "id": q["id"], "tier": q["category"], "question": q["question"],
                   "answer": q["answer"],
                   "results": {k: labels[(q["id"], k)] for k, *_ in DECIDERS}}
                  for i, q in enumerate(suite, 1)],
    }
    Path(ROOT / target).write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {target} from {len(records)} runs")


if __name__ == "__main__":
    main(*sys.argv[1:3])
