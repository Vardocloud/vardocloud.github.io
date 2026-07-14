# Next.js 16 Voice Agent UI — Architecture & Pitfalls

## The Three-Layer Pattern

Next.js 16 (Turbopack) requires a specific architecture for voice agent UIs
where API keys must stay server-side but the voice UI needs browser APIs.

### Layer 1: Server Component (`page.tsx`)

```tsx
// page.tsx — SERVER COMPONENT (no 'use client')
import ClientWrapper from './ClientWrapper';

export default function Home() {
  const sonioxApiKey = process.env.SONIOX_API_KEY;
  // Or any other API key for STT/TTS

  if (!sonioxApiKey) {
    return <div>API key yapılandırılmamış</div>;
  }

  const sttConfig = { api_key: sonioxApiKey };
  const ttsConfig = { api_key: sonioxApiKey };

  return <ClientWrapper sttConfig={sttConfig} ttsConfig={ttsConfig} />;
}
```

### Layer 2: Client Wrapper (`ClientWrapper.tsx`)

```tsx
'use client';
import dynamic from 'next/dynamic';

const VoiceAgent = dynamic(() => import('./VoiceAgent'), { ssr: false });

export default function ClientWrapper({ sttConfig, ttsConfig }) {
  return <VoiceAgent sttConfig={sttConfig} ttsConfig={ttsConfig} />;
}
```

### Layer 3: Voice Agent (`VoiceAgent.tsx`)

```tsx
'use client';
// Use Web Speech API, Soniox SDK, Edge TTS, etc.
// API keys come as props — no fetch/WS needed for credentials
```

## Why Direct Import Breaks in Next.js 16

In Next.js 16 with Turbopack, importing a `'use client'` component directly
from a server component (without `dynamic()`) causes the **entire JavaScript
bundle to be silently omitted** from the HTML.

Symptoms:
- Vanitas başlığı ve butonlar görünür
- Konsol tamamen boş (no errors, no logs)
- `onClick` handlers çalışmaz
- Test butonu bile log basmaz
- `document.querySelector('script')` döner null

This happens because the server component serializes the client component's
initial HTML, but Next.js 16 Turbopack doesn't emit a `<script>` tag for the
client bundle when the import chain goes through a server component boundary
without `dynamic()`.

## Counter-Example: What NOT To Do

```tsx
// ❌ BREAKS: page.tsx (server) directly imports 'use client' component
import VoiceAgent from './VoiceAgent'; // ← JavaScript bundle silently lost

export default function Home() {
  return <VoiceAgent />;
}
```

## `dynamic()` vs Direct Import in ClientWrapper

**`dynamic()` can hang over Cloudflared tunnels.** trycloudflare sometimes
fails to serve async chunk files, causing the loading spinner to spin forever.
In that case, switch to direct import in the ClientWrapper:

```tsx
// ✅ WORKS when dynamic() hangs — VoiceAgent gömülür, ayrı chunk yok
'use client';
import VoiceAgent from './VoiceAgent';

export default function ClientWrapper({ sttConfig, ttsConfig }) {
  return <VoiceAgent sttConfig={sttConfig} ttsConfig={ttsConfig} />;
}
```

**Trade-off:** Direct import increases initial bundle size but eliminates
the chunk-loading failure mode over unreliable tunnels.

## Security Note

In POC phase, passing `process.env.API_KEY` directly to the client wrapper
is acceptable. For production, use temporary/rotating keys via an API endpoint.

## 🚨 Cloudflared TryCloudflare: POST API Requests Hang

**Critical finding:** POST fetch requests to API routes (`/api/tmp-key`, etc.)
over trycloudflare tunnels **hang indefinitely** in browsers. The Promise
never resolves nor rejects. Curl works fine; browsers silently stall.

**Why:** trycloudflare's free tier appears to have issues with POST request
proxying, especially with non-empty request bodies. The browser sends the
request but never receives a response.

**Solutions (in priority order):**
1. **Server-side rendering (SSR)** — Fetch API keys on the server and pass as
   props to client components. Eliminates the need for browser-side POST.
2. **Production build (`next start`)** — Dev mode's HMR WebSocket causes
   "Unauthorized" errors on cloudflared. `next build && next start -p 3000`
   eliminates HMR traffic and is more stable.
3. **Named Cloudflare tunnel** (paid) — More reliable than trycloudflare free.
4. **GET endpoints** — Use query params instead of POST bodies where possible.

