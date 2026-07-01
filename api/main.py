"""FastAPI backend for Sentinel research dashboard."""
from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(title="Sentinel API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

research_sessions: dict[str, dict] = {}
websocket_connections: dict[str, list[WebSocket]] = {}


class ResearchStartRequest(BaseModel):
    topic: str
    depth: str = "standard"
    sources: list[str] = ["academic", "market", "code"]


@app.post("/api/research")
async def start_research(req: ResearchStartRequest):
    research_id = str(uuid.uuid4())[:8]
    research_sessions[research_id] = {
        "topic": req.topic, "status": "started",
        "agents": {}, "report": None, "verification": None,
    }
    await _broadcast(research_id, {"type": "research_started", "research_id": research_id, "topic": req.topic})
    asyncio.create_task(_run_agents(research_id, req))
    return {"research_id": research_id, "topic": req.topic}


@app.get("/api/status/{research_id}")
async def get_status(research_id: str):
    if research_id not in research_sessions:
        return {"error": "Not found"}
    s = research_sessions[research_id]
    return {"research_id": research_id, "topic": s["topic"], "status": s["status"], "agents": s["agents"], "has_report": s["report"] is not None}


@app.get("/api/report/{research_id}")
async def get_report(research_id: str):
    if research_id not in research_sessions:
        return {"error": "Not found"}
    s = research_sessions[research_id]
    report = s.get("report")
    if not report:
        p = Path(__file__).parent.parent / "data" / "latest_report.md"
        if p.exists():
            report = p.read_text(encoding="utf-8")
    return {"research_id": research_id, "topic": s["topic"], "report": report, "agents": s.get("agents", {}), "verification": s.get("verification")}


@app.get("/api/export/{research_id}")
async def export_report(research_id: str):
    if research_id not in research_sessions:
        return PlainTextResponse("Not found", status_code=404)
    s = research_sessions[research_id]
    report = s.get("report", "")
    if not report:
        return PlainTextResponse("No report available", status_code=404)
    return PlainTextResponse(report, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename=sentinel-report-{research_id}.md"})


@app.websocket("/ws/{research_id}")
async def websocket_endpoint(websocket: WebSocket, research_id: str):
    await websocket.accept()
    if research_id not in websocket_connections:
        websocket_connections[research_id] = []
    websocket_connections[research_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        websocket_connections[research_id].remove(websocket)


async def _broadcast(research_id: str, message: dict):
    if research_id in websocket_connections:
        dead = []
        for ws in websocket_connections[research_id]:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            websocket_connections[research_id].remove(ws)


async def _run_agents(research_id: str, req: ResearchStartRequest):
    """Run multi-agent research engine with real-time progress."""
    research_sessions[research_id]["status"] = "running"
    await _broadcast(research_id, {"type": "status_update", "status": "running"})

    async def on_progress(agent: str, status: str, message: str, progress: float):
        research_sessions[research_id]["agents"][agent] = {"status": status, "message": message, "progress": progress}
        await _broadcast(research_id, {"type": "agent_status", "agent": agent, "status": status, "message": message, "progress": progress})

    try:
        from agents.engine import run_research
        result = await run_research(req.topic, req.sources, progress=on_progress)

        report_text = result["report"]
        research_sessions[research_id]["report"] = report_text
        research_sessions[research_id]["agents"] = result["agents"]
        research_sessions[research_id]["verification"] = result["verification"]
        research_sessions[research_id]["status"] = "completed"

        # Save to file
        report_dir = Path(__file__).parent.parent / "data"
        report_dir.mkdir(exist_ok=True)
        (report_dir / f"report-{research_id}.md").write_text(report_text, encoding="utf-8")
        (report_dir / "latest_report.md").write_text(report_text, encoding="utf-8")

        await _broadcast(research_id, {
            "type": "research_complete", "research_id": research_id,
            "report": report_text, "agents": result["agents"],
            "verification": result["verification"],
        })
    except Exception as exc:
        research_sessions[research_id]["status"] = "error"
        await _broadcast(research_id, {"type": "research_error", "error": str(exc)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
