# Soniox Vanilla JS — Standalone Server Pattern (v15)

**Tarih:** 2026-07-05 (güncellendi)
**Proje:** vanitas-web (Voice Agent v15)
**Gerektiren:** Soniox API key (BWS'de `SONIOX_API_KEY`)

React/Next.js kullanmadan, düz HTML + JavaScript frontend'de SonioxClient JS SDK ile gerçek zamanlı STT entegrasyonu. VAD beklemesini minimize eder.

> **⚠️ ÖNEMLİ:** Bu skill ESKİ hayali API'yi (`client.start()` + `onResult` callback) anlatıyordu. 
> **Gerçek API:** `new SonioxClient({ api_key })` → `client.realtime.record({ model })` → `.on('result', handler)`.
> Aşağıdaki döküman GÜNCEL API'yi anlatır.

## Ne Zaman Kullanılır

- Proje **Next.js/React kullanmıyor** (düz HTML + Node.js server)
- **Mobil browser** hedef (SonioxClient WebSocket doğrudan Soniox'a bağlanır)
- **Düşük gecikme** hedefi (konuşurken anında transkripsiyon)

## Mimari

```
Browser (index.html)
  ├─ GET /api/config → { sonioxKey }       ← Server BWS'den okur
  ├─ SonioxClient → Soniox WebSocket API   ← Gerçek zamanlı STT
  ├─ POST /api/chat → Groq LLM             ← Metin → yanıt
  └─ POST /api/tts  → edge-tts CLI         ← Yanıt → ses
```

## DOĞRU API Kullanımı

### 1. Browser Bundle (UMD yok — esbuild ile)

SonioxClient JS SDK **UMD build içermez** (`dist/`'te sadece `.mjs` ve `.cjs` var). 
CDN'den `<script>` ile yüklenemez. esbuild ile bundle oluştur:

```bash
# Browser bundle oluştur
cd ~/vanitas-web
npx esbuild soniox-wrapper.js --bundle --outfile=public/soniox-bundle.js
```

Wrapper dosyası (`soniox-wrapper.js`):
```javascript
// Soniox SDK wrapper — esbuild ile browser bundle'ı için
import { SonioxClient } from '@soniox/client';
window.SonioxClient = SonioxClient;
```

HTML'de:
```html
<script src="soniox-bundle.js"></script>
```

### 2. Client Oluşturma

```javascript
// DOĞRU: constructor sadece api_key veya config alır
const SONIOX_KEY = await (await fetch('/api/config')).json().then(d => d.sonioxKey);
const client = new SonioxClient({ api_key: SONIOX_KEY });
```

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `api_key` | string | api_key veya config | API anahtarı |
| `config` | object/function | api_key veya config | Async config resolver |
| `ws_base_url` | string | hayır | Custom WebSocket URL |

### 3. Recording Başlatma

```javascript
// DOĞRU: client.realtime.record() ile
const recording = client.realtime.record({
  model: 'stt-rt-v5',           // ZORUNLU
  language_hints: ['tr'],        // Dil ipuçları
  enable_endpoint_detection: true, // Otomatik susma algılama
  max_endpoint_delay_ms: 500,    // Max bekleme (500-3000ms)
  endpoint_sensitivity: 0.3,     // Duyarlılık (-1.0 ile 1.0 arası)
});
```

## SttSessionConfig parametreleri:

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|-----------|----------|
| `model` | string | — | STT model (örn. `stt-rt-v5`) |
| `audio_format` | string | `'auto'` | `'auto'`, PCM formatları |
| `sample_rate` | number | — | PCM için örnekleme hızı |
| `num_channels` | number | — | Kanal sayısı |
| `language_hints` | string[] | — | Dil kodları (ISO) |
| `enable_endpoint_detection` | boolean | false | Susma algılama |
| `max_endpoint_delay_ms` | number | 2000 | Max endpoint gecikmesi |
| `endpoint_sensitivity` | number | 0.0 | -1.0 (geç/az hassas) ile 1.0 (erken/çok hassas) |
| `language_hints_strict` | boolean | false | Sadece belirtilen dilleri tanı |

### Endpoint Detection Tuning (Gürültülü Ortam)

```javascript
// SESSİZ ORTAM — hızlı tepki
{
  enable_endpoint_detection: true,
  max_endpoint_delay_ms: 500,
  endpoint_sensitivity: 0.3,    // hassas, çabuk sonlandırır
}

// GÜRÜLTÜLÜ ORTAM — arka plan seslerine dayanıklı
{
  enable_endpoint_detection: true,
  max_endpoint_delay_ms: 1200,  // daha uzun bekle
  endpoint_sensitivity: -0.5,   // negatif = az hassas
  language_hints_strict: true,  // sadece Türkçe
}
```

### Background Noise Filtering

Arka planda TV, başka konuşmalar, müzik varsa Soniox bunları da transkribe eder.
Her result'ta confidence filtresi + minimum kelime kontrolü yap:

```javascript
recording.on('result', (result) => {
  const tokens = result.tokens || [];
  // Düşük güvenli token'ları filtrele (arka plan sesi)
  const highConfTokens = tokens.filter(t => t.confidence >= 0.4);
  const text = highConfTokens.map(t => t.text).join('').trim();
  const wordCount = text.split(/\s+/).filter(w => w.length > 0).length;
  
  // Minimum 2 kelime yoksa atla
  if (!text || wordCount < 2) return;
  
  // İşleme al
  processWithLLM(text);
});
```

### Stream Lifecycle (Half-Duplex)

Soniox Recording kendi mikrofonunu açar (`MicrophoneSource`). Manuel `getUserMedia`
açma — çift mikrofon browser'da çakışmaya yol açar:

```javascript
// YANLIŞ — çift mikrofon
async function initSoniox() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });  // ❌ 1. mikrofon
  vpStream = stream;
  const client = new SonioxClient({ api_key });
  const recording = client.realtime.record({ model: 'stt-rt-v5' });  // ❌ 2. mikrofon (internal)
}

// DOĞRU — Soniox Recording mikrofonu yönetsin
async function initSoniox() {
  const client = new SonioxClient({ api_key });
  const recording = client.realtime.record({ model: 'stt-rt-v5' });  // ✅ tek mikrofon
}

// TTS sonrası temizlik (half-duplex):
function finishTts() {
  isSpeaking = false;
  isProcessing = false;    // ← KRİTİK: sıfırla!
  stopPcmCapture();
  // Varsa manuel stream'i kapat
  if (vpStream) {
    vpStream.getTracks().forEach(t => t.stop());
    vpStream = null;
  }
  startSoniox();  // Yeni Recording başlat
}
```

### 4. Event'leri Dinleme

```javascript
// Final sonuç (konuşma bittiğinde)
recording.on('result', (result) => {
  const text = result.tokens?.map(t => t.text).join('') || '';
  if (text.trim()) {
    // Metni LLM'e gönder
    processWithLLM(text);
  }
});

// Anlık token
recording.on('token', (token) => {
  // token.text, token.is_final, token.confidence
  if (token.text) {
    showInterim(token.text);
  }
});

// Endpoint (konuşma bitti sinyali)
recording.on('endpoint', () => {
  // Soniox susma algıladı — result event'i yakında gelir
});

// Hata
recording.on('error', (err) => {
  console.error('Soniox error:', err);
});

// Bağlantı kuruldu
recording.on('connected', () => {
  // WebSocket hazır, konuşmaya başlayabilir
});

// Oturum bitti
recording.on('finished', () => {
  // Temizlik
});
```

**Tüm event'ler:**

| Event | Parametre | Ne Zaman |
|-------|-----------|----------|
| `result` | `RealtimeResult` | Segment tamamlandı |
| `token` | `RealtimeToken` | Her token geldiğinde |
| `error` | `Error` | Hata oluştu |
| `endpoint` | `void` | Susma algılandı |
| `finalized` | `void` | Finalizasyon tamam |
| `finished` | `void` | Kayıt bitti |
| `connected` | `void` | WebSocket bağlandı |
| `state_change` | `{old_state, new_state, reason}` | Durum değişti |
| `reconnecting` | `ReconnectingEvent` | Yeniden bağlanıyor |
| `reconnected` | `{attempt}` | Yeniden bağlandı |
| `session_restart` | `{reset_transcript}` | Yeni STT oturumu |

### 5. Durdurma ve Temizlik

```javascript
// Recording'i durdur
await recording.stop();

// Client'ı temizle
client = null;
```

### 6. Tam Çalışan Örnek

```javascript
let client = null;
let recording = null;
let autoRestart = false;

async function startRecording() {
  const SONIOX_KEY = await (await fetch('/api/config')).json().then(d => d.sonioxKey);
  client = new SonioxClient({ api_key: SONIOX_KEY });
  
  recording = client.realtime.record({
    model: 'stt-rt-v5',
    language_hints: ['tr'],
    enable_endpoint_detection: true,
    max_endpoint_delay_ms: 500,
    endpoint_sensitivity: 0.3,
  });
  
  recording.on('result', (result) => {
    const text = result.tokens.map(t => t.text).join('');
    if (text.trim() && !isProcessing) {
      sendToLLM(text);
    }
  });
  
  recording.on('error', (err) => {
    console.error(err);
    if (autoRestart) setTimeout(startRecording, 2000);
  });
  
  recording.on('connected', () => {
    autoRestart = true;
    console.log('🎤 Dinliyorum...');
  });
}

function stopRecording() {
  autoRestart = false;
  if (recording) {
    recording.stop();
    recording = null;
  }
  client = null;
}
```

## Server Tarafı — Key Servis Etme

```javascript
// server.mjs — BWS'den key oku, browser'a servis et
if (req.method === 'GET' && url.pathname === '/api/config') {
  const SONIOX_KEY = await bwsSecrets.get('SONIOX_API_KEY');
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ sonioxKey: SONIOX_KEY }));
  return;
}
```

## Pitfall'lar

### 1. ❌ `apiKey` (camelCase) ÇALIŞMAZ

```javascript
// YANLIŞ — "Either config or api_key must be provided" hatası
new SonioxClient({ apiKey: '...' });

// DOĞRU
new SonioxClient({ api_key: '...' });
```

### 2. ❌ Constructor'a model/callbacks koyma

```javascript
// YANLIŞ — constructor sadece api_key/config alır
new SonioxClient({ api_key: '...', model: 'stt-rt-v5', onResult: ... });

// DOĞRU — model/callbacks recording'e gider
const client = new SonioxClient({ api_key: '...' });
const recording = client.realtime.record({ model: 'stt-rt-v5' });
recording.on('result', handler);
```

### 3. ❌ `client.start()` diye bir metod yok

```javascript
// YANLIŞ — hayali API
client.start({ api_key: '...', onResult: ... });

// DOĞRU
client.realtime.record({ model: 'stt-rt-v5' });
```

### 4. UMD build yok — CDN'den script ile yüklenemez

```javascript
// YANLIŞ — 404/parse hatası
<script src="https://unpkg.com/@soniox/client@latest/dist/index.umd.js"></script>

// DOĞRU — esbuild ile bundle oluştur
npx esbuild wrapper.js --bundle --outfile=public/soniox-bundle.js
```

### 5. Recording.stop() await edilebilir (Promise döndürür)

```javascript
await recording.stop(); // DOĞRU
```

### 6. Key güvenliği

- `/api/config`'ten dönen key browser'da görünür — bu amaçlıdır
- Key yalnızca Soniox WebSocket API'sine erişim sağlar
- Kısa ömürlü token için Soniox `config` async function kullanılabilir

## Monitoring

Browser konsolunda kontrol et:
1. `SonioxClient` global'de tanımlı mı? → `typeof SonioxClient !== 'undefined'`
2. `/api/config` key dönüyor mu? → `fetch('/api/config').then(r => r.json())`
3. WebSocket bağlandı mı? → `connected` event'i
4. Token'lar geliyor mu? → `token` event'i
5. Result geliyor mu? → `result` event'i

## VAD vs Soniox Endpoint Detection

| Özellik | VAD (eski) | Soniox Endpoint Detection |
|---------|-----------|--------------------------|
| **Gecikme** | 1000ms sessizlik bekle | 500ms (yapılandırılabilir) |
| **Transkripsiyon** | Ses bittikten sonra | Anlık (konuşurken) |
| **İşlem** | Browser'da (webrtcvad) | Sunucu taraflı (Soniox) |
| **Güvenilirlik** | Ortam gürültüsüne duyarlı | ML tabanlı, daha hassas |
