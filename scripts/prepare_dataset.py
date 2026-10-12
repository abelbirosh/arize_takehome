"""Assemble the benchmark questions and upload them to Phoenix as datasets.

    uv run python scripts/prepare_dataset.py            # write data/benchmark.jsonl + pilot
    uv run python scripts/prepare_dataset.py --upload   # ...and create the Phoenix datasets

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
    args = p.parse_args()

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
