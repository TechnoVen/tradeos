# OpenAlgo Codebase - Complete Analysis

## Context

This document provides a comprehensive analysis of the OpenAlgo codebase, covering every major component, directory structure, architectural pattern, and integration system. This analysis serves as the authoritative reference for understanding the complete project architecture.

---

## Executive Summary

**OpenAlgo** is a production-ready algorithmic trading platform built with:
- **Backend**: Flask 3.1.2 + Flask-RESTX (Python 3.12+)
- **Frontend**: React 19 + TypeScript + Vite
- **Database**: SQLAlchemy with 5 separate SQLite/DuckDB databases
- **Broker Support**: 29 Indian brokers via plugin architecture
- **Real-Time**: WebSocket proxy (port 8765) + Flask-SocketIO
- **Package Management**: UV (required - never use global Python)

**Key Statistics:**
- 500+ Python files
- 41 Flask blueprints
- 44+ REST API endpoints
- 57 service modules
- 29 database modules
- 29 broker integrations
- 5 separate databases
- 100+ documentation pages

---

## 1. Project Structure Overview

```
openalgo/
├── app.py                     # Main Flask application entry point (35KB)
├── pyproject.toml             # Python dependencies (155+ packages)
├── .env / .sample.env         # Environment configuration
│
├── blueprints/                # 41 Flask route handlers (UI endpoints)
├── restx_api/                 # 44 REST API endpoints (/api/v1/*)
├── services/                  # 57 business logic services
├── database/                  # 29 database models & utilities
├── broker/                    # 29 broker integrations (plugin-based)
├── utils/                     # 22 utility modules
├── websocket_proxy/           # WebSocket streaming server (port 8765)
│
├── frontend/                  # React 19 SPA with TypeScript
│   ├── src/                   # Source code
│   ├── dist/                  # Built artifacts (gitignored, CI/CD builds)
│   ├── e2e/                   # End-to-end tests
│   └── package.json           # Node.js dependencies
│
├── db/                        # Runtime SQLite databases
│   ├── openalgo.db            # Main database
│   ├── logs.db                # API/traffic logs
│   ├── latency.db             # Latency metrics
│   ├── sandbox.db             # Paper trading
│   └── historify.duckdb       # Historical data (DuckDB)
│
├── docs/                      # 100+ documentation files
├── test/                      # Test suite
├── strategies/                # Trading strategy examples
├── examples/                  # API usage examples (Python, Node.js, Go)
└── collections/               # Postman/API collections
```

---

## 2. Core Application Architecture

### Application Initialization Flow (app.py)

```
1. load_and_check_env_variables()
   └── Validates 50+ environment variables

2. create_app()
   ├── Initialize Flask with security middleware
   ├── Configure CORS, CSRF, CSP policies
   ├── Register 41 blueprints
   ├── Register REST API (Flask-RESTX)
   └── Configure rate limiting

3. setup_environment(app)
   ├── Parallel database initialization (15 databases, ThreadPoolExecutor)
   ├── Cache restoration from persistent storage
   ├── Scheduler initialization (strategies, flows, historify)
   └── WebSocket proxy server startup

4. socketio.run(app)
   └── Start Flask-SocketIO server with hot reload
```

### Request Flow Architecture

```
HTTP Request
    ↓
[WSGI Middleware]
    ├── TrafficLoggerMiddleware → logs all requests
    └── SecurityMiddleware → IP ban checking
    ↓
[Flask Request Context]
    ├── @before_request → session validation
    └── CSRFProtect → CSRF token validation (except /api/v1/*)
    ↓
[Route Matching]
    ├── Blueprints (UI routes)
    └── REST API (/api/v1/*)
    ↓
[Authentication]
    ├── Web UI: Flask-Login session
    └── REST API: API key verification
    ↓
[Service Layer]
    ├── Business logic execution
    ├── Dynamic broker module import
    ├── Broker API call (HTTPX client)
    └── Parallel background tasks:
        ├── Analyzer logging
        ├── API logging
        ├── SocketIO event emission
        └── Telegram alerts
    ↓
[Response]
    └── JSON response with standard format:
        {
          "status": "success" | "error",
          "message": "...",
          "data": {...}
        }
```

---

## 3. Blueprint Layer (41 UI Routes)

Located in `/blueprints/`

### Core Authentication
- `auth.py` - Login, registration, password reset, CSRF tokens
- `apikey.py` - API key management
- `brlogin.py` - OAuth broker callback handling
- `broker_credentials.py` - Broker credential management
- `security.py` - IP management, security settings

### Dashboard & Trading
- `dashboard.py` - Main trading dashboard
- `orders.py` - Order management UI
- `analyzer.py` - Paper trading mode
- `sandbox.py` - Sandbox environment
- `search.py` - Symbol search interface

### Advanced Features
- `flow.py` - Workflow execution system (graph-based automation)
- `strategy.py` - Strategy management & webhooks
- `python_strategy.py` - Python strategy scheduler
- `chartink.py` - TradingView integration
- `telegram.py` - Telegram bot interface

### Analysis Tools
- `gex.py` - Gamma exposure analysis
- `ivsmile.py` - IV smile charts
- `ivchart.py` - Implied volatility analysis
- `oitracker.py` - Open interest tracking
- `oiprofile.py` - OI profile visualization
- `straddle_chart.py` - Straddle strategy analysis
- `vol_surface.py` - Volatility surface 3D visualization
- `pnltracker.py` - P&L tracking dashboard

### System Management
- `admin.py` - Admin panel
- `settings.py` - Application settings
- `health.py` - Health check endpoints
- `latency.py` - Latency monitoring dashboard
- `traffic.py` - Traffic analytics
- `logging.py` - Log viewer
- `log.py` - Log management
- `master_contract_status.py` - Symbol sync status

### Frontend Integration
- `react_app.py` - Serves React SPA from `/frontend/dist/`

---

## 4. REST API Layer (44+ Endpoints)

Located in `/restx_api/`, accessible at `/api/v1/`

### Order Management
- `/placeorder` - Submit new order
- `/placesmartorder` - Auto price-type conversion
- `/modifyorder` - Modify pending order
- `/cancelorder` - Cancel single order
- `/cancelallorder` - Cancel all orders for symbol
- `/splitorder` - Split order into multiple lots
- `/basketorder` - Multi-leg basket execution
- `/optionsorder` - Options-specific orders
- `/optionsmultiorder` - Batch options orders
- `/closeposition` - Close position (opposite order)
- `/orderstatus` - Check order status

### Portfolio Management
- `/orderbook` - Open/filled orders
- `/tradebook` - Executed trades
- `/positionbook` - Open positions
- `/holdings` - Long-term holdings
- `/funds` - Account balance & margins
- `/openposition` - All open positions

