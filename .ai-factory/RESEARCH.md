# Research

Updated: 2026-05-01 00:00
Status: active

## Active Summary (input for /skills aif-plan)
<!-- aif:active-summary:start -->
Topic: Human-in-the-Loop Presentation Creation Architecture
Goal: Create technical description of full presentation generation pipeline with human-in-the-loop principle, where each phase requires human verification and can be iterated
Constraints: Explore mode — no implementation, only analysis and documentation
Decisions:
- Marimo Notebook as interactive UI with reactive cells
- Per-slide subfolders in workspace for each phase
- Versioned artifacts (v1/, v2/, ...) — never overwrite
- Slide status: Active/Removed — removed slides preserved, not deleted
- Partial approval — approve some slides, revise others
- Per-slide granularity for revision in all phases
- Outline and Manuscript fully editable: add/remove/reorder slides at any time
- Human-Directed Research (Model B): human directs every search query, AI executes + presents, human selects results
- Yandex Search API as search backend (not Google or Tavily)
- No Docker sandbox — Marimo-only execution (removed Docker, DesktopCommanderMCP, container lifecycle)
- Manuscript always considered in its entirety — no per-slide status, changes propagate to affect other slides
- Unified chat: one underlying LLM conversation, per-slide views are convenient representations
- Per-phase model selectors with auto-fallback (3 errors → auto, 3 more → local LM Studio)
- Export formats: PPTX (editable text), HTML (standalone), PDF (fallback)
- Strict phase gates: all slides complete Phase N before any slide starts Phase N+1
- Add slide: complete generation (Outline + Manuscript + Slide), unique ID + order_number, renumber affected slides
- Minimal reactivity, but manuscript always current (bidirectional sync with slides)
Open questions:
- Should removed slides be visible by default or hidden?
- How to handle CJK fonts in PPTX export?
- What's the HTML export structure (single file vs. per-slide)?
- How to implement bidirectional sync between manuscript and slides?
Success signals: Complete technical description document with mermaid diagrams, ready for implementation planning
Next step: Refine design, discuss edge cases, then create implementation plan via /skills aif-plan
<!-- aif:active-summary:end -->

## Sessions
<!-- aif:sessions:start -->
### 2026-05-01 00:00 — Presentation Creation Algorithm Architecture Mapping
What changed: Initial exploration of the full DeepPresenter presentation generation pipeline
Key notes:
- Mapped the complete AgentLoop.run() flow: Planner → Research → Generation (PPTAgent/Design) → Export
- Identified 7 MCP servers: any2markdown, task, deeppresenter, tool_agents, research, search, sandbox
- Documented context folding mechanism (keep head 10 + tail 4, summarize middle)
- Two generation modes: PPTAgent (legacy, template-based) vs Design (active, HTML/CSS free-form)
- Export pipeline: html2pptx Node.js (primary) → Playwright PDF (fallback)
Links (paths):
- `deeppresenter/main.py` — AgentLoop orchestration
- `deeppresenter/agents/agent.py` — Base Agent class, chat/action/execute/compact_history
- `deeppresenter/agents/planner.py` — Planner agent loop
- `deeppresenter/agents/research.py` — Research agent loop
- `deeppresenter/agents/design.py` — Design agent loop
- `deeppresenter/agents/pptagent.py` — PPTAgent (legacy) loop
- `deeppresenter/agents/env.py` — AgentEnv, MCP server management, tool execution
- `deeppresenter/roles/*.yaml` — System prompts for each agent
- `deeppresenter/tools/*.py` — MCP tool servers
- `deeppresenter/utils/webview.py` — PlaywrightConverter, html2pptx bridge
- `deeppresenter/mcp.json.example` — MCP server configuration
- `deeppresenter/config.yaml.example` — LLM config per agent

### 2026-05-01 00:00 — Human-in-the-Loop Architecture Design
What changed: Designed HITL pipeline architecture with per-slide lifecycle, versioning, slide management, human-directed research, Marimo-only execution, and all clarifications
Key notes:
- Created `hitl-presentation-architecture.md` with complete technical description
- Pipeline state machine with approve/partial/regenerate transitions per phase
- Per-slide lifecycle: Pending → Generated → Approved/Revision Requested → Locked
- Slide status: Active/Removed (never delete, always mark)
- Workspace structure: per-slide subfolders with versioned artifacts
- Marimo Notebook UI with reactive cells, per-slide cards, chat integration
- Slide management: add (AI/manual/duplicate/import), remove, restore, reorder
- Metadata schemas: global + per-slide with status tracking
- API surface: SlideManager, VersionManager, AgentOrchestrator, SearchManager interfaces
- Human-Directed Research (Model B): human directs every search query, AI executes and presents, human selects
- Yandex Search API as search backend (not Google or Tavily)
- Search modes: Full Human-Directed (default), Attachments Only, Offline Mode
- Execution model: Marimo-only (no Docker sandbox, no DesktopCommanderMCP)
- Agent generates code/artifacts, human executes in Marimo's reactive environment
- Removed dependencies: Docker, deeppresenter-sandbox, deeppresenter-host, container lifecycle
- Manuscript always considered in its entirety — no per-slide status, changes propagate
- Unified chat: one underlying LLM conversation, per-slide views are convenient representations
- Per-phase model selectors with auto-fallback (3 errors → auto, 3 more → local LM Studio)
- Export formats: PPTX (editable text), HTML (standalone), PDF (fallback)
- Strict phase gates: all slides complete Phase N before any slide starts Phase N+1
- Add slide: complete generation (Outline + Manuscript + Slide), unique ID + order_number, renumber affected slides
- Minimal reactivity, but manuscript always current (bidirectional sync with slides)
- Key insight: removed slides preserve all artifacts, can be restored at any time
Links (paths):
- `hitl-presentation-architecture.md` — Full technical description with mermaid diagrams
<!-- aif:sessions:end -->
