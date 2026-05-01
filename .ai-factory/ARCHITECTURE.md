# Architecture: Modular Monolith

## Overview

PPTAgent/DeepPresenter uses a modular monolith architecture — a single Python package with strong module boundaries separating concerns. This pattern fits the project's dual-codepath nature (legacy `pptagent/` and active `deeppresenter/`) while keeping deployment simple and future extraction ready.

The architecture supports both template-based slide generation (PPTAgent) and agent-based generation (DeepPresenter) within the same package, with clear boundaries between agents, tools, utilities, and export pipelines.

## Decision Rationale

- **Project type:** Agentic AI framework for PowerPoint generation
- **Tech stack:** Python 3.11+, uv, Typer CLI, FastAPI, Gradio, Docker
- **Key factor:** Dual codepaths with different complexity levels require strong module boundaries while sharing a single deployment unit (pyproject.toml, single package on PyPI)

## Folder Structure

```
PPTAgent/
├── deeppresenter/              # Active product surface (primary)
│   ├── agents/                 # Agent classes — Agent base, Research, Design, PPTAgent
│   │   ├── agent.py            # Base Agent class with MCP tool loop
│   │   ├── research.py         # Research agent — builds manuscript from prompt
│   │   ├── design.py           # Design agent — generates free-form HTML slides
│   │   ├── pptagent.py         # Template-driven generation (legacy path)
│   │   ├── planner.py          # Outline planner agent
│   │   ├── subagent.py         # Sub-agent delegation
│   │   └── env.py              # AgentEnv — MCP tool registry
│   ├── cli/                    # Typer CLI commands
│   │   ├── commands.py         # onboard, generate, serve, config, clean
│   │   ├── common.py           # Shared CLI options and helpers
│   │   └── model.py            # Model serving CLI
│   ├── tools/                  # MCP-style tool servers
│   │   ├── search.py           # Web/paper search tools
│   │   ├── research.py         # Research tool agents
│   │   ├── reflect.py          # Reflection tool
│   │   ├── any2markdown.py     # File conversion to markdown
│   │   └── task.py             # Task management
│   ├── utils/                  # Shared utilities
│   │   ├── config.py           # DeepPresenterConfig, LLM endpoint config
│   │   ├── log.py              # Custom logging wrapper (debug, info, error)
│   │   ├── constants.py        # Package-wide constants
│   │   ├── webview.py          # Playwright HTML→PDF conversion
│   │   ├── mcp_client.py       # MCP client for tool communication
│   │   └── mineru_api.py       # MinerU PDF parsing integration
│   ├── html2pptx/              # Node.js HTML→PPTX conversion
│   │   ├── html2pptx.js        # Core conversion logic
│   │   └── package.json        # Node dependencies
│   ├── docker/                 # Docker containerization
│   │   ├── Host.Dockerfile     # Host container (deeppresenter-host)
│   │   └── SandBox.Dockerfile  # Sandbox container (deeppresenter-sandbox)
│   ├── roles/                  # Agent role definitions (YAML prompts)
│   ├── test/                   # Integration tests
│   ├── main.py                 # AgentLoop orchestration entrypoint
│   └── serve.sh                # Local inference service script
├── pptagent/                   # Legacy generation library (scoped changes)
│   ├── document/               # Document parsing and processing
│   ├── presentation/           # Slide generation and layout induction
│   ├── templates/              # PPTX templates and layout definitions
│   ├── prompts/                # Generation prompts
│   ├── mcp_server.py           # MCP server entrypoint (pptagent-mcp)
│   └── test/                   # Unit tests
├── .ai-factory/                # AI Factory configuration
│   ├── config.yaml             # Language, workflow, git settings
│   ├── DESCRIPTION.md          # Project specification
│   ├── ARCHITECTURE.md         # This file
│   └── rules/                  # Project conventions
├── pyproject.toml              # Package metadata, deps, pytest config
├── docker-compose.yml          # Docker Compose for server deployment
└── webui.py                    # Gradio web UI entrypoint
```

## Dependency Rules

