# Bot-Korumalı PDF'leri Çekme (Incapsula / Cloudflare)

## Problem
Bazı kurumsal siteler (APA.org, EDUCAUSE vb.) PDF'leri Incapsula, Cloudflare Bot Management veya benzeri bot koruması arkasında sunar. `curl -L -O` ile PDF indirilmeye çalışıldığında 200-300 byte'lık HTML sayfası döner (`<META NAME="robots" CONTENT="noindex,nofollow">` + Incapsula script).

## Çözüm: web_extract Kullan

Doğrudan PDF URL'sini `web_extract`'e ver. Araç, bot korumasını geçerek PDF'i Markdown'a çevirir.

```
web_extract(urls=["https://ornek.org/belge.pdf"])
```

**Neden çalışıyor:** `web_extract` arka planda bot-detection bypass mekanizmaları kullanır (Playwright/browser tabanlı extraction, user-agent rotasyonu vb.).

## Sınırlamalar
- Çıktı Markdown formatında olur — PDF'in orijinal düzeni kaybolur (tablolar, sütunlar bozulabilir)
- Büyük PDF'lerde (2MB+) özetlenir/truncate edilir — tam metin gelmeyebilir
- Her site çalışmayabilir — Incapsula'nın sıkı ayarları varsa browser ile denemek gerek

## Akış
1. Önce `curl -L -O "PDF_URL"` dene — başarılı olursa PDF yerel dosya olarak kullan
2. HTML dönerse (212 byte, Incapsula script'i var) → `web_extract` ile PDF URL'sini dene
3. `web_extract` da başarısız olursa → browser ile PDF sayfasına git, PDF'i görüntüle/kaydet

## Bilinen Çalışan URL'ler
- `https://www.apa.org/science/programs/testing/responsible-use-ai-assessment-full-report.pdf` — ✅ web_extract ile çalışır
