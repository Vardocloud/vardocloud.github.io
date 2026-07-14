---
name: nextjs-client-component-hydration
description: >-
  Next.js App Router `'use client'` component hydration and server→client
  import chain patterns. Covers known pitfalls with component bundle loading
  and Soniox React SDK integration.
trigger: >-
  Next.js, App Router, client component, server component, hydration,
  'use client' çalışmıyor, JavaScript yüklenmiyor, buton çalışmıyor,
  bundle gelmiyor, Soniox, useRecording, useTts, voice agent.
---

# Next.js Client Component Hydration Patterns

## Server → Client Import Chain

Server component'ten `'use client'` component'ine direkt import + props
geçme bazı Next.js sürümlerinde çalışmaz. Tarayıcıya `<script>` tag'i
gitmez, sayfa statik HTML olarak kalır.

**Çözüm — ClientWrapper Pattern:**

```
page.tsx (server) → ClientWrapper.tsx ('use client') → ActualComponent.tsx ('use client')
```

```typescript
// page.tsx — SERVER component
import ClientWrapper from './ClientWrapper';

export default function Home() {
  const apiKey = process.env.API_KEY;
  return <ClientWrapper config={{ api_key: apiKey }} />;
}
```

```typescript
// ClientWrapper.tsx — 'use client' ara katman (ZORUNLU)
'use client';
import ActualComponent from './ActualComponent';
export default function ClientWrapper({ config }: { config: { api_key: string } }) {
  return <ActualComponent config={config} />;
}
```

### dynamic() ile Import

`dynamic(() => import(...), { ssr: false })` bazı hosting ortamlarında
chunk yüklenmesini asla tamamlamaz (sonsuz loading). **Çözüm:**
ClientWrapper ile direkt import kullan, dynamic()'den kaçın.

## Soniox React SDK Hook Patterns

### Config Zorunlulukları

1. **`api_key` (underscore):** SonioxConnectionConfig `api_key` alanını
   kullanır. `apiKey` (camelCase) TypeScript hatası verir.

2. **Config mount öncesi hazır olmalı:** Async config function veya
   sonradan değişen config "config changed after mount" hatası üretir.
   Soniox client'ı mount anında bir kere oluşturulur, sonra değişmez.

3. **`start()` void döndürür:** `recording.start()` Promise döndürmez.
   `await start()` işe yaramaz. `Promise.race([start(), timeout])`
   void anında resolve olduğu için timeout asla tetiklenmez.
   **Hataları `onError` callback'inden yakala.**

4. **`tts.isSpeaking` tuzağı:** `disabled={tts.isSpeaking}` butonu
   kitler. Kullanıcı hiçbir tepki alamaz. Alternatif state yönetimi
   kullan veya disabled'ı kaldır.

### Mimari

```typescript
'use client';
import { useRecording, useTts } from '@soniox/react';

function VoiceAgent({ sttConfig, ttsConfig }) {
  const recording = useRecording({
    config: sttConfig,         // { api_key: '...' }
    model: 'stt-rt-v5',
    language_hints: ['tr'],
    enable_endpoint_detection: true,
    onError: (err) => setError(err.message),
  });

  const tts = useTts({
    config: ttsConfig,         // { api_key: '...' }
    language: 'tr',
    onAudio: (chunk: Uint8Array) => {
      const ctx = new AudioContext();
      ctx.decodeAudioData(chunk.buffer.slice(0) as ArrayBuffer, (buffer) => {
        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(ctx.destination);
        source.start();
      });
    },
    onError: (err) => console.error(err),
  });
}
```

### Mobil Debug

Mobil browser'larda konsol olmadığı için inline debug paneli şart:

```typescript
const [debugLog, setDebugLog] = useState<string[]>([]);
const [debugError, setDebugError] = useState<string | null>(null);

const addLog = (msg: string) => {
  setDebugLog(prev => [...prev.slice(-19), msg]);
};

// Her state değişimini, buton tıklamasını, hatayı logla
// Kırmızı banner + log listesi olarak göster
```

## Web Speech API (Soniox Alternatifi)

Soniox React SDK (`useRecording`) mobil browser'larda WebSocket bağlantısı
kuramayınca çalışmaz. **Çözüm — Web Speech API + Edge TTS:**

```typescript
'use client';
import { useState, useCallback } from 'react';

export default function VoiceAgent() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [partialText, setPartialText] = useState('');

  const getRecognition = useCallback(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Tarayıcı ses tanımayı desteklemiyor.');
      return null;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'tr-TR';
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: any) => {
      let final = '';
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }
      if (final) setTranscript(prev => prev + ' ' + final);
      if (interim) setPartialText(interim);
    };

    recognition.onerror = (event: any) => {
      setError('Ses tanıma hatası: ' + event.error);
      setIsRecording(false);
    };

    recognition.onend = () => setIsRecording(false);
    return recognition;
  }, []);

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
    } else {
      const recognition = getRecognition();
      if (!recognition) return;
      recognitionRef.current = recognition;
      recognition.start();
      setIsRecording(true);
    }
  };
}
```

