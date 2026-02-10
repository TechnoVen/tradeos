# TradeOS: Comprehensive Technical Implementation Plan
## Transform OpenAlgo → International AI-Powered Trading Platform

**Context**: OpenAlgo is a production-ready algo trading platform for Indian brokers (Flask 3.1.2 + React 19 + Vite + SQLite). The goal is to fork it into TradeOS: an international, AI-powered, open-source trading OS with demo accounts, multi-LLM support, social sentiment analysis, and global broker coverage. Solo founder, $500/month budget, 3-month MVP target.

**Source Material**:
- `/home/nadir/code/TechnoVen/openalgo/docs/TRADEOS_TRANSFORMATION_PLAN.md` — Research + Q&A
- `/home/nadir/code/TechnoVen/openalgo/TradeOS Open Source + Sustainable B.txt` — Business model + final clarifications
- Current codebase: `/home/nadir/code/TechnoVen/openalgo/`

---

## Critical Decisions (Confirmed by User)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| License | AGPLv3 | True open-source, competitors must open-source forks |
| Backend | FastAPI (migrate from Flask) | Native async, built-in WebSocket, auto-docs |
| Frontend | Next.js 15 App Router (from Vite+React 19) | SSR, SEO, RSC, edge functions |
| Database | SQLite (dev) → PostgreSQL (prod) | Zero-config local, scalable prod |
| Caching | Redis 7+ | Sessions, rate limiting, ticker cache |
| Queue | RabbitMQ | Event streaming, broker data |
| Container | Docker Compose (MVP), K8s (later) | One-command setup |
| Auth | Email/Password + Google + GitHub + Magic Link + Demo (no auth) | Frictionless onboarding |
| AI | Self-hosted FinBERT + Ollama + cloud LLMs (BYO keys or our credits) | Privacy + flexibility |
| Demo | $100k virtual, instant, no signup, 30-day renewable | Zero-friction onboarding |
| Asset Priority | Crypto first → Stocks → Forex → Commodities | Fewest regulations |
| Brokers | Binance (MVP), IBKR+Coinbase (Phase 2) | Crypto first |
| Data | Binance WS (free RT) + Alpha Vantage (free historical) → Polygon.io (premium) | Budget-conscious |

---

## Current Codebase Inventory (What We're Building On)

### Backend (Flask)
- `app.py` — 41 blueprints registered, 14 DB inits, Flask-SocketIO, CSRF, rate limiting
- `blueprints/` — 41 route handlers (auth, orders, dashboard, strategy, flow, websocket, etc.)
- `restx_api/` — 44 REST endpoints with Flask-RESTX auto-docs
- `services/` — 57 business logic services (order, data, portfolio, auth, telegram, etc.)
- `database/` — 29 SQLAlchemy models across 5 SQLite DBs
- `broker/` — 29 brokers, each: `api/{auth,order,data,funds}.py` + `mapping/` + `streaming/` + `plugin.json`
- `utils/plugin_loader.py` — dynamic broker discovery at startup
- `websocket_proxy/server.py` — ZeroMQ message bus port 8765

### Frontend (Vite + React 19)
- React 19.2, React Router DOM v7, TanStack Query v5, Zustand v5
- Tailwind CSS v4, Radix UI / shadcn, Lucide icons
- lightweight-charts v5 (TradingView), Plotly.js, XYFlow
- CodeMirror (code editor), Socket.io-client v4
- Biome (lint/format), Vitest + Playwright (tests)

### Key Patterns to Preserve
1. **Broker plugin pattern**: `plugin.json` + standardized `api/` interface → keep, extend for international brokers
2. **Service layer**: Business logic in `services/` → keep, add new services
3. **API key encryption**: Fernet encryption → keep in FastAPI
4. **Symbol format**: `EXCHANGE:SYMBOL-TYPE` → extend for international (`NYSE:AAPL-EQ`, `CRYPTO:BTC/USDT`)
5. **Multi-DB isolation**: 5 separate databases → migrate to PostgreSQL schemas

---

## Repository Setup

### 1. Create TradeOS Repository

