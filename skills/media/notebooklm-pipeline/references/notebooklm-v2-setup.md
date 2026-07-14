# NotebookLM v2 — Auth & Restart Prosedürü

> Güncelleme: 12 Temmuz 2026
> Sistem: notebooklm-mcp-cli v0.8.6 (jacob-bd/notebooklm-mcp-cli)

## Mimarî

```
┌─────────────────┐     CDP (port 18800)     ┌──────────────────┐
│  Keepalive      │◄────────────────────────►│  nlm CLI         │
│  Chrome         │   20dk'da bir cookie     │  Auth Profilleri │
│  (VNC erişim)   │   sync                  │  legacy/pro      │
└────────┬────────┘                          └────────┬─────────┘
         │                                            │
         │  nb_keepalive.py                           │ MCP stdio
         │  (her 20 dk cron)                          │
         ▼                                            ▼
┌──────────────────────────────────────────────────────────┐
│              Hermes Gateway (MCP Client)                  │
│              mcp_notebooklm_* (39 tool)                   │
└──────────────────────────────────────────────────────────┘
```

## Auth Yöntemi

**Birincil:** `nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --profile <name> --force`
- Keepalive Chrome'dan CDP ile cookie extract
- Multi-profile destekler: `legacy` (varsayılan — archive/memory), `pro` (Studio)

**Yedek:** `nlm login --manual -f cookies.json`
- Manuel cookie import

## Profiller (Edel talimatı, 12 Tem 2026)

| Profil | Hesap | Kullanım | Varsayılan? |
|--------|-------|----------|-------------|
| `legacy` | isimgorulsunn@gmail.com | **Varsayılan** — archive, source add, notebook query | ✅ Evet |
| `pro` | kenshin4155@gmail.com | **Sadece Studio** — audio, video, slide_deck, infographic, quiz | ❌ Hayır |

`nlm login switch legacy` ile varsayılan değiştirildi.
Profil değiştirme: `nlm login switch <pro|legacy>`

### ⚠️ Multi-Profile Tuzak (12 Tem 2026)

**Google `authuser` parametresi güvenilir DEĞİLDİR.** İki NotebookLM sekmesi farklı `authuser` değerleriyle açık olsa bile, aynı OSID hash'ine sahip olabilirler = **aynı Google hesabı.**

**İki farklı profili iki farklı hesaba bağlamak için:**
1. Keepalive Chrome'da **her iki Google hesabı da gerçekten oturum açmış olmalı**
2. Kontrol: CDP → `Network.getAllCookies` → notebooklm.google.com domain'inde **iki farklı OSID** cookie'si olmalı
3. `accounts.google.com` domain'inde her iki hesap için ayrı `__Secure-1PSID` cookie'leri olmalı
4. Doğrulama komutu:
```bash
nlm login --check --profile pro   # kenshin4155 olmalı
nlm login --check --profile legacy # isimgorulsunn olmalı
```
5. Her iki profil de sync sonrası **farklı hesap** göstermiyorsa → Chrome'da eksik oturum var demektir

## Source Add (Archive) — Doğrulanmış Yöntem

```bash
# ✅ ÇALIŞIYOR — file-based, markdown-safe
nlm source add <NOTEBOOK_ID> --file <wiki_md_path> --title "Başlık" --wait --wait-timeout 120

# ❌ ÇALIŞMIYOR — markdown özel karakterler kırıyor
# nlm add text <NOTEBOOK_ID> "$(cat file.md)" --title "..."   # HATA
```

## Kaynak Limiti

NotebookLM notebook başına ~50 kaynak alır. Backfill stratejisi:
- Sadece önemli konseptleri seçici ekle
- 716 wiki sayfasının tamamını backfill etme (15+ notebook gerekir)
- Dolu notebook'u döndür: yeni notebook oluştur, eskiyi arşivle

## Restart Prosedürü

### Container/Gateway restart
1. MCP server → Gateway otomatik başlatır (timeout: 120s)
2. Keepalive Chrome → Düşer, 20dk içinde cron ayağa kaldırır
3. Auth profilleri → `~/.notebooklm-mcp-cli/profiles/*/cookies.json` dosyada, kaybolmaz
4. NVIDIA provider → Config'de, kaybolmaz
5. BWS secret'ları → Gateway restart'ta otomatik yüklenir

### Keepalive Chrome düşerse
- `nb_keepalive.py` (her 20 dk cron) → `ensure_chrome_alive()` ile restart
- Başarısızsa → cron sonraki tick'te tekrar dener
- 3 başarısız deneme → Telegram SOS: "Manual VNC login needed"

### MCP auth düşerse
- `nlm login --check` ile tespit
- Keepalive sync otomatik (20dk'da bir)
- Manuel: `nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --profile legacy --force`

## Health Check

```bash
# MCP server durumu
hermes mcp list | grep notebooklm

# Auth durumu (profil bazlı kontrol)
nlm login --check --profile legacy   # Varsayılan — archive için
nlm login --check --profile pro      # Sadece Studio gerektiğinde

# Keepalive Chrome
curl -sf http://127.0.0.1:18800/json/version > /dev/null && echo "✅ Chrome CDP alive"

# nlm doctor
nlm doctor

# Full test (legacy profil ile)
nlm notebook list --limit 3 --profile legacy
```
