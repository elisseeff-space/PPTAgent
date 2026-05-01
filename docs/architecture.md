[← Deployment](deployment.md) · [Back to README](../README.md) · [Contributing →](contributing.md)

# Architecture

Project structure, agent architecture, and design patterns for PPTAgent / DeepPresenter.

## Overview

PPTAgent is an agentic AI framework for automated PowerPoint generation. The project evolved through two major versions shipped in a single package:

- **PPTAgent** (legacy): Template-based, edit-driven presentation generation (EMNLP 2025)
- **DeepPresenter** (active): Agent-based system with deep research integration (ACL 2026)

## Architecture Pattern: Modular Monolith

The project uses a modular monolith architecture — a single Python package with strong module boundaries separating concerns. This supports both codepaths while keeping deployment simple.

## Directory Structure

```
PPTAgent/
├── deeppresenter/              # Active product surface (primary)
│   ├── agents/                 # Agent classes
│   │   ├── agent.py            # Base Agent with MCP tool loop
│   │   ├── research.py         # Research agent
│   │   ├── design.py           # Design agent (free-form HTML)
│   │   ├── pptagent.py         # Template-driven generation
│   │   ├── planner.py          # Outline planner
│   │   ├── subagent.py         # Sub-agent delegation
│   │   └── env.py              # AgentEnv (MCP tool registry)
│   ├── cli/                    # Typer CLI commands
│   │   ├── commands.py         # onboard, generate, serve, config
│   │   ├── common.py           # Shared CLI helpers
│   │   └── model.py            # Model serving CLI
│   ├── tools/                  # MCP-style tool servers
│   │   ├── search.py           # Web/paper search
│   │   ├── research.py         # Research tools
│   │   ├── reflect.py          # Reflection tool
│   │   ├── any2markdown.py     # File conversion
│   │   └── task.py             # Task management
│   ├── utils/                  # Shared utilities
│   │   ├── config.py           # DeepPresenterConfig
│   │   ├── log.py              # Custom logging
│   │   ├── webview.py          # Playwright HTML→PDF
│   │   └── mcp_client.py       # MCP client
│   ├── html2pptx/              # Node.js HTML→PPTX
│   ├── docker/                 # Dockerfiles
│   ├── roles/                  # Agent role definitions (YAML)
│   ├── test/                   # Integration tests
│   └── main.py                 # AgentLoop orchestration
├── pptagent/                   # Legacy generation library
│   ├── document/               # Document parsing
│   ├── presentation/           # Slide generation
│   ├── templates/              # PPTX templates
│   ├── mcp_server.py           # MCP server entrypoint
│   └── test/                   # Unit tests
├── docs/                       # Documentation
├── pyproject.toml              # Package metadata
├── docker-compose.yml          # Docker Compose
└── webui.py                    # Gradio web UI
```

## Agent Architecture

```
CLI (pptagent) → AgentLoop → Research Agent → PPTAgent/Design Agent → Export
                    ↓
              AgentEnv (MCP tool registry)
                    ↓
         Tools: search, research, reflect, any2markdown, task, sandbox
```

### Agent Flow

1. **Planner** (optional) — Generates outline from prompt
2. **Research** — Builds manuscript using web search, paper search, file conversion
3. **Generation** — Either `PPTAgent` (template-driven) or `Design` (free-form HTML)
4. **Export** — HTML→PPTX via Node.js or HTML→PDF via Playwright

### Key Components

- **Agents:** Extend `deeppresenter.agents.agent.Agent` base class
- **Tools:** MCP-style servers defined in `deeppresenter/mcp.json`
- **Config:** Loaded via `deeppresenter.utils.config.DeepPresenterConfig`
- **Workspaces:** `~/.cache/deeppresenter/<session_id>/` (override via `DEEPPRESENTER_WORKSPACE_BASE`)

## Dependency Rules

- ✅ `deeppresenter.agents` → `deeppresenter.tools` (agents call tools)
- ✅ `deeppresenter.cli` → `deeppresenter.main` → `deeppresenter.agents` (CLI orchestrates)
- ✅ `deeppresenter.utils` → external packages only
- ✅ `pptagent/` → independent (legacy, keep changes scoped)
- ❌ Cross-imports between `pptagent/` and `deeppresenter/` (independent codepaths)

## Design Principles

1. **Good taste first:** Restructure to eliminate edge cases, not add conditionals
2. **Pragmatism:** Solve real problems, not hypothetical ones
3. **Simplicity:** Max 3 indentation levels; short focused functions
4. **Fewer dependencies:** Prefer less code

## Code Style

- Type hints on all functions/methods
- English for comments and documentation
- Minimal exception handling — no control flow via try/except
- Modern Python: `pathlib`, `model_dump()`, f-strings
- Ruff for linting (ignores: F403, F405, E741, E722)

## See Also

- [Getting Started](getting-started.md) — Installation and setup
- [Configuration](configuration.md) — Config files and environment variables
- [Contributing](contributing.md) — Development workflow and conventions
