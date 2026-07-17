# Vanitas CONTEXT — Lighthouse Memory Architecture

## Version
- Architecture: Lighthouse v3.1 (6-layer)
- Created: 2026-06-26
- Previous: v3 (22 Jun 2026, broken — system_prompt_custom was invalid key, prefill was not JSON, MEMORY.md root-owned and over limit)

## Architecture Overview

Lighthouse is a 6-layer memory architecture for Vanitas (Hermes Agent). Each layer has a separate lifecycle, size limit, and purpose. The design prevents any single layer from causing memory bloat or session confusion.

### Theoretical Background
Lighthouse is inspired by Letta/MemGPT (Packer et al. 2023) which defines 3 tiers: Core Memory (identity), Recall Memory (conversation history), and Archival Memory (permanent knowledge). Lighthouse extends this with:
- TTL-based Hot Notes (Letta keeps all core memory permanently; Lighthouse rotates)
- Auto-archive threshold (Hot Notes → Library automatically; Letta requires manual archival_memory_insert)
- Layer separation (Persona vs Compass vs Hot Notes; Letta combines persona+rules in core memory)

## 6 Layers

### ACTIVE (always in system prompt context):

#### 1. PERSONA (SOUL.md)
- **Purpose:** Who Vanitas IS — personality, tone, communication style, time awareness, skill transparency
- **File:** `~/.hermes/SOUL.md`
- **Loaded by:** Hermes `load_soul_md()` → stable tier slot #1 (automatic)
- **Size limit:** 20,000 chars (context_file_max_chars), target ~4,000
- **Who writes:** Human (Edel) only. Vanitas CANNOT edit this.
- **What goes:** Identity, personality, conversation style, Turkish language quality, time awareness, skill transparency, memory philosophy (1-line), boundaries
- **What does NOT go:** Memory hierarchy details, server config, tool docs, capabilities list, anti-hallucination protocol

#### 2. COMPASS (AGENTS.md)
- **Purpose:** HOW Vanitas operates — protocols, server config, memory rules, anti-hallucination
- **File:** `~/.hermes/AGENTS.md`
- **Loaded by:** Hermes context tier (Gateway CWD = `~/.hermes/`)
- **Size limit:** 30,000 chars (context_file_max_chars), target ~15,000
- **Who writes:** Human (Edel) only. Vanitas can propose via write_approval system.
- **What goes:** Server context, update seal, BWS, sync protocol, Lighthouse hierarchy, anti-hallucination protocol, write rules, TTL system, session isolation, time awareness, calendar, wiki, tools, MCP servers, custom providers, voice, security
- **What does NOT go:** Personality (→ Persona), temporary facts (→ Hot Notes), user profile (→ USER.md)

#### 3. HOT NOTES (MEMORY.md)
- **Purpose:** What Vanitas knows NOW — short-term rotating buffer
- **File:** `~/.hermes/memories/MEMORY.md`
- **Loaded by:** Hermes volatile tier (frozen snapshot at session start)
- **Size limit:** 4,000 chars (memory_char_limit in config.yaml)
- **Who writes:** Vanitas freely (write_approval: true — Edel approves)
- **What goes:** Active project status, temporary configs, current research, recent errors, TTL-tagged entries
- **Entry delimiter:** `§` (section sign)

### ARCHIVE (on-demand via tools):

#### 4. LIBRARY (wiki_fts + ~/wiki/)
- **Purpose:** What Vanitas LEARNED — permanent knowledge
- **Storage:** `~/wiki/` directory + `wiki_fts` table in `state.db` (FTS5)
- **Size limit:** Unlimited
- **Who writes:** Vanitas via auto-archive (type=long) or manual wiki writes
- **Directories:**
  - `~/wiki/personal/conversations/` — personal conversations, life events
  - `~/wiki/entities/` — people profiles (Edel, contacts)
  - `~/wiki/experiences/` — life experiences, project logs
  - `~/wiki/vanitas-memory/` — auto-archived long-term memory entries
  - `~/wiki/apa-articles/` — academic articles
  - `~/wiki/arastirma/` — research notes
- **Search:** `session_search` or `wiki_fts` SQL query

