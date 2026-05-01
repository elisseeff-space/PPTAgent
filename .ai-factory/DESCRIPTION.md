# PPTAgent / DeepPresenter — Project Description

## Overview

PPTAgent is an agentic AI framework for automated PowerPoint generation from documents, prompts, or research. The project has evolved through two major versions shipped in a single package:

- **PPTAgent** (legacy): Template-based, edit-driven presentation generation accepted at EMNLP 2025. Uses layout induction, document parsing, and PPTEval evaluation.
- **DeepPresenter** (active): Agent-based system with deep research integration, free-form visual design, autonomous asset creation, text-to-image generation, and a sandboxed agent environment with 20+ MCP tools. Accepted at ACL 2026.

## Core Features

- Multi-agent research loop (planner → research → generation → export)
- Template-driven slide generation (PPTAgent legacy path)
- Free-form HTML slide design with browser conversion (DeepPresenter)
- Web search, paper search, and document parsing integration
- Docker-sandboxed agent execution environment
- MCP tool architecture for extensible agent capabilities
- Gradio web UI and Typer CLI
- Fine-tuned DeepPresenter-9B model available on HuggingFace/ModelScope

## Tech Stack

- **Programming language:** Python 3.11+
- **Package manager:** uv
- **CLI framework:** Typer
- **Web framework:** FastAPI, Gradio
- **Agent architecture:** Custom async agent loop with MCP-style tool calling
- **Browser automation:** Playwright (HTML→PDF conversion)
- **HTML→PPTX:** Node.js conversion pipeline
- **Containerization:** Docker (sandbox and host images)
- **LLM integration:** OpenAI-compatible APIs (configurable base_url/model)
- **Testing:** pytest with async support, test markers (llm, parse, asyncio)
- **Linting:** Ruff, pyupgrade via pre-commit

## Architecture Notes

### Dual Codepaths

The repository ships both `deeppresenter/` (active) and `pptagent/` (legacy) in a single package:

- `deeppresenter/` — CLI, agent loop, MCP tools, HTML-to-PPTX pipeline
- `pptagent/` — Template-based generation library, MCP server entrypoint

### Agent Architecture

```
CLI (pptagent) → AgentLoop → Research Agent → PPTAgent/Design Agent → Export
                    ↓
              AgentEnv (MCP tool registry)
                    ↓
         Tools: search, research, reflect, any2markdown, task, sandbox
```

### Key Components

- **Agents:** Extend `deeppresenter.agents.agent.Agent` base class
- **Tools:** MCP-style servers defined in `deeppresenter/mcp.json`
- **Config:** Loaded via `deeppresenter.utils.config.DeepPresenterConfig`
- **Workspaces:** `~/.cache/deeppresenter/<session_id>/` (override via `DEEPPRESENTER_WORKSPACE_BASE`)
- **Export:** HTML→PPTX via Node.js or HTML→PDF via Playwright

## Non-Functional Requirements

- **Logging:** Configurable via `DEEPPRESENTER_LOG_LEVEL` (0=debug, 10=info, 20=warning)
- **Error handling:** Minimal exception handling — no control flow via try/except
- **Security:** Docker sandbox for agent execution, no Windows support (WSL required)
- **Runtime dependencies:** Playwright browsers, Docker, Node 18+
- **Optional services:** Tavily (search), MinerU (PDF parsing), T2I model (image generation)
- **Offline mode:** Set `offline_mode: true` in config and deploy MinerU locally

## Architecture

For detailed architecture guidelines, see [.ai-factory/ARCHITECTURE.md](ARCHITECTURE.md).

**Pattern:** Modular Monolith
