# StepFun Değerlendirici Bakım Notları (8 Haz 2026)

## Script
- **Konum:** `~/.hermes/scripts/stepfun_evaluator.py`
- **Cron job:** `🧠 StepFun Sohbet Değerlendirici` (job_id: `ce2dfc29da0b`)
- **Zaman:** Her gün 10:00
- **Tür:** `no_agent=true` — doğrudan Python script çalıştırır, LLM içermez

## Dosya Bağımlılıkları

| Sabit | Yol | Tür | Not |
|-------|-----|-----|-----|
| `KEY_FILE` | `/tmp/.or_key` | Routeway API key (`sk-fmh...`) | ⚠️ **Ephemeral** — `/tmp` reboot/cleanup'ta silinir |
| `PROMPT_FILE` | `~/.hermes/skills/sohbet/references/stepfun-prompt.md` | Sistem prompt | 8 Haz'da path düzeltildi |
| `OUTPUT_FILE` | `~/.hermes/skills/sohbet/references/ogrenme.md` | Rapor çıktısı | Aynı path düzeltmesi |
| `DB` | `~/.hermes/state.db` | Session verisi | Hermes veritabanı |

## Bilinen Sorunlar

### 1. /tmp/.or_key Kaybolması
**Belirti:** `⚠️ StepFun değerlendirme hatası: [Errno 2] No such file or directory: '/tmp/.or_key'`
**Sebep:** `/tmp` dizini reboot'ta veya haftalık cleanup cron'unda (Pazar 04:00) temizlenir.

**Çözüm (öncelik sırasına göre):**
1. Kalıcı bir dizine taşı: `~/.hermes/secrets/routeway-key.txt` (önerilen)
2. Script'te `KEY_FILE` sabitini yeni yola güncelle
3. Edel key'i yazsın: `echo 'clsk-...tam-key...' > ~/.hermes/secrets/routeway-key.txt && chmod 600 ~/.hermes/secrets/routeway-key.txt`

### 2. Provider Tarihçesi: OpenRouter → Zenmux → Routeway (güncel: 20 Haz 2026)
- **31 Mayıs:** OpenRouter `stepfun/step-3.7-flash` (ücretsiz) ✅
- **8 Haziran:** StepFun ücretli oldu → Zenmux'a taşındı (402 Payment Required)
- **20 Haziran:** Edel düzeltti → gerçek provider **Routeway** (`routeway.ai`)
- **Aktif endpoint:** `https://api.routeway.ai/v1/chat/completions`
- **Key formatı:** `sk-fmh...` (Routeway API key — `clsk-` değil! Routeway docs'taki format eski; güncel key `sk-fmh` prefix ile başlıyor)
- **ALL_PROXY="" hâlâ zorunlu** — WARP Routeway'i de bloklar

### 3. Routeway API Detayları (20 Haz 2026)
- **Base URL:** `https://api.routeway.ai/v1`
- **Auth:** `Authorization: Bearer sk-fmh...` (Routeway `clsk-` formatı eski — güncel key `sk-fmh` prefix ile başlıyor)
- **Free modeller:** `:free` suffix (örn. `gpt-oss-120b:free`, `gpt-4o-mini:free`)
- **Rate limits:** 5-20 RPM / 200 RPD (free tier için)
- **Key formatı:** `sk-fmh...` (78 karakter, `sk-fmh` ile başlar — `clsk-` DEĞİL)
- **Dokümantasyon:** https://docs.routeway.ai
- **OpenAI-compatible** — script'te sadece `base_url` ve `api_key` değişir
- **⚠️ Bilinen sorun:** Key `/v1/models` endpoint'inde 200 döner (key geçerli), ama `/v1/chat/completions` 401 `Invalid API key` döner. Chat completion izni olmayan bir key olabilir veya key farklı bir provider'a ait (Edel dashboard'dan doğruladı, key Routeway için geçerli — henüz çözülmedi)
- **⚠️ Pollinations proxy (`127.0.0.1:19999`) `step-3.5-flash` modeli ile BAŞARILI çalışır** — HTTP 200, model=`stepfun/step-3.5-flash`, 109 reasoning token. Alternatif olarak denenebilir (Edel onayı gerekir)

### 4. 402 Payment Required — Model Ücretli
**Aktif model adayları (Routeway free):**
- `gpt-oss-120b:free` ($0.00) — Function Call, Reasoning, LLM ✅
- `gpt-4o-mini:free` ($0.00) — Vision, Function Call, LLM
- Diğer `:free` modeller Routeway model listesinde

### 5. Script Güncelleme (YAPILACAK — 20 Haz 2026)
Script hâlâ OpenRouter endpoint'ini (`https://openrouter.ai/api/v1`) kullanıyor ve key'i `/tmp/.or_key`'den okuyor. Yapılması gereken:
1. `API_URL` → `https://api.routeway.ai/v1/chat/completions`
2. `API_KEY` → `~/.hermes/secrets/routeway-key.txt`'den oku (kalıcı)
3. Model → `gpt-oss-120b:free` (Routeway free model)
4. Key kalıcı dizinden okunsun, `/tmp/`'den değil

### 6. Bilinen Routeway Sorunu (20 Haz 2026)
- `/v1/models` HTTP 200 ✅ (key geçerli)
- `/v1/chat/completions` HTTP 401 ❌ (Invalid API key)
- Key Bitwarden'dan alındı (`bws secret get`, `sk-fmh...`, 78 karakter)
- `/tmp/.or_key`'e yazıldı (chmod 600)
- ALL_PROXY="" ile test edildi
- Farklı auth yöntemleri (Bearer, X-API-Key), endpoint'ler, modeller denendi — hepsi 401
- 429 Too Many Failed Auth Attempts rate limit alındı
- **Çözüm önerisi:** Pollinations proxy (`127.0.0.1:19999`) `step-3.5-flash` ile çalışıyor — Edel onayı gerekir
- **Alternatif:** Key'i cloudflared tunnel + HTML form ile secure pipeline'dan tekrar gir (form: `templates/api-key-form.html` → sensitive-data-pipeline skill'i)

### 7. minimax-m3-free OpenCode Zen'den Kalktı (8 Haz 2026)
- `minimax-m3-free` OpenCode Zen model listesinde hâlâ görünüyor ama internal server error veriyor.
- Yerine geçebilecek Zen free modeller: `minimax-m2.7`, `minimax-m2.5`, `deepseek-v4-flash-free`, `mimo-v2.5-free`
- Watchdog daha önce bunu fark edemiyordu çünkü Zen modellerini Go proxy (19998) üzerinden test ediyordu → her zaman "ZEN FAILED" dönüyordu. 8 Haz'da düzeltildi: Zen modelleri artık doğrudan `https://opencode.ai/zen/v1` üzerinden test ediliyor.

## Test
```bash
ALL_PROXY="" python3 ~/.hermes/scripts/stepfun_evaluator.py
```
`ALL_PROXY=""` zorunlu — WARP Routeway'i de bloklar.
