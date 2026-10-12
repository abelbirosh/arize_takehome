"""Routing controllers: who decides the agent's next action.

Every controller sees the same `AgentState.snapshot()` and returns a `Decision`.
Only the decider changes between them; query writing, note taking and answering
always go to the generator LLM. That isolation is what makes the benchmark comparable.

- SystemOneController  A System One decision model (Jev) answers typed questions
                       (Choice/Noul) with probabilities.
- LLMController        A chat LLM picks the action by emitting JSON (ReAct-style routing).
- HybridController     A decision model decides; below a confidence threshold, an LLM does.
- FixedController      No model: search Wikipedia -> read -> search web -> read -> answer.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Protocol

from openinference.instrumentation import get_decision_attributes
from typesafe_sdk import Choice, Noul, TypeSafeClient

from research_agent.config import Settings
from research_agent.llm import LLM
from research_agent.ratelimit import throttle
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


# -------------------------------------------------------------------- System One


@dataclass(frozen=True)
class DecisionModel:
    model_id: str  # as sent to the System One API (OpenRouter maps bare jev ids)
    price_per_mtok: float  # USD per million input tokens; output is free
    system: str  # OpenInference decision.system


DECISION_MODELS: dict[str, DecisionModel] = {
    "jev": DecisionModel("jev-latest", 0.042, "typesafe"),
}


class SystemOneController:
    """Routes with a decision model through the System One API (OpenRouter or TypeSafe)."""

    def __init__(self, settings: Settings, key: str = "jev",
                 client: TypeSafeClient | None = None):
        self.settings = settings
        self.name = key
        self.spec = DECISION_MODELS[key]
        self.model = settings.jev_model if key == "jev" else self.spec.model_id
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
            f"{self.name}.decide", openinference_span_kind="decision"
        ) as span:
            span.set_input(
                to_json({"state": snapshot, "questions": {
                    k: q.model_dump(exclude_none=True) if hasattr(q, "model_dump") else q
                    for k, q in questions.items()
                }}),
                mime_type="application/json",
            )
            throttle(self.model)
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
            cost = in_tok / 1e6 * self.spec.price_per_mtok

            span.set_attributes(get_decision_attributes(
                provider=self.provider, system=self.spec.system,
                request_model_name=self.model, response_model_name=resp.model,
                token_count={"input": in_tok, "output": out_tok},
            ))
            span.set_attributes({
                "decision.action": action.value,
                "decision.confidence": nxt.confidence,
                "decision.probabilities": to_json(nxt.probabilities),
                "decision.evidence_sufficient": sufficient,
                "decision.latency_ms": latency,
                "decision.cost_usd": cost,
                **({"decision.read_target": target,
                    "decision.read_target_confidence": resp.answers["read_target"].confidence}
                   if target else {}),
            })
            span.set_output(
                to_json({k: a.model_dump() for k, a in resp.answers.items()}),
                mime_type="application/json",
            )
        return Decision(
            action=action, controller=self.name, model=self.model, target_id=target,
            confidence=nxt.confidence, probabilities=dict(nxt.probabilities),
            evidence_sufficient=sufficient, latency_ms=latency, cost_usd=cost,
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
    """A chat LLM as the decider. Uses its own `LLM` instance so routing cost and
    generation cost are accounted separately, even when it is the same model."""

    def __init__(self, settings: Settings, llm: LLM, name: str = "llm"):
        self.settings = settings
        self.llm = llm
        self.name = name

    def decide(self, state: AgentState) -> Decision:
        snapshot = state.snapshot(self.settings.max_unread_candidates)
        options = {a.value: ACTION_CRITERIA[a] for a in state.available_actions()}
        cost0 = self.llm.usage.cost_usd
        raw = self.llm.decide(snapshot, options)
        latency = self.llm.last_latency_ms  # excludes rate-limit queueing
        cost = self.llm.usage.cost_usd - cost0
        try:
            action, target, reason = parse_llm_decision(raw, state)
            valid = True
        except (ValueError, json.JSONDecodeError) as e:
            action, target = _fallback_action(state)
            reason, valid = f"invalid controller output ({e}); fell back", False
        return Decision(
            action=action, controller=self.name, model=self.llm.model, target_id=target,
            latency_ms=latency, cost_usd=cost, valid=valid, reason=reason,
        )


# ------------------------------------------------------------------------ Hybrid


class HybridController:
    name = "hybrid"

    def __init__(self, s1: SystemOneController, llm: LLMController, threshold: float):
        self.s1, self.llm, self.threshold = s1, llm, threshold
        self.name = f"hybrid-{s1.name}"

    def decide(self, state: AgentState) -> Decision:
        first = self.s1.decide(state)
        if first.confidence is not None and first.confidence >= self.threshold:
            first.controller = self.name
            return first
        second = self.llm.decide(state)
        second.controller = self.name
        second.escalated = True
        second.latency_ms += first.latency_ms
        second.cost_usd += first.cost_usd
        second.evidence_sufficient = first.evidence_sufficient
        second.probabilities = first.probabilities
        second.confidence = first.confidence
        second.reason = (
            f"{self.s1.name} picked {first.action.value} at confidence {first.confidence:.2f} "
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


# Claude models used as deciders (the generator stays fixed).
LLM_DECIDERS: dict[str, str] = {
    "claude-haiku-5.5": "anthropic/claude-haiku-5.5",
    "claude-sonnet-5.5": "anthropic/claude-sonnet-5.5",
    "claude-opus-5.5": "anthropic/claude-opus-5.5",
}

CONTROLLERS = (*DECISION_MODELS, *LLM_DECIDERS, "llm", "hybrid", "fixed")


def build_controller(kind: str, settings: Settings, generator_model: str) -> Controller:
    """`llm` routes with the generator model itself; `hybrid` is Jev + that model."""
    if kind in DECISION_MODELS:
        return SystemOneController(settings, kind)
    if kind in LLM_DECIDERS:
        return LLMController(settings, LLM(settings, model=LLM_DECIDERS[kind]), name=kind)
    if kind == "llm":
        return LLMController(settings, LLM(settings, model=generator_model))
    if kind == "hybrid":
        return HybridController(
            SystemOneController(settings, "jev"),
            LLMController(settings, LLM(settings, model=generator_model)),
            settings.hybrid_threshold,
        )
    if kind == "fixed":
        return FixedController()
    raise ValueError(f"unknown controller {kind!r}; expected one of {', '.join(CONTROLLERS)}")
