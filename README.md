# Deep Research Agent V1

> Global AI Viral Intelligence Tracker v4.0 — A daily AI intelligence tracker that runs two research engines side-by-side, producing structured reports and displaying them in a Next.js frontend. Available with two backend implementations: **Python/FastAPI** (original) and **Rust/Axum** (high-performance rewrite).

## Prerequisites

- **Python backend**: Python 3.11+, a Google Cloud project with Firestore enabled
- **Rust backend**: Rust toolchain (1.75+, install via [rustup](https://rustup.rs/))
- Node.js 20+
- API keys for: OpenAI, Tavily (+ Google Gemini if using the Python backend)

## Local Setup (Python Backend)

### 1. Clone and install Python dependencies

```bash
git clone https://github.com/cwijayasundara/deepresearch_agent_v1.git
cd deepresearch_agent_v1
pip install -e ".[dev]"
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Configure environment variables

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# LLM & Search API Keys
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key

# Authentication
APP_SHARED_PASSWORD=your-shared-password
JWT_SECRET=your-jwt-secret

# Firestore
FIRESTORE_PROJECT_ID=your-gcp-project-id
FIRESTORE_COLLECTION=research_reports

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Make sure you are authenticated with Google Cloud for Firestore access:

```bash
gcloud auth application-default login
```

### 4. Run tests

```bash
pytest backend/tests/ -q
```

All 98 tests should pass.

### 5. Start the API server

```bash
uvicorn backend.runtime.app:create_app --factory --host 0.0.0.0 --port 8000
```

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 6. Start the frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

The frontend runs at http://localhost:3000.

### 7. Log in and use the app

1. Open http://localhost:3000 in your browser
2. Log in with the password you set in `APP_SHARED_PASSWORD`
3. The dashboard shows the latest research report (if any)
4. Trigger a new research run via the API:

```bash
# Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password": "your-shared-password"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Trigger research
curl -X POST http://localhost:8000/api/reports/trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-02-28"}'
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/api/auth/login` | No | Login (returns JWT) |
| GET | `/api/reports/` | Yes | List all reports |
| GET | `/api/reports/{id}` | Yes | Get a single report |
| POST | `/api/reports/trigger` | Yes | Trigger a new research run |

## Running with Docker

```bash
docker compose up --build
```

This starts the API on port 8000 and the frontend on port 3000.

## Architecture

This project uses a strict 6-layer architecture with forward-only dependencies:

```
Types(0) -> Config(1) -> Repo(2) -> Service(3) -> Runtime(4) -> UI(5)
```

| Layer | Path | Description |
|-------|------|-------------|
| Types | `backend/types/` | Domain types (Pydantic models, enums, errors) |
| Config | `backend/config/` | Settings and prompt templates |
| Repo | `backend/repo/` | Firestore, Gemini, and LangChain clients |
| Service | `backend/service/` | Auth, report parsing, engine runners, orchestrator |
| Runtime | `backend/runtime/` | FastAPI app factory, dependency injection, job runner |
| UI | `backend/ui/` | API routes, auth middleware |

## Project Structure

```
backend/                 # Python/FastAPI backend
├── types/               # Enums, IDs, errors, Pydantic models
├── config/              # Settings (env vars), prompt templates
├── repo/                # Firestore, Gemini, LangChain clients
├── service/             # Auth, parser, engine runners, orchestrator
├── runtime/             # FastAPI app, DI, Cloud Run job entry
├── ui/                  # Routes (health, auth, reports), middleware
└── tests/               # Mirrors backend/ layer structure, 98 tests

rust-backend/            # Rust/Axum backend (drop-in replacement)
├── Cargo.toml           # Dependencies (axum, rig-core, tavily, tokio, etc.)
├── data/                # SQLite database (auto-created)
└── src/
    ├── main.rs          # Tokio entry point, Axum router, CORS
    ├── config.rs        # Settings from .env
    ├── errors.rs        # AppError → Axum IntoResponse
    ├── prompts.rs       # Research prompt template
    ├── parser.rs        # Markdown → structured data (regex)
    ├── orchestrator.rs  # Runs both engines via tokio::join!
    ├── types/           # Enums, events, report, request/response structs
    ├── auth/            # JWT service + Axum auth middleware
    ├── search/          # Parallel Tavily search fan-out
    ├── engines/         # Alpha + Sigma engines (3 parallel LLM sub-calls each)
    ├── repo/            # SQLite CRUD via tokio-rusqlite
    └── routes/          # Health, auth, report handlers

frontend/
├── src/app/             # Next.js pages (login, dashboard, report detail)
├── src/components/      # UI components (engine panel, side-by-side, etc.)
├── src/hooks/           # React hooks (auth, reports)
└── src/lib/             # API client, auth helpers, TypeScript types
specs/                   # Design docs and Stitch UI mockup
deploy/                  # Cloud Run and Cloud Scheduler configs
```

## Research Engines

| Engine | Label | Technology | Color |
|--------|-------|------------|-------|
| Alpha | Agent Alpha | Google Gemini Deep Research | Cyan `#00f2ff` |
| Sigma | Agent Sigma | LangChain + Tavily + GPT-5-mini | Magenta `#ff00e5` |

Both engines run in parallel via `asyncio.gather()`, parse their markdown output into structured data (TL;DR, viral events, deep dives, completeness audit), and store results in Firestore.

---

## Local Setup (Rust Backend)

The Rust backend is a drop-in replacement for the Python/FastAPI server. It exposes the **exact same JSON API**, so the frontend works without any changes. It uses SQLite instead of Firestore for local storage.

### 1. Install the Rust toolchain

If you don't have Rust installed:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

Verify:

```bash
rustc --version   # 1.75+ required
cargo --version
```

### 2. Configure environment variables

The Rust backend reads the same `.env` file as the Python backend. At minimum you need:

```env
# Required
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
APP_SHARED_PASSWORD=your-shared-password
JWT_SECRET=your-jwt-secret

# Optional (defaults shown)
APP_ENV=development
APP_PORT=8000
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
OPENAI_MODEL=gpt-5-mini
CORS_ORIGINS=http://localhost:3000
RUST_LOG=info
```

> **Note**: `GEMINI_API_KEY` and `FIRESTORE_PROJECT_ID` are not required for the Rust backend. It uses OpenAI (via Rig) for both engines and SQLite for storage.

### 3. Build the project

```bash
cd rust-backend
cargo build --release
```

The first build downloads and compiles dependencies (this can take a few minutes). Subsequent builds are fast.

### 4. Run the API server

```bash
cd rust-backend
cargo run --release
```

Or run the binary directly:

```bash
./rust-backend/target/release/rust-backend
```

The server starts on `http://0.0.0.0:8000` (or the port set in `APP_PORT`).

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 5. Start the frontend

In a separate terminal (same as the Python setup):

```bash
cd frontend
npm run dev
```

The frontend at http://localhost:3000 connects to the same `http://localhost:8000` API.

### 6. Trigger a research run

```bash
# Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password": "your-shared-password"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Trigger research
curl -X POST http://localhost:8000/api/reports/trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-02-28"}'
```

### Development commands

```bash
# Build (debug mode, faster compilation)
cargo build

# Build (release mode, optimized binary)
cargo build --release

# Run with debug logging
RUST_LOG=debug cargo run

# Check for compilation errors without building
cargo check
```

### Data storage

The Rust backend stores reports in a local SQLite database at `rust-backend/data/reports.db`. This file is auto-created on first run.

---

## Choosing a Backend

| | Python/FastAPI | Rust/Axum |
|---|---|---|
| **Storage** | Google Firestore | Local SQLite |
| **Engines** | Gemini + LangChain/GPT-5-mini | Rig/GPT-5-mini (both engines) |
| **Performance** | ~30s per research run | ~12-15s (parallel sub-calls) |
| **Dependencies** | pip, Google Cloud SDK | Rust toolchain only |
| **Best for** | Production (GCP), existing Firestore data | Local dev, speed, no cloud dependency |

Both backends serve the same API contract. The frontend works identically with either one.
