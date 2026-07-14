# Skool Public URL Pattern

> Skool post'larına browser login olmadan `web_extract` ile erişme yöntemi.
> Keşif tarihi: 27 Haz 2026 — AI Automation Society Nate Herk post'ları.

## URL Formatı

```
https://www.skool.com/<topluluk-slug>/<post-slug>
```

Post slug, mail body'sindeki linkten veya `web_search` ile bulunur. Örneğin:
- `skool.com/ai-automation-society/new-video-i-asked-claude-code-to-make-me-as-much-money-as-possible`
- `skool.com/ai-automation-society/glaido-is-live-on-windows`
- `skool.com/ai-automation-society/two-ai-events-i-want-you-at-this-summer`

## Başarılı Olduğu Topluluklar

| Topluluk | Public Feed | `web_extract` Çalışır mı? |
|----------|-------------|--------------------------|
| AI Automation Society (Nate Herk) | ✅ | ✅ — tüm postlar, yorumlar, linkler dahil |
| AI Money Lab (Julian Goldie) | ❌ | ❌ — login wall |
| Yapay Zekâdan Gelire (Umut Aktu) | ❌ | ❌ — login wall |

## `web_extract`'ten Ne Gelir?

Başarılı bir `web_extract` şunları döndürür:
- **Post başlığı** (ilk satırda)
- **Post body'si** — yazarın yazdığı tam metin
- **Embed linkler** — YouTube, Google Drive, diğer URL'ler
- **Beğeni/yorum sayısı** — text içinde "X likes Y comments" formatında
- **Community yorumları** (varsa) — diğer üyelerin yanıtları

**Gelmeyenler:**
- Classroom modül içeriği (özel, login gerekir)
- Video embed içeriği (sadece linki görünür, video player değil)
- Üyelere özel dosya ekleri

## Ne Zaman Kullanılır?

1. **Skool mail bildirimi geldiğinde** — önce public URL'ini dene
2. **Topluluk Public Feed: ✅ ise** — her zaman dene
3. **Topluluk Public Feed: ❌ ise** — login gerekir, atla

## Ne Zaman Kullanılmaz?

- Classroom modülleri (private content)
- Üyelere özel video/dosya içerikleri
- Community slug'ı bilinmiyorsa veya 404 veriyorsa

## Çalışma Prensibi

Skool'un feed sayfaları (`/ai-automation-society/...`) server-side render edilir ve Cloudflare koruması altındadır. `web_extract` Hermes'in arka uç backend'ini kullanır — bu backend Cloudflare'i geçebiliyorsa içerik okunur. Browserbase'e gerek kalmaz.

## Örnek Kullanım

```python
# AI Automation Society post'una public erişim
web_extract(urls=["https://www.skool.com/ai-automation-society/new-video-i-asked-claude-code-to-make-me-as-much-money-as-possible"])
# → Post body + 316 beğeni + 238 yorum + Google Drive linkleri
# → Süre: ~5 saniye, browser açılmadı
```