#### 5. CHAT LOG (messages_fts)
- **Purpose:** What Vanitas DISCUSSED — all conversations
- **Storage:** `messages` + `messages_fts` tables in `state.db` (FTS5+BM25)
- **Size limit:** Unlimited (auto-growing, auto-pruned after 90 days)
- **Search:** `session_search` tool — returns actual messages with timestamps
- **Session isolation:** New session = clean slate. Cross-session search only when user explicitly asks ("hatırlıyor musun?", "earlier", "last time").

### VAULT (separate, browser-based):

#### 6. VAULT (NotebookLM)
- **Purpose:** Deep archive — audiobooks, long analyses, permanent reference
- **Access:** NotebookLM MCP server (browser automation, Chrome CDP port 18800)
- **Size limit:** Unlimited (Google-hosted)
- **NotebookLM ID:** `6c7f3daa-1640-4fad-9917-ec44bc432e58`
- **Status:** Auth issues (RotateCookiesPage stale) — separate fix needed

## Read Hierarchy (6-Step)

```
1. MEMORY.md + USER.md     (~5ms)  → active short-term memory (in system prompt)
2. session_search           (~50ms) → messages_fts (past conversations, FTS5+BM25)
3. Skills                   (auto)  → 43+ skills (procedural knowledge)
4. wiki_fts                 (~10ms) → 391+ wiki documents (FTS5)
5. NotebookLM               (10-30s)→ permanent reference archive
6. "I don't know"           (0ms)   → end of hierarchy
```

## Write Rules

| Info Type | Write To | TTL | After Expiry |
|-----------|----------|-----|-------------|
| Temporary config, API key, port | Hot Notes (short) | 7 days | Auto-deleted |
| Project status, preferences | Hot Notes (medium) | 60 days | Auto-deleted |
| Personal info, permanent rule | Hot Notes (long) | 365 days | Auto-archived to Library after 60 days, 1-line summary stays |
| Edel's personal details, relationship | USER.md | permanent | — |
| Learned knowledge, research | Library (wiki) | permanent | — |
| Personality, tone | Persona (SOUL.md) | permanent | Human only |
| Protocol, rules | Compass (AGENTS.md) | permanent | Human only |
| New skill | Skills directory | permanent | — |

**Vanitas can write to:** Hot Notes, USER.md, Library, Skills
**Vanitas CANNOT write to:** Persona, Compass (requires Edel approval via write_approval)

## TTL System

| Type | TTL | Use Case | After Expiry |
|------|-----|----------|-------------|
| short | 7 days | API key, proxy, port, token, temporary config | Auto-deleted |
| medium | 60 days | Project status, preferences, workflow | Auto-deleted |
| long | 365 days | Personal info, permanent rule, infrastructure | Auto-archived to Library after 60 days |

**Tracking:** `MEMORY_META.json` in `~/.hermes/memories/` — each entry has entry_id, type, ttl_days, added_ts, expires_date, content_preview, archived flag.

**Cleanup:** `lighthouse_cleanup_expired()` function in `memory_tool.py` — called at session start. Removes expired short/medium entries, archives long entries to wiki.

## Auto-Archive Mechanism

When `memory(add, entry_type=long)` is called:
1. Full entry written to `~/wiki/vanitas-memory/<topic>-<timestamp>.md`
2. `wiki_reindex.py` triggered → `wiki_fts` updated
3. Entry tracked in `MEMORY_META.json`
4. After 60 days: entry removed from MEMORY.md, 1-line summary stays

## Session Isolation

- **Default:** New session = clean slate. No context carried from previous sessions.
- **Cross-session search:** Only when user explicitly asks ("hatırlıyor musun?", "earlier", "last time")
  - Use `session_search` freely
  - Show results WITH session timestamp AND Telegram topic name (if available)
  - Say: "X konusunda Y topic'te (tarih) konuşmuştuk"
  - Prefer most recent 7 days, then search all
- **In-session:** Stay current, don't mix sessions.

## Time Awareness

- Hermes injects `"Conversation started: <date>"` in volatile tier (automatic)
- Persona (SOUL.md) instructs: check this timestamp before answering time questions
- Prefill reminder: "Check 'Conversation started' timestamp. Know today's date."
- When user says "today", "yesterday" → verify against timestamp, don't guess

## Anti-Hallucination Protocol

Located in Compass (AGENTS.md). Key rules:
- Certainty tags: [CONFIRMED], [LIKELY], [INFERRED], [UNCERTAIN], [UNKNOWN]
- Source citation required for every factual claim
- NEVER invent numbers, dates, fees, program names
- Accuracy Log: scan MEMORY.md for [ERROR] entries before answering
- Sub-agents (delegate_task) are UNRELIABLE — verify their output

