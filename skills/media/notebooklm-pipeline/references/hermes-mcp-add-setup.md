# Hermes NotebookLM MCP Setup — hermes mcp add Workflow

## Setup (Yeğlenen Yöntem)

Wrapper script ve `hermes mcp add` ile otomatik yapılandırma:

```bash
# 1. Varsa eski MCP'yi kaldır
hermes mcp rm notebooklm-mcp

# 2. Yeni binary wrapper script'i ile ekle
echo "Y" | hermes mcp add notebooklm-mcp --command /home/ubuntu/.hermes/scripts/start-notebooklm-mcp.sh
```

## Binary Migration (24 Haz 2026)

| Önce | Sonra |
|------|-------|
| `/usr/local/bin/notebooklm-mcp` (npm) | `/home/ubuntu/.local/bin/notebooklm-mcp` (pip, nlm paketinden) |
| `notebooklm-mcp server` (default) | `notebooklm-mcp --transport stdio` |
| crash-loop, banner pollution | stabil, 39 tool |

## Script İçeriği

`/home/ubuntu/.hermes/scripts/start-notebooklm-mcp.sh`:
```bash
#!/bin/bash
exec /home/ubuntu/.local/bin/notebooklm-mcp --transport stdio
```

## Pitfall: `hermes mcp add --args` çalışmıyor

```bash
# HATA:
hermes mcp add notebooklm-mcp --command /home/ubuntu/.local/bin/notebooklm-mcp --args --transport stdio
# → "unrecognized arguments: --transport stdio"
```

Argümanları script'e göm, `--args` kullanma.

## Pitfall: `hermes mcp test` dictionary hatası

```
✗ Connection failed: dictionary update sequence element #0 has length 1; 2 is required
```

**Sebep:** Config'de `args: '[]'` (string) formatı.
**Çözüm:** `hermes mcp rm` + `hermes mcp add` ile yeniden ekle.

## Önemli: Yeni Session Gerekli

`hermes mcp add` tool'ları config'e kaydeder ama mevcut session'da GÖRÜNMEZ. Yeni bir konuşma başlatmak gerekir.
