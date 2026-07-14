# Node.js + Python Full-Duplex Integration

**Status:** v16 (10 Tem 2026) — FULL-DUPLEX ✅ (Soniox Voice Bot Demo, WebSocket proxy aktif)

## Architecture

```
Client (Browser)
  │
  ├─ HTTP (port 3005) — server.mjs
  │   ├─ GET / → full-duplex.html (default — WebSocket full-duplex)
  │   ├─ GET /full-duplex.html → full-duplex WebSocket client
  │   ├─ POST /api/chat → Groq LLM streaming
  │   ├─ POST /api/tts → Edge TTS
  │   ├─ POST /api/stt → Groq Whisper
  │   └─ GET /api/config → Soniox API key
  │
  └─ WebSocket (port 3005) — /ws/soniox
       └─ Proxy → ws://127.0.0.1:8765 (Python Soniox server)
            ├─ Silero VAD (barge-in)
            ├─ Soniox stt-rt-v5 (STT)
            ├─ Groq llama-3.3-70b (LLM)
            └─ Soniox tts-rt-v1 (TTS) / Edge TTS fallback
```

## Key Files

| File | Role |
|------|------|
| `~/vanitas-web/server.mjs` | Node.js HTTP server + WebSocket proxy + Python child process manager |
| `~/vanitas-web/soniox-server/main.py` | Python FastAPI/WebSocket full-duplex Soniox server |
| `~/vanitas-web/soniox-server/tools.py` | Vanitas persona + tool definitions |
| `~/vanitas-web/public/full-duplex.html` | Full-duplex frontend (WebSocket + PCM capture + TTS playback) |
| `~/vanitas-web/public/index.html` | Half-duplex fallback frontend |
| `~/vanitas-web/start_server_wrapper.sh` | Cron keeper script |
| `~/.hermes/scripts/start_vanitas_server.sh` | Cron keeper (copy in scripts dir) |

## Node.js Server Changes (server.mjs)

### WebSocket Proxy (ws package)

```javascript
import { WebSocketServer, WebSocket } from 'ws';

const wss = new WebSocketServer({ noServer: true });

wss.on('connection', (clientWs, req) => {
  const params = new URL(req.url, 'http://localhost').search;
  const pythonWs = new WebSocket(`ws://127.0.0.1:8765${params}`);

  pythonWs.on('open', () => {
    clientWs.on('message', data => pythonWs.send(data));
    pythonWs.on('message', data => clientWs.send(data));
    clientWs.on('close', () => pythonWs.close());
    pythonWs.on('close', () => clientWs.close());
  });
});

server.on('upgrade', (req, socket, head) => {
  const { pathname } = new URL(req.url, 'http://localhost');
  if (pathname === '/ws/soniox') {
    wss.handleUpgrade(req, socket, head, (ws) => {
      wss.emit('connection', ws, req);
    });
  } else {
    socket.destroy();
  }
});
```

### Python Subprocess Management

```javascript
import { spawn } from 'node:child_process';

