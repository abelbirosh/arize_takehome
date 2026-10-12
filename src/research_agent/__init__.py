"""A research agent whose next action is chosen by a swappable controller: a decision
model (Jev, Microsoft-Decision-1, GPT-6 Luna Decisions), a Claude LLM, or a fixed pipeline."""

from research_agent.agent import AgentResult, ResearchAgent
from research_agent.config import Settings
from research_agent.controllers import CONTROLLERS, build_controller
from research_agent.llm import LLM
from research_agent.tools import DefaultTools, Tools


def build_agent(
    controller: str = "jev",
    llm_model: str | None = None,
    settings: Settings | None = None,
    tools: Tools | None = None,
) -> ResearchAgent:
    """One agent per run/thread: usage accounting lives on the instance.

    `llm_model` is the generator (queries, notes, answers); the controller decides.
    """
    settings = settings or Settings()
    llm = LLM(settings, model=llm_model)
    return ResearchAgent(
        controller=build_controller(controller, settings, llm.model),
        llm=llm,
        tools=tools or DefaultTools(),
        settings=settings,
    )


__all__ = ["AgentResult", "CONTROLLERS", "ResearchAgent", "Settings", "build_agent"]
