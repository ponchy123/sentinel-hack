"""Kaspa on-chain verification — records research report hashes on Kaspa blockDAG.

Kaspa is a proof-of-work blockDAG chain with fast finality. This module
records SHA-256 hashes of research reports on Kaspa, creating an immutable
audit trail that proves a report existed at a specific time.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass

import httpx

log = logging.getLogger(__name__)

KASPA_API_MAINNET = "https://api.kaspa.org"
KASPA_API_TESTNET = "https://api-tn1.kaspa.org"


@dataclass
class KaspaRecord:
    report_hash: str
    topic: str
    agent_count: int
    source_count: int
    timestamp: float
    kaspa_tx_id: str | None = None
    verified: bool = False


class KaspaClient:
    """Client for Kaspa on-chain verification."""

    def __init__(self, network: str = "testnet"):
        self.base_url = KASPA_API_TESTNET if network == "testnet" else KASPA_API_MAINNET

    @classmethod
    def from_env(cls) -> KaspaClient:
        import os
        return cls(network=os.getenv("KASPA_NETWORK", "testnet"))

    def compute_report_hash(self, report_text: str, topic: str) -> str:
        """Compute a deterministic hash for a research report."""
        content = f"{topic}:{report_text}"
        return hashlib.sha256(content.encode()).hexdigest()

    def record_hash(self, report_hash: str, topic: str, metadata: dict) -> KaspaRecord:
        """
        Record a report hash on Kaspa network.
        Returns a KaspaRecord with verification status.
        """
        record = KaspaRecord(
            report_hash=report_hash,
            topic=topic,
            agent_count=metadata.get("agent_count", 0),
            source_count=metadata.get("source_count", 0),
            timestamp=time.time(),
        )

        # Build Kaspa OP_RETURN payload
        payload = json.dumps({
            "type": "sentinel_research",
            "hash": report_hash,
            "topic": topic,
            "ts": int(record.timestamp),
        }).encode()

        # Try to submit via Kaspa API
        try:
            tx_id = self._submit_op_return(payload)
            record.kaspa_tx_id = tx_id
            record.verified = True
            log.info("Kaspa record submitted: tx=%s", tx_id)
        except Exception as exc:
            log.warning("Kaspa submission failed (using local record): %s", exc)
            record.kaspa_tx_id = f"local:{report_hash[:12]}"
            record.verified = False

        return record

    def verify_hash(self, report_hash: str) -> dict:
        """Verify a report hash exists on Kaspa network."""
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{self.base_url}/api/search/hash/{report_hash}")
                if resp.status_code == 200:
                    data = resp.json()
                    return {"verified": True, "block_data": data}
                return {"verified": False, "reason": "Hash not found on chain"}
        except Exception as exc:
            return {"verified": False, "reason": f"Network error: {exc}"}

    def _submit_op_return(self, payload: bytes) -> str:
        """Submit OP_RETURN transaction to Kaspa."""
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                f"{self.base_url}/api/transactions",
                json={"data": payload.hex()},
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("txid", "unknown")


def record_research_on_kaspa(report_text: str, topic: str, agent_results: dict) -> KaspaRecord:
    """Record research results on Kaspa chain."""
    client = KaspaClient.from_env()
    report_hash = client.compute_report_hash(report_text, topic)

    source_count = sum(d.get("source_count", 0) for d in agent_results.values())
    metadata = {
        "agent_count": len(agent_results),
        "source_count": source_count,
    }

    return client.record_hash(report_hash, topic, metadata)