function startSonioxPythonServer() {
  const proc = spawn('python3', ['-u', 'soniox-server/main.py'], {
    cwd: path.join(__dirname, 'soniox-server'),
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  proc.stdout.on('data', d => console.log(`[Soniox] ${d}`));
  proc.stderr.on('data', d => console.log(`[Soniox] ${d}`));
  proc.on('exit', (code) => {
    // Auto-restart after 3 seconds
    setTimeout(startSonioxPythonServer, 3000);
  });
}
```

## Process Resilience

**Problem:** Hermes `terminal(background=true)` cannot reliably keep Node.js processes alive (exits silently after 3-16s).

**Solution:** Cron-based keeper (no_agent mode, every 1 minute).

```bash
# ~/.hermes/scripts/start_vanitas_server.sh
if lsof -i:3005 -sTCP:LISTEN >/dev/null 2>&1; then
  exit 0  # Already running
fi
# Kill orphans, restart Node.js, wait for Python VAD warmup (up to 25s)
node server.mjs >> /home/ubuntu/vanitas-server-output.log 2>&1 &
```

**Cron job setup:**
```
cronjob action=create name=vanitas-server-keeper no_agent=true \
  schedule=* * * * * script=start_vanitas_server.sh
```

## Full-Duplex Frontend (full-duplex.html)

### WebSocket Connection
```javascript
const ws = new WebSocket(`ws://${location.host}/ws/soniox?language=tr&voice=Maya`);
ws.binaryType = 'arraybuffer';
```

### Audio Pipeline
- **Input:** getUserMedia → AudioContext → ScriptProcessorNode → downsample to 16kHz → PCM s16le → WebSocket
- **Output:** WebSocket binary (24kHz PCM s16le) → AudioBuffer 24000Hz → play
- **Barge-in:** `user_speech_start` message → stopPlayback() → mic capture continues

### Message Types (Server → Client)
| Type | Format | Description |
|------|--------|-------------|
| `session_start` | JSON | Session started |
| `transcription` | JSON | `final_text`, `non_final_text` |
| `llm_response` | JSON | Streaming LLM chunk (`text`) |
| `user_speech_start` | JSON | Barge-in signal |
| `user_speech_end` | JSON | User stopped speaking |
| `metric` | JSON | `llm_first_token_ms`, `llm_total_ms`, `tts_first_chunk_ms` |
| `error` | JSON | Session error |
| TTS audio | Binary | PCM s16le @ 24000 Hz |

## Startup Sequence & Timing

1. **t=0s:** Cron fires → script runs → Node.js starts → spawns Python
2. **t=1s:** Node.js HTTP server ready (port 3005)
3. **t=2s:** Python VAD model loading (silero-vad from cache)
4. **t=3s:** Python WebSocket server ready (port 8765)
5. **t=4s+:** Full system operational

## API Key Configuration

`.env` (soniox-server/.env):
```
SONIOX_API_KEY=<soniox-stt-key>
SONIOX_API_KEY_TTS=<soniox-tts-key>  # Often same as STT key
OPENAI_API_KEY=<groq-api-key>
OPENAI_MODEL=llama-3.3-70b-versatile
OPENAI_BASE_URL=https://api.groq.com/openai/v1
WEBSOCKET_HOST=127.0.0.1
WEBSOCKET_PORT=8765
```

**⚠️ Pitfall:** `SONIOX_API_KEY_TTS` must be set separately. If empty, TTSProcessor fails to connect to Soniox TTS WebSocket → session immediately closes with code 1005.

## Persona Configuration

İki ayrı kod yolunda **iki farklı prompt** var — senkronize edilmezse tutarsızlık olur:

### 1. Full-duplex (WebSocket `/ws/soniox`)
`tools.py` → `get_system_message()` — Python Soniox server tarafında kullanılır.

### 2. Half-duplex (REST `/api/chat`)
`server.mjs` line 112 — Node.js HTTP handler'ında **hardcoded**.

**⚠️ KRİTİK PİTFALL:** İki prompt da AYNI olmalı. Birini güncelleyip diğerini unutursan:
- Full-duplex → yeni prompt'la doğru kimlik
- Half-duplex (fallback veya `/index.html`) → eski prompt'la yanlış kimlik ("benim adım vanitas" gibi halüsinasyonlar)

**Güncelleme prosedürü:**
1. `tools.py` → `get_system_message()`'i düzenle
2. `server.mjs` → line 112'deki `system` mesajını aynı içerikle güncelle
3. Sunucuyu yeniden başlat
4. Telefondan test et (hem full-duplex hem half-duplex fallback'i test et)

**Varsayılan prompt (11 Tem 2026 — her iki kod yolunda):**
```
Sen Vanitas'sin - Edel'in yapay zeka yol arkadasi. Sicak, samimi,
biraz muzip konusursun. Edel'e 'canim' diye hitap edersin.
Cevaplarin KISA ve dogal olmali - maksimum 2-3 cumle.
Bilmedigini uydurma, 'bilmiyorum canim' de.
Sesli gorusmedesin, emoji kullanma. Turkce konus.
```

## Testing

```python
# WebSocket proxy test
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://127.0.0.1:3005/ws/soniox?language=tr&voice=Alina') as ws:
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        print(json.loads(msg))  # Should see session_start
asyncio.run(test())
```

## Known Issues

## Known Issues

- **Port visibility in containers**: `lsof` and `ss` may show ports as free even when they're actively listening. Use `/proc/net/tcp` directly: `cat /proc/net/tcp | grep "0100007F:0BBD.*0A"` for reliable container port checks.
- **EADDRINUSE on restart**: Node.js port may not release immediately after kill. `server.mjs` has built-in retry (3 attempts, 2s apart) in `startServer()`.
- **Soniox TTS API key**: Same key often works for both STT and TTS, but must be explicitly set as `SONIOX_API_KEY_TTS`
- **VAD warmup**: Silero VAD model download on first run (~30s), subsequent runs cached (~3s)
- **lsof visibility**: In Docker/container environments, `lsof` and `ss` may not show listening sockets even when they work (curl/WebSocket connections succeed)
- **Edge TTS fallback**: If Soniox TTS unavailable, the frontend falls back to `/api/tts` (Edge TTS via Edge-TTS CLI)