```bash
# Fork to new directory
git clone /home/nadir/code/TechnoVen/openalgo tradeos
cd tradeos
rm -rf .git
git init
git add .
git commit -m "feat: initial commit - fork from OpenAlgo v1.x"

# Create GitHub repo
gh repo create your-org/tradeos --public --source=. --push --description "International AI-Powered Trading OS"
```

### 2. Global Rename: openalgo → tradeos

Files to update (sed across all Python, JS, HTML, JSON, YAML):
- All `from openalgo import` → `from tradeos import`
- All `openalgo.db` → `tradeos.db`
- All references in README, docs, HTML templates, Python files
- Update `frontend/package.json`: `"openalgo": "file:.."` → `"tradeos": "file:.."`
- Update `pyproject.toml` project name

### 3. README Credits

```markdown
# TradeOS — International AI-Powered Trading Platform

> Built upon the excellent foundation of [OpenAlgo](https://github.com/marketcalls/openalgo)
> by Rajandran R and the MarketCalls team. Deep gratitude for pioneering
> open-source algorithmic trading in India.
```

---

## Authentication & Login Options

TradeOS supports **5 login methods** — from zero-friction demo to full OAuth. The goal is to remove every barrier between the user and their first trade.

### Login Method Matrix

| Method | Signup Required | API Keys Required | Use Case |
|--------|----------------|-------------------|----------|
| **Demo (Instant)** | No | No | Try everything right now |
| **Magic Link** | Email only | No | Passwordless, simplest signup |
| **Email + Password** | Yes | No | Traditional, self-hosted users |
| **Google OAuth** | Yes (1-click) | No | Fastest real account creation |
| **GitHub OAuth** | Yes (1-click) | No | Developer-friendly onboarding |

---

### 1. Demo Mode (No Auth — Zero Friction)

**Flow**:
```
User clicks "Try Demo" (homepage)
    ↓
GET /demo/create (no credentials)
    ↓
Server generates: demo_token = secrets.token_urlsafe(32)
    ↓
Sets cookie: tradeos_demo=<token> (30-day expiry)
    ↓
Redirects to /dashboard with $100,000 USD virtual balance
    ↓
All trades routed to Binance Testnet (paper trading)
    ↓
After 30 days: "Enter email to keep your portfolio" banner
```

**Backend** (`database/demo_db.py`):
```python
class DemoAccount(Base):
    __tablename__ = "demo_accounts"
    id             = Column(UUID, primary_key=True, default=uuid4)
    session_token  = Column(String(64), unique=True, index=True)
    virtual_balance = Column(JSONB, default={"USD": 100000})
    expires_at     = Column(DateTime)          # +30 days
    email          = Column(String(255))       # Set on renewal
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=utcnow)
```

**Upgrade path**: Demo → real account preserves all strategies, watchlists, settings.

---

### 2. Magic Link (Email Only, Passwordless)

Best for users who want a real account without a password.

**Flow**:
```
User enters email → click "Send Magic Link"
    ↓
Server generates: token = secrets.token_urlsafe(32), TTL 15 min
    ↓
Stores in Redis: magic:{token} = email (TTL 900s)
    ↓
Sends email: "Click here to login → /auth/magic?token=<token>"
    ↓
User clicks link → server validates token from Redis
    ↓
Creates/finds user by email → issues JWT session
    ↓
Redirects to /dashboard
```

**New files**:
- `services/auth/magic_link_service.py`
- `blueprints/auth.py` — add `/auth/magic-link` + `/auth/magic` routes

**Email provider**: `python-sendgrid` (free up to 100 emails/day) or `smtplib` for self-hosted.

---

### 3. Email + Password (Traditional)

Inherited from OpenAlgo. Upgraded from Argon2 → keep Argon2 (already best-in-class).

**Enhancements over OpenAlgo**:
- Remove India-specific session expiry (3:30 AM IST) → configurable `SESSION_TIMEOUT_HOURS`
- Add email verification on signup (token in Redis, TTL 24h)
- Add TOTP 2FA (already in OpenAlgo — keep)
- Add "Remember me" (30-day session vs 24h default)

**Flow**:
```
POST /auth/register  → hash password (Argon2 + pepper) → send verify email
GET  /auth/verify?token=<t> → activate account
POST /auth/login    → verify password → issue JWT → set HttpOnly cookie
POST /auth/logout   → clear cookie + blacklist token in Redis
```

