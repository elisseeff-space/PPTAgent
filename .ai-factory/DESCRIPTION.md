# PPTAgent Project Specification

## Overview

An agentic PowerPoint generation system that uses AI to create presentations from research prompts, web content, and document inputs. The system supports both template-based generation (via `pptagent/`) and HTML-to-PPTX pipeline (via `deeppresenter/`).

## Core Features

- **Research Agent**: Gathers information from web search, research papers, and document parsing
- **PPT Generation**: AI-driven slide content generation from markdown manuscripts
- **Design Agent**: Generates HTML slides and converts to PPTX via browser automation
- **CLI Interface**: Typer-based command-line interface
- **MCP Server**: FastMCP-based server for programmatic access
- **Web UI**: Gradio-based web interface

## Tech Stack

- **Programming Language**: Python 3.11+
- **Framework**: FastAPI, Typer, Gradio
- **Database**: None (file-based)
- **ORM**: N/A
- **AI Integration**: OpenAI API, LangChain MCP adapters

## Architecture Notes

- **Dual Codepath**: `deeppresenter/` (current runtime) and `pptagent/` (legacy library)
- **HTML Pipeline**: HTML → browser rendering → PNG → PPTX conversion
- **Agent Orchestration**: Research → PPTAgent/Design → Export flow
- **MCP Tools**: Search, research, reflection, file conversion, task management

## Directory Structure

```
deeppresenter/        - Current runtime (CLI, agents, tools)
├── agents/           - Agent implementations
├── cli/              - Typer CLI commands
├── tools/             - MCP tool servers
├── utils/             - Shared utilities
└── html2pptx/        - Node-based conversion

pptagent/              - Legacy core library
└── mcp_server.py      - FastMCP server

.ai-factory/          - AI Factory context (this setup)
├── config.yaml       - Configuration
├── rules/base.md     - Base conventions
└── *.md             - Other artifacts

AGENTS.md             - Project map for AI agents
pyproject.toml        - Package metadata
```