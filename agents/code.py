"""Code Agent — searches GitHub repositories and code sources."""
from __future__ import annotations

import httpx
from uagents import Agent, Context

from .protocols import ResearchRequest, ResearchResult, AgentStatus

code_agent = Agent(
    name="sentinel-code",
    seed="sentinel_code_secret_2026",
    port=8003,
    endpoint=["http://localhost:8003/submit"],
)


@code_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Code Agent started: {code_agent.address}")


@code_agent.on_message(model=ResearchRequest)
async def handle_research(ctx: Context, sender: str, msg: ResearchRequest):
    ctx.logger.info(f"Received code research request: {msg.topic}")

    await ctx.send(sender, AgentStatus(
        agent_name="code", status="working",
        message=f"Searching GitHub for: {msg.topic}", progress=0.1,
    ))

    try:
        findings_parts: list[str] = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            # Search GitHub repositories
            try:
                resp = await client.get(
                    "https://api.github.com/search/repositories",
                    params={
                        "q": msg.topic,
                        "sort": "stars",
                        "order": "desc",
                        "per_page": 5,
                    },
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    repos = data.get("items", [])
                    if repos:
                        findings_parts.append("### Top Repositories")
                        for repo in repos:
                            findings_parts.append(
                                f"- **{repo.get('full_name', 'N/A')}** "
                                f"(Stars: {repo.get('stargazers_count', 0)}, "
                                f"Forks: {repo.get('forks_count', 0)})\n"
                                f"  {repo.get('description', 'No description')}\n"
                                f"  Language: {repo.get('language', 'N/A')}"
                            )
            except Exception:
                pass

            # Search GitHub code
            try:
                resp = await client.get(
                    "https://api.github.com/search/code",
                    params={"q": msg.topic, "per_page": 3},
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    code_items = data.get("items", [])
                    if code_items:
                        findings_parts.append("\n### Relevant Code Files")
                        for item in code_items[:3]:
                            repo_name = item.get("repository", {}).get("full_name", "")
                            findings_parts.append(
                                f"- `{item.get('path', '')}` in {repo_name}"
                            )
            except Exception:
                pass

        if not findings_parts:
            findings_parts.append(
                f"No specific code found for '{msg.topic}'. "
                "Try broader search terms."
            )

        findings = f"## Code Research for: {msg.topic}\n\n" + "\n".join(findings_parts)

        await ctx.send(sender, ResearchResult(
            agent_name="code",
            findings=findings,
            source_count=max(1, len(findings_parts)),
            confidence=0.6 if findings_parts else 0.1,
        ))
        ctx.logger.info("Code research complete.")
    except Exception as exc:
        ctx.logger.error(f"Code research failed: {exc}")
        await ctx.send(sender, ResearchResult(
            agent_name="code",
            findings=f"Error: {exc}",
            source_count=0,
            confidence=0.0,
        ))


if __name__ == "__main__":
    code_agent.run()