---

### 4. Google OAuth (1-Click)

**Library**: `authlib` (Python, works with FastAPI + Flask)

**Flow**:
```
User clicks "Continue with Google"
    ↓
Redirect to Google: accounts.google.com/o/oauth2/auth
    Params: client_id, redirect_uri=/auth/google/callback, scope=email profile
    ↓
User approves → Google redirects to /auth/google/callback?code=xxx
    ↓
Exchange code for access_token (Google API)
    ↓
Fetch user profile: {email, name, picture, google_id}
    ↓
Upsert user: CREATE or UPDATE users SET google_id=... WHERE email=...
    ↓
Issue JWT session → redirect to /dashboard
```

**New env vars**:
```env
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
```

**Setup** (free):
1. Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client ID
2. Authorized redirect URI: `http://localhost:5000/auth/google/callback`

---

### 5. GitHub OAuth (Developer-Friendly)

**Flow** (same pattern as Google):
```
User clicks "Continue with GitHub"
    ↓
Redirect to: github.com/login/oauth/authorize?client_id=...&scope=user:email
    ↓
User approves → GitHub redirects to /auth/github/callback?code=xxx
    ↓
Exchange code → POST github.com/login/oauth/access_token
    ↓
Fetch user: GET api.github.com/user + api.github.com/user/emails
    ↓
Upsert user by email → issue JWT → redirect to /dashboard
```

**New env vars**:
```env
GITHUB_CLIENT_ID=your_github_app_client_id
GITHUB_CLIENT_SECRET=your_github_app_client_secret
```

**Setup** (free): github.com/settings/developers → OAuth Apps → New OAuth App

---

### Session Management (JWT + Redis)

**Token structure**:
```python
# JWT payload
{
    "sub": "user_uuid",
    "email": "user@example.com",
    "tier": "free",             # free | pro | enterprise
    "iat": 1707580800,          # issued at
    "exp": 1707667200,          # expires (24h default, 30d "remember me")
    "jti": "unique_token_id"    # for blacklisting on logout
}
```

**Blacklisting** (logout / password change):
```python
# Store revoked JTIs in Redis (TTL = remaining token lifetime)
await redis.setex(f"jwt:blacklist:{jti}", remaining_ttl, "1")

# On every request: check blacklist before trusting token
if await redis.exists(f"jwt:blacklist:{jti}"):
    raise HTTPException(401, "Token revoked")
```

**FastAPI dependency**:
```python
# api/dependencies/auth.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = verify_jwt(token)          # Raises 401 if invalid/expired
    check_blacklist(payload["jti"])      # Raises 401 if revoked
    return await get_user_by_id(db, payload["sub"])
```

---

### AI Configuration (BYO Keys or Managed Credits)

The AI settings panel is part of the auth'd user settings, not the login flow itself.

**Settings page** (`/settings/ai`):

```
┌─────────────────────────────────────────────────────┐
│  AI Provider Settings                               │
├────────────────┬────────────────────────────────────┤
│  Provider      │  Configuration                     │
├────────────────┼────────────────────────────────────┤
│ OpenAI         │ [○ BYO Key]  [● TradeOS Credits]  │
│                │  sk-••••••••••••••••  [Verify]     │
├────────────────┼────────────────────────────────────┤
│ Anthropic      │ [○ BYO Key]  [○ TradeOS Credits]  │
│                │  sk-ant-••••••••  [Verify]         │
├────────────────┼────────────────────────────────────┤
│ Gemini         │ [○ BYO Key]  [○ TradeOS Credits]  │
├────────────────┼────────────────────────────────────┤
│ DeepSeek       │ [○ BYO Key]  [○ TradeOS Credits]  │
├────────────────┼────────────────────────────────────┤
│ Ollama (Local) │ URL: http://localhost:11434        │
│                │ Model: llama3.2  [Test Connection] │
├────────────────┼────────────────────────────────────┤
│ FinBERT        │ [● Self-hosted port 8001]          │
│                │ Status: ● Running  [Restart]       │
└────────────────┴────────────────────────────────────┘

TradeOS Credits Balance: $12.40  [Buy Credits]
Credits cost: provider rate × 1.15 (15% convenience fee)
```

