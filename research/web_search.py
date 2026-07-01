"""Web search layer with multiple providers."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterable
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from .models import (
    ScrapeResult, SearchResult, TextChunk, WebPage,
    canonicalize_url, chunk_text, content_hash, utc_now,
)

USER_AGENT = "sentinel-research-agent/0.1 (+https://github.com/sentinel-hack)"


class SearchProvider:
    name = "provider"

    def search(self, web: WebSearch, query: str, limit: int) -> list[SearchResult]:
        raise NotImplementedError


class DuckDuckGoProvider(SearchProvider):
    name = "duckduckgo"

    def search(self, web: WebSearch, query: str, limit: int) -> list[SearchResult]:
        response = web.get("https://duckduckgo.com/html/", params={"q": query})
        soup = BeautifulSoup(response.text, "html.parser")
        results: list[SearchResult] = []
        seen_urls: set[str] = set()

        for node in soup.select(".result"):
            link = node.select_one(".result__a")
            if link is None:
                continue
            url = _normalize_duckduckgo_url(link.get("href", ""))
            canonical_url = canonicalize_url(url)
            if not canonical_url or canonical_url in seen_urls:
                continue
            snippet = node.select_one(".result__snippet")
            results.append(SearchResult(
                title=_clean_text(link.get_text(" ", strip=True)),
                url=url,
                snippet=_clean_text(snippet.get_text(" ", strip=True) if snippet else ""),
                query=query,
                rank=len(results) + 1,
                provider=self.name,
                canonical_url=canonical_url,
            ))
            seen_urls.add(canonical_url)
            if len(results) >= limit:
                break
        return results


class ArxivProvider(SearchProvider):
    name = "arxiv"

    def search(self, web: WebSearch, query: str, limit: int) -> list[SearchResult]:
        response = web.get(
            "https://export.arxiv.org/api/query",
            params={
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": limit,
                "sortBy": "relevance",
            },
        )
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(response.text)
        results: list[SearchResult] = []

        for entry in root.findall("atom:entry", namespace):
            title = _clean_text(_xml_text(entry.find("atom:title", namespace)))
            summary = _clean_text(_xml_text(entry.find("atom:summary", namespace)))
            url = _xml_text(entry.find("atom:id", namespace)).strip()
            canonical_url = canonicalize_url(url)
            if not url or not canonical_url:
                continue
            results.append(SearchResult(
                title=title or url,
                url=url,
                snippet=summary,
                query=query,
                rank=len(results) + 1,
                provider=self.name,
                canonical_url=canonical_url,
            ))
            if len(results) >= limit:
                break
        return results


class GitHubProvider(SearchProvider):
    name = "github"

    def search(self, web: WebSearch, query: str, limit: int) -> list[SearchResult]:
        response = web.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "per_page": limit},
        )
        data = response.json()
        results: list[SearchResult] = []
        for item in data.get("items", [])[:limit]:
            url = item.get("html_url", "")
            canonical_url = canonicalize_url(url)
            if not canonical_url:
                continue
            results.append(SearchResult(
                title=item.get("full_name", ""),
                url=url,
                snippet=item.get("description", "") or "",
                query=query,
                rank=len(results) + 1,
                provider=self.name,
                canonical_url=canonical_url,
            ))
        return results


class WebSearch:
    def __init__(
        self,
        timeout: float = 15.0,
        *,
        providers: Iterable[SearchProvider] | None = None,
        chunk_chars: int = 3000,
        scraper: Callable[[str], ScrapeResult] | None = None,
    ) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        self.providers = tuple(providers or (DuckDuckGoProvider(),))
        self.chunk_chars = chunk_chars
        self.scraper = scraper

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        results: list[SearchResult] = []
        seen_urls: set[str] = set()
        for provider in self.providers:
            for result in provider.search(self, query, limit):
                if result.canonical_url in seen_urls:
                    continue
                results.append(result)
                seen_urls.add(result.canonical_url)
        return results

    def fetch(self, result: SearchResult) -> WebPage:
        if self.scraper is None:
            raise RuntimeError("WebSearch.fetch requires a Venice scrape function.")
        scraped = self.scraper(result.url)
        text = scraped.content.strip() or result.snippet
        chunks = self._chunk_text(text)
        return WebPage(
            title=scraped.title or result.title,
            url=result.url,
            final_url=scraped.final_url or scraped.url or result.url,
            canonical_url=canonicalize_url(scraped.final_url or result.url),
            text=text,
            content_type=scraped.content_type or "text/markdown",
            retrieved_at=utc_now(),
            content_hash=content_hash(text),
            chunks=chunks,
        )

    def get(self, url: str, *, params: dict[str, object] | None = None) -> httpx.Response:
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> WebSearch:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _chunk_text(self, text: str) -> tuple[TextChunk, ...]:
        overlap = min(250, max(0, self.chunk_chars // 10))
        return chunk_text(text, chunk_chars=self.chunk_chars, overlap=overlap)


def _normalize_duckduckgo_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    parsed = urlparse(raw_url)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path == "/l/":
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        return unquote(target)
    if parsed.scheme in {"http", "https"}:
        return raw_url
    return ""


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _xml_text(node: ET.Element | None) -> str:
    return "" if node is None or node.text is None else node.text