### Market Data
- `/quotes` - Single symbol quote (LTP, bid/ask, volume)
- `/multiquotes` - Batch quotes (up to 100 symbols)
- `/depth` - Order book depth (5-20 levels)
- `/history` - Historical OHLC data
- `/optionchain` - Options chain data
- `/ticker` - Real-time ticker WebSocket

### Symbol Services
- `/symbol` - Symbol search
- `/search` - Advanced symbol search
- `/optionsymbol` - Options symbol lookup
- `/instruments` - All instruments list
- `/intervals` - Supported timeframes
- `/expiry` - Options expiry dates

### Advanced Features
- `/optiongreeks` - Single option Greeks
- `/multioptiongreeks` - Batch Greeks calculation
- `/syntheticfuture` - Synthetic future calculations
- `/pnl` - Symbol-wise P&L
- `/analyzer` - Paper trading operations
- `/chart` - Chart data for UI

### System
- `/ping` - Connectivity check
- `/telegram` - Telegram bot management

**API Authentication:**
- API key in request body: `{"apikey": "...", ...}`
- Or in headers: `X-API-KEY: ...`
- Keys hashed with Fernet encryption (pepper-based)

**Rate Limiting:**
- Orders: 10 per second
- Other APIs: 10 per second
- Login: 5 per minute, 25 per hour
- 429 response on rate limit exceeded

---

## 5. Service Layer (57 Business Logic Services)

Located in `/services/`

### Standard Service Pattern
```python
def operation_service(api_key, data, broker=None, emit_event=True):
    # 1. Schema validation
    validated_data = schema.load(data)

    # 2. API key verification
    user_id = verify_api_key(api_key)

    # 3. Get broker auth token
    auth_token = get_auth_token(user_id, broker)

    # 4. Dynamic broker import
    broker_module = importlib.import_module(f"broker.{broker}.api.order_api")

    # 5. Broker API call
    response = broker_module.place_order(validated_data, auth_token)

    # 6. Parallel background tasks (non-blocking)
    executor.submit(log_to_analyzer_db, data)
    executor.submit(log_to_apilog_db, data)
    socketio.start_background_task(emit_socketio_event, data)
    executor.submit(send_telegram_alert, data)

    # 7. Return response
    return (success, response_data, http_status_code)
```

### Key Services
- **Order Services**: place, modify, cancel, close position, basket, split
- **Data Services**: quotes, depth, history, option chain, Greeks
- **Account Services**: funds, holdings, margin, positions, trades
- **Analysis Services**: analyzer, GEX, IV, OI, straddle, vol surface
- **Integration Services**: flow executor, telegram bot, chartink
- **Scheduled Services**: historify scheduler, flow scheduler, strategy scheduler

---

## 6. Database Architecture (5 Separate Databases)

Located in `/database/`, database files in `/db/`

### 1. Main Database (openalgo.db)
**Modules:** `auth_db.py`, `user_db.py`, `settings_db.py`
- `User` - User accounts (username, email, password_hash, totp_secret)
- `Auth` - Broker auth tokens (encrypted with Fernet)
- `api_keys` - API keys (hashed with pepper)
- `order_modes` - Auto/semi-auto mode per user
- `Settings` - Application settings
- TTL cache: 30-60 seconds for frequent queries

### 2. Logs Database (logs.db)
**Modules:** `traffic_db.py`, `apilog_db.py`
- `TrafficLog` - HTTP requests (IP, method, path, status, duration_ms)
- `Error404Tracker` - 404 tracking for security
- `IPBan` - IP ban list
- `OrderLog` - API request/response logs (JSON serialized)
- Asynchronous logging via ThreadPoolExecutor

### 3. Latency Database (latency.db)
**Modules:** `latency_db.py`
- `LatencyLog` - API response times
- Tracks p50, p90, p99 percentiles
- Monitoring dashboard at `/latency`

### 4. Sandbox Database (sandbox.db)
**Modules:** `sandbox_db.py`, `analyzer_db.py`
- `SandboxOrders` - Virtual orders
- `SandboxTrades` - Virtual executions
- `SandboxPositions` - Virtual positions
- `SandboxHoldings` - Virtual holdings
- `SandboxPnL` - Daily P&L tracking
- ₹1 Crore virtual capital per user
- Realistic margin system with leverage
- Auto square-off at market close

### 5. Historical Data (historify.duckdb)
**Modules:** `historify_db.py`
- DuckDB for efficient OLAP queries
- Stores OHLC data for multiple timeframes
- Background scheduler for data syncing

### Additional Database Modules
- `action_center_db.py` - Semi-auto order approval queue
- `strategy_db.py` - Trading strategies
- `flow_db.py` - Workflow definitions
- `chartink_db.py` - TradingView alerts cache
- `telegram_db.py` - Telegram bot configuration
- `health_db.py` - System health metrics
- `symbol.py` - Master contract cache (100K+ symbols)
- `market_calendar_db.py` - Trading hours & holidays
- `token_db_enhanced.py` - Symbol resolution cache (TTL: 1 hour)
- `chart_prefs_db.py` - User chart preferences
- `qty_freeze_db.py` - Quantity restrictions

---

## 7. Broker Integration System (29 Brokers)

Located in `/broker/`

### Complete Broker List
1. Zerodha
2. Dhan
3. Dhan Sandbox
4. Angel One
5. Fyers
6. Shoonya
7. Upstox
8. AliceBlue
9. IIFL
10. Kotak
11. Firstock
12. Samco
13. Mstock
14. Paytm Money
15. 5Paisa
16. 5Paisa XTS
17. Groww
18. Nubra
19. Compositedge
20. TradeJini
21. Wisdom
22. Zebu
23. Motilal Oswal
24. IndMoney
25. JainaNXTS
26. iBulls
27. FlatTrade
28. Definedge
29. Pocketful

### Standardized Broker Structure

```
broker/{broker_name}/
├── plugin.json               # Metadata (name, version, auth_type)
│
├── api/
│   ├── auth_api.py           # authenticate_broker(request_token)
│   ├── order_api.py          # place/modify/cancel/status orders
│   ├── data.py               # quotes, depth, historical data
│   ├── funds.py              # balance, margin, holdings
│   └── margin_api.py         # margin calculations
│
├── mapping/
│   ├── transform_data.py     # OpenAlgo → Broker format
│   ├── order_data.py         # Broker → OpenAlgo order mapping
│   └── margin_data.py        # Broker → OpenAlgo margin mapping
│
├── database/
│   └── master_contract_db.py # Symbol token database (100K+ symbols)
│
└── streaming/
    ├── {broker}_adapter.py   # WebSocket adapter (BaseBrokerWebSocketAdapter)
    ├── {broker}_mapping.py   # Symbol & depth mapping
    └── {broker}_websocket.py # Low-level WebSocket client
```