**Backend** (`api/routers/settings.py`):
```python
@router.post("/settings/ai/keys")
async def save_ai_key(
    provider: str,
    api_key: str,
    use_managed: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if use_managed:
        # Use our pooled key — bill user at cost × 1.15
        await set_ai_preference(db, user.id, provider, managed=True)
    else:
        # Encrypt with Fernet + store per-user
        encrypted = fernet.encrypt(api_key.encode())
        await upsert_api_key(db, user.id, provider, encrypted)
```

---

### Auth-Related New Files (Phase 1)

| File | Purpose |
|------|---------|
| `services/auth/magic_link_service.py` | Generate + validate magic link tokens |
| `services/auth/oauth_service.py` | Google + GitHub OAuth token exchange |
| `services/auth/jwt_service.py` | Issue, verify, blacklist JWT tokens |
| `blueprints/auth.py` | Update existing: add magic link + OAuth routes |
| `database/oauth_accounts_db.py` | `OAuthAccount` model (provider, provider_id, user_id) |
| `frontend/src/pages/login/` | Login page with all 5 options |
| `frontend/src/components/auth/` | GoogleButton, GitHubButton, MagicLinkForm |

### New `.env` Variables for Auth

```env
# Auth
JWT_SECRET=                     # Generate: secrets.token_hex(32)
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
SESSION_REMEMBER_ME_DAYS=30

# OAuth Providers (all optional — only enable what you configure)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Email (for magic links + verification)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=                  # SendGrid API key (free 100/day)
FROM_EMAIL=noreply@tradeos.io
```

---



### Week 1–2: Repository & Branding

**Tasks**:
1. Fork + rename repo (tradeos)
2. Global text replace: `openalgo` → `tradeos`
3. Update `plugin.json` field `"Plugin URI"` → `https://tradeos.io`
4. Disable Indian broker plugins by default (add `"enabled": false` to each Indian `plugin.json`, load only if `ENABLE_INDIAN_BROKERS=true` in `.env`)
5. New `.env.example` with international config (see Configuration section)
6. New `docker-compose.yml` with PostgreSQL + Redis + RabbitMQ services
7. Update `README.md` with credits, new setup instructions
8. New logo/branding (placeholder SVG → finalize later)

**Files Changed**:
- All `broker/*/plugin.json` — add `"region": "IN"` + `"enabled": false`
- `utils/plugin_loader.py` — filter by `enabled` flag
- `.env.example` → new international template
- `README.md` → full rewrite
- `frontend/src/` — update "OpenAlgo" text → "TradeOS"

---

### Week 3–4: Demo Account System

**New Files**:
- `database/demo_db.py` — DemoAccount model
- `services/demo_service.py` — create, validate, renew demo accounts
- `blueprints/demo.py` — `/demo/create`, `/demo/status`, `/demo/renew` routes
- `restx_api/demo.py` — REST endpoints

**DemoAccount Model** (SQLAlchemy):
```python
class DemoAccount(Base):
    __tablename__ = "demo_accounts"
    id = Column(UUID, primary_key=True, default=uuid4)
    session_token = Column(String(64), unique=True, index=True)
    virtual_capital = Column(Numeric(15,2), default=100000.00)
    currency = Column(String(3), default="USD")
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    email = Column(String(255), nullable=True)  # Set when user renews
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    positions = Column(JSON, default=dict)
    orders = Column(JSON, default=list)
```

