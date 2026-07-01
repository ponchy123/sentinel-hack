# Sentinel — Privacy-First Multi-Agent Research Network

> A multi-agent research system where specialized AI agents collaborate autonomously
> to produce cited reports, with all LLM inference routed through privacy-preserving
> infrastructure and results verified across multiple blockchain networks.

## Architecture

```
User → Dashboard → FastAPI → Multi-Agent Engine
                                  ├── Academic Agent (ArXiv + DuckDuckGo)
                                  ├── Market Agent (CoinGecko)
                                  └── Code Agent (GitHub)
                                      ↓
                              Venice.ai / Agnes AI Privacy Layer
                              (zero data retention)
                                      ↓
                              Multi-Chain Verification
                              ├── Bittensor (decentralized scoring)
                              ├── Kaspa (blockDAG record)
                              ├── Ethereum (on-chain hash)
                              └── CoralOS (Solana agent registry)
                                      ↓
                              BasedAI Governance Scoring
                                      ↓
                              Cited Markdown Report (downloadable)
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
cp .env.example .env
# Edit .env and add your API key

pip install -r requirements.txt

python -m api.main  # API at http://localhost:8080

cd dashboard && npm install && npm run dev  # Dashboard at http://localhost:3000
```

## Features

- **Multi-Agent Collaboration**: 3 specialist agents work in parallel
- **Privacy-First**: All LLM calls through zero-data-retention API
- **Real Data Sources**: ArXiv, CoinGecko, GitHub
- **Multi-Chain Verification**: Bittensor + Kaspa + Ethereum + CoralOS
- **Governance Scoring**: BasedAI trust and accountability metrics
- **Real-time Dashboard**: Live agent status, progress logs, source quality
- **Report Export**: Download as Markdown

## Bounty Integrations

| Sponsor | Integration | What It Does |
|---------|------------|--------------|
| **Fetch.ai** | uAgents framework | Multi-agent orchestration and communication |
| **Venice.ai** | Privacy LLM API | Zero data retention for all research queries |
| **Bittensor** | SN44 verification | Decentralized quality scoring of research |
| **Conduct AI** | Title sponsor | Enterprise multi-agent orchestration pattern |
| **BasedAI** | Governance layer | Trust scores and accountability audit trail |
| **Kaspa** | BlockDAG record | Research hash recorded on Kaspa chain |
| **CoralOS** | Solana registry | Agent identities registered on Coral Protocol |
| **GCC & ETH** | Ethereum record | Research hash stored on Ethereum network |

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent Engine | Fetch.ai uAgents | Multi-agent orchestration |
| LLM | Agnes AI / Venice.ai | Privacy-preserving inference |
| Governance | BasedAI | Decision scoring and audit |
| Chains | Kaspa + Ethereum + Solana | Multi-chain verification |
| Backend | FastAPI + WebSocket | Real-time API |
| Frontend | React + Vite | Research dashboard |

## Project Structure

```
sentinel-hack/
├── agents/              # Multi-agent system
│   ├── engine.py        # Core research engine
│   ├── orchestrator.py  # Fetch.ai uAgent orchestrator
│   ├── academic.py      # Academic specialist
│   ├── market.py        # Market specialist
│   └── code.py          # Code specialist
├── research/            # Research logic
│   ├── models.py        # Data models
│   ├── venice_client.py # LLM API client
│   ├── web_search.py    # Search providers
│   └── agent.py         # Research agent
├── integrations/        # Sponsor integrations
│   ├── basedai.py       # Governance scoring
│   ├── kaspa.py         # Kaspa on-chain
│   ├── coralos.py       # Solana agent registry
│   └── eth.py           # Ethereum on-chain
├── verification/
│   └── bittensor.py     # Bittensor verification
├── api/                 # FastAPI backend
├── dashboard/           # React frontend
├── demo/                # Demo video + logo
├── Dockerfile
├── docker-compose.yml
└── start.bat / start.sh
```

## Demo

- **Video**: https://youtu.be/YupSyEpONgg
- **GitHub**: https://github.com/ponchy123/sentinel-hack

## License

MIT
