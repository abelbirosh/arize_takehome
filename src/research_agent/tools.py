"""Retrieval tools: Wikipedia (MediaWiki API) and the web (TinyFish CLI)."""

from __future__ import annotations

import html
import json
import math
import re
import shutil
import subprocess
from collections import Counter
from typing import Protocol
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup
from openinference.semconv.trace import DocumentAttributes, SpanAttributes

from research_agent.state import Candidate, Origin
from research_agent.tracing import to_json, tracer

WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_HTML = "https://en.wikipedia.org/api/rest_v1/page/html/"
USER_AGENT = "jev-research-agent/0.1 (https://github.com/abelbirosh/arize_takehome)"
_TAG = re.compile(r"<[^>]+>")


class Tools(Protocol):
    def search(self, engine: Origin, query: str, k: int = 5) -> list[dict[str, str]]: ...
    def read(self, candidate: Candidate, max_chars: int, focus: str = "") -> str: ...


def _clean(text: str) -> str:
    return html.unescape(_TAG.sub("", text)).strip()


# ----------------------------------------------------------------- page text

_DROP_SECTIONS = {"references", "notes", "external links", "further reading", "see also",
                  "citations", "sources", "bibliography", "footnotes"}
_DROP_SELECTORS = ["style", "script", "sup.reference", ".mw-ref", ".reflist", ".navbox",
                   ".mw-references-wrap", ".metadata", ".ambox", ".hatnote", ".mw-editsection"]
_BLOCKS = ["h2", "h3", "h4", "p", "li", "tr", "dd", "caption"]
_CONTAINERS = {"p", "li", "tr", "dd"}


def html_to_text(page_html: str) -> str:
    """Wikipedia HTML -> text that keeps tables (as `a | b | c` rows) and infoboxes.

    The plain-text extracts API drops tables, which loses exactly the data that
    list pages and infoboxes hold (office holders, dates, results).
    """
    soup = BeautifulSoup(page_html, "html.parser")
    for sel in _DROP_SELECTORS:
        for el in soup.select(sel):
            el.decompose()
    for h2 in soup.find_all("h2"):
        if h2.get_text(strip=True).lower() in _DROP_SECTIONS:
            (h2.find_parent("section") or h2).decompose()
    lines = []
    for el in soup.find_all(_BLOCKS):
        if any(parent.name in _CONTAINERS for parent in el.parents):
            continue  # already emitted as part of its container
        if el.name == "tr":
            cells = [c.get_text(" ", strip=True) for c in el.find_all(["th", "td"])]
            text = " | ".join(c for c in cells if c)
        else:
            text = el.get_text(" ", strip=True)
        if not text:
            continue
        if el.name in ("h2", "h3", "h4"):
            text = f"\n## {text}"
        elif el.name == "li":
            text = f"- {text}"
        lines.append(re.sub(r"\s+", " ", text) if not text.startswith("\n") else text)
    return "\n".join(lines).strip()


_WORD = re.compile(r"[a-z0-9]+")
_STOP = set("the a an and or of to in on at for by with from as is was were be been are who "
            "what when where which how did does do that this it its his her their they".split())


def select_passages(text: str, focus: str, max_chars: int, chunk_chars: int = 1200,
                    lead_chars: int = 2000) -> str:
    """Fit a long page into `max_chars`: keep the lead, then the chunks that share
    the most (IDF-weighted) terms with `focus`, in original order.

    Deliberately model-free so every controller gets identical reads.
    """
    if len(text) <= max_chars:
        return text
    chunks, buf = [], ""
    for line in text.splitlines():
        if buf and len(buf) + len(line) > chunk_chars:
            chunks.append(buf)
            buf = ""
        buf += line + "\n"
    if buf:
        chunks.append(buf)

    terms = {w for w in _WORD.findall(focus.lower()) if w not in _STOP and len(w) > 2}
    chunk_terms = [set(_WORD.findall(c.lower())) for c in chunks]
    df = Counter(t for ts in chunk_terms for t in ts & terms)
    idf = {t: math.log((len(chunks) + 1) / (df[t] + 0.5)) for t in df}
    scores = [sum(idf.get(t, 0.0) for t in ts & terms) for ts in chunk_terms]

    keep, used = set(), 0
    for i, c in enumerate(chunks):  # the lead section, always
        if used + len(c) > lead_chars:
            break
        keep.add(i)
        used += len(c)
    for i in sorted(range(len(chunks)), key=lambda i: -scores[i]):
        if i in keep or scores[i] <= 0:
            continue
        if used + len(chunks[i]) > max_chars:
            continue
        keep.add(i)
        used += len(chunks[i])
    out, prev = [], -1
    for i in sorted(keep):
        if prev >= 0 and i != prev + 1:
            out.append("[...]\n")
        out.append(chunks[i])
        prev = i
    return "".join(out).strip()


