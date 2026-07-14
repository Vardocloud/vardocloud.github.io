---
name: google-ads-reports
description: "Google Ads Script'ten gelen e-posta raporlarını işle, özet + aksiyon planı çıkar."
version: 1.0.0
metadata:
  hermes:
    tags: [google-ads, reports, analytics, ppc]
    category: productivity
---

# Google Ads Reports Pipeline

Google Ads Script'ten gelen günlük kampanya raporlarını işleme workflow'u.

## Nasıl Çalışır

1. **Google Ads Script** → Edel'in Google Ads hesabında çalışır (JavaScript, AdsApp API)
2. **Script** → Günlük verileri e-posta ile `isimgorulsunn@gmail.com`'a gönderir
3. **Cron job** (`google-ads-daily-report`) → Gmail'de "Google Ads Rapor" konulu e-postaları arar (10:00 daily)
4. **Vanitas** → Veriyi yorumlar, özet + aksiyon planı çıkarır

## Neden Bu Yöntem?

Google Ads API + MCP Server kullanmadık çünkü:
- **Google Cloud hesabı** kredi kartı ister (Edel'de yok)
- **Composio** ücretli (free tier 20K call/ay, sonra $29/ay)
- **Google Ads Script** tamamen ücretsiz, Google Ads hesabının içinde çalışır, hiçbir ek ücret/hesap gerekmez

## Cron Job

- **Job ID:** `f6ce99d918eb`
- **Schedule:** `0 10 * * *` (her gün 10:00)
- **Skills loaded:** `google-ads-reports`, `google-workspace`
- **Deliver:** origin (Edel'in DM'ine)

## Cron Job Sorgusu

Gmail'de "Google Ads Rapor" konulu son 3 günün okunmamış e-postalarını ara.
Varsa içeriğini al ve şu analizi yap:

1. Harcama trendi (önceki güne göre artış/azalış)
2. En çok harcama yapan kampanyalar
3. Düşük performanslı kampanyalar (yüksek harcama, düşük dönüşüm)
4. Search term fırsatları (yüksek gösterim, düşük maliyet)
5. Budget optimizasyon önerileri
6. Aksiyon planı (ne yapılmalı?)

Çıktı formatı:
📊 Google Ads Analizi
📈 Performans Özeti
⚠️ Dikkat Edilmesi Gerekenler
🎯 Aksiyon Planı

## Failure Handling (Cron Job)

Cron job headless çalıştığı için (kullanıcı yok), hata durumlarında sessizce çökmek yerine düzgün raporlamalıdır.

### Token Expired / Revoked

**Error pattern:**
```
google.auth.exceptions.RefreshError: invalid_grant: Token has been expired or revoked.
```

**Root cause (most likely):** Google OAuth uygulaması "Testing" yayın durumundadır — bu durumda refresh token'lar ~7 günde bir düşer. Uygulama "Production"a alınmadıkça bu periyodik olarak tekrarlanır.

**Recovery flow (headless cron):**

1. Token durumunu kontrol et: `ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`
2. `REFRESH_FAILED` dönerse, yeni bir auth URL oluştur:
   ```
   ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url
   ```
3. Kullanıcıya şu formatta rapor ver:
   - Sorunu açıkla (token süresi doldu, Gmail'e erişilemiyor)
   - Auth URL'yi tek satır olarak ver
   - Kullanıcıdan: tarayıcıda aç → yetkilendir → `localhost:1/?code=...` URL'sini kopyala → sana göndermesini iste
   - Uyar: Testing modunda token'lar ~7 günde bir düşer, Production'a almak kalıcı çözüm
4. Pending OAuth session (`~/.hermes/google_oauth_pending.json`) otomatik oluşur — kullanıcı code'u gönderdiğinde doğrudan exchange yapılabilir.

**Long-term fix:** Google Cloud Console → OAuth consent screen → Publishing status → **"In Production"**. Bu, 7 günlük token expiry sınırını kaldırır. Sadece Gmail/Calendar gibi non-sensitive scopes kullanılıyorsa genellikle app verification gerekmez.

**OAuth consent screen tuzakları:** Kullanıcı OAuth linkini açtığında 403 hatası alır veya Save butonu tıklanmazsa, `references/oauth-consent-screen-pitfalls.md` dosyasındaki adımları izle.

### Other API Failures

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| `HttpError 403: Insufficient Permission` | Scope revoked / changed | Kullanıcı daha geniş scope seti ile re-authorize etmeli |
| `HttpError 403: Access Not Configured` | API not enabled in Cloud project | Kullanıcı Gmail/Calendar API'yi Google Cloud Console'da etkinleştirmeli |
| Network timeout / Connection refused | VPN / proxy / WSL Docker ağı | Retry; kalıcı ise kullanıcıya bildir |

### Cron Job'a Özel Uyarılar

- **Sessiz çökme yapma:** Token hatası varsa terminalde hata fırlatıp susma — her zaman kullanıcıya bildirilebilir bir durum raporu üret.
- **ALL_PROXY="" unutma:** Google API'ye erişirken WARP/WireGuard proxy'sini bypass etmek için `ALL_PROXY=""` öneki kullanılmalı.
- **Token dosyasını asla gösterme:** `~/.hermes/google_token.json` içeriğini terminal/read_file ile okuma — client_secret ve refresh_token içerir, prompt injection riski.

## Google Ads Script

**Dosya:** `~/.hermes/scripts/google_ads_script.gs`

Script'in yaptıkları:
- Campaign performansı (gösterim, tıklama, CTR, harcama, CPC, dönüşüm)
- Günlük özet toplamları
- En çok harcanan 10 search term
- Budget kullanım yüzdeleri
- 7 günlük ortalamaya göre trend karşılaştırması
- E-posta ile gönderim (`MailApp.sendEmail`)

### Kurulum Adımları

1. `ads.google.com` → Araçlar → Scripts
2. Yeni Script → kodu yapıştır (`google_ads_script.gs`)
3. İzinleri ver (Authorize)
4. Önizleme ile test et
5. Schedule: Günlük, 09:00

### Örnek Çıktı

```
📊 Google Ads Günlük Rapor (2026-06-14)
── KAMPANYA PERFORMANSI ──
• Kampanya Adı [ENABLED]
  Gösterim: 1,234 | Tıklama: 56 | CTR: %4.54
  Harcama: $45.20 | CPC: $0.81 | Dönüşüm: 3 ($120.00)

── ÖZET ──
Toplam Harcama: $145.20
Toplam Gösterim: 5,678
...
```

## Aksiyon Planı Çıkarma

Vanitas her rapor geldiğinde şunları yapmalı:
1. Veriyi oku ve anla
2. Trendleri yorumla (artış/azalış, sebep)
3. Anomalileri işaretle (anormal harcama, düşük CTR)
4. 3-5 maddelik somut aksiyon önerisi çıkar
5. Edel'e sohbet tonunda sun
