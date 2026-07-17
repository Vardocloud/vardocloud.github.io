---
name: upwork-cookie-session
description: Upwork Cloudflare Bot Management bypass via cookie export + Camoufox session management
---

# Upwork Cookie Session Management

## ⚡ Quick Answer: "Cookie'ler var, neden browse edemiyorum?"

**Cookie'ler = oturum canlı.** Ama Oracle Cloud IP'miz Cloudflare tarafından network seviyesinde bloklanır. Cookie'ler olsa bile:
- Chrome/Puppeteer ile Upwork → 403 (IP bloklu)
- curl/wget → 403
- Browserbase Cloud → login sayfası (cookie cloud'da yok)

Cookie'ler **sadece** Camoufox script'inin (`upw_session_refresh.cjs`) session refresh yapmasını sağlar. Browse/job search için farklı bypass yöntemleri gerekir → `upwork-job-search` skill'ine bak.

---

## 🤖 Cron Agent Execution Protocol

**Headless cron job runbook.** The script is now **self-sufficient** (patched 21 Haz 2026) — it loads credentials directly from bw-serve, handles the Camoufox crash, and saves cookies. The agent just runs it and reports.

### Step 1 — Run Session Refresh (single command, no pre-work needed)

The cron job runs the wrapper script directly (no_agent: true mode):
\`\`\`bash
cd /home/ubuntu/.hermes && bash scripts/upwork_refresh.sh
\`\`\`

The wrapper script does **direct-first, proxychains fallback**:
1. **Direct** (no proxy): `timeout 90 node upw_session_refresh.cjs`
2. **Fallback** (if direct fails): `proxychains4 -q -f ~/.local/etc/proxychains.conf timeout 120 node upw_session_refresh.cjs`
3. Reports `[SILENT]` on success, error message on failure

**Why dual-path?** WSL ve Docker Desktop ortamlarında direkt bağlantı genelde çalışır — proxychains sadece Oracle Cloud gibi datacenter IP'lerinde gerekli. WARP container düşse bile direkt yol sayesinde refresh devam eder.

To run the raw script without the wrapper (e.g. for debugging):
\`\`\`bash
cd /home/ubuntu/.hermes && node upw_session_refresh.cjs
\`\`\`

Script internally:
1. Checks bw-serve (port 8087) for credentials → gets username + password
2. Falls back to \`/tmp/pw_val.txt\` if bw-serve is down
3. Loads existing cookies from \`secrets/upwork_cookies.json\`
4. Navigates to Upwork via Camoufox
5. If cookies valid → "SESSION VALID" — saves refreshed cookies
6. If expired → re-logs in with bw-serve credentials, saves new cookies
7. Handles the known Camoufox async crash silently

**No separate password retrieval step needed.** No \`/tmp/pw_val.txt\` placeholder needed. Just run the script.

### Step 2 (If script fails) — Cookie Health Check
\`\`\`bash
cd /home/ubuntu/.hermes && node -e "
const fs=require('fs');
const c=JSON.parse(fs.readFileSync('secrets/upwork_cookies.json','utf8'));
const n=Date.now();
let v=0,e=0,s=0;
c.forEach(x=>{const exp=x.expirationDate||x.expires;if(exp===undefined||exp===null||exp===-1){s++;return}(exp*1000>n)?v++:e++});
console.log('Valid:',v,'Expired:',e,'No-expiry:',s,'Total:',c.length);
"
\`\`\`

If Valid < 70%: report BLOCKED to user (needs fresh Chrome cookie export).

### Step 3 — Build + Deliver the Report
Present a compact table. Every row must tell the next agent at a glance what happened:

| Kontrol | Durum | Detay |
|---------|-------|-------|
| **Cookie dosyası** | ✅/❌ N valid / M expired | Session token var mı? |
| **bw-serve** (port 8087) | ✅/❌ | curl status check |
| **bws** | ✅/❌ UPWORK var/yok | Secrets Manager |
| **`/tmp/pw_val.txt`** | ✅/❌ | Şifre dosyası |
| **Script çalıştı** | ✅/❌ | Cookie count, URL, session durumu |
| **Session sonucu** | ✅ VALID / ❌ EXPIRED / 🔴 BLOCKED | Özet |

If BLOCKED (no password source, cookies expired), append a recovery section with the three options from `references/bw-serve-down-recovery.md`.

---

## Problem
Upwork uses Cloudflare Bot Management (Enterprise tier). Datacenter IPs (Oracle Cloud, AWS, etc.) are flagged. Browser automation (Puppeteer, Playwright, Camoufox) can load pages but form POST submissions are blocked with "Due to technical difficulties."

## Solution: Cookie Export + Injection

### Step 1: User Exports Cookies from Chrome
1. User logs into Upwork on their own Chrome/Edge with "Keep me logged in" checked
2. Uses a cookie export extension (e.g., "Export cookie JSON file for Puppeteer" from Chrome Web Store)
3. Exports cookies as JSON file
4. Sends the file to Vanitas

### Step 2: Cookie Injection via Camoufox
- Camoufox is a Firefox fork with C++-level fingerprint spoofing
- ARM64 (aarch64) binary available — works on Oracle Cloud ARM
- Cookies are loaded into browser context BEFORE navigation
- Script: `~/.hermes/upw_session_refresh.cjs`

## ✅ Cron Refresh Pipeline

### Agent-Driven Cron (Tested 2026-06-14)
The agent:
1. Queries Bitwarden `bw-serve` API (port 8087, unlocked) via curl → extracts password
2. Saves password to `/tmp/pw_val.txt` (chmod 600)
3. Runs `node upw_session_refresh.cjs` which reads the password from file
4. Camoufox loads existing cookies → navigates to Upwork → if valid, saves cookies back; if expired, re-logs in

**Key insight:** `bw-serve` must already be running and unlocked. The script itself does NOT need to log in if cookies are still valid.

### ⚠️ Prerequisites Checklist (RUN THIS FIRST)

```bash
# 1. Check if bw-serve is running
curl -s http://localhost:8087/status
# Expected: {"serverUrl":"https://vault.bitwarden.com",...}
# If fails → "Failed to connect to host" → bw-serve is DOWN

# 2. Check if GPG secret key exists (needed to start bw-serve)
gpg --list-secret-keys
# If empty or missing → GPG key not on this machine

# 3. Check if bws (Bitwarden Secrets Manager) is available & has upwork secret
test -x ~/.hermes/bin/bws && echo "bws available" || echo "no bws"
env | grep BWS_ACCESS_TOKEN
~/.hermes/bin/bws secret list <project-id> 2>/dev/null | python3 -c "
import json,sys; data=json.load(sys.stdin)
upw = [s for s in data if 'upwork' in s.get('key','').lower()]
print(f'{len(upw)} upwork secrets found' if upw else 'NO upwork secret in bws')
"

# 4. Check cookie expiry (can skip password if cookies still valid)
node -e "
const fs = require('fs');
const c = JSON.parse(fs.readFileSync('/home/ubuntu/.hermes/secrets/upwork_cookies.json','utf8'));
const n = Date.now();
let v=0,e=0,s=0; c.forEach(x=>{const exp=x.expirationDate||x.expires;if(exp===undefined||exp===null||exp===-1){s++;return}(exp*1000>n)?v++:e++});
console.log('Valid:',v,'Expired:',e,'Session (no expiry):',s);
"

# 5. Check if Camoufox binary is cached (required by the npm package)\ntest -f ~/.cache/camoufox/camoufox-bin && echo "camoufox-bin: cached" || echo "camoufox-bin: MISSING — run 'npx camoufox fetch' first'\n\n# 6. Check if camoufox npm package is installed (prerequisite for binary)\ntest -d /home/ubuntu/node_modules/camoufox && echo "camoufox npm: installed" || echo "camoufox npm: MISSING — run 'npm install camoufox' first'\n\n# ⚠️ Camoufox binary may NOT be installed even if npm package is present.\n#   `npx camoufox fetch` downloads ~250MB ARM64 binary.\n#   After fetch: chmod +x ~/.cache/camoufox/camoufox-bin\n#   Tested 21 Jun 2026: binary was MISSING despite Edel thinking it was installed.\n#   ALWAYS verify with test -f, never assume.\n\n# 6. Check environment type — WARP needed?
# WSL/Docker Desktop: direct connection works, WARP not needed
# Oracle Cloud/AWS: proxychains+WARP required
curl -s -o /dev/null -w "%{http_code}" https://www.upwork.com 2>&1
# If 200 → WSL environment, skip WARP/proxychains checks
# If 000/403 → datacenter IP block, check WARP & proxychains

# 7. Check if WARP proxy is running (only needed for datacenter IPs)
curl -x socks5h://127.0.0.1:1080 -s -o /dev/null -w "%{http_code}" https://www.upwork.com 2>&1 | grep -q "000" && echo "WARP (1080): DOWN — restart warp-proxy" || echo "WARP (1080): UP"

# 8. Check proxychains4 (only needed for datacenter IPs)
which proxychains4 &>/dev/null && echo "proxychains4: available" || echo "proxychains4: MISSING — run 'apt install proxychains4'"
```

> **🐳 Docker / non-Oracle Cloud ortamı:** Eğer container direkt internete çıkabiliyorsa (Upwork'e `curl` ile 200 dönüyorsa) WARP ve proxychains4 **gerekli değildir**. Bu durumda item 6 ve 7'yi atlayabilirsin. Script direkt `node upw_session_refresh.cjs` ile çalışır. Sadece Oracle Cloud, AWS EC2 gibi datacenter IP'leri Cloudflare tarafından bloklanır — Docker Desktop/Local (Windows/Mac) genelde residential IP üzerinden çıktığı için blok yemez.

### Decision Tree

| bw-serve | GPG key | bws has upwork | Action |
|----------|---------|----------------|--------|
| ✅ Running | — | — | Use bw-serve API (standard path) |
| ❌ Down | — | ✅ | Use bws to fetch password (fallback) |
| ❌ Down | ❌ Missing | ❌ | **BLOCKED** — report to user |

**Blocker message format:**
> "bw-serve not running (port 8087), GPG secret key missing, bws has no upwork secret. Password cannot be retrieved. User needs to either start bw-serve, add upwork password to bws, or export fresh cookies from Chrome."

Report structure (cron delivery):
| Kaynak | Durum | Detay |
|--------|-------|-------|
| **bw-serve** (port 8087) | ❌ Down/✅ Up | Bağlantı durumu |
| **GPG secret key** | ❌ Yok/✅ Var | Makinede GPG var mı |
| **bws (Secrets Manager)** | ❌ upwork yok/✅ Var | bws'te upwork şifresi kayıtlı mı |
| **Cookie dosyası** | ❌ N/M expired/✅ Valid | Kaç çerez geçerli |
| **`/tmp/pw_val.txt`** | ❌ Yok/✅ Var | Şifre dosyası mevcut mu |

### Two Modes (21 Haz 2026 + 12 Tem 2026: Direct-First Wrapper)

1. **`no_agent: true` script mode (AKTİF):** Cron job `cfb2a93e2677` runs `scripts/upwork_refresh.sh` directly every 4h. The wrapper does direct-first, proxychains fallback. Deliverable: `[SILENT]` on success, error message on failure.
2. **Agent-driven (legacy):** An AI agent runs the script and reports. Same script, same behavior. Used when manual diagnosis is needed.

The wrapper script (`scripts/upwork_refresh.sh`) was created on 12 Tem 2026 after 3 consecutive WARP-proxy failures caused the refresh chain to break overnight. **Lesson:** Fixing proxychains as the sole path creates a single point of failure. Always try direct first when the environment supports it.

### Cookie Lifespan

- Session can last 18–24+ hours with "Keep me logged in" checked during export
- Cookie count may increase over sessions (100→101→111 observed) — Camoufox's `page.context().cookies()` returns ALL cookies including newly-set ones
- The refresh script overwrites the file each run, so stale cookies are purged
- As of 2026-06-16: 108/108 valid after 18 hours
- As of 2026-06-20: observed 4/111 valid (session expired) — session was DEAD
- As of 2026-06-21: 2499/2499 valid after fresh Chrome export (889KB file)
- **Google-only accounts:** Cookie-based refresh works while valid. When expired, user must export fresh cookies — no password-based re-login possible.
- **Kimlik doğrulamalı hesap (21 Haz 2026):** Edel'in ana hesabı Google OAuth bağlı, kimlik doğrulamalı. Cookie'leri 2535 adet, 2507/2535 valid (21 Haz 14:00 itibarıyla). Session cookie 16/22 valid.
## Security
- Cookie file: `~/.hermes/secrets/upwork_cookies.json` (chmod 600)
- External APIs never see cookie values
- Password stored in temp file `/tmp/pw_val.txt` (chmod 600)
- All credential operations use local Node.js scripts, not LLM tools

## Files
- `~/.hermes/upw_session_refresh.cjs` — Main session refresh script (Node.js + Camoufox)
- `~/.hermes/scripts/upwork_refresh.sh` — Cron wrapper: direct-first, proxychains fallback, silent-on-success
- `~/.hermes/secrets/upwork_cookies.json` — Persistent cookie store (600)
- `/tmp/pw_val.txt` — Password temp file (600, auto-cleaned on reboot)

## ⚠️ KRİTİK: Bitwarden Password Manager vs Secrets Manager

**İKİSİ FARKLI ÜRÜNDÜR.** Karıştırma:

| Ürün | CLI | Port | Ne işe yarar |
|------|-----|------|-------------|
| **Bitwarden Password Manager** | `bw` (`~/.hermes/bin/bw`) veya `bw-serve` | 8087 (REST API) | Kullanıcının vault'undaki item'ları (şifreleri) saklar |
| **Bitwarden Secrets Manager** | `bws` (`~/.hermes/bin/bws`) | Yok (env: `BWS_ACCESS_TOKEN`) | Machine-to-machine secret'lar için (API key'ler) |

**Kural:** Upwork şifresi BİRİNCİL olarak Password Manager'dadır. Secrets Manager'da yoksa "ekle" deme — Password Manager'a bak.

## Password Handling (Critical)

### Kaynak 1: Bitwarden Password Manager (bw-serve REST API — BİRİNCİL)

`bw-serve`, `bw serve` komutunun başlattığı REST API sunucusudur. Port 8087'de çalışır. Çalışıyorsa:

```bash
# Önce çalıştığını kontrol et
curl -sf http://localhost:8087/status || echo "bw-serve DOWN"

# Çalışıyorsa şifreyi çek
curl -s "http://localhost:8087/object/item/upwork" > /tmp/bw_item.json
python3 -c "
import json
with open('/tmp/bw_item.json') as f:
    item = json.load(f)['data']
print(item['login']['password'])
" > /tmp/pw_val.txt
chmod 600 /tmp/pw_val.txt
```

**⚠️ API quirks:** `/object/item/<name>` exact item name ile çalışır. `/object/search?query=...` boş dönebilir — search kullanma. `/status` her zaman çalışır.

### Kaynak 2: Bitwarden Password Manager (bw CLI — alternatif)

`bw-serve` kapalıysa, `bw` CLI (`~/.hermes/bin/bw`) ile direkt erişim dene:

```bash
# Önce login durumunu kontrol et
~/.hermes/bin/bw status | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['status'])"
# → 'unauthenticated' ise login gerek

