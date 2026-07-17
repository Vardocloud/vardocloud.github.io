---
name: voice-agent-development
description: >-
  Browser-based voice AI agent development — audio capture, STT (Deepgram / faster-whisper / Soniox),
  VAD, full-duplex vs half-duplex architecture, barge-in, TTS pipeline patterns and pitfalls
  for Turkish voice assistants. Reference: Soniox Voice Bot Demo (Python FastAPI + Silero VAD).
trigger: >-
  Voice agent, sesli asistan, real-time conversation AI, sesli chatbot,
  browser microphone, WebSocket audio streaming, STT pipeline, TTS integration,
  faster-whisper, Deepgram Voice Agent, webrtcvad, VAD.
---

# Voice Agent Development

Browser-based voice AI agent architecture, STT/TTS pipeline patterns, and
full-duplex conversation design for Turkish voice assistants.

> **Referans mimari:** Soniox Voice Bot Demo (Python FastAPI + Silero VAD + Soniox TTS full-duplex)
> https://github.com/soniox/soniox_examples/tree/master/apps/soniox-voice-bot-demo
> Bu demo, aşağıdaki tüm özellikleri (full-duplex, barge-in, VAD, streaming TTS) içeren
> açık kaynak referans implementasyonudur. Kendi sistemini kurarken bu mimariyi temel al.

## Voice Agent Architecture: Half-Duplex vs Full-Duplex

### Half-Duplex (CURRENT — Vanitas v15)

```
[User konuşur] → Soniox STT → stopSoniox() 🔇 MİKROFON KAPANIR
    → LLM (HTTP streaming) → TTS (tek parça mp3) → audio.play()
    → TTS bitti → startSoniox() → yeni mikrofou açılır 🔓
```

**Sorunlar:**
- TTS oynarken kullanıcı araya giremez (konuşması duyulmaz)
- Her turda mikrofou kapat/aç gecikmesi
- `isProcessing` ve `isSpeaking` state'leri yönetilmezse ikinci konuşma kaybolur
- Arka plan sesleri birikince sistem "sapıtır" (ard arda cevap üretir)

**Kritik pitfall:** `finishTts()` içinde `isProcessing = false` sıfırlanmazsa
yeni Soniox `result` event'i `if (!isProcessing)` engeline takılır ve
kullanıcının ikinci konuşması LLM'e hiç gitmez. **Her dönüş noktasında state sıfırla.**

### Full-Duplex (HEDEF — Soniox Voice Bot Demo)

```
[User konuşur ··················]
    ↓ STT stream (Soniox WebSocket)
    [LLM stream ·················]
        ↓ TTS stream (Soniox tts-rt-v1, aynı anda)
        [Sana cevap ·············]
    ↑ User araya girer → VAD algılar → TTS kesilir → yeni döngü
```

**Gerekenler:**
1. **Barge-in** — VAD (Silero VAD) konuşma algılayınca TTS hemen kesilmeli
2. **Full-duplex TTS** — Soniox `tts-rt-v1` WebSocket üzerinden streaming (text girer, ses çıkar)
3. **Mikrofou hep açık** — Her turda kapatıp açma, stream'ler aynı anda aktif
4. **LLM streaming** — HTTP streaming ile yanıt parça parça gelir, TTS hedefe akar

### Mimari Karşılaştırması

| Özellik | Half-Duplex (mevcut) | Full-Duplex (hedef) |
|---------|---------------------|---------------------|
| Barge-in (araya girme) | ❌ | ✅ Silero VAD ile |
| Aynı anda dinleme+konuşma | ❌ | ✅ |
| TTS gecikmesi | Tam mp3 (1-2sn) | Streaming (ilk ses <300ms) |
| Arka plan ses dayanımı | Düşük (endpoint sensitivity) | Yüksek (VAD+VAD eşiği) |
| State yönetimi | Karmaşık (isProcessing/isSpeaking) | Basit (session bazlı) |
| Backend | Node.js Express | Python FastAPI + WebSocket |
| VAD | Yok (Soniox endpoint) | Silero VAD (altın standart) |

## Barge-In Pattern

Kullanıcı TTS oynarken konuşursa:

1. **VAD** (Silero VAD) ses seviyesi eşiğini aşan ses algılar
2. **TTS interrupt** — mevcut TTS stream'i iptal edilir (WebSocket kapatılır, AudioContext durdurulur)
3. **State reset** — `isSpeaking=false, isProcessing=false`
4. **STT açık kalır** — yeni konuşma transkribe edilmeye devam eder
5. **LLM streaming** — yeni metin LLM'e gider

```javascript
// Frontend'de barge-in (mevcut half-duplex'e eklenecek)
function bargeIn() {
  if (isSpeaking || isProcessing) {
    // TTS'i kes
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    // State'i sıfırla
    isSpeaking = false;
    isProcessing = false;
    // Mikrofou AÇIK tut (stopSoniox yapma!)
  }
}
```

## Background Noise Filtering

Soniox `endpoint_detection` çok hassas olduğunda arka plan sesleri (TV, başka konuşmalar)
da "konuşma bitti" sinyali olarak algılanır. Çözüm:

