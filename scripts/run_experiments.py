"""Run the benchmark as Phoenix experiments: one experiment per controller.

    uv run python scripts/run_experiments.py --dataset research-bench-50-pilot
    uv run python scripts/run_experiments.py --dataset research-bench-50 --tag full-v2
    uv run python scripts/run_experiments.py --dataset research-bench-50 --tag full-v2 --resume

Every controller answers the same dataset; Haiku 5.5 generates in every run, so
only the routing decider differs. Each run is judged for correctness and
groundedness and scored on cost, latency, steps and routing behaviour; results
land in Phoenix (compare view) and in results/<tag>.jsonl.

v2 datasets (category / answerable / needs_web metadata, accepted answer variants)
get the v2 evaluators; v1 datasets keep the original correctness judge.
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

import openai
from phoenix.client import Client
from phoenix.client.experiments import create_evaluator

from research_agent import Settings, build_agent
from research_agent.controllers import DECISION_MODELS, LLM_DECIDERS
from research_agent.evals import Judge
from research_agent.tracing import setup_tracing

CONTROLLERS = ["jev", "msft", "oai", "claude-haiku-5.5", "claude-sonnet-5.5",
               "claude-opus-5.5", "fixed"]
RESULTS = Path(__file__).resolve().parent.parent / "results"

_lock = threading.Lock()
_records: list[dict] = []
_judge_cost = 0.0


def make_task(controller: str, settings: Settings):
    def task(input, metadata):  # noqa: A002 - Phoenix binds by parameter name
        agent = build_agent(controller, settings=settings)
        result = agent.run(input["question"])
        steps = [
            {
                "step": s.index, "action": s.decision.action.value,
                "model": s.decision.model, "target": s.decision.target_id,
                "confidence": s.decision.confidence,
                "evidence_sufficient": s.decision.evidence_sufficient,
                "latency_ms": round(s.decision.latency_ms, 1),
                "cost_usd": s.decision.cost_usd, "valid": s.decision.valid,
                "forced": s.decision.forced, "detail": s.detail[:200],
            }
            for s in result.steps
        ]
        notes = [{"title": n.title, "url": n.url, "facts": n.facts} for n in result.notes]
        out = {"answer": result.answer, "full_answer": result.full_answer,
               "stats": result.stats, "steps": steps, "notes": notes}
        with _lock:
            _records.append({"controller": controller, "id": metadata.get("id"),
                             "source": metadata.get("source"),
                             "category": metadata.get("category"),
                             "question": input["question"], **out})
        return out
    return task


def _attach(controller: str, example_id: str | None, key: str, judgement) -> None:
    global _judge_cost
    with _lock:
        _judge_cost += judgement.cost_usd
        for r in _records:
            if r["controller"] == controller and r["id"] == example_id:
                r[key] = asdict(judgement)


def _result(j) -> dict:
    out = {"label": j.label, "explanation": j.explanation}
    if j.score is not None:
        out["score"] = j.score
    return out


def make_correctness(judge: Judge, controller: str):
    @create_evaluator(kind="LLM", name="correctness")
    def correctness(input, output, expected, metadata):  # noqa: A002
        predicted = (output or {}).get("answer", "")
        if "accepted" in expected:  # v2 dataset
            j = judge.correctness(input["question"], expected["answer"], expected["accepted"],
                                  metadata.get("answerable", True), predicted)
        else:
            j = judge(input["question"], expected["answer"], predicted)
        _attach(controller, metadata.get("id"), "judge", j)
        return _result(j)
    return correctness


def make_grounded(judge: Judge, controller: str):
    @create_evaluator(kind="LLM", name="grounded")
    def grounded(input, output, metadata):  # noqa: A002
        output = output or {}
        j = judge.grounded(input["question"], output.get("answer", ""), output.get("notes", []))
        _attach(controller, metadata.get("id"), "grounded", j)
        return _result(j)
    return grounded


def routing_fit(output, metadata):
    """Did it search where the question category needs it? Web for recent or too-new
    questions, Wikipedia first for FRAMES."""
    if "needs_web" not in metadata:
        return {"label": "not_applicable"}
    actions = [s["action"] for s in (output or {}).get("steps", [])]
    searches = [a for a in actions if a in ("search_web", "search_wikipedia")]
    if metadata["needs_web"]:
        fit = "search_web" in searches
    else:
        fit = bool(searches) and searches[0] == "search_wikipedia"
    return {"score": 1.0 if fit else 0.0, "label": "fit" if fit else "misfit"}


# Free, code-based evaluators over the agent's own accounting.
def _stat(name):
    def evaluator(output):
        return (output or {}).get("stats", {}).get(name)
    # Phoenix names evaluators by __qualname__; without this every closure is "evaluator".
    evaluator.__name__ = evaluator.__qualname__ = name
    return evaluator


def forced_answer(output):
    return 1.0 if (output or {}).get("stats", {}).get("forced_answer") else 0.0


def used_web_search(output):
    return 1.0 if (output or {}).get("stats", {}).get("used_web_search") else 0.0


def latency_s(output):
    """Active seconds: wall time minus queueing behind the shared rate limiter."""
    return ((output or {}).get("stats", {}).get("active_ms") or 0) / 1000


CODE_EVALUATORS = [
    _stat("total_cost_usd"), _stat("routing_cost_usd"), _stat("routing_latency_ms"),
    _stat("steps"), _stat("invalid_decisions"), latency_s, forced_answer, used_web_search,
]


def evaluators_for(judge: Judge, controller: str) -> list:
    """Correctness (v1 or v2 by dataset) + groundedness + routing fit + code stats.
    On v1 datasets, grounded still works; routing_fit reports not_applicable."""
    return [make_correctness(judge, controller), make_grounded(judge, controller),
            routing_fit, *CODE_EVALUATORS]


def run_one(client: Client, dataset, controller: str, settings: Settings, judge: Judge,
            tag: str):
    decider = LLM_DECIDERS.get(controller) or DECISION_MODELS.get(controller)
    decider = getattr(decider, "model_id", decider) or controller
    return client.experiments.run_experiment(
        dataset=dataset,
        task=make_task(controller, settings),
        evaluators=evaluators_for(judge, controller),
        experiment_name=f"{controller} [{tag}]",
        experiment_description=f"Decider: {decider}; generator: {settings.llm_model}",
        experiment_metadata={
            "controller": controller, "decider": decider,
            "generator": settings.llm_model, "max_steps": settings.max_steps,
            "reasoning": settings.llm_reasoning, "judge": judge.model,
        },
        rate_limit_errors=openai.RateLimitError,
        timeout=900,
        retries=0,  # a retry would re-spend; failures are recorded instead
        print_summary=False,
    )


def resume_one(client: Client, experiment: dict, settings: Settings, judge: Judge) -> None:
    """Re-run only the failed/missing runs of an experiment, then judge the new ones."""
    controller = experiment["metadata"]["controller"]
    client.experiments.resume_experiment(
        experiment_id=experiment["id"], task=make_task(controller, settings),
        rate_limit_errors=openai.RateLimitError, timeout=900, retries=0,
        print_summary=False,
    )
    client.experiments.resume_evaluation(
        experiment_id=experiment["id"],
        evaluators=evaluators_for(judge, controller),
        rate_limit_errors=openai.RateLimitError, timeout=300, retries=0,
        print_summary=False,
    )


def summarize(records: list[dict]) -> None:
    print(f"\n{'controller':18} {'n':>3} {'acc':>5} {'hedged':>6} {'grnd':>5} {'$/run':>8} "
          f"{'route$':>8} {'active s':>8} {'steps':>6} {'forced':>6} {'invalid':>7}")
    for c in CONTROLLERS:
        rs = [r for r in records if r["controller"] == c]
        if not rs:
            continue
        n = len(rs)
        mean = lambda k: sum(r["stats"][k] or 0 for r in rs) / n  # noqa: E731
        label = lambda r, k: r.get(k, {}).get("label")  # noqa: E731
        acc = sum(label(r, "judge") == "correct" for r in rs) / n
        hedged = sum(label(r, "judge") == "hedged" for r in rs)
        claims = [r for r in rs if label(r, "grounded") in ("supported", "unsupported")]
        grnd = (sum(label(r, "grounded") == "supported" for r in claims) / len(claims)
                if claims else 0)
        print(f"{c:18} {n:>3} {acc:>5.0%} {hedged:>6} {grnd:>5.0%} "
              f"{mean('total_cost_usd'):>8.4f} {mean('routing_cost_usd'):>8.4f} "
              f"{mean('active_ms') / 1000:>8.1f} {mean('steps'):>6.1f} "
              f"{sum(r['stats']['forced_answer'] for r in rs):>6} "
              f"{sum(r['stats']['invalid_decisions'] for r in rs):>7}")
    agent_cost = sum(r["stats"]["total_cost_usd"] for r in records)
    print(f"\nagent cost ${agent_cost:.4f} + judges ${_judge_cost:.4f} "
          f"= ${agent_cost + _judge_cost:.4f} for {len(records)} runs")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="research-bench-pilot")
    p.add_argument("--controllers", nargs="*", default=CONTROLLERS)
    p.add_argument("--tag", default=None, help="label for experiment names / results file")
    p.add_argument("--resume", action="store_true",
                   help="re-run only failed/missing runs of the experiments tagged --tag")
    args = p.parse_args()

    settings = Settings()
    setup_tracing(settings.phoenix_project)
    client = Client(base_url=os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006"))
    dataset = client.datasets.get_dataset(dataset=args.dataset)
    tag = args.tag or f"{args.dataset} {time.strftime('%m-%d %H:%M')}"
    judge = Judge(settings)

    if args.resume:
        experiments = [e for e in client.experiments.list(dataset_id=dataset.id)
                       if e["name"].endswith(f"[{tag}]")
                       and e["metadata"].get("controller") in args.controllers
                       and (e["failed_run_count"] or e["missing_run_count"])]
        for e in experiments:
            print(f"resume {e['name']}: {e['failed_run_count']} failed, "
                  f"{e['missing_run_count']} missing")
        jobs = {e["metadata"]["controller"]: (resume_one, client, e, settings, judge)
                for e in experiments}
    else:
        print(f"{len(dataset.examples)} examples x {len(args.controllers)} controllers "
              f"= {len(dataset.examples) * len(args.controllers)} runs  [{tag}]")
        jobs = {c: (run_one, client, dataset, c, settings, judge, tag) for c in args.controllers}

    with ThreadPoolExecutor(max_workers=max(1, len(jobs))) as pool:
        futures = {c: pool.submit(*job) for c, job in jobs.items()}
        for c, f in futures.items():
            try:
                f.result()
            except Exception as e:  # one controller failing shouldn't sink the rest
                print(f"!! {c} failed: {e!r}")

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"{tag.replace(' ', '_').replace(':', '')}.jsonl"
    with open(out, "a" if args.resume else "w") as f:
        for r in _records:
            f.write(json.dumps(r, default=str, ensure_ascii=False) + "\n")
    summarize(_records)
    print(f"\nrecords: {out}\nPhoenix: {client.experiments.get_dataset_experiments_url(dataset_id=dataset.id)}")


if __name__ == "__main__":
    main()
