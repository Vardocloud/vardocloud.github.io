# APA (American Psychological Association) İçerik Kaynağı

## RSS Feed

**Press Releases RSS**: `https://www.apa.org/news/press/releases/press-release-rss.xml`

- Her hafta 1-2 yeni araştırma basın bülteni eklenir
- Feed yapısı: `<title>`, `<link>`, `<description>`, `<pubDate>`
- İçerikler: psikoloji araştırmaları, APA aktiviteleri, güncel olaylar

## Alternatif Yöntemler ve Maliyet Karşılaştırması

### APA İçeriğine Erişim Alternatifleri

| Yöntem | Maliyet | Incapsula | Otomasyon | Verim |
|--------|---------|-----------|-----------|-------|
| **Hermes Browser (Browserbase)** | $0 (mevcut) | ✅ Geçer | Cron ile | Tam metin |
| Scrapfly API | $0.30/1000 istek | ✅ Geçer | API ile | Tam metin |
| ZenRows | $69/ay başlangıç | ✅ Geçer | API ile | Tam metin |
| Browserless.io | $99/ay başlangıç | ⚠️ Belirsiz | API ile | Tam metin |
| Google Scholar API (SearchAPI) | $39/ay | N/A | API ile | Özet sadece |
| PubMed API | Ücretsiz | N/A | API ile | Tıbbi ağırlıklı |
| Psychology Today RSS | Ücretsiz | N/A | Curl | Popüler psikoloji |

### Karar: Browserbase Yeterli

Mevcut Hermes browser aracı (Browserbase) **ücretsiz ve çalışıyor**. Harici servise gerek yok.

### Yedek Plan

Eğer Browserbase kota dolumu veya kesinti olursa:
1. **Monitor on Psychology (Browserbase)** → tam metin makaleler, her zaman çalışır
2. **Scrapfly** → API tabanlı yedek ($0.30/bin istek)
3. **Psychology Today** → alternatif kaynak

| Kaynak | URL |
|--------|-----|
| Press Releases (son) | https://www.apa.org/news/press/releases |
| RSS Feed | https://www.apa.org/news/press/releases/press-release-rss.xml |
| PsycPORT (haber özetleri) | https://www.apa.org/news/psycport |
| Monitor on Psychology | https://www.apa.org/monitor |
| APA Journals | https://www.apa.org/pubs/journals |

## İçerik Türleri

APA press release'leri LinkedIn post'una uygun:
- Kısa, haber değeri olan başlıklar
- Araştırma bulguları (istatistiklerle)
- Pratik uygulama önerileri

Her release sayfasında detaylı makale bulunur → özetlenip Türkçe'ye uyarlanabilir.

## 🔐 Incapsula WAF ve Erişim Çözümü (29 Mayıs 2026)

APA web sitesi **Incapsula/Imperva WAF** ile korunmaktadır:

| Yöntem | Sonuç |
|--------|-------|
| **RSS Feed (curl)** | ❌ Artık Incapsula korumalı (29 Mayıs 2026 itibarıyla) — 925 byte `_Incapsula_Resource` dönüyor |
| **Hermes Browser (Browserbase)** | ✅ Çalışıyor — stealth özellikleri Incapsula'yı geçiyor |
| Playwright (local, stealth) | ❌ Headless detection + plugins=0 yakalanıyor |
| Playwright (WARP SOCKS5) | ❌ IP değişse de fingerprint yakalanıyor |
| Curl + Browserbase cookie'leri | ❌ `reese84` cookie'si browser fingerprint'e bağlı |
| **Login (Browserbase)** | ✅ Başarılı — `ERIGHTS` auth cookie'si alındı |

### Erişim Stratejisi

- **Public içerik (press releases)**: RSS → Browserbase ile tam metin. Login gerekmez.
- **Member içerik (dergiler, PsycNet)**: Browserbase → SSO login → member portal.
- **Otomasyon**: Cron job içinde `browser_navigate` + `browser_console` ile içerik çekme.

### APA Login Bilgileri