## Prefill Messages

- **File:** `~/.hermes/prefill_accuracy.md` (JSON array format)
- **Content:** 7-point Lighthouse reminder injected at session start
- **Format:** `[{"role": "system", "content": "..."}]`
- **Purpose:** Remind Vanitas of architecture rules, session isolation, time awareness, skill transparency

## User Profile (USER.md)

- **File:** `~/.hermes/memories/USER.md`
- **Size limit:** 2,000 chars
- **Sections:**
  - **Profile:** Name, role, timezone, communication preferences, technical skill
  - **Bond:** Relationship development notes, personal shorthand ("Akademya" = Prompt Engineering program)
- **Who writes:** Vanitas freely (write_approval: true)

## Configuration (config.yaml)

Key settings changed for Lighthouse:
```yaml
memory:
  memory_char_limit: 4000      # was 2200
  user_char_limit: 2000        # was 1375
  write_approval: true          # was false

context_file_max_chars: 30000   # was 20000 (default)

# Removed:
# system_prompt_custom          # was invalid key, never loaded by Hermes

# Fixed:
# prefill_messages_file          # was text .md, now valid JSON array
```

## File Structure (Container ↔ Host)

```
Container path                                    Host path (Windows)
------------------------------------------------- ------------------------------------------
/home/ubuntu/.hermes/SOUL.md                     C:\VanitasDocker\data\hermes\SOUL.md
/home/ubuntu/.hermes/AGENTS.md                   C:\VanitasDocker\data\hermes\AGENTS.md
/home/ubuntu/.hermes/CONTEXT.md                  C:\VanitasDocker\data\hermes\CONTEXT.md
/home/ubuntu/.hermes/memories/MEMORY.md          C:\VanitasDocker\data\hermes\memories\MEMORY.md
/home/ubuntu/.hermes/memories/USER.md            C:\VanitasDocker\data\hermes\memories\USER.md
/home/ubuntu/.hermes/memories/MEMORY_META.json   C:\VanitasDocker\data\hermes\memories\MEMORY_META.json
/home/ubuntu/.hermes/config.yaml                 C:\VanitasDocker\data\hermes\config.yaml
/home/ubuntu/.hermes/prefill_accuracy.md         C:\VanitasDocker\data\hermes\prefill_accuracy.md
/home/ubuntu/wiki/                               C:\VanitasDocker\data\hermes\wiki\
/home/ubuntu/wiki/personal/conversations/        (new — personal conversation archives)
/home/ubuntu/wiki/vanitas-memory/               (new — auto-archived long-term entries)
/home/ubuntu/wiki/entities/                      (existing — people profiles)
/home/ubuntu/wiki/experiences/                    (existing — life experiences)
state.db                                          Container volume (Docker)
```

## memory_tool.py Extensions

Three Lighthouse functions added to `tools/memory_tool.py`:

1. **`_lighthouse_track_entry(target, content, entry_type)`** — Tracks new entries in MEMORY_META.json with TTL
2. **`_lighthouse_archive_to_wiki(content)`** — Archives long entries to `~/wiki/vanitas-memory/`
3. **`lighthouse_cleanup_expired()`** — Removes/archives expired entries (call at session start)

**add() method:** Extended with `entry_type` parameter (default: "short"). Core logic unchanged — additive only.

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-26 | Lighthouse v3.1 created | v3 had invalid system_prompt_custom, broken prefill, root-owned MEMORY.md, full AGENTS.md, bloated SOUL.md |
| 2026-06-26 | SOUL.md rebuilt (15.5k → 3.7k bytes) | Separated personality from protocols |
| 2026-06-26 | AGENTS.md rebuilt (20.5k → 10.8k bytes) | Moved protocols from SOUL.md, reorganized |
| 2026-06-26 | MEMORY.md rebuilt (2.3k → 0.8k bytes) | Old entries archived to wiki, chown ubuntu |
| 2026-06-26 | USER.md enriched (1.5k → 1.9k bytes) | Added Profile + Bond sections |
| 2026-06-26 | config.yaml: system_prompt_custom deleted | Invalid Hermes key — never loaded |
| 2026-06-26 | config.yaml: memory_char_limit 2200→4000 | Prevent future overflow |
| 2026-06-26 | config.yaml: write_approval true | Vanitas must ask before writing |
| 2026-06-26 | prefill_accuracy.md → JSON format | Hermes expects JSON array, was plain text |
| 2026-06-26 | memory_tool.py: type param + auto-archive + cleanup | Lighthouse TTL + auto-archive |
| 2026-06-26 | Wiki: ~/wiki/personal/ + ~/wiki/vanitas-memory/ | New directories for Lighthouse archive |
| 2026-06-26 | CONTEXT.md created | Architecture documentation |
| 2026-06-26 | NotebookLM Self-Healing Auth added | 4-layer auto-recovery system |

