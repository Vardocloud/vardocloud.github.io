# Google Cloud IP Engellemesi — Evrensel Sorun

Oracle Cloud (ve diğer veri merkezi) IP'lerinden Google'ın TÜM hizmetlerine
otomatik erişim engelleniyor. Cookie export olmadan hiçbir yöntem çalışmaz.

## Engellenen Hizmetler

| Hizmet | Erişim Türü | Hata | Tarih |
|--------|------------|------|-------|
| Google Meet | Playwright ile giriş | `Couldn't sign you in` | 24 May 2026 |
| Google Meet | Guest join | Lobi → host denial | 24-25 May 2026 |
| YouTube (yt-dlp) | Video/audio indirme | `Sign in to confirm you're not a bot` | 27 May 2026 |
| YouTube Transcript API | Altyazı çekme | `IP blocked` | 27 May 2026 |
| loader.to | Dolaylı MP3 indirme | HTML sayfası dönüyor (JS redirect) | 27 May 2026 |
| cobalt.tools | API indirme | v7 API kapatılmış | 27 May 2026 |
| yt-downloader.net | Web indirme | Timeout | 27 May 2026 |

## Denediğimiz Tüm Başarısız Yöntemler

### Meet için
- ❌ Playwright stealth (Python)
- ❌ puppeteer-extra-plugin-stealth (Node.js)
- ❌ Chrome persistent context
- ❌ CDP bağlantısı
- ❌ OAuth token → cookie dönüşümü

### YouTube için
- ❌ yt-dlp (proxy dahil)
- ❌ youtube-transcript-api (doğrudan API)
- ❌ yt-dlp + Invidious proxy
- ❌ loader.to API → HTML redirect, ses yok
- ❌ cobalt.tools → API kapatılmış
- ❌ yt-downloader.net → timeout
- ❌ api.yt-dl.org → boş cevap

## Tek Çalışan Çözüm: Cookie Export

Edel'in kendi cihazından (telefon/bilgisayar) Google cookie'lerini dışa aktarıp
sunucuya Playwright storage state olarak yüklemek.

Detay: `cookie-export-auth.md`

## Neden Cloud IP'ler Engelleniyor?

Google, veri merkezi IP'lerini "bot" olarak işaretliyor. Kullanıcı cihazından gelen
isteğin aksine, cloud IP'den gelen her istek şüpheli. CAPTCHA, JS challenge, veya
doğrudan engelle uygulanıyor.

Bu, Google'ın abuse prevention stratejisinin bir parçası — cloud provider
değiştirsen de (AWS, Azure) aynı sorun olur.
