# Project Base Rules

> Auto-detected conventions from codebase analysis. Edit as needed.

## Naming Conventions

- Files: snake_case (e.g., `agent.py`, `webview.py`)
- Variables: snake_case
- Functions: snake_case
- Classes: PascalCase (e.g., `Agent`, `DeepPresenterConfig`)

## Module Structure

- `deeppresenter/` - Main runtime
  - `agents/` - Agent implementations
  - `cli/` - Typer CLI commands
  - `tools/` - MCP tool servers
  - `utils/` - Shared utilities
  - `html2pptx/` - Node-based conversion
- `pptagent/` - Legacy core library

## Error Handling

- Pydantic models for validation
- Explicit exceptions with clear messages
- No excessive exception wrapping

## Logging

- Uses `deeppresenter.utils.log` module
- Functions: `debug()`, `info()`, `timer()`

## Type Hints

- Required for all functions and methods
- Use `typing` module for complex types
- Pydantic `BaseModel` for data models