"""Answer-correctness judge, shared by dataset screening and Phoenix experiments."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openai import OpenAI

from research_agent.config import Settings
from research_agent.ratelimit import throttle

JUDGE_MODEL = "openai/gpt-6.1-sol"
LABELS = ("correct", "incorrect", "no_answer")

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


@dataclass
class Judgement:
    label: str
    explanation: str
    cost_usd: float = 0.0

    @property
    def score(self) -> float:
        return 1.0 if self.label == "correct" else 0.0


def _cost(resp) -> float:
    cost = (resp.usage.model_extra or {}).get("cost") if resp.usage else None
    return float(cost) if isinstance(cost, (int, float)) else 0.0


class Judge:
    def __init__(self, settings: Settings | None = None, model: str = JUDGE_MODEL):
        settings = settings or Settings()
        self.model = model
        self.client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key,
                             max_retries=6)

    def __call__(self, question: str, gold: str, predicted: str) -> Judgement:
        if not predicted.strip():
            return Judgement("no_answer", "empty prediction")
        throttle(self.model)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": JUDGE_PROMPT.format(
                question=question, gold=gold, predicted=predicted)}],
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
        if label not in LABELS:
            return Judgement("incorrect", f"unparseable judge output: {text[:200]}", cost)
        return Judgement(label, obj.get("explanation", ""), cost)

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
