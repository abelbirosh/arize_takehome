from research_agent.controllers import (
    CONTROLLERS,
    FixedController,
    HybridController,
    LLMController,
    SystemOneController,
    build_controller,
)

GENERATOR = "anthropic/claude-haiku-5.5"


def test_every_controller_builds(settings):
    for kind in CONTROLLERS:
        ctrl = build_controller(kind, settings, GENERATOR)
        assert ctrl.name.endswith(kind) or kind == "hybrid"


def test_jev_model_and_price(settings):
    jev = build_controller("jev", settings, GENERATOR)
    assert isinstance(jev, SystemOneController)
    assert jev.model == "jev-latest" and jev.spec.price_per_mtok == 0.042


def test_claude_deciders_are_separate_from_generator(settings):
    for name in ("claude-haiku-5.5", "claude-sonnet-5.5", "claude-opus-5.5"):
        ctrl = build_controller(name, settings, GENERATOR)
        assert isinstance(ctrl, LLMController)
        assert ctrl.llm.model == f"anthropic/{name}"
    # Even `llm` (generator routes itself) gets its own instance, so routing cost
    # never lands in the generator's usage.
    llm = build_controller("llm", settings, GENERATOR)
    assert llm.llm.model == GENERATOR
    assert isinstance(build_controller("hybrid", settings, GENERATOR), HybridController)
    assert isinstance(build_controller("fixed", settings, GENERATOR), FixedController)