### Plugin Loading System
**Location:** `/utils/plugin_loader.py`

```python
# Dynamic discovery at startup
def load_broker_auth_functions():
    for broker_dir in os.listdir("broker/"):
        try:
            module = importlib.import_module(f"broker.{broker_dir}.api.auth_api")
            auth_func = getattr(module, "authenticate_broker")
            registry[broker_dir] = auth_func
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load broker {broker_dir}: {e}")
```

**Key Features:**
- Auto-discovery: No manual registration needed
- Graceful failures: Invalid brokers logged but don't crash app
- Extensible: Drop new broker directory and restart

### Symbol Mapping System

**3-Tier Resolution:**
```
User Input: "SBIN"
    ↓
[Database Query: SymToken.query.filter_by(symbol="SBIN", exchange="NSE")]
    ↓
Symbol Record: {
    symbol: "SBIN",
    brsymbol: "SBIN-EQ",  # Broker-specific
    token: "408065",       # For WebSocket
    exchange: "NSE",
    brexchange: "NSE",     # Broker exchange code
    lotsize: 1,
    tick_size: 0.05
}
    ↓
Broker API Call: Uses brsymbol & brexchange
```

**Symbol Cache:**
- **Module:** `database/token_db_enhanced.py`
- **TTL:** 3600 seconds (1 hour)
- **Capacity:** 100,000+ symbols in memory
- **Lookup:** O(1) dictionary access
- **Bulk Operations:** `get_tokens_bulk()` for batch queries

### Master Contract Download

**Smart Download Logic:**
- Never re-download if already done today after 8 AM IST
- Downloads on first broker login
- Async thread prevents blocking UI
- Updates `master_contract_status_db` (success/error tracking)
- Triggers sandbox catch-up after download
- Loads symbols into memory cache

**Database Structure:**
```python
class SymToken(Base):
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)         # SBIN
    brsymbol = Column(String, index=True)       # SBIN-EQ
    name = Column(String)                       # STATE BANK OF INDIA
    exchange = Column(String, index=True)       # NSE
    brexchange = Column(String, index=True)     # NSE
    token = Column(String, index=True)          # 408065
    expiry = Column(String)                     # For derivatives
    strike = Column(Float)                      # For options
    lotsize = Column(Integer)                   # Contract size
    instrumenttype = Column(String)             # EQ, FUT, OPT
    tick_size = Column(Float)                   # 0.05
```

---

## 8. WebSocket Architecture

### Dual WebSocket System

**1. Flask-SocketIO (Port 5000)**
- **Purpose:** Real-time UI updates
- **Events:** Order updates, position changes, P&L, logs, health status
- **Pattern:** Server-initiated broadcasts to connected clients
- **Integration:** `socketio.start_background_task()` for non-blocking emits

**2. WebSocket Proxy (Port 8765)**
- **Purpose:** Unified market data streaming
- **Protocol:** Custom WebSocket protocol + ZeroMQ message bus
- **Location:** `/websocket_proxy/`

### WebSocket Proxy Architecture

```
React Frontend / Trading Strategies
    ↓ (WebSocket connection to port 8765)
[WebSocket Proxy Server] (websocket_proxy/server.py)
    ├── Client connection management
    ├── Per-client subscription tracking
    ├── Subscription index: {symbol, exchange, mode} → set(client_ids)
    └── Message throttling (50ms minimum between updates)
    ↓ (ZeroMQ SUB socket on port 5555)
[ZeroMQ Message Bus]
    ↓ (ZeroMQ PUB socket)
[Broker Adapter Pool]
    ├── Connection 1: Zerodha WebSocket (symbols 1-1000)
    ├── Connection 2: Zerodha WebSocket (symbols 1001-2000)
    └── Connection N: (auto-created when limit exceeded)
    ↓
[Broker WebSocket]
    └── Real-time market data from broker
```

### Connection Pooling

**Configuration:**
- `MAX_SYMBOLS_PER_WEBSOCKET`: 1000 (configurable)
- `MAX_WEBSOCKET_CONNECTIONS`: 3 (configurable)
- **Total capacity**: 3000 symbols per user

**Automatic Scaling:**
- Connection 1 created on first subscription
- Connection 2 created when 1000 symbols reached
- Connection 3 created when 2000 symbols reached
- All connections share single ZeroMQ publisher

**Module:** `websocket_proxy/connection_manager.py`

### Broker WebSocket Adapters

**Base Class:** `websocket_proxy/base_adapter.py` - `BaseBrokerWebSocketAdapter`

**Core Methods:**
```python
initialize(broker_name, user_id, auth_data)
    # Connect to broker, validate credentials

connect()
    # Establish WebSocket, start heartbeat

subscribe(symbols, exchange, mode)
    # Subscribe to market data
    # mode: 1=LTP, 2=QUOTE, 3=DEPTH

unsubscribe(symbols, exchange)
    # Unsubscribe from symbols

publish_to_zmq(topic, data)
    # Normalize & publish to ZeroMQ

disconnect()
    # Graceful shutdown
```

**Broker-Specific Adapters:**

**Zerodha** (`broker/zerodha/streaming/zerodha_adapter.py`)
- Mode 1: LTP only
- Mode 2: Quote (LTP, bid/ask, volume)
- Mode 3: Full depth (market depth, OI)
- Batch subscription: 500ms batching window
- Topic format: `{mode}:{token}:{exchange}`

**Dhan** (`broker/dhan/streaming/dhan_adapter.py`)
- Dual-depth support: 5-level and 20-level
- Separate WebSocket connections for each depth
- Depth accumulator for 20-level updates
- Fallback to 5-level if 20-level unavailable

**Angel One** (`broker/angel/streaming/angel_adapter.py`)
- SmartWebSocketV2 protocol
- Feed token required (separate from auth token)
- Exponential backoff reconnection (max 60s)
- Thread cleanup to prevent fd leaks

**Fyers, Shoonya, Others:**
- Follow standardized adapter pattern
- Broker-specific authentication & subscription formats
- Normalized output to OpenAlgo format

### Market Data Normalization

**Raw Broker Data (Zerodha):**
```python
{
    "token": 408065,
    "last_price": 320.50,
    "bid": 320.40,
    "ask": 320.60,
    "volume": 100000,
    "oi": 5000000
}
```

