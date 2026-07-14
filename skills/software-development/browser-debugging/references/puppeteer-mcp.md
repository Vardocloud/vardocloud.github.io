# Puppeteer MCP — Anti-Bot Bypass Alternatifi

## Ne Zaman Kullanılır

Browserbase yetersiz kaldığında veya maliyet/ping sorunu olduğunda Puppeteer MCP alternatifi. Özellikle:

- Incapsula/Imperva WAF bypass (APA, LinkedIn)
- Cloudflare JS challenge bypass (Skool, Cloudflare siteleri)
- Özel proxy gerektiğinde (WARP SOCKS5)
- Session/cookie yönetimi programatik kontrol istendiğinde
- Ücretsiz, rate-limit'siz browser otomasyonu

## Kurulum (Oracle ARM64)

```bash
# 1. Puppeteer MCP kur (community fork, official deprecated)
ALL_PROXY="" npm install -g puppeteer-mcp-server

# 2. Chromium zaten Snap ile kurulu
snap list | grep chromium  # 148.0+

# 3. Config.yaml'a ekle
# mcp_servers:
#   puppeteer:
#     command: /home/ubuntu/.npm-global/bin/mcp-server-puppeteer
```

## Stealth Plugin

MCP sunucusu standart Puppeteer kullanır. Incapsula bypass için `puppeteer-extra-plugin-stealth` gerekir:

```javascript
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
```

MCP sunucusu bunu otomatik içermez — custom wrapper gerekebilir.

## Diğer Çözümlerle Karşılaştırma

| | Browserbase | Puppeteer MCP | Playwright | Camoufox |
|---|---|---|---|---|
| **Maliyet** | Kredi/oturum | Ücretsiz | Ücretsiz | Ücretsiz |
| **Incapsula** | ✅ | ✅ (stealth ile) | ❌ (plugins=0) | ✅ |
| **Cloudflare** | ✅ | ✅ | ✅ | ✅ |
| **Özel proxy** | Kısıtlı | ✅ (herhangi) | ✅ (herhangi) | ✅ |
| **ARM64 desteği** | Cloud | ✅ (Chromium Snap) | ✅ | ❌ (x86_64 binary) |
| **Cookie yönetimi** | Temel | ✅ Tam kontrol | ✅ | ✅ |
| **Kurulum** | Yok | npm install | pip install | pip install |

## Oracle ARM64 Özel Not

- Chromium Snap ARM64 binary'dir, native çalışır
- Chrome for Testing ARM64 desteği 2026'da bekleniyor
- `puppeteer-extra-plugin-stealth` ARM64'te de çalışır
- `--no-sandbox` flag'i root kullanıcıda gerekli

## ✅ Doğrulanmış Test Sonuçları (30 Mayıs 2026)

Gerçek dünya testleri — Oracle ARM64 headless sunucuda Puppeteer MCP + xvfb ile:

| Site | WAF Türü | Sonuç | Not |
|------|----------|-------|-----|
| apa.org/monitor | Incapsula/Imperva | ✅ HTTP 200 | Screenshot alındı, sayfa içeriği görünür |
| skool.com | AWS CloudFront | ✅ HTTP 200 | Ana sayfa başarılı |
| skool.com/login | AWS CloudFront | ✅ HTTP 200 | Form doldurulabildi |
| httpbin.org/ip | Yok | ✅ HTTP 200 | IP doğrulandı |

**Sonuç:** Puppeteer MCP, Browserbase'e ücretsiz yerel alternatif olarak Incapsula ve CloudFront WAF'larını başarıyla aşıyor. ARM64 headless sunucuda çalışıyor.

**Bilinen kısıt:** `puppeteer_evaluate` React/Vue sayfalarda `undefined` dönüyor (hydration timing). Screenshot + vision alternatifi kullanılabilir.

### CSS Seçici Kısıtları (30 Mayıs 2026 — Skool taramasında keşfedildi)

Puppeteer MCP, standart Puppeteer'dan farklı olarak bazı CSS seçicileri desteklemez:

| Seçici | Puppeteer MCP | Açıklama |
|--------|---------------|----------|
| `button[type="submit"]` | ✅ Çalışır | En güvenilir buton seçicisi |
| `input[type="email"]` | ✅ Çalışır | Input seçimi |
| `input[type="password"]` | ✅ Çalışır | Input seçimi |
| `svg` | ✅ Çalışır | SVG elemanlarına tıklama |
| `button:has-text("LOG IN")` | ❌ `SyntaxError` | `:has-text()` çalışmaz |
| `a:contains("Classroom")` | ❌ `SyntaxError` | `:contains()` çalışmaz |
| `button:has()` | ❌ | `:has()` pseudo-class çalışmaz |

**Strateji:** Buton/sayfa seçimi gerektiğinde önce screenshot + vision ile sayfayı analiz et, sonra `button[type="submit"]` veya `input[type="..."]` gibi basit seçiciler kullan. Karmaşık seçiciler yerine direkt URL navigasyonu tercih et (örn. `/classroom` sayfasına gitmek için linke tıklamak yerine `puppeteer_navigate` ile direkt URL'ye git).

## Vision Analyze ile İçerik Çıkarma (Kritik Pattern)

`puppeteer_evaluate` React/Vue sayfalarda `undefined` döndüğünde ve karmaşık seçiciler (`:has-text`, `:contains`) çalışmadığında, **screenshot + vision_analyze** ikilisi sayfa içeriğini çıkarmak için en güvenilir yöntemdir:

```
puppeteer_navigate → puppeteer_screenshot → vision_analyze (detaylı soru ile)
```

**Vision analyze prompt stratejisi:**
- "List ALL posts visible" — tüm postları listele
- "What modules/courses are visible?" — Classroom içeriği
- "List group names and URLs" — dropdown/kenar çubuğu
- "What's the membership status? PENDING or JOIN?" — erişim kontrolü

**Neden çalışır:** Vision model sayfayı insan gibi okur — JS state'inden bağımsızdır, React hydration sorunlarından etkilenmez, her türlü WAF'ın ötesinde çalışır.

**Trade-off:** Her sayfa için 2-3 tool call (navigate + screenshot + vision). Büyük taramalarda token kullanımı yüksektir. Alternatif olarak, sayfa HTML'ini `web_extract` ile çekmeyi DENE (WAF yoksa daha verimli).

**Kullanım örneği (Skool taraması):**
1. `puppeteer_navigate("https://skool.com/grup-url")` 
2. `puppeteer_screenshot(name="grup-adi")`
3. `vision_analyze(question="Tüm postları, linkleri, repoları listele. Classroom içeriğini detaylı tara.")`
4. Yanıta göre bir sonraki sayfaya geç veya detaylandır

## Pitfalls

- Official Puppeteer MCP DEPRECATED (2025). Community fork `merajmehrabi/puppeteer-mcp-server` kullan
- MCP sunucusu stealth plugin ile GELMEZ — custom wrapper yazılması gerekebilir
- Snap Chromium bazen güncel olmayabilir
- WARP SOCKS5 ile kullanırken `ALL_PROXY="socks5://warp:1080"` environment ayarı gerek