```javascript
// Confidence filter + minimum kelime
recording.on('result', (result) => {
  const tokens = result.tokens || [];
  const highConfTokens = tokens.filter(t => t.confidence >= 0.4);
  const text = highConfTokens.map(t => t.text).join('').trim();
  const wordCount = text.split(/\s+/).filter(w => w.length > 0).length;
  
  // Minimum 2 kelime yoksa atla (arka plan gürültüsü)
  if (!text || wordCount < 2) return;
  
  // İşleme al
  processWithLLM(text);
});
```

**Endpoint detection tuning:**
- `endpoint_sensitivity: -0.5` — negatif değer = daha az hassas (arka plan sesine dayanıklı)
- `max_endpoint_delay_ms: 1200` — 1.2sn sessizlik bekler, yanlış tetiklenme azalır
- `language_hints_strict: true` — sadece Türkçe tanı, diğer dilleri filtrele
- Pozitif sensitivity (0.3) = çok hassas, gürültülü ortamda sorun çıkarır

## Stream Lifecycle (Half-Duplex)

Her turda mikrofou temizlemek kritik:

```javascript
// DÖNGÜ: Konuş → LLM → TTS → Tekrar dinle
// 1. Soniox result event'i → processWithLLM(text)
// 2. processWithLLM: stopSoniox(); LLM; TTS.play();
// 3. TTS bitti: finishTts() → releaseMicrophone() → startSoniox()
// 4. startSoniox: initSoniox() → yeni Recording

function releaseMicrophone() {
  stopPcmCapture();
  if (vpStream) {
    vpStream.getTracks().forEach(t => t.stop());
    vpStream = null;
  }
}

function finishTts() {
  isSpeaking = false;
  isProcessing = false;  // ← KRİTİK: sıfırlanmazsa sonraki result engellenir
  releaseMicrophone();    // ← KRİTİK: eski stream kapatılmazsa yeni getUserMedia çakışır
  startSoniox();
}
```

**⚠️ Çift mikrofon:** `initSoniox()` içinde manuel `getUserMedia` + Soniox Recording'in
kendi `MicrophoneSource` = aynı anda iki mikrofou açma → browser çakışması.
Soniox Recording mikrofonu kendi yönetsin, manuel getUserMedia sadece voiceprint gibi
yardımcı işlemler için kullan (ve aralarda kapat).

## STT Strategy Decision

| Solution | Latency | Turkish Quality | Cost | Server Load |
|----------|---------|-----------------|------|-------------|
| Deepgram Nova-2 | ~200ms | Excellent | $200 free credit | 0 |
| faster-whisper-tiny | ~2s (ARM64) | Good | Free | ~40% CPU, 400MB |
| faster-whisper-base | ~3s (ARM64) | Better | Free | ~50% CPU, 500MB |
| faster-whisper-small | 30s+ (ARM64) | Best | Free | **UNUSABLE on ARM64** |
| Web Speech API | ~500ms | Good (Chrome Mobile) / Weak (Desktop) | Free | 0 |
| Edge TTS (API route) | ~1s | Excellent (EmelNeural) | Free | Low |
| Pollinations Whisper | N/A | N/A | Free | 500 errors |

**Rule:** On ARM64 (Oracle Cloud A1, Raspberry Pi), use `tiny` or `base`.
Always test: `WhisperModel("tiny", device="cpu", compute_type="auto")`.
See `references/faster-whisper-arm64-benchmark.md` for full speed test data.

## Architecture: Local STT Pipeline

```
Browser Mic → getUserMedia → AudioContext(16kHz) → ScriptProcessorNode(512)
  → Int16 PCM → WebSocket binary
  → Server: vad_buffer re-framing → webrtcvad(480-sample frames) → speech_buffer
  → WhisperModel.transcribe() → Hermes Proxy → ElevenLabs Bella TTS
  → mp3 binary → WebSocket → AudioContext playback
```

## Architecture: Vanilla JS SonioxClient (Standalone Node.js)

React/Next.js kullanmayan projeler için SonioxClient JS SDK. Browser'da çalışır,
UMD build olmadığı için **esbuild ile bundle** gerekir. VAD beklemesi kalkar,
Soniox endpoint detection ile değişir.

```
Browser (index.html)
  ├─ script src="soniox-bundle.js"          ← esbuild ile bundle
  ├─ GET /api/config → { sonioxKey }        ← Server BWS'den okur
  ├─ new SonioxClient({ api_key })          ← Client oluştur
  ├─ client.realtime.record({ model })      ← Recording başlat
  │  └─ .on('result') → metin
  ├─ POST /api/chat → Groq LLM             ← Metin → yanıt
  └─ POST /api/tts  → edge-tts CLI         ← Yanıt → ses
```

**⚠️ DOĞRU API (kritik):**
- **YANLIŞ:** `new SonioxClient({ apiKey: '...', onResult: ... })` — constructor callback almaz
- **YANLIŞ:** `client.start({ api_key, onResult })` — **böyle bir metod yok**
- **DOĞRU:** `new SonioxClient({ api_key })` → `client.realtime.record({ model: 'stt-rt-v5' })` → `.on('result', handler)`

