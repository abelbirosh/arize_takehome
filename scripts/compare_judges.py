"""Run several judges on the human-graded sample and score each against the human labels.

    uv run python scripts/compare_judges.py            # paid: 2 calls per run per new judge

Judges: GPT-6.1 Sol at low effort (the benchmark's judge; its grades are already in the
results), GPT-6.1 Sol at high effort, Claude Opus 5.5, and the decision models Jev,
Microsoft-Decision-1 and GPT-6 Luna Decisions. Every grade is appended to
results/human_validation/judges.jsonl as it lands, so a rerun only pays for what is
missing or failed. Writes judge_comparison.json there and frontend/public/judges.json.
"""

from __future__ import annotations

import csv
import json
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from score_validation import cohen_kappa

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "results/human_validation"

# id -> (display name, kind, how it is called)
JUDGES = {
    "sol-low": ("GPT-6.1 Sol, low effort", "reasoning", "benchmark judge"),
    "sol-high": ("GPT-6.1 Sol, high effort", "reasoning", "openai/gpt-6.1-sol"),
    "opus": ("Claude Opus 5.5", "reasoning", "anthropic/claude-opus-5.5"),
    "jev": ("Jev (TypeSafe)", "decision", "jev"),
    "msft": ("Microsoft Decision 1", "decision", "msft"),
    "oai": ("OpenAI GPT-6 Luna Decisions", "decision", "oai"),
}

_lock = threading.Lock()


def _load(cache: Path, name: str) -> dict[int, dict]:
    done: dict[int, dict] = {}
    if cache.exists():
        for line in cache.read_text().splitlines():
            row = json.loads(line)
            if row["judge"] == name:
                done[row["n"]] = row  # the last grade of a run wins
    return done


def _grade(name: str, judge, t: dict) -> dict:
    row = {"judge": name, "n": t["n"], "cost_usd": 0.0, "latency_ms": 0.0}
    calls = {
        "correctness": lambda: judge.correctness(t["question"], t["gold"], t["accepted"],
                                                 t["answerable"], t["predicted"]),
        "grounded": lambda: judge.grounded(t["question"], t["predicted"], t["notes"]),
    }
    for check, call in calls.items():
        try:
            j = call()
            row[check] = j.label
            row["cost_usd"] += j.cost_usd
            row["latency_ms"] += j.latency_ms
        except Exception as e:  # noqa: BLE001 -- one failed call should not lose the rest
            row[check] = "error"
            row.setdefault("errors", []).append(f"{check}: {str(e)[:200]}")
    return {k: row[k] for k in ("judge", "n", "correctness", "grounded", "cost_usd",
                                "latency_ms", "errors") if k in row}


def run_judge(name: str, judge, tasks: list[dict], cache: Path, workers: int = 4) -> list[dict]:
    done = _load(cache, name)
    todo = [t for t in tasks if t["n"] not in done
            or "error" in (done[t["n"]]["correctness"], done[t["n"]]["grounded"])]

    def work(t: dict) -> None:
        row = _grade(name, judge, t)
        with _lock:
            with cache.open("a") as f:
                f.write(json.dumps(row) + "\n")
            done[t["n"]] = row

    with ThreadPoolExecutor(workers) as pool:
        list(pool.map(work, todo))
    return [done[t["n"]] for t in sorted(tasks, key=lambda t: t["n"])]


def _agree(pairs: list[tuple[str, str]]) -> tuple[float | None, float | None]:
    if not pairs:
        return None, None
    judge, human = zip(*pairs)
    return (sum(j == h for j, h in pairs) / len(pairs), cohen_kappa(list(judge), list(human)))


