"""Add evaluations that are missing or stale on a run's experiments (e.g. after --resume).

    uv run python scripts/backfill_evals.py --tag full-v1

`resume_experiment` re-runs failed runs under the same run id, so a grade logged
for the failed attempt ("empty prediction") stays attached to the new output. An
evaluation older than its run is therefore treated as stale and redone; log_evaluation
upserts by (run, name). The correctness judge is the only paid call.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from phoenix.client import Client

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_experiments import CODE_EVALUATORS, RESULTS  # noqa: E402

from research_agent import Settings  # noqa: E402
from research_agent.evals import Judge  # noqa: E402


def _ts(value) -> datetime:
    return value if isinstance(value, datetime) else datetime.fromisoformat(value)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="research-bench-25")
    p.add_argument("--tag", required=True)
    args = p.parse_args()

    client = Client(base_url=os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006"))
    dataset = client.datasets.get_dataset(dataset=args.dataset)
    examples = {ex["id"]: ex for ex in dataset.examples}
    judge = Judge(Settings())
    code = {fn.__name__: fn for fn in CODE_EVALUATORS}
    wanted = ["correctness", *code]

    results_path = RESULTS / f"{args.tag}.jsonl"
    records = [json.loads(line) for line in open(results_path)]
    by_key = {(r["controller"], r["id"]): r for r in records}

    jobs = []
    for exp in client.experiments.list(dataset_id=dataset.id):
        if not exp["name"].endswith(f"[{args.tag}]"):
            continue
        controller = exp["metadata"]["controller"]
        ran = client.experiments.get_experiment(experiment_id=exp["id"])
        started = {r["id"]: _ts(r["start_time"]) for r in ran["task_runs"]}
        done = {(e.experiment_run_id, e.name) for e in ran["evaluation_runs"]
                if not e.error and e.experiment_run_id in started
                and _ts(e.start_time) >= started[e.experiment_run_id]}
        for run in ran["task_runs"]:
            if run["error"] or run["output"] is None:
                continue
            for name in wanted:
                if (run["id"], name) not in done:
                    jobs.append((controller, run, name))

    print(f"{len(jobs)} missing evaluations "
          f"({sum(j[2] == 'correctness' for j in jobs)} need the judge)")

    def do(job):
        controller, run, name = job
        ex = examples[run["dataset_example_id"]]
        output = run["output"]
        if name == "correctness":
            j = judge(ex["input"]["question"], ex["output"]["answer"], output.get("answer", ""))
            client.experiments.log_evaluation(
                experiment_run_id=run["id"], name=name, annotator_kind="LLM",
                score=j.score, label=j.label, explanation=j.explanation, trace_id=run["trace_id"],
            )
            rec = by_key.get((controller, ex["metadata"]["id"]))
            if rec is not None:
                rec["judge"] = {"label": j.label, "explanation": j.explanation,
                                "cost_usd": j.cost_usd}
            return j.cost_usd
        value = code[name](output)
        client.experiments.log_evaluation(
            experiment_run_id=run["id"], name=name, annotator_kind="CODE",
            score=float(value) if value is not None else None,
        )
        return 0.0

    with ThreadPoolExecutor(max_workers=8) as pool:
        cost = sum(pool.map(do, jobs))

    with open(results_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, default=str, ensure_ascii=False) + "\n")
    print(f"logged {len(jobs)} evaluations; judge cost ${cost:.4f}; "
          f"unjudged records left: {sum('judge' not in r for r in records)}")


if __name__ == "__main__":
    main()