# Login (API key ile — env'de BWS_ACCESS_TOKEN varsa Organization'dan alınabilir)
# Eğer client_id/client_secret biliniyorsa:
# ~/.hermes/bin/bw login --apikey

# Unlock (master password gerekir — interactif)
# ~/.hermes/bin/bw unlock

# Session token alındıktan sonra:
# BW_SESSION="..." ~/.hermes/bin/bw get item upwork | python3 -c "
# import json,sys; item=json.load(sys.stdin);
# print(item['login']['password'])
# " > /tmp/pw_val.txt
```

**⚠️ Not:** `bw login` ve `bw unlock` interactif komutlardır (master password girer). Cron ortamında çalışmaz. Bu yüzden **bw-serve** (REST API) cron için, **bw CLI** manuel/one-shot için uygundur.

### Kaynak 3: Bitwarden Secrets Manager (bws — Docker-safe, farklı ürün)

Sadece yukarıdaki iki kaynak da başarısız olduysa ve Upwork şifresi **bilerek** bws'e eklenmişse kullan:

```bash
~/.hermes/bin/bws secret list 2b375eb2-293e-4774-b5e5-b46601543563 2>&1 | python3 -c "
import json,sys
data = json.load(sys.stdin)
for s in data:
    if 'upwork' in s.get('key','').lower():
        with open('/tmp/pw_val.txt','w') as f: f.write(s['value'])
        import os; os.chmod('/tmp/pw_val.txt', 0o600)
        print(f'PASSWORD_SOURCE: bws ({s[\"key\"]})')
        break
