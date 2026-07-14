# Test Session — 13 Haziran 2026

## Hedef
Meeting recording pipeline'ın her iki erişim tipinde (herkese açık + host onaylı) çalıştığını doğrulamak, sürekliliği test etmek.

## Test #1 — `meet.google.com/esa-jqcr-agj` (Herkese Açık)

| Aşama | Süre | Detay |
|---|---|---|
| Chrome 9222 bağlantı | ~2sn | Puppeteer MCP, NotebookLM Chrome |
| Google login | ~30sn | bw_secure_get.py "gmail" + secure_google_login.py |
| Meet navigate | ~5sn | Sayfa yüklendi |
| "Hemen katıl" | ~2sn | Buton bulundu ve tıklandı |
| Kamera hatası | dismiss | "Kamera bulunamadı" kapatıldı |
| ffmpeg start | ~3sn | zoom_rec.monitor üzerinden |
| **Kayıt süresi** | **8dk 18sn** | **7.9MB, 128kbit/s** |
| Sonlandırma | user: "bitti" | ffmpeg kill, tab kapatıldı |

## Ara — Skill'e Kaydetme + 10dk Bekleme

- Pipeline bilgisi `meet-record` skill'ine yazıldı
- Chrome 9222 açık kaldı
- PulseAudio sink canlı kaldı
- Xvfb :99 çalışmaya devam etti

## Test #2 — `meet.google.com/avg-rytm-roz` (Herkese Açık, 2. meeting)

| Aşama | Süre | Detay |
|---|---|---|
| Meet navigate | ~5sn | Yeni URL |
| "Hemen katıl" | ~2sn | Join now |
| Kamera hatası | dismiss | Önemsiz |
| ffmpeg start | ~3sn | zoom_rec.monitor ✅ |
| **Kayıt süresi** | **6dk 46sn** | **6.2MB, 128kbit/s** |
| Sonlandırma | user: "bitti" | ffmpeg kill |

## Test #3 — `meet.google.com/avg-rytm-roz` (Erişim Değişti: Host Onaylı)

Host (user) canlı olarak erişim tipini değiştirdi:
- **Önce:** "Hemen katıl" (herkese açık)
- **Sonra:** "Katılma isteği" (host onayı gerekli)

| Aşama | Süre | Detay |
|---|---|---|
| "Yeniden katıl" | ~2sn | Buton bulundu |
| Sayfa yenilendi | ~3sn | Yeni erişim tipi geldi |
| "Katılma isteği" | ~2sn | Ask to join gönderildi |
| Host kabul | ~3sn | User onayladı |
| Kamera hatası | dismiss | Önemsiz |
| ffmpeg start | ~3sn | zoom_rec.monitor ✅ |
| **Kayıt süresi** | **6dk 16sn** | **6.0MB, 128kbit/s** |
| Sonlandırma | user: "bitti" | ffmpeg kill |

## Toplam Sonuç

| Test | Tip | Süre | Boyut | Not |
|---|---|---|---|---|
| esa-jqcr-agj | Herkese açık | 8:18 | 7.9MB | İlk test |
| avg-rytm-roz #1 | Herkese açık | 6:46 | 6.2MB | 10dk ara sonrası |
| avg-rytm-roz #2 | Host onaylı | 6:16 | 6.0MB | Erişim tipi değişimi |

**Hepsi başarılı, hepsi 128kbit/s MP3. Pipeline sürekliliği kanıtlandı.**
