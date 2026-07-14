# notebooklm-mcp-cli: pip → uv Migration (12 Tem 2026)

## Problem

Eski `notebooklm-mcp v2.0.11` pip ile kurulmuştu. Bu versiyon:
- **Repackaged/fork** — orijinal `jacob-bd/notebooklm-mcp-cli`'nin yetkisiz bir kopyası
- **Bozuk auth** — `_ensure_client()` hiç `authenticate()` çağırmıyor, `_is_authenticated` hep False
- **undetected-chromedriver** — kendi Chrome'unu başlatıyor, keepalive Chrome profili locked olunca çakışıyor
- **fastmcp v2** — eski framework

## Çözüm: uv tool install ile doğru paket

```bash
# 1. uv kur (astral.sh/uv adresinden)
# 2. Eski pip paketini kaldır (opsiyonel, --force yeter)
pip3 uninstall notebooklm-mcp -y 2>/dev/null || true

# 3. Doğru paketi kur
uv tool install --force notebooklm-mcp-cli
```

Yeni versiyon: **v0.8.6+** — orijinal `jacob-bd/notebooklm-mcp-cli` reposu.

## Auth (Keepalive Chrome ile)

```bash
# Keepalive Chrome port 18800'de çalışıyorsa:
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --force
```

Bu adım keepalive Chrome'un CDP portuna bağlanır, NotebookLM cookie'lerini extract eder, `~/.notebooklm-mcp-cli/profiles/legacy/` altına kaydeder.

## Hermes MCP Ekleme

```bash
hermes mcp add notebooklm --command /home/ubuntu/.local/bin/notebooklm-mcp --args "--transport stdio"
```

Timeout sorunu yaşanırsa:
```bash
hermes config set mcp_servers.notebooklm.timeout 120
```

## Test

```bash
nlm doctor              # Auth + sistem durumu
nlm login --check       # Auth geçerli mi?
nlm notebook list       # Notebook listesi
```

## Farklar (Eski vs Yeni)

| Özellik | Eski (pip v2.0.11) | Yeni (uv v0.8.6) |
|----------|-------------------|-------------------|
| Framework | fastmcp v2 | fastmcp v3 (mcp v1.28) |
| Browser | undetected-chromedriver | Patchright (Playwright fork) |
| Auth | `_ensure_client()` bug | `nlm login` CDP |
| Tool sayısı | ~10 | 39 |
| CLI | `notebooklm-mcp server` | `nlm <command>` |
| Startup time | Hızlı | ~35s (auth verify) |

## MCP HTTP Transport

Uzun startup süresi sorun olursa HTTP transport kullanılabilir:

```bash
# Server'ı background'da başlat (HTTP mode)
notebooklm-mcp --transport http --port 8001 &

# Hermes'e HTTP olarak ekle (not: hermes mcp add --url ile)
hermes mcp add notebooklm --url http://127.0.0.1:8001/mcp
```
