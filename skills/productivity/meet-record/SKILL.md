---
name: meet-record
description: Google Meet toplantılarını headless Chrome+PulseAudio ile MP3 kaydetme
category: productivity
trigger: >-
  Kullanıcı "toplantı kaydı", "meeting record", "Google Meet", "meet", "seminere gir",
  "toplantıya gir", "kayıt al", "meeting join" gibi ifadeler kullandığında otomatik yüklenir.
---

# Meet Record — Google Meet Ses Kaydı

## Çalışan Yöntem (13 Haz 2026)

**Google hesabı girişli Chrome (port 9222, NotebookLM profili) + PulseAudio null-sink + ffmpeg ile başarılı kayıt.** NotebookLM Chrome'una yeni sekme açılır, mevcut sekmelere dokunulmaz.

### Akış

```
Bitwarden → bw_secure_get.py "gmail" → /tmp/bw_*.pwd (isteğe bağlı, login cookie kalıcı)
Chrome 9222 (NotebookLM profili, Google login hazır)
  → Puppeteer MCP ile bağlan
  → Meet URL'ine navigate et
  → "Hemen katıl" / "Katılma isteği" butonuna tıkla
  → Mikrofon izni sorarsa "Mikrofon olmadan devam et" seç
  → PulseAudio sink'e ses gider (genelde zoom_rec)
    → ffmpeg zoom_rec.monitor → MP3 (128kbit/s)
```

### Setup

```bash
# 1. PulseAudio null-sink var mı kontrol
pactl list sinks short | grep zoom

# 2. ffmpeg kaydı başlat
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k /tmp/meet_kaydi.mp3

# 3. Chrome port 9222 (NotebookLM) — Google girişli
# Puppeteer MCP ile bağlan
mcp_puppeteer_puppeteer_connect_active_tab(debugPort=9222)
```

### Google Giriş (İlk Sefer / Cookie Süresi Dolduysa)

```bash
# Şifreyi al (DeepSeek görmez)
python3 ~/.hermes/tools/bw_secure_get.py "gmail"
# → /tmp/bw_*.pwd (600 perms)

# Secure script ile doldur
python3 /tmp/secure_google_login.py
```

Google hesap seçici sekmesi Chrome'da açık kalır. Hesap seçilir, secure script şifreyi doldurur ve Next'e tıklar.

### Meet'e Katılma

**İki tip meeting var:**

| Tip | Buton | Ne zaman |
|---|---|---|
| Herkese açık | "Hemen katıl" (Join now) | Direkt katılabilirsin |
| Host onayı gerekli | "Katılma isteği" (Ask to join) | Host kabul edene kadar bekleme odasında kalınır |

Puppeteer MCP ile buton bul:
```js
const btns = document.querySelectorAll('button');
for (const btn of btns) {
  const t = (btn.textContent || '').trim();
  if (t.includes('Hemen katıl') || t.includes('Katılma isteği')) {
    btn.click(); break;
  }
}
```

**Mikrofon izni:** "Kullanıcıların toplantıda sizi duymasını istiyor musunuz?" diye sorarsa:
```js
// En küçük elementi bul (span.mUIrbf-vQzf8d)
"Mikrofon olmadan devam et" içeren en derin elementi bul ve tıkla
```

**Kamera hatası:** "Kamera bulunamadı" uyarısı çıkar — önemsiz, kapat butonuna tıkla.

### Ses Kontrolü (KRİTİK — Atlanırsa Boş Kayıt)

ÖNCE hangi sink'e bağlı olduğunu kontrol et:
```bash
pactl list sink-inputs | grep -E "application.name|Sink:"
# → Sink: 676 → application.name = "Chromium"
```

İKİ sink olabilir:
- `zoom_rec` (ID 676) — Chromium buraya bağlı ✅
- `zoom_recording` (ID 885) — boşta 

ffmpeg'i Chrome'un bağlı olduğu sink'in monitor'ünden başlat:
```bash
# Doğru: zoom_rec.monitor (Chrome burada)
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k /tmp/kayit.mp3

# Yanlış: zoom_recording.monitor (boş)
```

### Keepalive & Monitor

Script: `scripts/meet-monitor.py`

```bash
cd /tmp && python3 meet-monitor.py "meet.google.com/esa-jqcr-agj"
```

Her 30sn'de bir:
- Meeting sekmesi hâlâ açık mı kontrol et
- ffmpeg çalışıyor mu kontrol et, düşmüşse restart et
- Dosya büyüyor mu kontrol et

ffmpeg 86400s (24h) timeout ile başlat.

### Rejoin / Erişim Değişikliği Akışı

Meeting'den ayrıldıktan sonra "Toplantıdan ayrıldınız" ekranı gelir:
- **"Yeniden katıl"** → join sayfasına döner
- Erişim tipi değişmişse join butonu da değişir (örn. "Hemen katıl" → "Katılma isteği")

