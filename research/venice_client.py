"""Venice.ai API client for Sentinel research engine."""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .models import ScrapeResult

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://apihub.agnes-ai.com/v1"
DEFAULT_MODEL = "agnes-1.5-flash"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class VeniceError(RuntimeError):
    """Raised when the Venice API returns an unusable response."""


@dataclass(frozen=True)
class VeniceClient:
    api_key: str
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 60.0
    max_retries: int = 2
    backoff_seconds: float = 1.0

    @classmethod
    def from_env(cls, model: str | None = None, *, max_retries: int = 2) -> VeniceClient:
        api_key = os.getenv("VENICE_API_KEY", "")
        return cls(
            api_key=api_key,
            model=model or os.getenv("VENICE_MODEL", DEFAULT_MODEL),
            base_url=os.getenv("VENICE_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            max_retries=max_retries,
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1600,
    ) -> str:
        if not self.is_configured:
            log.warning("Venice API not configured — using mock response")
            return _mock_chat_response(messages)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            data = self._post_json("/chat/completions", payload)
            return data["choices"][0]["message"]["content"].strip()
        except VeniceError as exc:
            log.warning("Venice chat failed (%s) — falling back to mock", exc)
            return _mock_chat_response(messages)

    def chat_stream(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1600,
    ) -> str:
        if not self.is_configured:
            log.warning("Venice API not configured — using mock response")
            return _mock_chat_response(messages)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        try:
            return self._post_chat_stream("/chat/completions", payload).strip()
        except VeniceError as exc:
            log.warning("Venice stream failed (%s) — falling back to mock", exc)
            return _mock_chat_response(messages)

    def scrape(self, url: str) -> ScrapeResult:
        if not self.is_configured:
            log.warning("Venice API not configured — mock scrape for %s", url)
            return ScrapeResult(url=url, content=f"[MOCK] Content unavailable — Venice API not configured for {url}", title=f"Mock: {url}")
        try:
            data = self._post_json("/augment/scrape", {"url": url})
            content = _first_string(data, "content", "markdown", "text")
            if not content:
                return ScrapeResult(url=url, content=f"[FALLBACK] Empty response from scrape for {url}", title=f"Fallback: {url}")
            return ScrapeResult(
                url=url,
                final_url=_first_string(data, "final_url", "url", "source_url") or url,
                title=_first_string(data, "title"),
                content=content,
                content_type="text/markdown",
            )
        except VeniceError as exc:
            log.warning("Venice scrape failed for %s: %s", url, exc)
            return ScrapeResult(url=url, content=f"[MOCK] Scrape failed for {url}: {exc}", title=f"Mock: {url}")

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.post(
                    f"{self.base_url}{path}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=self.timeout,
                )
                if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * (2 ** attempt))
                    continue
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise VeniceError(f"Unexpected Venice API response: {data}")
                return data
            except httpx.HTTPError as exc:
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * (2 ** attempt))
                    continue
                raise VeniceError(f"Could not reach Venice API: {exc}") from exc
        raise VeniceError("Could not reach Venice API after retries")

    def _post_chat_stream(self, path: str, payload: dict[str, Any]) -> str:
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.stream(
                    "POST",
                    f"{self.base_url}{path}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=self.timeout,
                ) as response:
                    if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                        time.sleep(self.backoff_seconds * (2 ** attempt))
                        continue
                    response.raise_for_status()
                    chunks: list[str] = []
                    for line in response.iter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0]["delta"]
                            if "content" in delta:
                                chunks.append(delta["content"])
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
                    return "".join(chunks)
            except httpx.HTTPError as exc:
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * (2 ** attempt))
                    continue
                raise VeniceError(f"Could not reach Venice API: {exc}") from exc
        raise VeniceError("Could not reach Venice API after retries")


def _first_string(data: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for nested_key in ("data", "result", "scrape"):
        nested = data.get(nested_key)
        if isinstance(nested, dict):
            value = _first_string(nested, *keys)
            if value:
                return value
    return ""


def _mock_chat_response(messages: list[dict[str, str]]) -> str:
    user_msg = ""
    for m in messages:
        if m.get("role") == "user":
            user_msg = m.get("content", "")
            break
    if "queries" in user_msg.lower():
        return '{"queries": ["AI agent safety mechanisms 2026", "autonomous agent verification", "multi-agent research systems"]}'
    if "evidence" in user_msg.lower() or "extract" in user_msg.lower():
        return '{"summary": "This source discusses key findings relevant to the research topic.", "quotes": ["Key insight from the source material."]}'
    return "[MOCK] Venice API not configured with credits. Add credits at https://venice.ai/settings/billing to enable real research."
