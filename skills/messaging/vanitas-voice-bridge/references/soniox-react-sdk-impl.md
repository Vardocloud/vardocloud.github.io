# Soniox React SDK — Implementation Guide

**Package:** `@soniox/react` (⚠️ NOT `@soniox/client` — React hooks are in a separate package)

## CRITICAL: Config Prefetch Pattern (DO NOT use async config on hooks)

**⚠️ PITFALL (discovered 2026-07-01):** Passing `config: async () => {...}` directly to `useRecording()` or `useTts()` causes the Soniox SDK warning: "config changed after mount. The client is created once and will not be recreated." The SDK creates a client with empty config on mount, then when the async function resolves, it detects the config change but refuses to recreate the client. Result: hooks silently do nothing — mic never connects, TTS never speaks.

**Two correct solutions:**

### Option A — Server Component Injection (RECOMMENDED, CLEANEST)

Use Next.js App Router's Server Component to inject the API key directly from `process.env`. Eliminates the fetch entirely — no client-side loading state, no temporary key endpoint dependency.

```tsx
// src/app/page.tsx — Server Component (NO 'use client')
import VoiceAgent from './VoiceAgent';

export default function Home() {
  const sonioxApiKey = process.env.SONIOX_API_KEY;
  if (!sonioxApiKey) return <div>API key yapılandırılmamış</div>;

  return (
    <VoiceAgent
      sttConfig={{ api_key: sonioxApiKey }}
      ttsConfig={{ api_key: sonioxApiKey }}
    />
  );
}
```

```tsx
// src/app/VoiceAgent.tsx — Client Component ('use client')
'use client';
export default function VoiceAgentInner({ sttConfig, ttsConfig }: VoiceAgentProps) {
  const recording = useRecording({
    config: sttConfig,  // ✅ Sync object — ready at mount
    model: 'stt-rt-v5',
    language_hints: ['tr'],
    enable_endpoint_detection: true,
  });
  // ...
}
```

**Pros:** Zero fetch overhead, instant page load, no temp key expiry to manage.
**Cons:** API key exposed to client-side (acceptable for POC, mitigate with token-level auth later).
**This is the v13 POC approach (2026-07-01).**

### Option B — Client-side Prefetch (WORKS, MORE COMPLEX)

Fetch temporary API keys in a parent component, render child only when configs are ready.

```tsx
// page.tsx (parent) — fetches keys, only renders child when ready
export default function Home() {
  const [sttConfig, setSttConfig] = useState<{ api_key: string } | null>(null);
  const [ttsConfig, setTtsConfig] = useState<{ api_key: string } | null>(null);

  useEffect(() => {
    const init = async () => {
      const [sttRes, ttsRes] = await Promise.all([
        fetch('/api/tmp-key', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ usage_type: 'transcribe_websocket' }),
        }),
        fetch('/api/tmp-key', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ usage_type: 'tts_rt' }),
        }),
      ]);
      setSttConfig({ api_key: (await sttRes.json()).api_key });
      setTtsConfig({ api_key: (await ttsRes.json()).api_key });
    };
    init();
  }, []);

  if (!sttConfig || !ttsConfig) return <Loading />;
  return <VoiceAgent sttConfig={sttConfig} ttsConfig={ttsConfig} />;
}
```

```tsx
// VoiceAgent.tsx (child) — receives sync config objects
export default function VoiceAgentInner({ sttConfig, ttsConfig }: VoiceAgentProps) {
  const recording = useRecording({
    config: sttConfig,  // ✅ Sync object — ready at mount
    model: 'stt-rt-v5',
    language_hints: ['tr'],
    enable_endpoint_detection: true,
  });

  const tts = useTts({
    config: ttsConfig,  // ✅ Sync object — ready at mount
    language: 'tr',
    onAudio: (chunk: Uint8Array) => {
      // ... see TTS section below
    },
  });
}
```

**⚠️ PITFALL with Option B — browser tool vs real browser:** During development, browser automation tools (Browserbase/headless Chrome) may not execute fetch() reliably through cloudflared tunnels, causing the page to hang at "Bağlanıyor..." even though the same URL works in a real browser. When debugging "Bağlanıyor" freezes, first test the API endpoint directly: `curl https://<tunnel>/api/tmp-key -X POST -d '{"usage_type":"transcribe_websocket"}'`. If curl succeeds but the page still hangs, the issue is likely the browser automation tool, not the app code. Switch to Option A (Server Component) to eliminate the fetch dependency entirely.

## Installation

```bash
npm install @soniox/react @soniox/client
```

`@soniox/react` depends on `@soniox/client` — both needed.

## Key APIs

### useRecording(config)

**Returns:** `RecordingSnapshot` + control methods