**Normalized to OpenAlgo (Published to ZMQ):**
```json
{
    "symbol": "SBIN",
    "exchange": "NSE",
    "ltp": 320.50,
    "bid": 320.40,
    "ask": 320.60,
    "volume": 100000,
    "timestamp": "2024-02-09T15:30:45.123Z"
}
```

**Normalization Module:** `websocket_proxy/mapping.py`

---

## 9. Authentication & Authorization

### Web Session Authentication

**Flow:**
```
1. User submits username/password
   ↓
2. Query User table (user_db.py)
   ↓
3. Verify password: check_password() (Argon2 + pepper)
   ↓
4. Generate TOTP secret (if first login)
   ↓
5. Set session["user"] = username
   ↓
6. Session expiry: 3:30 AM IST (next day)
   ↓
7. Redirect to /dashboard
```

**Security Features:**
- Argon2 password hashing with pepper (32+ character `API_KEY_PEPPER`)
- TOTP 2FA support via pyotp
- Session validation in `@before_request` handler
- Auto-logout at market close (3:30 AM IST)
- HttpOnly, Secure, SameSite=Lax cookies

### Broker OAuth Authentication

**Flow:**
```
1. User clicks "Login with {Broker}"
   ↓
2. Redirect to broker OAuth page
   ↓
3. User authorizes OpenAlgo
   ↓
4. Broker redirects to /auth/broker/{broker}/callback?code=xxx
   ↓
5. Exchange code for access_token (broker.{broker}.api.auth_api)
   ↓
6. Encrypt & store in auth table (Fernet encryption)
   ↓
7. Set session["AUTH_TOKEN"], session["FEED_TOKEN"]
   ↓
8. Trigger async master contract download
   ↓
9. Redirect to /dashboard
```

**Example: Zerodha OAuth**
```python
def authenticate_broker(request_token):
    checksum = sha256(f"{api_key}{request_token}{api_secret}".encode()).hexdigest()
    response = httpx.post("https://api.kite.trade/session/token", {
        "api_key": api_key,
        "request_token": request_token,
        "checksum": checksum
    })
    return response.json()["data"]["access_token"]
```

### API Key Authentication

**Flow:**
```
1. Client sends API request with apikey
   ↓
2. Extract apikey from body or X-API-KEY header
   ↓
3. Query api_keys table
   ↓
4. Decrypt stored key with Fernet
   ↓
5. Compare with provided key
   ↓
6. Return user_id if valid
   ↓
7. Proceed with request
```

**API Key Generation:**
- Generated at `/apikey` endpoint
- Format: `secrets.token_hex(32)` (64-character hex)
- Encrypted with Fernet (key derived from `API_KEY_PEPPER`)
- Stored in api_keys table
- TTL cache prevents repeated DB lookups

---

## 10. Order Flow & Action Center

### Order Mode System

**Two Modes:**
1. **Auto Mode:** Orders execute immediately
2. **Semi-Auto Mode:** Orders queued for approval (Action Center)

**Order Routing Logic:**
```python
def should_route_to_pending(user_id):
    order_mode = get_order_mode(user_id)
    return order_mode == "semi_auto"
```

### Semi-Auto Workflow (Action Center)

```
User places order (semi_auto mode)
    ↓
[order_router_service.queue_order()]
    ↓
Create PendingOrder:
    - user_id
    - api_type (placeorder, modifyorder, etc.)
    - order_data (JSON)
    - status = "pending"
    - created_at, created_at_ist
    ↓
Return 202 Accepted {"pending_id": "..."}
    ↓
User approves via Action Center UI
    ↓
Update PendingOrder:
    - status = "approved"
    - approved_at, approved_by
    ↓
[pending_order_execution_service.execute_pending_order()]
    ↓
Call broker API (now executes)
    ↓
Update PendingOrder:
    - broker_order_id
    - broker_status
    ↓
Emit SocketIO event → UI updates
```

**Bypassed Operations (Always Execute):**
- `closeposition`
- `cancelorder`
- `cancelallorder`
- `modifyorder` (configurable)

**Use Case:** Managed accounts where advisor approval required before execution

---

## 11. Analyzer/Paper Trading Mode

### Sandbox Database (sandbox.db)

**Isolation:**
- Completely separate from live trading
- Own database: `/db/sandbox.db`
- Own tables: SandboxOrders, SandboxTrades, SandboxPositions, SandboxHoldings
- No interaction with live broker APIs

**Virtual Capital:**
- ₹1 Crore (10 million INR) per user
- Realistic margin system with leverage:
  - Equity: 1x
  - Futures: 10x
  - Options: 10x
- Margin requirements calculated per order

**Features:**
1. **Execution Engine:** Continuous background thread processes sandbox orders
2. **Square-Off Scheduler:** Auto-closes all positions at market close (3:30 PM IST)
3. **Settlement System:** T+1 settlement for holdings
4. **PnL Tracking:** Daily P&L calculations
5. **Market Data:** Uses live market data (quotes API) for realistic fills

**Activation:**
```python
# User enables analyzer mode in settings
set_analyze_mode(user_id, True)

# All orders routed to sandbox
if get_analyze_mode(user_id):
    execute_in_sandbox(order_data)
else:
    execute_with_broker(order_data)
```

**API Transparency:**
- API responses identical format (live vs paper)
- Orders return same structure
- Positions/trades use same schema
- Complete testing without risking capital

---

## 12. Frontend Architecture (React 19)

Located in `/frontend/`

### Technology Stack
- **Framework:** React 19
- **Language:** TypeScript
- **Build Tool:** Vite
- **UI Components:** shadcn/ui (Radix UI primitives)
- **State Management:**
  - TanStack Query (server state)
  - Zustand (client state)
- **Routing:** React Router
- **Linting:** Biome.js
- **Testing:** Vitest (unit), Playwright (E2E)

### Directory Structure
```
frontend/
├── src/
│   ├── api/                  # API client functions (fetch wrappers)
│   ├── app/                  # App configuration & providers
│   ├── components/           # Reusable React components
│   │   ├── ui/               # shadcn/ui components
│   │   └── [feature]/        # Feature-specific components
│   ├── pages/                # Page components (routes)
│   ├── hooks/                # Custom React hooks
│   ├── stores/               # Zustand state stores
│   ├── contexts/             # React contexts
│   ├── types/                # TypeScript types & interfaces
│   ├── utils/                # Frontend utilities
│   ├── assets/               # Images, fonts, static assets
│   ├── main.tsx              # Entry point
│   └── App.tsx               # Root component
│
├── public/                   # Public static files
├── dist/                     # Built output (gitignored, CI/CD builds)
├── e2e/                      # Playwright E2E tests
├── node_modules/             # Dependencies
│
├── package.json              # Dependencies & scripts
├── tsconfig.json             # TypeScript configuration
├── biome.json                # Linting & formatting rules
├── components.json           # shadcn/ui config
└── vite.config.ts            # Vite build config
```

