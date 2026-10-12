"""Assemble the benchmark questions and upload them to Phoenix as datasets.

    uv run python scripts/prepare_dataset.py            # v1: data/benchmark.jsonl + pilot
    uv run python scripts/prepare_dataset.py --upload   # ...and create the Phoenix datasets
    uv run python scripts/prepare_dataset.py --suite v2 [--upload]   # 50-question suite

No model calls: questions come from data/candidates_*.jsonl.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# 2 per FRAMES reasoning type, chosen from the 70-question pool to need 2-4
# Wikipedia articles, have short unambiguous gold answers and, where the earlier
# partial closed-book screen covered them, not be answerable from memory.
FRAMES_IDS = [
    "frames-338", "frames-536",  # multiple constraints
    "frames-203", "frames-352",  # numerical reasoning
    "frames-618", "frames-588",  # post processing
    "frames-322", "frames-207",  # tabular reasoning
    "frames-489", "frames-718",  # temporal reasoning
]
PILOT_IDS = ["fresh-physics-icecube", "frames-338"]

DATASET = "research-bench-25"
PILOT = "research-bench-pilot"

# --- v2: 50 questions in 7 categories -----------------------------------------
# Easy recent controls (everyone should pass) carried over from v1.
V2_CONTROLS = ["fresh-physics-icecube", "fresh-apple-foldable", "fresh-apple-ceo",
               "fresh-wc-motm", "fresh-jev-book"]
# v1 FRAMES minus the three no controller solved (203, 322, 207), plus 7 more.
V2_FRAMES = ["frames-338", "frames-536", "frames-352", "frames-618", "frames-588",
             "frames-489", "frames-718",
             "frames-10", "frames-243", "frames-494", "frames-76", "frames-414",
             "frames-318", "frames-400"]
# One per category, for a cheap pilot before the full run.
V2_PILOT = ["fresh-apple-ceo", "two-slam-count", "multi-earliest-born",
            "arith-usm-final-games", "frames-338", "new-msft-base-model", "unans-wc-shootout"]
DATASET_V2 = "research-bench-50"
PILOT_V2 = "research-bench-50-pilot"


def load(name: str) -> dict[str, dict]:
    return {r["id"]: r for r in map(json.loads, open(DATA / name))}


def build() -> list[dict]:
    fresh = list(load("candidates_fresh.jsonl").values())
    frames_pool = load("candidates_frames.jsonl")
    rows = fresh + [frames_pool[i] for i in FRAMES_IDS]
    return [
        {"id": r["id"], "source": r["source"], "question": r["question"],
         "answer": r["answer"], "reasoning_types": r["reasoning_types"],
         "evidence": r.get("evidence") or r.get("wiki_links", [])}
        for r in rows
    ]


def build_v2() -> list[dict]:
    fresh = load("candidates_fresh.jsonl")
    frames = load("candidates_frames.jsonl")
    rows = [{"id": i, "category": "control", "question": fresh[i]["question"],
             "answer": fresh[i]["answer"], "accepted": [fresh[i]["answer"]],
             "answerable": True, "needs_web": True, "evidence": fresh[i]["evidence"]}
            for i in V2_CONTROLS]
    rows += list(load("questions_v2_authored.jsonl").values())
    rows += [{"id": i, "category": "frames", "question": frames[i]["question"],
              "answer": frames[i]["answer"], "accepted": [frames[i]["answer"]],
              "answerable": True, "needs_web": False, "evidence": frames[i]["wiki_links"],
              "reasoning_types": frames[i]["reasoning_types"]}
             for i in V2_FRAMES]
    return rows


def upload_v2(rows: list[dict], name: str, description: str) -> None:
    from phoenix.client import Client

    client = Client(base_url=os.environ.get("PHOENIX_COLLECTOR_ENDPOINT",
                                            "http://localhost:6006"))
    ds = client.datasets.create_dataset(
        name=name,
        dataset_description=description,
        inputs=[{"question": r["question"]} for r in rows],
        outputs=[{"answer": r["answer"], "accepted": r["accepted"]} for r in rows],
        metadata=[{k: r[k] for k in ("id", "category", "answerable", "needs_web", "evidence")}
                  for r in rows],
    )
    print(f"uploaded {name}: {len(rows)} examples (dataset id {ds.id})")


def write(rows: list[dict], path: Path) -> None:
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def upload(rows: list[dict], name: str, description: str) -> None:
    from phoenix.client import Client

    client = Client(base_url=os.environ.get("PHOENIX_COLLECTOR_ENDPOINT",
                                            "http://localhost:6006"))
    ds = client.datasets.create_dataset(
        name=name,
        dataset_description=description,
        inputs=[{"question": r["question"]} for r in rows],
        outputs=[{"answer": r["answer"]} for r in rows],
        metadata=[{"id": r["id"], "source": r["source"],
                   "reasoning_types": r["reasoning_types"],
                   "evidence": r["evidence"]} for r in rows],
    )
    print(f"uploaded {name}: {len(rows)} examples (dataset id {ds.id})")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--upload", action="store_true")
    p.add_argument("--suite", choices=["v1", "v2"], default="v1")
    args = p.parse_args()

    if args.suite == "v2":
        rows = build_v2()
        ids = [r["id"] for r in rows]
        assert len(rows) == 50 and len(set(ids)) == 50, (len(rows), len(set(ids)))
        pilot = [r for r in rows if r["id"] in V2_PILOT]
        assert len(pilot) == len(V2_PILOT)
        write(rows, DATA / "benchmark_v2.jsonl")
        write(pilot, DATA / "pilot_v2.jsonl")
        from collections import Counter
        print(f"wrote {len(rows)} questions:", dict(Counter(r["category"] for r in rows)),
              f"and a {len(pilot)}-question pilot")
        if args.upload:
            upload_v2(rows, DATASET_V2, "50 research questions in 7 categories (control, "
                      "two_recent, multi_entity, arithmetic, frames, too_new, unanswerable)")
            upload_v2(pilot, PILOT_V2, "7-question pilot: one per category")
        return

    rows = build()
    pilot = [r for r in rows if r["id"] in PILOT_IDS]
    assert len(rows) == 25 and len(pilot) == 2, (len(rows), len(pilot))
    write(rows, DATA / "benchmark.jsonl")
    write(pilot, DATA / "pilot.jsonl")
    print(f"wrote {len(rows)} questions ({sum(r['source'] == 'fresh' for r in rows)} fresh, "
          f"{sum(r['source'] == 'frames' for r in rows)} FRAMES) and a {len(pilot)}-question pilot")
    if args.upload:
        upload(rows, DATASET, "25 research questions: 15 post-cutoff (web + Wikipedia), "
                              "10 FRAMES multi-hop (Wikipedia)")
        upload(pilot, PILOT, "2-question pilot: one fresh, one FRAMES")


if __name__ == "__main__":
    main()
