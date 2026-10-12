# Jev-routed research agent

A research agent with **adaptive tool routing**. Each step, it chooses its next action (search Wikipedia, search the web, read a result, or answer) from what it has learned so far, instead of following a fixed sequence.

The experiment: give the *deciding* to [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), TypeSafe's "System One" decision model, and keep a general-purpose LLM for *generating*. Jev returns typed, calibrated probabilities instead of text, so it can't hallucinate an action or a source. It is also roughly 100× cheaper and faster per call than an LLM. Does that make a better agent controller? Phoenix is used to trace it and to benchmark it across controllers and LLM providers.

## Division of labour

| Step | Who | Shape |
|---|---|---|
| Next action: `search_wikipedia` / `search_web` / `read_source` / `answer` | **Jev** | `Choice` + probabilities |
| Which unread result to read next (asked speculatively, in the same call) | **Jev** | `Choice` over result ids |
| "Do the notes already answer the question?" (logged for calibration analysis) | **Jev** | `Noul` |
| Write the search query, take notes from a source, write the final answer | **LLM** | text |

All three Jev questions go in **one** request, are evaluated in parallel, and see the same structured state (`AgentState.snapshot()`): the question, budget, searches run, notes, unread results, and history.

## Controllers (the benchmark axis)

Only the decider changes. Query writing, note taking and answering always use the same LLM, so differences come from routing alone.

| `--controller` | Who decides |
|---|---|
| `jev` | Jev |
| `llm` | The LLM, replying in JSON (classic ReAct-style). Invalid replies (bad JSON, made-up actions or source ids) are counted and replaced by a fallback. |
| `hybrid` | Jev; if its `next_action` confidence is below `HYBRID_THRESHOLD`, the LLM decides that step |
| `fixed` | No model: search Wikipedia → read 2 → search web → read 2 → answer |

The harness applies the same guards to every controller: the last step of the budget is always `answer`, and a read target that's invalid or already read is replaced.

## Tracing (Phoenix / OpenInference)

```
research_agent                 AGENT     metadata: controller, llm_model
  step.N <action>              CHAIN
    route.<controller>         CHAIN     route.action / confidence / valid / escalated / latency
      jev.decide               DECISION  decision.* model + tokens, probabilities, evidence_sufficient
      ChatCompletion           LLM       (LLM controller only; auto-instrumented)
    wikipedia.search|web.search RETRIEVER retrieval.documents
    read_source                TOOL
    ChatCompletion             LLM       query / notes / answer
```

Jev calls use OpenInference's `DECISION` span kind, which exists for models that "score or select among candidate options supplied in the request rather than generating text".

## Setup

```bash
uv sync
cp .env.example .env   # add OPENROUTER_API_KEY
```

One OpenRouter key covers Jev (`/api/v1/systemone`) and every LLM provider. To call TypeSafe directly, unset `TYPESAFE_BASE_URL` and set `TYPESAFE_API_KEY`. Web search and fetch go through the [TinyFish](https://tinyfish.ai) CLI (`tinyfish auth login`). Wikipedia needs no key.

### Phoenix

```bash
uv run phoenix serve                            # UI + collector on http://localhost:6006
uv run python scripts/register_pricing.py       # teach Phoenix the OpenRouter model prices
```

Phoenix prices spans from its own model table, which doesn't know OpenRouter ids such as `anthropic/claude-haiku-5.5`. Without this step the cost columns show $0. Jev's cost is not priced by Phoenix, because decision spans report `decision.*` token counts rather than `llm.*`. The agent records it itself as `jev_cost_usd`. To use Phoenix Cloud instead, set `PHOENIX_COLLECTOR_ENDPOINT` and `PHOENIX_API_KEY` in `.env`.

## Run

```bash
uv run research-agent "Who was the prime minister of the UK when the author of The Coal Question died?" --controller jev
uv run research-agent "..." --controller llm --model openai/gpt-5.6-luna --trace   # send to Phoenix
uv run pytest
```

## Layout

```
src/research_agent/
  state.py        AgentState, Decision, StepRecord; snapshot() is what every controller sees
  controllers.py  Jev / LLM / hybrid / fixed controllers + shared action definitions
  agent.py        decide → act → observe loop, budget guard, per-run stats
  llm.py          OpenAI-compatible LLM wrapper (query, notes, answer, LLM routing)
  tools.py        Wikipedia (MediaWiki API) + web (TinyFish CLI), traced
  tracing.py      Phoenix registration + OpenInference tracer
  cli.py          single-question runner
tests/            fake Jev/LLM/tools; loop, guards, hybrid escalation, span tree
```
