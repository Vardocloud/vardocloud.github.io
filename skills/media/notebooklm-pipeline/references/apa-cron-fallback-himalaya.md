# APA Cron: Gmail API Fallback (Himalaya IMAP)

Google API token expired olduğunda (`GSETUP --check` → `REFRESH_FAILED`), pipeline'ı durdurma. Himalaya IMAP ile direkt gelen kutusunu tara.

## Setup Check

Himalaya zaten yapılandırılmış (`~/.config/himalaya/config.toml` + App Password). 

```bash
# IMAP ayakta mı?
cat ~/.config/himalaya/gmail_pass   # App Password dosyası
which himalaya                       # binary yüklü
```

## Gmail'de APA Mail'i Tara

```bash
# Son 50 mailde APA kaynaklı olanları bul
himalaya envelope list --page-size 50 | grep -i "apa\|american psych\|monitor\|psychology"

# Gürültüyü temizle
himalaya envelope list --page-size 50 | grep -i "apa\|american psych" | grep -iv "skool\|instagram\|noreply\|nater\|yardocloud\|digest"
```

## Neden Çalışır

- IMAP, OAuth'tan bağımsızdır — App Password ile doğrudan IMAP/SMTP erişimi vardır.
- Himalaya config'deki `backend.auth.cmd = "cat ~/.config/himalaya/gmail_pass"` App Password'i otomatik okur.
- Google API (`gws` / `google_api.py`) 7 günde bir refresh token expire olabilir — IMAP buna bağlı değildir.

## Ne Zaman Kullan

- Cron job'larda Gmail API token expired hatası alınınca
- Gmail API rate-limit'e takılınca
- Token refresh'i sessizce başarısız olunca (SIN #26: önce sessiz dene, başarısızsa IMAP fallback)

## Sınırlamalar

- `himalaya search` subcommand bu versiyonda yok — `envelope list` + `grep` kullanılır.
- IMAP arama Google API kadar hızlı DEĞİLDİR (tüm kutuyu listeler, grep filtreler).
- App Password 2FA gerektirir — eğer kullanıcı App Password'ü iptal ederse çalışmaz.

## Podcast Yayın Tarihi Belirleme Heuristiği

Bir podcast bölümünün "yeni" mi yoksa "eski ama atlanmış" mı olduğunu belirlemek için:

1. **Bölüm numarasına bak**: Higher number = daha yeni. Bonus bölümlerde numara olmaz — bunlar her zaman daha dikkatli incelenmeli.
2. **İçerikteki zaman referanslarını kontrol et**: 
   - "Mental Health Awareness Month" (Mayıs) → Mayıs veya öncesi
   - "APA 2025 Stress in America survey" → Survey bir önceki yıla aitse, podcast bu yıl içinde ama belirsiz bir tarihte
   - "New study published this month" → güncel
   - Belirli bir etkinliğe atıf varsa (APA 2026 Convention, August 6-8) → o etkinlikten önce kaydedilmiş
3. **LinkedIn/Instagram cross-reference**: APA'nın veya konuğun sosyal medyasında tanıtım yapılmışsa, paylaşım tarihi ≈ yayın tarihi.
4. **Verimsiz yöntemler** (kaçın):
   - Sayfa kaynağında JSON-LD meta verisi arama (çoğu APA podcast sayfasında yok)
   - Browser console ile sayfa meta etiketlerini tek tek sorgulama
   - RSS feed scraping (gereksiz tool call)
5. **Çok eskiyse** (2+ ay): Index'e ekle ama bu cron run'ında raporlama — sadece son 7 gün içinde yayınlanan içerik raporlanır. Eski içerik sessizce index'e eklenir.

## Test Edildi

- 20 Temmuz 2026: Gmail API `REFRESH_FAILED` → Himalaya IMAP başarıyla APA mail'lerini listeledi
- Sonuç: 10 Temmuz'dan beri yeni APA mail'i yok → [SILENT] kararı doğrulandı
