# Sentinel — Privacy-First Multi-Agent Research Network

> A multi-agent research system where specialized AI agents collaborate autonomously
> to produce cited reports, with all LLM inference routed through Venice.ai's
> zero-data-retention infrastructure and results verified on Bittensor.

## Architecture

```
User → Dashboard → FastAPI → Multi-Agent Engine
                                  ├── Academic Agent (ArXiv + DuckDuckGo)
                                  ├── Market Agent (CoinGecko)
                                  └── Code Agent (GitHub)
                                      ↓
                              Venice.ai Privacy Layer
                              (zero data retention)
                                      ↓
                              Bittensor Verification
                              (decentralized scoring)
                                      ↓
                              Cited Markdown Report
                              (downloadable)
```

## Quick Start

### Option 1: One-click (recommended)
```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh && ./start.sh
```

### Option 2: Docker
```bash
docker-compose up
```

### Option 3: Manual
```bash
# 1. Get Venice.ai API Key (free, no credit card)
#    Sign up → Settings → API → Generate Key

# 2. Setup
cp .env.example .env
# Edit .env and add VENICE_API_KEY

pip install -r requirements.txt

# 3. Start API
python -m api.main

# 4. Start Dashboard
cd dashboard && npm install && npm run dev
```

### 5. Use
Open http://localhost:3000, enter a topic, click "Start Research".

## Features

- **Multi-Agent Collaboration**: 3 specialist agents (Academic, Market, Code) work in parallel
- **Privacy-First**: All LLM calls through Venice.ai with zero data retention
- **Real Data Sources**: ArXiv papers, CoinGecko market data, GitHub repositories
- **Decentralized Verification**: Bittensor network scores research quality
- **Real-time Dashboard**: Live agent status, progress logs, source quality metrics
- **Report Export**: Download research reports as Markdown

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/research` | Start a research session |
| GET | `/api/status/{id}` | Get research status |
| GET | `/api/report/{id}` | Get final report + source quality |
| GET | `/api/export/{id}` | Download report as Markdown |
| WS | `/ws/{id}` | Real-time agent updates |

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent Engine | Fetch.ai uAgents + custom engine | Multi-agent orchestration |
| Privacy Layer | Venice.ai API | Zero data retention LLM |
| Verification | Bittensor SN44 | Decentralized quality scoring |
| Backend | FastAPI + WebSocket | Real-time API |
| Frontend | React + Vite | Research dashboard |
| Search | ArXiv + DuckDuckGo + CoinGecko + GitHub | Multi-source research |

## Project Structure

```
sentinel-hack/
├── agents/
│   ├── engine.py        # Multi-agent research engine (core)
│   ├── orchestrator.py  # Fetch.ai uAgent orchestrator
│   ├── academic.py      # Academic specialist agent
│   ├── market.py        # Market specialist agent
│   └── code.py          # Code specialist agent
├── research/
│   ├── models.py        # Data models
│   ├── venice_client.py # Venice.ai API client
│   ├── web_search.py    # Search providers
│   └── agent.py         # Research agent logic
├── api/
│   └── main.py          # FastAPI backend
├── dashboard/
│   └── src/             # React frontend
├── verification/
│   └── bittensor.py     # Bittensor verification
├── Dockerfile
├── docker-compose.yml
├── start.bat / start.sh
└── README.md
```

## Sponsors Integrated

- **Fetch.ai** — uAgents framework for multi-agent communication
- **Venice.ai** — Privacy-preserving LLM API (zero data retention)
- **Bittensor** — Decentralized verification of research quality
- **Microsoft** — Azure OpenAI (available as LLM backbone)

## License

MIT
