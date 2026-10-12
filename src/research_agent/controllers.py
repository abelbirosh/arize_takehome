"""Routing controllers: who decides the agent's next action.

Every controller sees the same `AgentState.snapshot()` and returns a `Decision`.
Only the decider changes between them; query writing, note taking and answering
always go to the LLM. That isolation is what makes the benchmark comparable.

- JevController     Jev answers typed questions (Choice/Noul) with probabilities.
- LLMController     The LLM picks the action by emitting JSON (classic ReAct-style routing).
- HybridController  Jev decides; if its confidence is below a threshold, the LLM decides.
- FixedController   No model: search Wikipedia -> read -> search web -> read -> answer.
"""

from __future__ import annotations

import json
import re
import time
from typing import Protocol

from openinference.instrumentation import get_decision_attributes
from typesafe_sdk import Choice, Noul, TypeSafeClient

from research_agent.config import Settings
from research_agent.llm import LLM
from research_agent.state import Action, AgentState, Decision, Origin
from research_agent.tracing import to_json, tracer

# What each action means. Shared by Jev (as Choice criteria) and the LLM
# controller (as its option list), so both controllers get the same definitions.
ACTION_CRITERIA: dict[Action, str] = {
    Action.SEARCH_WIKIPEDIA: (
        "Run a new Wikipedia search. Right when an encyclopedic fact (a person, place, "
        "organization, creative work, historical event, date or definition) is still "
        "missing and no unread result looks likely to contain it."
    ),
    Action.SEARCH_WEB: (
        "Run a new general web search. Right when the missing information is recent "
        "(news, releases, results or events from the last two years), niche, commercial "
        "or otherwise unlikely to be on Wikipedia, or when Wikipedia searches have not "
        "turned it up."
    ),
    Action.READ_SOURCE: (
        "Read one of the unread search results in `unread_sources`. Right when at least "
        "one unread result's title or snippet suggests it contains information that is "
        "still missing from `notes`."
    ),
    Action.ANSWER: (
        "Stop researching and write the final answer. Right when `notes` already contain "
        "the facts needed for every part of `question`, or when `budget.steps_remaining` "
        "is too small for more research to help."
    ),
}


class Controller(Protocol):
    name: str

    def decide(self, state: AgentState) -> Decision: ...


def _fallback_action(state: AgentState) -> tuple[Action, str | None]:
    """Sensible default when a controller's output is unusable."""
    unread = state.unread()
    if unread:
        return Action.READ_SOURCE, unread[0].id
    return (Action.ANSWER, None) if state.notes else (Action.SEARCH_WIKIPEDIA, None)


# --------------------------------------------------------------------------- Jev


class JevController:
    name = "jev"

    def __init__(self, settings: Settings, client: TypeSafeClient | None = None):
        self.settings = settings
        self.model = settings.jev_model
        self.client = client or TypeSafeClient(
            api_key=settings.jev_api_key, base_url=settings.jev_base_url, model=self.model
        )
        self.provider = (
            "openrouter" if settings.jev_base_url and "openrouter" in settings.jev_base_url
            else "typesafe"
        )

    def questions(self, state: AgentState) -> dict:
        actions = state.available_actions()
        qs: dict = {
            "next_action": Choice(
                instructions=(
                    "A research agent is answering `question`. Given the facts it has "
                    "gathered in `notes`, the searches it has already run in `searches`, "
                    "the results it has not read yet in `unread_sources`, and its "
                    "remaining step budget in `budget`, which action should it take next?"
                ),
                criteria={a.value: ACTION_CRITERIA[a] for a in actions},
            ),
            "evidence_sufficient": Noul(
                instructions=(
                    "Do the facts in `notes` already contain everything needed to answer "
                    "every part of `question` correctly?"
                ),
            ),
        }
        unread = state.unread(self.settings.max_unread_candidates)
        if unread:
            # Speculative: only consumed if next_action is read_source. Asking now
            # saves a second round trip (questions run in parallel).
            qs["read_target"] = Choice(
                instructions=(
                    "If the agent reads exactly one more source from `unread_sources`, "
                    "which one is most likely to contain the information still missing "
                    "from `notes` for answering `question`?"
                ),
                criteria={c.id: c.brief()[:300] for c in unread},
            )
        return qs

    def decide(self, state: AgentState) -> Decision:
        snapshot = state.snapshot(self.settings.max_unread_candidates)
        questions = self.questions(state)
        with tracer.start_as_current_span(
            "jev.decide", openinference_span_kind="decision"
        ) as span:
            span.set_input(
                to_json({"state": snapshot, "questions": {
                    k: q.model_dump(exclude_none=True) if hasattr(q, "model_dump") else q
                    for k, q in questions.items()
                }}),
                mime_type="application/json",
            )
            t0 = time.perf_counter()
            resp = self.client.system_one(state=snapshot, questions=questions, model=self.model)
            latency = (time.perf_counter() - t0) * 1000

            nxt = resp.answers["next_action"]
            action = Action(nxt.choice)
            target = None
            if action is Action.READ_SOURCE and "read_target" in resp.answers:
                target = resp.answers["read_target"].choice
            sufficient = resp.answers["evidence_sufficient"].noul
            in_tok = resp.usage.input_tokens or 0
            out_tok = resp.usage.output_tokens or 0
            cost = in_tok / 1e6 * self.settings.jev_price_per_mtok

            span.set_attributes(get_decision_attributes(
                provider=self.provider, system="typesafe",
                request_model_name=self.model, response_model_name=resp.model,
                token_count={"input": in_tok, "output": out_tok},
            ))
            span.set_attributes({
                "decision.action": action.value,
                "decision.confidence": nxt.confidence,
                "decision.probabilities": to_json(nxt.probabilities),
                "decision.evidence_sufficient": sufficient,
                "decision.latency_ms": latency,
                **({"decision.read_target": target,
                    "decision.read_target_confidence": resp.answers["read_target"].confidence}
                   if target else {}),
            })
            span.set_output(
                to_json({k: a.model_dump() for k, a in resp.answers.items()}),
                mime_type="application/json",
            )
        return Decision(
            action=action, controller=self.name, target_id=target,
            confidence=nxt.confidence, probabilities=dict(nxt.probabilities),
            evidence_sufficient=sufficient, latency_ms=latency, cost_usd=cost,
            jev_cost_usd=cost,
        )


