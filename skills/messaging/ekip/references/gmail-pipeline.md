# Gmail → Bilgi Çıkarma Pipeline (EKİP)

Cron job olarak çalışan, Gmail'den bilgi çıkaran 4 adımlı pipeline.

## Mimari

```
Gmail (google-workspace) → Analist (GLM-5.1) → Yazar (GPT-5.4-mini) → NotebookLM
```

## Adımlar

### 1. Gmail Kontrolü
```bash
ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py gmail search "is:unread is:important" --max 10
ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py gmail search "is:unread -is:important" --max 10
```

**⚠️ ALL_PROXY="" ZORUNLU:** Google API WARP proxy'den geçemez. `warp-proxy` skill'i aktif sunucularda her GAPI komutunun başında `ALL_PROXY=""` olmalı.

### 2. Analist (GLM-5.1) — Sınıflandırma
```bash
curl -s --max-time 60 http://127.0.0.1:19998/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.1",
    "messages": [{"role":"user","content":"Email listesini kategorize et (iş/kişisel/spam/bülten/güvenlik), her birine 1-10 puan ver, en kritik 2 tanesini seç. KISA cevap ver.\n\nEMAIL_LISTESI"}],
    "max_tokens": 2000
  }'
```

**⚠️ GLM-5.1 ayarları:**
- `max_tokens ≥ 2000` (reasoning token'ları içeriği yemeden önce)
- Prompt sonuna **"KISA cevap ver, sadece sonuçları yaz"** ekle
- `temperature: 1.0`, `timeout: 300000` (OpenCode config)

### 3. Yazar (GPT-5.4-mini) — Türkçe Özet
```bash
curl -s --max-time 30 http://127.0.0.1:19999/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.4-mini",
    "messages": [{"role":"user","content":"Şu emaili 2 cümleyle Türkçe özetle: EMAIL_ICERIK"}],
    "max_tokens": 300
  }'
```

### 4. NotebookLM — Arşivleme
Kritik içerik varsa `🧠 Vanitas Hafıza Arşivi` notebook'una `source_add` ile ekle. Önemsiz içeriklerde bu adımı atla.

## Önem Skalası

| Puan | Anlam | Aksiyon |
|------|-------|---------|
| 9-10 | Hesap güvenliği, acil iş | NotebookLM + bildir |
| 7-8 | Önemli güvenlik/kişisel | NotebookLM |
| 4-6 | Bilgilendirme | Sadece günlük özette |
| 1-3 | Spam/bülten | Görmezden gel |

## Güvenlik Mail'leri — Özel İşleme

Instagram, Google, banka gibi güvenlik bildirimleri **her zaman kritik kabul edilir**. Şifre değişikliği, yeni cihaz girişi, konum değişikliği → anında NotebookLM + bildir.

## Pitfall'lar

- **ALL_PROXY="" unutma:** WARP aktif sunucuda GAPI çağrıları proxy üzerinden timeout olur
- **GLM-5.1 reasoning:** max_tokens < 2000'de tüm token'lar reasoning'e gider, content boş döner
- **Ctrl+C safety:** Pipeline cron'da çalışır — her adımın kendi timeout'u olmalı
