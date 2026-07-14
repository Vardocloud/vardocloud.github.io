---
name: browser-stt
description: Browser tabanlı speech-to-text — ses yakalama, format tuzakları, Deepgram entegrasyonu
---

# Browser STT (Speech-to-Text)

Tarayıcıdan mikrofon sesi alıp Deepgram'a gönderme. En kritik pitfall: **MediaRecorder format uyuşmazlığı.**

## Kritik Pitfall: AudioContext Sample Rate Deepgram'a UYMALI

```javascript
// ❌ YANLIŞ — AudioContext 24000Hz ama Deepgram 16000Hz bekliyor
audioCtx = new AudioContext({sampleRate: 24000});
// Ses 24kHz'de örneklenip 16kHz sanılır → bozuk transkripsiyon ("Beyin", "Susam?")

// ✅ DOĞRU — her ikisi de 16000Hz
audioCtx = new AudioContext({sampleRate: 16000});
```

**Belirti:** Deepgram çalışır ama transkripsiyon anlamsız tek kelimeler ("Beyin", "Bir", "Susam?"). Playback için aynı AudioContext kullanılıyorsa bile capture sample rate'i Deepgram'ın `sample_rate` parametresiyle eşleşmeli.

## Kritik Pitfall: MediaRecorder ≠ Ham Ses

```javascript
// ❌ YANLIŞ — MediaRecorder her zaman konteynır (WebM/OGG) üretir
mediaRecorder = new MediaRecorder(stream, {mimeType: 'audio/webm;codecs=opus'});
// Deepgram encoding=opus → ham opus bekler, WebM konteynır alınca "corrupt data"
```

```javascript
// ✅ DOĞRU — AudioContext ScriptProcessor ile ham PCM yakala
audioCtx = new AudioContext({sampleRate: 16000});
processor = audioCtx.createScriptProcessor(4096, 1, 1);
processor.onaudioprocess = (e) => {
  const input = e.inputBuffer.getChannelData(0);
  const int16 = new Int16Array(input.length);
  for (let i = 0; i < input.length; i++) {
    const s = Math.max(-1, Math.min(1, input[i]));
    int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }
  ws.send(int16.buffer);
};
```

**Neden:** MediaRecorder sesi konteynır formatında (WebM/OGG) paketler. Deepgram streaming API'si ham ses formatı bekler (linear16, opus, mulaw). Konteynır ile ham format aynı değildir — `audio/webm;codecs=opus` bile olsa bu WebM kabı içinde opus'tur, ham opus değil.

## Deepgram Encoding Eşleştirme Tablosu

| Browser Üretimi | Deepgram `encoding` | Sonuç |
|---|---|---|
| MediaRecorder WebM | `opus` | ❌ "corrupt data" |
| MediaRecorder WebM | `webm` | ❌ Streaming'de desteklenmez |
| AudioContext PCM Int16 | `linear16` | ✅ Çalışır |
| Ham opus çerçeveleri | `opus` | ✅ Çalışır (ama browser'dan zor) |

## PCM Yakalama Şablonu (Browser JS)

```javascript
const audioCtx = new AudioContext({sampleRate: 16000});
const stream = await navigator.mediaDevices.getUserMedia({
  audio: { channelCount: 1, sampleRate: 16000 }
});

const source = audioCtx.createMediaStreamSource(stream);
const processor = audioCtx.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (e) => {
  const float32 = e.inputBuffer.getChannelData(0);
  const int16 = new Int16Array(float32.length);
  for (let i = 0; i < float32.length; i++) {
    const s = Math.max(-1, Math.min(1, float32[i]));
    int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }
  ws.send(int16.buffer);
};

source.connect(processor);
processor.connect(audioCtx.destination); // Chrome'da zorunlu
```

## Deepgram Streaming WS Parametreleri (Python Sunucu)

```python
uri = (
    "wss://api.deepgram.com/v1/listen?"
    "language=tr&model=nova-2&smart_format=true&punctuate=true"
    "&encoding=linear16&sample_rate=16000&channels=1"
    "&interim_results=false"
)
dg_ws = await websockets.connect(uri, additional_headers={
    "Authorization": f"Token {api_key}"  # env'den al
})

# Browser'dan gelen PCM'i direkt ilet — dönüşüm yok
await dg_ws.send(browser_pcm_bytes)

# Sonuçları oku
async for raw in dg_ws:
    msg = json.loads(raw)
    if msg.get("type") == "Results" and msg.get("is_final"):
        text = msg["channel"]["alternatives"][0].get("transcript", "")
        if text: await handle_reply(text)
```

## Hata Teşhis Rehberi

| Semptom | Olası Neden | Kontrol Edilecek |
|---|---|---|
| Hiç tepki yok (no reaction) | Deepgram hiç cevap vermiyor | `process_deepgram` task'i hiç tetiklendi mi? Log'da "Results" var mı? |
| 400 "corrupt or unsupported data" | Format uyuşmazlığı | `encoding` parametresi gerçek gönderilen formatla eşleşiyor mu? |
| 1011 timeout "no response message" | Ses var ama anlaşılmıyor | Chunk boyutları mantıklı mı? (16kHz mono ≈ 32KB/sn) |
| 200 OK ama boş transcript | Ses seviyesi düşük veya sessizlik | Örnekleme hızı doğru mu? `sample_rate` parametresi eşleşiyor mu? |
| ScriptProcessor tetiklenmiyor | Bağlantı kopuk | `source.connect(processor)` + `processor.connect(destination)` yapıldı mı? |

## Mimari Akış

```
Browser Mikrofon
  → AudioContext ScriptProcessor (Float32 → Int16)
    → WebSocket (binary)
      → Python Sunucu (8765)
        → Deepgram WS (linear16/16kHz)
          ← Transkripsiyon (JSON)
        → Hermes Proxy (8767)
          ← Yanıt metni
        → Bella TTS (Pollinations)
          ← MP3 ses
      ← WebSocket (binary MP3)
    → AudioContext.decodeAudioData → hoparlör
```

## Dikkat Edilecekler

- AudioContext **kullanıcı etkileşimi sonrası** oluşturulmalı (click handler içinde) — autoplay politikası
- ScriptProcessorNode deprecated ama tüm browser'larda çalışıyor. AudioWorklet alternatifi daha karmaşık (ayrı JS dosyası gerektirir)
- Buffer size 4096 → 16kHz'de ~256ms gecikme, konuşma için yeterli
- `processor.connect(audioCtx.destination)` Chrome'da ses çıkışını engellemek için gerekli (yoksa audio loop oluşmaz)
- Deepgram `interim_results=false` → sadece tamamlanmış cümleler döner, yarım kelimeler gelmez
- TTS playback için yeni AudioContext gerekebilir (eskisi `close()` edilmişse)

## İlgili Dosyalar

- Voice agent ana kod: `~/voice-agent-venv/voice_agent_v10_3.py` (PCM fix'li)
- Log: `/tmp/voice_agent_v10_3.log`
- Health check: `GET /health` → `{"version": "v10.3", "stt": "deepgram-nova-2-linear16"}`
- Deepgram doküman: https://developers.deepgram.com/docs/streaming-audio