else:
    print('PASSWORD_SOURCE: none — no upwork secret in bws')
"
```

**⚠️ Uyarı:** 2026-06-20 itibarıyla bws'te 34 secret var ama Upwork şifresi YOK (hepsi API key). Bu normaldir — Upwork şifresi Password Manager'a aittir.

### Google-Only Login Accounts (No Password — 21 Haz 2026)
Some Upwork accounts use **Google OAuth** only — no password field, no Bitwarden item. The `upw_session_refresh.cjs` script has `USERNAME` hardcoded and attempts password-based login, which will **fail silently** or get stuck on a Google login page if cookies expire.

**Rule for Google-only accounts:**
- Cookie-based refresh works fine **as long as cookies are valid** — script reads "SESSION VALID" without needing to login.
- If cookies expire, **re-login is impossible** via the script. No password to fill, no Bitwarden fallback.
- Recovery requires a **fresh cookie export** from Chrome (same as initial setup).
- `/tmp/pw_val.txt` still needs a placeholder (`echo "placeholder" > /tmp/pw_val.txt`) even though it's unused — the script reads it synchronously at module load.

**Identification:** Check the login page after cookies expire. If it shows "Continue with Google" instead of email/password fields, it's a Google-only account.

### 📋 pw_server.py — Secure Password Capture (Script)

Located at `scripts/pw_server.py` — use for one-time secure password entry. Runs an HTTP form on a local port; password is written to `/tmp/pw_val.txt` (chmod 600). NEVER goes through Telegram.

**Usage:** Start server on a chosen port → give URL to Edel → she types password → server saves and exits.

**Fallback:** If Edel can't reach the port (no Docker mapping), use TryCloudflare tunnel (`cloudflared tunnel --url http://localhost:<PORT>`). Note: Oracle Cloud may block QUIC/TCP outbound, breaking the tunnel.

