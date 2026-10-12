"""Phoenix / OpenInference tracing.

Span layout for one run:

    research_agent (AGENT)
      step.N <action> (CHAIN)
        route.<controller> (CHAIN)
          jev.decide (DECISION)      <- Jev call, probabilities as attributes
          ChatCompletion (LLM)       <- LLM-as-controller, auto-instrumented
        wikipedia.search / web.search (RETRIEVER)
        read_source (TOOL)
        ChatCompletion (LLM)         <- query writing / note taking / answering

Without `setup_tracing()` every span is a no-op, so the agent runs untraced.
"""

from __future__ import annotations

import json
from typing import Any

from openinference.instrumentation import OITracer, TraceConfig
from opentelemetry import trace as trace_api

tracer = OITracer(trace_api.get_tracer("research_agent"), config=TraceConfig())

_configured = False


def setup_tracing(project_name: str) -> None:
    """Send traces to Phoenix (PHOENIX_COLLECTOR_ENDPOINT, default localhost:6006)."""
    global _configured
    if _configured:
        return
    from phoenix.otel import register

    register(project_name=project_name, auto_instrument=True, batch=True, verbose=False)
    _configured = True


def to_json(value: Any) -> str:
    return json.dumps(value, default=str, ensure_ascii=False)
