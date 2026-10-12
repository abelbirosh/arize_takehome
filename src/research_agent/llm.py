"""The general-purpose LLM: writes queries, reads sources, writes answers.

Any OpenAI-compatible endpoint works; OpenRouter is the default so one key
covers every provider in the benchmark grid. Calls are auto-traced by the
OpenInference OpenAI instrumentor.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

from openai import OpenAI

from research_agent.config import Settings
from research_agent.state import AgentState, Candidate, Origin

NOTHING = "NOTHING_RELEVANT"
# Reasoning tokens count against max_tokens, so leave room for them on top of
# the visible output. Unused headroom is not billed.
REASONING_HEADROOM = 2048

log = logging.getLogger(__name__)


@dataclass
class Usage:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    empty_replies: int = 0
    by_purpose: dict[str, int] = field(default_factory=dict)


class LLM:
    def __init__(self, settings: Settings, model: str | None = None, client: OpenAI | None = None):
        self.model = model or settings.llm_model
        self.client = client or OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)
        self.reasoning = settings.llm_reasoning
        self._openrouter = "openrouter.ai" in settings.llm_base_url
        self.usage = Usage()

    def _extra_body(self) -> dict | None:
        if not self._openrouter:
            return None
        # Some models (e.g. Gemini 3.8 Flash) cannot disable reasoning, so the
        # benchmark default is a uniform low effort rather than "off".
        reasoning = ({"enabled": False} if self.reasoning == "off"
                     else {"effort": self.reasoning})
        return {"usage": {"include": True}, "reasoning": reasoning}

    def complete(self, purpose: str, system: str, user: str, max_tokens: int = 1024) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0,
            max_tokens=max_tokens + (0 if self.reasoning == "off" else REASONING_HEADROOM),
            extra_body=self._extra_body(),
        )
        self._track(purpose, resp)
        content = (resp.choices[0].message.content or "").strip()
        if not content:
            log.warning("%s: empty reply from %s (finish_reason=%s)", purpose, self.model,
                        resp.choices[0].finish_reason)
            self.usage.empty_replies += 1
        return content

    def _track(self, purpose: str, resp) -> None:
        u = self.usage
        u.calls += 1
        u.by_purpose[purpose] = u.by_purpose.get(purpose, 0) + 1
        if resp.usage:
            u.input_tokens += resp.usage.prompt_tokens or 0
            u.output_tokens += resp.usage.completion_tokens or 0
            cost = (resp.usage.model_extra or {}).get("cost")
            if isinstance(cost, (int, float)):
                u.cost_usd += cost

    # --- Generation tasks -------------------------------------------------

    def write_query(self, state: AgentState, engine: Origin) -> str:
        where = "Wikipedia's search box" if engine is Origin.WIKIPEDIA else "a web search engine"
        prior = [s.query for s in state.searches] or ["(none)"]
        notes = "\n".join(f"- [{n.title}] {n.facts}" for n in state.notes) or "(none yet)"
        text = self.complete(
            "write_query",
            system=(
                f"You write one search query for {where} to find the information still "
                "missing to answer a research question. Target the single most important "
                "missing fact. Do not repeat a previous query. Reply with the query only."
            ),
            user=(
                f"Question: {state.question}\n\nNotes so far:\n{notes}\n\n"
                f"Previous queries: {'; '.join(prior)}"
            ),
            max_tokens=64,
        )
        # Models with reasoning off sometimes narrate first; the query is the last line.
        lines = [ln.strip().strip('"`') for ln in text.splitlines() if ln.strip()]
        query = re.sub(r"^(search\s+)?query\s*:\s*", "", lines[-1], flags=re.I) if lines else ""
        return query.strip('"`') or state.question

    def extract_notes(self, state: AgentState, candidate: Candidate, text: str) -> str:
        if not text.strip():
            return ""
        notes = "\n".join(f"- [{n.title}] {n.facts}" for n in state.notes) or "(none yet)"
        out = self.complete(
            "extract_notes",
            system=(
                "You read a source for a research agent and record the facts in it that "
                "help answer its question: names, dates, numbers, relationships. Questions "
                "are often multi-step, so also record bridging facts that would become "
                "decisive once another part is resolved (e.g. who held a role and over "
                "which dates, even if the date that matters is not yet known). Write terse "
                "bullet points, quote exact figures, and do not repeat facts already in the "
                f"notes. If nothing in the source is relevant, reply exactly {NOTHING}."
            ),
            user=(
                f"Question: {state.question}\n\nNotes so far:\n{notes}\n\n"
                f"Source: {candidate.title} ({candidate.url})\n\n{text}"
            ),
            max_tokens=500,
        )
        return "" if NOTHING in out else out

    def write_answer(self, state: AgentState) -> tuple[str, str]:
        """Returns (full answer with reasoning, short final answer)."""
        notes = "\n\n".join(f"[{n.title}]({n.url})\n{n.facts}" for n in state.notes)
        out = self.complete(
            "write_answer",
            system=(
                "You answer a research question using the research notes provided. Reason "
                "briefly from the notes, citing sources by title. If the notes are "
                "insufficient, give your best answer and say what is uncertain. End with a "
                "final line of the form `FINAL ANSWER: <concise answer>`."
            ),
            user=f"Question: {state.question}\n\nResearch notes:\n{notes or '(no notes collected)'}",
            max_tokens=800,
        )
        m = re.search(r"FINAL ANSWER:\s*(.+)", out, flags=re.IGNORECASE)
        return out, (m.group(1).strip() if m else out.strip().splitlines()[-1] if out else "")

    # --- Routing (LLM-as-controller baseline) -----------------------------

    def decide(self, snapshot: dict, action_help: dict[str, str]) -> str:
        options = "\n".join(f"- {k}: {v}" for k, v in action_help.items())
        return self.complete(
            "decide",
            system=(
                "You are the controller of a research agent. Given the agent's state, pick "
                f"its next action from exactly these options:\n{options}\n\n"
                "If you pick read_source, also give the id of one entry in `unread_sources`. "
                'Reply with a JSON object only: {"action": "...", "target": "<id or null>", '
                '"reason": "<one sentence>"}'
            ),
            user=json.dumps(snapshot, ensure_ascii=False),
            max_tokens=200,
        )
