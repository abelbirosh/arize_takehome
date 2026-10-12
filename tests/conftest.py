"""Fakes for the three external dependencies: tools, LLM, and the Jev client."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Callable

import pytest

from research_agent.config import Settings
from research_agent.llm import Usage
from research_agent.state import Candidate, Origin


class FakeTools:
    def __init__(self):
        self.searches: list[tuple[Origin, str]] = []
        self.reads: list[str] = []

    def search(self, engine: Origin, query: str, k: int = 5):
        self.searches.append((engine, query))
        n = len(self.searches)
        return [
            {"title": f"{engine.value} page {n}.{i}", "url": f"https://{engine.value}/{n}/{i}",
             "snippet": f"snippet {n}.{i}"}
            for i in range(2)
        ]

    def read(self, candidate: Candidate, max_chars: int, focus: str = "") -> str:
        self.reads.append(candidate.id)
        return f"full text of {candidate.title}"


class FakeLLM:
    def __init__(self, decide_reply: str | Callable[[dict], str] = ""):
        self.model = "fake/llm"
        self.usage = Usage()
        self.decide_reply = decide_reply
        self.decide_calls = 0
        self.last_latency_ms = 5.0

    def write_query(self, state, engine):
        self.usage.calls += 1
        return f"query {len(state.searches) + 1}"

    def extract_notes(self, state, candidate, text):
        self.usage.calls += 1
        return f"fact from {candidate.title}"

    def write_answer(self, state):
        self.usage.calls += 1
        return "reasoning...\nFINAL ANSWER: 42", "42"

    def decide(self, snapshot, action_help):
        self.usage.calls += 1
        self.decide_calls += 1
        r = self.decide_reply
        return r(snapshot) if callable(r) else r


def _answer(kind: str, **fields):
    ns = SimpleNamespace(type=kind, **fields)
    ns.model_dump = lambda: {"type": kind, **fields}
    return ns


class FakeJevClient:
    """`script(questions, state) -> (action, confidence)`; read_target picks the first id."""

    def __init__(self, script: Callable[[dict, dict], tuple[str, float]]):
        self.script = script
        self.calls: list[dict] = []

    def system_one(self, state, questions, model=None):
        self.calls.append({"state": state, "questions": questions})
        action, conf = self.script(questions, state)
        options = list(questions["next_action"].criteria)
        assert action in options, f"script chose unavailable action {action}"
        rest = (1 - conf) / max(len(options) - 1, 1)
        probs = {o: (conf if o == action else rest) for o in options}
        answers = {
            "next_action": _answer("choice", choice=action, confidence=conf, probabilities=probs),
            "evidence_sufficient": _answer("noul", noul=0.9 if state["notes"] else 0.1),
        }
        if "read_target" in questions:
            first = next(iter(questions["read_target"].criteria))
            answers["read_target"] = _answer("choice", choice=first, confidence=0.8,
                                             probabilities={first: 0.8})
        return SimpleNamespace(answers=answers, model="jev-test",
                               usage=SimpleNamespace(input_tokens=1000, output_tokens=0))


@pytest.fixture
def settings():
    return Settings(llm_api_key="x", jev_api_key="x", max_steps=6)


def scripted(*plan: str, conf: float = 0.9):
    """Jev script that walks through `plan`, then answers."""
    def script(questions, state):
        i = len(state["history"])
        return (plan[i] if i < len(plan) else "answer"), conf
    return script


def llm_json(action: str, target: str | None = None) -> str:
    return json.dumps({"action": action, "target": target, "reason": "test"})