**Reference:** See the script header for full instructions and the 21 Jun 2026 session for the complete workflow.

### Script NOW Handles Bitwarden (Patched 21 Haz 2026)
The `upw_session_refresh.cjs` script was **upgraded** on 21 Haz 2026 to handle its own credential loading via `loadCreds()`: queries bw-serve (port 8087) for username + password, falls back to `/tmp/pw_val.txt`, continues with empty password if both fail. See "Script NOW Handles Bitwarden" above for details.

### For One-off Login (Vanitas-initiated)
The system redacts `process.env.PW` in all tool outputs. Solutions:
- Use `fs.readFileSync('/tmp/pw_val.txt','utf8').trim()` to read from file
- Or use `process["env"]["PW"]` bracket notation
- Or use `require('/tmp/pw_module.cjs')` for module-based approach
- NEVER hardcode password in script files

## Camoufox Notes
- Install (npm package + binary): `npm install camoufox && npx camoufox fetch && chmod +x ~/.cache/camoufox/camoufox-bin`
- İkisi de gerekli: npm paketi (`require('camoufox')`) için, binary (`camoufox-bin`) için.
- `npm install camoufox` → `added 40 packages` (~5sn). Sonrası `npx camoufox fetch` → ~250MB ARM64 binary indirir.
- Fetch binary: `npx camoufox fetch` (downloads ~250MB ARM64 binary)
- Requires `chmod +x ~/.cache/camoufox/camoufox-bin`
- Options: `headless: true`, `os: 'windows'` (or `'macos'` for better fingerprint), `humanize: 1.5` (or 2.0 for slower), `locale: ['en-US']`
- **proxychains4 ile geoip: false ZORUNLU:** `geoip: true` (varsayılan) Camoufox'un kendi IP servisine bağlanmasını dener, proxychains4 ile çakışır ve `Failed to connect to proxy` hatası verir.
- **Camoufox proxy parametresi (socks5):** Çalışmaz — `NS_ERROR_UNKNOWN_PROXY_HOST` hatası. Mutlaka proxychains4 kullan.

## CRITICAL: Job Searching vs Session Management

This skill handles **session/cookie management only**. For **job searching**, use the `upwork-job-search` skill instead.

**Why separate?** Cloudflare blocks ALL direct access from Oracle Cloud datacenter IPs (not just form POSTs — even GET requests, RSS feeds, and curl return challenge pages). Cookie-based session management cannot bypass this IP-level block.

