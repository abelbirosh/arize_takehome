"""Runtime settings, read from the environment (and `.env`)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or default


@dataclass(frozen=True)
class Settings:
    # LLM (any OpenAI-compatible endpoint; OpenRouter by default).
    llm_base_url: str = field(default_factory=lambda: _env("LLM_BASE_URL", OPENROUTER_BASE_URL))
    llm_api_key: str | None = field(
        default_factory=lambda: _env("LLM_API_KEY") or _env("OPENROUTER_API_KEY")
    )
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "anthropic/claude-haiku-5.5"))
    # OpenRouter reasoning: "off" or an effort level (minimal/low/medium/high).
    llm_reasoning: str = field(default_factory=lambda: _env("LLM_REASONING", "low"))

    # Jev. TYPESAFE_BASE_URL=https://openrouter.ai/api routes through OpenRouter.
    jev_base_url: str | None = field(default_factory=lambda: _env("TYPESAFE_BASE_URL"))
    jev_api_key: str | None = field(
        default_factory=lambda: _env("TYPESAFE_API_KEY") or _env("OPENROUTER_API_KEY")
    )
    jev_model: str = field(default_factory=lambda: _env("JEV_MODEL", "jev-latest"))
    # USD per million input tokens; output tokens are free.
    jev_price_per_mtok: float = 0.042

    # Agent budget.
    max_steps: int = field(default_factory=lambda: int(_env("MAX_STEPS", "8")))
    max_unread_candidates: int = 20
    max_source_chars: int = 15_000

    # Hybrid controller: below this Jev confidence, the LLM decides instead.
    hybrid_threshold: float = field(
        default_factory=lambda: float(_env("HYBRID_THRESHOLD", "0.5"))
    )

    # Web search backend: "tinyfish" (CLI) is the only one wired up today.
    web_backend: str = field(default_factory=lambda: _env("WEB_BACKEND", "tinyfish"))

    phoenix_project: str = field(
        default_factory=lambda: _env("PHOENIX_PROJECT_NAME", "jev-research-agent")
    )
