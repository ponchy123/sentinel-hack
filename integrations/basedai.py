"""BasedAI governance layer — scores agent decisions for trust and accountability.

BasedAI provides decentralized LLM inference with built-in governance scoring.
This module wraps their API to add governance scores to each agent's output,
creating an auditable trail of AI decision-making.
"""
from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass

import httpx

log = logging.getLogger(__name__)

BASEDAI_API = "https://api.basedai.com/v1"


@dataclass
class GovernanceScore:
    agent_name: str
    decision_hash: str
    trust_score: float
    accountability_score: float
    timestamp: float
    reasoning: str


class BasedAIClient:
    """Client for BasedAI governance scoring."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    @classmethod
    def from_env(cls) -> BasedAIClient:
        import os
        return cls(api_key=os.getenv("BASEDAI_API_KEY", ""))

    def score_decision(self, agent_name: str, input_text: str, output_text: str) -> GovernanceScore:
        """
        Score an agent's decision for governance purposes.
        Uses content hashing + heuristic scoring when API is unavailable.
        """
        decision_content = f"{agent_name}:{input_text}:{output_text}"
        decision_hash = hashlib.sha256(decision_content.encode()).hexdigest()[:16]

        # Try API first
        if self.api_key:
            try:
                return self._api_score(agent_name, decision_hash, input_text, output_text)
            except Exception as exc:
                log.warning("BasedAI API failed, using local scoring: %s", exc)

        # Local governance scoring based on content analysis
        return self._local_score(agent_name, decision_hash, input_text, output_text)

    def _api_score(self, agent_name: str, decision_hash: str, input_text: str, output_text: str) -> GovernanceScore:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"{BASEDAI_API}/governance/score",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"agent": agent_name, "input": input_text, "output": output_text},
            )
            resp.raise_for_status()
            data = resp.json()
            return GovernanceScore(
                agent_name=agent_name,
                decision_hash=decision_hash,
                trust_score=data.get("trust_score", 0.5),
                accountability_score=data.get("accountability_score", 0.5),
                timestamp=time.time(),
                reasoning=data.get("reasoning", "API-scored"),
            )

    def _local_score(self, agent_name: str, decision_hash: str, input_text: str, output_text: str) -> GovernanceScore:
        """Local governance scoring based on content quality heuristics."""
        # Trust: based on output specificity and citation count
        citation_count = output_text.count("[") + output_text.count("Source:")
        specificity = min(1.0, len(output_text) / 500)
        trust = min(1.0, 0.3 + citation_count * 0.1 + specificity * 0.3)

        # Accountability: based on source diversity and transparency
        source_indicators = output_text.lower().count("source") + output_text.lower().count("found via")
        transparency = 0.5 if "error" not in output_text.lower() else 0.2
        accountability = min(1.0, 0.4 + source_indicators * 0.05 + transparency * 0.3)

        reasoning_parts = []
        if citation_count > 0:
            reasoning_parts.append(f"{citation_count} citations found")
        if specificity > 0.5:
            reasoning_parts.append("detailed output")
        if "error" not in output_text.lower():
            reasoning_parts.append("no errors")
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "basic scoring"

        return GovernanceScore(
            agent_name=agent_name,
            decision_hash=decision_hash,
            trust_score=round(trust, 3),
            accountability_score=round(accountability, 3),
            timestamp=time.time(),
            reasoning=reasoning,
        )


def score_agent_decisions(results: dict[str, dict], topic: str) -> list[GovernanceScore]:
    """Score all agent decisions for governance audit trail."""
    client = BasedAIClient.from_env()
    scores = []
    for agent_name, data in results.items():
        findings = data.get("findings", "")
        score = client.score_decision(agent_name, topic, findings)
        scores.append(score)
        log.info("Governance score for %s: trust=%.2f, accountability=%.2f",
                 agent_name, score.trust_score, score.accountability_score)
    return scores
