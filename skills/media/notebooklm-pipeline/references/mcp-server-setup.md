# NotebookLM MCP Server Setup (Hermes Native MCP)

Last updated: 12 Tem 2026

## Package: `notebooklm-mcp-cli` (v0.8.6+)

Kurulum: `uv tool install notebooklm-mcp-cli` (pip DEĞİL — pip'teki v2.0.11 eski/buggy repackage'dır)

| Binary | Kaynak | Açıklama |
|--------|--------|----------|
| `notebooklm-mcp` | `uv tool install` | MCP server (fastmcp v3, 39 tool) |
| `nlm` | `uv tool install` | CLI: notebook/list/source/studio yönetimi |

## Auth (Keepalive Chrome Üzerinden)

Keepalive Chrome (port 18800) zaten auth'luysa:

```bash
# Varsayılan profili güncelle
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --force

# Belirli bir profili güncelle (multi-account)
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --profile pro --force
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --profile legacy --force
```

Bu method keepalive Chrome'daki oturumu kullanır, yeni Chrome açmaz.

## Multi-Profile (İki Hesap)

| Profil | Hesap | Kullanım |
|--------|-------|----------|
| `legacy` | isimgorulsunn@gmail.com | Genel kullanım |
| `pro` | kenshin4155@gmail.com | Studio (pro avantajları) |

Varsayılan profil `nlm config set auth.default_profile pro` ile değiştirilir.

Profil dizinleri: `~/.notebooklm-mcp-cli/profiles/{legacy,pro}/`

## Keepalive-MCP Bridge

`nb_keepalive.py` her 20 dk'da bir çalışır, keepalive Chrome'dan cookie'leri alır ve HER İKİ MCP profiline de yazar (sync_mcp_auth()).

Mekanizma:
1. `cdp_extract_both.py` → keepalive Chrome'dan cookie extract (port 18800)
2. `sync_mcp_auth()` → her profil için `nlm login --cdp-url --profile NAME --force`
3. Başarısız olursa → `nb_autologin.py` fallback → SOS alert

Keepalive Chrome ölürse → `ensure_chrome_alive()` ile auto-restart.

## Hermes'e MCP Ekleme

```bash
# STDIO transport (direct)
hermes mcp add notebooklm --command /home/ubuntu/.local/bin/notebooklm-mcp --args "--transport stdio"

# Veya wrapper script ile
cat > ~/.hermes/scripts/start-notebooklm-mcp.sh << 'EOF'
#!/bin/bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
exec /home/ubuntu/.local/bin/notebooklm-mcp --transport stdio
EOF
chmod +x ~/.hermes/scripts/start-notebooklm-mcp.sh
hermes mcp remove notebooklm
hermes mcp add notebooklm --command ~/.hermes/scripts/start-notebooklm-mcp.sh
```

Not: Server startup ~35s sürebilir. MCP timeout yeterli olmalı (120s).

## Auth Kontrol

```bash
nlm doctor        # Kapsamlı auth + hata kontrolü
nlm login --check # Sadece auth durumu
```

Beklenen:
- Cookies: present (46+)
- CSRF token: yes
- Account: isimgorulsunn@gmail.com
- Notebooks found: N

## Önemli Noktalar

- Eski pip paketinden (`notebooklm-mcp v2.0.11`) geçiş yaparken ÖNCE pip'i kaldır, SONRA uv tool install --force yap
- Binary isimleri çakışırsa `--force` kullan
- Keepalive Chrome profili ayrı, nlm auth profili ayrı (~/.notebooklm-mcp-cli/profiles/)
- MCP server HTTP transport da destekler: `notebooklm-mcp --transport http --port 8001`
