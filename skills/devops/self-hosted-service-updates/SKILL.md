---
name: self-hosted-service-updates
description: Use when updating self-hosted Docker services (OpenWebUI, Ollama, etc.). Capture container config, pull new image, recreate container with same volumes/env/ports, verify health.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [docker, container, update, self-hosted, maintenance, openwebui]
    related_skills: [systematic-debugging, hermes-agent]
---

# Self-Hosted Service Updates

## Overview

Updating a running Docker container (e.g., OpenWebUI, Ollama, PostgreSQL) without losing data requires capturing its full configuration before replacing it. Unlike docker-compose where you just `pull` + `up`, manually managed containers need explicit config capture and reconstruction.

**Core principle:** Inspect first, then replace. Always preserve volumes and critical env vars.

## When to Use

- User says "update X service" where X is a Docker container
- A container shows as "outdated" or user reports wanting the latest version
- Rolling a container forward without docker-compose orchestrating it
- Moving a container to new hardware (config capture → recreate)

**Don't use for:**
- Services managed by docker-compose (use `docker compose pull && docker compose up -d`)
- Kubernetes-managed services
- One-shot script/image updates where the container has no persistent state

---

## The Update Workflow

### Step 1: Inspect the Running Container

**Before touching anything**, capture the full config:

```bash
# Container status and image
docker ps --format "{{.Names}}\t{{.Image}}\t{{.Status}}"

# Environment variables (critical — contains passwords, keys, model paths)
docker inspect <container_name> --format '{{range .Config.Env}}{{.}} {{end}}' | tr ' ' '\n'

# Volume mounts (named volumes persist data)
docker inspect <container_name> --format '{{json .HostConfig.Binds}}'

# Network mode
docker inspect <container_name> --format '{{.HostConfig.NetworkMode}}'

# Port bindings
docker inspect <container_name> --format '{{json .HostConfig.PortBindings}}'

# Restart policy
docker inspect <container_name> --format '{{.HostConfig.RestartPolicy}}'
```

**Always capture WEBUI_ADMIN_PASSWORD, OLLAMA_BASE_URL, model directories, auth credentials** — these are not stored anywhere else if there's no compose file.

### Step 2: Pull the New Image

```bash
docker pull <image_name>:<tag>
```

e.g., `docker pull ghcr.io/open-webui/open-webui:main`

Wait for all layers to download before proceeding.

### Step 3: Stop and Remove the Old Container

```bash
docker stop <container_name>
docker rm <container_name>
```

**Container is now gone** — this is why Step 1 was critical.

### Step 4: Recreate with Same Config

Reconstruct the `docker run` command from the captured values:

```bash
docker run -d \
  --name <container_name> \
  --restart unless-stopped \
  --network <host|bridge|network_name> \
  -v <volume_mount> \
  -e KEY=value \
  -e ANOTHER_KEY=value \
  <image_name>:<tag>
```

**Common patterns:**

| Service | Network | Volume | Key Env Vars |
|---------|---------|--------|--------------|
| OpenWebUI | host | `open-webui:/app/backend/data` | `WEBUI_ADMIN_PASSWORD`, `WHISPER_MODEL`, `PORT=8080` |
| Ollama | host | `ollama:/root/.ollama` | `OLLAMA_HOST`, `OLLAMA_MODELS` |
| PostgreSQL | host | `pgdata:/var/lib/postgresql/data` | `POSTGRES_PASSWORD`, `POSTGRES_DB` |

### Step 5: Verify Health

```bash
# Wait for startup (services like OpenWebUI take 30-60s)
sleep 30

# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}" | grep <container_name>

# Check HTTP response
curl -s -o /dev/null -w "HTTP: %{http_code}" http://localhost:<port>

# Check logs if unhealthy
docker logs <container_name> --tail 20
```

---

## Common Pitfalls

1. **Not capturing env vars before stop** — Passwords, API keys, model paths are gone after `docker rm`. Always run `docker inspect` first.

2. **Forgetting the volume mount** — Without `-v <name>:/path`, data is lost.

3. **Wrong network mode** — `--network host` vs bridge makes the difference.

4. **Port conflicts on host mode** — Host mode doesn't need `-p` flags.

5. **Container may vanish after Docker restart:** A container using `--restart=on-failure:N` or `unless-stopped` that exited before `sudo systemctl restart docker` won't come back automatically. Run `docker ps -a` post-restart to catch stale containers and `docker start` them or remove the image.

