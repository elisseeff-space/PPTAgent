[← CLI Reference](cli.md) · [Back to README](../README.md) · [Architecture →](architecture.md)

# Deployment

Server deployment options for PPTAgent / DeepPresenter.

## Docker Compose (Recommended)

Use this mode for a stable server environment with explicit dependencies.

### Pull Public Images

```bash
# Pull the sandbox image
docker pull forceless/deeppresenter-sandbox
docker tag forceless/deeppresenter-sandbox deeppresenter-sandbox

# Start the host service
docker compose up -d
```

### Build From Source

```bash
# Build the sandbox image
docker build -t deeppresenter-sandbox -f deeppresenter/docker/SandBox.Dockerfile .

# Start the host service
docker compose up -d
```

### Access the Service

The service exposes the web UI on `http://localhost:7861`.

## Docker Images

| Image | Purpose |
|-------|---------|
| `deeppresenter-sandbox` | Sandboxed agent execution environment |
| `deeppresenter-host` | Main application server with web UI |

## Docker Compose Configuration

The `docker-compose.yml` file defines:

- **Ports:** 7861 (web UI)
- **Volumes:**
  - `./workspace:/opt/workspace` — Persistent workspace
  - `./deeppresenter:/usr/src/pptagent/deeppresenter` — Live code mounting
  - Docker socket for container management
  - HuggingFace/ModelScope cache mounts
- **Environment:**
  - `DEEPPRESENTER_LOG_LEVEL` — Log level (0=debug, 10=info, 20=warning)
  - `DEEPPRESENTER_WORKSPACE_BASE` — Workspace path inside container

## Configuration for Docker

Before starting, ensure config files exist:

```bash
cp deeppresenter/config.yaml.example deeppresenter/config.yaml
cp deeppresenter/mcp.json.example deeppresenter/mcp.json
```

Edit these files with your LLM credentials and optional service keys.

## Local Inference Service

For local model serving:

```bash
uvx pptagent serve
```

This starts the inference service used by the CLI for local model deployment.

## See Also

- [Getting Started](getting-started.md) — Installation options
- [Configuration](configuration.md) — LLM credentials and optional services
- [CLI Reference](cli.md) — Command reference including `pptagent serve`
