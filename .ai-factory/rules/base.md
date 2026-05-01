# Project Base Rules

> Auto-detected conventions from codebase analysis. Edit as needed.

## Naming Conventions

- **Files:** snake_case (e.g., `mcp_client.py`, `webview.py`, `config.py`)
- **Variables:** snake_case (e.g., `base_url`, `log_level`, `session_id`)
- **Functions:** snake_case (e.g., `get_logger()`, `set_logger()`, `create_logger()`)
- **Classes:** PascalCase (e.g., `DeepPresenterConfig`, `PlaywrightConverter`, `InputRequest`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `PDF_OPTIONS`, `PACKAGE_DIR`)

## Module Structure

- **deeppresenter/** — Active product surface (CLI, agents, tools, utils)
  - `agents/` — Agent classes (Agent base, Research, Design, PPTAgent)
  - `cli/` — Typer CLI commands (onboard, generate, serve, config, clean)
  - `tools/` — MCP-style tool servers (search, research, reflect, sandbox)
  - `utils/` — Config, logging, constants, web conversion, MCP client
  - `html2pptx/` — Node.js HTML→PPTX conversion
  - `test/` — Integration tests
- **pptagent/** — Legacy generation library (keep changes scoped)
  - `document/` — Document parsing and processing
  - `presentation/` — Slide generation and layout
  - `templates/` — PPTX templates and layout definitions
  - `test/` — Unit tests

## Error Handling

- Minimal exception handling — no control flow via try/except
- Exceptions only for concrete failure modes, not normal control flow
- Use assertions for validation (e.g., `assert name not in loggerDict`)
- Prefer early returns and guard clauses over nested conditionals
- Max 3 indentation levels — restructure if deeper needed

## Logging

- Custom logging wrapper in `deeppresenter.utils.log`
- Module-level functions: `debug()`, `info()`, `warning()`, `error()`, `critical()`, `exception()`
- ContextVar-based logger isolation per session
- Log level configurable via `DEEPPRESENTER_LOG_LEVEL` (0=debug, 10=info, 20=warning)
- Console output by default, optional file handler
- Use `colorlog` for colored console output

## Testing

- pytest with `asyncio_mode = "auto"`
- Test markers: `llm` (requires API key), `parse` (requires MinerU), `asyncio`
- Tests in `pptagent/test/` (unit) and `deeppresenter/test/` (integration)
- Run: `uv run pytest`
- Skip API tests: `uv run pytest -m "not llm and not parse"`

## Code Style

- Type hints on all functions/methods
- English for comments and documentation
- Modern Python: `pathlib`, `model_dump()`, f-strings
- Ruff for linting (ignores: F403, F405, E741, E722)
- pyupgrade via pre-commit
- Prefer fewer dependencies and less code
- Async generator pattern for streaming agent output

## Architecture Principles

- **Good taste first:** Restructure to eliminate edge cases, not add conditionals
- **Pragmatism:** Solve real problems, not hypothetical ones
- **Simplicity:** Short focused functions, max 3 indentation levels
- **Fewer dependencies:** Prefer less code
- **Dual codepaths:** `deeppresenter` and `pptagent` are related but independent