def summarize(rows: list[dict], human: dict[int, tuple[str, str]]) -> list[dict]:
    """Agreement with the human, per judge; failed calls are left out of their check."""
    by_judge: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_judge[r["judge"]].append(r)
    out = []
    for name, rs in by_judge.items():
        corr = [(r["correctness"], human[r["n"]][0]) for r in rs if r["correctness"] != "error"]
        binary = [(str(j == "correct"), str(h == "correct")) for j, h in corr]
        grnd = [(r["grounded"], human[r["n"]][1]) for r in rs if r["grounded"] != "error"]
        latencies = [r["latency_ms"] for r in rs if r.get("latency_ms") is not None]
        c_agree, c_kappa = _agree(corr)
        b_agree, b_kappa = _agree(binary)
        g_agree, g_kappa = _agree(grnd)
        out.append({
            "judge": name, "n": len(rs), "correctness_n": len(corr), "grounded_n": len(grnd),
            "correctness_agree": c_agree, "correctness_kappa": c_kappa,
            "counts_as_correct_agree": b_agree, "counts_as_correct_kappa": b_kappa,
            "grounded_agree": g_agree, "grounded_kappa": g_kappa,
            "cost_per_grade": sum(r["cost_usd"] for r in rs) / len(rs) / 2,
            "latency_per_grade_ms": (sum(latencies) / len(latencies) / 2) if latencies else None,
        })
    return out


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build(results: Path, suite_path: Path) -> tuple[list[dict], dict, list[dict]]:
    """The 25 tasks, the human labels, and the benchmark judge's existing grades."""
    keys = _read_csv(DIR / "key.csv")
    labels = {int(r["n"]): (r["human_correctness"], r["human_grounded"])
              for r in _read_csv(DIR / "labels.csv")}
    runs = {(r["controller"], r["id"]): r for r in map(json.loads, results.open())}
    suite = {q["id"]: q for q in map(json.loads, suite_path.open())}
    tasks, existing = [], []
    for k in keys:
        run, q = runs[(k["controller"], k["id"])], suite[k["id"]]
        n = int(k["n"])
        tasks.append({"n": n, "question": run["question"], "gold": q["answer"],
                      "accepted": q["accepted"], "answerable": q.get("answerable", True),
                      "predicted": run["answer"], "notes": run.get("notes") or []})
        existing.append({"judge": "sol-low", "n": n, "correctness": run["judge"]["label"],
                         "grounded": (run.get("grounded") or {}).get("label", "error"),
                         "cost_usd": run["judge"].get("cost_usd", 0.0)
                         + (run.get("grounded") or {}).get("cost_usd", 0.0),
                         "latency_ms": None})
    return tasks, labels, existing


def main() -> None:
    from research_agent import Settings
    from research_agent.evals import DecisionJudge, Judge

    settings = Settings()
    judges = {
        "sol-high": Judge(settings, "openai/gpt-6.1-sol", effort="high"),
        "opus": Judge(settings, "anthropic/claude-opus-5.5", effort="low"),
        "jev": DecisionJudge(settings, "jev"),
        "msft": DecisionJudge(settings, "msft"),
        "oai": DecisionJudge(settings, "oai"),
    }
    tasks, human, rows = build(ROOT / "results/full-v2-merged.jsonl",
                               ROOT / "data/benchmark_v2.jsonl")
    cache = DIR / "judges.jsonl"
    with ThreadPoolExecutor(len(judges)) as pool:
        graded = pool.map(lambda kv: run_judge(kv[0], kv[1], tasks, cache), judges.items())
        for g in graded:
            rows += g
    summary = summarize(rows, human)
    for s in summary:
        s["name"], s["kind"], s["model"] = JUDGES[s["judge"]]
    summary.sort(key=lambda s: list(JUDGES).index(s["judge"]))
    errors = [r for r in rows if "error" in (r["correctness"], r["grounded"])]
    payload = {"runs": len(tasks), "judges": summary}
    (DIR / "judge_comparison.json").write_text(json.dumps(payload, indent=1) + "\n")
    (ROOT / "frontend/public/judges.json").write_text(json.dumps(payload, indent=1) + "\n")
    for s in summary:
        lat = s["latency_per_grade_ms"]
        print(f"{s['name']:<30} corr {s['correctness_agree']:.0%} k={s['correctness_kappa']:.2f}  "
              f"grounded {s['grounded_agree']:.0%} k={s['grounded_kappa']:.2f}  "
              f"${s['cost_per_grade']:.5f}/grade  {'-' if lat is None else f'{lat:.0f} ms'}")
    if errors:
        print(f"{len(errors)} runs still have a failed call; rerun to retry them")


if __name__ == "__main__":
    main()
