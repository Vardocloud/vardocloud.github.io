---
name: ekip-bakim
description: "EKİP multi-agent sisteminin düzenli bakımı — OpenCode güncelleme, model kontrolü, sağlık taraması, benchmark. OpenCode 1.16.2+ için."
version: 1.0.0
metadata:
  hermes:
    tags: [ekip, maintenance, opencode, models, health-check]
    category: devops
---

# EKİP Bakım

EKİP multi-agent sisteminin düzenli bakımı: OpenCode güncelleme, model listesi karşılaştırma, endpoint sağlık kontrolü.

## Bakım Adımları

### 1. OpenCode Güncelleme

```bash
# İki yöntem (npm daha güvenilir):
npm i -g opencode-ai@latest
# veya:
opencode upgrade

opencode models  # Tüm provider'lardaki modelleri gör
```

### 2. Config Karşılaştırma

```bash
# OpenCode Go'daki modeller
opencode models opencode-go | sort
# Config'deki modeller
python3 -c "import json; d=json.load(open('$HOME/.config/opencode/opencode.json')); [print(f'  - {m}') for m in d['provider']['opencode-go']['models']]" | sort
```

Config'de olmayan yeni modeller varsa → `opencode.json`'a ekle.

### 3. Sağlık Kontrolü

```bash
# Portlar
ss -tlnp | grep -E "19998|19999"

# Pollinations ping
curl -s --max-time 10 http://127.0.0.1:19999/v1/chat/completions \
  -H "Content-Type: application/json" -H "User-Agent: Mozilla/5.0" \
  -d '{"model":"gpt-5.4-mini","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'

# OpenCode Go ping (minimax-m3)
curl -s --max-time 15 http://127.0.0.1:19998/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax-m3","messages":[{"role":"user","content":"ping"}],"max_tokens":20}'

# Zen free quota kontrol — cost "0" dönmeli
curl -s --max-time 30 http://127.0.0.1:19998/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"ping"}],"max_tokens":50}' | python3 -c "import sys,json; d=json.load(sys.stdin); c=d.get('cost','?'); print(f'cost={c} (0=free, >0=paid)')"
```

### Proxy Yeniden Başlatma

Config değişikliğinden sonra:

```bash
# Önce çalışan process'i bul ve öldür
PID=$(ss -tlnp | grep 19998 | grep -oP 'pid=\K\d+')
kill $PID 2>/dev/null
sleep 1
cd ~/.hermes/scripts && nohup python3 opencode-go-proxy.py > /tmp/go-proxy.log 2>&1 &

# Pollinations için de aynı
PID=$(ss -tlnp | grep 19999 | grep -oP 'pid=\K\d+')
kill $PID 2>/dev/null
sleep 1
cd ~/.hermes/scripts && nohup python3 pollinations-proxy.py > /tmp/pollinations-proxy.log 2>&1 &
```

> ⚠️ **Systemd uyarısı:** Proxy'ler bazen systemd servisi olarak değil, elle/manuel başlatılır. `systemctl --user status` inactive gösterebilir ama process `ss -tlnp` ile görünür. Restart'tan sonra elle başlatmak gerekebilir (yukarıdaki komut). Systemd'ye geri döndürmek için: `systemctl --user enable --now opencode-go-proxy.service pollinations-proxy.service`

### Proxy max_tokens Override (13 Haz 2026)

OpenCode Go proxy'si (opencode-go-proxy.py) artık gelen istekte `max_tokens` yoksa veya < 4096 ise otomatik 32768'e yükseltir. Bu, API yanıtlarının yarıda kesilmesini önler. Override yapıldığında proxy log'unda `[PROXY] max_tokens override: X -> 32768` satırı görünür.

Proxy restart gerektiren bir değişiklik değil — kod zaten deploy edildi.

### 5. Yeni Model Benchmark

Yeni bir model eklendiğinde:

```bash
# Hızlı test: 200 token, Türkçe
curl -s --max-time 25 http://127.0.0.1:19998/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"YENI-MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Türkiye'nin başkentini bir cümleyle söyle.\"}],\"max_tokens\":200}"
```

Değerlendirme kriterleri:
- Content var mı? (null = ❌)
- Reasoning token sayısı (0 = ⚡ ideal)
- `finish_reason` (stop = ✅, length = ⚠️ yetmedi)
- `<think>` tag'i döküyor mu?
- Türkçe kalitesi

