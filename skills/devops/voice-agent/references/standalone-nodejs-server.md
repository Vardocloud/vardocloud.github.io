# Standalone Node.js Server — Next.js Bypass Pattern

**Tarih:** 2026-07-01
**Proje:** vanitas-web (Voice Agent v13 Web Speech API + Edge TTS)

## Ne Zaman Kullanılır

Next.js 16'nın aşağıdaki sorunlarından biriyle karşılaşıldığında:

1. `src/app/` route'ları 404 döndürüyor (build'de görünür, serve'de yok)
2. Cloudflared tunnel async chunk'ları yükleyemiyor (sonsuz loading)
3. Hydration başarısız (butonlar çalışmıyor, konsol boş)
4. Port 3000 EADDRINUSE (gizli LISTEN socket)

## Mimari

```
Browser → Cloudflare Tunnel → Node.js :3005
  ├─ GET /index.html → public/index.html (statik)
  ├─ POST /api/chat → Groq LLM (streaming)
  └─ POST /api/tts → edge-tts CLI → MP3
```

**Tek port, tek origin → CORS sorunu yok.**

## İmplementasyon

Dosya: `~/vanitas-web/server.mjs` (7000 bayt)

```javascript
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const PUBLIC = path.join(import.meta.dirname, 'public');
const PORT = 3005;

// MIME types
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
};

// Helpers
function sendJSON(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

// Groq API key → BWS üzerinden
async function getGroqKey() {
  const { execSync } = await import('child_process');
  const result = execSync(
    '/home/ubuntu/.hermes/bin/bws secret get d686ba82-168c-4d84-a9b5-b466015dc15f',
    { encoding: 'utf-8' }
  );
  return JSON.parse(result).value;
}
```

## Bilinen Pitfall'lar

### 1. Groq Model Adı (2026-07-01)
- **Eski:** `llama-4-scout-17b-16e-instruct` → 404
- **Yeni:** `meta-llama/llama-4-scout-17b-16e-instruct`

### 2. Edge TTS Endpoint Öldü (2026-07-01)
- `speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge` → 400
- **Çözüm:** `edge-tts` Python CLI v7.2.7
- `pip install edge-tts` (sistemde zaten kurulu)

### 3. Cloudflared PATH
- Background process'lerde PATH Hermes bin dizinini içermez
- **Çözüm:** Tam yol: `/home/ubuntu/.hermes/bin/cloudflared`

### 4. Shell Injection
- `edge-tts --text ${text}` → shell injection riski
- **Çözüm:** `escapeShell()` fonksiyonu:
```javascript
function escapeShell(s) {
  return "'" + s.replace(/'/g, "'\\''") + "'";
}
```

### 5. Port 3000 Kullanılamıyor
- Gizli LISTEN socket kalıyor
- **Çözüm:** Port 3005 kullan

## Start Komutları

```bash
cd ~/vanitas-web
node server.mjs &
/home/ubuntu/.hermes/bin/cloudflared tunnel --url http://localhost:3005
```

## Dosya Yapısı

```
vanitas-web/
├── server.mjs          # Node.js sunucu (hem statik hem API)
├── public/
│   └── index.html      # Web Speech API + Vanitas UI
├── src/app/api/        # Next.js route'lar (alternatif, çalışmıyorsa kullanma)
│   ├── chat/route.ts
│   └── tts/route.ts
└── package.json        # Next.js bağımlılıkları (sadece build için)
```