### Development Workflow

**Local Development:**
```bash
cd frontend
npm install
npm run dev          # Dev server with hot reload (port 5173)
```

**Production Build:**
```bash
npm run build        # Outputs to frontend/dist/
```

**Testing:**
```bash
npm test             # Vitest unit tests
npm run e2e          # Playwright E2E tests
npm run lint         # Biome linting
npm run format       # Biome formatting
```

### API Integration Pattern

**TanStack Query Example:**
```typescript
import { useQuery } from '@tanstack/react-query';

const { data, isLoading, error } = useQuery({
  queryKey: ['positions'],
  queryFn: () => api.getPositions(),
  refetchInterval: 5000  // Auto-refresh every 5s
});
```

**Real-Time Updates (SocketIO):**
```typescript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('order_update', (data) => {
  // Update UI with new order status
});
```

### Build Process

**Important:** `frontend/dist/` is **gitignored**
- CI/CD pipeline builds on every push
- Local builds required before running app locally
- Flask serves built assets via `blueprints/react_app.py`
- Route `/react` → serves React SPA
- 404 handler → serves React for client-side routing

---

## 13. Utilities & Helpers

Located in `/utils/`

### Key Utility Modules

**auth_utils.py** - Authentication Helpers
- Password validation (strength checks)
- Master contract download orchestration
- Session validation helpers
- `should_download_master_contract()` logic

**logging.py** - Centralized Logging
- Colored console output
- Log level configuration
- Module-specific loggers via `get_logger(__name__)`

**traffic_logger.py** - WSGI Traffic Middleware
- Records all HTTP requests
- Logs: IP, method, path, status, duration_ms
- Asynchronous logging to `traffic_db`
- Skips: static files, health checks, traffic endpoints

**security_middleware.py** - IP Ban Enforcement
- Checks IPBan table on every request
- Returns 403 for banned IPs
- 403 error handler registration

**plugin_loader.py** - Dynamic Broker Loading
- Auto-discovers brokers in `/broker/` directory
- Loads `authenticate_broker()` function from each
- Graceful error handling (logs errors, continues)
- Returns dict of `{broker_name: auth_function}`

**latency_monitor.py** - API Latency Tracking
- Tracks response times for all API calls
- Calculates p50, p90, p99 percentiles
- Stores in `latency_db`
- Dashboard at `/latency`

**health_monitor.py** - System Health Checks
- Background daemon monitors system health
- Checks: database connections, broker API status, WebSocket connectivity
- Stores health metrics in `health_db`
- Alerts on failures

**httpx_client.py** - HTTP Client Wrapper
- Shared HTTPX client with connection pooling
- Default timeouts: 10s connect, 30s read
- Connection reuse for broker API calls
- Thread-safe singleton pattern

**constants.py** - Validation Constants
- Valid exchanges: NSE, BSE, NFO, MCX, CDS, NCDEX
- Valid order types: MARKET, LIMIT, SL, SL-M
- Valid products: CNC, NRML, MIS, BO, CO
- Valid actions: BUY, SELL

**socketio_error_handler.py** - SocketIO Error Recovery
- Catches SocketIO emit failures
- Logs errors without crashing
- Retry logic for transient failures

**ip_helper.py** - IP Address Extraction
- Handles X-Forwarded-For headers
- Works behind reverse proxies (nginx, Cloudflare)
- Fallback to `request.remote_addr`

**email_utils.py** - Email Notifications
- Password reset emails
- SMTP configuration from settings
- Template rendering with Jinja2

**number_formatter.py** - Indian Number Formatting
- Formats numbers with Indian conventions (lakhs, crores)
- Currency formatting (₹ symbol)

**version.py** - Version Management
- Application version tracking
- Displayed in UI footer

---

## 14. Performance Optimizations

### 1. Caching Strategy

**Multi-Level Caching:**
- **L1: In-Memory TTL Cache**
  - Auth tokens: 5-10 minutes
  - Feed tokens: 30 minutes
  - Usernames: 30 seconds
  - Symbols: 1 hour (100K+ symbols)
- **L2: Database**
  - Indexed queries on symbol, token, exchange
  - Connection pooling (SQLite: NullPool, PostgreSQL: 50 connections)
- **L3: Persistent Storage**
  - Cache restoration on app startup
  - Faster startup (no master contract download needed)

### 2. Asynchronous Operations

**ThreadPoolExecutor:**
- Analyzer logging (non-blocking)
- API logging (non-blocking)
- Master contract download (background thread)
- Telegram alerts (background)

**SocketIO Background Tasks:**
- `socketio.start_background_task(func)` for non-blocking emits
- Prevents slow UI updates from blocking request handling

### 3. Parallel Initialization

**Database Initialization:**
```python
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [
        executor.submit(init_auth_db),
        executor.submit(init_user_db),
        executor.submit(init_apilog_db),
        # ... 12 more databases
    ]
    concurrent.futures.wait(futures)
```

**Benefit:** 15 databases initialized in ~2 seconds (vs 30 seconds sequential)

### 4. Connection Pooling

**HTTP Client:**
- Shared HTTPX client across all broker API calls
- Connection reuse reduces handshake overhead (10-50ms savings)
- Configurable pool size: 10 connections

**WebSocket:**
- Automatic connection pooling when symbol limit exceeded
- Shared ZeroMQ publisher prevents duplicate connections
- Connection reuse across multiple subscriptions

### 5. Message Throttling

**WebSocket Proxy:**
- Minimum 50ms between identical market data updates
- Prevents network flooding on high-frequency ticks
- Reduces bandwidth by 90-99% for slow clients

### 6. Subscription Indexing

**O(1) Lookups:**
```python
# Instead of iterating all clients (O(n))
for client in clients:
    if client.subscribed_to(symbol):
        send_to_client(client, data)

# Use subscription index (O(1))
clients = subscription_index[(symbol, exchange, mode)]
for client in clients:
    send_to_client(client, data)
```

**Benefit:** Scales to 10,000+ connected clients

### 7. Database Query Optimization

**Indexed Columns:**
- `symbol`, `token`, `exchange`, `brsymbol`, `brexchange` in SymToken
- `user_id`, `broker` in Auth
- `api_key` in api_keys
- `ip_address` in IPBan

**Bulk Operations:**
- `copy_from_dataframe()` for master contract insertion (100K+ rows in 5s)
- Batch queries for symbol resolution

---

## 15. Security Architecture

### 1. Password Security
- **Hashing:** Argon2 with pepper (32+ character `API_KEY_PEPPER`)
- **Re-hashing:** Automatic re-hash on login if algorithm updated
- **Validation:** Minimum 8 characters, complexity requirements

