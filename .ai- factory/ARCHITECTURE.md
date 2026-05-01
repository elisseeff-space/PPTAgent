# Architecture: Modular Monolith
## Overview
The project is organized as a single Python package (`deeppresenter/`) with strong internal module boundaries, plus a co-located legacy library (`pptagent/`). The architecture follows the **Modular Monolith** pattern: agents, CLI, tools, and utilities are separate modules under one deployable package, enabling clear boundaries without the operational overhead of microservices. The legacy `pptagent/` is maintained as a separate concern with its own internal structure and is not subject to the rules of the main `deeppresenter/` package.
## Decision Rationale
- **Project type:** AI agentic CLI tool / multi-agent pipeline
- **Tech stack:** Python 3.11+, Typer (CLI), Pydantic (config), Docker + Playwright (conversion), MCP tools
- **Key factor:** Agent orchestration is inherently sequential (Research → PPTAgent/Design → Export), not independently scalable. Strong module boundaries prevent tight coupling between agents without requiring separate services.
## Folder Structure
```
deeppresenter/                # Primary runtime — Modular Monolith
├── __init__.py              # Package entry
├── __main__.py             # python -m entry
├── main.py                  # Orchestration: AgentLoop (composition root)
│
├── agents/                  # Domain + Application — core agent logic
│   ├── agent.py            # Base Agent: chat, action, execute, compact
│   ├── env.py            # AgentEnv: tool registry + MCP client wiring
│   ├── research.py       # Research(Agent)
│   ├── design.py        # Design(Agent)
│   ├── pptagent.py     # PPTAgent(Agent)
│   ├── planner.py     # Planner(Agent)
│   ├── subagent.py     # SubAgent: multiagent delegation
│   └── __init__.py
│
├── cli/                    # Presentation — Typer commands
│   ├── commands.py      # onboard, generate, serve, config, clean
│   ├── common.py        # Shared constants
│   ├── dependency.py  # Runtime checks
│   ├── model.py       # Local model setup
│   └── __init__.py
│
├── tools/                  # Infrastructure — MCP tool servers
│   ├── search.py      # Web search
│   ├── research.py    # Research tools
│   ├── reflect.py    # Reflection tools
│   ├── task.py       # Task management
│   ├── any2markdown.py  # MinerU document parser
│   ├── tool_agents.py  # Agent delegation tool
│   └── __init__.py
│
├── utils/                  # Shared kernel
│   ├── config.py     # DeepPresenterConfig, LLM, Endpoint
│   ├── typings.py    # ChatMessage, InputRequest, Role, MCPServer
│   ├── constants.py  # PACKAGE_DIR, WORKSPACE_BASE, prompts
│   ├── log.py      # Logging
│   ├── webview.py  # PlaywrightConverter
│   ├── mcp_client.py  # MCPClient
│   ├── mineru_api.py  # MinerU API
│   ├── outline.py   # Outline schema
│   ├── pdf2longimage.py
│   └── __init__.py
│
├── html2pptx/           # Infrastructure — Node.js conversion
├── roles/              # Domain — YAML role configs
├── config.yaml.example  # Config template
├── mcp.json.example   # MCP template
├── serve.sh           # Dev script
└── docker/            # Sandbox Docker image
pptagent/              # Legacy library — separate concern
├── agent.py          # Legacy base agent
├── pptgen.py         # Core generation
├── induct.py        # Layout induction
├── ppteval.py      # Evaluation
├── document/       # Document parsing
├── presentation/   # Presentation model
├── templates/     # PPT templates
├── prompts/        # Legacy prompts
├── mcp_server.py   # FastMCP server
└── test/          # Tests
```
## Dependency Rules
The rules apply to `deeppresenter/` only. `pptagent/` is maintained independently.
```
cli/ ────────> main.py ────────> agents/
                                   |
                  tools/             utils/
                                   |
                              (shared kernel)
```
- ✅ `cli/` → `main.py`, `utils/`
- ✅ `agents/` → `utils/`, `roles/`
- ✅ `agents/` → `pptagent/` (legacy library only when needed)
- ✅ `tools/` → `utils/`
- ✅ `main.py` → `agents/`, `utils/`, `roles/`
- ❌ `utils/` → `agents/` (shared kernel must not know agents)
- ❌ `utils/` → `cli/` (shared kernel must not know CLI)
- ❌ `agents/` → `cli/` (agents must not know CLI commands)
- ❌ `cli/` → `tools/` (CLI must not call tool servers directly)
- ❌ Circular deps between any modules
### pptagent/ (Legacy) Rules
- `pptagent/` is treated as an **external dependency** for `deeppresenter/`
- Import only via public API: `from pptagent import SomePublicClass`
- Do not reach into `pptagent/` internals from `deeppresenter/` agents
- `pptagent/mcp_server.py` is independently deployed and managed
## Layer/Module Communication
### Agent Orchestration (main.py / AgentLoop)
`AgentLoop` is the **composition root**. It wires agents, config, and workspace:
```python
# main.py
class AgentLoop:
    async def run(self, request: InputRequest, ...) -> AsyncGenerator[str | ChatMessage, None]:
        async for msg in self.research_agent.loop(request, outline):
            yield msg
```
### Tool Execution (agents/env.py)
`AgentEnv` is the **tool registry**:
```python
# agents/env.py
class AgentEnv:
    async def connect_server(self, server: MCPServer) -> None: ...
    def register_tool(self, func: Callable) -> None: ...
    async def tool_execute(self, tool_ call: ToolCall) -> ChatMessage: ...
```
### Agent Base Interface
```python
# agents/agent.py
class Agent:
    async def loop(self, req: InputRequest, *args, **kwargs) -> AsyncGenerator[str | ChatMessage]: ...
    async def finish(self, result: str) -> None: ...
```
## Key Principles
1. **Shared kernel has no upward dependencies.** `utils/` is the lowest layer and must not import from `agents/`, `cli/`, or `tools/`.
2. **Agents own their toolset.** Each agent declares its toolset via `AgentEnv` (registered in `main.py`). Agents do not instantiate tool servers directly.
3. **CLI is a thin presentation layer.** `cli/` only imports from `main.py` and `utils/`. Business logic lives in agents, not commands.
4. **One composition root.** All agent instantiation and wiring happens in `AgentLoop` (`main.py`). No module should create agent instances independently.
5. **Tool servers are infrastructure.** `tools/` implements MCP tool servers using FastMCP. It does not contain business logic.
6. **Roles are data.** `roles/*.yaml` are loaded by the `Agent` base class. Agents do not hard-code system prompts.
7. **Async throughout.** The entire agent pipeline is async (`async for`, `await`). Blocking I/O must not enter agent loops.
8. **No database.** Outputs are files (PPTX, markdown, HTML, JSON). State lives in the workspace directory, not a DB.
## Code Examples
### Correct Tool Registration
```python
# agents/subagent.py
class SubAgent:
    @staticmethod
    def delegate(config: DeepPresenterConfig, agent_env: AgentEnv,
                 workspace: Path, language: Literal["zh", "en"]]) -> Callable:
        async def _delegate(request: dict) -> str: ...
        return _delegate
# main.py — registered in AgentLoop
self.agent_env.register_tool(
    SubAgent.delegate(self.config, agent_env, self.workspace, self.language)
)
```
### Correct Config Access in Agent
```python
# agents/agent.py
class Agent:
    def __init__(self, config: DeepPresenterConfig, ...):
        self.llm: LLM = config[self.role_config.use_model]  # via __getitem__
```
### Shared Kernel — Logging (no upward deps)
```python
# utils/log.py
def debug(msg: str) -> None: ...
def timer(name: str): ...  # context manager
```
### CLI — Thin Presentation
```python
# cli/commands.py
from deeppresenter.main import AgentLoop, InputRequest
from deeppresenter.utils.config import DeepPresenterConfig
async def run():
    loop = AgentLoop(config=config, ...)
    async for msg in loop.run(request):
        ...
```
## Anti-Patterns
- ❌ **Creating agent instances in CLI commands.** Agents must be created in `AgentLoop`, not in `cli/commands.py`.
- ❌ **Tool servers calling LLM directly.** `tools/` implements tool logic only; LLM calls belong in agents.
- ❌ **Importing agent base in utils.** `utils/` must not import `from deeppresenter.agents.agent`.
- ❌ **Hard-coding system prompts.** Prompts go in `roles/*.yaml`, loaded at agent init time.
- ❌ **Synchronous blocking I/O in agent loops.** Use `asyncio` throughout.
- ❌ **Reaching into pptagent internals.** Import only via public API.
