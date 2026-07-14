---
name: context-mode-bakim
description: "Context-mode MCP server bakim. Session dizini fix'i, sessiz restart, keepalive cozumu, gateway restart stratejileri."
version: 1.2.0
metadata:
  hermes:
    tags: [context-mode, mcp, server, troubleshooting, bakim]
    category: devops
---

# Context-mode MCP Server Bakimi

Context-mode MCP server'i Hermes'in FTS5/session arama ve sandbox execute altyapisini saglar.

## Belirtiler

- Tool listesinde `mcp_context_mode_*` toollari yok
- `ctx_doctor`'da `FTS5 / SQLite: FAIL` veya versiyon uyarisi
- Context-mode process `ps aux`'da gorunmuyor
- Gateway log'da `Failed to parse JSONRPC message`

## Ikili Kayit Cakismasi (En Sik Karsilasilan)

Context-mode hem config.yaml'de MCP server olarak, hem de opencode.json'da plugin+MCP olarak kayitliysa toollari bilerek bosaltir.

**Belirti:** `ctx_* tools/list intentionally empty`

**Cozum:** opencode.json'dan context-mode referanslarini kaldir.

## FTS5/SQLite Modul Eksik

`ctx_doctor` → `FTS5 / SQLite: FAIL`

**Cozum:** `ALL_PROXY="" npm update -g context-mode`

## Sifirdan Kurulum (Fresh Install)

Context-mode MCP server'i hic kurulu degilse veya tamamen silinmisse.

### Adim 1: Kurulum
```bash
npm install -g context-mode
```

### Adim 2: Binary Yolunu Bul (KRITIK)
npm prefix'e gore binary farkli yerlere inebilir:
```bash
which context-mode           # PATH'te varsa
npm root -g                  # /home/ubuntu/.npm-global veya /usr
# Binary: $(npm root -g)/bin/context-mode
```

**⚠️ Pitfall:** Gateway restart sonrasi npm prefix degisebilir (`~/.npm-global` → `/usr`). Binary yeri degisir, eski config yolu gecersiz olur. Her restart sonrasi `which context-mode` ile dogrula.

### Adim 3: Config Guncelleme
```bash
hermes config set "mcp_servers.context-mode.command" "$(which context-mode)"
hermes config set "mcp_servers.context-mode.env.CONTEXT_MODE_DIR" "/tmp/context-mode-sessions"
```

### Adim 4: Gateway Reload
```bash
kill -TERM 1
# Gateway ayni PID ile yeniden baslar, MCP server'lari yeniden spawn eder
```

### Adim 5: Dogrulama
```bash
# MCP server'in gateway tarafindan tanindigini kontrol et
hermes tools list | grep context
# Beklenen: "context-mode  all tools enabled"

# Doctor testi
context-mode doctor 2>&1 | grep -E "PASS|FAIL|FTS5"
# Beklenen: Hepsi PASS, sadece PreToolUse hook FAIL olabilir (Claude Code yoksa)
```

## Kurulum (İlk Defa / Yeniden)

### Adım 1: npm install

```bash
# npm prefix kontrolü — binary'nin nereye gideceğini belirler
npm config get prefix

# context-mode kurulumu
npm install -g context-mode

# 139 paket eklenir (~12 saniye)
```

**Önemli:** `npm config get prefix` çıktısına göre binary yolu değişir:
- `/usr` → `/usr/bin/context-mode`
- `/home/ubuntu/.npm-global` → `/home/ubuntu/.npm-global/bin/context-mode`

### Adım 2: Binary Doğrulama

```bash
# Binary mevcut mu?
ls -la /usr/bin/context-mode 2>/dev/null || ls -la /home/ubuntu/.npm-global/bin/context-mode 2>/dev/null

# Çalışıyor mu?
context-mode --help | head -5
# Beklenen: "Usage: context-mode  Start MCP server (stdio)"
```

Eğer binary PATH'te değilse (npm prefix farklıysa), tam yolu kullan veya PATH'e ekle.

### Adım 3: Config Güncelleme

Config'de `command` yolu doğru değilse `hermes config set` ile düzelt:

```bash
# Binary neredeyse o yolu ver
hermes config set mcp_servers.context-mode.command /usr/bin/context-mode
# veya
hermes config set mcp_servers.context-mode.command /home/ubuntu/.npm-global/bin/context-mode
```

### Adım 4: Gateway Reload