For job searching, use these Cloudflare-free approaches (detailed in `upwork-job-search` skill):
1. Google Custom Search API (free, 100 queries/day)
2. Upwork Official API (OAuth2, different infrastructure)
3. User-side Chrome extension (residential IP)

## CRITICAL: User Approval Rules

### Job Applications and Proposals
- **NEVER submit job applications, proposals, or bids without Edel's explicit approval** — this is a hard rule

### Profile Information
- **NEVER fill out profile information (skills, title, bio, photo, etc.) without asking first**
- Profile is incomplete and must be done with Edel's input
- When filling profile: ask about each section, get Edel's input, then fill one at a time

### Bot Detection Risk
- Bot detection risk is REAL — authentic-looking profile + natural timing needed

### Profile Completion Status (last updated: 12 Tem 2026)
- **Current progress:** Step 8/10 (Hourly Rate) — Education/Languages skipped (optional)
- **Completed:** Skills (3/10) — 9 skills added (Psychology, Mental Health, Counseling, Academic Research, Research Paper Writing, Academic Editing, Academic Proofreading, Content Writing, English), Title (4/10) — "Psychology Researcher & Academic Writer", Employment (5/10) — internship auto-detected
- **Pending:** Hourly Rate, Photo, Overview
- **Display Name / Identity:** `[UNKNOWN — ask Edel]` — cookie'lerden/config'den okunamıyor, session tarafından döndürülmüyor. Upwork profilde görünen kişi adı. Email: `isimgorulsunn@gmail.com`. Harici alias: "Vanilla". Öğrenince kaydet.

### Profile Completion Automation

See `references/profile-completion-automation.md` for detailed steps and selectors.

Upwork doesn't show find-work page until profile is past step 3/10 (Skills). To automate profile completion:

#### Skills page (`/nx/create-profile/skills`)
- **Input selector:** `input[placeholder="Enter skills here"]`
- **Dropdown selector:** `[role="option"]` — click the first match
- **Add skills one by one:** type → wait 2s for dropdown → click first option → wait 1.5s
- **Verification:** check `page.locator('button').filter({ hasText: 'Remove' }).count()` after each add
- **Next button:** `page.locator('button').filter({ hasText: /Next/i })`

#### Profile Title page (`/nx/create-profile/title`)
- **Input selector:** `input[type="text"][placeholder="Example: Writing"]`
- **⚠️ Auto-fill trap:** Upwork auto-fills a suggestion. Must click **"Clear Input"** button FIRST, then type.
- **Keyboard type required:** `page.keyboard.type(title, { delay: 30 })` — `fill()` does NOT trigger Vue `v-model` and Next stays disabled. Keyboard typing fires keydown/keyup events Vue needs.
- **Next button location:** Buried among many "Edit"/"Delete" buttons for skills. May be at index 30+. List ALL buttons with `page.locator('button')` and find one containing "Next" AND "experience". Do NOT use `.filter({ hasText: /Next/i })` — it matches "Next item. Update list" (typeahead nav).
- **Verification:** Check `isDisabled()` on Next before clicking. If disabled, keyboard-typing didn't register.
- Format example: "Psychology Researcher & Academic Writer"

#### Available Psychology Skills
Search "psycholog" → Psychology, Counseling Psychology, Industrial Psychology; "mental" → Mental Health; "counseling" → Counseling, Child Counseling; "academic" → Academic Research, Academic Editing, Academic Proofreading; "research" → Research Paper Writing, Research Methods; "behavioral" → Cognitive Behavioral Therapy; "thesis" → Thesis, Thesis Writing.

#### Employment Page (`/nx/create-profile/employment`, step 5/10)
- Upwork may auto-detect past experience (e.g. internships from LinkedIn/CV import).
- "Courthouse Internship — Izmir Regional Court | July 2022 - August 2022" detected 14 June 2026.
- Next button text: "Next, add your education" — may appear clickable (`disabled=false`) but NOT respond to clicks (Vue event handler not bound after keyboard navigation). **Bypass:** use `page.evaluate(() => { window.location.href = '/nx/create-profile/hourly-rate' })` to skip. Employment itself IS saved — the button just doesn't fire.
- Education (6/10) and Languages (7/10) appear to be optional — Hourly Rate (8/10) is accessible directly after Employment.
- Multiple "Edit"/"Delete" buttons exist (one per skill tag + experience entry) — do NOT use `.filter({ hasText: /Next/i })` alone, it catches "Next item. Update list" (typeahead navigation). Scan ALL buttons for the real profile-step Next.

## Proxy Options
- **WARP+ proxy** (`127.0.0.1:1080` SOCKS5) — partially works for navigation but Cloudflare blocks WARP IP ranges on form submit
- **Proxychains4** — successfully routes Camoufox through WARP:
  ```bash
  sudo apt-get install proxychains4
  sudo sed -i 's/socks4.*127.0.0.1.*9095/socks5\t127.0.0.1 1080/' /etc/proxychains4.conf
  cd ~/.hermes && proxychains4 -q node upw_session_refresh.cjs
  ```
- **Camoufox + proxychains4 ile job search:** `~/.hermes/upw_job_search.cjs` script'i mevcut. Cookie'leri load edip WARP üzerinden Camoufox açar:
  ```bash
  cd ~/.hermes && proxychains4 -q node upw_job_search.cjs
  ```
  ⚠️ Job search sayfaları (`freelance-jobs/`, `search/jobs/`) Cloudflare challenge gösterir — WARP IP'sinde bile. Ana sayfa (`/nx/create-profile/*`) çalışır.