- ✅ `deeppresenter.agents` → `deeppresenter.tools` (agents call tools)
- ✅ `deeppresenter.agents` → `deeppresenter.utils` (agents use config, logging)
- ✅ `deeppresenter.cli` → `deeppresenter.main` → `deeppresenter.agents` (CLI orchestrates agents)
- ✅ `deeppresenter.utils` → external packages only (config, logging, constants)
- ✅ `pptagent/` → independent (legacy, keep changes scoped)
- ❌ `deeppresenter.utils` → `deeppresenter.agents` or `deeppresenter.tools` (no upward dependencies)
- ❌ `deeppresenter.tools` → `deeppresenter.agents` (tools don't call agents)
- ❌ Cross-imports between `pptagent/` and `deeppresenter/` (independent codepaths)

## Layer/Module Communication

- **Agent → Tool:** Async MCP-style tool calling via `AgentEnv` registry
- **CLI → Agent:** `AgentLoop.run()` orchestrates Research → Generation → Export
- **Agent → Agent:** Sub-agent delegation via `SubAgent` class
- **Module → Module:** Explicit public API only — no reaching into module internals
- **Python → Node:** HTML→PPTX conversion via subprocess call to Node.js pipeline

## Key Principles

1. **Good taste first:** Restructure to eliminate edge cases, not add conditionals. Max 3 indentation levels.
2. **Pragmatism:** Solve real problems in this repository, not hypothetical ones. Code serves reality.
3. **Fewer dependencies:** Prefer less code. Keep functions short and focused.
4. **Dual codepaths:** `deeppresenter` and `pptagent` are related but independent — changing one doesn't update the other.
5. **Minimal exception handling:** No control flow via try/except. Exceptions only for concrete failure modes.

## Code Examples

### Agent Base Class Pattern

```python
# deeppresenter/agents/agent.py
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from deeppresenter.utils.config import DeepPresenterConfig
from deeppresenter.utils.log import info, error

class Agent(ABC):
    """Base class for all agents with MCP tool calling loop."""
    
    def __init__(self, config: DeepPresenterConfig, env: AgentEnv):
        self.config = config
        self.env = env
    
    @abstractmethod
    async def run(self, prompt: str) -> AsyncGenerator[str, None]:
        """Execute agent logic and stream results."""
        ...
    
    async def _call_tool(self, tool_name: str, **kwargs) -> dict:
        """Call an MCP tool via the agent environment."""
        tool = self.env.get_tool(tool_name)
        if tool is None:
            error(f"Tool not found: {tool_name}")
            return {}
        return await tool.execute(**kwargs)
```

### Config Loading Pattern

```python
# deeppresenter/utils/config.py
from pydantic import BaseModel

class DeepPresenterConfig(BaseModel):
    """Runtime configuration loaded from config.yaml."""
    
    llm: LLM
    offline_mode: bool = False
    context_folding: bool = True
    
    @classmethod
    def load(cls, path: Path) -> "DeepPresenterConfig":
        """Load config from YAML file."""
        import yaml
        data = yaml.safe_load(path.read_text())
        return cls.model_validate(data)
```

### MCP Tool Server Pattern

```python
# deeppresenter/tools/search.py
from deeppresenter.utils.log import debug

async def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web for relevant information."""
    debug(f"Searching: {query}")
    # Tool implementation — calls Tavily or fallback search
    results = await _execute_search(query, max_results)
    return results
```

## Anti-Patterns

- ❌ **Adding conditionals instead of restructuring:** If you need more than 3 indentation levels, the design needs fixing
- ❌ **Defensive try/except for control flow:** Exceptions are for failure modes, not normal logic paths
- ❌ **Cross-imports between codepaths:** `pptagent/` and `deeppresenter/` are independent — don't couple them
- ❌ **Assuming README is current:** Stale documentation exists — verify files before referencing
- ❌ **Treating Docker/Playwright as optional:** These are runtime dependencies for some codepaths
- ❌ **Modifying both stacks for one change:** Keep changes scoped unless task explicitly spans both