### 2. API Key Security
- **Generation:** `secrets.token_hex(32)` (cryptographically secure)
- **Storage:** Encrypted with Fernet (key derived from pepper)
- **Transmission:** HTTPS only (secure cookie flag)

### 3. CSRF Protection
- **Flask-WTF:** CSRF tokens for all POST requests
- **Exemptions:** `/api/v1/*` (API key authentication), OAuth callbacks
- **Token Rotation:** New token on each page load

### 4. IP Ban System
- **Module:** `database/traffic_db.py` - `IPBan` model
- **Enforcement:** `security_middleware.py` checks on every request
- **Manual Bans:** Admin can ban IPs via UI
- **Auto-Bans:** 404 tracker can trigger auto-ban (configurable)

### 5. Rate Limiting
- **Module:** `limiter.py` - Flask-Limiter
- **Strategy:** Moving window algorithm
- **Storage:** In-memory (production: Redis recommended)
- **Per-Endpoint Limits:**
  - Login: 5/minute, 25/hour
  - Orders: 10/second
  - Other APIs: 10/second

### 6. Content Security Policy (CSP)
- **Module:** `csp.py`
- **Policy:** Restricts script sources, prevents XSS
- **Nonce-based:** Inline scripts allowed with nonce

### 7. Session Security
- **Expiry:** 3:30 AM IST (market close)
- **Flags:** HttpOnly, Secure (HTTPS), SameSite=Lax
- **Validation:** `@before_request` checks expiry on every request

### 8. Secrets Management
- **Pre-commit Hook:** `.secrets.baseline` with detect-secrets
- **Scanning:** Prevents accidental commit of API keys, passwords
- **Environment:** All secrets in `.env` (never committed)

---

## 16. Testing Strategy

### Current Testing Approach
- **Manual Testing:** Primary method via web UI & Swagger API
- **API Playground:** `/playground` endpoint for interactive testing
- **Analyzer Mode:** Paper trading for strategy validation
- **End-to-End:** Manual E2E workflows

### Test Infrastructure
- **Location:** `/test/` directory
- **Framework:** pytest configured in `pyproject.toml`
- **Coverage:** `pytest --cov` for coverage reports
- **Frontend:** Vitest (unit), Playwright (E2E)

### Running Tests

**Backend:**
```bash
# All tests
uv run pytest test/ -v

# Specific test file
uv run pytest test/test_broker.py -v

# Single test function
uv run pytest test/test_broker.py::test_function_name -v

# With coverage
uv run pytest test/ --cov
```

**Frontend:**
```bash
cd frontend

# Unit tests
npm test

# E2E tests
npm run e2e

# Coverage
npm run test:coverage
```

### Manual Testing Access Points
- **Web UI:** http://127.0.0.1:5000
- **Swagger API:** http://127.0.0.1:5000/api/docs
- **React App:** http://127.0.0.1:5000/react
- **Analyzer:** http://127.0.0.1:5000/analyzer
- **Health Check:** http://127.0.0.1:5000/health

---

## 17. Deployment & Operations

### Local Development

**Using UV (Recommended):**
```bash
# First time setup
pip install uv
cp .sample.env .env
# Edit .env with your broker credentials

# Build React frontend
cd frontend && npm install && npm run build && cd ..

# Run application
uv run app.py
```

**Access Points:**
- Main app: http://127.0.0.1:5000
- API docs: http://127.0.0.1:5000/api/docs
- WebSocket proxy: ws://127.0.0.1:8765

### Production with Gunicorn

**Linux/Unix:**
```bash
uv run gunicorn --worker-class eventlet -w 1 app:app
```

**Important:** Must use `-w 1` (single worker) for WebSocket compatibility

**Why Single Worker:**
- SocketIO requires sticky sessions
- WebSocket proxy shares ZeroMQ publisher
- Multiple workers cause connection issues

### Docker Deployment

**Build:**
```bash
./docker-build.sh
# Or: docker build -t openalgo .
```

**Run:**
```bash
docker-compose up -d
```

**Configuration:**
- WebSocket server started separately by `start.sh`
- Detected via `/.dockerenv` or `APP_MODE=standalone`
- PostgreSQL recommended for production (SQLite for development only)

### Environment Configuration

**Critical Variables:**
- `APP_KEY` - Flask secret key (generate with `secrets.token_hex(32)`)
- `API_KEY_PEPPER` - Encryption pepper (generate with `secrets.token_hex(32)`)
- `BROKER_API_KEY` / `BROKER_API_SECRET` - Broker credentials
- `VALID_BROKERS` - Comma-separated list of enabled brokers
- `DATABASE_URL` - Main database path (SQLite or PostgreSQL)
- `WEBSOCKET_HOST` / `WEBSOCKET_PORT` - WebSocket server config
- `FLASK_DEBUG` - Debug mode (development only)

### Monitoring & Observability

**Health Check:**
- Endpoint: `/health`
- Checks: Database, broker API, WebSocket connectivity
- Dashboard: `/health` UI

**Latency Monitoring:**
- Dashboard: `/latency`
- Tracks: p50, p90, p99 response times
- Database: `latency.db`

**Traffic Logs:**
- Dashboard: `/traffic`
- Logs: All HTTP requests with IP, status, duration
- Database: `logs.db`

**API Logs:**
- Logs: All API requests/responses (JSON)
- Database: `logs.db` (OrderLog table)
- Async logging: Non-blocking

---

## 18. Integration Points

### TradingView Integration
- **Webhooks:** `/chartink` endpoint accepts TradingView alerts
- **Strategy Module:** `blueprints/chartink.py`
- **JSON Format:** `tv_json.py` for alert parsing
- **Execution:** Auto-executes orders based on alert signals

### Amibroker Integration
- **REST API:** Direct API calls from AFL scripts
- **Example:** `/examples/amibroker/`
- **Authentication:** API key in headers

### Excel Integration
- **VBA Scripts:** `/examples/excel/` (if exists)
- **REST API:** XMLHTTP requests from Excel
- **Real-Time Data:** WebSocket connections from VBA

### Python Strategies
- **Scheduler:** `blueprints/python_strategy.py`
- **Location:** `/strategies/`
- **Example:** `strategies/examples/simple_ema_strategy.py`
- **Execution:** Background thread runs strategies on schedule
- **Hot Reload:** Strategies excluded from Flask auto-reload

### Telegram Bot
- **Module:** `services/telegram_bot_service.py`
- **Features:** Trade alerts, order status, account balance
- **Configuration:** `database/telegram_db.py`
- **Webhook:** `/telegram` endpoint

