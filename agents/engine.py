"""Multi-agent research engine — coordinates 3 specialist agents in parallel."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Callable, Awaitable

from research.venice_client import VeniceClient
from research.web_search import WebSearch, ArxivProvider, DuckDuckGoProvider, GitHubProvider
from research.agent import ResearchAgent

log = logging.getLogger(__name__)

ProgressCallback = Callable[[str, str, str, float], Awaitable[None]]  # (agent, status, message, progress)


@dataclass
class AgentResult:
    agent_name: str
    findings: str = ""
    source_count: int = 0
    confidence: float = 0.0
    sources: list[dict] = field(default_factory=list)


async def run_academic(topic: str, venice: VeniceClient, progress: ProgressCallback | None = None) -> AgentResult:
    """Run academic research via ArXiv + DuckDuckGo."""
    if progress:
        await progress("academic", "working", f"Searching ArXiv for: {topic}", 0.1)

    def _do_research():
        web = WebSearch(providers=[ArxivProvider(), DuckDuckGoProvider()], scraper=venice.scrape)
        agent = ResearchAgent(venice=venice, web=web, max_sources=8)
        return agent.run(topic, iterations=1, query_count=3, results_per_query=3)

    loop = asyncio.get_event_loop()
    try:
        report = await loop.run_in_executor(None, _do_research)
        sources = [
            {"id": s.source_id, "title": s.title, "url": s.url, "provider": s.provider, "summary": s.summary}
            for s in report.sources
        ]
        if progress:
            await progress("academic", "done", f"Found {len(report.sources)} sources", 1.0)
        return AgentResult(
            agent_name="academic",
            findings=report.markdown,
            source_count=len(report.sources),
            confidence=min(0.9, 0.5 + len(report.sources) * 0.05),
            sources=sources,
        )
    except Exception as exc:
        log.error("Academic research failed: %s", exc)
        if progress:
            await progress("academic", "error", str(exc), 0.0)
        return AgentResult(agent_name="academic", findings=f"Error: {exc}")


async def run_market(topic: str, progress: ProgressCallback | None = None) -> AgentResult:
    """Run market research via CoinGecko API."""
    if progress:
        await progress("market", "working", f"Searching CoinGecko for: {topic}", 0.1)

    import httpx
    findings_parts: list[str] = []
    sources: list[dict] = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get("https://api.coingecko.com/api/v3/search", params={"query": topic})
            if resp.status_code == 200:
                coins = resp.json().get("coins", [])[:5]
                for coin in coins:
                    name = coin.get("name", "N/A")
                    symbol = coin.get("symbol", "N/A")
                    rank = coin.get("market_cap_rank", "N/A")
                    findings_parts.append(f"- **{name}** ({symbol}): Market Cap Rank #{rank}")
                    sources.append({"id": f"cg-{symbol}", "title": name, "url": f"https://coingecko.com/en/coins/{symbol}", "provider": "coingecko"})
                    if progress:
                        await progress("market", "working", f"Found {name}...", 0.3)
        except Exception:
            pass
        try:
            resp = await client.get("https://api.coingecko.com/api/v3/search/trending")
            if resp.status_code == 200:
                trending = resp.json().get("coins", [])[:3]
                if trending:
                    findings_parts.append("\n### Trending")
                    for item in trending:
                        coin = item.get("item", {})
                        findings_parts.append(f"- {coin.get('name', 'N/A')} (Score: {coin.get('score', 'N/A')})")
        except Exception:
            pass

    if not findings_parts:
        findings_parts.append(f"No specific market data found for '{topic}'.")

    findings = f"## Market Data for: {topic}\n\n" + "\n".join(findings_parts)
    if progress:
        await progress("market", "done", f"Found {len(sources)} market data points", 1.0)
    return AgentResult(
        agent_name="market", findings=findings,
        source_count=max(1, len(findings_parts)),
        confidence=0.6 if findings_parts else 0.1, sources=sources,
    )


async def run_code(topic: str, progress: ProgressCallback | None = None) -> AgentResult:
    """Run code research via GitHub API."""
    if progress:
        await progress("code", "working", f"Searching GitHub for: {topic}", 0.1)

    import httpx
    findings_parts: list[str] = []
    sources: list[dict] = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(
                "https://api.github.com/search/repositories",
                params={"q": topic, "sort": "stars", "order": "desc", "per_page": 5},
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            if resp.status_code == 200:
                repos = resp.json().get("items", [])
                if repos:
                    findings_parts.append("### Top Repositories")
                    for repo in repos:
                        name = repo.get("full_name", "N/A")
                        stars = repo.get("stargazers_count", 0)
                        forks = repo.get("forks_count", 0)
                        desc = repo.get("description", "No description")
                        lang = repo.get("language", "N/A")
                        findings_parts.append(f"- **{name}** (Stars: {stars}, Forks: {forks})\n  {desc}\n  Language: {lang}")
                        sources.append({"id": f"gh-{name}", "title": name, "url": repo.get("html_url", ""), "provider": "github"})
                        if progress:
                            await progress("code", "working", f"Found {name}...", 0.3)
        except Exception:
            pass

    if not findings_parts:
        findings_parts.append(f"No specific code found for '{topic}'.")

    findings = f"## Code Research for: {topic}\n\n" + "\n".join(findings_parts)
    if progress:
        await progress("code", "done", f"Found {len(sources)} repositories", 1.0)
    return AgentResult(
        agent_name="code", findings=findings,
        source_count=max(1, len(findings_parts)),
        confidence=0.6 if findings_parts else 0.1, sources=sources,
    )


async def run_research(
    topic: str,
    sources: list[str],
    progress: ProgressCallback | None = None,
) -> dict:
    """Run all agents in parallel and aggregate results."""
    venice = VeniceClient.from_env()
    tasks = []

    if "academic" in sources:
        tasks.append(("academic", run_academic(topic, venice, progress)))
    if "market" in sources:
        tasks.append(("market", run_market(topic, progress)))
    if "code" in sources:
        tasks.append(("code", run_code(topic, progress)))

    # Run all agents concurrently
    agent_results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)

    results = {}
    for (name, _), result in zip(tasks, agent_results):
        if isinstance(result, Exception):
            results[name] = AgentResult(agent_name=name, findings=f"Error: {result}")
        else:
            results[name] = result

    # Build report
    parts = [f"# Research Report: {topic}\n"]
    for name, r in results.items():
        parts.append(f"\n## {name.title()} Research\n\n{r.findings}\n")
        parts.append(f"*Source: {name.title()} Agent | {r.source_count} sources | Confidence: {r.confidence:.0%}*\n")

    # Bittensor verification
    verification = None
    try:
        from verification.bittensor import verify_research
        verification = await verify_research(topic, parts)
        parts.append(f"\n## Decentralized Verification\n\n")
        parts.append(f"**Bittensor Score**: {verification.get('score', 'N/A')}\n")
        parts.append(f"**Confidence**: {verification.get('confidence', 'N/A')}\n")
    except Exception:
        pass

    # BasedAI governance scoring
    governance_scores = []
    try:
        from integrations.basedai import score_agent_decisions
        agent_results_dict = {name: {"findings": r.findings, "source_count": r.source_count} for name, r in results.items()}
        governance_scores = score_agent_decisions(agent_results_dict, topic)
        if governance_scores:
            avg_trust = sum(s.trust_score for s in governance_scores) / len(governance_scores)
            avg_accountability = sum(s.accountability_score for s in governance_scores) / len(governance_scores)
            parts.append(f"\n## BasedAI Governance\n\n")
            parts.append(f"**Avg Trust Score**: {avg_trust:.2f}\n")
            parts.append(f"**Avg Accountability**: {avg_accountability:.2f}\n")
            parts.append(f"**Decisions Audited**: {len(governance_scores)}\n")
    except Exception:
        pass

    # Kaspa on-chain verification
    kaspa_record = None
    try:
        from integrations.kaspa import record_research_on_kaspa
        agent_results_dict = {name: {"source_count": r.source_count} for name, r in results.items()}
        kaspa_record = record_research_on_kaspa("\n".join(parts), topic, agent_results_dict)
        if kaspa_record:
            parts.append(f"\n## Kaspa On-Chain Record\n\n")
            parts.append(f"**Report Hash**: `{kaspa_record.report_hash}`\n")
            parts.append(f"**Tx ID**: `{kaspa_record.kaspa_tx_id}`\n")
            parts.append(f"**Verified**: {'Yes' if kaspa_record.verified else 'Pending'}\n")
    except Exception:
        pass

    # CoralOS agent registration
    coral_result = None
    try:
        from integrations.coralos import register_sentinel_agents
        coral_result = register_sentinel_agents()
        if coral_result and coral_result.registrations:
            parts.append(f"\n## CoralOS Agent Registry\n\n")
            parts.append(f"**Agents Registered**: {coral_result.total_agents}\n")
            for reg in coral_result.registrations:
                parts.append(f"- {reg.agent_name}: `{reg.agent_id}` ({'verified' if reg.verified else 'pending'})\n")
    except Exception:
        pass

    return {
        "report": "\n".join(parts),
        "agents": {name: {"findings": r.findings, "source_count": r.source_count, "confidence": r.confidence, "sources": r.sources} for name, r in results.items()},
        "verification": verification,
        "governance": [{"agent": s.agent_name, "trust": s.trust_score, "accountability": s.accountability_score} for s in governance_scores],
        "kaspa": {"hash": kaspa_record.report_hash, "tx": kaspa_record.kaspa_tx_id, "verified": kaspa_record.verified} if kaspa_record else None,
        "coralos": {"agents": coral_result.total_agents, "verified": coral_result.verified_count} if coral_result else None,
    }