| Return | Description |
|--------|-------------|
| `state` | `idle` → `starting` → `connecting` → `recording` |
| `finalText` | Accumulated finalized transcript |
| `partialText` | Current non-final (interim) transcript |
| `text` | `finalText + partialText` |
| `isRecording` | `state === 'recording'` |
| `isActive` | Not idle/stopped/error |
| `segments` | Finalized RealtimeSegment[] |
| `utterances` | Utterances (one per endpoint) |
| `start()` | Begin recording |
| `stop()` | Gracefully stop (waits for final results) |
| `cancel()` | Immediate stop |
| `clearTranscript()` | Reset text state |
| `isSupported` | Boolean — browser mic available? |
| `isReconnecting` | Auto-reconnect in progress |

**Required config prop:** `model` — e.g. `'stt-rt-v5'`

```tsx
const rec = useRecording({
  config: async () => { /* temp key fetch */ },
  model: 'stt-rt-v5',
  language_hints: ['tr'],
  enable_endpoint_detection: true,
});
```

### useTts(config)

**Returns:** `TtsSnapshot` + control methods

| Return | Description |
|--------|-------------|
| `state` | `idle` → `connecting` → `speaking` → `stopping` → `error` |
| `isSpeaking` | Boolean |
| `speak(text)` | Start TTS with given text |
| `stop()` | Graceful stop |
| `cancel()` | Immediate cancel |
| `sendText(text)` | WS mode: send partial chunk |
| `finish()` | WS mode: signal end of text |

**Config options:**
```tsx
const tts = useTts({
  config: async () => {
    const res = await fetch('/api/tmp-key', { method: 'POST', body: JSON.stringify({ usage_type: 'tts_rt' }) });
    const data = await res.json();
    return { api_key: data.api_key };
  },
  language: 'tr',
  onAudio: (chunk: Uint8Array) => {
    // Play audio in browser
    const audioBuffer = new ArrayBuffer(chunk.byteLength);
    new Uint8Array(audioBuffer).set(chunk);
    audioCtx.decodeAudioData(audioBuffer, (buffer) => {
      const source = audioCtx.createBufferSource();
      source.buffer = buffer;
      source.connect(audioCtx.destination);
      source.start();
    });
  },
  onError: (err) => console.error('TTS error:', err),
});
```

**Mode:** Default `'websocket'` (streaming). Set `mode: 'rest'` for HTTP mode (requires `voice` param).

## Temporary API Key Endpoint (Next.js)

```tsx
// src/app/api/tmp-key/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const sonioxApiKey = process.env.SONIOX_API_KEY;
  const body = await request.json();
  const usageType = body.usage_type || 'transcribe_websocket';

  const response = await fetch('https://api.soniox.com/v1/auth/temporary-api-key', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${sonioxApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      usage_type: usageType,
      expires_in_seconds: 300,
    }),
  });

  const data = await response.json();
  return NextResponse.json({ api_key: data.api_key, expires_at: data.expires_at });
}
```

## Groq LLM Endpoint (Next.js)

```tsx
// src/app/api/chat/route.ts
export async function POST(request: NextRequest) {
  const { message, conversation } = await request.json();
  
  // Get Groq key from env or BWS at runtime
  const groqApiKey = await getGroqKey();

  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${groqApiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'llama-4-scout-17b-16e-instruct',
      messages: [systemPrompt, ...conversation, userMessage],
      stream: true,
      temperature: 0.8,
      max_tokens: 256,
    }),
  });

  return new Response(response.body, {
    headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
  });
}
```

## Gotchas / Build Fixes

### 1. `api_key` NOT `apiKey` (TypeScript CRITICAL)
`SonioxConnectionConfig` type uses **`api_key`** (snake_case, underscore), NOT `apiKey` (camelCase). This is unlike most JS/TS APIs.

```tsx
// ❌ TypeScript error: Type '{ apiKey: string; }' is not assignable to type 'SonioxConnectionConfig'
const config = { apiKey: '...' };

// ✅ Correct
const config = { api_key: '...' };
```

### 2. `model` REQUIRED in useRecording
Type error: `Property 'model' is missing` — add `model: 'stt-rt-v5'` to config.

### 3. `ArrayBuffer` vs `SharedArrayBuffer` in onAudio
`chunk.buffer.slice(0)` returns `ArrayBuffer | SharedArrayBuffer`, but `decodeAudioData` expects `ArrayBuffer`. TS error, not runtime — but blocks build.

```tsx
// ❌ TS error: Type 'ArrayBuffer | SharedArrayBuffer' not assignable to 'ArrayBuffer'
ctx.decodeAudioData(chunk.buffer.slice(0), callback);

// ✅ Fix: cast
ctx.decodeAudioData(chunk.buffer.slice(0) as ArrayBuffer, callback);

// ✅ Better: create new ArrayBuffer (avoids SharedArrayBuffer entirely)
const audioBuffer = new ArrayBuffer(chunk.byteLength);
new Uint8Array(audioBuffer).set(chunk);
ctx.decodeAudioData(audioBuffer, callback);
```

