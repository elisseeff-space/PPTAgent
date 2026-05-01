# Replace SerpAPI with Yandex AI Studio Search

**Branch:** `feature/replace-serpapi-with-yandex-search`
**Date:** 2026-05-01
**Mode:** Full

## Settings

| Setting | Value |
|---------|-------|
| Testing | No (skipped by user) |
| Logging | Verbose (DEBUG level) |
| Docs | Yes — mandatory docs checkpoint |

## Overview

Replace the SerpAPI (Google Search) backend in the DeepPresenter search tools with Yandex AI Studio Search API. The tool interface (`search_web`, `search_images`) must remain unchanged — agents consume the same output format regardless of backend.

## Affected Files

| File | Change |
|------|--------|
| `deeppresenter/tools/search.py` | Replace SerpAPI HTTP client with Yandex Search API client; update env var loading; keep tool signatures identical |
| `deeppresenter/mcp.json.example` | Replace `SERPAPI_KEY` env var with Yandex auth credential |
| `deeppresenter/cli/commands.py` | Update onboarding prompt from "SerpAPI key for Google web search" to Yandex equivalent |

## Research Context

- **Current backend:** SerpAPI (`serpapi.com/search`) via GET request with `api_key` query param. Supports `search_web` (Google web) and `search_images` (Google Images).
- **Priority:** SerpAPI takes priority over Tavily — if `GOOGLE_KEYS` env var is set, SerpAPI tools are registered; otherwise Tavily tools.
- **Output contract:** `search_web` returns `{query, total_results, results: [{title, url, displayed_link, content}]}`. `search_images` returns `{query, total_results, images: [{url, thumbnail, description}]}`.
- **Yandex AI Studio Search API:** User-provided docs at https://aistudio.yandex.ru/docs/ru/search-api/operations/web-search-sync.html. Authentication and exact endpoint need verification from docs (IAM token or API key).

## Tasks

### Task 1: Research Yandex AI Studio Search API contract

- [x]

**Goal:** Understand the exact API contract before writing code.

**Actions:**
1. Fetch and document from https://aistudio.yandex.ru/docs/ru/search-api/operations/web-search-sync.html:
   - Base endpoint URL
   - Authentication method (IAM token in header? API key? Service account?)
   - HTTP method (GET vs POST)
   - Request body/query parameters format
   - Response JSON structure (field names for title, URL, snippet, etc.)
   - Rate limits and error codes
2. Determine if Yandex AI Studio Search supports image search, or if `search_images` needs a different approach (fallback to Tavily, skip image search, etc.)
3. Write findings to a short design note (inline in code comments or a brief doc).

**Logging:** Add DEBUG logs documenting the API contract decision.

**Deliverable:** A clear API contract summary that informs Task 2 implementation.

---

### Task 2: Replace SerpAPI HTTP client in `search.py`

- [x]

**Goal:** Replace `_serpapi_request()` with a Yandex Search API client.

**File:** `deeppresenter/tools/search.py`

**Actions:**
1. Replace `GOOGLE_KEYS` env var loading with `YANDEX_*` env var(s) (determined by Task 1 — likely `YANDEX_IAM_TOKEN` or `YANDEX_API_KEY`).
2. Replace `SERPAPI_URL` constant with Yandex endpoint.
3. Replace `_serpapi_request()` with `_yandex_search_request(params: dict) -> dict`:
   - Use correct HTTP method (GET/POST)
   - Set correct auth headers
   - Handle error responses with WARNING logs
   - Keep the same async aiohttp pattern
4. Update the debug log at module load to reflect Yandex key loading.
5. Keep the `GOOGLE_KEYS` / `TAVILY_KEYS` conditional structure but rename for clarity (e.g., `YANDEX_KEYS` / `TAVILY_KEYS`).

**Logging requirements:**
- DEBUG: Number of Yandex keys loaded at startup
- DEBUG: Each search request (query, params, response status)
- WARNING: API errors with status code and response body

**Deliverable:** `_yandex_search_request()` function ready for tool wiring.

---

### Task 3: Update `search_web` tool to use Yandex API

- [x]

**Goal:** Rewrite `search_web()` to call Yandex Search and return the same output format.

**File:** `deeppresenter/tools/search.py`

**Actions:**
1. In the `if len(YANDEX_KEYS):` branch, rewrite `search_web()`:
   - Map `query`, `max_results`, `time_range` params to Yandex API format
   - Call `_yandex_search_request()` 
   - Map Yandex response fields to the existing output format: `{title, url, displayed_link, content}`
   - Handle missing fields gracefully (use `.get()` with defaults)