```javascript
// DOĞRU KULLANIM:
const client = new SonioxClient({ api_key: SONIOX_KEY });
const recording = client.realtime.record({
  model: 'stt-rt-v5',
  language_hints: ['tr'],
  enable_endpoint_detection: true,
  max_endpoint_delay_ms: 500,
});
recording.on('result', (result) => {
  const text = result.tokens?.map(t => t.text).join('') || '';
  if (text.trim()) processWithLLM(text);
});
recording.on('error', (err) => console.error(err));
```

**Detaylı referans:** `references/soniox-vanilla-js.md` — tam implementasyon,
tüm event'ler, pitfall'lar, esbuild bundle adımları.

## Architecture: Soniox React SDK (Next.js — v13+)

Modern, low-code yaklaşım. Ses işleme tamamen browser'da Soniox SDK ile yapılır.
Sunucu sadece API key tutar ve LLM proxy'si olarak çalışır (~50 satır).

```
Next.js Server Component → VoiceAgent Client Component
  ├─ useRecording(STT)  → Soniox API → metin
  ├─ fetch(/api/chat)   → Groq/LLM → yanıt
  └─ useTts(TTS)        → Soniox API → ses → AudioContext.play()
```

**Avantajları:** PCM/WebSocket binary yönetimi yok, deadlock riski yok,
sunucu kodu ~50 satır (sadece LLM proxy'si + temporary key).

**Detaylı referans:** `references/soniox-react-sdk.md`

## Architecture: Next.js 16 Voice Agent (Server Component Pattern)**

Modern yaklaşım: API key'leri server'da tut, browser'a hiçbir secret gitmesin. Next.js 16'da `'use client'` component'lerini server component'ten direkt import edersen **JavaScript bundle'ı gönderilmez** — sayfa statik HTML olur, butonlar çalışmaz.

**Doğru yapı — üç katmanlı:**

```
page.tsx (server component)
  └─ process.env'dan API key'leri oku
  └─ ClientWrapper'a props olarak geç

ClientWrapper.tsx ('use client')
  └─ dynamic(() => import('./VoiceAgent'), { ssr: false })
  └─ server'dan gelen props'ları VoiceAgent'a ilet

VoiceAgent.tsx ('use client')
  └─ Web Speech API / Edge TTS / Groq LLM
  └─ API key'ler props olarak gelir
```

**Neden direkt import çalışmaz:**
Next.js 16 (Turbopack), server component'ten `'use client'` component'i direkt import edilince, client bundle'ı HTML'e `<script>` tag'i olarak eklemez. Butonlar görünür ama hiçbir `onClick` çalışmaz, `useEffect` tetiklenmez. Konsol tamamen boş kalır.

**Çözüm:** `dynamic()` import + client wrapper katmanı (TERCİH EDİLEN):

```tsx
// ClientWrapper.tsx — ZORUNLU ara katman
'use client';
import dynamic from 'next/dynamic';
const VoiceAgent = dynamic(() => import('./VoiceAgent'), { ssr: false });

interface Props {
  sttConfig: { api_key: string };
  ttsConfig: { api_key: string };
}

export default function ClientWrapper({ sttConfig, ttsConfig }: Props) {
  return <VoiceAgent sttConfig={sttConfig} ttsConfig={ttsConfig} />;
}
```

**Alternatif:** `dynamic()` cloudflared tunnel üzerinden asenkron chunk yüklemede takılı kalırsa (loading animasyonu sonsuza kadar döner, sayfa açılmaz), direkt import dene:

```tsx
// ClientWrapper.tsx — direkt import alternatifi
'use client';
import VoiceAgent from './VoiceAgent';  // direkt import, aynı bundle'a gömülür

export default function ClientWrapper({ sttConfig, ttsConfig }: Props) {
  return <VoiceAgent sttConfig={sttConfig} ttsConfig={ttsConfig} />;
}
```

**`dynamic()` vs direkt import kararı:**
- `dynamic()`: VoiceAgent ayrı chunk olarak yüklenir, sayfa daha hızlı açılır
- Direkt import: VoiceAgent ClientWrapper bundle'ına gömülür, chunk yükleme sorunu olmaz
- **Cloudflared tunnel'da direkt import daha güvenilirdir** — trycloudflare bazen async chunk'ları doğru serve edemez
- Her iki durumda da SSR kapalı olmalı

**Tuzak:** `dynamic()` ile `ssr: false` kullan. Aksi halde server'da `AudioContext`/`getUserMedia` hataları alırsın.

## Architecture: Browser-Native (Web Speech API + Edge TTS)

Soniox/Deepgram/WebSocket yerine sıfır bağımlılıklı, her browser'da çalışan yaklaşım.
Mobil browser'larda (Chrome Android, Firefox Android, Brave) en güvenilir seçenek.

```
Tarayıcı:
  ├─ SpeechRecognition (Web Speech API) → metin
  ├─ fetch(/api/chat) → Groq/LLM → yanıt
  └─ fetch(/api/tts) → Edge TTS (EmelNeural) → mp3 → Audio.play()
```

**Avantajları:**
- Hiçbir API key browser'a gitmez (server-side API route)
- WebSocket gerekmez (mobil operatörler WS portlarını engelleyebilir)
- Mikrofon izni direkt browser tarafından sorulur (güvenilir UX)
- Cloudflare tunnel üzerinden bile çalışır

### CRITICAL: Edge TTS Endpoint Değişikliği (2026-07-01)

**Eski endpoint öldü:** `https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge` — HTTP 400 döndürüyor ("Our services aren't available right now").

**Çözüm:** `edge-tts` Python CLI (v7.2.7) kullan:

```javascript
// Node.js server.mjs — execSync ile edge-tts CLI
const { execSync } = require('child_process');
const tmpFile = `/tmp/vanitas_tts_${Date.now()}.mp3`;
execSync(
  `edge-tts --text ${escapeShell(text)} --voice tr-TR-EmelNeural --write-media ${tmpFile}`,
  { timeout: 30000, stdio: 'pipe' }
);
const audioData = fs.readFileSync(tmpFile);
fs.unlinkSync(tmpFile);
```

**Notlar:**
- `edge-tts` Python paketi pip ile kurulu olmalı: `pip install edge-tts`
- CLI otomatik olarak Edge TTS'in güncel API'sini kullanır
- `escapeShell()` ile shell injection koruması şart:
  ```javascript
  function escapeShell(s) { return "'" + s.replace(/'/g, "'\\''") + "'"; }
  ```

### CRITICAL: Groq Model Adı Değişikliği (2026-07-01)

**Eski:** `llama-4-scout-17b-16e-instruct` → HTTP 404 "model_not_found"
**Yeni:** `meta-llama/llama-4-scout-17b-16e-instruct` (Preview kategorisinde)

Groq API'sinde model adlarına `meta-llama/` prefix'i eklenmiş. Tüm model referanslarını güncelle.

### CRITICAL: Cloudflared PATH Sorunu

Background process'lerde (Node.js server, cloudflared) PATH, Hermes bin dizinini içermez. `cloudflared` komutu "command not found" verir.

**Çözüm:** Her zaman tam yol kullan:
```bash
/home/ubuntu/.hermes/bin/cloudflared tunnel --url http://localhost:3005
```

### Pitfall: Port 3000 EADDRINUSE

Port 3000'de sürekli LISTEN durumunda gizli socket kalıyor (TIME_WAIT değil, gerçek LISTEN). `pkill -f node` bile temizlemiyor.

**Çözüm:** Alternatif port kullan (3005 veya 3001):
- Next.js varsayılan: 3000 → EADDRINUSE riski
- Node.js standalone: 3005 → temiz

## Architecture: Standalone Node.js Server (Next.js Bypass)

Next.js 16 routing sorunları (src/app/ vs app/, hydration, cloudflared chunk yükleme) tıkandığında kullanılacak终极 çözüm. Tek Node.js sunucusu hem statik dosyaları (`public/`) servis eder hem de API'leri çalıştırır.

```mermaid
flowchart LR
  A[Phone Browser] --> B[Cloudflare Tunnel]
  B --> C[Node.js Server :3005]
  C --> D[public/index.html]
  C --> E[/api/chat → Groq]
  C --> F[/api/tts → edge-tts CLI]
```

**Avantajları:**
- **Tek port, tek origin** — CORS sorunu yok, tunnel tek bir port'a
- **Next.js yok** — hydration hatası, chunk yükleme, derleme sorunu yok
- **Sade düz HTTP** — her ortamda çalışır (WSL, Docker, VPS)
- **Edge TTS CLI** — güncel API'yi otomatik kullanır (endpoint değişse bile çalışır)

**server.mjs minimal template (60 satır):**

```javascript
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const PUBLIC = path.join(import.meta.dirname, 'public');
const PORT = 3005;

// Static file serving
function serveStatic(req, res) {
  let urlPath = new URL(req.url, 'http://localhost').pathname;
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(PUBLIC, urlPath);
  if (!filePath.startsWith(PUBLIC)) return sendJSON(res, 403, { error: 'Forbidden' });
  if (!fs.existsSync(filePath)) return sendJSON(res, 404, { error: 'Not Found' });
  const content = fs.readFileSync(filePath);
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
  res.end(content);
}

// API: Chat (Groq LLM streaming proxy)
async function handleChat(req, res) {
  // 1. Parse body → message + conversation
  // 2. Get Groq key from BWS
  // 3. POST to https://api.groq.com/openai/v1/chat/completions
  //    model: 'meta-llama/llama-4-scout-17b-16e-instruct' ← NOT: llama-4-scout-17b-16e-instruct
  //    stream: true
  // 4. Pipe response.body directly to res (text/event-stream)
}

// API: TTS (Edge TTS CLI)
async function handleTTS(req, res) {
  // 1. Parse body → { text }
  // 2. edge-tts --text '...' --voice tr-TR-EmelNeural --write-media /tmp/tts_xxx.mp3
  // 3. Read file, send as audio/mpeg, delete tmp file
  // See "CRITICAL: Edge TTS Endpoint Değişikliği" above
}

// Router
async function onRequest(req, res) {
  if (req.method === 'POST' && pathname === '/api/chat') return handleChat(req, res);
  if (req.method === 'POST' && pathname === '/api/tts') return handleTTS(req, res);
  if (req.method === 'GET') return serveStatic(req, res);
}

http.createServer(onRequest).listen(PORT, '0.0.0.0');
```

**Tam implementasyon:** `~/vanitas-web/server.mjs` (6970 bytes, production'da çalışıyor)

**Çalıştırma:**
```bash
cd ~/vanitas-web
node server.mjs &  # Port 3005
/home/ubuntu/.hermes/bin/cloudflared tunnel --url http://localhost:3005
```

**Tam yol ile cloudflared çağırmayı unutma!** PATH'te olmadığı için `cloudflared` tek başına "command not found" verir.

**Notlar:**
- Next.js API route'ları (`src/app/api/`) çalışıyorsa kullanmaya gerek yok
- Sadece Next.js routing/serving sorunlarında başvur
- edge-tts Python paketi sistemde kurulu olmalı: `pip install edge-tts`
- Groq model adı `meta-llama/llama-4-scout-17b-16e-instruct` (prefix unutma!)

**Mobil Web Speech API Notları:**
- Chrome Android'de Türkçe STT kalitesi **iyidir** (eski versiyonlardaki gibi zayıf değil)
- `continuous: true` + `interimResults: true` ile doğal konuşma akışı
- `onerror` callback'inde `event.error` değerini kontrol et (genellikle `no-speech` veya `aborted`)
- Echo loop guard'ları (aşağıda Web Speech API section'ında) TTS çalarken recognition'ı durdurur
- Firefox Android'de SpeechRecognition desteği sınırlı olabilir → kullanıcıya uyarı göster

See `references/cloudflared-tunnel-setup.md` for relay pattern.
Browser → Sunucu WS → Deepgram WS → LLM → TTS → Browser.


## Ses Formatları — EN KRİTİK KONU

### Tarayıcıda PCM Yakalama (Local STT)

**ScriptProcessorNode (tek güvenilir PCM kaynağı):**

```javascript
const captureCtx = new AudioContext({sampleRate: 16000});  // 16kHz for VAD
await captureCtx.resume();  // CRITICAL: mobile/Chrome starts suspended
const source = captureCtx.createMediaStreamSource(stream);
const processor = captureCtx.createScriptProcessor(512, 1, 1);  // 512=power of 2

// MUST connect to destination (via silent GainNode) or onaudioprocess won't fire
const silence = captureCtx.createGain();
silence.gain.value = 0;
source.connect(processor);
processor.connect(silence);
silence.connect(captureCtx.destination);

processor.onaudioprocess = (e) => {
  const input = e.inputBuffer.getChannelData(0);
  const int16 = new Int16Array(512);
  for (let i = 0; i < 512; i++) {
    int16[i] = Math.max(-32768, Math.min(32767, (input[i] || 0) * 32767));
  }
  ws.send(int16.buffer);
};
```

**CRITICAL: ScriptProcessorNode without output connection → ZERO callbacks.**
Use GainNode(0)→destination to satisfy audio graph without feedback.

**CRITICAL: `createScriptProcessor(bufferSize)` — bufferSize MUST be power of 2**
(256, 512, 1024, 2048, 4096, 8192, 16384). 480 is NOT valid.

**CRITICAL: `AudioContext.resume()` — always await before creating nodes.**
Even from button click handler, some browsers start suspended.

### Tarayıcıda Ses Yakalama (Deepgram Relay)

Same ScriptProcessorNode approach, but use 24000 sample rate for Deepgram.

### Deepgram'ın beklediği formatlar
- `linear16`: Ham PCM, 16-bit signed integer, little-endian
- `opus`: Ham Opus frame'leri (WebM konteyner DEĞİL)
- `flac`, `mulaw`, `pcm`

### Tarayıcıda ses üretimi

**ScriptProcessorNode (önerilen, deprecated ama çalışıyor):**
```javascript
var ctx = new AudioContext({sampleRate: 24000});
var src = ctx.createMediaStreamSource(stream);
var proc = ctx.createScriptProcessor(4096, 1, 1);
src.connect(proc);
proc.onaudioprocess = function(e) {
  var input = e.inputBuffer.getChannelData(0);
  var pcm = new Int16Array(input.length);
  for (var i = 0; i < input.length; i++) {
    var s = Math.max(-1, Math.min(1, input[i]));
    pcm[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }
  ws.send(pcm.buffer);
};
```

**Tuzak:** `proc.connect(ctx.destination)` eklenmezse bazı tarayıcılarda onaudioprocess tetiklenmez.

**MediaRecorder (kullanmayın):**
WebM/Opus konteyner üretir, Deepgram ham Opus frame bekler → uyuşmazlık.
`Failed to parse audio` veya `encoding mismatch` hatası alınır.

### AudioContext `resume()` — MOBİL KRİTİK

Mobil tarayıcılarda AudioContext "suspended" durumda başlar:
```javascript
ctx.resume().then(function() {
  // Şimdi ScriptProcessorNode oluştur
  proc = ctx.createScriptProcessor(4096, 1, 1);
  // ...
});
```
`resume()` beklenmeden oluşturulan node'lar sessiz kalır.

## WebSocket Binary Data — FastAPI/Starlette

`await ws.receive()` returns binary data as `{"type": "websocket.receive", "bytes": b"..."}` dict, NOT raw bytes. Handle both:

```python
raw = await ws.receive()
if isinstance(raw, dict):
    if raw.get("text"):
        msg = json.loads(raw["text"])
        if msg.get("type") == "stop":
            break
        continue
    if raw.get("bytes"):
        raw = raw["bytes"]  # extract binary from dict
    else:
        continue
if not isinstance(raw, bytes):
    continue
# Now 'raw' is bytes — process PCM
```

## VAD (webrtcvad) — Local STT

### Installation Fix
webrtcvad 2.0.10 imports `pkg_resources` (removed in setuptools 67+).
Patch `webrtcvad.py`: remove `import pkg_resources`, replace version line with `__version__ = "2.0.10"`.

### Buffer Size Mismatch
webrtcvad expects 10/20/30ms frames (160/320/480 samples at 16kHz).
ScriptProcessorNode forces power-of-2 buffers (512 samples).

**Solution:** Use 512-sample ScriptProcessor. Server accumulates in `vad_buffer`,
extracts 480-sample VAD frames:

```python
vad_buffer = bytearray()
VAD_FRAME = 480 * 2  # 960 bytes = 30ms at 16kHz

# For each WebSocket message:
vad_buffer.extend(raw)
while len(vad_buffer) >= VAD_FRAME:
    frame = vad_buffer[:VAD_FRAME]
    vad_buffer = vad_buffer[VAD_FRAME:]
    is_voice = vad.is_speech(bytes(frame), 16000)
    # ... speech/silence state machine
```

### VAD State Machine
- Mode 3 (most aggressive). `SILENCE_TIMEOUT = 1.0` seconds.
- `is_speaking` flag tracks state.
- On silence ≥ SILENCE_TIMEOUT → `flush_speech()`.
- **Always flush on WebSocket disconnect** if `is_speaking` and buffer has data.
- `MAX_UTTERANCE = 15s` safety cap.

### ARM64 Performance
Always benchmark model before deploying:
```python
model = WhisperModel("tiny", device="cpu", compute_type="auto")
t0 = time.time()
segments, _ = model.transcribe(audio, language="tr")
print(f"Ratio: {(time.time()-t0)/duration:.1f}x")  # >1.5x = too slow
```

## TTS: ElevenLabs Bella

Best Turkish voice via Pollinations:
```
POST https://gen.pollinations.ai/v1/audio/speech
{model: "elevenlabs", voice: "bella", input: text, response_format: "mp3", speed: 1.0}
```
Fallback: `qwen-tts` with same endpoint.
Bella mp3 → browser `decodeAudioData` (AudioContext) for playback.

## Deepgram Voice Agent Settings (BYO LLM)

```json
{
  "type": "Settings",
  "audio": {
    "input": {"encoding": "linear16", "sample_rate": 24000},
    "output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"}
  },
  "agent": {
    "listen": {"provider": {"type": "deepgram", "model": "nova-3"}},
    "think": {
      "provider": {"type": "open_ai", "model": "gpt-4o"},
      "endpoint": {
        "url": "https://api.pollinations.ai/v1/chat/completions",
        "headers": {
          "Authorization": "Bearer {API_KEY}",
          "Content-Type": "application/json"
        }
      },
      "prompt": "Sen Vanitas'sın..."
    },
    "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}}
  }
}
```

### LLM endpoint uyumluluğu
- DeepSeek: `https://api.deepseek.com/v1/chat/completions` — OpenAI uyumlu
- Pollinations: `https://gen.pollinations.ai/v1/chat/completions` — OpenAI uyumlu
- Her ikisi de `think.provider.type: "open_ai"` ile çalışır
- `think.provider.model` alanı endpoint'te geçerli bir model olmalı

### TTS Sesleri
- Deepgram Aura-2: SADECE İngilizce (athena-en, thalia-en, vs.)
- ElevenLabs: Türkçe var ama Voice Agent üzerinden `voice_id` zorunlu, API key gerekebilir
- Şimdilik Aura-2 İngilizce sesle başla, sonra ElevenLabs'a geç

## Tarayıcıda Ses Oynatma

Binary WebSocket mesajları `Blob` olarak gelir, WAV formatında:
```javascript
ws.onmessage = function(e) {
  if (e.data instanceof Blob) {
    e.data.arrayBuffer().then(function(buf) {
      var blob = new Blob([buf], {type: 'audio/wav'});
      var audio = new Audio(URL.createObjectURL(blob));
      audio.play();
    });
  }
};
```

## Cloudflared ile WebSocket

- Cloudflared ücretsiz tünelleri WebSocket destekler
- **Idle timeout:** ~8 saniye ses gelmezse kapanır
- Sunucu relay yaklaşımında browser ↔ sunucu arası sürekli veri akışı olduğu için timeout olmaz
- Her yeniden başlatmada tünel URL'si değişir

## Web Speech API Echo Loop (tarayıcı STT kullanılıyorsa)

Chrome Web Speech API `continuous: true` → TTS sesini yakalar → STT metne çevirir → tekrar gönderir → sonsuz döngü.

**Mobil Öncelik:** Web Speech API, mobil Chrome/Android'de Türkçe kalitesi olarak **iyi** seviyededir.
Desktop Chrome'da daha zayıf olabilir. Mobilde en güvenilir STT seçeneğidir çünkü:
- WebSocket engeli yok (mobil operatörler WS portlarını kapatabilir)
- API key gerekmez
- Mikrofon izni direkt browser tarafından yönetilir
- Cloudflare tunnel üzerinden sorunsuz çalışır

**Firefox uyarısı:** Firefox Android'de Web Speech API desteği Chrome kadar olgun değil.
`SpeechRecognition` constructor'ı mevcut olmayabilir → kullanıcıya "Tarayıcınız ses tanımayı desteklemiyor" uyarısı göster.

**Five-layer defense:**
1. `recognitionPaused` flag — ignore `onresult` during TTS
2. `recognition.abort()` — synchronous stop (vs async `stop()`)
3. `onend` respects `recognitionPaused` — no auto-restart
4. `no-speech` respects `recognitionPaused`
5. Multi-layer echo guard: substring, prefix, word overlap >50%

**CRITICAL:** Place ALL guards BEFORE `addMessage()` (DOM change). Otherwise duplicate messages appear on screen even if utterance is blocked.

**Recommendation:** For mobile browsers, Web Speech API is the most reliable STT option. For desktop/server-side, prefer server-side STT (faster-whisper or Deepgram) for better Turkish quality.

## Next.js 16 Hydration Debugging

**Belirti:** Sayfa açılır, Vanitas başlığı ve butonlar görünür, ama hiçbir `onClick` çalışmaz. Konsol tamamen boştur (hata mesajı bile yok). `useEffect` tetiklenmez, `setJsReady(true)` olmaz.

**Olası nedenler (sıralı kontrol):**

1. **Server component → client component direkt import** (en yaygın)
   - **Belirti:** `page.tsx` server component, `VoiceAgent.tsx` direkt import edilmiş
   - **Sebep:** Next.js 16 (Turbopack) client bundle HTML'e `<script>` tag'i eklemez
   - **Çözüm:** Ara katman (`ClientWrapper.tsx`) ile `dynamic()` import ekle

2. **`dynamic()` + cloudflared → sonsuz loading**
   - **Belirti:** Sayfa loading animasyonunda takılır, `dynamic()` import chunk'ı yüklenemez
   - **Sebep:** Cloudflared trycloudflare async chunk'ları serve edemez
   - **Çözüm:** `dynamic()` yerine direkt import kullan (ClientWrapper'ta)
   - **Alternatif:** Production build (`next start`) dene — HMR WebSocket yok, daha kararlı

3. **Direct `'use client'` page.tsx → hydration yok**
   - **Belirti:** `page.tsx`'in ilk satırı `'use client'`, tüm kod tek dosyada. Ama React hydrate olmaz.
   - **Sebep:** Next.js 16'da `'use client'` directive'i tek başına yeterli değil; client bundle'ı oluşsa bile hydration başlamayabilir
   - **Çözüm:** Yine üç katmanlı yapıya dön (server page → client wrapper → VoiceAgent)
   - **Not:** Bu sorun `layout.tsx` içeriğinden bağımsızdır (sade layout da aynı sonucu verir)

4. **Cloudflared tunnel + POST istekleri bloke**
   - **Belirti:** `/api/tmp-key` gibi POST endpoint'leri curl'de çalışır, browser'da sonsuz pending
   - **Sebep:** Cloudflared trycloudflare POST isteklerini doğru proxy'lemez
   - **Çözüm:** API key'leri server component'te oku, client'a props olarak geç (fetch gerekmez)

5. **Mobil browser'da event handler çalışmıyor**
   - **Belirti:** Desktop'ta çalışır, telefonda butona basınca hiçbir şey olmaz
   - **Sebep:** Brave/Firefox Android `onClick`'i tetiklemez
   - **Çözüm:** `onTouchStart` + `e.preventDefault()` + `touch-action: manipulation` + `-webkit-tap-highlight-color: transparent`

**Acil çözüm — Next.js routing/serving tıkandığında (2 seçenek):**

**Seçenek A — Python HTTP server + API backend (basit):**
1. Tüm kodu tek bir `index.html` + `<script>` içinde yaz
2. `public/` dizinine koy
3. `python3 -m http.server 9000` ile serve et
4. API route'ları (`/api/chat`, `/api/tts`) için Next.js production build ayrı portta çalıştır
5. Cloudflared bu statik dosyayı sorunsuz proxy'ler — chunk yok, WebSocket yok
6. **⚠️ DEZAVANTAJ:** Farklı portlar → farklı origin → API çağrıları bloke

**Seçenek B — Standalone Node.js server (ÖNERİLEN):**
1. `server.mjs` yaz — hem `public/` statik dosyaları hem de API'leri tek portta serve eder
2. `node server.mjs` ile çalıştır
3. Cloudflared tek port'a tunnel açar
4. **✅ AVANTAJ:** Tek origin, CORS yok, API'ler otomatik çalışır
5. Detaylar: yukarıdaki "Architecture: Standalone Node.js Server" bölümü

## Hata Ayıklama Kontrol Listesi

### Local STT Pipeline
1. **PCM geliyor mu?** → Sunucu log: "İlk PCM verisi geldi!" yoksa ScriptProcessor çıkışa bağlı değil veya AudioContext suspended
2. **VAD çalışıyor mu?** → `vad_frame_count` > 0, `speech_frame_count` > 0
3. **Sessizlik flush tetikleniyor mu?** → "Sessizlik X.Xs → flush" logu
4. **Transkripsiyon?** → Whisper çıktısı boşsa ses seviyesi çok düşük veya model çok yavaş
5. **WebSocket binary?** → `raw.get("bytes")` ile dict'ten çıkar, direkt bytes değil
6. **createScriptProcessor(480) hatası?** → 480 power-of-2 değil, 512 kullan

### Deepgram Pipeline
1. **Welcome geliyor mu?** → WebSocket bağlantısı OK
2. **SettingsApplied geliyor mu?** → Ayarlar geçerli
3. **"We did not receive audio"** → Ses formatı yanlış
4. **"Failed to think"** → LLM endpoint/api key/model hatası
5. **Ses geliyor ama çalmıyor** → Binary mesaj handle edilmiyor
6. **Tarayıcı hemen kopuyor** → AudioContext suspended, proc.connect yok

## Pitfalls

- **Half-duplex'ta `finishTts()` içinde `isProcessing = false` sıfırlanmazsa** ikinci Soniox result event'i engellenir, kullanıcının konuşması LLM'e gitmez. Her state dönüş noktasında (`finishTts`, `finishTurn`, `bargeIn`) tüm flag'leri sıfırla.
- **Mikrofon stream'i temizlenmezse** yeni `getUserMedia` çağrısı başarısız olur. Her tur sonunda `releaseMicrophone()` ile tüm track'leri durdur.
- **Soniox Recording kendi mikrofonunu açar** + manuel `getUserMedia` = çift mikrofon çakışması. Ya birini kullan ya diğerini, asla ikisini birden açma.
- **Endpoint sensitivity pozitif değerleri** (0.3 gibi) gürültülü ortamda çok hassas davranır, arka plandaki her sesi konuşma sanar. Negatif değer (-0.5) kullan.
- **Confidence filtresiz transkripsiyon** arka plan gürültüsünü de metne çevirir. `tokens.filter(t => t.confidence >= 0.4)` ve minimum 2 kelime kontrolü şart.
- **SonioxClient constructor'ı `api_key` (underscore) bekler.** `apiKey` (camelCase) "Either config or api_key must be provided" hatası verir.

- **SonioxClient constructor'ı `api_key` (underscore) bekler.** `apiKey` (camelCase) "Either config or api_key must be provided" hatası verir.
- **SonioxClient constructor'a model/callbacks koyma.** Constructor sadece `api_key` veya `config` alır. Model ve event'ler `client.realtime.record({ model })` + `.on('result', handler)` ile kullanılır.
- **Soniox SDK UMD build içermez.** CDN'den `<script>` ile yüklenemez. esbuild ile bundle gerekir: `npx esbuild wrapper.js --bundle --outfile=public/soniox-bundle.js`.
- **Soniox config async function ile çalışmaz.** "config changed after mount" hatası alınır. Config'i mount ÖNCESİNDE hazır et (server component pattern).
- **`tts.isSpeaking` butonu kitler.** Voice agent'ın en sinsi hatası. `disabled={tts.isSpeaking}` yaparsan kullanıcı butona hiç basamaz.
- **Cloudflared trycloudflare POST isteklerini bloke eder.** Browser'dan `/api/xxx` POST fetch'i sonsuza kadar pending kalır (Promise ne resolve ne reject olur). Curl çalışır, browser çalışmaz. Çözüm: API key'leri server'da oku, client'a props olarak geç (server component pattern). Veya production build kullan (`next start`).
- **`next dev` HMR WebSocket cloudflared'da sorun çıkarır.** "Unauthorized" hataları alınır, tunnel zamanla bozulur. Production build alıp `next start -p 3000` ile çalıştır — HMR yok, daha kararlı.
- **Mobil browser'da `onClick` tek başına yetmez.** Brave/Firefox Android'de `onClick` hiç tetiklenmeyebilir. Her butona `onTouchStart` + `touch-action: manipulation` + `-webkit-tap-highlight-color: transparent` ekle.
- **ScriptProcessorNode çıkışa bağlı değilse onaudioprocess ÇALIŞMAZ.** GainNode(0)→destination zorunlu.
- **AudioContext `resume()` beklenmezse sessiz kalır.** Mobil/Chrome suspended başlatır.
- **createScriptProcessor bufferSize power-of-2 olmalı.** 480 = GEÇERSİZ, 512 kullan.
- **FastAPI WebSocket binary veriyi dict içinde `{"bytes": ...}` döndürür.** Direkt bytes bekleme.
- **webrtcvad frame'leri ScriptProcessor buffer'ıyla eşleşmez.** Sunucuda re-frame yap.
- MediaRecorder WebM/Opus → Deepgram raw Opus bekler → UYUŞMAZ
- Deepgram Aura-2'de Türkçe ses yok (sadece İngilizce) — Bella kullan
- **faster-whisper-small ARM64'te 10x gerçek zamanlı — kullanılamaz.** tiny veya base seç.
- DeepSeek free tier bakiye sıfırlanabiliyor → Pollinations fallback
- Cloudflared tünel URL'si her yeniden başlatmada değişir
