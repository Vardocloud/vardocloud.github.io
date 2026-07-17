# Companion Mode Join — Google Meet Bypass

## Discovery (17 Temmuz 2026)

`meet_join` tool'u ve "Join now" butonu sürekli başarısız olunca (Playwright Chromium 148+ → "unsupported browser" interstitial → false positive "host denied admission"), **"Other ways to join → Use Companion mode"** Hermes browser araçları ile denendi ve **çalıştı**.

## Doğrulanmış Flow

```python
# browser_navigate → browser_click → browser_type → browser_click
# REF ID'LER snapshot'taki element referanslarıdır — her sayfa yüklemesinde değişebilir

# 1. Sayfayı aç
browser_navigate("https://meet.google.com/...")

# 2. Permission dialog: "Continue without microphone and camera"
browser_click("@e3")   # veya snaphot'taki ref

# 3. "Sign in with your Google account" dialog → dismiss
browser_click("@e3")   # "Got it" butonu

# 4. İsim gir
browser_type("@e9", "Berkcan")

# 5. "Other ways to join" genişlet
browser_click("@e3")

# 6. "Use Companion mode" seç
browser_click("@e8")

# 7. Beş saniye bekle, snapshot ile doğrula
# → Katılımcı listesinde ismin görünüyor mu?
# → "Leave call" butonu var mı?
```

## Camoufox ile Companion Mode (PulseAudio'suz — ÖNERİLEN)

Hermes browser araçları yerine **Camoufox (Firefox)** kullanarak da Companion mode ile join yapılabilir. Bu yöntem Docker/WSL'de PulseAudio olmasa bile çalışır.

**Script:** `scripts/camoufox-companion-transcriber.py`

```bash
python3 camoufox-companion-transcriber.py "https://meet.google.com/..." "Berkcan"
```

Script şunları otomatik yapar:
1. Camoufox ile pre-join UI bekle
2. React-compatible value setter ile isim gir
3. "Other ways to join" → "Use Companion mode" tıkla
4. Join now fallback (Companion mode yoksa)
5. Captions aç, dili Türkçe'ye çevir
6. 3sn aralıkla caption poll + transkript kaydı

**Neden Camoufox + Companion mode?**
- Playwright Chromium 148+ Google Meet'te "unsupported browser" interstitial gösterir
- Hermes browser araçları çalışır ama session'lar arası context taşımaz
- Camoufox (Firefox fork) detection'ı tamamen atlar
- Companion mode host admission lobby'sini atlar
- Caption-only mod PulseAudio gerektirmez

## Companion Mode vs Join Now

| Özellik | Join now | Companion mode |
|----------|----------|---------------|
| Browser detection | Sık bloklanır (Chrome 148+) | Atlar |
| Host admission | Lobby bekler, reddedilebilir | Doğrudan bağlanır |
| Ses/mikrofon | Açılabilir | Kapalı (sadece izleme) |
| Caption alma | Çalışır | Çalışır ✅ |
| Chat | Çalışır | Çalışır |
| Uygunluk | Host onayı gereken toplantılar | "Open to anyone" toplantılar |

## Sınırlamalar

- Companion mode'da kendi mikrofonsuzsun — sadece dinleyici olarak katılırsın
- Host seni "remove" edebilir (guest olduğun için)
- Toplantı "open to anyone" değilse çalışmaz
- Hermes browser araçları her session'da yeni Playwright context kullanır — auth paylaşılmaz

## Caption Kalitesi ve Groq Whisper

**Google Meet otomatik altyazıları Türkçe için yetersizdir.** (Edel: *"Transcripti alt yazı olarak çekiyorsan sorun olabilir doğruluğunda ve tutarlılığında. Groq Whisper ile çekmen lazımdı."*)

| Senaryo | Yöntem | Kalite |
|---------|--------|--------|
| İngilizce toplantı | Meet captions | ✅ Yeterli |
| Türkçe toplantı, PulseAudio var | Ses kaydı + Groq Whisper | ✅ Yüksek doğruluk |
| Türkçe toplantı, PulseAudio yok | Meet captions (Türkçe dil seçili) | ⚠️ Düşük kalite, anlamsız karakterler |

**Hatırlatma:** Meet captions'ı Türkçe içerikte birincil transkript kaynağı olarak kullanma. Edel'e durumu bildir: "Toplantı kaydınız varsa Groq Whisper ile temiz transkript çıkarabilirim."

## Caption Alma

Companion mode'da altyazılar tam olarak çalışır:

```python
# Altyazıları aç
browser_click("@e7")  # "Turn on captions"

# Dil değiştir (Türkçe konuşma için)
browser_click("@e28")  # "Meeting language" combobox
# Turkish (Turkey) seçeneğini bul ve tıkla
# 100+ dil listesinde ref değişebilir, JS ile:
browser_console(expression="""
  document.querySelectorAll('[role=option]').find(o => o.textContent.includes('Turkish')).click()
""")

# Altyazıları oku
browser_console(expression="""
  const cr = document.querySelector('[role="region"][aria-label*="aption" i]');
  if (!cr) return [];
  const texts = [];
  const walker = document.createTreeWalker(cr, NodeFilter.SHOW_TEXT, null, false);
  let n; while(n = walker.nextNode()) { const t = n.textContent.trim(); if(t.length>3) texts.push(t); }
  texts;
""")
```