### Flow Builder
- **Visual Workflow:** Graph-based automation
- **Module:** `blueprints/flow.py`
- **Services:** `flow_executor_service.py`, `flow_scheduler_service.py`
- **Price Monitoring:** `flow_price_monitor_service.py`
- **Database:** `flow_db.py`

---

## 19. Key Design Patterns

### 1. Plugin Architecture
- Brokers dynamically loaded at runtime
- No manual registration needed
- Extensible: Drop new broker and restart

### 2. Service Layer Pattern
- Blueprints (UI) and REST API both call services
- Services contain all business logic
- Consistent interface across endpoints

### 3. Repository Pattern
- Database modules abstract query complexity
- Services call database functions
- Easy to swap database backends

### 4. Factory Pattern
- `BrokerFactory.create_broker_adapter()` creates adapters
- `plugin_loader.py` creates auth functions
- Dynamic module imports via `importlib`

### 5. Observer Pattern
- SocketIO emits events to all connected clients
- ZeroMQ pub-sub for market data distribution
- Subscribers receive updates without polling

### 6. Adapter Pattern
- Broker WebSocket adapters normalize data
- Symbol mapping adapters transform formats
- Consistent interface across 29 brokers

### 7. Singleton Pattern
- `SharedZmqPublisher` - single instance across all adapters
- HTTPX client - shared connection pool
- Database sessions - scoped sessions

### 8. Background Job Pattern
- ThreadPoolExecutor for async tasks
- APScheduler for recurring jobs
- SocketIO background tasks for non-blocking emits

---

## 20. Critical Files Reference

| Component | File | Purpose | Lines |
|-----------|------|---------|-------|
| **Main App** | `app.py` | Flask application entry point | 35KB |
| **Environment** | `.env` / `.sample.env` | Configuration variables | - |
| **Dependencies** | `pyproject.toml` | Python packages & config | 155+ deps |
| **Frontend Entry** | `frontend/src/main.tsx` | React entry point | - |
| **REST API Registry** | `restx_api/__init__.py` | API endpoint registration | - |
| **Service Example** | `services/place_order_service.py` | Order placement logic | - |
| **Auth Module** | `database/auth_db.py` | Authentication & token storage | - |
| **Symbol Cache** | `database/token_db_enhanced.py` | Symbol resolution cache | - |
| **Plugin Loader** | `utils/plugin_loader.py` | Dynamic broker discovery | 38 lines |
| **WebSocket Server** | `websocket_proxy/server.py` | Market data streaming | 71KB |
| **Base Adapter** | `websocket_proxy/base_adapter.py` | Adapter interface | 23KB |
| **Connection Pool** | `websocket_proxy/connection_manager.py` | WebSocket pooling | 31KB |
| **Broker Factory** | `websocket_proxy/broker_factory.py` | Adapter creation | 13KB |
| **Traffic Logger** | `utils/traffic_logger.py` | HTTP request logging | - |
| **Security Middleware** | `utils/security_middleware.py` | IP ban enforcement | - |
| **Health Monitor** | `utils/health_monitor.py` | System health checks | - |
| **Latency Monitor** | `utils/latency_monitor.py` | API latency tracking | - |

---

## 21. Development Best Practices

### 1. Always Use UV
**Never use global Python:**
```bash
# Good
uv run app.py
uv run python script.py
uv add package_name

# Bad
python app.py
pip install package
```

### 2. Frontend Build Required
**Before running app locally:**
```bash
cd frontend
npm install
npm run build
cd ..
uv run app.py
```

### 3. Environment Setup
**Never commit secrets:**
- Copy `.sample.env` to `.env`
- Generate new keys: `uv run python -c "import secrets; print(secrets.token_hex(32))"`
- Set `APP_KEY` and `API_KEY_PEPPER`

### 4. Database Access
**Always use SQLAlchemy ORM:**
```python
# Good
user = User.query.filter_by(username='admin').first()

# Bad
cursor.execute("SELECT * FROM users WHERE username='admin'")
```

### 5. Adding New Broker
**Follow standardized structure:**
1. Create `broker/newbroker/` directory
2. Implement all required modules (api/, mapping/, database/, streaming/)
3. Add `plugin.json` metadata
4. Add to `VALID_BROKERS` in `.env`
5. Restart app (auto-discovered)

### 6. Error Handling
**Return consistent JSON responses:**
```python
return {
    'status': 'success' | 'error',
    'message': 'Human-readable message',
    'data': {...}  # Optional
}
```

### 7. Logging
**Use centralized logging:**
```python
from utils.logging import get_logger
logger = get_logger(__name__)
logger.info("Order placed successfully")
```

### 8. Async Operations
**Don't block request handling:**
```python
# Good
executor.submit(log_to_database, data)
socketio.start_background_task(emit_event, data)

# Bad
log_to_database(data)  # Blocks response
```

### 9. Git Commits
**Use conventional commits:**
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Build/config changes

### 10. Testing Before Deployment
**Always test in analyzer mode first:**
- Enable analyzer mode in settings
- Test strategies with virtual capital
- Verify all order flows work correctly
- Switch to live mode only after validation

---

## 22. Troubleshooting Guide

### WebSocket Connection Issues
**Symptoms:** WebSocket fails to connect, market data not updating
**Solutions:**
1. Check WebSocket server is running: `netstat -tuln | grep 8765`
2. Verify `WEBSOCKET_HOST` and `WEBSOCKET_PORT` in `.env`
3. For Gunicorn: Ensure `-w 1` (single worker)
4. Check firewall settings for port 8765
5. Verify broker WebSocket adapter is loaded correctly

### Database Locked Errors
**Symptoms:** `database is locked` errors in logs
**Solutions:**
1. SQLite doesn't handle high concurrency well
2. Close all connections and restart app
3. For production: Use PostgreSQL instead of SQLite
4. Check no manual sqlite3 connections open

### Broker Integration Not Loading
**Symptoms:** Broker not appearing in login dropdown
**Solutions:**
1. Check broker name in `VALID_BROKERS` (.env)
2. Verify `plugin.json` exists in broker directory
3. Check broker module structure matches standard pattern
4. Restart application to reload plugins
5. Check logs for import errors: `grep "Failed to load broker" log/*.log`

### React Frontend Build Errors
**Symptoms:** Build fails, TypeScript errors
**Solutions:**
1. Ensure Node.js version matches `package.json` engines
2. Delete `node_modules` and run `npm install` again
3. Check for TypeScript errors: `npm run build`
4. Verify all dependencies installed: `npm list`