**Flow**:
1. `GET /demo` → create UUID session, set cookie, redirect to dashboard
2. All paper trades go to `sandbox.db` (reuse OpenAlgo's analyzer/sandbox pattern)
3. After 30 days: show renewal banner, require email to extend
4. `POST /demo/renew` → save email, extend 30 days
5. Upgrade path: `POST /demo/upgrade` → convert to real account

---

### Week 5–6: Binance Broker Integration

**New Directory**: `broker/binance/`

**Structure** (following existing OpenAlgo pattern):
```
broker/binance/
├── plugin.json           {"Plugin Name": "binance", "region": "GLOBAL", "enabled": true}
├── api/
│   ├── auth_api.py       # API key + secret validation, HMAC signing
│   ├── order_api.py      # Place/cancel/modify orders (REST + async)
│   ├── data.py           # Quotes, depth, OHLCV
│   └── funds.py          # Account balance per asset
├── mapping/
│   ├── transform_data.py # TradeOS universal ↔ Binance format
│   └── order_data.py     # Order type mappings (LIMIT→LIMIT, MARKET→MARKET)
├── streaming/
│   ├── binance_websocket.py  # Binance WS streams
│   └── binance_adapter.py    # Normalize to TradeOS format
└── database/
    └── symbol_db.py      # Crypto symbol mapping (BTC/USDT, ETH/USDT, etc.)
```

**Universal Symbol Format** (extended):
```
CRYPTO:BTC/USDT    # Crypto pair
NYSE:AAPL-EQ       # US stock
FOREX:EUR/USD      # Forex pair
COMEX:GC-FUT       # Commodity futures
```

**Binance Testnet** for demo accounts:
- URL: `https://testnet.binance.vision`
- Free testnet funds available
- Same API as production — perfect for demo mode

---

### Week 7–8: Free Data Integration

**New Services**:
- `services/data_router.py` — routes requests to appropriate provider based on user tier
- `services/providers/finnhub.py` — Finnhub client (free real-time US via IEX)
- `services/providers/alpha_vantage.py` — Alpha Vantage client (broad coverage)
- `services/providers/binance_data.py` — Binance WebSocket (free, unlimited for crypto)

**Data Router Logic**:
```python
class DataRouter:
    async def get_quote(self, symbol: str, user_tier: str) -> Quote:
        if symbol.startswith("CRYPTO:"):
            return await self.binance.get_quote(symbol)     # Always free
        elif user_tier == "premium":
            return await self.polygon.get_quote(symbol)     # Phase 2
        else:
            return await self.finnhub.get_quote(symbol)     # Free, 15-min delay

    async def get_historical(self, symbol: str, user_tier: str) -> List[OHLCV]:
        if user_tier == "premium":
            return await self.polygon.get_historical(symbol)
        else:
            return await self.alpha_vantage.get_historical(symbol)  # 1 year free
```

**Rate Limiting** (Redis-backed):
- Free tier: 1 req/sec, 500/day
- Premium: 100 req/sec, unlimited

---

### Week 9–10: Basic AI Integration

**New Files**:
- `services/ai/llm_router.py` — Multi-LLM abstraction layer
- `services/ai/strategy_generator.py` — NL → Pine Script-like strategy
- `services/ai/risk_analyzer.py` — Portfolio risk assessment
- `blueprints/ai_assistant.py` — Chat UI endpoints
- `restx_api/ai.py` — AI REST endpoints

**LLM Router** (supports all providers from day 1):
```python
class LLMRouter:
    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "deepseek": DeepSeekProvider,
        "ollama": OllamaProvider,   # Self-hosted, no cost
    }

    async def chat(self, messages, provider="openai", model=None, user_api_key=None):
        """Routes to correct LLM. User BYO key (free) or managed key (15% markup)."""
        provider_class = self.PROVIDERS[provider]
        api_key = user_api_key or get_managed_key(provider)
        return await provider_class(api_key=api_key).chat(messages, model)
```

**Strategy Generation Flow**:
```
User NL input: "Buy BTC when RSI < 30 and MACD crosses above signal"
     ↓ GPT-4 / Claude prompt engineering
Output: Python strategy class code
     ↓ Backtesting engine (reuse OpenAlgo's existing backtesting)
Result: Equity curve, max drawdown, Sharpe ratio → show in UI
```

**AI Credit System** (for SaaS):
- User has `ai_credits` balance (pre-purchased)
- Each call deducts: tokens × provider_cost × 1.15 markup
- BYO key users: no charge, no deduction

---

### Week 11–12: Docker + Production Polish

**`docker-compose.yml`** (MVP all-in-one):
```yaml
version: '3.9'
services:
  tradeos-api:
    build: .
    ports: ["5000:5000"]
    environment:
      - DATABASE_URL=postgresql://tradeos:tradeos@postgres:5432/tradeos
      - REDIS_URL=redis://redis:6379/0
    depends_on: [postgres, redis]
  tradeos-ws:
    build: .
    command: ["python", "websocket_proxy/server.py"]
    ports: ["8765:8765"]
  postgres:
    image: postgres:16-alpine
    environment: {POSTGRES_DB: tradeos, POSTGRES_USER: tradeos, POSTGRES_PASSWORD: tradeos}
    volumes: ["postgres_data:/var/lib/postgresql/data"]
  redis:
    image: redis:7-alpine
    volumes: ["redis_data:/data"]
  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports: ["5672:5672", "15672:15672"]
volumes:
  postgres_data:
  redis_data:
```

**One-command setup**:
```bash
git clone https://github.com/your-org/tradeos.git && cd tradeos
cp .env.example .env  # Edit with your API keys
docker-compose up -d
# Visit http://localhost:5000
```

---

## Phase 2: Backend Migration Flask → FastAPI (Weeks 13–20)

### Migration Strategy: Parallel Running

Run Flask + FastAPI side-by-side. Nginx routes:
- Old routes → Flask (port 5000) during transition
- New routes → FastAPI (port 8000)
- Migrate one blueprint at a time, then cut over

**FastAPI Project Structure**:
```
tradeos/
├── api/                    # FastAPI app
│   ├── main.py             # FastAPI entry (replace app.py)
│   ├── routers/
│   │   ├── auth.py, orders.py, market_data.py
│   │   ├── portfolio.py, ai.py, demo.py, webhooks.py
│   ├── dependencies/
│   │   ├── auth.py         # FastAPI Depends() for API key auth
│   │   ├── rate_limit.py   # Redis-backed (slowapi)
│   │   └── database.py     # DB session injection
│   └── models/             # Pydantic schemas (request/response)
├── broker/                 # Unchanged (adapter pattern preserved)
├── services/               # Unchanged (business logic)
└── database/               # SQLAlchemy models (Flask + FastAPI compatible)
```

**Migration Order** (safest → riskiest):
1. Market data endpoints (read-only)
2. Portfolio/positions (read-only)
3. Order placement (needs thorough testing)
4. WebSocket (replace Flask-SocketIO → FastAPI native)
5. Auth endpoints (last — needs session migration)

---

## Phase 3: Frontend → Next.js 15 (Weeks 21–28)

### Next.js App Router Structure

```
tradeos/frontend/
├── app/
│   ├── layout.tsx          # Root layout (dark mode, auth provider)
│   ├── page.tsx            # Landing page (SSR)
│   ├── (auth)/login/page.tsx
│   ├── (app)/              # Authenticated shell
│   │   ├── layout.tsx      # Sidebar + header
│   │   ├── dashboard/page.tsx
│   │   ├── trading/page.tsx        # Charts + order placement
│   │   ├── portfolio/page.tsx      # Positions + P&L
│   │   ├── ai-agent/page.tsx       # AI chat + strategy builder
│   │   ├── sentiment/page.tsx      # Social sentiment dashboard
│   │   └── settings/page.tsx       # LLM keys, broker creds
│   └── api/[...proxy]/route.ts     # Next.js → FastAPI proxy
├── components/
│   ├── ui/                 # shadcn (keep, compatible with Next.js)
│   ├── trading/            # TradingView chart, order book
│   ├── ai/                 # AI chat, strategy builder, backtest results
│   └── sentiment/          # Fear & Greed gauge, sentiment ticker, news feed
└── lib/
    ├── api.ts              # TanStack Query + axios
    └── stores/             # Zustand (keep)
```

**Key reusable components** (from current frontend):
- `lightweight-charts` → TradingView chart component (already installed)
- `plotly.js` → Order book depth, P&L charts (already installed)
- All shadcn/Radix UI components (already installed)
- CodeMirror → strategy code editor (already installed)

---

## Phase 4: AI + Social + Market Indicators (Weeks 29–44)

### FinBERT Sentiment Microservice

Separate Docker container (heavy ML, isolated):
```
services/sentiment/
├── Dockerfile              # Python + transformers + torch (CPU)
├── main.py                 # FastAPI on port 8001
└── tasks.py                # Celery: run every 5 min per symbol
```

**Pipeline**:
```
Twitter/X + Reddit + StockTwits (Celery, 5-min interval)
    → FinBERT (self-hosted) or VADER (fast fallback)
    → Redis cache (30-min TTL)
    → GET /api/v1/sentiment/{symbol}
    → WebSocket push to frontend
```

### News Aggregation

**Free RSS Sources**: CoinTelegraph, CoinDesk, Reuters, MarketWatch, Seeking Alpha
**Processing**: RSS (15-min) → GPT-3.5-turbo summarize → PostgreSQL → WebSocket push

### Fear & Greed Index (Crypto)

**Components** (all free):
- Volatility (25%): Binance OHLCV
- Momentum (25%): BTC 30d price change
- Social (15%): FinBERT scores
- Volume (25%): Binance 24h vs 30d avg
- Dominance (10%): CoinGecko API (free)

### Advanced Indicators

**Library**: `pandas-ta` (100+ indicators, MIT, zero cost)
```python
import pandas_ta as ta
df.ta.rsi(length=14, append=True)
df.ta.macd(fast=12, slow=26, signal=9, append=True)
df.ta.ichimoku(append=True)
```

---

## Database Schema (PostgreSQL Production)

### Core Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- Argon2
    tier VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Demo Accounts (no user required)
CREATE TABLE demo_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(64) UNIQUE NOT NULL,
    virtual_balance JSONB DEFAULT '{"USD": 100000}',
    expires_at TIMESTAMPTZ NOT NULL,
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT true
);

