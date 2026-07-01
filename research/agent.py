"""Core research agent logic — plans searches, reads sources, writes reports."""
from __future__ import annotations

import json
from collections.abc import Callable
from textwrap import dedent
from urllib.parse import urlparse

from .models import (
    CollectionError, EvidenceChunk, ResearchReport, SearchResult,
    SourceNote, WebPage, utc_now,
)
from .venice_client import VeniceClient, VeniceError
from .web_search import WebSearch

SYSTEM_PROMPT = """You are a careful research assistant.
Use the supplied source material only when making factual claims.
Flag uncertainty, contradictions, and missing context instead of filling gaps."""

ProgressCallback = Callable[[str], None]

DEFAULT_ITERATIONS = 2
DEFAULT_QUERY_COUNT = 4
DEFAULT_RESULTS_PER_QUERY = 3
DEFAULT_MAX_SOURCES = 20
DEFAULT_MAX_CHUNKS_PER_SOURCE = 4


class ResearchAgent:
    def __init__(
        self,
        venice: VeniceClient,
        web: WebSearch | None = None,
        progress: ProgressCallback | None = None,
        max_sources: int | None = DEFAULT_MAX_SOURCES,
        max_chunks_per_source: int = DEFAULT_MAX_CHUNKS_PER_SOURCE,
    ) -> None:
        self.venice = venice
        self.web = web or WebSearch(scraper=venice.scrape)
        self.progress = progress or (lambda _: None)
        self.max_sources = max_sources
        self.max_chunks_per_source = max_chunks_per_source

    def run(
        self,
        topic: str,
        *,
        iterations: int = DEFAULT_ITERATIONS,
        query_count: int = DEFAULT_QUERY_COUNT,
        results_per_query: int = DEFAULT_RESULTS_PER_QUERY,
    ) -> ResearchReport:
        notes: list[SourceNote] = []
        seen_source_keys: set[str] = set()
        seen_content_hashes: set[str] = set()
        queries = self._initial_queries(topic, query_count)

        for iteration in range(1, iterations + 1):
            self.progress(f"Research pass {iteration}/{iterations}: {', '.join(queries)}")
            self._collect_notes(
                topic, queries, results_per_query,
                seen_source_keys, seen_content_hashes, notes, iteration,
            )
            if iteration < iterations:
                queries = self._follow_up_queries(topic, notes, query_count)

        report = self._write_report(topic, notes)
        return ResearchReport(
            topic=topic,
            markdown=report,
            sources=notes,
        )

    def _initial_queries(self, topic: str, count: int) -> list[str]:
        prompt = dedent(f"""
            Create {count} diverse web search queries for researching this topic:
            {topic}
            Cover background, recent developments, primary sources, criticism, and data.
            Return JSON only: {{"queries": ["..."]}}
        """).strip()
        return self._query_list(prompt, count, fallback=[topic])

    def _follow_up_queries(self, topic: str, notes: list[SourceNote], count: int) -> list[str]:
        digest = _source_digest(notes, max_chars=6000)
        prompt = dedent(f"""
            We are researching: {topic}
            Current notes:
            {digest}
            Create {count} follow-up queries that fill gaps, verify claims,
            and look for dissenting evidence.
            Return JSON only: {{"queries": ["..."]}}
        """).strip()
        return self._query_list(prompt, count, fallback=[topic])

    def _query_list(self, prompt: str, count: int, fallback: list[str]) -> list[str]:
        response = self.venice.chat(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.4, max_tokens=500,
        )
        try:
            data = json.loads(response)
            queries = data.get("queries", [])
        except (json.JSONDecodeError, AttributeError):
            queries = []
        clean = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
        return (clean or fallback)[:count]

    def _collect_notes(
        self, topic: str, queries: list[str], results_per_query: int,
        seen_source_keys: set[str], seen_content_hashes: set[str],
        notes: list[SourceNote], iteration: int,
    ) -> None:
        for query in queries:
            if self.max_sources is not None and len(notes) >= self.max_sources:
                return
            self.progress(f"Searching: {query}")
            try:
                results = self.web.search(query, limit=results_per_query)
            except Exception as exc:
                self.progress(f"Search failed: {exc}")
                continue
            for result in results:
                if self.max_sources is not None and len(notes) >= self.max_sources:
                    return
                source_key = result.canonical_url or result.url
                if source_key in seen_source_keys:
                    continue
                seen_source_keys.add(source_key)
                source_id = f"S{len(notes) + 1}"
                note = self._read_source(topic, query, source_id, result, seen_content_hashes)
                if note is not None:
                    notes.append(note)

    def _read_source(
        self, topic: str, query: str, source_id: str,
        result: SearchResult, seen_content_hashes: set[str],
    ) -> SourceNote | None:
        self.progress(f"Reading {source_id}: {result.title}")
        try:
            page = self.web.fetch(result)
        except Exception as exc:
            self.progress(f"Fetch failed for {result.url}: {exc}")
            return None
        if page.content_hash in seen_content_hashes:
            return None
        seen_content_hashes.add(page.content_hash)
        chunks = self._summarize_chunks(topic, query, source_id, page)
        if not chunks:
            return None
        summary = self._summarize_source(topic, query, source_id, page, chunks)
        return SourceNote(
            source_id=source_id, title=page.title, url=result.url,
            canonical_url=page.canonical_url, final_url=page.final_url,
            query=query, rank=result.rank, snippet=result.snippet,
            provider=result.provider, retrieved_at=page.retrieved_at,
            content_type=page.content_type, content_hash=page.content_hash,
            chunks=chunks, summary=summary,
        )

    def _summarize_chunks(
        self, topic: str, query: str, source_id: str, page: WebPage,
    ) -> tuple[EvidenceChunk, ...]:
        evidence: list[EvidenceChunk] = []
        for chunk in page.chunks[: self.max_chunks_per_source]:
            prompt = dedent(f"""
                Topic: {topic}
                Search query: {query}
                Source ID: {source_id}
                Chunk ID: {chunk.chunk_id}
                Source title: {page.title}
                Source URL: {page.final_url}

                Source chunk:
                {chunk.text}

                Extract only evidence relevant to the topic.
                Return JSON only: {{"summary": "...", "quotes": ["short quote", "..."]}}
            """).strip()
            try:
                response = self.venice.chat(
                    [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                    temperature=0.1, max_tokens=600,
                )
                data = json.loads(response)
                evidence.append(EvidenceChunk(
                    chunk_id=chunk.chunk_id, text=chunk.text,
                    summary=str(data.get("summary", "")).strip(),
                    quotes=tuple(
                        q.strip() for q in data.get("quotes", [])
                        if isinstance(q, str) and q.strip()
                    ),
                ))
            except Exception:
                continue
        return tuple(evidence)

    def _summarize_source(
        self, topic: str, query: str, source_id: str,
        page: WebPage, chunks: tuple[EvidenceChunk, ...],
    ) -> str:
        chunk_digest = _chunk_digest(chunks, max_chars=6000)
        prompt = dedent(f"""
            Topic: {topic}
            Search query: {query}
            Source ID: {source_id}
            Source title: {page.title}
            Source URL: {page.final_url}

            Chunk evidence:
            {chunk_digest}

            Synthesize a source note using only the chunk evidence.
            Include key facts, limitations, and useful quotes.
            Keep under 150 words. Refer to source as [{source_id}].
        """).strip()
        return self.venice.chat(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.1, max_tokens=500,
        )

    def _write_report(self, topic: str, notes: list[SourceNote]) -> str:
        if not notes:
            return f"# Research report: {topic}\n\nNo usable web sources were collected."
        prompt = dedent(f"""
            Research topic: {topic}

            Source notes:
            {_source_digest(notes, max_chars=30000)}

            Write a detailed source-backed Markdown research survey.
            - Start with H1 title
            - Open with "## Overview"
            - Use topic-specific sections
            - Use footnote-style citations [^1] [^2]
            - Do not cite with internal source IDs like [S1]
            - Include uncertainty and contradictions
            - End with "## References" as numbered list
        """).strip()
        return self.venice.chat_stream(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=5000,
        )


def _chunk_digest(chunks: tuple[EvidenceChunk, ...], max_chars: int) -> str:
    parts = []
    for chunk in chunks:
        quote_text = "; ".join(chunk.quotes)
        parts.append(f"{chunk.chunk_id}: {chunk.summary}" + (f"\nQuotes: {quote_text}" if quote_text else ""))
    return "\n\n".join(parts)[:max_chars]


def _source_digest(notes: list[SourceNote], max_chars: int) -> str:
    chunks = [
        "\n".join([
            f"[{note.source_id}] {note.title}",
            f"URL: {note.final_url or note.url}",
            f"Found via: {note.query}",
            f"Note: {note.summary}",
        ])
        for note in notes
    ]
    return "\n\n".join(chunks)[:max_chars]
