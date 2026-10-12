"""Run the agent on one question: `uv run research-agent "..." --controller jev`."""

from __future__ import annotations

import argparse
import json
import sys

from research_agent import CONTROLLERS, Settings, build_agent
from research_agent.tracing import setup_tracing


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("question")
    p.add_argument("--controller", choices=CONTROLLERS, default="jev")
    p.add_argument("--model", help="generator LLM id (default: LLM_MODEL env)")
    p.add_argument("--trace", action="store_true", help="send traces to Phoenix")
    p.add_argument("--json", action="store_true", help="print the full result as JSON")
    args = p.parse_args(argv)

    settings = Settings()
    if args.trace:
        setup_tracing(settings.phoenix_project)
    agent = build_agent(args.controller, args.model, settings)
    result = agent.run(args.question)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
        return 0

    for s in result.steps:
        d = s.decision
        conf = f" conf={d.confidence:.2f}" if d.confidence is not None else ""
        flags = "".join(f" [{f}]" for f in ("forced", "escalated") if getattr(d, f))
        flags += "" if d.valid else " [INVALID]"
        target = f" -> {d.target_id}" if d.target_id else ""
        print(f"{s.index}. {d.action.value}{target}{conf} ({d.latency_ms:.0f}ms){flags}")
        detail = s.detail if d.action.value != "answer" else ""
        if detail:
            print(f"     {detail[:160]}")
        print(f"     => {s.outcome[:240].replace(chr(10), ' ')}")
    st = result.stats
    print(f"\nANSWER: {result.answer}")
    print(f"\n{st['steps']} steps | {result.wall_ms / 1000:.1f}s wall | "
          f"routing {st['routing_latency_ms']:.0f}ms | ${st['total_cost_usd']:.4f} "
          f"(generator ${st['generator_cost_usd']:.4f}, routing ${st['routing_cost_usd']:.6f}) | "
          f"invalid={st['invalid_decisions']} escalations={st['escalations']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