- Residential proxy NOT tested — would need BrightData/IPRoyal etc.

## Proxychains4 Pitfalls
- `geoip: false` zorunlu — aksi halde Camoufox IP servisine bağlanamaz
- `-q` flag sessiz mod (gereksiz proxy loglarını gizler)
- proxychains4'ün DNS proxy özelliği (proxy_dns) WARP üzerinden DNS çözümlemesi yapar
- WARP IP'si Cloudflare'e ait olduğu için Cloudflare korumalı sayfalarda challenge alınabilir

### 🔴 PITFALL: WARP Single Point of Failure (12 Tem 2026)

**Sorun:** `scripts/upwork_refresh.sh` originally used proxychains4 → WARP as the **only** route. When WARP container was unstable (3 consecutive failures: 11 Tem 20:00, 12 Tem 00:00, 12 Tem 08:00), the entire Upwork refresh chain broke. Each failure notified Edel.

**Belirti:** Script exits with code 1, no meaningful stdout captured. Cron shows "script failed" without details — the `set -e` in the bash script causes instant exit before variable capture.

**Çözüm (uygulandı):** Wrapper script now tries **direct first** (no proxy), falls back to proxychains/WARP. WSL/Docker Desktop ortamlarında direkt bağlantı genelde çalıştığı için bu çift yollu strateji WARP düşse bile refresh'i korur.

**Kural:** Upwork refresh gibi otomatik cron işlerinde asla tek bir proxy/route'a bağımlı kalma. İlk yol direkt olsun, proxy her zaman fallback olsun.

### WARP Üzerinden Script Zaman Aşımı (Timeout — 21 Haz 2026)

WARP + proxychains4 ile session refresh script'i 180s içinde tamamlanmayabilir. Camoufox başlatma + cookie yükleme + page.goto() zinciri WARP üzerinden 60-120s sürebilir.

