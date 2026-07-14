# APA Monitor Content Extraction

## Main Content Extraction

Monitor makalelerinde `document.querySelector('main').innerText` ÇALIŞMAZ — `<main>` sadece sidebar/metadata içerir.

**Doğru yöntemler (deneme sırası):**

1. `document.querySelector('[role="main"]').innerText` — tam metni başlıklar ve yapısal bilgiyle verir, en temiz sonuç
2. `[...document.querySelectorAll('p')].map(p => p.innerText).filter(t => t.length > 50).join('\n\n')` — fallback, kısa paragrafları (sidebar, navigasyon, footer) temizler

## URL Discovery

ÖNCELİKLİ: `web_search query="site:apa.org/monitor/2026/06 psychology"` ile keşfet. Browser kullanma — Imperva'yı tetikler.

Yedek: `browser_console` ile `[...document.querySelectorAll('a')].filter(a => a.href && a.href.includes('/monitor/2026/')).map(a => a.href)`.

## Soft-Launch Pattern

Yeni sayının ana sayfası (`/monitor/2026/07-08` gibi) 404 dönebilir ama bireysel makalelere erişilebilir. `web_search query="site:apa.org/monitor/2026/07-08"` ile bireysel makaleleri dene.

## Firecrawl (Aktif)

APA Incapsula/Imperva korumalı olsa da Firecrawl browser provider ile erişim açıldı:
- `web_extract(url)` öncelikli — Firecrawl üzerinden Imperva'yı aşar
- `browser_navigate` kullanma — hâlâ Imperva hCaptcha ile bloke olur
- Kurulum: `hermes config set web.extract_backend firecrawl`
- Gereklilik: `.env`'de `FIRECRAWL_API_KEY=fc-***`
