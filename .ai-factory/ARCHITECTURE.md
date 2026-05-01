# Architecture: Modular Monolith

## Overview

A **Modular Monolith** architecture is recommended for this agentic PowerPoint generation system. The project has clear module boundaries (agents, CLI, tools, utils) while maintaining simplicity as a single deployment unit. Python's module system naturally supports this pattern without requiring complex dependency injection frameworks.

This architecture balances:
- **Simple operations**: Single package deployment (via `pyproject.toml`)
- **Clear boundaries**: Each module (agents, tools, cli) is self-contained
- **Future extraction ready**: Modules can be split into separate packages if needed

## Decision Rationale

- **Project type**: AI agent system with CLI interface
- **Tech stack**: Python 3.11+, FastAPI, Typer, Gradio
- **Team size**: Small team (< 10)
- **Key factor**: Clear module boundaries already exist in the codebase (`agents/`, `tools/`, `cli/`, `utils/`)

## Folder Structure

```
deeppresenter/              # Main package (single deployment)
├── __init__.py           # Package version
├── main.py                # AgentLoop orchestration
├── agents/                # Agent implementations
│   ├── __init__.py
│   ├── agent.py           # Base class
│   ├── subagent.py        # Sub-agent logic
│   ├── research.py        # Research agent
│   ├── pptagent.py        # PPT generation agent
│   ├── design.py         # Design/HTML agent
│   └── planner.py        # Planning agent
├── cli/                   # Typer CLI
│   ├── __init__.py
│   ├── commands.py        # CLI commands
│   ├── common.py         # Shared CLI utilities
│   ├── dependency.py     # Dependencies
│   ├── model.py         # CLI models
│   └── __main__.py      # CLI entry
├── tools/                 # MCP tool servers
│   ├── __init__.py
│   ├── search.py
│   ├── research.py
│   ├── reflect.py
│   ├── any2markdown.py
│   ├── task.py
│   └── tool_agents.py
├── utils/                 # Shared utilities
│   ├── __init__.py
│   ├── config.py         # Config loading
│   ├── constants.py      # Constants
│   ├── log.py          # Logging
│   ├── webview.py      # Browser conversion
│   ├── mineru_api.py   # Document parsing
│   ├── mcp_client.py   # MCP client
│   └── ...
└── html2pptx/           # Node-based conversion
    ├── package.json
    └── *.js

pptagent/                  # Legacy core (separate package)
├── mcp_server.py         # FastMCP server
├── test/                # Tests
└── ...                  # Core generation library
```

## Dependency Rules

- ✅ `agents/` → `utils/`
- ✅ `cli/` → `utils/`, `agents/`
- ✅ `tools/` → `utils/`, `agents/`
- ❌ No reverse dependencies (tools must not import CLI specifics)
- ❌ No cross-boundary imports within `deeppresenter/` unless via explicit API

## Module Communication

1. **Agent → Agent**: Via `Agent` base class methods
2. **CLI → Agents**: Via `AgentLoop.run()` entrypoint
3. **Tools → Agents**: Via MCP tool calls
4. **Utils**: Pure utility functions, no agent logic

## Key Principles

1. **Single Entry Point**: `deeppresenter/main.py:AgentLoop` orchestrates all agents
2. **Shared Utils**: Common functionality in `utils/`, not duplicated in modules
3. **Type Hints**: Required for all public functions
4. **Pydantic Models**: Use for configuration and data validation
5. **No Circular Imports**: Utils must not import from agents/cli/tools

## Code Examples

### Agent Base Class

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class Agent(ABC):
    def __init__(self, env: AgentEnv) -> None:
        self.env = env

    @abstractmethod
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute agent logic. Override in subclasses."""
        ...
```

### Config Loading

```python
from pydantic import BaseModel
from pathlib import Path
import yaml

class DeepPresenterConfig(BaseModel):
    model_config: dict[str, Any]
    workspace_base: Path

def load_config(path: Path) -> DeepPresenterConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return DeepPresenterConfig(**data)
```

## Anti-Patterns

- ❌ Do NOT import CLI commands from tools or agents
- ❌ Do NOT put agent logic in utils modules
- ❌ Do NOT bypass the Agent base class for new agents
- ❌ Do NOT use global mutable state in utils