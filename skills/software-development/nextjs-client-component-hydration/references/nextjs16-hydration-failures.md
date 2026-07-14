# Next.js 16 Hydration Failure Patterns (1 July 2026)

## Setup
- Model: deepseek-v4-flash via OpenCode
- Next.js 16.2.9 (Turbopack)
- React 19.2.4
- Host: WSL (Ubuntu), target: mobile phone via Cloudflare trycloudflare tunnel

## Error 1: page.tsx `'use client'` — JavaScript Yüklenmez

**Belirti:** Sayfada `<script>` tag'i yok, butonlara tıklanamıyor,
konsolda `__NEXT_DATA__` yok. Server component HTML'i gelir ama
client bundle gönderilmez.

**Yanlış:**
```typescript
// page.tsx — sayfa route dosyası
'use client';
import VoiceAgent from './VoiceAgent';
export default function Home() {
  return <VoiceAgent />;
}
```

**Sonuç:** `<script src="...page_tsx..." async>` var ama bu chunk
sadece page component'ini içerir. VoiceAgent import'u tree-shake
edilir ve client'a gitmez. Butonlar statik HTML olarak kalır.

**Doğru:** page.tsx server component kalır, ClientWrapper araya girer.
(Bkz: SKILL.md → page.tsx `'use client'` Limitation)

## Error 2: Server Component → Client Component Direct Import

**Belirti:** `page.tsx` (server) → `VoiceAgent` ('use client') direkt
import. Sayfa "Vanitas Voice" başlığını gösterir ama JavaScript
çalışmaz. `document.querySelectorAll('script').length` 18+ olmasına
rağmen React hydrate olmaz.

**Error 1033** Cloudflare hatası görülmez ama sayfa fonksiyonel değildir.

**Teşhis (browser console'dan):**
```javascript
// React hydrate olmuş mu?
document.querySelector('#js-test')?.textContent
// "⏳ JavaScript yükleniyor..." — hydrate OLMAMIŞ

// Bundle yüklenmiş mi?
document.querySelectorAll('script').length
// 18+ — yüklenmiş ama React başlamamış

// Server'dan gelen "404" iç gömülü mü?
document.body.innerHTML.includes('This page could not be found.')
// EVET — Next.js sayfayı bulamadığı için not-found render etmiş
```

## Error 3: dynamic() Import Sonsuz Loading

**Belirti:** `ClientWrapper` mount olur, loading animasyonu gösterir,
ama `VoiceAgent` dynamic import'ı hiç tamamlanmaz.

**Kod:**
```typescript
const VoiceAgent = dynamic(() => import('./VoiceAgent'), { ssr: false });
```

**Teşhis:**
- `performance.getEntriesByType('resource')` → `.js` chunk'ları
  yüklenmiş görünür (664B gibi küçük boyutlar)
- Ama dynamic import'ın bağımlılıkları (`@soniox/react` vs.)
  yüklenmez, Promise pending kalır
- Cloudflared üzerinden JavaScript chunk'ları doğru sırada
  yüklenemez

**Çözüm:** dynamic() kullanma, direkt import kullan:
```typescript
import VoiceAgent from './VoiceAgent';  // direkt import
```

## Error 4: Cloudflared "Unauthorized" + HMR

**Belirti:** Cloudflared log'unda:
```
Unable to reach the origin service: malformed HTTP response "Unauthorized"
```

**Sebep:** Next.js dev server'ın HMR WebSocket'i cloudflared ile
çakışır. Cloudflared, `/webpack-hmr` endpoint'ine yapılan WebSocket
isteklerini HTTP isteği sanıp "Unauthorized" hatası alır.

**Aynı tunnel üzerinden curl testi çalışır** (HTTP istekleri sorunsuz
geçer) ama browser'daki HMR WebSocket bağlantısı kopar.

**Çözüm:** Tunnel'ı kill et, yeniden başlat:
```bash
pkill -f cloudflared
~/cloudflared tunnel --url http://localhost:3000
```

## Error 5: npx next build'den sonra 500 Internal Server Error

**Belirti:** `rm -rf .next` + `npm run dev` sonrası localhost 500 atar.

**Sebep:** Eski bir `next dev` process'i port 3000'i işgal etmiştir.
Yeni process farklı port (3001) açar ama eski process 500 döner.

**Çözüm:**
```bash
lsof -ti:3000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
rm -rf .next
npm run dev
```

## Error 6: trycloudflare DNS Kaydı Oluşmaz

**Belirti:** `curl https://xxx.trycloudflare.com` → `Could not resolve host`
Cloudflared "running" görünür ama URL erişilemez.

**Teşhis:**
```bash
curl -s -o /dev/null -w "%{http_code}" https://<tunnel-url>
# 000 — DNS çözülemedi (exit code 6)
```

**Sebep:** trycloudflare geçici domain'leri bazen DNS kaydını hiç
oluşturamaz. Özellikle üst üste hızlıca yeni tunnel açılırsa.

**Çözüm:** Tunnel process'ini kill et, 5sn bekle, yeniden başlat.
Yeni URL üretilir. Eski URL kalıcı olarak ölür.

## Error 7: next start (production) ile Tunnel Çalışmaz

**Belirti:** `npx next start -p 3000` ile cloudflared, connectivity
pre-check'lerden geçer ama tarayıcı Error 1033 alır.

**Sebep:** Production server'ın health check response'u ile dev
server'ınki farklıdır. Cloudflared production server'a bağlanırken
beklediği yanıtı alamaz.

**Çözüm:** Dev server kullan (`npm run dev`). Production server
sadece doğrudan erişim (localhost veya reverse proxy arkasında) için
uygundur, cloudflared tunnel için değil.