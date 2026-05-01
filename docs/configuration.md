# Configuration Reference

## config.yaml

Runtime configuration for DeepPresenter agents.

```yaml
# DeepPresenter configuration
offline_mode: false
context_folding: true

research_agent:
  base_url: "https://openrouter.ai/api/v1"
  model: "anthropic/claude-sonnet-4-5"
  api_key: "your_key"

design_agent:
  base_url: "https://openrouter.ai/api/v1"
  model: "google/gemini-3-pro-preview"
  api_key: "your_key"

long_context_model:
  base_url: "https://open.bigmodel.cn/api/paas/v4/"
  model: "glm-4-5"
  api_key: "your_key"
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `offline_mode` | bool | `false` | Disable network tools |
| `context_folding` | bool | `true` | Enable context compression |
| `research_agent` | object | - | Research agent LLM config |
| `design_agent` | object | - | Design agent LLM config |
| `long_context_model` | object | - | Long context model config |

### Agent Config Object

```yaml
base_url: string   # API endpoint
model: string     # Model identifier
api_key: string   # API key
```

### Optional Models

```yaml
vision_model:
  base_url: "https://open.bigmodel.cn/api/paas/v4/"
  model: "glm-4-6v-flash"
  api_key: "your_key"

t2i_model:
  base_url: "https://ark.cn-beijing.volces.com/api/v3"
  model: "doubao-seedream-4-5-251128"
  api_key: "your_key"
  sampling_parameters:
    response_format: "b64_json"
```

## mcp.json

MCP server configuration for tool integrations.

```json
{
  "TAVILY_API_KEY": "your_tavily_key",
  "MINERU_API_KEY": "your_mineru_key",
  "MINERU_API_URL": "http://localhost:8000"
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `TAVILY_API_KEY` | string | Tavily web search API key |
| `MINERU_API_KEY` | string | MinerU cloud API key |
| `MINERU_API_URL` | string | Local MinerU endpoint |

## Environment Variables

| Variable | Description |
|-----------|-------------|
| `DEEPPRESENTER_WORKSPACE_BASE` | Override default workspace path |
| `OPENAI_API_KEY` | OpenAI API key (if not in config) |
| `TAVILY_API_KEY` | Tavily API key (alternative to mcp.json) |
| `MINERU_API_KEY` | MinerU API key (alternative to mcp.json) |

## Workspace

Default workspaces are created under:

```
~/.cache/deeppresenter/
```

Override with `DEEPPRESENTER_WORKSPACE_BASE` environment variable.

## Constants

Key constants defined in `deeppresenter/utils/constants.py`:

- `WORKSPACE_BASE`: Default workspace root
- `DEFAULT_MODEL`: Fallback model
- `MAX_CONTEXT_LENGTH`: Maximum context tokens
- `DEFAULT_ASPECT_RATIO`: Default PPTX aspect ratio