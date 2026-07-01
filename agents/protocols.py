"""Shared message models for Sentinel multi-agent communication."""
from __future__ import annotations

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    topic: str
    depth: str = "standard"  # "quick" | "standard" | "deep"
    sources: list[str] = ["academic", "market", "code"]


class ResearchResult(BaseModel):
    agent_name: str
    findings: str
    source_count: int = 0
    confidence: float = 0.0


class AgentStatus(BaseModel):
    agent_name: str
    status: str  # "idle" | "working" | "done" | "error"
    message: str = ""
    progress: float = 0.0


class AggregatedResult(BaseModel):
    topic: str
    academic_result: str = ""
    market_result: str = ""
    code_result: str = ""
    report: str = ""
    verification_score: float | None = None
