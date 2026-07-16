---
name: no-agent-cron-scripts
description: "Hermes no_agent=true cron script patterns — API key storage, error handling, exit codes, monitoring reliability"
version: 1.0.0
metadata:
  hermes:
    tags: [cron, scripts, monitoring, devops, reliability]
    category: devops
---

# no_agent Cron Scripts — Reliability Patterns

Hermes `no_agent=true` cron jobs run Python/shell scripts directly (no LLM agent loop). Stdout is delivered to the user, stderr is logged. Exit code determines `last_status`.

## Critical Patterns

### 1. API Key Storage — Two Valid Patterns

**Pattern A (Standard — Persistent):**
```python
import os
HOME = os.path.expanduser("~")
KEY_FILE = f"{HOME}/.hermes/secrets/service_key.txt"
# Or check env var first, file as fallback
```

**Pattern B (Secure Pipeline — /tmp/ isolation):**
Use when the primary LLM must NEVER see the key value. The key is fetched from Bitwarden Secrets Manager (`bws`) by a helper script and written to `/tmp/` with `chmod 600`. The cron script reads it from there, never via an agent.

```python
KEY_FILE = "/tmp/.or_key"
with open(KEY_FILE) as f:
    key = f.read().strip()
```

Valid only when ALL of these hold:
1. Script runs `no_agent=true` (no LLM agent in the loop)
2. Key is fetched from a secrets manager (bws), not hardcoded or agent-injected
3. `/tmp/` is in a Docker container or tmpfs that persists between cron runs
4. Key file is `chmod 600` — readable only by the owner

This is an intentional trade-off: security isolation (key never reaches the LLM) over absolute persistence (key survives a reboot). If the container restarts, the key must be re-fetched from Bitwarden.

⚠️ **PITFALL — Key file can vanish mid-lifecycle.** `/tmp/` is NOT durable. tmpwatch (`systemd-tmpfiles-clean`), Docker container restarts, `sudo reboot`, or even just process lifecycle on tmpfs can silently remove `/tmp/.or_key`. The cron script then crashes with a cryptic `FileNotFoundError` — exactly what Edel reported: `[Errno 2] No such file or directory: '/tmp/.or_key'`. The script MUST handle this gracefully. If your script crashes on a missing key file, that is a script bug, not an infrastructure problem — the resilience pattern below fixes it.

### 2. Error Handling — Exit Non-Zero on Failure

**Problem:** Catching exceptions without `sys.exit(1)` makes cron report `last_status: "ok"` even when the script failed. The error message goes to the user but monitoring shows green.

**Wrong:**
```python
try:
    result = risky_call()
except Exception as e:
    print(f"⚠️ Hata: {e}")
    # ← sys.exit(1) missing — cron sees exit code 0
```

**Correct:**
```python
import sys
try:
    result = risky_call()
except Exception as e:
    print(f"⚠️ Hata: {e}")
    sys.exit(1)  # cron sees exit code 1 → last_status = "error"
```

### 2b. Resilience — Recoverable Failures (Key File Missing, Network Glitch)

Some failures are transient and recoverable. The script should distinguish between "this will never work" (bad API key, wrong URL) and "this might work after a retry" (network blip, key file missing, 502).

**Pattern C — Auto-Recovery from Missing Key File:**

The `/tmp/.or_key` file can vanish between cron runs (tmpwatch, reboot, container restart). The script should first check if the key file exists, and if missing, attempt to regenerate it from Bitwarden before falling back:

