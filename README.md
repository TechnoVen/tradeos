# TradeOS - International AI-Powered Algorithmic Trading Platform

<div align="center">

**Trade + OS = Your complete Trading Operating System**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

</div>

**TradeOS** is an open-source, AI-powered algorithmic trading platform designed for international markets. It provides a unified API layer across multiple brokers, AI-driven strategy generation, and a complete trading infrastructure — from market data to order execution.

> **Built upon [OpenAlgo](https://github.com/marketcalls/openalgo)** — the excellent open-source Indian algo trading platform by [marketcalls](https://github.com/marketcalls). TradeOS extends OpenAlgo's foundation into an international, AI-enhanced trading OS.

## What's Different from OpenAlgo?

| Feature | OpenAlgo | TradeOS |
|---------|----------|---------|
| **Markets** | Indian stocks (NSE/BSE) | Crypto, Stocks, Forex, Commodities (worldwide) |
| **Brokers** | 24+ Indian brokers | Binance (Phase 1), IBKR, Coinbase + 24 Indian brokers |
| **AI** | MCP Server | Multi-LLM (OpenAI, Anthropic, Gemini, DeepSeek, Ollama) |
| **Demo** | Analyzer mode | $100K virtual account, no signup, 30-day renewable |
| **Data** | Broker-provided | Free APIs (Finnhub, Alpha Vantage, CoinGecko) + broker data |
| **License** | AGPL v3 | AGPL v3 |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/TechnoVen/tradeos.git
cd tradeos

# Install UV package manager
pip install uv

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see .env.example for all options)

# Build the frontend
cd frontend && npm install && npm run build && cd ..

# Run the application
uv run app.py
```

The application will be available at `http://127.0.0.1:5000`

### Requirements
- **Python**: 3.12+
- **Node.js**: 20+ (for frontend build)
- **RAM**: 2GB minimum
- **Disk**: 1GB

## Core Features

### Unified REST API (`/api/v1/`)
A single, standardized API across all brokers with 30+ endpoints:
- **Order Management**: Place, modify, cancel, basket orders, smart orders
- **Portfolio**: Positions, holdings, order book, trade book, funds
- **Market Data**: Real-time quotes, historical data, market depth
- **Advanced**: Option Greeks, margin calculator, auto-split orders

### AI-Powered Trading
Multi-LLM integration for intelligent trading:
- **Strategy Generation**: Describe a strategy in natural language, get executable code
- **Market Analysis**: AI-driven market insights and risk assessment
- **MCP Server**: Connect Claude, ChatGPT, or any AI assistant for natural language trading
- **Multiple Providers**: OpenAI, Anthropic, Gemini, DeepSeek, Ollama (local)

### Demo Accounts
Try TradeOS without risking real money:
- $100,000 virtual capital
- No signup required — instant access
- 30-day sessions, renewable with email
- Full feature access including AI tools

### Real-Time WebSocket Streaming
- Unified WebSocket proxy for all brokers (port 8765)
- ZeroMQ message bus for high-performance data distribution
- Subscribe to LTP, Quote, or Market Depth for any symbol
- Automatic reconnection and failover

### Flow Visual Strategy Builder
Build strategies visually with drag-and-drop:
- Node-based editor powered by React Flow
- Pre-built nodes for data, conditions, orders, notifications
- Real-time execution with live market data
- Webhook triggers for external signals

### Python Strategy Manager
Host and run Python strategies directly:
- Built-in code editor with syntax highlighting
- Run multiple strategies in parallel
- Automated scheduling with start/stop times
- Secure environment variable management

### Analyzer Mode (Paper Trading)
- Virtual capital for risk-free testing
- Realistic margin system with leverage
- All order types supported
- Separate database for complete isolation

### Enterprise Security
- **Argon2** password hashing (PHC winner)
- **Fernet** encryption for tokens and credentials
- **TOTP** two-factor authentication
- **Rate limiting** on all endpoints
- **CSP, CORS, CSRF** protections
- **Zero data collection** — your data stays on your server

## Supported Brokers

### International (Phase 1-2)
- **Binance** — Crypto (Phase 1 MVP)
- **Interactive Brokers** — Global stocks, options, futures (Phase 2)
- **Coinbase** — Crypto (Phase 2)

