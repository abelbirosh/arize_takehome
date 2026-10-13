# Benchmark plan (v1)

> Superseded by the v2 suite: 50 questions, 7 deciders including Microsoft and OpenAI decision models, and groundedness and routing-fit evaluators. The v2 results and how to rerun them are in the [README](../README.md). This page records the original 25-question plan.

**Question:** can a $0.04/M-token decision model (Jev) make a research agent's routing decisions as well as Claude models of increasing size, and what does each cost in accuracy, money and latency?

## Grid

The generator is fixed: **Claude Haiku 5.5** writes the queries, notes and answers in every run. Only the routing decider changes:

| Controller | Decider | $/M input / output |
|---|---|---|
| `jev` | TypeSafe Jev 1.13 (System One decision model) | $0.042 / free |
| `claude-haiku-5.5` | Claude Haiku 5.5, JSON reply | $0.10 / $0.50 |
| `claude-sonnet-5.5` | Claude Sonnet 5.5, JSON reply | $2 / $10 |
| `claude-opus-5.5` | Claude Opus 5.5, JSON reply | $4 / $20 |
| `fixed` | none: search Wikipedia → read 2 → search web → read 2 → answer | — |

25 questions × 5 controllers = **125 runs**, one repetition, as 5 Phoenix experiments on the dataset `research-bench-25`.

**Held constant:** tools (Wikipedia + TinyFish web), 8-step budget, prompts, `LLM_REASONING=low`, temperature 0.

**Judge:** `openai/gpt-6.1-sol`. It compares the short answer against the gold answer: correct / incorrect / no_answer.

## Dataset (25)

- **15 fresh**: events after the models' training cutoffs (2026 Nobel Prizes, 2026 World Cup, US Open, Tour de France, Apple's September event, TypeSafe's Jev launch). Answers verified against primary sources (`evidence` in `data/benchmark.jsonl`).
- **10 FRAMES** (google/frames-benchmark): 2 per reasoning type. Each needs 2–4 Wikipedia articles and has a short, unambiguous gold answer. Questions the models answered from memory in a partial closed-book screen were avoided.

## Metrics (Phoenix evaluators)

| Evaluator | Meaning |
|---|---|
| `correctness` | LLM judge vs gold |
| `total_cost_usd`, `routing_cost_usd` | OpenRouter-reported cost; routing cost = decider only |
| `latency_s`, `routing_latency_ms` | active time, excluding queueing behind the shared rate limiter |
| `steps`, `forced_answer` | steps taken; whether the 8-step budget forced the answer |
| `invalid_decisions` | unparseable or impossible LLM decisions (Claude deciders) |
| `used_web_search` | whether the run searched the web at all |

Jev's `evidence_sufficient` and `next_action` confidence are logged per step, for calibration analysis (`scripts/analyze.py`).

## Pilot (2 questions × 5 controllers)

$0.21 for 10 runs. Measured per run: Jev $0.0009, Haiku $0.0027, Sonnet $0.018, Opus $0.076, fixed $0.0022, judge ~$0.0007. Projected full run: ~$2.60.

## Status

- [x] Controllers, dataset, metrics agreed
- [x] Pilot
- [x] Full run (`full-v1`). Interrupted by a network outage while the machine slept, then finished with `--resume` and `scripts/backfill_evals.py` (`results/full-v1*.{jsonl,log}`).
- [x] Superseded by v2 (`results/full-v2-merged.jsonl`)
