# CLI Reference

## Commands

### onboard

Interactive configuration wizard for first-time setup.

```bash
uvx pptagent onboard
```

Creates and updates `config.yaml` and `mcp.json` interactively.

---

### generate

Generate a presentation from a prompt or document.

```bash
uvx pptagent generate "PROMPT" [OPTIONS]
```

#### Options

| Option | Description |
|--------|-------------|
| `-o, --output FILE` | Output file path |
| `-f, --file FILE` | Attachment files (multiple allowed) |
| `-p, --pages RANGE` | Page range for PDFs (e.g., "1-5, 10") |
| `--type TYPE` | Conversion type: `design` (default) or `pptagent` |
| `--aspect RATIO` | Aspect ratio: `standard` (4:3) or `wide` (16:9) |
| `--language LANG` | Language: `en` (default) or `zh` |
| `--offline` | Enable offline mode |

#### Examples

```bash
# Basic generation
uvx pptagent generate "Q4 Report" -o report.pptx

# With attachments
uvx pptagent generate "Analyze Q4 data" \
  -f data.xlsx \
  -f charts.pdf \
  -p "10-12" \
  -o report.pptx

# Legacy PPTAgent mode
uvx pptagent generate "Create presentation" \
  --type pptagent \
  -o legacy.pptx

# Wide aspect ratio
uvx pptagent generate "Presentation" \
  --aspect wide \
  -o wide.pptx

# Chinese language
uvx pptagent generate "季度报告" \
  --language zh \
  -o report_zh.pptx
```

---

### config

View current configuration.

```bash
uvx pptagent config
```

Displays loaded configuration from `config.yaml` and `mcp.json`.

---

### reset

Reset configuration to defaults.

```bash
uvx pptagent reset
```

Removes `config.yaml` and `mcp.json` files.

---

### serve

Start the local inference service used by the CLI.

```bash
uvx pptagent serve
```

Starts Gradio web UI for local model inference.

---

### clean

Clean workspace directories.

```bash
uvx pptagent clean [SESSION_ID]
```

Removes cached workspace(s) from `DEEPPRESENTER_WORKSPACE_BASE`.

#### Options

| Option | Description |
|--------|-------------|
| `SESSION_ID` | Specific session to clean (default: all) |

---

## Input Types

The CLI accepts:

- Plain text prompts
- File paths (`.txt`, `.md`, `.pdf`, `.xlsx`, `.docx`)
- Mixed prompt with attachments

## Output Formats

| Extension | Format |
|----------|--------|
| `.pptx` | PowerPoint presentation |
| `.pdf` | PDF (fallback if HTML2PPTX fails) |