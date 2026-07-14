# Cron Failure Debugging — Sistematik Yaklaşım

## Tetikleyici
Bir cron job hata verdiğinde ("failed" status, Telegram'da hata mesajı).

## Diagnostic Flow

### 1. Job konfigürasyonunu oku
```bash
cronjob(action='list')  → job_id, model, provider, prompt_preview, enabled_toolsets
```

### 2. Hata türünü sınıflandır

| Hata | Olası Kök Neden | İlk Aksiyon |
|------|-----------------|-------------|
| `401 Unauthorized` | API key geçici hatası | Aynı provider'daki diğer job'ları kontrol et |
| `400 tools array too long` | Tool limiti aşıldı | enabled_toolsets kontrol et → MCP bypass var mı? |
| `content_policy_blocked` | Azure content filter | Token refresh dene → fallback modele geç |
| `[SILENT]` / boş yanıt | Model context overflow | Skill yüklemesi var mı kontrol et |
| Script hatası (Python/Shell) | Dosya eksik, key yok | Script'i oku, hata satırını bul |
| Timeout | Proxy darboğazı | Provider load dağılımını kontrol et |

### 3. Provider sağlığını doğrula
- **Pollinations jobs:** `model-watchdog` log'unda "POLL OK" var mı?
- **OpenCode Zen:** "ZEN OK" var mı?
- **Aynı provider'da çalışan diğer job'lar:** Onlar başarılı mı?

### 4. Script/Model uyumunu kontrol et
- Script no_agent=True ise → script'i doğrudan terminal'de çalıştır
- Job LLM-driven ise → prompt ile model/provideryı karşılaştır
- Prompt'ta yazan model ≠ config'deki model → **config drift** (düzelt)

### 5. Tool limiti kontrolü (Pollinations gpt-5.4-mini)
- enabled_toolsets var mı? Yoksa ekle
- Varsa ama hala 128+ tool → **MCP bypass** ihtimali
- Çözüm: deepseek-v4-flash-free'e geç (opencode-zen)

### 6. Fix doğrulama
- Job'ı manuel çalıştır: `cronjob(action='run', job_id='...')`
- Log kontrolü: model-watchdog.log, gateway journal
- Ertesi scheduled run'da hata tekrarlamıyor mu?

## Pitfalls

- **Tek hataya odaklanma:** Bazı job'lar aynı anda birden fazla hata verebilir (önce 401, sonra 400 tools). Her hatayı ayrı değerlendir.
- **Provider health ≠ job health:** Provider çalışıyor olabilir ama model/config uyumsuzluğu job'ı kırabilir.
- **no_agent script'leri:** LLM hata mesajı vermez, doğrudan script stdout'una bakar.
- **Prompt-model drift:** Cron job prompt'unda model adı yazıyorsa ama config farklıysa, prompt güncellenmemiş olabilir.
