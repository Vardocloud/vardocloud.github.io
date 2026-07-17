---
name: meet-bot
description: "Google Meet ve Zoom toplantılarına otomatik katılım, transkripsiyon ve ses kaydı."
version: 1.13.0
metadata:
  hermes:
    category: meet-bot
---

# Meet-Bot Skill

Google Meet ve Zoom toplantılarına otomatik katılım, transkripsiyon ve ses kaydı.

## 📋 TOPLANTI ÖNCESİ ZORUNLU KONTROL LİSTESİ

Her canlı toplantı/seminer/webinar öncesinde şu adımları sırayla uygula. **17 Temmuz 2026: bu liste atlandı → 259 satır anlamsız transkript, kaçan seminer.**

### Adım 0: Skill'i Yükle (ASLA ATLAMA)
Bir `meet.google.com` URL'i veya "toplantı/katıl/join/seminer" ifadesi gördüğünde:
```python
skill_view('meet-bot')   # ← İLK BUNU YAP
```

### Adım 1: Ses Altyapısını Kontrol Et
```bash
pulseaudio --check && echo "✅ Ses kaydı mümkün" || echo "❌ Ses kaydı yok"
```
- **PulseAudio çalışıyorsa** → `meet_join` + ffmpeg ses kaydı + Groq Whisper
- **PulseAudio yoksa (no sudo ile)** → Edel'e hemen bildir: "Ses yakalayamıyorum, sen kaydeder misin?"
- Ses kaydı yokken Meet captions'ı Türkçe için yeterli GÖRME

### Adım 2: Groq API Key Doğrula
```bash
[ -n "$GROQ_API_KEY" ] && echo "✅ KEY VAR" || bws secret list 2>/dev/null | grep -q GROQ_API_KEY && echo "✅ BWS'DE VAR" || echo "❌ KEY YOK"
```
Groq Whisper olmadan Türkçe transkript kaliteli olmaz.

### Adım 3: Doğru Scripti Çalıştır
```bash
# Ses kaydı yok → text-only transkript:
python3 ~/.hermes/skills/meet-bot/scripts/meet_autojoin.py "$MEET_URL" "$GUEST_NAME"

# Ses kaydı var → hermes meet join + ffmpeg + Groq Whisper
```

### Adım 4: Join Sonrası Doğrulama
- Toplantıda olduğunu doğrula (meet_status / browser_snapshot)
- Caption dili Türkçe'ye çevrildi mi kontrol et
- Edel'e bildir: "✅ Toplantıdayım, transkript alınıyor."

---

## 🏆 Join Yöntem Sırası (Karar Ağacı)

| Ne zaman | İlk dene | Başarısız olursa |
|----------|----------|-----------------|
| PulseAudio var | `meet_join` | Hermes browser tools + Companion mode |
| "host denied admission" | Browser tools + Companion mode | Chrome CDP (port 18800) |
| WSL/lokal, Chromium profili var | Cookie export → `meet_join` | Chrome CDP + Companion mode |
| Chrome CDP port 18800 açık | Chrome CDP + Companion mode | Edel'e bildir |
| Hepsi başarısız | Edel'e: "Katılamadım. Mac'inden dener misin?" | - |

**Detaylı auth/yöntem bilgisi:** `references/` dizinindeki dosyalara bak.

---

## ⚠️ Caption Quality Warning (Türkçe)

**Google Meet otomatik altyazıları Türkçe için GÜVENİLİR DEĞİLDİR.** Meet'in İngilizce çevirisi Türkçe konuşmayı anlamsız karakterlere dönüştürür.

| Dil | Meet Caption Kalitesi | Önerilen |
|-----|----------------------|----------|
| İngilizce | ✅ Yüksek | Meet captions yeterli |
| Türkçe | ❌ Anlamsız karakterler | **Groq Whisper (whisper-large-v3, language=tr)** — `media/media-transcription` skill'ine bak |

**Meet captions kararı:** Sadece İngilizce içerikte kullan. Türkçe'de asla birincil yöntem olarak kullanma.

---

## 🔧 meet_autojoin.py Script

**Konum:** `scripts/meet_autojoin.py` (skill altında)

Chrome CDP (port 18800) + Companion mode ile join eder, captions'ı Türkçe'ye çevirir, transkript alır. PulseAudio gerektirmez.

```bash
python3 scripts/meet_autojoin.py "https://meet.google.com/xxx-yyyy-zzz" "Berkcan"
```

Detaylar: script'in kendisinde ve `references/chrome-cdp-meet.md`

---

## 🔄 Hermes Browser Tools ile Join (Fallback)

browser_navigate → "Continue without microphone" → "Got it" → isim gir → "Other ways to join" → "Use Companion mode" → toplantıda

**Caption dili düzeltme:** browser_click(@e28) → "Turkish (Turkey)" seç → yeni captions Türkçe gelir.

Detaylı adımlar: `references/companion-mode-join.md`

---

## Pitfalls

- Camoufox/Firefox → join yapar ama **captions çalışmaz** (Firefox headless'ta [role="region"] gelmez)
- Chrome CDP → en güvenilir caption yöntemi, Edel'in hesabı login, 2FA gerekmez
- meet_join "host denied admission" → genelde false positive (browser unsupported), Companion mode dene
- Telegram'dan meet.google.com URL'i görünce → otomatik skill yükle + script çalıştır
- NotebookLM auth cookies → **flat list** formatında kaydet (Playwright context.cookies()). Dict with 'cookies' key → TypeError.
- nlm login --cdp-url → yeni Chrome açar, bekleme yapar. --manual ile export edilmiş cookies kullan.
- Dil değiştirilmezse İngilizce captions Türkçe'yi anlamsız karakterlere dönüştürür

---

## Referanslar

| Dosya | İçerik |
|-------|--------|
| `references/auth-troubleshooting.md` | Auth sorun giderme |
| `references/browser-unsupported.md` | Chromium "browser not supported" bypass |
| `references/chrome-cdp-meet.md` | Chrome CDP join + caption capture |
| `references/chromium-profile-auth.md` | ~/.config/chromium profili kullanımı |
| `references/companion-mode-join.md` | Companion mode adım adım |
| `references/cookie-export-auth.md` | Cookie export yöntemi |
| `references/host-denied.md` | "host denied admission" tanı |
| `references/zoom-recording.md` | Zoom kaydı (ayrı skill) |
| `scripts/meet_autojoin.py` | Otomatik join + transkript scripti |
| `scripts/camoufox-companion-transcriber.py` | Camoufox Companion mode scripti |
| `scripts/camoufox-meet-recorder.py` | Camoufox + ses kaydı scripti |
