# APA Email Tracking Link Processing

Tracking linklerini (click.info.apa.org) asıl URL'lere çözümleme workflow'u.

## Gereken Araçlar

- Himalaya CLI
- `~/.config/himalaya/config.toml` + `gmail_pass` (App Password)
- curl

## Adım Adım

### 1. APA Email'lerini Bul

```bash
himalaya envelope list --account gmail from "apa.org"
```

Not: Himalaya query syntax'ı IMAP filter formatını kullanır, `--query` flag'i yok. Doğrudan `from "apa.org"` yaz.

### 2. Email Body'sini Oku

```bash
himalaya message read <ID> --account gmail
```

Raw MIME export için:
```bash
himalaya message export <ID> --account gmail
```

### 3. Tracking Linklerini Çıkar

APA email'lerindeki tüm linkler şu formattadır:
```
https://click.info.apa.org/?qs=ABB7InYiOjEsImQiOjQ5MzN9AAcAAAAAA...
```

Bunları regex ile bul:
```
re.findall(r'https://click\.info\.apa\.org/\?qs=[A-Za-z0-9_-]+', body)
```

### 4. Asıl URL'leri Bul

```bash
curl -sI -L --max-redirs 5 "https://click.info.apa.org/?qs=..." 2>&1 | grep -i "^location:"
```

Son `location:` header'ı asıl URL'yi verir.

### 5. URL Türünü Belirle

- `psycnet.apa.org/fulltext/` — 403 Forbidden, APA üyelik gerekli
- `www.apa.org/topics/...` — 200 OK, public
- `www.apa.org/education-career/...` — 200 OK, public
- `www.apa.org/events/...` — 200 OK, public
- `convention.apa.org/` — 200 OK, public
- `us.cnn.com/...` — Public medya haberi
- `www.cnbc.com/...` — Public medya haberi
- `www.forbes.com/...` — Public (genelde)
- `apamr.co1.qualtrics.com/...` — Public anket formu
- `apa-org.zoom.us/...` — Zoom webinar kayıt

### 6. Public Sayfaları İşle

Public APA sayfaları: `web_extract` ile içerik çekilebilir.
PsycNET makaleleri: APA login gerekir.

## Email Türleri ve İçerikleri

| Email Türü | Gönderen | İçerik |
|------------|----------|--------|
| APA Media Watch | APA Public Affairs | Medyada psikoloji haberleri (CNN, Forbes, CNBC) |
| Practice Update | APA Practice News | Güncel uygulama haberleri |
| Editor's Choice | American Psychological Association | PsycNET'ten seçme makaleler |
| Member Update | APA Membership | Üye kaynakları ve rehberler |
| CE Roundup | APA Continuing Education | Yeni webinarlar ve CE fırsatları |
| Benefits Digest | APA Membership | Üye avantajları ve etkinlikler |
| Science Spotlight | American Psychological Association | Yeni araştırma özetleri |
| Monitor on Psychology | Monitor Digital | Monitor dergisi sayısı |

## Pitfall

- Tracking linkleri çalışır ama PsycNET fulltext linkleri APA üyeliği gerektirir. Üyelik olmadan 403 döner.
- Himalaya query syntax'ı standart IMAP değildir: `from "apa.org"` şeklinde yaz, `--query from:apa.org` değil.
- Email ID'leri oturuma göre değişir — her session'da yeniden listele.