```js
// "Toplantıdan ayrıldınız" ekranından yeniden katıl
const btns = document.querySelectorAll('button');
for (const btn of btns) {
  const t = (btn.textContent || '').trim();
  if (t.includes('Yeniden katıl') || t.includes('Join again')) {
    btn.click(); break;
  }
}
```

### Re-Test / Süreklilik Testi (13 Haz 2026 — Kanıtlanmış)

User'ın "10 dk ara verip tekrar dene" talebi üzerine test edildi:

1. İlk test: 8dk 18sn kayıt ✅ → skill'e kaydedildi
2. 10dk ara → hiçbir şey resetlenmedi (Chrome 9222 ayakta, PulseAudio sink canlı)
3. İkinci test: 6dk 46sn kayıt ✅ — farklı meeting, farklı erişim tipi
4. Üçüncü test: Erişim tipi değiştirildi ("Hemen katıl" → "Katılma isteği"), yeniden join → 6dk 16sn ✅

**Sonuç:** Pipeline sürekliliği koruyor. Skill kaydı, Chrome oturumu, PulseAudio — hepsi 10dk+ boşlukta ayakta kalıyor.

### Re-Test Akışı

User "tekrar dene" dediğinde:
1. Mevcut meeting sayfasını kontrol et (hâlâ açık mı?)
2. Açık değilse → yeniden navigate et
3. Erişim tipini kontrol et (değişmiş olabilir)
4. Join + ffmpeg kayıt başlat
5. Raporla

### Erişim Tipi Değişikliği (Canlı Test — 13 Haz 2026)

Meeting sahibi **"Hemen katıl" ↔ "Katılma isteği"** arasında canlı değişiklik yapabilir. Bu durumda:

1. Sayfa yeniden yüklenince yeni buton tipi gelir
2. "Yeniden katıl" → yeni join sayfası → yeni buton tipi
3. Eskisi gibi join'le — buton metni farklı olabilir

```js
// Hangi buton tipi geldiğini algıla
const txt = document.body.innerText;
if (txt.includes('Hemen katıl')) console.log('OPEN access');
if (txt.includes('Katılma isteği')) console.log('HOST_APPROVAL access');
// Sonra uygun butona tıkla
```

### NotebookLM Chrome Kullanımı (13 Haz 2026 — Teyit Edildi)

NotebookLM'nin Chrome'u (port 9222, profil: `.notebooklm-mcp-cli/chrome-profiles/default`) Google Meet için kullanılabilir:
- **Yeni sekme açılır**, mevcut NotebookLM sekmelerine dokunulmaz
- Auth `configured` kalır, NotebookLM çalışmaya devam eder
- User "notebooklm'i bozmamışsındır" diye sordu — teyit: bozulmamıştır ✅
- Google login cookie kalıcıdır — şifreyi her seferinde girmek gerekmez

### Pitfall'lar

- **İKİ sink var:** `zoom_rec` vs `zoom_recording` — hangisine bağlı olduğunu `pactl list sink-inputs` ile kontrol et. Yanlış sink'ten kayıt = 0 byte.
- **ls size 0 gösterir:** `ls -la` çıktısı 0 byte gösterebilir ama ffmpeg aslında yazıyordur. `process poll` veya `ffprobe` ile kontrol et. `ls -la` çıktısına güvenme, ffmpeg process output'una bak.
- **NotebookLM bozulmaz:** Yeni sekme aç, mevcut NotebookLM sekmelerine dokunma. Auth "configured" kalır. Kullanıcı "notebooklm'i bozmamışsındır" diye sorar — sorun olmadığı teyit edildi.
- **Google login cookie kalıcı:** Chrome 9222 profili çerezleri tutar. Her seferinde şifre girmek gerekmez. İlk login yeterli.
- **"Katılma isteği" bekleme odası:** Host kabul edene kadar bekleme odasında kalınır. Beklerken ses gelmez. Host onaylayınca otomatik geçer.
- **Erişim tipi değişirse:** Meeting sahibi erişim tipini "Hemen katıl" ↔ "Katılma isteği" arasında değiştirebilir. Yeniden katıl butonuna basınca yeni tip algılanır.
- **Kamera hatası = safe:** Google Meet "Kamera bulunamadı" diye uyarır — kapatıp geç. Ses kaydı için önemsiz.
- **Tarayıcı uyarısı:** "Bu tarayıcı sürümü artık desteklenmiyor" — Chromium 148 eski ama çalışır, dikkate alma.

### Referanslar

- `references/test-session-2026-06-13.md` — 3 test meeting'inin detaylı kaydı
- `scripts/meet-monitor.py` — keepalive + ffmpeg monitor scripti
