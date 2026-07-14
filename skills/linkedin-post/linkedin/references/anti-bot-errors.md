# LinkedIn Anti-Bot Hataları

## 2026-05-23: Cron job `linkedin_sabah` başarısız

**Hata:** `RuntimeError: Your request was blocked.`
**Zaman:** 09:00 (ilk çalıştırma)
**Job ID:** 272dc0178605
**Model:** pollinations/mistral-large
**Skill:** linkedin-post:linkedin (dosya mevcut değildi — 2026-05-23'te oluşturuldu)

**Muhtemel sebep:** Firecrawl/web_extract ile LinkedIn URL'si çekilmeye çalışıldı. LinkedIn Cloudflare benzeri anti-bot koruması kullanır ve otomatik istekleri agresif şekilde engeller.

**Durum:** Cron job hala aktif, yarın 09:00'da tekrar deneyecek. Skill oluşturuldu ama cron job'un prompt'u hala eski ("Firecrawl ile LinkedIn...").

**Yapılması gerekenler:**
1. Cron job prompt'unu güncelle — alternatif kaynaklara yönlendir
2. Veya cron job'u pause et, manuel test yap