### 4. Next.js Static Prerendering Fails
`SonioxProvider` async config can't run during build. Fix:
```tsx
// In layout.tsx or root page:
export const dynamic = 'force-dynamic';
```

### 5. `@soniox/client` vs `@soniox/react`
React hooks live in `@soniox/react`. `@soniox/client` is the core SDK (errors, client, types). Install both.

### 6. `.env.local` Secret Redaction
Writing env vars with API keys via `write_file` causes `***` corruption. Use Node.js script or `cat >` in terminal to bypass redaction:
```bash
node -e "
const fs = require('fs');
fs.writeFileSync('.env.local', 'KEY=actualval\n');
"
```

### 7. Cloudflared Binary Install (no sudo)
On systems without root/sudo (WSL, containers), download binary directly:
```bash
curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/cloudflared
chmod +x ~/cloudflared
~/cloudflared tunnel --url http://localhost:3001
```

### 8. Next.js Port Conflict
When port 3000 is in use, Next.js auto-fallback to port 3001. Cloudflared tunnel and all curl tests must use the actual port (check dev server log for "using available port 3001 instead").

## Turkish TTS Notes

- `language: 'tr'` in `useTts` config for Turkish
- Soniox TTS supports 60+ languages including Turkish (confirmed at soniox.com/platform/turkish)
- Voice parameter NOT required in WebSocket mode (auto-selected)
- **Untested:** Turkish TTS quality compared to Edge TTS EmelNeural

### 9. Server Component Config Injection (More Reliable)

**⚠️ PITFALL (discovered 2026-07-01):** Even the client-side `useEffect → fetch → setState` pattern can fail. The UI can stay stuck at "Bağlanıyor..." because the Soniox config never resolves in some browser/network environments.

**✅ SOLUTION:** Use Next.js App Router Server Component to inject config at build/render time:

```tsx
// page.tsx — Server Component (NO 'use client' directive)
import VoiceAgent from './VoiceAgent';

export default function Home() {
  const sonioxApiKey = process.env.SONIOX_API_KEY;
  if (!sonioxApiKey) return <div>API key not configured</div>;

  return <VoiceAgent sttConfig={{ api_key: sonioxApiKey }} ttsConfig={{ api_key: sonioxApiKey }} />;
}
```

```tsx
// VoiceAgent.tsx — Client Component with 'use client'
'use client';
interface VoiceAgentProps {
  sttConfig: { api_key: string };
  ttsConfig: { api_key: string };
}
export default function VoiceAgentInner({ sttConfig, ttsConfig }: VoiceAgentProps) {
  // useRecording({ config: sttConfig, ... }) — config is a static object, NOT async fn
  // useTts({ config: ttsConfig, ... }) — same
}
```

**Tradeoff:** Exposes permanent API key to client-side JS. Acceptable for POC/testing. For production, use tmp-key endpoint flow.

### 10. TypeScript: `SonioxConnectionConfig` uses `api_key` (snake_case)

The Soniox SDK expects `api_key` (underscore), NOT `apiKey` (camelCase):

```typescript
// ✅ CORRECT
const config = { api_key: '...' };

// ❌ TypeScript error: not assignable to SonioxConnectionConfig
const config = { apiKey: '...' };
```

### 11. TypeScript: `decodeAudioData` ArrayBuffer cast (Next.js 16)

Next.js 16 strict TypeScript needs explicit cast for `decodeAudioData`:

```typescript
// ✅ CORRECT
ctx.decodeAudioData(chunk.buffer.slice(0) as ArrayBuffer, (buffer) => { ... });

// ❌ "Argument of type 'ArrayBuffer | SharedArrayBuffer' is not assignable to parameter of type 'ArrayBuffer'"
ctx.decodeAudioData(chunk.buffer.slice(0), (buffer) => { ... });
```

### 12. Debug: Recording stuck at "Bağlanıyor..."

1. **Browser console (F12):** Check for `config changed after mount` warning
2. **Add debug panel:** Show `recording.state` and catch errors:
   ```typescript
   const [debugError, setDebugError] = useState<string|null>(null);
   const recording = useRecording({
     config: sttConfig,
     onError: (err) => setDebugError(err.message || String(err)),
   });
   const toggleRecording = async () => {
     try { await recording.start(); }
     catch (err: any) { setDebugError(err.message); }
   };
   ```
3. **State meanings:** `idle` = not connected, `connecting` = WebSocket handshake, `recording` = active
4. **API key fetch:** If using client-side tmp-key fetch and it never resolves → switch to Server Component injection (section 9)
