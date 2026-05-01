# Getting Started with DeepPresenter

An agentic PowerPoint generation system that transforms documents, prompts, and research into polished presentations.

## Prerequisites

- Python 3.11+
- [uv](https://astral.sh/uv/install) package manager
- Node.js 18+ (for HTML→PPTX conversion)
- Docker (for sandbox environment)
- Playwright browsers (`playwright install --with-deps`)

> **Note:** Windows is not supported. Use WSL if you are on Windows.

## Installation

### Quick Start (CLI)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.uv | sh

# Interactive setup
uvx pptagent onboard

# Generate a presentation
uvx pptagent generate "Single Page with Title: Hello World" -o hello.pptx
```

### From Source

```bash
# Clone and install
git clone https://github.com/icip-cas/PPTAgent.git
cd PPTAgent

# Install in development mode
uv pip install -e .

# Install system dependencies
playwright install --with-deps
playwright install chromium
npm install --prefix deeppresenter/html2pptx

# Download models
modelscope download forceless/fasttext-language-id

# Pull Docker images
docker pull forceless/deeppresenter-sandbox
docker pull forceless/deeppresenter-host
docker tag forceless/deeppresenter-sandbox deeppresenter-sandbox
```

## Configuration

After installation, configure your API keys:

```bash
# Interactive wizard
uvx pptagent onboard

# Or manually copy and edit templates
cp deeppresenter/config..yaml.example deeppresenter/config.yaml
cp deeppresenter/mcp.json.example deeppresenter/mcp.json
```

### Optional Services (Improve Quality)

| Service | Purpose | Config Variable |
|--------|---------|-----------------|
| Tavily | Web search quality | `TAVILY_API_KEY` in `mcp.json` |
| MinerU | PDF parsing quality | `MINERU_API_KEY` or `MINERU_API_URL` |
| Text-to-Image | Image generation | `t2i_model` in `config.yaml` |

## Basic Usage

### CLI Commands

```bash
# Generate with prompt
uvx pptagent generate "Q4 Report" -o report.pptx

# Generate with attachments
uvx pptagent generate "Q4 Report" \
  -f data.xlsx \
  -f charts.pdf \
  -p "10-12" \
  -o report.pptx

# View configuration
uvx pptagent config

# Reset configuration
uvx pptagent reset

# Start inference service
uvx pptagent serve
```

### Python API

```python
from pathlib import Path
from deeppresenter.main import AgentLoop
from deeppresenter.utils.config import DeepPresenterConfig
from deeppresenter.utils.typings import ConvertType, InputRequest, PowerpointType

# Load configuration
config = DeepPresenterConfig.from_yaml(Path("config.yaml"))

# Create request
request = InputRequest(
    instruction="Q4 Report",
    attachments=[Path("data.xlsx"), Path("charts.pdf")],
    pages="10-12",
    convert_type=ConvertType.DESIGN,
    powerpoint_type=PowerpointType.WIDE,
)

# Run generation
async for message in AgentLoop(config).run(request):
    print(message)
```

## Docker Deployment

```bash
# Pull images
docker pull forceless/deeppresenter-sandbox
docker tag forceless/deeppresenter-sandbox deeppresenter-sandbox

# Build from source (alternative)
docker build -t deeppresenter-sandbox -f deeppresenter/docker/SandBox.Dockerfile .

# Start services
docker compose up -d
```

Access the web UI at `http://localhost:7861`.

## Offline Mode

For fully offline operation:

1. Deploy MinerU locally
2. Set `offline_mode: true` in `config.yaml`
3. Disable network-dependent tools (web search)

## Next Steps

- [Architecture Overview](architecture.md) - System design and components
- [Configuration Reference](configuration.md) - Full configuration options
- [CLI Reference](cli.md) - Complete command reference