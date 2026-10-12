"""The agent's working memory and the records it produces."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Action(StrEnum):
    SEARCH_WIKIPEDIA = "search_wikipedia"
    SEARCH_WEB = "search_web"
    READ_SOURCE = "read_source"
    ANSWER = "answer"


class Origin(StrEnum):
    WIKIPEDIA = "wikipedia"
    WEB = "web"


@dataclass
class Candidate:
    """A search result the agent may choose to read."""

    id: str
    origin: Origin
    title: str
    url: str
    snippet: str
    read: bool = False

    def brief(self) -> str:
        return f"{self.title} ({self.origin}) - {self.snippet}"


@dataclass
class Note:
    source_id: str
    title: str
    url: str
    facts: str


@dataclass
class Search:
    engine: Origin
    query: str
    n_results: int


@dataclass
class Decision:
    """One routing decision, from whichever controller made it."""

    action: Action
    controller: str
    target_id: str | None = None
    confidence: float | None = None
    probabilities: dict[str, float] = field(default_factory=dict)
    evidence_sufficient: float | None = None
    latency_ms: float = 0.0
    cost_usd: float = 0.0  # cost of this routing decision (Jev and/or LLM)
    jev_cost_usd: float = 0.0  # the Jev share, so totals don't double-count LLM usage
    valid: bool = True  # False if the controller produced an unusable answer
    forced: bool = False  # True if the harness overrode the controller (budget)
    escalated: bool = False  # True if the hybrid controller deferred to the LLM
    reason: str | None = None


@dataclass
class StepRecord:
    index: int
    decision: Decision
    detail: str  # query issued, source read, or answer written
    outcome: str


@dataclass
class AgentState:
    question: str
    max_steps: int
    candidates: list[Candidate] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    searches: list[Search] = field(default_factory=list)
    steps: list[StepRecord] = field(default_factory=list)
    _next_id: int = 1

    @property
    def steps_used(self) -> int:
        return len(self.steps)

    @property
    def steps_remaining(self) -> int:
        return self.max_steps - self.steps_used

    def unread(self, limit: int | None = None) -> list[Candidate]:
        out = [c for c in self.candidates if not c.read]
        return out[:limit] if limit else out

    def candidate(self, cid: str) -> Candidate | None:
        return next((c for c in self.candidates if c.id == cid), None)

    def add_candidates(self, origin: Origin, results: list[dict[str, str]]) -> list[Candidate]:
        """Add search results, skipping URLs already seen. Returns the new ones."""
        seen = {c.url for c in self.candidates}
        added = []
        for r in results:
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            c = Candidate(
                id=f"s{self._next_id}",
                origin=origin,
                title=r["title"],
                url=r["url"],
                snippet=r.get("snippet", ""),
            )
            self._next_id += 1
            self.candidates.append(c)
            added.append(c)
        return added

    def snapshot(self, max_unread: int = 20) -> dict[str, Any]:
        """Structured view of the state, shared by every controller."""
        return {
            "question": self.question,
            "budget": {"steps_used": self.steps_used, "steps_remaining": self.steps_remaining},
            "searches": [
                {"engine": s.engine.value, "query": s.query, "n_results": s.n_results}
                for s in self.searches
            ],
            "notes": [{"source": n.title, "facts": n.facts} for n in self.notes],
            "sources_read": [c.title for c in self.candidates if c.read],
            "unread_sources": [
                {"id": c.id, "origin": c.origin.value, "title": c.title, "snippet": c.snippet}
                for c in self.unread(max_unread)
            ],
            "history": [
                {"step": s.index, "action": s.decision.action.value, "detail": s.detail,
                 "outcome": s.outcome}
                for s in self.steps
            ],
        }

    def available_actions(self) -> list[Action]:
        actions = [Action.SEARCH_WIKIPEDIA, Action.SEARCH_WEB]
        if self.unread():
            actions.append(Action.READ_SOURCE)
        actions.append(Action.ANSWER)
        return actions
