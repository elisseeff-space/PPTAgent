[Back to README](../README.md) · [Configuration →](configuration.md)

# Getting Started

Installation, setup, and first steps for PPTAgent / DeepPresenter.

## Prerequisites

- **Python:** 3.11+
- **Package manager:** uv
- **Node.js:** 18+ (for HTML→PPTX conversion)
- **Docker:** Required for sandbox execution
- **Playwright browsers:** For HTML→PDF conversion

> [!IMPORTANT]
> Windows is not supported. If you are on Windows, please use WSL.

## Installation

### Option 1: CLI via uvx (Recommended)

The fastest way to get started — no local installation needed:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# First-time interactive setup
uvx pptagent onboard

# Generate a presentation
uvx pptagent generate "Single Page with Title: Hello World" -o hello.pptx
```

### Option 2: Build From Source

For development or minimal setup with full control:

```bash
# Clone the repository
git clone https://github.com/icip-cas/PPTAgent.git
cd PPTAgent

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

### Option 3: Docker Compose

For server deployment with explicit dependencies:

```bash
# Pull the public images
docker pull forceless/deeppresenter-sandbox
docker tag forceless/deeppresenter-sandbox deeppresenter-sandbox

# Or build from source
docker build -t deeppresenter-sandbox -f deeppresenter/docker/SandBox.Dockerfile .

# Start the host service
docker compose up -d
```

The service exposes the web UI on `http://localhost:7861`.

## First Run

### Interactive Configuration

```bash
uvx pptagent onboard
```

This wizard guides you through:
- LLM API credentials (OpenAI-compatible)
- Optional services (Tavily, MinerU, T2I model)
- Config file locations

### Generate Your First Presentation

```bash
# Simple prompt
uvx pptagent generate "Single Page with Title: Hello World" -o hello.pptx

# With attachments
uvx pptagent generate "Q4 Report" \
  -f data.xlsx \
  -f charts.pdf \
  -p "10-12" \
  -o report.pptx
```

### Start Web UI (Development)

```bash
python webui.py
```

## Verify Installation

After installation, verify everything works:

```bash
# Check CLI is available
uvx pptagent --help

# Verify Python dependencies
uv run python -c "import deeppresenter; print(deeppresenter.__version__)"

# Check Docker images
docker images | grep deeppresenter

# Verify Node conversion
node deeppresenter/html2pptx/html2pptx_cli.js --help
```

## Next Steps

- [Configuration](configuration.md) — Set up LLM credentials and optional services
- [CLI Reference](cli.md) — Full command reference
- [Architecture](architecture.md) — Understand the project structure
- [Deployment](deployment.md) — Server deployment with Docker Compose

## See Also

- [Configuration](configuration.md) — LLM credentials, optional services, offline mode
- [CLI Reference](cli.md) — All CLI commands and options
- [Architecture](architecture.md) — Agent architecture and module structure