### Master Contract Download Fails
**Symptoms:** Symbols not resolving, "symbol not found" errors
**Solutions:**
1. Check broker API credentials in `.env`
2. Verify broker API is accessible (network/firewall)
3. Check master contract download status: `/master-contract-status`
4. Manually trigger download: Force download button in UI
5. Check logs for API errors: `grep "master_contract" log/*.log`

### Session Expiry Issues
**Symptoms:** Logged out unexpectedly
**Solutions:**
1. Session expires at 3:30 AM IST by default
2. Check `is_session_valid()` logic in `utils/session.py`
3. Verify `session_expiry` set correctly on login
4. Check session cookie flags (HttpOnly, Secure, SameSite)

### High Memory Usage
**Symptoms:** Python process consuming excessive RAM
**Solutions:**
1. Check symbol cache size: 100K+ symbols = ~500MB RAM
2. Reduce `MAX_WEBSOCKET_CONNECTIONS` in `.env`
3. Limit connected WebSocket clients
4. Check for memory leaks in broker adapters
5. Consider switching to PostgreSQL (less memory than SQLite)

### Rate Limit Errors
**Symptoms:** 429 Too Many Requests errors
**Solutions:**
1. Check rate limits in `.env`: `ORDER_RATE_LIMIT`, `API_RATE_LIMIT`
2. Increase limits if legitimate high-frequency trading
3. Use batch APIs (`/multiquotes`, `/basketorder`) instead of individual calls
4. Implement exponential backoff in client code

---

## 23. Future Considerations

### Scalability
- **Horizontal Scaling:** Requires shared session store (Redis) and PostgreSQL
- **WebSocket Scaling:** Sticky sessions needed for SocketIO
- **Database:** PostgreSQL recommended for production (connection pooling, concurrency)
- **Caching:** Redis for rate limiting, session storage, symbol cache

### Performance
- **Async/Await:** Consider migrating to FastAPI for native async support
- **Database Queries:** Add more indexes for frequently queried columns
- **WebSocket:** Consider dedicated WebSocket server (separate process)
- **Caching:** CDN for frontend assets, Redis for API responses

### Security
- **OAuth2:** Implement OAuth2 for API authentication (not just API keys)
- **Role-Based Access Control:** Granular permissions per user
- **Audit Logging:** Complete audit trail for compliance
- **Encryption at Rest:** Encrypt sensitive database tables

### Features
- **Multi-User Support:** Sub-accounts, family accounts
- **Portfolio Analytics:** Advanced P&L analysis, tax reporting
- **Backtesting:** Historical strategy backtesting engine
- **Market Replay:** Replay historical market data for strategy testing
- **AI Integration:** AI-powered strategy suggestions, risk management

---

## 24. Documentation Resources

### Internal Documentation
- **README.md** - Project overview & quick start
- **CLAUDE.md** - AI assistant development guide (extremely comprehensive)
- **INSTALL.md** - Installation instructions
- **DOCKER_README.md** - Docker deployment guide
- **CONTRIBUTING.md** - Contribution guidelines
- **SECURITY.md** - Security policies

### API Documentation
- **Swagger UI:** http://127.0.0.1:5000/api/docs (interactive API testing)
- **/docs/api/** - Detailed API documentation (50+ endpoint docs)
- **Postman Collection:** `/collections/postman/` (importable collection)

### Architecture Documentation
- **/docs/design/** - 27 architecture design documents
- **HEALTH_MONITORING_IMPLEMENTATION.md** - Health monitoring guide
- **HEALTH_MONITOR_REACT_FRONTEND.md** - Frontend monitoring

### User Guides
- **/docs/userguide/** - 30+ user guides for various features
- **Broker Setup Guides** - Individual broker configuration docs

### External Resources
- **Official Docs:** https://docs.openalgo.in
- **GitHub Repository:** https://github.com/marketcalls/openalgo
- **Issue Tracker:** https://github.com/marketcalls/openalgo/issues

---

## 25. Summary & Architectural Principles

### Core Architectural Principles

1. **Separation of Concerns**
   - Blueprints handle UI routes
   - REST API handles programmatic access
   - Services contain business logic
   - Database modules handle persistence

2. **Plugin-Based Extensibility**
   - Brokers dynamically discovered at runtime
   - No hardcoded broker list
   - Easy to add new brokers (drop directory, restart)

3. **Async-First Design**
   - All long-running operations non-blocking
   - ThreadPoolExecutor for background tasks
   - SocketIO background tasks for real-time updates

4. **Database Isolation**
   - 5 separate databases prevent lock contention
   - Main, logs, latency, sandbox, historical data
   - Reduces database locks, improves concurrency

5. **Security Layered**
   - IP bans, CSRF protection, API key verification
   - Session expiry, rate limiting, password hashing
   - Multiple security layers (defense in depth)

6. **Observability**
   - Traffic logs, API logs, analyzer logs
   - Latency monitoring, health checks
   - Complete audit trail for compliance

7. **Fault Tolerance**
   - Broker disconnections trigger reconnect
   - Master contract retry logic
   - Graceful error handling (no crashes)

8. **User Control**
   - Order modes (auto/semi-auto)
   - Analyzer mode (paper trading)
   - Role-based permissions (future)

### What Makes OpenAlgo Unique

1. **Broker Agnostic:** 29 brokers with unified API
2. **Real-Time Streaming:** Unified WebSocket proxy with automatic connection pooling
3. **Paper Trading:** Complete sandbox mode with realistic margins
4. **Order Approval:** Semi-auto mode for managed accounts
5. **Visual Workflows:** Flow builder for automation
6. **Multi-Platform:** TradingView, Amibroker, Excel, Python, REST API
7. **Production-Ready:** Used by real traders with real capital

---

## Conclusion

OpenAlgo is a **comprehensive, production-grade algorithmic trading platform** that successfully abstracts 29 diverse Indian brokers into a unified API. Its modular architecture, plugin system, and real-time streaming capabilities make it a powerful tool for algorithmic traders, strategy developers, and trading firms.

The codebase demonstrates professional software engineering practices:
- Clean architecture with clear separation of concerns
- Extensive error handling and logging
- Security-first design with multiple protection layers
- Performance optimizations (caching, pooling, async operations)
- Comprehensive documentation (100+ docs)
- Extensible design (easy to add brokers, features)

**Total Codebase Size:** 500+ Python files, 29 broker integrations, 44+ REST endpoints, 41 blueprints, 57 services, 29 databases modules, 100+ documentation pages

**Key Technologies:** Flask, React 19, SQLAlchemy, WebSocket, ZeroMQ, TypeScript, Vite, shadcn/ui, TanStack Query

This analysis provides a complete understanding of the OpenAlgo architecture, enabling developers to confidently navigate, extend, and maintain the codebase.
