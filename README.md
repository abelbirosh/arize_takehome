# Can a decision model route a research agent?

A research agent where a cheap **decision model** picks each next step (search Wikipedia, search the web, read a result, or answer) and a general LLM writes the text. It's benchmarked in [Phoenix](https://phoenix.arize.com) against Claude deciders and a fixed sequence.

**Presentation:** [arizetakehome.vercel.app](https://arizetakehome.vercel.app)

## Result

50 questions × 7 deciders = 350 runs (`results/full-v2-merged.jsonl`). Claude Haiku 5.5 writes every query, note and answer, so only the decider changes between runs.

| Decider | Kind | Accuracy | $/run | Routing $/run | Active s/run |
|---|---|---|---|---|---|
| Jev (TypeSafe) | decision model | 70% | 0.0019 | 0.0004 | 21.7 |
| Microsoft Decision 1 | decision model | 72% | 0.0020 | 0.0003 | 21.9 |
| OpenAI GPT-6 Luna Decisions | decision model | 66% | 0.0022 | 0.0007 | 23.3 |
| Claude Haiku 5.5 | LLM, JSON reply | 66% | 0.0028 | 0.0014 | n/a* |
| Claude Sonnet 5.5 | LLM, JSON reply | 66% | 0.0219 | 0.0204 | 32.4 |
| Claude Opus 5.5 | LLM, JSON reply | 60% | 0.0433 | 0.0420 | 37.4 |
| Fixed sequence | no model | 72% | 0.0024 | 0 | 26.3 |

Decision models matched or beat the Claude deciders on accuracy at a fraction of the routing cost and latency. On this suite, a fixed search → read → answer sequence was just as accurate.

\* One Haiku routing call stalled for 2.2 hours, which skews its mean latency.

## How it works

| Step | Who decides | Output |
|---|---|---|
| Next action: `search_wikipedia` / `search_web` / `read_source` / `answer` | decider | choice + probabilities |
| Which unread result to read next | decider | choice over result ids |
| Search query, notes from a source, final answer | Haiku 5.5 | text |

Every decider sees the same structured state (`AgentState.snapshot()`) and runs under the same guards: an 8-step budget, a forced answer on the last step, and a fallback for invalid or repeated reads. Each run is traced to Phoenix and scored by:

- an LLM judge for correctness and groundedness;
- a code check for routing fit;
- code evaluators for cost, latency, steps, forced answers and invalid decisions.

## Repository

```
src/research_agent/   agent loop, controllers (deciders), LLM wrapper, tools, tracing, judges
scripts/              dataset prep, Phoenix experiments, resume/backfill, analysis, chart export
data/                 question suites (v1: 25, v2: 50) and candidate pools
results/              every run's answer, steps, stats and grades (.jsonl) plus raw logs
frontend/             the presentation (React + Vite, deployed on Vercel)
tests/                agent, controller, evaluator, tool and tracing tests with fakes
docs/                 the original v1 benchmark plan
```

## Run it

Requires Python 3.12+ with [uv](https://docs.astral.sh/uv/), an OpenRouter key (covers Jev and every LLM), and the [TinyFish](https://tinyfish.ai) CLI for web search (`tinyfish auth login`).

```bash
uv sync
cp .env.example .env                              # add OPENROUTER_API_KEY
uv run pytest                                     # offline; uses fakes
```

Ask one question:

```bash
uv run research-agent "Who was the UK prime minister when the author of The Coal Question died?" --controller jev
```

`--controller` accepts `jev`, `msft`, `oai`, `claude-haiku-5.5`, `claude-sonnet-5.5`, `claude-opus-5.5`, `fixed`, `llm` or `hybrid`. Add `--trace` to send spans to Phoenix.

Reproduce the benchmark (this makes paid model calls, about $4 for the full v2 grid):

```bash
uv run phoenix serve                                              # http://localhost:6006
uv run python scripts/register_pricing.py                         # OpenRouter prices for Phoenix cost columns
uv run python scripts/prepare_dataset.py --suite v2 --upload
uv run python scripts/run_experiments.py --dataset research-bench-50-pilot --tag pilot-v2   # 7 questions
uv run python scripts/run_experiments.py --dataset research-bench-v2 --split main --tag full-v2   # other 43
uv run python scripts/merge_pilot.py                              # -> results/full-v2-merged.jsonl
uv run python scripts/analyze.py results/full-v2-merged.jsonl     # summary tables, no model calls
```

The presentation runs on Node 22.12+:

```bash
npm install
npm run dev
python3 scripts/export_frontend_metrics.py      # regenerate the charts from results/
```

See [frontend/README.md](frontend/README.md) for the content files.