class Wikipedia:
    def __init__(self, client: httpx.Client | None = None):
        self.http = client or httpx.Client(
            headers={"User-Agent": USER_AGENT}, timeout=20, follow_redirects=True
        )

    def search(self, query: str, k: int = 5) -> list[dict[str, str]]:
        r = self.http.get(WIKI_API, params={
            "action": "query", "list": "search", "srsearch": query,
            "srlimit": k, "format": "json",
        })
        r.raise_for_status()
        return [
            {
                "title": hit["title"],
                "url": "https://en.wikipedia.org/wiki/" + hit["title"].replace(" ", "_"),
                "snippet": _clean(hit.get("snippet", "")),
            }
            for hit in r.json().get("query", {}).get("search", [])
        ]

    def read(self, title: str) -> str:
        r = self.http.get(WIKI_HTML + quote(title.replace(" ", "_"), safe=""))
        r.raise_for_status()
        return html_to_text(r.text)


class TinyFishWeb:
    """Web search + fetch via the `tinyfish` CLI (uses the CLI's saved API key)."""

    def __init__(self, binary: str = "tinyfish", timeout: float = 60):
        self.binary = shutil.which(binary) or binary
        self.timeout = timeout

    def _run(self, *args: str) -> dict:
        out = subprocess.run(
            [self.binary, *args], capture_output=True, text=True, timeout=self.timeout
        )
        if out.returncode != 0:
            raise RuntimeError(f"tinyfish {args[0]} failed: {out.stderr.strip()[:300]}")
        return json.loads(out.stdout)

    def search(self, query: str, k: int = 5) -> list[dict[str, str]]:
        data = self._run("search", "query", query)
        return [
            {"title": r["title"], "url": r["url"], "snippet": r.get("snippet", "")}
            for r in data.get("results", [])[:k]
        ]

    def read(self, url: str) -> str:
        data = self._run("fetch", "content", "get", url)
        results = data.get("results") or []
        return (results[0].get("text") or "") if results else ""


class DefaultTools:
    """Routes searches/reads to the right backend and traces each call."""

    def __init__(self, wikipedia: Wikipedia | None = None, web: TinyFishWeb | None = None):
        self.wikipedia = wikipedia or Wikipedia()
        self.web = web or TinyFishWeb()

    def search(self, engine: Origin, query: str, k: int = 5) -> list[dict[str, str]]:
        with tracer.start_as_current_span(
            f"{engine.value}.search", openinference_span_kind="retriever"
        ) as span:
            span.set_input(query)
            backend = self.wikipedia if engine is Origin.WIKIPEDIA else self.web
            results = backend.search(query, k)
            for i, r in enumerate(results):
                prefix = f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.{i}"
                span.set_attribute(f"{prefix}.{DocumentAttributes.DOCUMENT_ID}", r["url"])
                span.set_attribute(
                    f"{prefix}.{DocumentAttributes.DOCUMENT_CONTENT}",
                    f"{r['title']}: {r['snippet']}",
                )
            span.set_output(to_json(results), mime_type="application/json")
            return results

    def read(self, candidate: Candidate, max_chars: int, focus: str = "") -> str:
        with tracer.start_as_current_span("read_source", openinference_span_kind="tool") as span:
            span.set_tool(
                name="read_source",
                description="Fetch the full text of a search result",
                parameters={"id": candidate.id, "url": candidate.url},
            )
            span.set_input(to_json({"id": candidate.id, "url": candidate.url}),
                           mime_type="application/json")
            if candidate.origin is Origin.WIKIPEDIA:
                full = self.wikipedia.read(candidate.title)
            else:
                full = self.web.read(candidate.url)
            text = select_passages(full, focus, max_chars)
            span.set_output(text[:2000] + ("..." if len(text) > 2000 else ""))
            span.set_attributes({"read.page_chars": len(full), "read.kept_chars": len(text)})
            return text
