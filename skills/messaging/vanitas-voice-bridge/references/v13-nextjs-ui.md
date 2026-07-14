# v13 — Next.js UI + Groq Streaming + Web Speech TTS

**Date:** 2026-06-23
**Location:** `/home/ubuntu/vanitas-web/`

## Architecture

```
Browser (Next.js port 3000) → SonioxClient (STT, via esm.sh CDN)
  → transcript → fetch POST /api/chat
    → Server → Groq streaming (llama-4-scout, SSE)
      → streaming response → UI (auto-scroll, typing dots)
        → Web Speech API TTS (tr-TR, ücretsiz)
```

## Key Files

| File | Purpose |
|------|---------|
| `src/app/page.tsx` | Main UI: SonioxClient STT + fetch streaming + Web Speech TTS |
| `src/app/api/chat/route.ts` | Groq streaming proxy (raw fetch, no AI SDK) |
| `src/app/tmp-key/route.ts` | Soniox temporary key proxy → v12 :8765 |
| `src/app/globals.css` | Dark theme CSS |
| `src/app/layout.tsx` | Root layout |

## Groq Streaming SSE Pattern

Groq returns standard SSE: `data: {"choices":[{"delta":{"content":"text"}}]}\n\n`

Frontend parsing pattern (no AI SDK needed):
```typescript
const res = await fetch("/api/chat", { method: "POST", body: JSON.stringify({ messages }) });
const reader = res.body!.getReader();
const decoder = new TextDecoder();
let buffer = "";
let assistantMsg = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split("\n");
  buffer = lines.pop() || "";
  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const data = line.slice(6).trim();
      if (data === "[DONE]") break;
      try {
        const parsed = JSON.parse(data);
        const delta = parsed.choices?.[0]?.delta?.content;
        if (delta) assistantMsg += delta;
      } catch {}
    }
  }
}
```

API route (Next.js App Router):
```typescript
export async function POST(req: Request) {
  const { messages } = await req.json();
  const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: { "Authorization": `Bearer ${process.env.GROQ_API_KEY}` },
    body: JSON.stringify({
      model: "meta-llama/llama-4-scout-17b-16e-instruct",
      messages: [{ role: "system", content: SYSTEM_PROMPT }, ...messages],
      stream: true,
    }),
  });
  return new Response(groqRes.body, {
    headers: { "Content-Type": "text/event-stream" },
  });
}
```

## TTS: Web Speech API (Browser-native)

No server-side TTS needed. Browser's built-in `speechSynthesis`:
```typescript
const speakText = (text: string) => {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "tr-TR";
    utterance.rate = 1.05;
    window.speechSynthesis.speak(utterance);
  }
};
```
**Pros:** Ücretsiz, sıfır kurulum, native Türkçe.
**Cons:** Ses kalitesi Edge TTS'den düşük, ses seçimi yok, bazen geç başlar.

## Pitfalls

### Vercel AI SDK v6: `useChat` Removed
**⚠️** `useChat` export was removed from `ai` package in v6. `ai/react` also doesn't export it. Cannot use `useChat` with `ai@^6.0.x`.

**Fix:** Use raw `fetch` + SSE streaming (pattern above) or downgrade to `ai@5.x`.

### `@soniox/vercel-ai-sdk-provider` is Async-Only
**⚠️** The `@soniox/vercel-ai-sdk-provider` implements the Vercel AI SDK's `Transcription Interface` which uses `experimental_transcribe`. This is an **async** (file-based) transcription API (`stt-async-v4`), NOT real-time WebSocket. For real-time STT in browser, use `@soniox/client` (Web SDK) with `client.realtime.record()`.

**Real-time:** `@soniox/client` → `SonioxClient.realtime.record()` (browser WebSocket)
**Async/file:** `@soniox/vercel-ai-sdk-provider` → `soniox.transcription('stt-async-v4')` (server-side)

### `soniox` npm Package Not Found
**⚠️** `npm install soniox` returns 404. The Soniox JS packages are scoped:
- `@soniox/client` — Web SDK (browser): `npm install @soniox/client`
- `@soniox/node` — Node SDK (server): `npm install @soniox/node`
- `@soniox/vercel-ai-sdk-provider` — Vercel AI: `npm install @soniox/vercel-ai-sdk-provider`

The unscoped `soniox` name is NOT published on npm. It only exists as a Python package (`pip install soniox`).

### Temporary Key Endpoint: CORS from Next.js
**⚠️** When using Next.js (port 3000), fetch to v12 (port 8765) causes CORS errors. **Fix:** Create a proxy route in Next.js:
```typescript
// src/app/tmp-key/route.ts
export async function POST() {
  const res = await fetch("http://127.0.0.1:8765/tmp-key", { method: "POST" });
  return NextResponse.json(await res.json());
}
```

### Dynamic Import for CDN Modules
**⚠️** `@soniox/client` loaded via esm.sh CDN must use dynamic `import()`:
```typescript
const { SonioxClient } = await import("https://esm.sh/@soniox/client@2.6.0");
```
Static `import` at top of file fails because esm.sh URLs are not bundled. Use inside async function.

### GROQ_API_KEY in .env.local
**⚠️** Next.js dev server reads `.env.local`. The key must be present there for the API route to work. The key is read from `~/voice-agent-venv/.groq_key` (56 chars, `gsk_...` format).

### Next.js Middleware Token Auth
**⚠️** Tunnel URL'leri herkese açıktır. Korumak için `src/middleware.ts`:
```typescript
const VALID_TOKEN=*** || "2fcff74bacf5";
export function middleware(request) {
  const { pathname } = new URL(request.url);
  if (pathname.startsWith("/_next/") || pathname.startsWith("/api/") || pathname.startsWith("/tmp-key"))
    return NextResponse.next();
  const token = request.nextUrl.searchParams.get("token");
  if (token !== VALID_TOKEN) return new NextResponse("<h1>Access Denied</h1>", { status: 403 });
  return NextResponse.next();
}
```
Kullanım: `https://<tunnel>/?token=2fcff74bacf5` — Token'siz 403.

## Startup

```bash
# 1. Ensure v12 is running (tmp-key provider)
cd ~/voice-agent-venv && python3 vanitas_ses.py &

# 2. Start Next.js
cd ~/vanitas-web && npm run dev
# → http://localhost:3000

# 3. Cloudflare tunnel for phone access
cloudflared tunnel --url http://localhost:3000 --no-autoupdate
```

## Service Stack Summary

| Component | Port | Tech | Purpose |
|-----------|------|------|---------|
| v12 voice agent | 8765 | FastAPI + Soniox SDK | tmp-key endpoint, backward compat |
| Hermes proxy | 8767 | FastAPI + httpx | Deep path to Hermes Gateway |
| vanitas-web (v13) | 3000 | Next.js 16 + Groq | UI, STT, streaming chat |
| Hermes Gateway | 8642 | Hermes Agent | Full context LLM |