# --------------------------------------------------------------------------- LLM


_JSON = re.compile(r"\{.*\}", re.DOTALL)


def parse_llm_decision(text: str, state: AgentState) -> tuple[Action, str | None, str | None]:
    """Validate the LLM's JSON. Raises ValueError on anything unusable."""
    m = _JSON.search(text)
    if not m:
        raise ValueError("no JSON object in reply")
    obj = json.loads(m.group(0))
    action = Action(obj.get("action"))  # ValueError on hallucinated action names
    if action not in state.available_actions():
        raise ValueError(f"action {action} not available")
    target = obj.get("target")
    if action is Action.READ_SOURCE:
        cand = state.candidate(str(target)) if target else None
        if cand is None or cand.read:
            raise ValueError(f"invalid read target {target!r}")
    return action, (str(target) if action is Action.READ_SOURCE else None), obj.get("reason")


class LLMController:
    name = "llm"

    def __init__(self, settings: Settings, llm: LLM):
        self.settings = settings
        self.llm = llm

    def decide(self, state: AgentState) -> Decision:
        snapshot = state.snapshot(self.settings.max_unread_candidates)
        options = {a.value: ACTION_CRITERIA[a] for a in state.available_actions()}
        cost0 = self.llm.usage.cost_usd
        t0 = time.perf_counter()
        raw = self.llm.decide(snapshot, options)
        latency = (time.perf_counter() - t0) * 1000
        cost = self.llm.usage.cost_usd - cost0
        try:
            action, target, reason = parse_llm_decision(raw, state)
            valid = True
        except (ValueError, json.JSONDecodeError) as e:
            action, target = _fallback_action(state)
            reason, valid = f"invalid controller output ({e}); fell back", False
        return Decision(
            action=action, controller=self.name, target_id=target, latency_ms=latency,
            cost_usd=cost, valid=valid, reason=reason,
        )


# ------------------------------------------------------------------------ Hybrid


class HybridController:
    name = "hybrid"

    def __init__(self, jev: JevController, llm: LLMController, threshold: float):
        self.jev, self.llm, self.threshold = jev, llm, threshold

    def decide(self, state: AgentState) -> Decision:
        first = self.jev.decide(state)
        if first.confidence is not None and first.confidence >= self.threshold:
            first.controller = self.name
            return first
        second = self.llm.decide(state)
        second.controller = self.name
        second.escalated = True
        second.latency_ms += first.latency_ms
        second.cost_usd += first.cost_usd
        second.jev_cost_usd = first.jev_cost_usd
        second.evidence_sufficient = first.evidence_sufficient
        second.probabilities = first.probabilities
        second.confidence = first.confidence
        second.reason = (
            f"jev picked {first.action.value} at confidence {first.confidence:.2f} "
            f"< {self.threshold}; llm: {second.reason}"
        )
        return second


# ------------------------------------------------------------------------- Fixed


class FixedController:
    """Retrieve-then-read pipeline with no model in the loop."""

    name = "fixed"

    def __init__(self, reads_per_engine: int = 2):
        self.reads_per_engine = reads_per_engine

    def decide(self, state: AgentState) -> Decision:
        for engine, action in ((Origin.WIKIPEDIA, Action.SEARCH_WIKIPEDIA),
                               (Origin.WEB, Action.SEARCH_WEB)):
            if not any(s.engine is engine for s in state.searches):
                return Decision(action=action, controller=self.name)
            reads = sum(1 for c in state.candidates if c.read and c.origin is engine)
            unread = [c for c in state.unread() if c.origin is engine]
            if reads < self.reads_per_engine and unread:
                return Decision(action=Action.READ_SOURCE, controller=self.name,
                                target_id=unread[0].id)
        return Decision(action=Action.ANSWER, controller=self.name)


def build_controller(kind: str, settings: Settings, llm: LLM) -> Controller:
    if kind == "jev":
        return JevController(settings)
    if kind == "llm":
        return LLMController(settings, llm)
    if kind == "hybrid":
        return HybridController(JevController(settings), LLMController(settings, llm),
                                settings.hybrid_threshold)
    if kind == "fixed":
        return FixedController()
    raise ValueError(f"unknown controller {kind!r}; expected jev|llm|hybrid|fixed")