### Indian Brokers (24+ — disabled by default)
<details>
<summary>View Indian brokers (set ENABLE_INDIAN_BROKERS=true in .env)</summary>

5paisa, AliceBlue, AngelOne, Compositedge, Definedge, Dhan, Firstock, Flattrade, Fyers, Groww, IBulls, IIFL, Indmoney, JainamXTS, Kotak Neo, Motilal Oswal, Mstock, Paytm Money, Pocketful, Samco, Shoonya, Tradejini, Upstox, Wisdom Capital, Zebu, Zerodha

</details>

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.0, SQLAlchemy 2.0, Flask-SocketIO |
| **Frontend** | React 19, TypeScript, Vite 7, Tailwind CSS 4, shadcn/ui |
| **Databases** | SQLite (dev), DuckDB (historical data) |
| **Real-Time** | ZeroMQ, WebSocket proxy |
| **AI** | OpenAI, Anthropic, Gemini, DeepSeek, Ollama |
| **Security** | Argon2, Fernet, TOTP, CSP, CORS |

## Supported Platforms

Connect your strategies from:
- **TradingView** — Webhook alerts for Pine Script
- **Python** — Official SDK with 100+ technical indicators
- **Amibroker** — Direct AFL integration
- **GoCharting** — Webhook integration
- **ChartInk** — Scanner webhook integration
- **MetaTrader** — MT4/MT5 compatibility
- **Excel / Google Sheets** — REST API
- **Telegram** — Real-time alerts and commands
- **N8N** — Workflow automation
- **AI Assistants** — Claude, ChatGPT via MCP Server

## Development

```bash
# Run the app (development mode)
uv run app.py

# Frontend development (hot reload)
cd frontend && npm run dev

# Run tests
uv run pytest test/ -v
cd frontend && npm test

# Build frontend for production
cd frontend && npm run build
```

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

## Roadmap

- [x] **Phase 1**: Repository setup, branding, global rename
- [ ] **Phase 1**: Demo account system ($100K virtual)
- [ ] **Phase 1**: Binance broker integration
- [ ] **Phase 1**: Free data APIs (Finnhub, Alpha Vantage)
- [ ] **Phase 1**: Basic AI integration (multi-LLM)
- [ ] **Phase 1**: Docker + production polish
- [ ] **Phase 2**: Flask -> FastAPI migration
- [ ] **Phase 2**: React -> Next.js 15 migration
- [ ] **Phase 3**: IBKR + Coinbase integration
- [ ] **Phase 4**: Advanced AI + social sentiment

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Community & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/TechnoVen/tradeos/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/TechnoVen/tradeos/discussions)

## License

TradeOS is released under the **[AGPL v3.0 License](LICENSE)**.

## Credits & Acknowledgments

### Original Project
TradeOS is built upon **[OpenAlgo](https://github.com/marketcalls/openalgo)** by [Rajandran R](https://github.com/marketcalls) and the OpenAlgo community. We are grateful for their excellent work in creating an open-source algorithmic trading platform. The original Indian broker integrations, unified API design, and plugin architecture form the foundation of TradeOS.

### Open Source Libraries
TradeOS is made possible by many outstanding open-source projects:

<details>
<summary>View all dependencies and credits</summary>

**Core**: Flask, React 19, SQLAlchemy, TypeScript, Vite, Tailwind CSS

**UI**: shadcn/ui, Radix UI, Lucide Icons, Sonner, cmdk

**Data & Charts**: TradingView Lightweight Charts, Plotly, DuckDB, React Flow

**Editors**: CodeMirror, @uiw/react-codemirror

**State & Data**: TanStack Query, Zustand, Axios, Socket.IO

**Security**: Argon2-CFFI, Cryptography (Fernet), ZeroMQ

**Testing**: Vitest, Playwright, Biome, axe-core

</details>

## Disclaimer

**This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.**

Always test strategies in Analyzer/Demo mode before live trading. Past performance does not guarantee future results. Trading involves substantial risk of loss.

---

Built with care by the TradeOS team. Making algorithmic trading accessible worldwide.
