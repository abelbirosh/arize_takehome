"""LLM judges shared by dataset screening and Phoenix experiments.

- `Judge.__call__` / `batch`: v1 correctness (correct / incorrect / no_answer).
- `Judge.correctness`: v2 correctness with accepted variants, a `hedged` label, and
  premise-checking for unanswerable questions.
- `Judge.grounded`: is the answer supported by the agent's own research notes?
- `DecisionJudge`: the same two checks asked of a decision model, as one Choice over
  the same labels and definitions.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass

from openai import OpenAI
from typesafe_sdk import Choice, TypeSafeClient

from research_agent.config import Settings
from research_agent.controllers import DECISION_MODELS
from research_agent.ratelimit import throttle

JUDGE_MODEL = "openai/gpt-6.1-sol"
LABELS = ("correct", "incorrect", "no_answer")
CORRECTNESS_LABELS = ("correct", "hedged", "incorrect", "no_answer")
GROUNDED_LABELS = ("supported", "unsupported", "not_applicable")

JUDGE_PROMPT = """You grade answers to research questions against a gold answer.

Question: {question}
Gold answer: {gold}
Predicted answer: {predicted}

Decide whether the predicted answer is correct:
- "correct": it states the gold answer or an equivalent (same entity, number, or date;
  formatting, extra context, and minor spelling differences are fine).
- "incorrect": it gives a different answer, contradicts the gold answer, or hedges
  between several candidates.
- "no_answer": it declines or says it cannot determine the answer.

Reply with JSON only: {{"label": "correct" | "incorrect" | "no_answer", "explanation": "<one sentence>"}}"""

BATCH_PROMPT = """You grade several predicted answers to one research question against a gold answer.

Question: {question}
Gold answer: {gold}

Predicted answers:
{predictions}

Label each one "correct" (states the gold answer or an equivalent: same entity, number, or
date; formatting, extra context and minor spelling differences are fine), "incorrect"
(different answer, contradicts the gold answer, or hedges between candidates), or
"no_answer" (declines or says it cannot determine the answer).

Reply with JSON only, mapping each key to its label: {{"<key>": "<label>", ...}}"""


CORRECTNESS_PROMPT = """You grade a research agent's final answer against a gold answer.

Question: {question}
Can the question be answered as asked: {answerable}
Gold answer: {gold}
Accepted variants: {accepted}
Predicted answer: {predicted}

Choose one label:
- "correct": the prediction commits to the gold answer or an accepted variant (or a clear
  equivalent: same entity, number or date; extra context and formatting are fine). If the
  question cannot be answered as asked, "correct" means the prediction says so for the
  right reason: it identifies the false premise or that no such thing exists.
- "hedged": the prediction mentions the gold answer but does not commit to it: it offers
  other candidates alongside it, or presents it as a guess or as unverified.
- "incorrect": the prediction commits to a different answer. For a question that cannot
  be answered as asked, inventing an answer is "incorrect".
- "no_answer": the prediction declines, or says it could not determine the answer,
  without identifying a false premise.

Reply with JSON only: {{"label": "<label>", "explanation": "<one sentence>"}}"""

GROUNDED_PROMPT = """You check whether a research agent's final answer is supported by the
notes it collected while researching. You are not judging whether the answer is true.

Question: {question}
Final answer: {predicted}

Research notes:
{notes}

Choose one label:
- "supported": the notes contain the facts the answer's key claim rests on, directly or
  by simple arithmetic or comparison of facts in the notes.
- "unsupported": the key claim is missing from the notes or goes beyond them; the answer
  relies on outside knowledge or a guess.
- "not_applicable": the answer makes no factual claim (it only declines or says it could
  not determine the answer).

