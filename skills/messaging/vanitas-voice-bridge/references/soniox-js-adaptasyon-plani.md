# Stage 2 — soniox-js Adaptasyon Planı

Tartışma tarihi: 23 Haziran 2026
Durum: 🔜 Planlandı (Stage 1 ✅ tamamlandı)

## Amaç

Browser tarafındaki ~120 satırlık inlined ScriptProcessor + PCM → WebSocket kodunu Soniox JS SDK (`@soniox/speech-to-text-web`) ile değiştirmek. Bu, üç büyük değişiklik getiriyor.

## 1. Mimari Değişiklik

**Mevcut (Stage 1 — v11):**
```
Browser (PCM) → WebSocket → Sunucu → Soniox SDK (STT) → LLM → TTS → Browser
```

**Hedef (Stage 2 — soniox-js):**
```
Browser → soniox-js SDK → Soniox API (direkt!) → STT metni → WebSocket → Sunucu → LLM → TTS
```

Soniox SDK browser'da mikrofonu alıp doğrudan Soniox API'sine bağlanır. Sunucuya artık ham PCM değil, çözümlenmiş metin gider.

## 2. Bileşen Detayları

### 2a. Temporary API Key Endpoint (Sunucu)

API key'in browser'da görünmemesi gerekir. Bunun için FastAPI'de bir endpoint yazılır:

```python
@app.post("/api/voice-token")
async def get_voice_token(token: str = Depends(verify_voice_token)):
    # Soniox'ta temp key oluştur (SDK'daki pattern)
    # Veya mevcut SONIOX_API_KEY ile kısa ömürlü bir token oluştur
    return {"apiKey": temp_key}
```

Browser bu endpoint'e POST yaparak temporary key alır, SonioxClient'a iletir.

```javascript
const client = new SonioxClient({
  apiKey: async () => {
    const resp = await fetch('/api/voice-token', { method: 'POST' });
    const { apiKey } = await resp.json();
    return apiKey;
  },
});
```

Soniox JS SDK, key çözülene kadar sesi buffer'da tutar — kayıp olmaz.

### 2b. WebSocket Protokol Değişikliği (PCM → Metin)

**ESKİ:** Browser → PCM binary → WebSocket binary mesajı → Sunucu → Soniox SDK STT
**YENİ:** Browser → soniox-js SDK STT → metin → WebSocket text mesajı → Sunucu

Sunucudaki WebSocket handler artık:
- Binary mesaj beklemez (PCM yok)
- Text mesajları (JSON) alır: `{"type": "transcript", "text": "merhaba", "is_final": true}`
- Text mesajlarını LLM'e iletir
- Aynı TTS + ses dönüş kanalını korur

### 2c. JS Kodu Yeniden Yazımı

**Mevcut (~120 satır):**
```javascript
// AudioContext ScriptProcessor
const audioCtx = new AudioContext({sampleRate: 16000});
const source = audioCtx.createMediaStreamSource(stream);
const processor = audioCtx.createScriptProcessor(4096, 1, 1);
// PCM capture + Int16 conversion + WebSocket send
processor.onaudioprocess = (e) => {
  const input = e.inputBuffer.getChannelData(0);
  const int16 = new Int16Array(input.length);
  for (let i = 0; i < input.length; i++)
    int16[i] = Math.max(-32768, Math.min(32767, input[i] * 32767));
  ws.send(int16.buffer);
};
// Audio graph connections, error handling, cleanup...
```

**Hedef (~50 satır):**
```javascript
import { SonioxClient } from '@soniox/speech-to-text-web';

const client = new SonioxClient({
  apiKey: async () => (await fetch('/api/voice-token')).json().apiKey,
});

client.start({
  model: 'stt-rt-v5',
  languageHints: ['tr'],
  onPartialResult: (result) => {
    ws.send(JSON.stringify({type: 'interim', text: result.text}));
  },
  onFinalResult: (result) => {
    ws.send(JSON.stringify({type: 'transcript', text: result.text, is_final: true}));
  },
  onError: (err) => console.error('Soniox error:', err),
});
```

## 3. Sunucu Tarafı Değişiklikleri (vanitas_ses.py)

Mevcut `vanitas_ses.py`'nin WebSocket handler'ı şunları yapar:
1. Binary mesaj al → PCM buffer'a ekle
2. `soniox_session.send_bytes(pcm_chunk)` ile Soniox'a ilet
3. Soniox event'lerinden transcript oluştur
4. Transcript varsa LLM'e gönder

Stage 2'de:
1. Text mesaj al (`{"type": "transcript", "text": "..."}`)
2. Direkt bu metni LLM'e ilet
3. Soniox SDK backend kısmı kalkar (STT tamamen browser'a taşınır)

**Değişen:** `ws_endpoint` fonksiyonu — binary branch kalkar, text branch basitleşir.
**Değişmeyen:** TTS pipeline, proxy çağrısı, voiceprint, dual-path.

## 4. Avantajlar

| Neden | Açıklama |
|-------|----------|
| Token assembly yok | SDK hallediyor (subword concat, dedup, is_final) |
| PCM format derdi yok | Browser SDK mikrofonu doğrudan yönetiyor |
| Dil desteği | Soniox JS SDK `languageHints: ['tr']` ile Türkçe |
| Ses kalitesi | Browser native mic codec, PCM'ye çevrim yok |
| Daha az kod | Sunucu ~40 satır, browser ~50 satır eksilir |
| Daha az pitfall | PCM sample rate, buffer size, Int16 dönüşümü, AudioContext — hepsi kalkar |

## 5. Dezavantajlar / Riskler

| Risk | Açıklama | Çözüm |
|------|----------|-------|
| Bağımlılık | Browser CDN/npm'den SDK yükler | npm paketi olarak bundle'la |
| Gecikme | Ses → Soniox API → metin → WebSocket | Direkt API, çoğu durumda daha hızlı |
| Offline | SDK çalışmazsa ses gitmez | `navigator.onLine` kontrolü, hata mesajı |
| API key | Browser'da key sızdırma riski | Temporary endpoint ile çözülür |

## 6. Uygulama Sırası

1. **Temporary API key endpoint yaz** → `vanitas_ses.py`'ye `/api/voice-token` ekle
2. **WebSocket protokolünü değiştir** — binary→text geçişi
3. **JS frontend'i yeniden yaz** — soniox-js SDK ile
4. **Test** — browser'da konuş, transcript'in geldiğini doğrula
5. **Eski kodu temizle** — AudioContext/ScriptProcessor/Int16 kodunu kaldır
