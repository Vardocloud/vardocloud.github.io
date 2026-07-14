# Puppeteer MCP Pitfalls — Vanitas Deneyimleri (30 Mayıs 2026)

## evaluate() çalışmıyor (JS-heavy sayfalar)

Puppeteer MCP'nin `evaluate` komutu React/Vue gibi client-side rendering yapan sayfalarda `undefined` dönüyor. Sayfa hydrate olmadan evaluate çalışıyor.

**Çözüm:** JS-heavy sayfalar için Browserbase kullan, Puppeteer'ı statik sayfalar için kullan.

## Ne zaman hangisi?

| Durum | Araç |
|-------|------|
| Statik sayfa, API testi, screenshot | Puppeteer MCP ✅ |
| React/Vue sayfası, form doldurma, login | Browserbase ✅ |
| Incapsula/Cloudflare bypass'lı site | Puppeteer (stealth avantajı) |

## Navigate + Screenshot çalışıyor

`puppeteer_navigate` ve `puppeteer_screenshot` sorunsuz. HTTP status ve görüntü alınabilir.

## xvfb zorunlu

Headless sunucuda `xvfb-run` wrapper kullanılır:
```yaml
mcp_servers:
  puppeteer:
    command: xvfb-run
    args: [-a, /home/ubuntu/.npm-global/bin/mcp-server-puppeteer]
```

## Install

```bash
ALL_PROXY="" npm install -g puppeteer-mcp-server
```
