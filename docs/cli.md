[← Configuration](configuration.md) · [Back to README](../README.md) · [Deployment →](deployment.md)

# CLI Reference

Full command reference for the `pptagent` CLI.

## Commands

| Command | Description |
|---------|-------------|
| `pptagent onboard` | Interactive configuration wizard |
| `pptagent generate` | Generate presentations from prompt or documents |
| `pptagent config` | View current configuration |
| `pptagent reset` | Reset configuration to defaults |
| `pptagent serve` | Start the local inference service |

## `pptagent onboard`

Interactive wizard for creating and updating LLM credentials and optional service configuration.

```bash
uvx pptagent onboard
```

Guides you through:
- LLM API credentials (OpenAI-compatible)
- Optional services (Tavily, MinerU, T2I model)
- Config file locations

## `pptagent generate`

Generate presentations from a prompt, with optional file attachments.

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

### Options

| Option | Description |
|--------|-------------|
| `-f, --file` | Attach files (documents, spreadsheets, PDFs) |
| `-p, --pages` | Page range for multi-page attachments (e.g., "10-12") |
| `-o, --output` | Output file path (`.pptx` or `.pdf`) |

### Generation Modes

- **CLI mode (`uvx pptagent`)** — Fastest local setup or OpenClaw integration
- **Build from source** — Minimal abstraction layer with full control
- **Docker Compose** — Stable server environment

## `pptagent config`

View current configuration settings.

```bash
uvx pptagent config
```

## `pptagent reset`

Reset configuration to defaults.

```bash
uvx pptagent reset
```

## `pptagent serve`

Start the local inference service used by the CLI.

```bash
uvx pptagent serve
```

## Notes

> [!NOTE]
> On macOS, the CLI may automatically install several local dependencies, including Homebrew, Node.js, Docker, poppler, Playwright, and llama.cpp.
>
> On Linux, you should prepare the environment by yourself.

## See Also

- [Getting Started](getting-started.md) — Installation and first steps
- [Configuration](configuration.md) — LLM credentials and optional services
- [Deployment](deployment.md) — Docker Compose server deployment
