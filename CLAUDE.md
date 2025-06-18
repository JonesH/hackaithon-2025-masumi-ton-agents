# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Simple Agent API - a FastAPI-based service for serving AI agents with PostgreSQL/pgvector storage. The application uses the Agno framework for agent management and supports multiple pre-built agents (web search, finance, Agno assist).

## Architecture

- **FastAPI Server**: Main API server (`api/main.py`) with CORS middleware and route organization
- **Agent System**: Located in `agents/` with a selector pattern for different agent types
- **Database Layer**: SQLAlchemy ORM with PostgreSQL/pgvector for vector storage (`db/`)  
- **API Routes**: Organized under `api/routes/` with versioned routing (`/v1`)
- **Docker Composition**: Uses `compose.yaml` for local development with pgvector database

Key architectural patterns:
- Agent factory pattern in `agents/selector.py` with enum-based agent selection
- Dependency injection for database sessions via `db/session.py`
- Environment-based configuration through `api/settings.py`

## Development Commands

### Environment Setup
```bash
# Install uv package manager (required)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup development environment (creates .venv and installs dependencies)
./scripts/dev_setup.sh

# Activate virtual environment
source .venv/bin/activate
```

### Code Quality
```bash
# Format code with ruff
./scripts/format.sh

# Validate code (lint + type check)
./scripts/validate.sh
```

### Running the Application
```bash
# Local development with Docker
export OPENAI_API_KEY="your_key_here"
docker compose up -d

# API available at http://localhost:8000
# API docs at http://localhost:8000/docs
# Database on localhost:5432

# Stop services
docker compose down
```

### Dependency Management
```bash
# After modifying pyproject.toml dependencies:
./scripts/generate_requirements.sh

# To upgrade all dependencies:
./scripts/generate_requirements.sh upgrade

# Rebuild containers after dependency changes:
docker compose up -d --build
```

## Key Technical Details

- **Python Version**: 3.12+ (configured in dev_setup.sh)
- **Package Manager**: uv for dependency management
- **Code Style**: Ruff for formatting and linting, MyPy for type checking
- **Database**: PostgreSQL with pgvector extension for vector operations
- **Agent Framework**: Agno 1.4.6 for agent orchestration
- **Model Default**: GPT-4.1 (configurable per agent)

## Agent System

Agents are defined in the `agents/` directory with a centralized selector pattern:
- `AgentType` enum defines available agent types
- `get_agent()` factory function handles agent instantiation
- Each agent supports configurable model_id, user_id, session_id, and debug_mode

Pre-built agents:
- `web_agent`: Web search capabilities via DuckDuckGo
- `finance_agent`: Financial data via YFinance API  
- `agno_assist`: Agno platform assistance (requires knowledge base loading)

## Configuration

Environment variables are managed through:
- `example.env` for reference
- Docker compose environment section
- `api/settings.py` for application configuration

Required environment variables:
- `OPENAI_API_KEY`: Primary model provider API key
- Database credentials (defaults: user=ai, password=ai, db=ai)

## Code Style Preferences

Follow these Python development practices for this project:

### Modern Python Features
- Use Python 3.11+ features and built-in generics: `list[str]`, `dict[str, int]`, `str | None`
- Avoid imports from typing module where possible (use built-in types)
- Use union syntax `|` instead of `Optional[]` or `Union[]`

### Code Organization
- Write self-documenting code with clear, descriptive names
- Keep functions small and focused on single responsibility
- Use guard clauses and early returns to reduce nesting
- Extract complex logic into well-named helper functions
- Prefer flat code structure over deeply nested blocks

### Type Hints
- Use comprehensive type hints throughout
- Leverage modern Python type syntax (built-in generics, union types)
- Only import from typing when necessary (Protocol, TypeVar, Generic)

### Error Handling
- Avoid over-catching exceptions; let unexpected errors propagate
- Only catch exceptions when meaningful recovery is possible
- Use specific exception types rather than broad catches

### General Practices
- Follow DRY principles - extract common functionality
- Use constants for magic numbers and repeated values
- Favor explicit, readable code over clever implementations
- Maintain consistent code style with existing codebase patterns