-- Orders (universal all brokers)
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    demo_account_id UUID REFERENCES demo_accounts(id),
    broker VARCHAR(50) NOT NULL,       -- "binance", "ibkr", "demo"
    symbol VARCHAR(50) NOT NULL,       -- "CRYPTO:BTC/USDT"
    side VARCHAR(10) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    quantity NUMERIC(20,8) NOT NULL,
    price NUMERIC(20,8),
    status VARCHAR(20) DEFAULT 'pending',
    broker_order_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Strategies
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    code TEXT NOT NULL,
    natural_language TEXT,
    backtest_results JSONB,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys (encrypted with Fernet)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    service VARCHAR(50) NOT NULL,      -- "openai", "binance", "polygon"
    key_encrypted TEXT NOT NULL,
    is_managed BOOLEAN DEFAULT false,  -- true = using our managed key
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- OHLCV (TimescaleDB hypertable)
CREATE TABLE ohlcv (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    open NUMERIC(20,8), high NUMERIC(20,8),
    low NUMERIC(20,8), close NUMERIC(20,8),
    volume NUMERIC(20,8)
);
SELECT create_hypertable('ohlcv', 'time');
CREATE INDEX ON ohlcv (symbol, time DESC);
```

---

## API Endpoints

```
# Trading
POST   /api/v1/orders                    Place order (universal)
GET    /api/v1/orders                    List orders
DELETE /api/v1/orders/{id}               Cancel order
GET    /api/v1/positions                 Open positions
GET    /api/v1/portfolio                 Account summary + P&L