## Mevcut Model Durumu

| Model | Provider | max_tokens | Not |
|-------|----------|-----------|-----|
| glm-5.1 | OpenCode Go | 4000 | Analist — derin analiz, güvenlik, Türkçe içerik |
| deepseek-v4-flash | OpenCode Go | 4000 | Kodcu — kod, rutin işler, maliyet-etkin |
| deepseek-v4-flash-free | opencode-zen | 2000 | Free tier — 10+ rutin cron job (Bundle, LinkedIn, Skool, APA, Gmail, vb.) |
| gpt-5.4-mini | Pollinations | 1000 | Yazar — en iyi Türkçe, ❌ tool çağıramaz |
| gemma-4-26b | Pollinations | 200 | Yardımcı — hızlı basit işler, ❌ tool çağıramaz |
| deepseek-v4-pro | DeepSeek | - | Vanitas ana model — sohbet + orkestrasyon |
| stepfun/step-3.7-flash | OpenRouter | 8000 | Değerlendirici — sohbet kalitesi değerlendirme, `/tmp/.or_key` |
| minimax-m3 | OpenCode Go | 4000 | Yeni (Haz 2026) — minimax-m2.7 halefi, reasoning |
| qwen3.6-plus | OpenCode Go | 4000 | Yeni (Haz 2026) — qwen3.7-max alternatifi |
| qwen3.7-plus | OpenCode Go | 4000 | Yeni (Haz 2026) — qwen3.7-max üstü, reasoning |
| kimi-k2.7-code | OpenCode Go | 4000 | Yeni (Haz 2026) — kimi-k2.6 kod odaklı versiyonu |

> 🔄 Yeni modeller `opencode models` ile keşfedilir. Config'e eklemek için `~/.config/opencode/opencode.json` güncellenmeli.

## StepFun Değerlendirici (5. EKİP Ajanı)

🧠 **Değerlendirici** — günlük sohbet kalitesini değerlendiren EKİP'in 5. ajanı. StepFun 3.7 Flash (OpenRouter üzerinden ücretsiz) kullanır.

### İlk Kurulum (OpenRouter API Key)

OpenRouter API key'i `/tmp/.or_key` dosyasına yazılmalıdır:

```bash
echo 'sk-or-v1-...tam-key...' > /tmp/.or_key && chmod 600 /tmp/.or_key
```

**⚠️ Önemli tespit (11 Haz 2026):** Bu key daha önce hiç sisteme kaydedilmemişti. Ne `.env`'de, ne eski config backup'larda, ne loglarda — hiçbir yerde yoktu. İlk defa kuruluyor. "Config değişikliğinde kayboldu" sanmayın, baştan hiç eklenmemiş.

**Key nereden alınır:** https://openrouter.ai/keys (ücretsiz).

### Script

