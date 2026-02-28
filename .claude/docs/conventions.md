# Coding Conventions

## Python

### Naming
- **Files**: `snake_case.py` (e.g., `user_service.py`)
- **Functions**: `snake_case` (e.g., `create_user`)
- **Classes**: `PascalCase` (e.g., `UserService`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private**: prefix with `_` (e.g., `_validate_email`)

### Type Hints
- All function signatures must have type annotations
- This applies to all Python code including test functions, fixtures, and E2E tests — not just `backend/`
- No `Any` type — use specific types or Generics
- Use `TypeVar` for generic functions
- Use `Protocol` for structural typing

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("User created: email=%s", user.email)
logger.error("Failed to connect", exc_info=True)
```
Never use `print()` in production code.

### Error Handling
```python
# Wrap external calls
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error("API call failed: url=%s", url, exc_info=e)
    raise ServiceError(f"External API unavailable: {url}") from e
```
- Catch specific exceptions, never bare `except:`
- Always log with context before re-raising
- Use custom exception classes from `backend/types/`

### Imports
```python
# 1. Standard library
import logging
from pathlib import Path

# 2. Third-party
from fastapi import APIRouter
from pydantic import BaseModel

# 3. Project (layer order)
from backend.types.user import UserCreate
from backend.config.settings import Settings
```

## TypeScript / React

### Naming
- **Files**: `snake_case.ts` or `kebab-case.ts` (no PascalCase filenames)
- **Functions**: `camelCase`
- **Components**: `PascalCase` (React convention)
- **Types/Interfaces**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`

### Patterns
- Functional components only (no class components)
- Use hooks for state and effects
- Tailwind CSS for styling (no CSS modules)
- No `any` type — use `unknown`, specific types, or generics

## File Size Limits

| Metric | Limit | Warning |
|--------|-------|---------|
| Lines per file | 300 | 250 |
| Lines per function | 50 | 40 |

When a file exceeds limits, split into focused modules following the layer model.

## Git Workflow

- Feature branches: `feature/<story-id>-<brief-name>`
- Spike branches: `spike/<topic>` (for prototyping, should not merge to main without review)
- Commit messages: imperative mood, reference story ID
- One logical change per commit
- PR required for all merges to main

## Secrets

- Never hardcode API keys, passwords, tokens, or credentials
- Use environment variables loaded through `backend/config/`
- Store development values in `.env` (gitignored)
- Document required variables in `.env.example`
