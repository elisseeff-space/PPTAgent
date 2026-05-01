# PPTAgent / DeepPresenter — QWEN.md

## Project Overview

**PPTAgent** is an agentic AI framework for automated PowerPoint generation from documents, prompts, or research. The project has evolved through two major versions:

- **PPTAgent** (original): Template-based, edit-driven presentation generation accepted at EMNLP 2025. Uses layout induction, document parsing, and PPTEval evaluation.
- **DeepPresenter** (current): Agent-based system with deep research integration, free-form visual design, autonomous asset creation, text-to-image generation, and a sandboxed agent environment with 20+ MCP tools. Accepted at ACL 2026.

The repository ships both codepaths in a single package (`pptagent` on PyPI):
- `deeppresenter/` — the active runtime, CLI, multi-agent loop, MCP tool wiring, and HTML-to-PPTX pipeline.
- `pptagent/` — the legacy generation library, still used for the `pptagent-mcp` MCP server entrypoint.

### Key Technologies

- **Python 3.11+** with `uv` package manager
- **LLM integration**: OpenAI-compatible APIs (configurable base_url/model per agent)
- **Agent framework**: Custom async agent loop with MCP-style tool calling
- **Frontend**: Gradio web UI (`webui.py`), Typer CLI
- **Conversion**: Playwright for HTML→PDF, Node.js for HTML→PPTX
- **Sandbox**: Docker containers (`deeppresenter-sandbox`, `deeppresenter-host`)
- **Fine-tuned models**: DeepPresenter-9B available on HuggingFace/ModelScope

### Architecture

```
CLI (pptagent) → AgentLoop → Research Agent → PPTAgent/Design Agent → Export
                    ↓
              AgentEnv (MCP tool registry)
                    ↓
         Tools: search, research, reflect, any2markdown, task, sandbox
```

The `AgentLoop.run()` orchestrates:
1. **Optional Planner** — generates outline
2. **Research** — builds manuscript from prompt + attachments using web search, paper search, file conversion
3. **Generation** — either `PPTAgent` (template-driven) or `Design` (free-form HTML slides)
4. **Export** — HTML→PPTX via Node.js or fallback to PDF via Playwright

## Building and Running

### Prerequisites

- Python 3.11+, `uv`, Node 18+, Docker, Playwright browsers
- LLM API credentials (configured via `pptagent onboard` or manually in config files)

### Setup

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

### Configuration

```bash
# Interactive setup (CLI mode)
uvx pptagent onboard

# Or manual config
cp deeppresenter/config.yaml.example deeppresenter/config.yaml
cp deeppresenter/mcp.json.example deeppresenter/mcp.json
```

Key config files:
- `deeppresenter/config.yaml` — LLM credentials per agent, offline mode, context folding
- `deeppresenter/mcp.json` — MCP tool server definitions (search, research, sandbox, etc.)

### Running

```bash
# CLI generation
uvx pptagent generate "Your prompt here" -o output.pptx

# With attachments
uvx pptagent generate "Q4 Report" -f data.xlsx -f charts.pdf -o report.pptx

# Start local inference service
uvx pptagent serve

# Web UI (development)
python webui.py

# Docker Compose (server deployment)
docker compose up -d
# Service available at http://localhost:7861

# MCP server (legacy)
pptagent-mcp
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with specific markers
uv run pytest -m "not llm and not parse"  # skip tests requiring API keys

# Test markers:
#   llm     — requires OPENAI_API_KEY
#   parse   — requires minerU API
#   asyncio — async tests
```

### Linting & Formatting

```bash
uv run ruff check --fix && uv run ruff format
```

### Building Package

```bash
uv build
```

## Development Conventions

### Code Style

- Type hints on all functions/methods
- English for comments and documentation
- Minimal exception handling — no control flow via try/except
- Modern Python: use `pathlib`, `model_dump()`, f-strings
- Ruff for linting (ignores: F403, F405, E741, E722)
- pyupgrade via pre-commit

### Architecture Principles

- **Good taste first**: restructure to eliminate edge cases, not add conditionals
- **Pragmatism**: solve real problems, not hypothetical ones
- **Simplicity**: max 3 indentation levels; short focused functions
- **Fewer dependencies**: prefer less code

### File Organization

- `deeppresenter/` — primary product surface (CLI, agents, tools, utils)
- `pptagent/` — legacy generation library (keep changes scoped unless task spans both)
- Tests: `pptagent/test/` (unit) and `deeppresenter/test/` (integration)
- Config templates: `*.example` files, never commit real credentials
- Workspaces: `~/.cache/deeppresenter/<session_id>/` (override via `DEEPPRESENTER_WORKSPACE_BASE`)

### Key Patterns

- Agents extend `deeppresenter.agents.agent.Agent` base class
- Tools are MCP-style servers defined in `deeppresenter/mcp.json`
- Config loaded via `deeppresenter.utils.config.DeepPresenterConfig`
- Async generator pattern for streaming agent output
- `InputRequest` pydantic model carries prompt, attachments, conversion type

## Important Notes

- **Windows not supported** — use WSL if on Windows
- **Stale documentation**: README may reference old paths; verify files exist
- **Two codepaths**: `deeppresenter` and `pptagent` are related but independent; changing one doesn't update the other
- **Docker required**: sandbox image is a runtime dependency, not optional
- **Optional services** for quality: Tavily (search), MinerU (PDF parsing), T2I model (image generation)
- **Offline mode**: set `offline_mode: true` in config and deploy MinerU locally
