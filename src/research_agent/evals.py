"""LLM judges shared by dataset screening and Phoenix experiments.

- `Judge.__call__` / `batch`: v1 correctness (correct / incorrect / no_answer).
- `Judge.correctness`: v2 correctness with accepted variants, a `hedged` label, and
  premise-checking for unanswerable questions.
- `Judge.grounded`: is the answer supported by the agent's own research notes?
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openai import OpenAI

from research_agent.config import Settings
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
    def __init__(self, settings: Settings | None = None, model: str = JUDGE_MODEL):
        settings = settings or Settings()
        self.model = model
        self.client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key,
                             max_retries=6)

    def _ask(self, prompt: str, labels: tuple[str, ...], fallback: str) -> Judgement:
        throttle(self.model)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2048,
            extra_body={"reasoning": {"effort": "low"}, "usage": {"include": True}},
        )
        cost = _cost(resp)
        text = resp.choices[0].message.content or ""
        m = re.search(r"\{.*\}", text, re.DOTALL)
        try:
            obj = json.loads(m.group(0)) if m else {}
        except json.JSONDecodeError:
            obj = {}
        label = obj.get("label")
        if label not in labels:
            return Judgement(fallback, f"unparseable judge output: {text[:200]}", cost)
        return Judgement(label, obj.get("explanation", ""), cost)

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