Reply with JSON only: {{"label": "<label>", "explanation": "<one sentence>"}}"""


@dataclass
class Judgement:
    label: str
    explanation: str
    cost_usd: float = 0.0
    latency_ms: float = 0.0

    @property
    def score(self) -> float | None:
        if self.label in ("correct", "supported"):
            return 1.0
        if self.label == "not_applicable":
            return None
        return 0.0


def _cost(resp) -> float:
    cost = (resp.usage.model_extra or {}).get("cost") if resp.usage else None
    return float(cost) if isinstance(cost, (int, float)) else 0.0


class Judge:
    def __init__(self, settings: Settings | None = None, model: str = JUDGE_MODEL,
                 effort: str = "low"):
        settings = settings or Settings()
        self.model = model
        self.effort = effort
        self.client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key,
                             max_retries=6)

    def _ask(self, prompt: str, labels: tuple[str, ...], fallback: str) -> Judgement:
        throttle(self.model)
        t0 = time.perf_counter()
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2048 if self.effort == "low" else 16384,  # room for longer reasoning
            extra_body={"reasoning": {"effort": self.effort}, "usage": {"include": True}},
        )
        latency = (time.perf_counter() - t0) * 1000
        cost = _cost(resp)
        text = resp.choices[0].message.content or ""
        m = re.search(r"\{.*\}", text, re.DOTALL)
        try:
            obj = json.loads(m.group(0)) if m else {}
        except json.JSONDecodeError:
            obj = {}
        label = obj.get("label")
        if label not in labels:
            return Judgement(fallback, f"unparseable judge output: {text[:200]}", cost, latency)
        return Judgement(label, obj.get("explanation", ""), cost, latency)

    def __call__(self, question: str, gold: str, predicted: str) -> Judgement:
        if not predicted.strip():
            return Judgement("no_answer", "empty prediction")
        return self._ask(JUDGE_PROMPT.format(question=question, gold=gold, predicted=predicted),
                         LABELS, "incorrect")

    def correctness(self, question: str, gold: str, accepted: list[str], answerable: bool,
                    predicted: str) -> Judgement:
        if not predicted.strip():
            return Judgement("no_answer", "empty prediction")
        return self._ask(CORRECTNESS_PROMPT.format(
            question=question, gold=gold, accepted="; ".join(accepted) or "(none)",
            answerable="yes" if answerable else "no (false premise or no such thing)",
            predicted=predicted,
        ), CORRECTNESS_LABELS, "incorrect")

    def grounded(self, question: str, predicted: str, notes: list[dict]) -> Judgement:
        if not predicted.strip():
            return Judgement("not_applicable", "empty prediction")
        listing = "\n\n".join(f"[{n['title']}]\n{n['facts']}" for n in notes) or "(no notes)"
        return self._ask(GROUNDED_PROMPT.format(question=question, predicted=predicted,
                                                notes=listing),
                         GROUNDED_LABELS, "unsupported")

    def batch(self, question: str, gold: str, predictions: dict[str, str]) -> dict[str, str]:
        """Grade several predictions in one call (one rate-limit slot instead of N)."""
        listing = "\n".join(f"[{k}] {v or '(empty)'}" for k, v in predictions.items())
        throttle(self.model)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": BATCH_PROMPT.format(
                question=question, gold=gold, predictions=listing)}],
            temperature=0,
            max_tokens=2048,
            extra_body={"reasoning": {"effort": "low"}, "usage": {"include": True}},
        )
        text = resp.choices[0].message.content or ""
        m = re.search(r"\{.*\}", text, re.DOTALL)
        obj = json.loads(m.group(0)) if m else {}
        return {k: (obj.get(k) if obj.get(k) in LABELS else "judge_error") for k in predictions}


def _label_definitions(prompt: str) -> dict[str, str]:
    """The `- "label": definition` items of a judge prompt, in order."""
    body = prompt.split("Choose one label:")[1].split("Reply with JSON")[0]
    items = re.findall(r'^- "([a-z_]+)": (.+?)(?=^- "|\Z)', body, re.MULTILINE | re.DOTALL)
    return {label: " ".join(text.split()) for label, text in items}


class DecisionJudge:
    """Correctness and grounding asked of a decision model (Jev, Microsoft-Decision-1,
    GPT-6 Luna Decisions): one Choice whose options are the LLM judge's labels, with the
    same definitions. A decision model returns a label and probabilities, no explanation."""

    def __init__(self, settings: Settings | None = None, key: str = "jev",
                 client: TypeSafeClient | None = None):
        settings = settings or Settings()
        self.spec = DECISION_MODELS[key]
        self.model = settings.jev_model if key == "jev" else self.spec.model_id
        self.client = client or TypeSafeClient(
            api_key=settings.jev_api_key, base_url=settings.jev_base_url, model=self.model)

    def _ask(self, state: dict, name: str, instructions: str,
             criteria: dict[str, str]) -> Judgement:
        throttle(self.model)
        t0 = time.perf_counter()
        resp = self.client.system_one(
            state=state, questions={name: Choice(instructions=instructions, criteria=criteria)},
            model=self.model)
        latency = (time.perf_counter() - t0) * 1000
        answer = resp.answers[name]
        cost = (resp.usage.input_tokens or 0) / 1e6 * self.spec.price_per_mtok
        return Judgement(answer.choice, f"confidence {answer.confidence:.2f}", cost, latency)

    def correctness(self, question: str, gold: str, accepted: list[str], answerable: bool,
                    predicted: str) -> Judgement:
        if not predicted.strip():
            return Judgement("no_answer", "empty prediction")
        state = {"question": question, "gold_answer": gold, "accepted_answers": accepted,
                 "answerable_as_asked": answerable, "predicted_answer": predicted}
        return self._ask(state, "correctness", (
            "Grade `predicted_answer` to `question` against `gold_answer` and "
            "`accepted_answers`. `answerable_as_asked` is false when the question has a "
            "false premise or asks about something that does not exist."),
            _label_definitions(CORRECTNESS_PROMPT))

    def grounded(self, question: str, predicted: str, notes: list[dict]) -> Judgement:
        if not predicted.strip():
            return Judgement("not_applicable", "empty prediction")
        state = {"question": question, "final_answer": predicted,
                 "research_notes": [{"title": n["title"], "facts": n["facts"]} for n in notes]}
        return self._ask(state, "grounded", (
            "Is `final_answer` supported by the facts in `research_notes`, the notes a "
            "research agent collected? Do not judge whether the answer is true."),
            _label_definitions(GROUNDED_PROMPT))
