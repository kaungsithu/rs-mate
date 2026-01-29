# CLAUDE.md — AI Assistant Guide for RSMate

## Project Overview

RSMate is a web-based tool for managing Amazon Redshift users, roles, groups, and privileges. It replaces manual SQL commands with a UI built on FastHTML + MonsterUI + HTMX.

- **Language:** Python 3.10+ (3.12+ recommended)
- **Framework:** FastHTML (v0.12.4) with MonsterUI components
- **Database:** Amazon Redshift (via `redshift_connector`)
- **License:** AGPL-3.0

## Quick Start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py  # Runs on port 5001
```

## Repository Structure

```
rs-mate/
├── app.py                    # Entry point, all routes (~46 routes)
├── requirements.txt          # Python dependencies
├── components/               # UI layer (FastHTML + MonsterUI components)
│   ├── common.py             # Shared UI helpers
│   ├── database.py           # DB connection form
│   ├── user.py               # User management UI
│   ├── role.py               # Role management UI
│   └── group.py              # Group management UI
├── redshift/                 # Data/model layer (Redshift interaction)
│   ├── database.py           # Connection handling
│   ├── user.py               # User dataclass & operations
│   ├── role.py               # Role dataclass & operations
│   ├── group.py              # Group dataclass & operations
│   ├── privilege.py          # Privilege management
│   └── sql_queries.py        # Centralized SQL queries
├── helpers/
│   └── session_helper.py     # Session serialization/encryption utilities
├── llms-ctx/                 # LLM context docs (FastHTML, MonsterUI)
├── .github/workflows/        # CI/CD (flake8 lint + pytest)
└── img/                      # Screenshots and media
```

## Architecture

The codebase follows a Model-View-Controller pattern:

- **Model** (`redshift/`): Python `@dataclass` classes with class/static methods for DB operations. All SQL is centralized in `sql_queries.py`.
- **View** (`components/`): Functional components returning FastHTML elements. UI factory functions are prefixed `mk_*()`.
- **Controller** (`app.py`): Route handlers using `@rt()` decorator. Session state via encrypted pickle objects.

## Key Conventions

### Code Style
- **Linting:** flake8 — max line length 127, max complexity 10
- **Testing:** pytest (configured in CI, no test files yet)
- **Naming:** `mk_*()` prefix for UI component factory functions
- **Exports:** Modules use `__all__` for explicit public API

### Session Management
- Passwords encrypted with Fernet (`cryptography` library)
- Environment variable: `RSMATE_FERNET_KEY` (auto-generated if absent)
- Helper functions: `sess_store_obj()` / `sess_get_obj()` in `helpers/session_helper.py`
- Session keys: `redshift` (connection), `rsuser`, `rsrole`, `rsgroup`

### SQL Patterns
- Parameterized queries using `pyformat` style to prevent injection
- All query strings defined in `redshift/sql_queries.py`
- Operations execute via `redshift_connector` cursor

### UI Patterns
- HTMX attributes drive interactivity (no custom JavaScript)
- List.js (CDN) for client-side filtering
- MonsterUI components with Violet theme, light mode
- Modal dialogs for confirmations; toast notifications for feedback
- Lazy loading of related data (groups, roles, privileges)

## Build & CI

The GitHub Actions pipeline (`.github/workflows/python-app.yml`) runs on `ubuntu-latest` with Python 3.10:

1. Install dependencies from `requirements.txt`
2. Lint with flake8 (fail on syntax errors / undefined names)
3. Run pytest

## Common Tasks

| Task | Command |
|------|---------|
| Run app | `python app.py` |
| Install deps | `pip install -r requirements.txt` |
| Lint | `flake8 . --count --max-line-length=127 --max-complexity=10 --statistics` |
| Run tests | `pytest` |

## Known TODOs in Code

- `redshift/database.py` — Replace print logging with proper logging
- `redshift/user.py` — Groups/roles update may overwrite each other
- `app.py` — `group_select` returning a list with two values

Use a TODO Tree extension or `grep -rn "TODO" .` to find all items.

## LLM Context Files

The `llms-ctx/` directory contains framework documentation for AI assistants:
- `llms-ctx/fasthtml/llms-ctx.txt` — FastHTML API reference
- `llms-ctx/monster-ui/llms-ctx.txt` — MonsterUI summary
- `llms-ctx/monster-ui/llms-ctx-full.txt` — Full MonsterUI docs

Consult these when working with UI components or routing.

## Important Notes

- The app requires **superuser privileges** on the target Redshift cluster
- System users (ID <= 100) are not filtered — be careful not to modify them
- Deploy in the same VPC as the Redshift cluster for security
- Debug mode and live reload are enabled by default in `app.py`
