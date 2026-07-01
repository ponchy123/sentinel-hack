"""Orchestrator Agent — receives requests, dispatches to sub-agents, aggregates results."""
from __future__ import annotations

import asyncio
import os

from uagents import Agent, Context

from .protocols import ResearchRequest, ResearchResult, AgentStatus, AggregatedResult

# Sub-agent addresses (set on startup)
ACADEMIC_ADDRESS: str | None = None
MARKET_ADDRESS: str | None = None
CODE_ADDRESS: str | None = None

# Result storage — keyed by (topic, agent_name) to track per-request
_results: dict[str, ResearchResult] = {}
_current_topic: str = ""

orchestrator = Agent(
    name="sentinel-orchestrator",
    seed="sentinel_orchestrator_secret_2026",
    port=8000,
    endpoint=["http://localhost:8000/submit"],
)


@orchestrator.on_event("startup")
async def startup(ctx: Context):
    global ACADEMIC_ADDRESS, MARKET_ADDRESS, CODE_ADDRESS
    from .academic import academic_agent
    from .market import market_agent
    from .code import code_agent

    ACADEMIC_ADDRESS = academic_agent.address
    MARKET_ADDRESS = market_agent.address
    CODE_ADDRESS = code_agent.address

    ctx.logger.info(f"Orchestrator started: {orchestrator.address}")
    ctx.logger.info(f"  Academic: {ACADEMIC_ADDRESS}")
    ctx.logger.info(f"  Market:   {MARKET_ADDRESS}")
    ctx.logger.info(f"  Code:     {CODE_ADDRESS}")


@orchestrator.on_message(model=ResearchRequest)
async def handle_research(ctx: Context, sender: str, msg: ResearchRequest):
    global _current_topic
    ctx.logger.info(f"Dispatching research: {msg.topic}")
    _results.clear()
    _current_topic = msg.topic

    targets = []
    if "academic" in msg.sources and ACADEMIC_ADDRESS:
        targets.append(ACADEMIC_ADDRESS)
    if "market" in msg.sources and MARKET_ADDRESS:
        targets.append(MARKET_ADDRESS)
    if "code" in msg.sources and CODE_ADDRESS:
        targets.append(CODE_ADDRESS)

    request = ResearchRequest(topic=msg.topic, depth=msg.depth, sources=msg.sources)
    for address in targets:
        await ctx.send(address, request)
        ctx.logger.info(f"  -> Sent to {address[:20]}...")


@orchestrator.on_message(model=ResearchResult)
async def handle_result(ctx: Context, sender: str, msg: ResearchResult):
    _results[msg.agent_name] = msg
    ctx.logger.info(
        f"Received from {msg.agent_name}: "
        f"{msg.source_count} sources, confidence={msg.confidence:.2f}"
    )

    expected = {"academic", "market", "code"}
    received = set(_results.keys())
    if expected.issubset(received):
        ctx.logger.info("All results received. Aggregating...")
        await _aggregate_and_report(ctx, _current_topic)


@orchestrator.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    ctx.logger.info(f"Status from {msg.agent_name}: {msg.status} - {msg.message}")


async def _aggregate_and_report(ctx: Context, topic: str):
    aggregated = AggregatedResult(topic=topic)
    parts: list[str] = [f"# Research Report: {topic}\n"]

    if "academic" in _results:
        r = _results["academic"]
        aggregated.academic_result = r.findings
        parts.append(f"## Academic Research\n\n{r.findings}\n")
        parts.append(f"*Source: Academic Agent | {r.source_count} sources | Confidence: {r.confidence:.0%}*\n")

    if "market" in _results:
        r = _results["market"]
        aggregated.market_result = r.findings
        parts.append(f"## Market Data\n\n{r.findings}\n")
        parts.append(f"*Source: Market Agent | {r.source_count} sources | Confidence: {r.confidence:.0%}*\n")

    if "code" in _results:
        r = _results["code"]
        aggregated.code_result = r.findings
        parts.append(f"## Code Research\n\n{r.findings}\n")
        parts.append(f"*Source: Code Agent | {r.source_count} sources | Confidence: {r.confidence:.0%}*\n")

    try:
        from verification.bittensor import verify_research
        verification = await verify_research(topic, parts)
        aggregated.verification_score = verification.get("score", 0.0)
        parts.append(f"\n## Decentralized Verification\n\n")
        parts.append(f"**Bittensor Network Score**: {verification.get('score', 'N/A')}\n")
        parts.append(f"**Confidence**: {verification.get('confidence', 'N/A')}\n")
        parts.append(f"*Verified by decentralized validators on Bittensor subnet*\n")
    except Exception as exc:
        ctx.logger.warning(f"Bittensor verification skipped: {exc}")

    aggregated.report = "\n".join(parts)
    ctx.logger.info("Report aggregation complete.")

    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "latest_report.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(aggregated.report)


def get_latest_report() -> str | None:
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "latest_report.md")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


if __name__ == "__main__":
    from .academic import academic_agent
    from .market import market_agent
    from .code import code_agent

    print("Starting Sentinel multi-agent system...")
    print("Orchestrator:    http://localhost:8000")
    print("Academic Agent:  http://localhost:8001")
    print("Market Agent:    http://localhost:8002")
    print("Code Agent:      http://localhost:8003")
    print("Press Ctrl+C to stop.\n")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run all agents concurrently
    tasks = [
        orchestrator.run(),
        academic_agent.run(),
        market_agent.run(),
        code_agent.run(),
    ]
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    except KeyboardInterrupt:
        print("\nShutting down...")
