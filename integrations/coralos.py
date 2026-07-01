"""CoralOS agent registry — registers Sentinel agents on Solana-based Coral Protocol.

CoralOS provides a decentralized agent marketplace on Solana. This module
registers each Sentinel agent as a verifiable entity, linking on-chain
identity to agent capabilities and research outputs.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field

import httpx

log = logging.getLogger(__name__)

CORAL_API = "https://api.coralos.ai/v1"


@dataclass
class AgentRegistration:
    agent_id: str
    agent_name: str
    capabilities: list[str]
    registered_at: float
    coral_tx_id: str | None = None
    verified: bool = False


@dataclass
class CoralOSResult:
    registrations: list[AgentRegistration] = field(default_factory=list)
    total_agents: int = 0
    verified_count: int = 0


class CoralOSClient:
    """Client for CoralOS agent registration on Solana."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    @classmethod
    def from_env(cls) -> CoralOSClient:
        import os
        return cls(api_key=os.getenv("CORALOS_API_KEY", ""))

    def register_agent(self, agent_name: str, capabilities: list[str], description: str) -> AgentRegistration:
        """
        Register an agent on CoralOS.
        Creates a deterministic agent ID from name + capabilities.
        """
        # Generate deterministic agent ID
        content = f"{agent_name}:{':'.join(sorted(capabilities))}"
        agent_id = hashlib.sha256(content.encode()).hexdigest()[:12]

        registration = AgentRegistration(
            agent_id=agent_id,
            agent_name=agent_name,
            capabilities=capabilities,
            registered_at=time.time(),
        )

        # Try CoralOS API
        if self.api_key:
            try:
                tx_id = self._api_register(agent_name, capabilities, description)
                registration.coral_tx_id = tx_id
                registration.verified = True
                log.info("CoralOS registered %s: tx=%s", agent_name, tx_id)
                return registration
            except Exception as exc:
                log.warning("CoralOS API failed for %s: %s", agent_name, exc)

        # Local registration (deterministic ID still useful for cross-referencing)
        registration.coral_tx_id = f"local:{agent_id}"
        registration.verified = False
        return registration

    def _api_register(self, name: str, capabilities: list[str], description: str) -> str:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"{CORAL_API}/agents/register",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"name": name, "capabilities": capabilities, "description": description},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("tx_id", "unknown")

    def verify_agent(self, agent_id: str) -> dict:
        """Verify an agent registration on CoralOS."""
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{CORAL_API}/agents/{agent_id}")
                if resp.status_code == 200:
                    return {"verified": True, "data": resp.json()}
                return {"verified": False, "reason": "Agent not found"}
        except Exception as exc:
            return {"verified": False, "reason": f"Network error: {exc}"}


# Agent capability definitions for Sentinel
SENTINEL_AGENTS = {
    "academic": {
        "name": "Sentinel Academic Agent",
        "capabilities": ["arxiv_search", "paper_analysis", "citation_extraction", "web_scraping"],
        "description": "Searches academic papers on ArXiv and web, extracts evidence, generates cited summaries.",
    },
    "market": {
        "name": "Sentinel Market Agent",
        "capabilities": ["market_data", "coin_search", "trend_analysis", "price_tracking"],
        "description": "Queries CoinGecko for market data, identifies trending assets, tracks price movements.",
    },
    "code": {
        "name": "Sentinel Code Agent",
        "capabilities": ["github_search", "repo_analysis", "dependency_tracking", "code_review"],
        "description": "Searches GitHub repositories, analyzes code quality, tracks dependencies and stars.",
    },
}


def register_sentinel_agents() -> CoralOSResult:
    """Register all Sentinel agents on CoralOS."""
    client = CoralOSClient.from_env()
    result = CoralOSResult()

    for agent_type, config in SENTINEL_AGENTS.items():
        reg = client.register_agent(
            agent_name=config["name"],
            capabilities=config["capabilities"],
            description=config["description"],
        )
        result.registrations.append(reg)
        result.total_agents += 1
        if reg.verified:
            result.verified_count += 1

    log.info("CoralOS registration complete: %d agents, %d verified",
             result.total_agents, result.verified_count)
    return result