# NotebookLM Self-Healing Auth — Permanent Solution

## Overview

4-layer automatic authentication recovery. Designed for unattended operation —
when Edel lacks PC access, the system self-heals. Telegram SOS for edge cases.

## Architecture

```
Layer 1: nb_bootstrap_warmup.py  → container start + 30s → 1x initial check
Layer 2: nb_keepalive.py (loop)  → every 30min (stale) or 4hours (valid)
Layer 3: nb_autologin.py         → BWS creds + TOTP → CDP auto Google login
Layer 4: nb_telegram_alert.py    → 3x fail → Telegram SOS to Edel
```

## Components

### nb_bootstrap_warmup.py (new)
- Runs 30 seconds after container start
- Invokes nb_keepalive.py one time, then exits
- Catches early auth expiry during first 2 hours after start

### nb_keepalive.py (modified, 147→249 lines)
- Auth check via `nlm notebook list` (HTTP validation, not just file check)
- If valid: navigate Chrome to notebooklm.google.com, refresh cookies
- If invalid: invoke nb_autologin.py, exponential backoff 30s→60s→120s, MAX_RETRIES=3
- If 3x fail: invoke nb_telegram_alert.py
- Adaptive interval: SUCCESS → 14400s (4h), FAIL → 1800s (30min)
- Log: `~/.hermes/logs/nb_keepalive.log` + `~/.hermes/logs/nb_keepalive_loop.log`
- Lock file: `~/.hermes/logs/nb_keepalive.lock`

### nb_autologin.py (modified, 212→363 lines)
- Get Google email+password from Bitwarden via bw-serve HTTP API (port 8087)
- Generate TOTP via `pyotp` using `~/.hermes/.nb_totp_secret`
- CDP login flow: account chooser → email → password → TOTP → "try another way"
- **NEW: RotateCookiesPage handler** — detect and re-navigate to NotebookLM
- **NEW: Captcha/challenge detection** — fail gracefully, log specific reason
- **NEW: Phone verification detection** — fail + alert via nb_keepalive retry
- **NEW: "Verify it's you" / suspicious activity detection**
- **NEW: TOTP option selector** — navigate to "Authenticator app" after "try another way"
- **NEW: Lock file** — prevent parallel execution via PID check
- **NEW: Fail reason file** — `~/.hermes/logs/nb_autologin_fail_reason.txt`
- **FIX: WebSocket import** — uses `websocket-client` (v1.9.0), not `websockets`
- **FIX: Unique message IDs** — counter incremented per CDP call

### nb_telegram_alert.py (new, ~80 lines)
- Reads `TELEGRAM_BOT_TOKEN` (env, 46 chars) and `TELEGRAM_HOME_CHANNEL` (env, `-1003917030255:12`)
- Parses channel: chat_id=`-1003917030255`, message_thread_id=`12`
- Sends via Telegram Bot API HTTP POST
- Zero dependencies (only urllib)
- Confirmed working 200 OK with test message (message_id 15510)

### entrypoint.sh (modified, lines 139-150)
- Old: `nlm login --provider openclaw --cdp-url 18800` (cookie-extract only, no Google login)
- New:
  ```bash
  # Bootstrap: immediate first check
  gosu ubuntu python3 ~/.hermes/scripts/nb_bootstrap_warmup.py &
  # Loop: adaptive interval
  (
    INTERVAL=3600
    while true; do
      sleep $INTERVAL
      gosu ubuntu python3 ~/.hermes/scripts/nb_keepalive.py >> ~/.hermes/logs/nb_keepalive_loop.log 2>&1
      if tail -50 ~/.hermes/logs/nb_keepalive_loop.log | grep -q "Auth expired"; then
        INTERVAL=1800
      else
        INTERVAL=14400
      fi
    done
  ) &
  ```