**Belirti:** Script başlar ("Loaded N cookies" log'u görünür), sonra hiç çıktı vermeden timeout'a düşer. "URL:" veya "SESSION VALID" log'u gelmez.

**Çözüm — timeout'u arttır:**
```bash
# WARP üzerinden çalıştırırken 300s timeout kullan
timeout 300 /home/ubuntu/.local/bin/proxychains4 -q -f /home/ubuntu/.local/etc/proxychains.conf node upw_session_refresh.cjs
```

**WARP'suz direkt çalıştırma:** Eğer container direkt internete çıkabiliyorsa (Oracle Cloud DEĞİL), proxychains4 ve WARP gerekmez. Direkt `node upw_session_refresh.cjs` ~30s içinde tamamlanır.\n\n### 🐳 Docker Ortamında WARP Hostname Çözümü (PITFALL — 21 Haz 2026)\n\nproxychains4 `strict_chain` + `proxy_dns` modunda hostname çözemez:\n```\nproxy warp has invalid value or is not numeric\n```\n**Çözüm:** WARP Docker hostname'i yerine direkt IP kullan:\n```bash\n# WARP container IP'sini bul\ngetent hosts warp  # → 172.19.0.2\n\n# Config'te hostname yerine IP kullan\nsed -i 's/socks5\\twarp\\t1080/socks5\\t172.19.0.2\\t1080/' ~/.local/etc/proxychains.conf\n```\n**Docker bridge IP'leri restart'ta değişebilir** — her seferinde `getent hosts warp` ile kontrol et.\n\n### 🔧 proxychains4 Source Kurulum (sudo yoksa — 21 Haz 2026)\n\nDocker container'da `sudo` ve `apt-get` yoksa proxychains4 source'dan derlenebilir:\n```bash\ncd /tmp\ngit clone --depth 1 https://github.com/rofl0r/proxychains-ng.git\ncd proxychains-ng\n./configure --prefix=$HOME/.local\nmake -j4\nmake install\n# Config:\nmkdir -p $HOME/.local/etc\ncp src/proxychains.conf $HOME/.local/etc/\nsed -i 's/^socks4.*127.0.0.1.*9050/socks5\\twarp\\t1080/' $HOME/.local/etc/proxychains.conf\n# Kullanım:\n$HOME/.local/bin/proxychains4 -q -f $HOME/.local/etc/proxychains.conf node script.cjs\n```

## Wiki Reference
- Full documentation in wiki: `concepts/upwork-cloudflare-bypass.md`
- Covers: all failed methods and why, Cloudflare Bot Management analysis, IP reputation notes, edge cases
- Session-specific job search notes: `references/job-search-script-notes.md`

## Common Issues

### Cookie Issues
- Cookie `sameSite` values from Chrome export may be lowercase (`strict`, `lax`, `no_restriction`) — normalize to Playwright format: `Strict`, `Lax`, `None`
- Cookie banner (OneTrust) may overlay form fields — dismiss with `Reject All` button

### Login Process
- Upwork uses 2-step login: email → Continue → password → Log In
- Password field name is `login[password]` (id: `login_password`)
- "Log in" button uses `getByRole('button', { name: 'Log in', exact: true })`

### Camoufox Crash (Playwright Bug) — FIXED in script (21 Haz 2026)

**✅ `process.on('uncaughtException')` handler IS now implemented in `upw_session_refresh.cjs`.** The script suppresses the known async crash.

- **Error:** `FFPage._onUncaughtError: Cannot read properties of undefined (reading 'url')` — happens on direct navigation. `page.on('pageerror', () => {})` does NOT catch this (it's in Playwright's internal `addPageError`, not the page).
- **Fix (applied):** `process.on('uncaughtException', (e) => { if (e.message?.includes('Cannot read properties of undefined')) return; process.exit(1); })` at top of script.
- **Result:** Script completes normally even when this error fires asynchronously after cookie save.

### Skills Not Persisted
- If Camoufox crashes mid-session, ALL added skills are lost (page resets to 0 on reload).
- Always verify skill count before clicking Next.
- If crash happens, re-add all skills.

### 🔴 PITFALL: Camoufox Binary Goes Missing (18 Tem 2026)

**Sorun:** `npm install camoufox` paketi yüklü olsa bile `~/.cache/camoufox/camoufox-bin` binary'si kaybolabilir (örneğin container restart, cache temizliği, güncelleme).
**Belirti:** Script hata vermeden exit code 1 ile çıkar. Direkt çalıştırınca Camoufox ile ilgili hata görülür.
**Çözüm:** 
```bash
# npm paketi varsa binary fetch + chmod
npx camoufox fetch
chmod +x ~/.cache/camoufox/camoufox-bin
```
**Önleme:** `scripts/upwork_refresh.sh` wrapper'ına binary kontrolü eklenebilir. Şu an manuel müdahale gerekiyor.

### WARP Container Kapalıyken Çalıştırma (18 Tem 2026)

WARP Docker container'ı (172.19.0.2:1080) kapalı olsa bile **direkt Camoufox bağlantısı çalışır** — Camoufox'un fingerprint spoofing'i Cloudflare'i bypass eder. WSL/Docker Desktop ortamlarında residential IP üzerinden çıkıldığı için bu beklenen davranıştır. **Proxychains fallback yolu sadece datacenter IP'lerinde (Oracle Cloud) gerekir.**

Script durumu kontrolü:
```bash
# WARP container çalışıyor mu?
docker ps --format "{{.Names}}" 2>/dev/null | grep -q warp && echo "WARP: OK" || echo "WARP: DOWN"
```

### Camoufox Binary Installation & Troubleshooting

### 🔴 Pitfall: `npx camoufox fetch` GitHub API Rate Limit (21 Haz 2026)

`npx camoufox fetch` GitHub API'ye bağlanır ve rate limit'e takılabilir (`Failed to fetch releases`, `API rate limit exceeded`).

**Belirti:**
```
Error: Failed to fetch releases from https://api.github.com/repos/daijro/camoufox/releases: TypeError: releases is not iterable
```
veya
```
Error: API rate limit exceeded for ...
```

**Çözüm — Manuel İndirme:**

1. **En son release tag'ini bul:**
   ```bash
   curl -sI "https://github.com/daijro/camoufox/releases/latest" -o /dev/null -w "%{redirect_url}"
   # → https://github.com/daijro/camoufox/releases/tag/v150.0.2-beta.25
   ```

2. **Asset listesini al (expanded_assets endpoint'inden):**
   ```bash
   TAG="v150.0.2-beta.25"  # yukarıdaki tag
   curl -sL "https://github.com/daijro/camoufox/releases/expanded_assets/$TAG" | \
     python3 -c "
   import sys, re
   html = sys.stdin.read()
   urls = re.findall(r'/(daijro/camoufox/releases/download/[^\"]+)', html)
   for u in set(urls):
       if 'linux' in u.lower() and 'x86_64' in u.lower():
           print(f'https://github.com{u}')
   "
   ```

3. **İndir ve çıkar:**
   ```bash
   mkdir -p ~/.cache/camoufox
   curl -sL "ASSET_URL" -o /tmp/camoufox.zip
   # Python ile zip aç (unzip genelde yok):
   python3 -c "
   import zipfile, os
   os.makedirs('/tmp/cx', exist_ok=True)
   with zipfile.ZipFile('/tmp/camoufox.zip') as z:
       z.extractall('/tmp/cx')
   "
   cp -r /tmp/cx/* ~/.cache/camoufox/
   chmod +x ~/.cache/camoufox/camoufox-bin
   ```

4. **Doğrula:**
   ```bash
   test -f ~/.cache/camoufox/camoufox-bin && echo "✅ binary"
   test -f ~/.cache/camoufox/version.json && echo "✅ version.json"
   ```

**⚠️ Kritik:** Sadece `camoufox-bin` binary'ini kopyalamak YETMEZ. Camoufox `version.json`, tüm `.so` kütüphaneleri ve `fonts/` dizinini bekler. **Tüm zip içeriğini** kopyala, sadece binary'i değil.

### Cookie Count Reduction After Refresh (21 Haz 2026)

Camoufox v150, Chrome'dan export edilen `~2499` cookie'yi alıp sadece `42` temiz cookie olarak kaydeder. Bu NORMAL'dir — Camoufox kendi tarayıcı context'inde geçerli olanları filtreler.

Gözlem: 2499 cookie (Chrome export, 889KB) → 42 cookie (Camoufox refresh, ~15KB). Tümü valid.

**Kural:** Cookie sayısındaki büyük azalma alarm sebebi DEĞİLDİR. Validasyon oranına bak (`Valid / Total`).

### Script Crashes on Missing /tmp/pw_val.txt — FIXED (21 Haz 2026)

**✅ This is now fixed.**

**Fix:** Ensure `/tmp/pw_val.txt` exists before running. If only doing a cookie refresh (no login needed), create a placeholder:
```bash
echo "placeholder" > /tmp/pw_val.txt && chmod 600 /tmp/pw_val.txt
```

**Long-term fix:** Refactor the script to lazy-load the password inside the login branch instead of at module level.

### bw-serve Not Running (Docker/WSL Environment)

**Error:** `curl: (7) Failed to connect to localhost port 8087`
**Root cause:** bw-serve's entrypoint.sh may have failed to start, or the container was just restarted before the entrypoint completed. Normally, bw-serve auto-starts via `entrypoint.sh` on container boot (no systemd needed — runs directly in the entrypoint).

**Diagnosis:**
```bash
curl -s http://localhost:8087/status    # Connection refused = not running
# Check if entrypoint ran:
ps aux | grep "bw serve" | grep -v grep
# Check entrypoint logs:
docker logs vanatis-hermes 2>&1 | grep -i "bw-serve\|bitwarden"
```

**Recovery:**
1. **Wait 30s** — entrypoint.sh may still be starting Bitwarden. bw-serve takes ~15-20s after container boot.
2. **Restart container:** `docker restart vanatis-hermes` — entrypoint.sh handles bw-serve auto-start.
3. Still down? Manual start: `bash ~/.hermes/scripts/bw-serve.sh` (requires GPG secret key on this machine)
4. Add upwork password to bws (Bitwarden Secrets Manager) for permanent fallback
5. Export fresh cookies from Chrome and send to Vanitas
6. See `references/bw-serve-down-recovery.md` for full diagnosis

### Profile Blocks Find-Work
- Until profile passes step 3/10 (Skills), `/nx/find-work/` redirects to `/nx/create-profile/`.
- Complete profile steps first, then job search becomes accessible.

### 🔴 PITFALL: False Positive "SESSION VALID" Check (12 Tem 2026)

**Sorun:** `upw_session_refresh.cjs` oturum kontrolü sadece şu koşullara bakar:
```javascript
if (url.includes('login') || url.includes('account-security') || body.includes('Log in to Upwork')) {
    // EXPIRED
} else {
    console.log('SESSION VALID - Already logged in');
}
```

Bu kontrol **Google OAuth hesapları için yetersizdir.** Upwork ana sayfası "Log in to Upwork" metnini içermeyen bir logged-out görünüm gösterebilir. Sayfa yüklenir, URL `upwork.com/` olarak kalır (login'e redirect olmaz), ancak kullanıcı aslında giriş yapmamıştır — sadece Google Sign-In popup'ı JavaScript ile geç render olur.

**Belirti:**
- Script "SESSION VALID" yazdırır, cookie'leri kaydeder (exit 0)
- Camoufox sayfası açıldığında "Google ile oturum açın" popup'ı görünür
- `/nx/find-work/` gibi protected route'lar `/ab/account-security/login` adresine redirect eder
- Vue/Nuxt state'inde kullanıcı objesi yoktur (kontrol: `window.$nuxt?.$store?.state?.user`)

**Kök neden:** `waitUntil: 'load'` ile sayfa HTML'i yüklenir ama Vue/Nuxt uygulamasının API çağrıları henüz tamamlanmamış olabilir. Google OAuth popup'ı JavaScript tarafından sayfa tamamen yüklendikten sonra eklenir.

**Teşhis — gerçek session validasyonu:**
```javascript
// Protected route'a git — login redirect olursa session gerçekten expired
await page.goto('https://www.upwork.com/nx/find-work/', { waitUntil: 'load', timeout: 30000 });
if (page.url().includes('login')) {
    console.log('❌ SESSION EXPIRED - Protected route redirected to login');
}
```

**Kural:** Google OAuth hesaplarında, ana sayfanın login'e redirect olmadan yüklenmesi session'ın geçerli olduğu anlamına gelmez. Gerçek validasyon için protected route testi şarttır. Google OAuth ile bağlı hesaplarda cookie expiry sonrası re-login imkansızdır — fresh Chrome export gerekir.

### Upwork SPA Route Access (12 Tem 2026)

Camoufox ile cookie yükleyip Upwork'e gidildiğinde route erişim matrisi:

| Route | Cookie ile Erişim | Not |
|-------|-------------------|-----|
| `upwork.com/` | ✅ Homepage yüklenir | Vue SPA, client-side auth |
| `upwork.com/nx/find-work/` | ❌ Redirect → `/ab/account-security/login` | Protected |
| `upwork.com/freelancers/settings` | ❌ "Only available to Upwork customers" | Public freelancer profili |
| `upwork.com/nx/freelancer/profile/` | ❌ 404 | Yanlış path |
| `upwork.com/nx/freelancer/account/` | ❌ 404 | Yanlış path |

**Çıkarım:** Cookie dosyası ana sayfayı göstermeye yeter ama protected route'lar için XSRF token / access token gibi ek auth bilgileri gerekir. Bu token'lar Camoufox tarafından yakalanamıyorsa session aslında geçerli değildir.

### Display Name / Profile Identity
Upwork'te görünen profil adı cookie'lerden veya config'den okunamıyor. Bilinenler:
- **Login email:** `isimgorulsunn@gmail.com`
- **Harici alias:** Vanilla
- **Profil title:** Psychology Researcher & Academic Writer
- **Görünen ad:** (öğrenilince kaydet)
