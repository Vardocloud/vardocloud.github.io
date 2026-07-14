# Soniox React SDK (Next.js Entegrasyonu)

Soniox React SDK (`@soniox/react`) ile Next.js App Router üzerinde voice agent kurulumu.
Bu referans, klasik WebSocket/PCM pipeline'ı yerine Soniox'un managed STT/TTS API'sini
kullanan modern yaklaşımı belgeler.

## Mimari

```
Server Component (page.tsx)           ← API key .env.local'dan okunur
  └─ props: sttConfig, ttsConfig
      └─ Client Component (VoiceAgent.tsx)
           ├─ useRecording({config: sttConfig, ...})   ← STT
           ├─ useTts({config: ttsConfig, ...})          ← TTS
           └─ fetch('/api/chat')                        ← LLM (Groq/OpenAI)
```

Temel fark: Ses işleme tamamen browser'da (Soniox SDK yönetir).
Sunucu sadece LLM proxy'si + API key tutar. PCM/WebSocket binary yönetimi yok.

## Önemli API'ler

### useRecording (STT)

```typescript
import { useRecording } from '@soniox/react';

const recording = useRecording({
  config: { api_key: '...' },        // ZORUNLU: underscore format
  model: 'stt-rt-v5',                // Soniox STT model
  language_hints: ['tr'],            // Türkçe için
  enable_endpoint_detection: true,   // Otomatik konuşma bitişi
  onError: (err) => console.error(err),
});

// Dönüş:
recording.state          // 'idle' | 'connecting' | 'recording' | 'stopped' | 'error'
recording.isRecording   // boolean
recording.isActive      // boolean (state !== idle/stopped/canceled/error)
recording.finalText     // Son tamamlanmış metin
recording.partialText   // Anlık ara metin (interim)
recording.error         // Error | null
recording.isReconnecting // WebSocket yeniden bağlanıyor mu?
recording.start()       // ⚠️ void döndürür, Promise DEĞİL
recording.stop()        // Promise<void> döndürür
```

### useTTS

```typescript
import { useTts } from '@soniox/react';

const tts = useTts({
  config: { api_key: '...' },    // ZORUNLU: underscore format
  language: 'tr',
  onAudio: (chunk: Uint8Array) => {
    // Ses verisi geldi — AudioContext ile oynat
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

tts.speak('Merhaba');        // Ses sentezle
tts.isSpeaking               // boolean — TTS oynatıyor mu?
tts.state                    // 'idle' | 'connecting' | 'speaking' | 'stopping' | 'error'
tts.cancel()                 // Anında iptal
tts.stop()                   // Promise<void> — bitmesini bekle
```

## 🔴 Kritik Tuzaklar

### 1. start() Promise döndürmez

```typescript
// YANLIŞ — await işe yaramaz:
await recording.start();      // start() void döndürür

// DOĞRU:
recording.start();
// Hataları onError callback'inden yakala:
onError: (err) => setError(err.message)
```

### 2. Config async function ile çalışmaz

```typescript
// YANLIŞ — "config changed after mount" hatası:
const recording = useRecording({
  config: () => fetch('/api/tmp-key').then(r => r.json()),  // HATA
});

// DOĞRU — config hazır olana kadar component'i mount etme:
// Server component pattern (önerilen) veya conditional render
```

### 3. api_key (underscore) — camelCase DEĞİL

```typescript
// DOĞRU:
config: { api_key: '...' }

// YANLIŞ — TypeScript hatası:
config: { apiKey: '...' }
```

### 4. tts.isSpeaking butonu kitler

```typescript
// useTts mount olur olmaz isSpeaking=false döndürür.
// Ama bazı durumlarda undefined olabilir.
// Buton disabled={tts.isSpeaking} yaparsan kullanıcı hiç tıklayamaz.
// Çözüm: disabled'ı kaldır veya state'e göre yönet.
```

## Config Sağlama Stratejileri

### Önerilen: Server Component Pattern (Next.js App Router)

**page.tsx (Server Component):**
```typescript
import VoiceAgent from './VoiceAgent';

export default function Home() {
  const apiKey = process.env.SONIOX_API_KEY;
  if (!apiKey) return <div>API key yok</div>;
  
  return (
    <VoiceAgent
      sttConfig={{ api_key: apiKey }}
      ttsConfig={{ api_key: apiKey }}
    />
  );
}
```

**VoiceAgent.tsx (Client Component):**
```typescript
'use client';
import { useRecording, useTts } from '@soniox/react';

interface Props {
  sttConfig: { api_key: string };
  ttsConfig: { api_key: string };
}

export default function VoiceAgentInner({ sttConfig, ttsConfig }: Props) {
  const recording = useRecording({ config: sttConfig, ... });
  const tts = useTts({ config: ttsConfig, ... });
}
```

### Alternatif: Conditional Render (Client-side fetch)

```typescript
'use client';
import { useState, useEffect } from 'react';
import VoiceAgent from './VoiceAgent';

export default function Home() {
  const [config, setConfig] = useState(null);

  useEffect(() => {
    fetch('/api/tmp-key', { method: 'POST', body: JSON.stringify({...}) })
      .then(r => r.json())
      .then(d => setConfig({ api_key: d.api_key }));
  }, []);

  if (!config) return <div>Yükleniyor...</div>;
  return <VoiceAgent sttConfig={config} ttsConfig={config} />;
}
```

## Debugging

Voice agent sorunlarını tespit için sayfaya canlı debug paneli ekle:

```typescript
const [debugLog, setDebugLog] = useState<string[]>([]);
const [debugError, setDebugError] = useState<string | null>(null);

const addLog = (msg: string) => {
  console.log('[VA]', msg);
  setDebugLog(prev => [...prev.slice(-19), msg]);
};

// Her state değişimini logla:
useEffect(() => {
  addLog('State: ' + recording.state);
}, [recording.state]);

// Hataları yakala:
onError: (err) => {
  setDebugError(err.message);
  addLog('HATA: ' + err.message);
}
```

## Next.js API Route — LLM Proxy

```typescript
// app/api/chat/route.ts — Groq streaming
export async function POST(req: Request) {
  const { message, conversation } = await req.json();
  
  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.GROQ_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama-4-scout',
      messages: [
        { role: 'system', content: 'Sen Vanitas'sın...' },
        ...conversation,
        { role: 'user', content: message },
      ],
      stream: true,
    }),
  });

  return new Response(res.body, {
    headers: { 'Content-Type': 'text/event-stream' },
  });
}
```

## Next.js App Router Uyarıları

- `'use client'` component'leri server component'ten import edilebilir — Next.js otomatik client bundle'a alır
- Dynamic import (`ssr: false`) gerekmez ama AudioContext kullanımı varsa önerilir
- `.env.local`'deki değişkenler `process.env.X` ile server component'te okunur
- API route'lar Dynamic olarak işaretlenir (ƒ) — statik export çalışmaz
- `npm run dev` port değiştirebilir (3000 doluysa 3001) — cloudflared URL'ini güncelle