## Dependencies
- `pyotp>=2.9` — TOTP generation. Installed via pip3, persisted in `~/.hermes/scripts/requirements.txt`
- `websocket-client>=1.9.0` — CDP WebSocket. Already installed in container.
- `bw serve` on port 8087 — Bitwarden HTTP API. Auto-started + auto-unlocked by entrypoint.sh
- Chrome CDP on port 18800 — Xvfb :99, headless Chromium 149. Auto-started by entrypoint.sh
- TOTP secret: `~/.hermes/.nb_totp_secret` (33 bytes)

## File Structure

```
/home/ubuntu/.hermes/scripts/
├── nb_autologin.py           # CDP Google login (Bitwarden + TOTP) — 363 lines
├── nb_keepalive.py           # Auth lifecycle (check → refresh → autologin → alert) — 249 lines
├── nb_telegram_alert.py      # 3x fail → Telegram SOS — 80 lines
├── nb_bootstrap_warmup.py    # 1x initial check after container start — 40 lines
├── start-chrome-keepalive.sh # Chromium launcher (existing, unchanged)
└── requirements.txt          # pyotp + websocket-client dependencies

/home/ubuntu/.hermes/logs/
├── nb_keepalive.log           # appended by nb_keepalive.py
├── nb_keepalive_loop.log      # appended by entrypoint.sh keepalive loop
├── nb_keepalive.lock          # pid file (prevent parallel)
├── nb_autologin.lock          # pid file (prevent parallel)
├── nb_autologin_fail_reason.txt # last failure reason
└── nb_last_login.txt          # last successful cookie refresh timestamp

/home/ubuntu/.notebooklm-mcp-cli/
├── profiles/
│   ├── default/
│   │   ├── auth.json          # cookies, CSRF, session ID, email
│   │   └── metadata.json
│   └── pro/                   # (optional — for NotebookLM Pro account)
│       └── auth.json
└── chrome-profiles/
    └── default/               # persistent browser profile for nlm login (auto mode)
```

## Cookie Export Alternative (PC-free manual fallback)

If auto-login fails 3x AND VNC is unavailable (e.g., Edel only has phone):

1. On a Mac/Windows with Chrome logged in:
   - Go to `https://notebooklm.google.com`
   - Press F12 → Network tab → filter: `batchexecute`
   - Click any notebook → find `batchexecute` request in list
   - In right panel, scroll to Request Headers
   - Find `cookie:` line → right-click value → Copy value
   - Paste into a text file: `SID=...; HSID=...; SSID=...; ...`
2. Transfer to container:
   - `docker cp cookies.txt vanatis-hermes:/tmp/cookies.txt`
   - `docker exec vanatis-hermes gosu ubuntu nlm login --manual --file /tmp/cookies.txt`
3. Cookies persist for weeks. Profile written to `~/.notebooklm-mcp-cli/profiles/default/auth.json`

## Multi-Profile Support (Pro account)

nlm v0.7.7 supports named profiles:
- `nlm login --profile pro` → pro account, separate browser session + credentials
- `nlm login --profile default` → current account
- `nlm login switch pro` → set pro as default
- Each profile gets own `auth.json`, browser session, cookies
- MCP server uses default profile only. To switch: `nlm login switch pro`

## Retry Flow (Visual)

```
nb_keepalive.py runs (every 30min-4h)
  ├─ nlm notebook list → success?
  │   ├─ YES: navigate Chrome, nlm login refresh cookies, set interval=4h, exit
  │   └─ NO: invoke nb_autologin.py (attempt 1/3)
  │       ├─ success → refresh cookies, exit
  │       └─ fail → sleep 30s → attempt 2/3
  │           ├─ success → refresh cookies, exit
  │           └─ fail → sleep 60s → attempt 3/3
  │               ├─ success → refresh cookies, exit
  │               └─ fail → invoke nb_telegram_alert.py
  │                   └─ "NotebookLM auth expired. Manual login needed.
  │                       Cookie export: see CONTEXT.md NotebookLM section."
  │                   → set interval=30min (faster retries)
  └─ release lock, exit
```

## Detection Matrix (nb_autologin.py)

