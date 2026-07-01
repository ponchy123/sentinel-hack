"""Academic Agent — searches ArXiv and academic sources via Venice Research Engine."""
from __future__ import annotations

import asyncio

from uagents import Agent, Context

from .protocols import ResearchRequest, ResearchResult, AgentStatus

academic_agent = Agent(
    name="sentinel-academic",
    seed="sentinel_academic_secret_2026",
    port=8001,
    endpoint=["http://localhost:8001/submit"],
)

ORCHESTRATOR_ADDRESS: str | None = None


@academic_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Academic Agent started: {academic_agent.address}")


@academic_agent.on_message(model=ResearchRequest)
async def handle_research(ctx: Context, sender: str, msg: ResearchRequest):
    global ORCHESTRATOR_ADDRESS
    ORCHESTRATOR_ADDRESS = sender
    ctx.logger.info(f"Received research request: {msg.topic}")

    await ctx.send(sender, AgentStatus(
        agent_name="academic", status="working",
        message=f"Searching academic sources for: {msg.topic}", progress=0.1,
    ))

    try:
        from research.venice_client import VeniceClient
        from research.web_search import WebSearch, ArxivProvider, DuckDuckGoProvider
        from research.agent import ResearchAgent

        venice = VeniceClient.from_env()
        web = WebSearch(
            providers=[ArxivProvider(), DuckDuckGoProvider()],
            scraper=venice.scrape,
        )
        agent = ResearchAgent(venice=venice, web=web, max_sources=10)

        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(
            None,
            lambda: agent.run(msg.topic, iterations=1, query_count=3, results_per_query=3),
        )

        await ctx.send(sender, ResearchResult(
            agent_name="academic",
            findings=report.markdown,
            source_count=len(report.sources),
            confidence=min(0.9, 0.5 + len(report.sources) * 0.05),
        ))
        ctx.logger.info(f"Research complete: {len(report.sources)} sources found.")
    except Exception as exc:
        ctx.logger.error(f"Research failed: {exc}")
        await ctx.send(sender, ResearchResult(
            agent_name="academic",
            findings=f"Error: {exc}",
            source_count=0,
            confidence=0.0,
        ))


if __name__ == "__main__":
    academic_agent.run()