# Market Data
GET    /api/v1/market/quote/{symbol}     Real-time/delayed quote
GET    /api/v1/market/historical/{symbol} OHLCV data
GET    /api/v1/market/depth/{symbol}     Order book

# Demo (no auth required)
POST   /api/v1/demo/create               Create demo account
GET    /api/v1/demo/status               Check balance + expiry
POST   /api/v1/demo/renew                Extend with email
POST   /api/v1/demo/upgrade              Convert to real account

# AI
POST   /api/v1/ai/chat                   Chat with trading AI
POST   /api/v1/ai/strategy/create        NL → strategy code
POST   /api/v1/ai/strategy/backtest      Run backtest
GET    /api/v1/ai/strategies             List user strategies

# Social + News
GET    /api/v1/sentiment/{symbol}        Sentiment score + label
GET    /api/v1/news                      Latest news (paginated)
GET    /api/v1/indicators/fear-greed     Fear & Greed 0-100

# Webhooks (preserve OpenAlgo)
POST   /api/v1/webhooks/tradingview      TradingView alerts
POST   /api/v1/webhooks/custom           Generic webhooks
```

---

## Environment Configuration (.env.example)

```env
# Core
APP_KEY=                    # Generate: python -c "import secrets; print(secrets.token_hex(32))"
API_KEY_PEPPER=             # Generate same way
TRADEOS_MODE=SELF_HOSTED    # or SAAS
DATABASE_URL=sqlite:///db/tradeos.db   # or postgresql://...
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Indian brokers (disabled by default)
ENABLE_INDIAN_BROKERS=false

