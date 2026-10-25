"""Judges and code evaluators, with a fake OpenAI client (no API calls)."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from research_agent.evals import Judge

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from run_experiments import normalize, routing_fit  # noqa: E402


class FakeCompletions:
    def __init__(self, reply: str):
        self.reply = reply
        self.prompts: list[str] = []

    def create(self, **kw):
        self.prompts.append(kw["messages"][0]["content"])
        usage = SimpleNamespace(model_extra={"cost": 0.001})
        return SimpleNamespace(usage=usage,
                               choices=[SimpleNamespace(message=SimpleNamespace(content=self.reply))])


def judge_replying(reply: dict | str, settings) -> tuple[Judge, FakeCompletions]:
    j = Judge(settings)
    fake = FakeCompletions(reply if isinstance(reply, str) else json.dumps(reply))
    j.client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
    return j, fake


def test_correctness_labels_and_scores(settings):
    for label, score in [("correct", 1.0), ("hedged", 0.0), ("incorrect", 0.0),
                         ("no_answer", 0.0)]:
        j, _ = judge_replying({"label": label, "explanation": "x"}, settings)
        out = j.correctness("Q?", "Minsk", ["Minsk", "Minsk, Belarus"], True, "Minsk")
        assert (out.label, out.score, out.cost_usd) == (label, score, 0.001)


def test_correctness_prompt_carries_variants_and_premise(settings):
    j, fake = judge_replying({"label": "correct"}, settings)
    j.correctness("Who won the 2026 Ryder Cup?", "No 2026 Ryder Cup was held",
                  ["there was no 2026 Ryder Cup"], False, "There was no Ryder Cup in 2026.")
    prompt = fake.prompts[0]
    assert "there was no 2026 Ryder Cup" in prompt
    assert "no (false premise" in prompt


def test_unparseable_and_empty(settings):
    j, _ = judge_replying("sure, looks right to me", settings)
    assert j.correctness("Q?", "A", [], True, "A").label == "incorrect"
    assert j.grounded("Q?", "A", []).label == "unsupported"
    assert j.correctness("Q?", "A", [], True, "  ").label == "no_answer"  # no API call
    assert j.grounded("Q?", "", []).label == "not_applicable"


def test_grounded_scores_and_notes_in_prompt(settings):
    j, fake = judge_replying({"label": "not_applicable"}, settings)
    out = j.grounded("Q?", "I could not determine it.",
                     [{"title": "Aryna Sabalenka", "facts": "- born in Minsk"}])
    assert out.score is None
    assert "born in Minsk" in fake.prompts[0]
    j, _ = judge_replying({"label": "supported"}, settings)
    assert j.grounded("Q?", "Minsk", []).score == 1.0


def steps(*actions):
    return {"steps": [{"action": a} for a in actions]}


def test_routing_fit():
    web, frames = {"needs_web": True}, {"needs_web": False}
    assert routing_fit(steps("search_wikipedia", "search_web", "answer"), web)["score"] == 1.0
    assert routing_fit(steps("search_wikipedia", "answer"), web)["score"] == 0.0
    assert routing_fit(steps("search_wikipedia", "search_web", "answer"), frames)["score"] == 1.0
    assert routing_fit(steps("search_web", "search_wikipedia", "answer"), frames)["score"] == 0.0
    assert routing_fit(steps("answer"), frames)["score"] == 0.0
    assert routing_fit(steps("answer"), {})["label"] == "not_applicable"  # v1 dataset


def test_stringified_dataframe_fields_are_restored():
    meta = {"answerable": "False", "needs_web": "False", "evidence": "['https://x']", "id": "q1"}
    assert normalize(meta) == {"answerable": False, "needs_web": False,
                               "evidence": ["https://x"], "id": "q1"}
    # A stringified "False" must not count as needing the web.
    assert routing_fit(steps("search_wikipedia", "answer"),
                       {"needs_web": "False"})["score"] == 1.0
    assert normalize({"accepted": "['Red Bull–Bora–Hansgrohe', 'Red Bull Bora']"})["accepted"] == [
        "Red Bull–Bora–Hansgrohe", "Red Bull Bora"]


def test_judge_sends_its_reasoning_effort(settings):
    j, fake = judge_replying({"label": "correct", "explanation": "x"}, settings)
    j.effort = "high"
    seen = {}
    create = fake.create
    fake.create = lambda **kw: (seen.update(kw), create(**kw))[1]
    j.correctness("Q?", "Minsk", ["Minsk"], True, "Minsk")
    assert seen["extra_body"]["reasoning"] == {"effort": "high"}


class FakeDecisionClient:
    def __init__(self, choice: str, confidence: float = 0.8):
        self.choice, self.confidence = choice, confidence
        self.calls: list[dict] = []

    def system_one(self, state, questions, model=None):
        self.calls.append({"state": state, "questions": questions, "model": model})
        (name, q), = questions.items()
        probs = {o: (self.confidence if o == self.choice else 0.0) for o in q.criteria}
        answer = SimpleNamespace(type="choice", choice=self.choice,
                                 confidence=self.confidence, probabilities=probs)
        return SimpleNamespace(answers={name: answer}, model=model,
                               usage=SimpleNamespace(input_tokens=2000, output_tokens=0))


def test_decision_judge_grades_correctness_as_one_choice(settings):
    from research_agent.evals import CORRECTNESS_LABELS, DecisionJudge
    fake = FakeDecisionClient("hedged", 0.7)
    j = DecisionJudge(settings, "msft", client=fake)
    out = j.correctness("Q?", "Minsk", ["Minsk", "Minsk, Belarus"], False, "Maybe Minsk")
    call = fake.calls[0]
    (q,) = call["questions"].values()
    assert tuple(q.criteria) == CORRECTNESS_LABELS
    assert all(len(text) > 20 for text in q.criteria.values())
    assert call["state"]["predicted_answer"] == "Maybe Minsk"
    assert call["state"]["accepted_answers"] == ["Minsk", "Minsk, Belarus"]
    assert call["state"]["answerable_as_asked"] is False
    assert out.label == "hedged" and out.score == 0.0
    assert out.cost_usd == pytest.approx(2000 / 1e6 * 0.042)
    assert "0.70" in out.explanation


def test_decision_judge_grades_grounding_without_the_gold_answer(settings):
    from research_agent.evals import GROUNDED_LABELS, DecisionJudge
    fake = FakeDecisionClient("supported")
    j = DecisionJudge(settings, "oai", client=fake)
    out = j.grounded("Q?", "Minsk", [{"title": "T", "url": "u", "facts": "- born in Minsk"}])
    call = fake.calls[0]
    (q,) = call["questions"].values()
    assert tuple(q.criteria) == GROUNDED_LABELS
    assert "gold_answer" not in call["state"]
    assert call["state"]["research_notes"] == [{"title": "T", "facts": "- born in Minsk"}]
    assert call["model"] == "openai/gpt-6-luna-decisions"
    assert out.label == "supported"


def test_decision_judge_skips_empty_predictions(settings):
    from research_agent.evals import DecisionJudge
    fake = FakeDecisionClient("correct")
    j = DecisionJudge(settings, "jev", client=fake)
    assert j.correctness("Q?", "Minsk", [], True, "  ").label == "no_answer"
    assert j.grounded("Q?", "", []).label == "not_applicable"
    assert fake.calls == []
