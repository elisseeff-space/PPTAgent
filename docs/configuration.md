[← Getting Started](getting-started.md) · [Back to README](../README.md) · [CLI Reference →](cli.md)

# Configuration

LLM credentials, optional services, and runtime settings for PPTAgent / DeepPresenter.

## Config Files

If you use the CLI, `pptagent onboard` creates and updates configurations interactively. For Docker Compose or manual setup, prepare them manually:

```bash
cp deeppresenter/config.yaml.example deeppresenter/config.yaml
cp deeppresenter/mcp.json.example deeppresenter/mcp.json
```

### Main Config: `deeppresenter/config.yaml`

Key settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `offline_mode` | Disable network-dependent tools | `false` |
| `context_folding` | Enable context management to prevent overflow | `true` |
| `t2i_model` | Text-to-image model for slide images | (none) |

### MCP Tools Config: `deeppresenter/mcp.json`

Defines MCP tool servers for search, research, sandbox, and file conversion.

## Optional Services

The following services noticeably improve generation quality:

### Tavily (Web Search)

Improves web search quality for research agent.

1. Apply for an API key at [tavily.com](https://www.tavily.com/)
2. Set `TAVILY_API_KEY` in `deeppresenter/mcp.json`

### MinerU (PDF Parsing)

Improves PDF parsing quality for document processing.

**Option A: Cloud API**
1. Apply for an API key at [mineru.net](https://mineru.net/apiManage/docs)
2. Set `MINERU_API_KEY` in `deeppresenter/mcp.json`

**Option B: Local Deployment**
1. Deploy MinerU locally
2. Set `MINERU_API_URL` in `deeppresenter/mcp.json`

### Text-to-Image Model

Improves image generation quality for slide visuals.

Configure `t2i_model` in `deeppresenter/config.yaml`.

## Environment Variables

Additional configurable variables are defined in `deeppresenter/utils/constants.py`. Key ones:

| Variable | Description |
|----------|-------------|
| `DEEPPRESENTER_LOG_LEVEL` | Log level (0=debug, 10=info, 20=warning) |
| `DEEPPRESENTER_WORKSPACE_BASE` | Override default workspace path (`~/.cache/deeppresenter/`) |
| `OPENAI_API_KEY` | LLM API key (configured via `pptagent onboard`) |
| `TAVILY_API_KEY` | Tavily search API key |
| `MINERU_API_KEY` | MinerU cloud API key |
| `MINERU_API_URL` | MinerU local deployment URL |

## Offline Mode

For fully offline operation:

1. Deploy MinerU locally
2. Set `offline_mode: true` in `deeppresenter/config.yaml`

This disables network-dependent tools like web search.

## Fine-Tuned Model

We strongly recommend deploying our fine-tuned model for the best experience. According to experiments, it significantly outperforms existing open-source models.

| Format | HuggingFace | ModelScope |
|--------|-------------|------------|
| GGUF (Quantized) | [Forceless/DeepPresenter-9B-GGUF](https://huggingface.co/Forceless/DeepPresenter-9B-GGUF) | [forceless/DeepPresenter-9B-GGUF](https://modelscope.cn/models/forceless/DeepPresenter-9B-GGUF) |
| Full Weights | [Forceless/DeepPresenter-9B](https://huggingface.co/Forceless/DeepPresenter-9B) | [forceless/DeepPresenter-9B](https://modelscope.cn/models/forceless/DeepPresenter-9B) |

## See Also

- [Getting Started](getting-started.md) — Installation and first steps
- [CLI Reference](cli.md) — Command reference including `pptagent onboard`
- [Architecture](architecture.md) — How config is loaded and used by agents