- Email: `isimgorulsunn@gmail.com`
- Şifre: `~/.hermes/secrets/apa.env` (600)
- Cookie dosyası: `~/.hermes/secrets/apa_cookies.json`
- Auth cookie: `ERIGHTS` (oturum anahtarı)
- SSO endpoint: `https://sso.apa.org/apasso/idm/apalogin?ERIGHTS_TARGET=https://www.apa.org`
- Input ID'leri: Email `#loginName`, Password `#loginPassword`

### My APA Member Portal (Tam Katalog — 29 Mayıs 2026)

**Hesap**: Vatinas Reister | International Affiliate | C2605900445 | 31/12/2026
⚠️ Auto-Renew KAPALI — manuel yenileme gerek.

**🎓 Ücretsiz CE Kursları (yeni üye hakkı — 5 adet):**

| Kurs | Tarih | CE |
|------|-------|-----|
| Biopsychosocial Approach to Grief Assessment | 24 Tem 2026 | 3 |
| Genetic Assessment in Clinical Practice | 21 Tem 2026 | 1.5 |
| Weight Stigma & Chronic Disease | 20 Tem 2026 | 2 |
| Couple Therapy for Reproductive Grief | 13 Tem 2026 | 2 |
| Ketamine-Assisted Couple Therapy | 25 Haz 2026 | 2 |
| Monitor CE Corner: OCD Diagnosis | Sürekli | — |

**📰 Monitor on Psychology (Nisan/Mayıs 2026 sayısı):**
Linkedin için en değerli kaynak. Her sayıdan 1-2 makale → post.

| Makale | LinkedIn Potansiyeli |
|--------|---------------------|
| The psychology of why we use slang | ⭐⭐⭐⭐⭐ Gençlik, kimlik |
| How learning protects the aging brain | ⭐⭐⭐⭐⭐ Nöroplastisite |
| Behavioral intervention for substance use | ⭐⭐⭐⭐ Bağımlılık |
| Buy now, pay later: financial stressor | ⭐⭐⭐⭐⭐ Güncel, herkese |
| Esports psychology | ⭐⭐⭐⭐ Yeni konu |
| Teaching writing in the age of AI | ⭐⭐⭐⭐⭐ Eğitim+teknoloji |
| AI use surges among psychologists | ⭐⭐⭐⭐⭐ Mesleki AI |

**🔬 Research Alerts**: Henüz kurulmamış. Kurulum: My APA → Research Alerts. Haftalık yeni araştırma bildirimi. Örnek konular: anxiety, depression, adolescent, AI therapy.

**📚 Dergi**: Psychological Test Adaptation and Development (aktif).

**🏛️ Diğer**: APA Divisions, Advocacy Network, APA Community Directory, Preference Center.

### LinkedIn İçerik Stratejisi

- **Monitor dergisi** → derinlemesine, klinik pratiğe uygun içerik
- **Press Releases (RSS)** → hızlı, haber değerli, haftada 1-2
- **CE kursları** → Edel'in mesleki gelişimi + öğrendiklerini paylaş
- **Kombinasyon**: Monitor (derinlik) + RSS (güncellik) + CE (kişisel deneyim)

### Pitfall: Cookie'ler curl'da ÇALIŞMAZ

Incapsula `reese84` cookie'sini browser fingerprint (TLS, canvas, WebGL, fontlar) ile doğrular. Browserbase'ten alınan cookie'ler curl/Python requests'te çalışmaz. **Her erişim için Browserbase şart.**

### Pitfall: Monitor Sayfasında Link Click Çalışmaz

APA Monitor index sayfasında (`https://www.apa.org/monitor`) makale linklerine `browser_click` ile tıklamak navigasyonu tetiklemez. Sayfa aynı kalır.

**Çözüm:** `browser_console` ile JavaScript kullanarak href'i bul, sonra `browser_navigate` ile direkt git:

```javascript
// Monitor sayfasındaki tüm linkleri tara
const links = document.querySelectorAll('a');
for (const l of links) {
  if (l.textContent.includes('makale başlığı anahtar kelimesi')) {
    return l.href;  // örn: https://www.apa.org/monitor/2026/04-05/makale-slug
  }
}
```
