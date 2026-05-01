# Architecture

## Overview

DeepPresenter is an agentic PowerPoint generation system with two generation paths:

1. **DeepPresenter (primary)**: Research → Design → HTML → PPTX
2. **PPTAgent (legacy)**: Manuscript → Induct → Generate → PPTX

## Directory Structure

```
PPTAgent/
├── deeppresenter/          # Primary runtime
│   ├── agents/            # Agent implementations
│   ├── cli/             # Typer CLI commands
│   ├── tools/           # MCP-style tool servers
│   ├── utils/           # Utilities
│   ├── html2pptx/       # Node conversion helper
│   └── docker/          # Sandbox configuration
│
├── pptagent/             # Legacy library (shipped, still used)
│   ├── templates/       # PPTX templates
│   ├── prompts/         # Generation prompts
│   ├── test/           # Tests
│   └── mcp_server.py   # FastMCP entrypoint
│
└── pyproject.toml        # Package metadata
```

## Generation Pipeline

### DeepPresenter Pipeline (Design Agent)

```
Input Request
    │
    ▼
Planner (optional) → Outline
    │
    ▼
Research Agent → Manuscript (markdown)
    │
    ▼
Design Agent → Slide HTML
    │
    ▼
HTML2PPTX → PPTX/PDF
```

### PPTAgent Pipeline (Legacy)

```
Manuscript (markdown)
    │
    ▼
Induction → Layout/Template extraction
    │
    ▼
Generation → PPTX
```

## Agent Architecture

### Base Agent (`agents/agent.py`)

All agents inherit from the `Agent` base class providing:

- Tool registration and execution
- Message history management
- Async iteration interface

### Specialized Agents

| Agent | Purpose | Output |
|-------|---------|--------|
| `Planner` | Structured outline generation | JSON outline |
| `Research` | Document analysis, web search | Markdown manuscript |
| `Design` | Visual design, HTML slides | HTML directory |
| `PPTAgent` | Template-based generation | PPTX file |
| `SubAgent` | Delegated sub-tasks | Variable |

### AgentEnv (`agents/env.py`)

Runtime environment providing:

- Tool registration (`register_tool`)
- File system operations (`read_file`, `write_file`)
- Tool invocation framework

### Tool Servers (`tools/`)

| Tool | Purpose |
|------|---------|
| `search` | Web search (Tavily) |
| `research` | Academic search (arXiv, Semantic Scholar) |
| `reflect` | Self-reflection and improvement |
| `any2markdown` | Document parsing |
| `task` | Task management |
| `tool_agents` | Agent delegation |

## CLI Commands

Located in `deeppresenter/cli/commands.py`:

| Command | Description |
|---------|-------------|
| `onboard` | Interactive configuration wizard |
| `generate` | Generate presentations |
| `config` | View configuration |
| `reset` | Reset configuration |
| `serve` | Start inference service |
| `clean` | Clean workspace |

## Key Utilities

| Module | Purpose |
|--------|---------|
| `utils/config.py` | Configuration loading |
| `utils/log.py` | Logging utilities |
| `utils/webview.py` | Playwright conversion |
| `utils/mcp_client.py` | MCP client support |
| `utils/mineru_api.py` | PDF parsing |
| `utils/pdf2longimage.py` | PDF to image |

## Configuration

- **Runtime config**: `deeppresenter/config.yaml`
- **MCP config**: `deeppresenter/mcp.json`
- **CLI entrypoint**: `pptagent` → `deeppresenter.cli:main`
- **MCP entrypoint**: `pptagent-mcp` → `pptagent.mcp_server:main`

## Entry Points

```python
# CLI
pptagent = "deeppresenter.cli:main"

# MCP Server
pptagent-mcp = "pptagent.mcp_server:main"
```

## Dependencies

Core dependencies in `pyproject.toml`:

- **FastAPI**: Web framework
- **Typer**: CLI framework
- **Gradio**: Web UI
- **Playwright**: Browser automation
- **python-pptx**: PPTX generation
- **openai**: LLM integration
- **docker**: Sandbox isolation