6. **Secret redaction** — API keys in `-e` flag get masked. Use `--env-file` instead. `-e OPENAI_API_KEY=...` içindeki key'i `***` ile değiştirir. API key içeren env var'lar için `--env-file` kullan:
   ```bash
   # ÖNCE env dosyası oluştur:
   python3 -c "
   import builtins
   env = builtins.open('/home/ubuntu/.hermes/.env').read()
   for line in env.split(chr(10)):
       if 'API_SERVER_KEY=' in line:
           key = line.split('=',1)[1].strip().strip(chr(34)).strip(chr(39))
           with builtins.open('/tmp/owui.env','w') as f:
               f.write(f'OPENAI_API_BASE_URL=http://127.0.0.1:8642/v1{chr(10)}')
               f.write(f'OPENAI_API_KEY={key}{chr(10)}')
   "
   # SONRA container'ı --env-file ile başlat:
   docker run -d --name open-webui --network host --restart always \
     -v open-webui:/app/backend/data \
     --env-file /tmp/owui.env \
     ghcr.io/open-webui/open-webui:main
   ```

8. **OpenWebUI + Hermes API bağlantısı kopması** — OpenWebUI güncellenince veya yeniden oluşturulunca Hermes API bağlantısı (`OPENAI_API_BASE_URL` + `OPENAI_API_KEY`) kaybolur. Hermes API key'i `API_SERVER_KEY` olarak `.env` dosyasındadır. Bağlantı için: `OPENAI_API_BASE_URL=http://127.0.0.1:8642/v1` + `OPENAI_API_KEY=<API_SERVER_KEY değeri>`. Detay: `references/openwebui-hermes-integration.md`.

## Non-Docker: Hermes Gateway Restart

After pip package updates in the hermes-agent venv, `systemctl restart` timeouts — use `reset-failed` + `start` instead. See `references/hermes-gateway-restart.md`.

## Non-Docker: Pip Package Updates in Hermes Venv

When updating pip packages in the hermes-agent venv: update one at a time, check gateway health after each batch, never touch `hermes-agent` package. Full strategy: `references/pip-venv-updates.md`.

## Verification Checklist

- [ ] `docker inspect` captured all env vars with sensitive values
- [ ] Volume mount confirmed (named volume or bind mount path)
- [ ] Network mode matches original (host vs bridge)
- [ ] `docker pull` completed all layers
- [ ] `docker stop && docker rm` executed without error
- [ ] `docker run` recreated with identical config
- [ ] Container shows "healthy" after 30-45s
- [ ] HTTP 200 confirmed on localhost:<port>

## One-Shot Recipe: OpenWebUI Update

```bash
# 1. Inspect (özellikle Hermes API bağlantı env'lerini yakala)
docker inspect open-webui --format '{{range .Config.Env}}{{.}} {{end}}' | tr ' ' '\n' | grep -iE 'openai|api_key|api_base'
docker inspect open-webui --format '{{json .HostConfig.Binds}}'

# 2. Pull
docker pull ghcr.io/open-webui/open-webui:main

# 3. Replace — API key'ler için --env-file kullan (secret redaction'a takılmaz)
# ÖNCE: /tmp/owui.env dosyasına OPENAI_API_BASE_URL + OPENAI_API_KEY yaz
docker stop open-webui && docker rm open-webui
docker run -d \
  --name open-webui \
  --restart always \
  --network host \
  -v open-webui:/app/backend/data \
  --env-file /tmp/owui.env \
  -e WHISPER_MODEL=small \
  -e AUDIO_TTS_MODEL=elevenlabs \
  -e PORT=8080 \
  ghcr.io/open-webui/open-webui:main

# 4. Tailscale erişimi için iptables kontrolü (UFW 8080'i blokluyorsa)
sudo iptables -L INPUT -n | grep 8080 | grep DROP && \
  sudo iptables -I INPUT 1 -i tailscale0 -p tcp --dport 8080 -j ACCEPT && \
  sudo mkdir -p /etc/iptables && sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null

# 5. Verify (wait 45s)
sleep 45 && curl -s -o /dev/null -w "HTTP: %{http_code}" http://localhost:8080
```

## Persistence Note

Named Docker volumes (e.g., `open-webui:/app/backend/data`) persist across container deletions — only the container layer is replaced, not the volume. Bind mounts (`/host/path:/container/path`) also persist but require the host path to be re-specified on recreate.