2. If Yandex API doesn't support `time_range` filtering, log a DEBUG note and pass through without the filter.
3. Keep the `search_web` signature and docstring identical (agents depend on this).

**Logging requirements:**
- DEBUG: Entry with query, max_results, time_range
- DEBUG: Number of results mapped
- WARNING: If response structure is unexpected (missing expected fields)

**Deliverable:** `search_web()` tool wired to Yandex, same MCP interface.

---

### Task 4: Handle `search_images` tool

- [x]

**Goal:** Decide and implement image search strategy.

**File:** `deeppresenter/tools/search.py`

**Actions:**
1. Based on Task 1 research, determine if Yandex AI Studio Search supports image search.
2. If YES: Implement `search_images()` using Yandex image search API, mapping response to `{url, thumbnail, description}`.
3. If NO: Option A — Fall back to Tavily for images only (if `TAVILY_KEYS` is set). Option B — Return empty results with a DEBUG log noting image search unavailable. Option C — Use Yandex Image Search as a separate endpoint if available.
4. Choose the best approach based on research and implement it.

**Logging requirements:**
- DEBUG: Image search strategy chosen and why
- WARNING: If image search returns no results

**Deliverable:** `search_images()` tool with working implementation or graceful fallback.

---

### Task 5: Update `mcp.json.example` configuration

- [x]

**Goal:** Replace SerpAPI env var with Yandex auth credential in the MCP config template.

**File:** `deeppresenter/mcp.json.example`

**Actions:**
1. In the `search` server definition, replace:
   ```json
   "SERPAPI_KEY": "your_seriapi_api_key_here"
   ```
   with the Yandex equivalent (determined by Task 1, e.g.):
   ```json
   "YANDEX_IAM_TOKEN": "your_yandex_iam_token_here"
   ```
2. Keep `TAVILY_API_KEY` unchanged (it's the fallback backend).

**Logging:** N/A (config file change).

**Deliverable:** Updated `mcp.json.example` with Yandex credential placeholder.

---

### Task 6: Update onboarding CLI prompt

- [x]

**Goal:** Replace SerpAPI onboarding prompt with Yandex prompt.

**File:** `deeppresenter/cli/commands.py`

**Actions:**
1. Find the SerpAPI onboarding block (around line 239-247):
   ```python
   if Confirm.ask("Configure SerpAPI key for Google web search?", default=False):
   ```
2. Replace with Yandex equivalent:
   ```python
   if Confirm.ask("Configure Yandex AI Studio Search API key?", default=False):
       yandex_key = Prompt.ask("Yandex API key / IAM token", password=True)
       for server in mcp_data:
           if server.get("name") == "search":
               server["env"]["YANDEX_IAM_TOKEN"] = yandex_key  # or appropriate key name
               break
   ```
3. Keep Tavily onboarding unchanged.

**Logging:** N/A (CLI prompt change).

**Deliverable:** Updated onboarding flow prompts for Yandex credential.

---

### Task 7: Lint, format, and verify

- [x]

**Goal:** Ensure code quality and no regressions.

**Actions:**
1. Run `uv run ruff check --fix && uv run ruff format`
2. Verify `deeppresenter/tools/search.py` has no lint errors
3. Verify the tool interface is unchanged (same function signatures, same output dict structure)
4. Run existing tests (if any) with `uv run pytest -m "not llm and not parse"`

**Logging:** N/A (verification step).

**Deliverable:** Clean lint, passing tests, verified interface compatibility.

---

## Commit Plan

| Commit | Tasks | Message |
|--------|-------|---------|
| 1 | Task 1 | `docs: research Yandex AI Studio Search API contract` |
| 2 | Tasks 2-4 | `feat: replace SerpAPI with Yandex Search in search tools` |
| 3 | Tasks 5-6 | `chore: update config and onboarding for Yandex Search` |
| 4 | Task 7 | `chore: lint, format, and verify search module` |

## Notes

- **Backward compatibility:** The MCP tool interface (`search_web`, `search_images`) must not change. Agents consume the output dict format — any field rename breaks the research agent.
- **Tavily fallback:** Keep Tavily as the secondary backend. The priority should be: Yandex > Tavily (same pattern as current SerpAPI > Tavily).
- **No cross-codepath changes:** Only `deeppresenter/` is affected. `pptagent/` is independent and should not be touched.
- **Yandex docs access:** The API docs at aistudio.yandex.ru may require authentication. If the docs are inaccessible, the implementer should ask for the API contract details directly.