| Scenario | Detection | Action |
|----------|-----------|--------|
| Already logged in | URL contains notebooklm.google.com | Return success |
| Account chooser | `[data-identifier="email"]` element | Click account |
| Email input | `#identifierId` selector | Type email, click Next |
| Password input | `input[type=password]` | Type password, click Next |
| TOTP (2FA) | `input[autocomplete="one-time-code"]` | Generate TOTP, type, submit |
| RotateCookiesPage | URL contains `RotateCookiesPage` | Wait + re-navigate to NotebookLM |
| "Try another way" | Button text match | Click → look for TOTP option |
| TOTP option link | Text contains "Authenticator app" | Click → TOTP flow |
| Captcha (reCAPTCHA/hCaptcha) | Element detection + body text | Log fail reason, return False |
| Phone verification | Body text contains "phone/text message" | Log fail reason, return False |
| Suspicious activity | Body text "Verify it/suspicious" | Log fail reason, return False |
| Timeout (15 attempts) | Counter reaches 15 | Log fail reason, return False |

## Validation Steps

After build:
1. `python3 -c "import pyotp; print(pyotp.TOTP('JBSWY3DPEHPK3PXP').now())"` → works ✓
2. `python3 ~/.hermes/scripts/nb_telegram_alert.py --message "alert test"` → Telegram message received ✓
3. Cookie Export or VNC login → `nlm login --check` → "Authentication valid!"
4. `python3 ~/.hermes/scripts/nb_keepalive.py` → runs cleanly, logs visible
5. `docker restart vanatis-hermes` → 30s later bootstrap warmup fires

## Changelog (NotebookLM)

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-26 | nb_auth_refresh.sh removed | Used invalid old binary `/usr/local/bin/notebooklm-mcp` |
| 2026-06-26 | nb_telegram_alert.py created | Edel needs SOS when auth fails during PC-absent periods |
| 2026-06-26 | nb_bootstrap_warmup.py created | Initial auth check 30s after container start avoids 2h gap |
| 2026-06-26 | nb_keepalive.py enhanced (147→249 lines) | 3x retry + exponential backoff + adaptive interval + Telegram |
| 2026-06-26 | nb_autologin.py enhanced (212→363 lines) | RotateCookiesPage handler, challenge detection, lock file, TOTP option |
| 2026-06-26 | entrypoint.sh modified | Loop now calls nb_keepalive.py instead of manual nlm login |
| 2026-06-26 | pyotp installed (v2.10.0) | nb_autologin.py crashes on missing TOTP library |
| 2026-06-26 | requirements.txt created | Persist pyotp across container restarts |
| 2026-06-27 | Lighthouse auto-cleanup 3-layer trigger | add()>75%, entrypoint 6h loop, bootstrap warmup |
| 2026-06-27 | MEMORY.md/USER.md konsolide (4k→1.3k, 2k→1.3k) | Cleanup eksigi nedeniyle limite ulasildi |
| 2026-06-27 | NotebookLM 3-layer direktif enjeksiyonu | Vanitas /new sonrasi da nlm login oneriyordu |

## NotebookLM Direktif Sorunu ve Fix (27 Haz 2026)

### Sorun
Vanitas `/new` yapildiktan sonra bile NotebookLM auth stale gorununce "nlm login --wsl" veya PowerShell firewall kurali oneriyordu.
Sebebi: Eski session aliskanligi + Compass direktifi tek katmanda zayif kaliyordu.

### Cozum — 3 Katmanli Direktif Enjeksiyonu
Ayni mesaji 3 farkli bellek katmanina enjekte ettik:
1. **SOUL.md (Persona):** "NotebookLM Auth Protocol (CRITICAL)" — 6 satir, Boundaries oncesi
2. **prefill_accuracy.md (Prefill):** 8. madde — her session basinda model gorur
3. **AGENTS.md (Compass):** "CRITICAL OVERRIDE - old habits die hard" — 5 satir daha guclu

### Wissen suçtiquons ilgiii çe üst
- Single-layer direktif (sadece Compass) yetersizdi
- 3-katmanli enjeksiyon: Persona+Prefill+Compass ayni mesaji farkli formatlarda verir
- Model eski aliskanliga kayarsa prefill "HAYIR nb_keepalive calistir" der
- Compass okumazsa SOUL.md (her zaman yuklu) gorur
- SOUL.md ozet okursa Compass detaya iner

# Provider Model Picker Gorunurluk Fix (17 Tem 2026)

## Sorun