# Crypto Brokers
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_TESTNET=true        # Use testnet for demo accounts

# Market Data (free)
FINNHUB_API_KEY=            # Free: https://finnhub.io
ALPHA_VANTAGE_API_KEY=      # Free: https://alphavantage.co
POLYGON_API_KEY=            # Premium: https://polygon.io

# AI (BYO keys - users add their own in settings)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_AI_API_KEY=
DEEPSEEK_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# Social (optional)
TWITTER_BEARER_TOKEN=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=TradeOS/1.0

# SaaS Billing (only for hosted version)
STRIPE_SECRET_KEY=
BILLING_ENABLED=false
AI_CREDIT_MARKUP=1.15       # 15% markup on AI API costs
```

---

## Cost Breakdown (MVP, $500/month budget)

| Service | Free Option | Paid Option |
|---------|------------|-------------|
| Hosting | Local dev ($0) | DigitalOcean $6/mo droplet |
| PostgreSQL | SQLite for MVP | $15/mo managed |
| Redis | Upstash 30MB free | $10/mo |
| Binance WebSocket | Free, unlimited | — |
| Alpha Vantage | Free (5 req/min) | $50/mo |
| Finnhub | Free (60 req/min) | $49/mo |
| OpenAI (testing) | — | ~$50/mo |
| **Total Production** | — | **~$130/mo** |

Break-even: **5 paying users × $29/mo** = $145/mo

---

## Files to Create (Prioritized by Phase)

### Phase 1 MVP (Weeks 1–12)
| Week | New Files |
|------|-----------|
| 1–2 | `README.md`, `LICENSE` (AGPLv3), `.env.example`, `docker-compose.yml` |
| 3–4 | `database/demo_db.py`, `services/demo_service.py`, `blueprints/demo.py` |
| 5–6 | `broker/binance/` (entire directory with all submodules) |
| 7–8 | `services/data_router.py`, `services/providers/{finnhub,alpha_vantage,binance_data}.py` |
| 9–10 | `services/ai/{llm_router,strategy_generator,risk_analyzer}.py`, `blueprints/ai_assistant.py` |
| 11–12 | `CONTRIBUTING.md`, `scripts/migrate_from_openalgo.py` |

### Files to Modify (Phase 1)
- `utils/plugin_loader.py` — add `enabled` flag filtering
- All `broker/*/plugin.json` — add `"region": "IN"`, `"enabled": false`
- `pyproject.toml` — rename project to tradeos

---

## Security Checklist
- [ ] API keys: Fernet encryption (keep from OpenAlgo)
- [ ] Passwords: Argon2 (upgrade from bcrypt)
- [ ] TLS 1.3: nginx config
- [ ] Rate limiting: Redis-backed `slowapi`
- [ ] CORS: explicit origin whitelist
- [ ] CSP: keep OpenAlgo's `csp.py`
- [ ] Input validation: Pydantic on all FastAPI endpoints
- [ ] No raw SQL: SQLAlchemy ORM only
- [ ] Secrets scanning: `detect-secrets` pre-commit hook

---

## Verification Plan (MVP)

1. **Rename check**: No "OpenAlgo" references in UI, only "TradeOS"
2. **Indian brokers disabled**: Broker list shows only Binance when `ENABLE_INDIAN_BROKERS=false`
3. **Demo flow**: `GET /demo` → $100k balance → place paper BTC trade → see position → expires in 30 days
4. **Binance Testnet**: Connect testnet API key → place limit order → verify fill
5. **AI strategy**: Type "Buy BTC when RSI < 30" → see Python code → run backtest → see equity curve
6. **Free data**: BTC/USDT quote via Binance WS (real-time, free)
7. **Docker**: `docker-compose up` → `localhost:5000` → TradeOS dashboard loads
8. **Credits from README**: OpenAlgo credit visible in README and About page

---

