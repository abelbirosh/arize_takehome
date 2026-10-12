"""Register OpenRouter model prices in Phoenix so its cost columns are right.

Phoenix prices spans from its own model table (matched on `llm.model_name`),
and that table doesn't know new or OpenRouter-namespaced ids. This pulls live
prices from OpenRouter's public model list and adds any that are missing.

    uv run python scripts/register_pricing.py [model ...]
"""

from __future__ import annotations

import os
import re
import sys

import httpx

from research_agent.config import Settings

BENCHMARK_MODELS = [
    "anthropic/claude-haiku-5.5",
    "openai/gpt-5.6-luna",
    "google/gemini-3.8-flash",
    "deepseek/deepseek-v4.1-flash",
]

PHOENIX = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006").rstrip("/")


def gql(query: str, variables: dict | None = None) -> dict:
    headers = {}
    if key := os.environ.get("PHOENIX_API_KEY"):
        headers["Authorization"] = f"Bearer {key}"
    r = httpx.post(f"{PHOENIX}/graphql", json={"query": query, "variables": variables or {}},
                   headers=headers, timeout=30)
    r.raise_for_status()
    body = r.json()
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def main(models: list[str]) -> None:
    Settings()  # loads .env
    prices = {m["id"]: m["pricing"] for m in
              httpx.get("https://openrouter.ai/api/v1/models", timeout=30).json()["data"]}
    existing = {e["node"]["name"] for e in
                gql("{ generativeModels(first: 1000) { edges { node { name } } } }")
                ["generativeModels"]["edges"]}

    for model in models:
        if model in existing:
            print(f"= {model} (already registered)")
            continue
        if model not in prices:
            print(f"! {model}: not on OpenRouter, skipped")
            continue
        p = prices[model]
        per_m = lambda usd_per_token: float(usd_per_token) * 1e6  # noqa: E731
        costs = [
            {"tokenType": "input", "kind": "PROMPT", "costPerMillionTokens": per_m(p["prompt"])},
            {"tokenType": "output", "kind": "COMPLETION",
             "costPerMillionTokens": per_m(p["completion"])},
        ]
        if float(p.get("input_cache_read") or 0):
            costs.append({"tokenType": "cache_read", "kind": "PROMPT",
                          "costPerMillionTokens": per_m(p["input_cache_read"])})
        gql(
            """mutation($input: CreateModelMutationInput!) {
                 createModel(input: $input) { model { name } } }""",
            {"input": {
                "name": model,
                "provider": model.split("/")[0],
                # Also match dated snapshots such as anthropic/claude-haiku-5.5-20260901.
                "namePattern": f"^{re.escape(model)}(-\\d+)?$",
                "costs": costs,
            }},
        )
        print(f"+ {model}: ${per_m(p['prompt']):.3f} in / ${per_m(p['completion']):.3f} out per M")


if __name__ == "__main__":
    main(sys.argv[1:] or BENCHMARK_MODELS)