Telegram `/model` picker'inda buyuk provider'larda (ornegin NVIDIA ~119 model) istenen
model `max_models=50` truncation'i nedeniyle listede gorunmuyordu. `z-ai/glm-5.2`
alfabetik sirada ~113. oldugu icin ilk 50'de cikmiyordu.

Sebep zinciri:
1. Hermes, models.dev tarafindan tercih edilen (`_MODELS_DEV_PREFERRED`) provider'lar
   icin `cached_provider_model_ids()` fonksiyonunu kullanir
2. Bu fonksiyon models.dev katalogundaki TUM modelleri dondurur (119 adet)
3. Picker `max_models=50` ile ilk 50'yi gosterir
4. `z-ai/glm-5.2` alfabetik sirada 113. → truncate → gorunmez

**Not:** Model vardi ve `/model glm-5.2` yazarak secilebiliyordu, ama picker'da
gorunmedigi icin kesfedilemiyordu.

## Cozum: `usercustomize.py` Monkey-Patch

`site-packages/usercustomize.py` dosyasi, Python'un `sys.meta_path` mekanizmasini
kullanarak `hermes_cli.models` modulunun yuklenmesini intercept eder. Modul
yuklendikten sonra iki patch uygular:

1. **`_PROVIDER_MODELS['nvidia']`** — curated listeye `z-ai/glm-5.2` ekler
2. **`cached_provider_model_ids()`** — NVIDIA icin model listesinin BASINA `z-ai/glm-5.2`'yi
   tasir. Bu sayede picker'da HER ZAMAN ilk sirada gorunur.

### Calisma Prensibi

```python
# sys.meta_path uzerinden hermes_cli.models yuklenmesini yakala
class _NvidiaPatcherFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname != "hermes_cli.models":
            return None
        # Gercek spec'i bul, loader'i bizim patcher ile sar
        ...

# Modul yuklendikten sonra:
def exec_module(self, module):
    self._real.exec_module(module)
    
    # Patch 1: curated listeye ekle
    nv = module._PROVIDER_MODELS.get("nvidia")
    nv.append("z-ai/glm-5.2")
    
    # Patch 2: cached_provider_model_ids'i override et
    # → NVIDIA'da z-ai/glm-5.2'yi liste basina tasi
    _orig = module.cached_provider_model_ids
    def _patched(provider):
        result = list(_orig(provider))
        if provider == "nvidia" and "z-ai/glm-5.2" in result:
            result.remove("z-ai/glm-5.2")
            result.insert(0, "z-ai/glm-5.2")
        return result
    module.cached_provider_model_ids = _patched
```

### Yeni Model Eklemek Icin

Baska bir modeli picker'da ust siralara tasimak gerekirse:

1. `usercustomize.py` icindeki `_patched_cached()` fonksiyonuna yeni model ekle
2. Model adini (ornegin `z-ai/glm-5.2`) `insert(0, ...)` ile basa ekle
3. Container restart

```python
# Ornek: minimax-m3'u de basa ekle
if provider == "nvidia":
    for mid in ["z-ai/glm-5.2", "minimaxai/minimax-m3"]:
        if mid in result:
            result.remove(mid)
            result.insert(0, mid)
```

### Kalicilik

- Dosya: `/home/ubuntu/.local/lib/python3.11/site-packages/usercustomize.py`
- Host yedegi: `C:\VanitasDocker\data\hermes\scripts\usercustomize.py`
- Container restart'ta otomatik yuklenir (Python site-customize mekanizmasi)
- Hermes imaji guncellense bile calisir (ayri bir dosya, pip install override etmez)
- **Dikkat:** Python minor versiyonu degisirse (3.11 → 3.12) dosya yolu guncellenmeli

### Ilgili Dosyalar

| Container | Host | Amac |
|-----------|------|------|
| `~/.local/lib/.../usercustomize.py` | `scripts/usercustomize.py` | Monkey-patch |
| `hermes_cli/models.py` | (hermes paketi) | `cached_provider_model_ids` |
| `hermes_cli/model_switch.py` | (hermes paketi) | `list_picker_providers` |
| `gateway/run.py` line ~11080 | (hermes paketi) | `max_models=50` |

## Changelog (Model Picker)

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-17 | `usercustomize.py` enhanced | `cached_provider_model_ids` monkey-patch ile glm-5.2 basa tasindi |
| 2026-07-17 | CONTEXT.md updated | Yontem dokumante edildi, Vanitas'a referans |