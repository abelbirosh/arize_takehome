"""Closed-book screen: can the models answer a question with no retrieval at all?

Questions most models answer from memory say little about research routing,
so the benchmark prefers ones they can't.

    uv run python scripts/screen_closed_book.py data/candidates.jsonl data/screen.jsonl
"""

from __future__ import annotations

import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from research_agent.config import Settings
from research_agent.evals import Judge
from research_agent.llm import LLM

MODELS = [
    "anthropic/claude-haiku-5.5",
    "openai/gpt-6-luna",
    "google/gemini-3.8-flash",
    "deepseek/deepseek-v4.1-flash",
]

SYSTEM = ("Answer the question from your own knowledge; you have no tools. Think briefly, "
          "then end with a line `FINAL ANSWER: <concise answer>`. If you do not know, give "
          "your best guess.")


def closed_book(model: str, question: str) -> str:
    llm = LLM(Settings(), model=model)
    out = llm.complete("closed_book", SYSTEM, question, max_tokens=600)
    m = re.search(r"FINAL ANSWER:\s*(.+)", out, flags=re.I)
    return m.group(1).strip() if m else out.strip()[-300:]


def screen(item: dict, judge: Judge) -> dict:
    preds = {}
    for model in MODELS:
        try:
            preds[model] = closed_book(model, item["question"])
        except Exception as e:  # keep screening other models
            preds[model] = f"ERROR: {e}"[:300]
    try:
        labels = judge.batch(item["question"], item["answer"], preds)
    except Exception as e:
        labels = {m: f"judge_error: {e}"[:200] for m in MODELS}
    results = {m: {"prediction": preds[m], "label": labels[m]} for m in MODELS}
    n_correct = sum(r["label"] == "correct" for r in results.values())
    return {**item, "closed_book": results, "closed_book_correct": n_correct}


def main(src: str, dst: str) -> None:
    """Resumable: items already in `dst` are skipped; each result is appended as it lands."""
    items = [json.loads(line) for line in open(src)]
    try:
        done = {json.loads(line)["id"] for line in open(dst)}
    except FileNotFoundError:
        done = set()
    todo = [it for it in items if it["id"] not in done]
    print(f"{len(done)} already screened, {len(todo)} to go", flush=True)
    judge, lock = Judge(), threading.Lock()
    with ThreadPoolExecutor(max_workers=8) as pool, open(dst, "a") as f:
        for fut in as_completed(pool.submit(screen, it, judge) for it in todo):
            row = fut.result()
            with lock:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
            print(f"{row['closed_book_correct']}/4  {row['id']:>12}  {row['question'][:90]}",
                  flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
