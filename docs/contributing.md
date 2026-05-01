[← Architecture](architecture.md) · [Back to README](../README.md)

# Contributing

Development workflow, conventions, and guidelines for PPTAgent / DeepPresenter.

## Development Setup

```bash
# Install dependencies
uv sync

# Install Playwright browsers
playwright install --with-deps
playwright install chromium

# Install Node deps for HTML→PPTX
npm install --prefix deeppresenter/html2pptx

# Download fasttext language ID model
modelscope download forceless/fasttext-language-id

# Pull Docker sandbox image
docker pull forceless/deeppresenter-sandbox
docker tag forceless/deeppresenter-sandbox deeppresenter-sandbox

# Install pre-commit hooks
uv run pre-commit install
```

## Development Workflow

### Linting & Formatting

```bash
uv run ruff check --fix && uv run ruff format
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Skip tests requiring API keys
uv run pytest -m "not llm and not parse"
```

**Test markers:**
- `llm` — requires OPENAI_API_KEY
- `parse` — requires minerU API
- `asyncio` — async tests

### Building Package

```bash
uv build
```

## Code Conventions

### Naming
- **Files:** snake_case (e.g., `mcp_client.py`, `webview.py`)
- **Variables/Functions:** snake_case
- **Classes:** PascalCase (e.g., `DeepPresenterConfig`, `PlaywrightConverter`)
- **Constants:** UPPER_SNAKE_CASE

### Code Style
- Type hints on all functions/methods
- English for comments and documentation
- Minimal exception handling — no control flow via try/except
- Max 3 indentation levels — restructure if deeper needed
- Prefer `pathlib`, `model_dump()`, f-strings

### Architecture
- Treat `deeppresenter/` as primary product surface
- Keep changes scoped — don't refactor both `deeppresenter/` and `pptagent/` unless task spans both
- Verify files exist before referencing — README may contain stale paths

## Git Workflow

### Commit Messages

Follow conventional commit format:
- `feat:` — New features
- `fix:` — Bug fixes
- `docs:` — Documentation changes
- `refactor:` — Code refactoring
- `chore:` — Maintenance tasks

### Pre-commit Hooks

Pre-commit hooks enforce:
- Ruff linting and formatting
- pyupgrade for modern Python syntax
- pyproject.toml validation

Install with: `uv run pre-commit install`

## Project Structure Notes

- `deeppresenter/` — Active product surface (CLI, agents, tools, utils)
- `pptagent/` — Legacy generation library (keep changes scoped)
- Tests: `pptagent/test/` (unit) and `deeppresenter/test/` (integration)
- Config templates: `*.example` files, never commit real credentials
- Workspaces: `~/.cache/deeppresenter/<session_id>/`

## Common Development Tasks

### Adding a New Agent

1. Create agent class in `deeppresenter/agents/`
2. Extend `deeppresenter.agents.agent.Agent` base class
3. Define role YAML in `deeppresenter/roles/`
4. Wire into `AgentLoop` in `deeppresenter/main.py`

### Adding a New Tool

1. Create tool server in `deeppresenter/tools/`
2. Define in `deeppresenter/mcp.json`
3. Tool is automatically available to agents via `AgentEnv`

### Modifying CLI Commands

1. Edit `deeppresenter/cli/commands.py`
2. Add shared options in `deeppresenter/cli/common.py`
3. Test with `uv run python -m deeppresenter.cli <command>`

## See Also

- [Getting Started](getting-started.md) — Installation and setup
- [Architecture](architecture.md) — Project structure and patterns
- [Configuration](configuration.md) — Config files and environment variables
