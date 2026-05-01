# DeepPresenter
An agentic PowerPoint generation system that transforms documents, prompts, and research into polished presentations.
## News
- **ACL 2026**: [DeepPresenter](https://arxiv. org/abs/2602.22839) accepted to ACL 2026
- **EMNLP 2025**: [PPTAgent](https://arxiv. org/abs/2501.03936) accepted to EMNLP 2025
## Quick Start
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.uv | sh
# Setup
uvx pptagent onboard
# Generate
uvx pptagent generate "Single Page with Title: Hello World" -o hello. pptx
```
## Documentation
- [Getting Started](docs/getting-started. md) - Installation and basic usage
- [Architecture](docs/architecture. md) - System design
- [Configuration](docs/configuration. md) - Configuration reference
- [CLI Reference](docs/cli. md) - Command reference
## Features
- **DeepPresenter Pipeline**: Research → Visual Design → HTML → PPTX
- **Free-Form Visual Design**: Agent-driven slide layout generation
- **Deep Research Integration**: Web search, academic sources, PDF parsing
- **Autonomous Asset Creation**: Text-to-image generation
- **MCP Server**: `pptagent- mcp` command for tool integrations
## CLI Commands
| Command | Description |
|----------|-------------|
| `onboard` | Interactive configuration wizard |
| `generate` | Generate presentations |
| `config` | View current configuration |
| `reset` | Reset configuration |
| `serve` | Start local inference service |
| `clean` | Clean workspaces |
## Recommended Models
Fine-tuned models significantly outperform open-source alternatives:
| Model | HuggingFace | ModelScope |
|-------|-------------|------------|
| GGUF | [Forceless/DeepPresenter-9B- GGUF](https://huggingface. co/Forceless/DeepPresenter-9B- GGUF) | [forceless/DeepPresenter-9B- GGUF](https://modelscope. cn/models/forceless/DeepPresenter-9B- GGUF) |
| Full | [Forceless/DeepPresenter-9B](https://huggingface. co/Forceless/DeepPresenter-9B) | [forceless/DeepPresenter-9B](https://modelscope. cn/models/forceless/DeepPresenter-9B) |
## Requirements
- Python 3.11+
- Playwright (browsers)
- Docker
- Node. js 18+ (for HTML→PPTX)
## Citation
```bibtex
@Inproceedings{zheng-etal-2025-pptagent,
    title = "{PPTA}gent: Generating and Evaluating Presentations Beyond Text- to- Slides",
    author = "Zheng, Hao and Guan, Xinyan and Kong, Hao and others",
    booktitle = "Proceedings of EMNLP 2025",
    pages = "14413--14429",
}
@misc{zheng2026deeppresenter,
    title = {DeepPresenter: Environment- Grounded Reflection for Agentic Presentation Generation},
    author = {Hao Zheng and others},
    year = {2026},
    eprint = {2602.22839},
    archivePrefix = {arXiv},
    primaryClass = {cs. AI},
}
```