MCP server'ın aktifleşmesi için gateway'in config'i yeniden okuması gerek:

```bash
# Container ortamında (PID 1 = gateway process)
kill -TERM 1
```

Gateway aynı PID ile yeniden başlar, config yeniden okunur. Terminal bağlantısı bir an kesilir, Telegram otomatik yeniden bağlanır.

### Adım 5: Doğrulama

```bash
# Doctor testi
context-mode doctor

# Beklenen:
# ✅ Storage session: PASS
# ✅ Server test: PASS
# ✅ FTS5 / SQLite: PASS
# ✅ Version: v1.x.x

# NOT: Bilgi tabanı boş olabilir — yeni kurulumda normal
# ctx_search → "Knowledge base is empty — no content has been indexed yet"
```

Gateway restart sonrası `mcp_context_mode_*` araçlarının tool listesinde görünmesi 1-2 tur sürebilir. `hermes tools list` ile "context-mode all tools enabled" mesajını doğrula.

## Session Dizini Yazma Hatasi (root-owned)

Context-mode session dizini root'e aitse binary sessizce crash eder.
Belirti: gateway altinda 3 dk'da bir restart dongusu, ama mcp-stderr'de hata gorunmez.

**Teshis:** `ctx_doctor`'da `Hook: FAIL` + `Hook output: not writable`

```bash
ls -la /home/ubuntu/.claude/context-mode/sessions
# root root ise ubuntu kullanicisi yazamaz
```

**Cozum — CONTEXT_MODE_DIR env degiskeni:**

```bash
# 1. Gecici dizin olustur
mkdir -p /tmp/context-mode-sessions

# 2. Config'e env olarak ekle
hermes config set mcp_servers.context-mode.env.CONTEXT_MODE_DIR /tmp/context-mode-sessions
```

`CONTEXT_MODE_DIR` binary'nin session yazma dizinini override eder.
`/tmp/` herkesin yazabildigi icin root permission sorunu asilir.

## Sessiz Restart Dongusu (Keepalive Hatasi)

Context-mode 3 dakikada bir surekli restart ediliyor ama mcp-stderr'de HIC HATA YOK.
Binary manuel test'te calisir.

**Iki olasi kok neden:**
1. **Session dizini yazilamiyor** — yukaridaki CONTEXT_MODE_DIR fix'i gerekir
2. **Gateway keepalive timeout** — binary saglam, baglanti kuruluyor ama keepalive tetikleniyor

**Manuel test:**

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | timeout 3 /usr/bin/context-mode
# Basarili: {"result":{"protocolVersion":"2024-11-05","capabilities":{...}},"jsonrpc":"2.0","id":1}
```

**Cozum:** Gateway restart gerekir (asagiya bak).

## Gateway Restart (Container Icinde)

**KRITIK — Container'da `hermes gateway restart` CALISMAZ:**

```
✗ Refusing to restart the gateway from inside the gateway process.
```

Gateway PID 1 olarak calistigi icin kendini restart edemez.

### Alternatif 1: kill -TERM 1 (Gateway reload, container kalmaz)

```bash
kill -TERM 1
# Gateway AYNI PID ile yeniden baslar, config yeniden okunur
# NOT: kill -HUP 1 YETMEZ — config yeniden yuklenmez
```

### Alternatif 2: kill -KILL 1 (Container restart)

```bash
kill -KILL 1
# Docker restart policy calisir, container yeniden baslar
# Config, npm install, script'ler korunur (HOME dizininde)
```

### Alternatif 3: Host'tan Docker restart (en guvenilir)

```bash
docker restart vanatis-hermes
```

### Gateway "deactivating (stop-sigterm)" Loop'u

Systemd user servisinde restart'ta olusursa:

```bash
systemctl --user status hermes-gateway | grep "Main PID"
kill -9 <PID>
systemctl --user start hermes-gateway
```

Detay: `server-maintenance` skill → "Gateway Restart Timeout" bolumu.

## Dogrulama

- `which context-mode` — binary PATH'te mi? Dogru yolda mi?
- `hermes tools list | grep context` — gateway MCP server'i goruyor mu?
- `ps aux | grep context-mode | grep -v grep` — process calisiyor mu?
- `mcp_context_mode_ctx_doctor` — tum kontroller PASS mi?
- `mcp_context_mode_ctx_search` — sorgu calisiyor mu?