**Önemli:** `recognition.continuous = true` — Türkçe'de doğal konuşma
duraklamalarını kesmeden kayıt yapar. `interimResults = true` anlık
transkripsiyon gösterimi için.

## Edge TTS API Route (Next.js)

Soniox TTS (`useTts`) WebSocket bağlantısı gerektirir ve mobilde
çalışmayabilir. **Alternatif — Edge TTS (EmelNeural Türkçe kadın sesi, ücretsiz):**

```typescript
// src/app/api/tts/route.ts
export async function POST(request: Request) {
  const { text } = await request.json();
  const ssml = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">
    <voice name="Microsoft Server Speech Text to Speech Voice (tr-TR, EmelNeural)">
      <prosody rate="0%" pitch="0%">${escapeXml(text)}</prosody>
    </voice>
  </speak>`;

  const res = await fetch(
    'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-24khz-96kbitrate-mono-mp3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
      body: ssml,
    }
  );
  return new Response(await res.arrayBuffer(), {
    headers: { 'Content-Type': 'audio/mpeg' },
  });
}
```

Browser'da oynatma:
```typescript
const ttsRes = await fetch('/api/tts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: fullResponse }),
});
const audioBlob = await ttsRes.blob();
const audio = new Audio(URL.createObjectURL(audioBlob));
audio.play();
```

## page.tsx `'use client'` Limitation (Next.js 16)

`page.tsx` dosyasına doğrudan `'use client'` koymak **yeterli değildir.**
Next.js 16'da page.tsx route dosyası olduğu için, `'use client'` directive'i
bulunsa bile client bundle'ı gönderilmeyebilir. Sayfa statik HTML olarak
kalır, hiçbir `<script>` tag'i eklenmez, React hydrate olmaz.

**Çözüm:** page.tsx **server component olarak kalır**, client component
`ClientWrapper` üzerinden import edilir:

```
page.tsx (server, sadece render) → ClientWrapper.tsx ('use client') → VoiceAgent.tsx ('use client')
```

```typescript
// page.tsx — SERVER component, ASLA 'use client' yapma
import ClientWrapper from './ClientWrapper';
export default function Home() {
  return <ClientWrapper />;
}
```

ClientWrapper en minimal `'use client'` wrapper'ı olur, direkt import ile
asıl component'i çağırır:

```typescript
// ClientWrapper.tsx — 'use client' olmak zorunda
'use client';
import VoiceAgent from './VoiceAgent';
export default function ClientWrapper() {
  return <VoiceAgent />;
}
```

**Neden dynamic() çalışmadı:** `dynamic(() => import(...), { ssr: false })`
bazı Next.js sürümlerinde chunk yüklemeyi hiç tamamlamaz (sonsuz loading
animasyonu). ClientWrapper ile direkt import daha güvenilirdir.

## Plain HTML Fallback (Next.js Pes Edince)

Next.js hydration defalarca başarısız olursa (buton çalışmıyor, JS
yükleniyor ama React hydrate olmuyor), **en hızlı çözüm Next.js'i terk
etmektir.** Tek sayfalık bir voice agent UI için React/Next.js gereksizdir.

### Adımlar

1. **Tek HTML dosyası oluştur:** `public/index.html`
   - Tüm CSS `<style>` içinde
   - Tüm JavaScript `<script>` içinde
   - API çağrıları `fetch('/api/...')` ile — backend ayrı bir portta

2. **API'leri ayrı serve et:** Next.js API route'larını ayrı bir portta
   çalıştır veya Express/Python ile yeniden yaz.

3. **Statik dosyayı serve et:**
   ```bash
   cd public && python3 -m http.server 3000
   ```

4. **Cloudflared'ı aynı porta yönlendir:**
   ```bash
   ~/cloudflared tunnel --url http://localhost:3000
   ```

### Avantajları

- ❌ React hydration sorunu yok
- ❌ Tailwind/PostCSS derleme sorunu yok
- ❌ HMR WebSocket cloudflared "Unauthorized" hatası yok
- ❌ Server/client component karmaşası yok
- ✅ Her browser'da çalışır (JS çalışıyorsa)
- ✅ Mobil dokunma event'leri sorunsuz
- ✅ Tarayıcı konsolunda direkt log görünür

### Dezavantajları

- React state management yok (manuel DOM güncelleme)
- Server-Side Rendering yok
- API route'ları ayrı yönetilmeli

### Ne Zaman Kullanılır

- POC/MVP aşamasında
- Mobil browser + Cloudflare Tunnel ile test edilirken
- Next.js hydration sorunları çözülemiyorsa
- API key'ler client'a gömülecekse (güvenlik riski kabul edilebilirse)

## Cloudflared Tunnel Troubleshooting (Genişletilmiş)

### Error 1033 — "Cloudflare Tunnel error"

**Sebep:** Cloudflared ile origin server arasında iletişim kopmuş. Genelde
HMR WebSocket bağlantısı cloudflared'ı bozar.

**Çözüm:**
```bash
pkill -f cloudflared
~/cloudflared tunnel --url http://localhost:3000
# Yeni URL oluşur — eskisi kalıcı olarak ölür
```

### DNS Çözülmüyor (Could not resolve host)

Cloudflare'in yeni trycloudflare domain'i bazen 1-2 dakika içinde DNS
kaydı oluşturamaz. Bazen de hiç oluşmaz.

**Belirtiler:**
- `curl` → `Could not resolve host` (exit code 6)
- Browser → Error 1033

**Çözüm:** Tunnel'ı kill edip yeniden başlat. Process hala "running"
görünse bile DNS kaydı oluşmamış olabilir.

```bash
process action=kill session_id=<id>
~/cloudflared tunnel --url http://localhost:3000
# YENİ bir URL alırsın — yeniden test et
```

### Production Server (next start) ile Tunnel

`next start` ile cloudflared arasında daha sık bağlantı sorunu olur.
`next dev` genelde daha kararlı çalışır. Sebebi: dev server HMR için
beklerken bağlantıyı canlı tutar, production server ise statik serving
yapar ve cloudflared'ın health check'lerine yanıt vermeyebilir.

## Mobil Event Handling

Buton `onClick` mobil browser'larda bazen tetiklenmez. **Çift katmanlı
güvence:**

```tsx
<button
  onClick={toggleRecording}
  onTouchStart={(e) => { e.preventDefault(); toggleRecording(); }}
  className="select-none touch-action-manipulation"
