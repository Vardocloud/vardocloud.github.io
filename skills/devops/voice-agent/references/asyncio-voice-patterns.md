# Asyncio Patterns for Voice Agents

## Deadlock: asyncio.Lock Recursive

```python
# ❌ DEADLOCK: lock içinde kendini çağırma
async def handle_reply(text):
    async with reply_lock:
        await _process(text)
        if utterance_queue:
            await handle_reply(utterance_queue.pop())  # ← KİLİTLENİR!

# ✅ DOĞRU: kuyruk işleme lock DIŞINDA
async def handle_reply(text):
    async with reply_lock:
        await _process(text)
    # Lock bırakıldı, recursive güvenli
    if utterance_queue:
        await handle_reply(utterance_queue.pop())
```

## Streaming Timeout

```python
# ❌ RİSKLİ: aiter_lines() sonsuza kadar bekleyebilir
async for line in response.aiter_lines():
    process(line)

# ✅ GÜVENLİ: chunk ve toplam timeout
async def _stream_with_timeout():
    last_chunk = loop.time()
    async for line in response.aiter_lines():
        process(line)
        last_chunk = loop.time()
        if loop.time() - last_chunk > 20:
            raise Exception("Stream stalled")

await asyncio.wait_for(_stream_with_timeout(), timeout=45)
```

## Browser Audio: Interim Display

```python
# Deepgram Results mesajları:
if transcript:
    if is_final:
        utterance_queue.append(transcript)
        await send({"type": "transcript", "text": transcript})
        schedule_llm_reply()
    else:
        await send({"type": "interim", "text": transcript})  # ANINDA!
```

## AudioContext Resilience (JavaScript)

```javascript
// sampleRate fallback
try {
  audioCtx = new AudioContext({sampleRate: 16000});
} catch(e) {
  audioCtx = new AudioContext(); // default
}

// getUserMedia esnek
stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    channelCount: { ideal: 1 }  // zorunlu değil
  }
});

// Echo loop önleme: ZeroGain
const zeroGain = audioCtx.createGain();
zeroGain.gain.value = 0;
processor.connect(zeroGain);
zeroGain.connect(audioCtx.destination);
```

## WebSocket Çift Yönlü Hatalar

- `Cannot call "receive" once a disconnect message has been received.`
  → Tarayıcı kapandığında asyncio task'leri temizlenmeden kalır.
  → Fix: `except websockets.exceptions.ConnectionClosed` ile yakala.

- `asyncio.FIRST_COMPLETED` task cancel
  → Browser disconnect edince diğer task iptal olur.
  → Fix: `browser_alive` flag ile kontrol et, iptalden önce temizle.