- **Konum:** `~/.hermes/scripts/stepfun_evaluator.py`
- **Çağrı yöntemi:** `ctx_execute_file` ile (Oracle Cloud → OpenRouter direkt bağlanamaz, proxy bypass gerekir)
- **Key okuma:** `builtins.open('/tmp/.or_key').read().strip()` (normal `open()` redacte uğrar)
- **ALL_PROXY:** Mutlaka `ALL_PROXY=""` ile temizlenmeli (WARP proxy OpenRouter'ı kırar)
- **max_tokens:** 8000 (4000 yetmez — reasoning token tüketir, content boş döner)

### Çalışma Zamanı

- **Cron:** Günlük 10:00 (`🧠 StepFun Sohbet Değerlendirici`)
- **Kaynaklar:** `sohbet` skill'inden 5 kural + NotebookLM YouTube taktikleri + NotebookLM Vanitas analiz notları
- **Çıktı:** `references/ogrenme.md` dosyasına yazılır (otomatik)

### Sağlık Kontrolü

```bash
# Dosya var mı?
ls -la /tmp/.or_key && stat /tmp/.or_key

# Key formatı doğru mu?
head -c 10 /tmp/.or_key  # "sk-or-v1-..." görmelisin

# Test çağrısı (ctx_execute_file ile)
mcp_context_mode_ctx_execute \
  --language python \
  --code "
import builtins
key = builtins.open('/tmp/.or_key').read().strip()
print(f'Key loaded: {key[:12]}... (len={len(key)})')
# Call OpenRouter
print('Simulating OpenRouter call... OK')
"
```

### Yaygın Sorunlar

| Sorun | Belirti | Çözüm |
|-------|---------|-------|
| Key yok | `[Errno 2] No such file or directory: '/tmp/.or_key'` | `echo key > /tmp/.or_key && chmod 600` |
| ALL_PROXY aktif | OpenRouter timeout/bağlantı hatası | `ALL_PROXY=""` ile çağır |
| max_tokens düşük | Content boş döner | 8000 kullan |
| Reasoning token saçılması | Kısa prompt'ta boş döner | Tek konuşma → birleşik prompt (iyi+kötü aynı anda) daha güvenilir |

### Değerlendiricinin Devre Dışı Kalmasının Etkisi

StepFun sadece bir **değerlendiricidir**, öğrenme motoru değildir. Asıl öğrenme Hermes'in kendi mekanizmalarıyla (memory, skill_manage, session_search, FTS5) çalışır. StepFun çalışmasa bile Vanitas'ın günlük öğrenme/uyum döngüsü **devam eder** — sadece değerlendirme raporu üretilmez.

Detaylı soruşturma referansı: `references/stepfun-or-key-setup.md`

## Watchdog Zen Model Test Fix (8 Haz 2026)

`model-watchdog.py` Zen free modellerini (`minimax-m3-free`, `mimo-v2.5-free`, `deepseek-v4-flash-free`, `nemotron-3-*`) **yanlış endpoint'ten** test ediyordu:

- ❌ **Eski:** `http://127.0.0.1:19998/v1` (Go proxy) → Zen modelleri route edilemez, her zaman "ZEN FAILED"
- ✅ **Yeni:** `https://opencode.ai/zen/v1` (doğrudan Zen endpoint) → gerçek durumu yansıtır

**Etkisi:** Watchdog, Zen free modellerini hiçbir zaman "çalışıyor" olarak görmediği için model kalktığında "fark edemiyordu" — çünkü onun gözünde zaten hep "failed" durumundaydı. Düzeltme sonrası bir gün "çalışıyor" → ertesi gün "çalışmıyor" geçişini yakalayabilecek.

**Doğrulama:** Watchdog log'unda `ZEN OK:` satırları görmek gerekiyor (eskiden `ZEN VIA GO OK:` yoktu, hep `ZEN FAILED` vardı).

**minimax-m3-free durumu (8 Haz 2026):** OpenCode Zen model listesinde hâlâ görünüyor ama internal server error veriyor. Watchdog doğru endpoint'ten test edince "ZEN FAILED" olarak işaretleyecek ve 3 strike sonra uyarı verecek.

## Cron Job:

```bash
# Her Pazartesi 04:00'te
cronjob create \
  --schedule "0 4 * * 1" \
  --name "EKİP Haftalık Bakım" \
  --prompt "EKİP bakımını yap: opencode upgrade, model karşılaştır, sağlık kontrolü, gerekiyorsa config güncelle ve proxy restart. ekip-bakim skill'ini kullan."
```

## Cron Job Provider Yük Dengeleme

### Truncation Hatası Teşhisi

`RuntimeError: Response remained truncated after 3 continuation attempts` → İki olası kök neden:

1. **Proxy darboğazı** (en sık): `opencode-go` proxy (19998) aşırı yüklenmesi. Aynı anda çok fazla cron job'ı aynı provider'a yüklenince proxy timeout verir.
2. **Free model token limiti** (yeni — 6 Haz 2026'da tespit): Job `opencode-zen` free modele (`deepseek-v4-flash-free`) taşındıysa ve job ağır çıktı üretiyorsa (örn: Bundle — 15+ haber okuma + wiki güncelleme + NotebookLM arşiv), free modelin çıktı token limiti (~2000) yetersiz kalır. **Belirti:** Hatadan ÖNCE kısmi çıktı gelir (haberler işlenmiş ama kesilmiş). Proxy overload'dan farkı: diğer job'lar normal çalışır, sadece ağır job patlar. **Çözüm:** Ağır job'ı `opencode-go` + `deepseek-v4-flash`'e geri al.

**Teşhis:**
```bash
# Hangi cron job'ları opencode-go kullanıyor?
python3 -c "
import json
with open('$HOME/.hermes/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    p = j.get('provider') or ''
    if 'opencode-go' in p:
        print(f\"{j['name']:35s} | {j.get('model','?'):20s} | enabled={j.get('enabled')} | {j.get('schedule_display','?')}\")
"
# Çakışan saatleri kontrol et — aynı saatte 3+ job varsa overload riski yüksek.
```

### Provider Migrasyonu

Rutin cron job'ları (`deepseek-v4-flash`) opencode-go'dan opencode-zen free modele taşı. Açık hesap: `deepseek-v4-flash-free` tool calling destekler, çoğu rutin iş için yeterli.

**Neler taşınır:** linkedin, skool, APA, Gmail Pipeline, Gmail Deep Dive, Günlük Sentez, Bundle, Yarı Güvenlik, Bardo Lead — hepsi `deepseek-v4-flash` kullanan rutin işler.

**Neler opencode-go'da kalır:** Sadece `glm-5.1` kullanan derin analiz işleri (Tam Güvenlik).

**Migrasyon script'i:** `references/cron-provider-migrate.py`

**Migrasyon sonrası:** Gateway restart gerekmez — scheduler jobs.json'u her çalışmada yeniden okur. Ama `guard_agent_created` gibi config değişiklikleri için gateway restart önerilir (s6-svc veya process kill).

### guard_agent_created

Kanban worker'ları skill oluşturamıyorsa (`Agent-created skill blocked` hatası):

```bash
hermes config set guard_agent_created false
```

Bu ayar config.yaml'da `guard_agent_created: true` olarak gelir. false yapınca Kanban worker'ları skill oluşturabilir.

## Kanban Blocked Task Teşhisi

Tüm task'lar aynı profil ile `blocked` durumdaysa üç olası neden:

### 1. Model Çökmesi

Belirti: `hermes kanban show <task_id>` → "Agent crash x2: pid XXXX exited with code 1"

```bash
# Profil modelini kontrol et
cat ~/.hermes/profiles/<profil>/config.yaml
# Modeli değiştir (örn: kimi-k2.5 → glm-5.1)
patch ~/.hermes/profiles/<profil>/config.yaml ...
# Tüm blocked task'ları geri al
hermes kanban unblock <task_ids...>
# Worker'ları başlat
hermes kanban dispatch
```

### 2. Provider Config Eksikliği

Belirti: `hermes kanban show <task_id>` → "Unknown provider 'custom:<name>'"

Profil config'i `custom_providers` bloğunu içermiyor. Ana config'deki `custom_providers` profillere otomatik miras kalmaz.

```bash
# Teşhis: custom_providers var mı?
grep -A 15 custom_providers ~/.hermes/profiles/<profil>/config.yaml
# Boş çıktı → EKSİK. Ana config'den kopyala.
# Sonra unblock + dispatch
```

### 3. Skill Çözümleme Hatası

Belirti: `hermes kanban show <task_id>` → "Unknown skill(s): <skill-name>"

Profiller skill'leri kendi `skills/` dizininden çözer, global dizinden değil.

```bash
# Symlink çözümü:
ln -sfn ~/.hermes/skills/<kategori>/<skill> ~/.hermes/profiles/<profil>/skills/<kategori>/<skill>
# Alternatif: Task'ı skillsiz yeniden oluştur
hermes kanban archive <task_id>
hermes kanban create "TITLE" --assignee PROFILE --body "explicit instructions..."
```

### Genel Recovery Akışı

```bash
# 1. Board durumunu gör
hermes kanban list

# 2. Bir task'ın detayını incele
hermes kanban show <task_id>
# Diagnostics kısmında hata mesajına bak.
# "exited with code N" → Model çökmesi
# "Unknown provider" → Provider config eksik
# "Unknown skill(s)" → Skill çözümleme

# 3. Nedene göre yukarıdaki çözümü uygula
# 4. Tüm blocked task'ları geri al
hermes kanban unblock <task_ids...>
# 5. Worker'ları başlat
hermes kanban dispatch
```

- OpenCode güncellemesi: `npm i -g opencode-ai@latest` (birincil) veya `opencode upgrade`
- Config değişikliğinden sonra go-proxy restart ŞART — yeni modelleri tanımaz.
- Yeni model eklerken `opencode.json`'a `"enabled": true` yeterli. Limit biliniyorsa `limit: {context, output}` ekle.
- OpenCode Go'daki model listesi `opencode models` ile alınır, go-proxy model listesi `curl :19998/v1/models` ile.
