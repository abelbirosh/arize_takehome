"""The span tree Phoenix will receive, captured in memory."""

from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from research_agent.agent import ResearchAgent
from research_agent.controllers import SystemOneController

from conftest import FakeJevClient, FakeLLM, FakeTools, scripted

exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace_api.set_tracer_provider(provider)


def test_span_tree(settings):
    exporter.clear()
    jev = FakeJevClient(scripted("search_wikipedia", "read_source"))
    ResearchAgent(SystemOneController(settings, "jev", client=jev), FakeLLM(), FakeTools(), settings).run("Q?")

    spans = {s.name: s for s in exporter.get_finished_spans()}
    kind = lambda n: spans[n].attributes["openinference.span.kind"]
    assert kind("research_agent") == "AGENT"
    assert kind("jev.decide") == "DECISION"
    assert kind("route.jev") == "CHAIN"

    d = spans["jev.decide"].attributes
    assert d["decision.system"] == "typesafe"
    assert d["decision.token_count.input"] == 1000
    assert "decision.probabilities" in d

    agent = spans["research_agent"].attributes
    assert agent["output.value"] == "42"
    assert agent["metadata"]  # controller + model, for filtering in Phoenix
