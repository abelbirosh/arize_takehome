"""The research loop: decide -> act -> observe, until the controller says answer."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

from openinference.instrumentation import using_metadata

from research_agent.config import Settings
from research_agent.controllers import Controller
from research_agent.llm import LLM, Usage
from research_agent.state import Action, AgentState, Decision, Note, Origin, Search, StepRecord
from research_agent.tools import Tools
from research_agent.tracing import to_json, tracer


@dataclass
class AgentResult:
    question: str
    answer: str  # short final answer
    full_answer: str
    controller: str
    llm_model: str
    steps: list[StepRecord]
    notes: list[Note]
    wall_ms: float
    stats: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ResearchAgent:
    def __init__(self, controller: Controller, llm: LLM, tools: Tools, settings: Settings):
        self.controller = controller
        self.llm = llm
        self.tools = tools
        self.settings = settings

    def run(self, question: str) -> AgentResult:
        state = AgentState(question=question, max_steps=self.settings.max_steps)
        self.llm.usage = Usage()  # per-run accounting; one agent per thread
        metadata = {"controller": self.controller.name, "llm_model": self.llm.model,
                    "max_steps": self.settings.max_steps}
        t0 = time.perf_counter()
        full_answer, answer = "", ""
        with using_metadata(metadata), tracer.start_as_current_span(
            "research_agent", openinference_span_kind="agent"
        ) as span:
            span.set_input(question)
            while True:
                decision = self._route(state)
                with tracer.start_as_current_span(
                    f"step.{state.steps_used} {decision.action.value}",
                    openinference_span_kind="chain",
                ) as step_span:
                    step_span.set_input(to_json({"decision": asdict(decision)}),
                                        mime_type="application/json")
                    detail, outcome = self._act(state, decision)
                    step_span.set_output(outcome)
                state.steps.append(StepRecord(state.steps_used, decision, detail, outcome))
                if decision.action is Action.ANSWER:
                    full_answer, answer = detail, outcome
                    break
            wall_ms = (time.perf_counter() - t0) * 1000
            stats = self._stats(state, wall_ms)
            span.set_output(answer)
            span.set_attributes({f"agent.{k}": v for k, v in stats.items()
                                 if isinstance(v, (int, float, str, bool))})
        return AgentResult(
            question=question, answer=answer, full_answer=full_answer,
            controller=self.controller.name, llm_model=self.llm.model,
            steps=state.steps, notes=state.notes, wall_ms=wall_ms, stats=stats,
        )

    # ------------------------------------------------------------------ routing

    def _route(self, state: AgentState) -> Decision:
        # The last step is always the answer, whatever the controller wants.
        if state.steps_remaining <= 1:
            return Decision(action=Action.ANSWER, controller=self.controller.name,
                            forced=True, reason="step budget exhausted")
        with tracer.start_as_current_span(
            f"route.{self.controller.name}", openinference_span_kind="chain"
        ) as span:
            span.set_input(to_json(state.snapshot(self.settings.max_unread_candidates)),
                           mime_type="application/json")
            decision = self.controller.decide(state)
            # Harness-level guards: every controller gets the same safety net.
            if decision.action is Action.READ_SOURCE:
                cand = state.candidate(decision.target_id or "")
                if cand is None or cand.read:
                    unread = state.unread()
                    decision.target_id = unread[0].id if unread else None
                    if decision.target_id is None:
                        decision.action, decision.valid = Action.ANSWER, False
            span.set_attributes({
                "route.controller": decision.controller,
                "route.action": decision.action.value,
                "route.valid": decision.valid,
                "route.escalated": decision.escalated,
                "route.latency_ms": decision.latency_ms,
                **({"route.confidence": decision.confidence}
                   if decision.confidence is not None else {}),
            })
            span.set_output(to_json(asdict(decision)), mime_type="application/json")
            return decision

    # ------------------------------------------------------------------- acting

    def _act(self, state: AgentState, d: Decision) -> tuple[str, str]:
        """Execute a decision. Returns (detail, outcome) for the step record."""
        if d.action in (Action.SEARCH_WIKIPEDIA, Action.SEARCH_WEB):
            engine = Origin.WIKIPEDIA if d.action is Action.SEARCH_WIKIPEDIA else Origin.WEB
            query = self.llm.write_query(state, engine)
            try:
                results = self.tools.search(engine, query)
            except Exception as e:  # tool failures are observations, not crashes
                state.searches.append(Search(engine, query, 0))
                return query, f"search failed: {e}"
            added = state.add_candidates(engine, results)
            state.searches.append(Search(engine, query, len(results)))
            return query, f"{len(results)} results, {len(added)} new: " + "; ".join(
                f"{c.id} {c.title}" for c in added)

        if d.action is Action.READ_SOURCE:
            cand = state.candidate(d.target_id or "")
            assert cand is not None  # guaranteed by _route
            cand.read = True
            try:
                focus = " ".join([state.question, *(n.facts for n in state.notes),
                                  *(q.query for q in state.searches)])
                text = self.tools.read(cand, self.settings.max_source_chars, focus)
            except Exception as e:
                return cand.title, f"read failed: {e}"
            facts = self.llm.extract_notes(state, cand, text)
            if not facts:
                return cand.title, "nothing relevant"
            state.notes.append(Note(cand.id, cand.title, cand.url, facts))
            return cand.title, facts

        full, short = self.llm.write_answer(state)
        return full, short

    # -------------------------------------------------------------------- stats

    def _stats(self, state: AgentState, wall_ms: float) -> dict[str, Any]:
        decisions = [s.decision for s in state.steps]
        routed = [d for d in decisions if not d.forced]
        actions = [d.action.value for d in decisions]
        jev_cost = sum(d.jev_cost_usd for d in routed)
        return {
            "steps": len(state.steps),
            "searches": len(state.searches),
            "reads": sum(1 for c in state.candidates if c.read),
            "notes": len(state.notes),
            "forced_answer": any(d.forced for d in decisions),
            "invalid_decisions": sum(1 for d in routed if not d.valid),
            "escalations": sum(1 for d in routed if d.escalated),
            "decision_latency_ms": sum(d.latency_ms for d in routed),
            "decision_cost_usd": sum(d.cost_usd for d in routed),
            "jev_calls": sum(1 for d in routed if d.evidence_sufficient is not None),
            "jev_cost_usd": jev_cost,
            "llm_calls": self.llm.usage.calls,
            "llm_empty_replies": self.llm.usage.empty_replies,
            "llm_cost_usd": self.llm.usage.cost_usd,
            "total_cost_usd": self.llm.usage.cost_usd + jev_cost,
            "llm_input_tokens": self.llm.usage.input_tokens,
            "llm_output_tokens": self.llm.usage.output_tokens,
            "wall_ms": wall_ms,
            "action_trace": " > ".join(actions),
        }
