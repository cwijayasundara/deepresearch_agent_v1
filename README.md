# Deep Research Agent V1

> Global AI Viral Intelligence Tracker v4.0 — A daily AI intelligence tracker that runs two research engines (Gemini Deep Research + LangChain/Tavily/GPT-4.1) side-by-side, producing structured reports stored in Firestore, served via FastAPI, and displayed in a Next.js frontend.

## Prerequisites

- Python 3.11+
- Node.js 20+
- A Google Cloud project with Firestore enabled
- API keys for: Google Gemini, OpenAI, Tavily

## Local Setup

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
backend/
├── types/           # Enums, IDs, errors, Pydantic models
├── config/          # Settings (env vars), prompt templates
├── repo/            # Firestore, Gemini, LangChain clients
├── service/         # Auth, parser, engine runners, orchestrator
├── runtime/         # FastAPI app, DI, Cloud Run job entry
├── ui/              # Routes (health, auth, reports), middleware
└── tests/           # Mirrors backend/ layer structure, 98 tests
    ├── types/
    ├── config/
    ├── repo/
    ├── service/
    ├── runtime/
    ├── ui/
    └── e2e/
frontend/
├── src/app/         # Next.js pages (login, dashboard, report detail)
├── src/components/  # UI components (engine panel, side-by-side, etc.)
├── src/hooks/       # React hooks (auth, reports)
└── src/lib/         # API client, auth helpers, TypeScript types
specs/               # Design docs and Stitch UI mockup
deploy/              # Cloud Run and Cloud Scheduler configs
```

## Research Engines

| Engine | Label | Technology | Color |
|--------|-------|------------|-------|
| Alpha | Agent Alpha | Google Gemini Deep Research | Cyan `#00f2ff` |
| Sigma | Agent Sigma | LangChain + Tavily + GPT-4.1 | Magenta `#ff00e5` |

Both engines run in parallel via `asyncio.gather()`, parse their markdown output into structured data (TL;DR, viral events, deep dives, completeness audit), and store results in Firestore.