```python
#!/usr/bin/env python3
import os, sys, json, subprocess, time
from pathlib import Path

HOME = os.path.expanduser("~")
KEY_FILE = "/tmp/.or_key"
BITWARDEN_SCRIPT = f"{HOME}/.hermes/scripts/fetch_routeway_key.py"  # or inline

def get_api_key():
    """Get API key with auto-recovery from Bitwarden if file is missing."""
    if os.path.exists(KEY_FILE) and os.path.getsize(KEY_FILE) > 0:
        with open(KEY_FILE) as f:
            return f.read().strip()
    
    # Key file missing — attempt recovery
    recovery_path = "/tmp/.key_recovery_attempt"
    print(f"⚠️ Key file {KEY_FILE} bulunamadı. Kurtarma deneniyor...")
    
    # Anti-loop: prevent infinite recovery loops
    if os.path.exists(recovery_path):
        age = time.time() - os.path.getmtime(recovery_path)
        if age < 3600:  # 1 hour cooldown
            print("❌ Kurtarma daha önce denendi ve başarısız oldu. Son çalışma hatası ele alındı.")
            sys.exit(1)
    
    # Mark recovery attempt
    Path(recovery_path).touch()
    
    # Try Bitwarden re-fetch
    try:
        result = subprocess.run(
            ["bws", "secret", "list", "--output", "json"],
            capture_output=True, text=True, timeout=15,
            env={**os.environ, "ALL_PROXY": ""}  # Bitwarden needs direct net
        )
        if result.returncode == 0:
            secrets = json.loads(result.stdout)
            # Find by name or ID — adapt to your key's identifier
            for s in secrets:
                if "routeway" in s.get("key", "").lower() or "decd94e7" in s.get("id", ""):
                    key = s.get("value", "").strip()
                    if key:
                        os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
                        with open(KEY_FILE, "w") as f:
                            f.write(key)
                        os.chmod(KEY_FILE, 0o600)
                        print(f"✅ Key dosyası yeniden oluşturuldu: {KEY_FILE}")
                        os.remove(recovery_path)
                        return key
                    break
        print("❌ Kurtarma başarısız: Bitwarden'da routeway key'i bulunamadı.")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ Kurtarma başarısız: Bitwarden çağrılamadı ({e}).")
    
    sys.exit(1)
```

**When to retry vs when to fall back:**

| Durum | Aksiyon |
|-------|---------|
| HTTP 502 (upstream) | 3 retry with 2s/4s/8s backoff → fallback model |
| HTTP 429 (rate limit) | Bekle (e.g. 5s) → 1 retry → fallback model |
| HTTP 504 (timeout) | 2 retry → fallback model (daha küçük prompt/max_tokens) |
| Key file missing | Auto-recovery from Bitwarden (anti-loop protected) |
| Bad API key (401/403) | Fallback hemen, retry yok — sorun kalıcı |

**Fallback model pattern for Routeway:**

```python
PRIMARY_MODEL = "deepseek-v4-flash:free"
FALLBACK_MODEL = "step-3.5-flash:free"  # reasoning → regex extraction

def call_model(model, messages, max_retries=3):
    for attempt in range(max_retries):
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        body = json.dumps({"model": model, "messages": messages}).encode()
        req = urllib.request.Request(
            "https://api.routeway.ai/v1/chat/completions",
            data=body, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 502 and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
                print(f"⚠️ {model} 502, {wait}s bekleniyor (deneme {attempt+2}/{max_retries})...")
                time.sleep(wait)
            elif e.code in (429, 504) and attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise
    raise Exception(f"{model} max retries exhausted")

# Usage with fallback
try:
    result = call_model(PRIMARY_MODEL, messages)
except Exception as e:
    print(f"⚠️ {PRIMARY_MODEL} başarısız: {e}. Fallback: {FALLBACK_MODEL}")
    result = call_model(FALLBACK_MODEL, messages)  # single attempt on fallback
```

### 3. Silent Operation — Empty Stdout = No Delivery

**Pattern:** `no_agent=true` jobs with empty stdout produce no Telegram delivery. Use this for watchdog scripts that only alert on state changes:
```python
import json, os

STATE_FILE = os.path.expanduser("~/.hermes/scripts/state/last_check.json")
prev = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        prev = json.load(f)

current = check_something()
if current != prev:
    print(json.dumps(current, indent=2))  # Only printed → delivered on change
    with open(STATE_FILE, "w") as f:
        json.dump(current, f)
# No output on no-change = silent = no Telegram spam
```