>
```

```css
/* globals.css */
button {
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}
body {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
```

**Neden:** Mobil browser'larda 300ms dokunma gecikmesi olabilir.
`touch-action: manipulation` bu gecikmeyi kaldırır. `onTouchStart`
dokunma anında tetiklenir (click'ten önce). `preventDefault()` çift
tetiklemeyi engeller.

## Cloudflared Tunnel Troubleshooting

### Sık Sorunlar

**1. Tunnel URL değişir:** Her `cloudflared` restart YENİ bir
trycloudflare.com URL'i üretir. Eski URL anında ölür.

**2. "Unauthorized" hatası:** Cloudflared bazen `Unable to reach the
origin service: malformed HTTP response "Unauthorized"` hatası alır.
Dev server hala çalışıyordur ama tunnel bağlantısı kopmuştur.
**Çözüm:** Tunnel'ı kill edip yeniden başlat.

**3. Binary kurulumu (sudo'suz ortam):**
```bash
curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
  -o ~/cloudflared && chmod +x ~/cloudflared
```

**4. Tunnel'ı log dosyasına yazdır (URL'i yakalamak için):**
```bash
~/cloudflared tunnel --url http://localhost:3000 2>&1 | tee /tmp/cf.log &
sleep 8
TUNNEL_URL=$(grep -oP 'https://[a-z-]+\.trycloudflare\.com' /tmp/cf.log)
```

### JavaScript'in Çalışmadığını Tespit

Sayfada JavaScript çalışmıyorsa (butonlara tepki yok, state
değişmiyor):

```typescript
// ClientWrapper.tsx'te JS test banner'ı
const [jsReady, setJsReady] = useState(false);
useEffect(() => setJsReady(true), []);

return (
  <div style={{
    position: 'fixed', top: 0, left: 0, right: 0,
    padding: '4px', fontSize: '11px', textAlign: 'center', zIndex: 9999,
    color: jsReady ? '#4ade80' : '#ef4444',
    background: jsReady ? '#052e16' : '#450a0a',
  }}>
    {jsReady ? '✅ JavaScript çalışıyor' : '⏳ JavaScript yükleniyor...'}
  </div>
);
```

## Build Kontrolü

```bash
# TypeScript + derleme testi
npx next build

# Port çakışması
lsof -ti:3000 | xargs kill -9 2>/dev/null
npm run dev

# .env lokal değişkenleri
grep -c API_KEY .env.local  # > 0 olmalı

# Browser'da script kontrolü (console'dan):
# document.querySelectorAll('script').length  # > 5 olmalı

# Cloudflared tunnel testi
curl -s -o /dev/null -w "%{http_code}" https://<tunnel>/
```