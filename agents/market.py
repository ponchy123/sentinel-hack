"""Market Agent — searches financial/market data sources."""
from __future__ import annotations

import httpx
from uagents import Agent, Context

from .protocols import ResearchRequest, ResearchResult, AgentStatus

market_agent = Agent(
    name="sentinel-market",
    seed="sentinel_market_secret_2026",
    port=8002,
    endpoint=["http://localhost:8002/submit"],
)


@market_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Market Agent started: {market_agent.address}")


@market_agent.on_message(model=ResearchRequest)
async def handle_research(ctx: Context, sender: str, msg: ResearchRequest):
    ctx.logger.info(f"Received market research request: {msg.topic}")

    await ctx.send(sender, AgentStatus(
        agent_name="market", status="working",
        message=f"Searching market data for: {msg.topic}", progress=0.1,
    ))

    try:
        findings_parts: list[str] = []

        # Search CoinGecko for crypto market data
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(
                    "https://api.coingecko.com/api/v3/search",
                    params={"query": msg.topic},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    coins = data.get("coins", [])[:5]
                    for coin in coins:
                        findings_parts.append(
                            f"- {coin.get('name', 'N/A')} ({coin.get('symbol', 'N/A')}): "
                            f"Market Cap Rank #{coin.get('market_cap_rank', 'N/A')}"
                        )
            except Exception:
                pass

            # Search for trending
            try:
                resp = await client.get("https://api.coingecko.com/api/v3/search/trending")
                if resp.status_code == 200:
                    data = resp.json()
                    trending = data.get("coins", [])[:3]
                    if trending:
                        findings_parts.append("\n### Trending Coins")
                        for item in trending:
                            coin = item.get("item", {})
                            findings_parts.append(
                                f"- {coin.get('name', 'N/A')} "
                                f"(Score: {coin.get('score', 'N/A')})"
                            )
            except Exception:
                pass

        if not findings_parts:
            findings_parts.append(
                f"No specific market data found for '{msg.topic}'. "
                "Consider searching on CoinGecko or CoinCap directly."
            )

        findings = f"## Market Data for: {msg.topic}\n\n" + "\n".join(findings_parts)

        await ctx.send(sender, ResearchResult(
            agent_name="market",
            findings=findings,
            source_count=max(1, len(findings_parts)),
            confidence=0.6 if findings_parts else 0.1,
        ))
        ctx.logger.info("Market research complete.")
    except Exception as exc:
        ctx.logger.error(f"Market research failed: {exc}")
        await ctx.send(sender, ResearchResult(
            agent_name="market",
            findings=f"Error: {exc}",
            source_count=0,
            confidence=0.0,
        ))


if __name__ == "__main__":
    market_agent.run()