### 4. Script Naming — Name Reflects What It Calls

A script named `stepfun_evaluator.py` that calls `openrouter.ai` is misleading. If it uses OpenRouter API:
- Name: `openrouter_evaluator.py`
- Variable: `or_key` (not `stepfun_key`)
- Error messages: "OpenRouter" not "StepFun"

## Verification Checklist

- [ ] API keys in `~/.hermes/secrets/` or env vars (Pattern A), OR `/tmp/.or_key` with Bitwarden pipeline (Pattern B)
- [ ] Every `except` block has `sys.exit(1)` unless intentional silent skip
- [ ] `chmod 600` on key files
- [ ] Script name matches the API/service it actually calls
- [ ] State directory exists (`os.makedirs(dirname, exist_ok=True)`)
- [ ] `cronjob action='list'` shows correct `last_status` after manual test run

### 4b. NVIDIA'da "Listede Ama Çalışmıyor" Tuzağı

NVIDIA'nın build.nvidia.com sitesinde "Free Endpoint" etiketiyle listelenen 73 modelin HEPSİ fiilen çalışmaz. Bir modelin:
- build.nvidia.com'da "Free Endpoint" ✅
- API `/v1/models` listesinde (118 model) ✅
- config.yaml'da NVIDIA provider `models:` listesinde ✅
- Hatta 8M indirme sayısı olması ✅
...o modelin API'den yanıt vereceği anlamına gelmez. Özellikle büyük modeller (70B+) ve Z.ai gibi üçüncü taraf modeller timeout yiyebilir.

**GLM-5.2 örneği (16 Tem 2026):**
- build.nvidia.com'da "Free Endpoint" ✅, 8M indirme, Z.ai tarafından yayınlanmış
- API `/v1/models` listesinde `z-ai/glm-5.2` olarak ✅
- config.yaml NVIDIA provider `models:` listesinde ✅ (294. satır)
- **API çağrısı: timeout ❌** (100sn+ yanıt yok)

**Güvenilir test yöntemi:** Her modeli küçük prompt'la 15sn timeout'lu API çağrısı ile test et:
```python
from openai import OpenAI
import httpx
client = OpenAI(api_key=..., base_url="https://integrate.api.nvidia.com/v1",
                timeout=httpx.Timeout(15, connect=10))
try:
    r = client.chat.completions.create(model="test-edilecek-model",
        messages=[{"role":"user","content":"1+1?"}], max_tokens=5)
    print("OK")
except:
    print("FAIL (timeout/error)")
```

