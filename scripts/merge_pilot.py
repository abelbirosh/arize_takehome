"""Copy the v2 pilot's runs and evaluations into the full-v2 experiments.

    uv run python scripts/merge_pilot.py

The pilot (research-bench-50-pilot, tag pilot-v2) ran the same code on the 7
questions that make up the "pilot" split of research-bench-v2. The full run
covered only the "main" split, so copying the pilot runs in gives one complete
50-question experiment per decider in Phoenix. Run once; it refuses to copy into
an experiment that already has runs for the pilot questions. No model calls.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from phoenix.client import Client

RESULTS = Path(__file__).resolve().parent.parent / "results"


def _ts(value) -> datetime:
    return value if isinstance(value, datetime) else datetime.fromisoformat(value)


def main() -> None:
    client = Client(base_url=os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006"))
    pilot_ds = client.datasets.get_dataset(dataset="research-bench-50-pilot")
    full_ds = client.datasets.get_dataset(dataset="research-bench-v2")
    pilot_meta = {ex["id"]: ex["metadata"]["id"] for ex in pilot_ds.examples}
    target = {ex["metadata"]["id"]: ex["id"] for ex in full_ds.examples}

    pilots = {e["metadata"]["controller"]: e for e in client.experiments.list(dataset_id=pilot_ds.id)
              if e["name"].endswith("[pilot-v2]")}
    fulls = {e["metadata"]["controller"]: e for e in client.experiments.list(dataset_id=full_ds.id)
             if e["name"].endswith("[full-v2]")}

    copied = 0
    for controller, full in sorted(fulls.items()):
        pilot = pilots.get(controller)
        if pilot is None:
            print(f"!! no pilot experiment for {controller}")
            continue
        existing = client.experiments.get_experiment(experiment_id=full["id"])
        have = {r["dataset_example_id"] for r in existing["task_runs"]}
        src = client.experiments.get_experiment(experiment_id=pilot["id"])
        evals_by_run: dict[str, list] = {}
        for ev in src["evaluation_runs"]:
            if not ev.error:
                evals_by_run.setdefault(ev.experiment_run_id, []).append(ev)
        for run in src["task_runs"]:
            dest_example = target[pilot_meta[run["dataset_example_id"]]]
            if dest_example in have:
                print(f"   skip {controller} {pilot_meta[run['dataset_example_id']]}: already present")
                continue
            new = client.experiments.log_run(
                experiment_id=full["id"], dataset_example_id=dest_example, output=run["output"],
                start_time=_ts(run["start_time"]), end_time=_ts(run["end_time"]),
                trace_id=run["trace_id"], error=run["error"],
            )
            for ev in evals_by_run.get(run["id"], []):
                result = ev.result or {}
                if isinstance(result, list):  # single-output evaluators only
                    result = result[0] if result else {}
                client.experiments.log_evaluation(
                    experiment_run_id=new["id"], name=ev.name, annotator_kind=ev.annotator_kind,
                    trace_id=ev.trace_id,
                    **{k: result[k] for k in ("score", "label", "explanation")
                       if result.get(k) is not None},
                )
            copied += 1
        print(f"{controller}: copied pilot runs into {full['name']}")

    # Merge the local records the same way.
    merged = RESULTS / "full-v2-merged.jsonl"
    rows = [json.loads(line) for name in ("full-v2.jsonl", "pilot-v2.jsonl")
            for line in open(RESULTS / name)]
    with open(merged, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"copied {copied} runs; wrote {len(rows)} records to {merged}")


if __name__ == "__main__":
    main()
