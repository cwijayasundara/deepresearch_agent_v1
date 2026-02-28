# Deep Research Agent V1

> Built with [claude-code-forge](https://github.com/cwijayasundara/claude_code_forge_v1) — a Claude Code plugin for spec-driven development.

## Getting Started

### Prerequisites

- Python 3.11+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Development

```bash
make test    # Run tests
make lint    # Run linters (layer deps + file size)
make fmt     # Format code
make check   # Lint + test
```

## Architecture

This project uses a strict 6-layer architecture with forward-only dependencies:

```
Types(0) -> Config(1) -> Repo(2) -> Service(3) -> Runtime(4) -> UI(5)
```

| Layer | Path | Description |
|-------|------|-------------|
| Types | `src/types/` | Domain types (Pydantic models, no project imports) |
| Config | `src/config/` | Configuration loading |
| Repo | `src/repo/` | Data access (DB, HTTP, filesystem) |
| Service | `src/service/` | Business logic (no direct I/O) |
| Runtime | `src/runtime/` | App startup, dependency wiring |
| UI | `src/ui/` | API routes, CLI handlers |

## Forge Commands

This project includes the full claude-code-forge toolkit. Just run `claude` in this directory — no `--plugin-dir` needed.

| Command | Description |
|---------|-------------|
| `/build` | Full 11-phase SDLC pipeline |
| `/add-feature` | Add a feature to this project |
| `/just-do-it` | Quick build without spec ceremony |
| `/resume` | Resume an interrupted pipeline |
| `/debug` | 5-phase debugging workflow |
| `/review` | 8-agent parallel code review |
| `/validate` | Full verification suite |
| `/help` | Show all commands |

## Project Structure

```
.claude/             # Forge agents, commands, skills, hooks, linters
src/
├── types/           # Domain types
├── config/          # Configuration
├── repo/            # Data access
├── service/         # Business logic
├── runtime/         # App startup
└── ui/              # API / CLI
tests/               # Mirrors src/ structure
specs/               # Feature specs, stories, design docs
```