**Güvenilirliği kanıtlanmış NVIDIA free modelleri:**
1. `mistralai/mistral-small-4-119b-2603` — 0.9sn, en hızlı/güvenilir
2. `deepseek-ai/deepseek-v4-flash` — 1.1sn
3. `minimaxai/minimax-m3` — 13sn (dar context'te çalışır, economy bültenleri için Edel onaylı)

**NVIDIA'da listelenen ama çalışmayan modeller:**
- ~~`z-ai/glm-5.2`~~ — timeout (sitede Free Endpoint yazsa da, 8M indirmesi olsa da)
- ~~`meta/llama-3.3-70b-instruct`~~ — timeout
- ~~`meta/llama-3.1-70b-instruct`~~ — timeout

Detaylı benchmark: `references/nvidia-model-benchmarks.md`

## 4c. Telegram Kanalı İzleme — HTML Parsing + State Diffing

Telegram public kanalları (`t.me/s/KanalAdi`) JavaScript gerektirmeden statik HTML sunar. no_agent cron + state dosyası ile yeni mesaj kontrolü yapılabilir.

**Pattern:** `curl`/`urllib` ile HTML çek → regex ile mesaj datetime + text ayrıştır → state'teki son datetime ile karşılaştır → yeni mesaj varsa bildir.

Detaylı teknik, Python şablonu ve state başlatma: `references/telegram-channel-html-monitoring.md`

**⚠️ Kanala düşme uyarısı — deliver=local kullan:** Kullanıcının ana topic'ini gereksiz mesajlarla doldurmamak için no_agent cron'ları **`deliver=local`** ile kur. Bu sayede:
- Yeni mesaj varsa cron çıktısı `~/.hermes/cron/output/` altına kaydedilir
- Telegram topic'ine hiçbir şey düşmez
- Kullanıcı istediğinde Vanitas kontrol edip yorum katarak sunar

```python
# Cron kurulumunda:
# cronjob(action='create', schedule='0 12 * * *', name='Kanal izleme',
#         script='kanal_izleme.py', no_agent=True, deliver='local')
```

### 5. JSON API Output — Delegate Parsing to Python

When a no_agent script consumes JSON output from a Hermes API wrapper (e.g.,
`google_api.py`), do NOT use shell-level parsing (`grep -c "^Subject:"` on JSON
output — it always returns 0). Instead, delegate to a Python sub-script that
handles JSON properly.

See `references/json-api-parsing-pattern.md` for the full pattern with
examples, including priority detection and error handling.

### 5b. Google OAuth Token Expiry in Testing Mode

Google Cloud OAuth apps in Testing mode issue refresh tokens that expire after
~7 days. When a cron script's Google API calls start failing with
`invalid_grant: Token has been expired or revoked.`, the fix is a Quick Re-Auth.

See `references/google-oauth-testing-mode.md` for the full procedure, including
detection, re-auth steps, and the stale-token-path pitfall that affects
`gmail_check.sh` and `morning_greeting.sh`.

**TL;DR:** Shell wrapper → `exec python3 "$SCRIPT_DIR/helper.py"`

## Provider-Specific Checks

### Routeway — Free Model Selection (20 Haz 2026 Güncel)

**KRİTİK: Türkçe kalitesi BİRİNCİL KRİTERDİR.** Halüsinasyon oranı, hız, content dolu olması ikincildir. Nemotron 0.0 hallucination rate ile mükemmel görünür ama Türkçesi berbattır ("baziliklardir" gibi çıktılar). Değerlendirmede kullanılamaz.

**Sadece 2 free model Routeway'de fiilen çalışmaktadır** (2026-06-20 itibarıyla, diğer 13 model 502 Bad Gateway):
- `step-3.5-flash:free` (StepFun reasoning) — **Türkçesi kabul edilebilir.** `content` ALWAYS empty, JSON must be extracted from `reasoning_content` via regex.
- `nemotron-3-nano-30b-a3b:free` (NVIDIA) — **Türkçesi berbat.** Kullanma.
- Diğer tüm `:free` modeller (gpt-oss-120b, minimax-m2, mistral-nemo, gpt-4o-mini, vs.): 502 Bad Gateway.

**Step-3.5-flash reasoning_content Extraction Pattern:**
```python
import json, re

response_data = json.loads(raw_response)
msg = response_data['choices'][0]['message']
content = msg.get('content', '') or ''
reasoning = msg.get('reasoning_content', '') or ''

# Strategy 1: reasoning_content içinde JSON ara (en güvenilir)
if not content.strip() and reasoning.strip():
    json_match = re.search(r'(\{.*\}|\[.*\])', reasoning, re.DOTALL)
    if json_match:
        content = json_match.group(1)

# Strategy 2: Hiçbir şey yoksa empty dict
if not content.strip():
    content = '{}'
```

- [ ] Routeway URL: `https://api.routeway.ai/v1/chat/completions` (NOT `openrouter.ai`)
- [ ] `method="POST"` set in `urllib.request.Request`
- [ ] User-Agent header: `Mozilla/5.0 (Windows NT 10.0; Win64; x64)` (Routeway Cloudflare'dan geçer)
- [ ] Rate limits: Free = 5-20 RPM / 200 RPD. Keep max_tokens ≤ 4000 to avoid 504s.
- [ ] **Aktif preferred model:** `step-3.5-flash:free` — reasoning_content'ten regex ile JSON çıkar (Türkçesi en iyi çalışan)
- [ ] Key stored at `/tmp/.or_key` via secure pipeline (Bitwarden → bws → Python → file)
- [ ] **Resilience:** Script handles missing `/tmp/.or_key` gracefully — auto-recovery or clear error message (see Section 2b)

### Routeway Known Error: Missing `/tmp/.or_key`

En sık karşılaşılan hata: `[Errno 2] No such file or directory: '/tmp/.or_key'`

**Kök neden:** `/tmp/` kalıcı değildir. Docker container restart, `sudo reboot`, tmpwatch temizliği, veya boot sonrası tmpfs silinir. Key re-fetch script'i çalışmamışsa veya cron, key-fetch'ten önce tetiklenmişse bu hata alınır.

**Çözüm sırası:**
1. Script'i kontrol et — `get_api_key()` Pattern C (Section 2b) kullanıyor mu? Eğer ham `open(KEY_FILE).read()` varsa → Pattern C'ye güncelle.
2. Eğer script `no_agent=true` ve auto-recovery yoksa → elle key re-fetch script'ini çalıştır: `python3 ~/.hermes/scripts/fetch_routeway_key.py`
3. Eğer fetch script'i de yoksa → Bitwarden'dan manuel al:
   ```bash
   bws secret list --output json | python3 -c "import json,sys; [print(s['value']) for s in json.load(sys.stdin) if 'routeway' in s.get('key','').lower()]" > /tmp/.or_key && chmod 600 /tmp/.or_key
   ```
4. Cron schedule'ını kontrol et — key re-fetch job'ı ana cron'dan önce mi çalışıyor? Gerekirse bir `cron_before` dependency ekle.

### NVIDIA — Güvenilir Provider (16 Tem 2026, rev. 3)

**Durum:** NVIDIA NIM (`integrate.api.nvidia.com/v1`) — güvenilir cron alternatifi.

**ÖNEMLİ — Tüm NVIDIA modelleri çalışmaz!** Listedekilerin çoğu timeout yiyor.

Gerçek test sonuçları (küçük prompt, max_tokens=5):
- `mistralai/mistral-small-4-119b-2603` — **0.9s** (⭐ en hızlı/güvenilir)
- `deepseek-ai/deepseek-v4-flash` — **1.1s** (orijinal sentez modeli)
- `minimaxai/minimax-m3` — **13s** (yavaş ama Edel onaylı, dar context'te çalışır)
- ~~`meta/llama-3.3-70b-instruct`~~ — **timeout** (❌ çalışmıyor)
- ~~`z-ai/glm-5.2`~~ — **timeout** (❌ çalışmıyor)

Detaylı benchmark: `references/nvidia-model-benchmarks.md`

**⚠️ Provider Model Whitelist — Gizli 404 Tuzağı**

NVIDIA provider `discover_models: false` ile yapılandırılmıştır ve sadece `models:` listesindeki modellere izin verir. Listede olmayan bir model çağrılırsa `HTTP 404: 404 page not found` hatası alınır. **Ancak listede olması da yetmez** — GLM 5.2 listede olmasına rağmen timeout yiyor.

**Agent job'larda bir model kullanmadan önce:**
1. Provider `models:` listesinde var mı? → kontrol et
2. API'den fiilen yanıt alınabiliyor mu? → 15sn timeout'lu test et
3. Cron 120sn limitine sığıyor mu? → toplam süre < 110sn olmalı

Eksik bir model eklemek için config.yaml'da NVIDIA provider'ının `models:` listesine elle ekle (`hermes config edit` ile). Hem kısa adı hem tam adı ekle (örn. `glm-5.2: z-ai/glm-5.2` ve `z-ai/glm-5.2: z-ai/glm-5.2`).

Not: Model alias'ı (örn: `nvidia-free-m3`) provider+model çözümlemesi ayrıdır. Alias doğru çözülse bile, provider'ın models listesinde yoksa 404 alınır.

**🔤 Türkçe Model Seçimi (Güncel — 16 Tem 2026)**

NVIDIA'da Türkçe için modellerin performansı:
- `mistralai/mistral-small-4-119b-2603` — ⭐⭐⭐⭐ **Türkçesi iyi, en hızlı (0.9sn)**
- `minimaxai/minimax-m3` — ⭐⭐⭐⭐ **MoE mimarisi, kodlama+agentic'te frontier. 13sn.**
- `meta/llama-3.3-70b-instruct` — ⭐⭐ Türkçesi zayıf (ekonomi için kullanma)
- `z-ai/glm-5.2` — ⭐⭐⭐ NVIDIA'da 96sn çalışır (kodlama için kullanılır, cron'da timeout riski)

Edel'in uyarısı: Llama 3.3'ün Türkçesi ekonomi kavramlarını doğru bağlamda işleyemeyebilir.

**Agent job'larda bir model kullanmadan önce** şu modelin provider'ın `models:` listesinde olduğunu KONTROL ET:
```yaml
# config.yaml → NVIDIA provider section
discover_models: false
models:
  mistralai/mistral-small-4-119b-2603: mistralai/mistral-small-4-119b-2603  # ✅ var
  minimaxai/minimax-m3: minimaxai/minimax-m3  # ✅ var (ama yavaş)
  meta/llama-3.3-70b-instruct: meta/llama-3.3-70b-instruct  # ✅ var
```

Eksik bir model eklemek için config.yaml'da NVIDIA provider'ının `models:` listesine ekle:
```yaml
models:
  # ... mevcut listeye yeni satır
  yeni-model-adı: yeni-model-adı
```

Not: Model alias'ı (örn: `nvidia-free-m3`) provider+model çözümlemesi ayrıdır. Alias doğru çözülse bile, provider'ın models listesinde yoksa 404 alınır.

**🔤 Türkçe Model Seçimi — Ekonomi İçin Kritik**

NVIDIA'da Türkçe ekonomik analiz için modellerin performansı:
- `mistralai/mistral-small-4-119b-2603` — ⭐⭐⭐⭐ **Türkçesi iyi, önerilen**
- `minimaxai/minimax-m3` — ⭐⭐⭐ Türkçesi orta ama çok yavaş
- `meta/llama-3.3-70b-instruct` — ⭐⭐ Türkçesi zayıf (ekonomi için önerilmez)
- `meta/llama-3.2-3b-instruct` — ⭐ çok küçük model, Türkçesi sınırlı

Edel'in uyarısı: Llama 3.3'ün Türkçesi ekonomi kavramlarını (enflasyon, faiz, cari açık) doğru bağlamda işleyemeyebilir. Mistral Small 4 bu konuda daha güvenilir.

**Mistral Small 4 (119B) — Günlük Sentez için önerilen model:**
Full context (~13 haber dosyası + öğrenme geçmişi + şema) ile:
- 30-60sn yanıt süresi (cron 120sn limitine sığar)
- 10,719 karakter detaylı sentez üretebildi
- Mistral modelleri genelde kaliteli ve hızlı

**DeepSeek V4 Flash da NVIDIA üzerinden çalışır:**
- Model: `deepseek-ai/deepseek-v4-flash`
- Küçük prompt: ~33sn, full context: ~82sn
- Cron limitine sığar ancak Mistral Small 4'ten yavaş

Detaylı benchmark sonuçları: `references/nvidia-model-benchmarks.md`

**Kurallar:**
- endpoint: `https://integrate.api.nvidia.com/v1`
- API key: `NVIDIA_API_KEY` (`.env`'de)
- API timeout: max 100sn (cron 120sn limiti için 20sn marj)
- max_tokens: 8192 (fazlası cron'da timeout riski)
- Retry gerekmez — NVIDIA rate limit yok

**ESKİ (opencode-zen) → YENİ (NVIDIA) geçiş rehberi:**
```
ESKİ: base_url=https://opencode.ai/zen/v1, MODEL=deepseek-v4-flash-free, key=OPENCODE_ZEN_API_KEY
YENİ: base_url=https://integrate.api.nvidia.com/v1, MODEL=mistralai/mistral-small-4-119b-2603, key=NVIDIA_API_KEY

Alternatif NVIDIA modelleri:
- mistralai/mistral-small-4-119b-2603 (119B ⭐ en hızlı, günlük sentez + ekonomi)
- meta/llama-3.3-70b-instruct (70B, ~10sn, Türkçe gerektirmeyen işler)
- deepseek-ai/deepseek-v4-flash (33-82sn, orijinal model)
```

### LiteRouter — Eskiden Aktif (20 Haz 2026, artık önerilmez)

**Durum:** Routeway'deki kronik 502/504 sorunları (deepseek-v4-flash:free her seferde 502) ve free model çeşitliliğinin sınırlı olması (sadece step-3.5-flash çalışıyordu) nedeniyle **LiteRouter'a geçildi.**

**LiteRouter** (`literouter.com`):
- Endpoint: `https://api.literouter.com/v1/chat/completions`
- OpenAI uyumlu (drop-in replacement)
- Free modellerde **unlimited requests** (1 req/5sn soft limit)
- Instant failover — bir provider 502 verirse otomatik başkasına geçer
- 19 adet free model (`:free` suffix ile)
- Free modeller ~~Pollinations sponsorluğunda~~ — Polen tüketmez
- API key: Bitwarden secret ID'den alınır, `/tmp/.or_key`'e kaydedilir

**Aktif Model: `deepseek-v3.2:free`** (20 Haz 2026 itibarıyla)
- DeepSeek ailesi — Türkçede kanıtlanmış başarı (V4 Flash ile aynı soy)
- **Non-thinking mod** → content DOLU gelir (step-3.5-flash'taki boş content sorunu yok)
- **Resmi JSON Output** — `response_format={"type":"json_object"}` çalışıyor
- GPT-5 seviyesinde benchmark
- Tool calling var, "Thinking in Tool-Use" destekliyor
- Hızlı yanıt

**Test edilen diğer free modellerin durumu:**
| Model | JSON | Türkçe | Content | Durum |
|-------|------|--------|---------|-------|
| deepseek-v3.2:free | ✅ resmi | ⭐⭐⭐⭐⭐ | Dolu | ✅ **AKTİF** |
| grok-4.1-fast-reasoning:free | ✅ resmi | ❓ | kapatılabilir | ⏳ Yedek |
| mistral-small-24b-instruct-2501:free | ⚠️ tool ile | ⭐⭐⭐⭐ | Dolu | ⏳ Yedek |
| gemma-3-27b-it:free | ❓ | ⭐⭐⭐⭐ | Dolu | ⏳ Yedek |

**Routeway → LiteRouter kod değişimi:**
```python
# ESKİ: Routeway
BASE_URL = "https://api.routeway.ai/v1/chat/completions"
MODEL = "step-3.5-flash:free"  # reasoning, content boş → regex extraction

# YENİ: LiteRouter (20 Haz 2026)
BASE_URL = "https://api.literouter.com/v1/chat/completions"
MODEL = "deepseek-v3.2:free"  # non-thinking, content dolu → direkt JSON parse
# Reasoning regex extraction KALDIRILDI (content dolu geldiği için)
# Markdown code block temizleme EKLENDİ (bazen ```json``` içinde geliyor)
```

**Key notu:** `/tmp/.or_key` artık LiteRouter API key'ini tutar. Bitwarden secret ID'den (`673ec835-9f80-4200-8e55-b46f00ecc30d`) alınır.
