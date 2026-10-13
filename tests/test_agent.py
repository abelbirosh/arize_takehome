from research_agent.agent import ResearchAgent
from research_agent.controllers import (
    FixedController,
    HybridController,
    SystemOneController,
    LLMController,
)
from research_agent.state import Action

from conftest import FakeJevClient, FakeLLM, FakeTools, llm_json, scripted


def make(controller, llm, settings, tools=None):
    return ResearchAgent(controller, llm, tools or FakeTools(), settings)


def test_jev_loop_search_read_answer(settings):
    jev = FakeJevClient(scripted("search_wikipedia", "read_source", "answer"))
    tools = FakeTools()
    result = make(SystemOneController(settings, "jev", client=jev), FakeLLM(), settings, tools).run("Q?")

    assert [s.decision.action for s in result.steps] == [
        Action.SEARCH_WIKIPEDIA, Action.READ_SOURCE, Action.ANSWER]
    assert result.answer == "42"
    assert tools.reads == ["s1"]  # read_target picked the first candidate
    assert len(result.notes) == 1
    assert result.stats["decision_calls"] == 3
    assert result.stats["routing_cost_usd"] > 0
    assert result.stats["final_evidence_sufficient"] == 0.9
    assert result.stats["invalid_decisions"] == 0


def test_jev_only_offered_available_actions(settings):
    jev = FakeJevClient(scripted("search_web", "answer"))
    make(SystemOneController(settings, "jev", client=jev), FakeLLM(), settings).run("Q?")

    first, second = jev.calls
    assert "read_source" not in first["questions"]["next_action"].criteria
    assert "read_target" not in first["questions"]
    assert "read_source" in second["questions"]["next_action"].criteria
    assert set(second["questions"]["read_target"].criteria) == {"s1", "s2"}


def test_single_unread_result_needs_no_read_target(settings):
    # Microsoft/OpenAI reject 1-option Choice questions: with one unread result,
    # don't ask, just read it.
    class OneResultTools(FakeTools):
        def search(self, engine, query, k=5):
            return super().search(engine, query, k)[:1]

    jev = FakeJevClient(scripted("search_web", "read_source", "answer"))
    tools = OneResultTools()
    make(SystemOneController(settings, "jev", client=jev), FakeLLM(), settings, tools).run("Q?")
    assert "read_target" not in jev.calls[1]["questions"]
    assert tools.reads == ["s1"]


def test_budget_forces_answer(settings):
    jev = FakeJevClient(lambda q, s: ("search_web", 0.9))  # never wants to stop
    result = make(SystemOneController(settings, "jev", client=jev), FakeLLM(), settings).run("Q?")

    assert result.stats["steps"] == settings.max_steps
    assert result.steps[-1].decision.action is Action.ANSWER
    assert result.steps[-1].decision.forced
    assert result.stats["forced_answer"]


def test_hybrid_escalates_only_when_unsure(settings):
    # Confident on step 0, unsure afterwards.
    jev = FakeJevClient(lambda q, s: ("search_wikipedia", 0.95 if not s["history"] else 0.2))
    llm = FakeLLM(decide_reply=llm_json("answer"))
    ctrl = HybridController(SystemOneController(settings, "jev", client=jev),
                            LLMController(settings, llm), threshold=0.5)
    result = make(ctrl, FakeLLM(), settings).run("Q?")

    d0, d1 = result.steps[0].decision, result.steps[1].decision
    assert d0.action is Action.SEARCH_WIKIPEDIA and not d0.escalated
    assert d1.action is Action.ANSWER and d1.escalated
    assert d1.confidence == 0.2  # Jev's confidence is kept for calibration analysis
    assert llm.decide_calls == 1
    assert result.stats["escalations"] == 1


def test_llm_controller_invalid_output_falls_back(settings):
    replies = iter(["sure! I think we should search", llm_json("browse_internet"),
                    llm_json("answer")])
    decider = FakeLLM(decide_reply=lambda snap: next(replies))
    result = make(LLMController(settings, decider), FakeLLM(), settings).run("Q?")

    assert result.stats["invalid_decisions"] == 2
    # fallback: no notes/candidates -> search; then candidates exist -> read
    assert [s.decision.action for s in result.steps] == [
        Action.SEARCH_WIKIPEDIA, Action.READ_SOURCE, Action.ANSWER]


def test_llm_controller_rejects_hallucinated_target(settings):
    replies = iter([llm_json("search_web"), llm_json("read_source", "s99"), llm_json("answer")])
    decider = FakeLLM(decide_reply=lambda snap: next(replies))
    result = make(LLMController(settings, decider), FakeLLM(), settings).run("Q?")

    step = result.steps[1].decision
    assert step.action is Action.READ_SOURCE and not step.valid
    assert step.target_id == "s1"


def test_fixed_pipeline(settings):
    s = settings.__class__(llm_api_key="x", jev_api_key="x", max_steps=10)
    result = make(FixedController(), FakeLLM(), s).run("Q?")
    assert result.stats["action_trace"] == (
        "search_wikipedia > read_source > read_source > search_web > read_source > "
        "read_source > answer")