## 🚨 Mobile Browser Compatibility

Voice agent butonları mobil browser'larda (Brave Android, Firefox Android)
`onClick` ile çalışmayabilir. **`onTouchStart` zorunludur.**

```tsx
<button
  onClick={toggleRecording}
  onTouchStart={(e) => { e.preventDefault(); toggleRecording(); }}
  className="touch-action-manipulation select-none"
>
```

**Required CSS for mobile:**
```css
button {
  touch-action: manipulation;        /* 300ms delay'i kaldırır */
  -webkit-tap-highlight-color: transparent;  /* gri flash'i kaldırır */
  cursor: pointer;                    /* imleç göster */
}
```

**Why?** Mobil browser'lar dokunma olaylarını farklı işler:
- `onClick` 300ms gecikmeyle çalışır (double-tap zoom beklemesi)
- Bazı browser'larda (Brave, Firefox Android) `onClick` hiç tetiklenmez
- `onTouchStart` anında tetiklenir
- `touch-action: manipulation` double-tap zoom'u devre dışı bırakır

## 🚨 Direct `'use client'` page.tsx: Hydration Still Fails

Even when `page.tsx` is itself a `'use client'` component with no server
component intermediary, **React may still fail to hydrate** in Next.js 16.

**Symptoms:** The HTML renders correctly (Vanitas başlığı, butonlar, durum
yazısı). `document.title` sorgulanabilir. But JavaScript testi (`onClick`,
`console.log`, `useEffect`) çalışmaz. Sayfa tepkisizdir.

**Why:** Next.js 16 Turbopack generates the client bundle and emits `<script>`
tags, but the React hydration runtime may silently abort. The `useEffect` in
`ClientWrapper` (`setJsReady(true)`) never fires — the component never mounts
on the client side.

**Confirmed on:** Next.js 16.2.9 with Turbopack, both `next dev` and
`next start` modes.

**Solution:** Always use the three-layer pattern (server page → client wrapper
→ dynamic VoiceAgent). The direct `'use client'` page.tsx approach is not
reliable.

## 🚨 Last Resort: Plain HTML + JS (Next.js'i Bypass)

When ALL Next.js/React approaches fail (hydration hangs, dynamic import stuck,
cloudflared blocks chunks), fall back to a **self-contained HTML file**:

### Steps

1. **Write `public/index.html`** — Tek dosya, tüm UI + JS içinde.
   - CSS: inline `<style>` (Tailwind kullanma)
   - JS: inline `<script>` (tüm mantık aynı dosyada)
   - API çağrıları: `fetch('/api/xxx')` ile, aynı origin'de çalışır

2. **Serve with Python** (Next.js gerekmez):
   ```bash
   cd vanitas-web/public
   python3 -m http.server 3000
   ```

3. **Or use Next.js production build** (API routes çalışır):
   ```bash
   cd vanitas-web
   next build && next start -p 3000
   ```
   Next.js, `public/index.html` varsa onu `/`'de serve eder.

4. **Tunnel ile aç**:
   ```bash
   cloudflared tunnel --url http://localhost:3000
   ```

**Avantajları:**
- React hydration sorunu tamamen ortadan kalkar
- Hiçbir chunk/WebSocket/HMR yüklenmez
- Cloudflared üzerinden sorunsuz çalışır
- Mobil browser'larda doğrudan çalışır
- Hata ayıklama çok daha kolaydır

**Dezavantajları:**
- API route'ları için ayrı bir server gerekir (veya Next.js production build)
- UI kod tekrarı (her şey tek dosyada)
- React ekosisteminden kopmuş olursunuz

### When to use this fallback

1. Cloudflared tunnel async chunk'ları serve edemiyorsa (sonsuz loading)
2. React hydration başarısız oluyorsa (konsol boş, butonlar çalışmıyor)
3. Mobil browser'da JS çalışmıyorsa
4. Hızlı POC gerekiyorsa (Next.js kurulumu olmadan)

## Testing Checklist

1. Sayfa yüklenince "T" test butonu log basıyor mu? → JavaScript çalışıyor
2. `document.querySelectorAll('script').length > 0` → bundle yüklenmiş
3. Butona basınca mikrofon izni soruluyor mu? → STT çalışıyor
4. Mobilde dene: buton anında tepki veriyor mu? → `onTouchStart` gerekebilir
5. `next dev` yerine `next start` dene — HMR sorun çıkarabilir
