---
title: Canlı Toplantı Öncesi Hazırlık Kontrol Listesi
date: 2026-07-17
---

# Canlı Toplantı/Seminer/Webinar Öncesi Hazırlık

**Bu liste, 17 Temmuz 2026'da skill yüklemeyi atladığım için tüm semineri kaçırmamın ardından yazıldı. Atlamayacaksın.**

## ⏰ Toplantıdan HEMEN ÖNCE

### Adım 0: Skill Yükle (ZORUNLU)
```python
skill_view('meet-bot')  # Google Meet için
# veya
skill_view('media-transcription')  # Transkript için
```
Bir `meet.google.com` URL'i, Zoom linki, "toplanti/katil/join/seminer" ifadesi → ÖNCE skill yükle.  
**ASLA doğrudan tool'a atlama.**

### Adım 1: Ses Altyapısı
```bash
pulseaudio --check && echo "✅ Ses kaydı mümkün" || echo "❌ Ses kaydı yok (no sudo ise kurulamaz)"
```
- PulseAudio/ALSA yoksa → Edel'e hemen bildir: "Ses kaydı yapamıyorum, sen kaydeder misin?"
- Groq Whisper olmadan Türkçe transkript kaliteli olmaz

### Adım 2: API Key'ler
```bash
[ -n "$GROQ_API_KEY" ] && echo "✅ Groq KEY var" || echo "❌ Groq KEY yok"
```

### Adım 3: Script
```bash
# Ses kaydı yok:
python3 scripts/meet_autojoin.py "$URL" "$GUEST_NAME"
# Ses kaydı var:
# meet_join + ffmpeg + Groq Whisper
```

## ⏸️ Toplantı SIRASINDA

1. Join sonrası doğrula: `meet_status` veya `browser_snapshot`
2. Caption dili Türkçe'ye çevrildi mi kontrol et
3. Edel'e bildir: "✅ Toplantıdayım, transkript aliniyor."
4. Bot düşerse hemen rejoin dene
5. Periyodik kontrol: her 2-3 dk sessizce `meet_status`

## ❌ ASLA YAPMA

- Skill yüklemeden işe başlama
- Google Meet captions'ı Türkçe için yeterli GÖRME
- Dene-yanıl yaparken toplantının yarısını kaçırma
- Ses kaydı yokken "oldu" deyip geçiştirme
- Bir yöntem başarısız olunca hemen diğerine atlama (önce skill'e bak)
