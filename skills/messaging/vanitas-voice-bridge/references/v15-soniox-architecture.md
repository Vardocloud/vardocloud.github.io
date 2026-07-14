# v15 — SonioxClient JS SDK (5 Temmuz 2026)

## Architecture

Browser → SonioxClient (`@soniox/client`) → Soniox WebSocket API → onFinal/onInterim → text → Groq LLM → Edge TTS

## Pipeline

```
Kullanıcı konuşur → SonioxClient WebSocket → Soniox API (gerçek zamanlı STT)
  → onInterim: anlık transkripsiyon (ekranda gösterilir)
  → onFinal: cümle tamamlandı → 300ms debounce
  → processWithLLM(text)
    → Heartbeat routing (opsiyonel)
    → Groq llama-3.3-70b streaming LLM
    → Edge TTS (tr-TR-EmelNeural)
  → SonioxClient.restart()
```

## Gecikme

| Aşama | Süre | Not |
|-------|------|-----|
| Soniox STT (gerçek zamanlı) | ~0ms | Konuşurken anında, VAD beklemesi yok |
| Groq LLM | ~300ms | llama-3.3-70b-versatile |
| Edge TTS | ~1300ms | edge-tts CLI, tr-TR-EmelNeural |
| **Toplam** | **~1600ms** | |

## API Key

- **BWS'de:** `SONIOX_API_KEY` (7c096523ad8b2dd29a2e0f99972ca8620060417e50c6c7167e1ec659dff65749)
- Sunucu `/api/config` endpoint'inden servis edilir
- Frontend `fetch('/api/config')` ile alır, hardcode yok

## Frontend (index.html)

- **`public/soniox-bundle.js`** — esbuild ile build edilmiş browser bundle (bkz: esbuild-browser-bundling.md)

### 🔴 KRİTİK: SonioxClient API (SDK v2.2+)

**YANLIŞ (eski dokümantasyon):** Constructor'a `apiKey`, `model`, `onFinal`, `onInterim`, `start()`, `stop()` parametreleri geçilmez. Bu API mevcut değildir!

**DOĞRU API:**

```javascript
// 1. Client — sadece api_key
const client = new SonioxClient({ api_key: SONIOX_KEY });

// 2. Recording — model, dil, endpoint config
const recording = client.realtime.record({
  model: 'stt-rt-v5',
  language_hints: ['tr'],           // DİKKAT: 'language' değil, 'language_hints' (array)
  enable_endpoint_detection: true,  // Soniox built-in VAD
  max_endpoint_delay_ms: 500,
  endpoint_sensitivity: 0.3,
});

// 3. Event handlers
recording.on('result', (result) => {
  // Final transkripsiyon — kullanıcı sustuğunda tetiklenir
  const text = result.tokens.map(t => t.text).join('');
});
recording.on('token', (token) => {
  // Anlık token (interim) — konuşurken gösterilir
  // token.is_final = true/false
  // token.text, token.confidence
});
recording.on('endpoint', () => { /* konuşma bitti sinyali */ });
recording.on('error', (err) => { /* hata */ });
recording.on('connected', () => { /* WebSocket bağlandı */ });

// 4. Kontrol
recording.stop();  // recording'i durdur
```

**⚠️ Parametre İsimleri (snake_case):**
| Yanlış (camelCase) | Doğru (snake_case) |
|-------------------|---------------------|
| `apiKey` | `api_key` |
| `language` | `language_hints` (string[]) |
| `sampleRate` | `sample_rate` (opsiyonel, genelde gerekmez) |
| `onFinal` | `recording.on('result', handler)` |
| `onInterim` | `recording.on('token', handler)` |
| `start()` | Yok — `realtime.record()` hemen başlatır |
| `stop()` | `recording.stop()` |

**📦 @soniox/client UMD Build Yok:**
- SDK sadece ESM (`index.mjs`) ve CJS (`index.cjs`) — UMD bundle yok
- `unpkg.com/@soniox/client@latest/dist/index.umd.js` **çalışmaz** (404)
- CDN'den script onerror → "Soniox SDK yüklenemedi"
- Çözüm: esbuild ile bundle et (bkz: `references/esbuild-browser-bundling.md`)

### ⚠️ `@soniox/client` UMD Build Yok
- SDK sadece ESM (`index.mjs`) ve CJS (`index.cjs`) formatında — UMD bundle yok
- `unpkg.com/@soniox/client@latest/dist/index.umd.js` **çalışmaz**
- Çözüm: esbuild ile kendin bundle et (bkz: `references/esbuild-browser-bundling.md`)

## Server (server.mjs)

- `/api/config` → `GET`, Soniox key'i döndürür (BWS'den)
- `/api/chat` → `POST`, Groq LLM streaming
- `/api/tts` → `POST`, Edge TTS (tr-TR-EmelNeural)
- `/api/heartbeat` → `POST`, task durumu sorgulama
- `/api/voiceprint/verify` → `POST`, MFCC voiceprint

## Pitfalls

### API Key Arama Sırası

**KRİTİK:** Bir API key ararken:
1. Önce **BWS** (`bws secret list`) — env variable'ları ve sistem anahtarları
2. Sonra **BW** (`bw list items`) — şifreler, notlar, kullanıcı hesapları
3. En son `.env` dosyası

Bu sırayı izle. BW'de farklı isimle kaydedilmiş olabilir (örn: "Soniox" item'ı).

### BWS Secret Oluşturma

```bash
# Proje ID'sini bul
bws project list

# Secret oluştur
bws secret create KEY_NAME "value" PROJECT_ID
```

### Deepgram'a Dönme

Deepgram v10'da terk edildi (WebM/opus format uyuşmazlığı). **Groq Whisper** daha hızlı ve aynı API key'i kullanır. **Soniox** gerçek zamanlı STT ile daha da iyi. Deepgram'a geri dönme.

### Groq Whisper Alternatifi

Groq'ta `whisper-large-v3` ve `whisper-large-v3-turbo` var. Ses dosyasını multipart/form-data ile `/v1/audio/transcriptions` endpoint'ine gönder. Aynı API key kullanılır. Hız: ~400ms (Deepgram'dan 2.7x hızlı).

### ElevenLabs Key Durumu

BWS'de `ELEVENLABS_API_KEY` iki key içerir (alt alta, newline ile ayrılmış). İlk key 401 döner (süresi dolmuş). İkinci key aktif. Kullanırken split yap:
```javascript
const keys = elevenLabsValue.split('\n');
const activeKey = keys[1].trim();
```
