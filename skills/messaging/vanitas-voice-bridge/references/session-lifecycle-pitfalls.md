# Voice Agent Session Lifecycle Pitfalls (5 Temmuz 2026)

## Sorun: İkinci Konuşma İşlenmiyor

### Sebep 1: `isProcessing` Sıfırlanmıyor

`processWithLLM()` başlangıcında `isProcessing = true` yapılır. TTS bittiğinde `finishTts()` çağrılır. Eğer `finishTts()` içinde `isProcessing = false` YOKSA:

```
Konuşma 1 → result event → processWithLLM (isProcessing=true)
  → TTS oynat → finishTts()
  → startSoniox() → yeni recording başlar
  → Konuşma 2 → result event → **isProcessing hala true → processWithLLM ÇAĞRILMAZ!** ❌
```

**Düzeltme:** `finishTts()` içinde `isProcessing = false` ekle:
```javascript
function finishTts() {
  isSpeaking = false;
  isProcessing = false;  // ← KRİTİK: bunu unutma!
  updateTranscript('', '');
  autoRestart = true;
  releaseMicrophone();
  startSoniox();
}
```

### Sebep 2: Mikrofon Stream'i Temizlenmiyor

`initSoniox()` içinde `getUserMedia` ile stream alınır (`vpStream`). TTS sonrası `finishTurn()`/`finishTts()` içinde bu stream KAPATILMAZSA, yeni `getUserMedia` çağrısı başarısız olur (browser aynı anda iki mikrofon stream'i açılmasına izin vermeyebilir).

**Düzeltme:** Tüm dönüş noktalarında stream'i kapat:
```javascript
function releaseMicrophone() {
  stopPcmCapture();
  if (vpStream) {
    vpStream.getTracks().forEach(t => t.stop());
    vpStream = null;
  }
}

// Çağrılması gereken yerler:
// - finishTurn() → startSoniox() öncesi
// - finishTts() → startSoniox() öncesi
// - stopSession() → temiz kapatma
```

### Sebep 3: Çift Mikrofon (Manuel getUserMedia + Soniox Recording)

Soniox `realtime.record()` kendi `MicrophoneSource`'u ile AYRI bir mikrofon açar. Eğer sen de manuel `getUserMedia` ile ikinci bir stream açarsan, browser'da kaynak çakışması olur.

**Düzeltme:** İkisinden birini kullan. Soniox Recording'i tercih et:
```javascript
// YANLIŞ — iki mikrofon:
const stream = await getUserMedia(...);  // ❌
vpStream = stream;
sonioxClient.realtime.record({ ... });  // ❌ ikinci mikrofon

// DOĞRU — sadece Soniox Recording:
sonioxClient = new SonioxClient({ api_key: KEY });
sonioxClient.realtime.record({ model: 'stt-rt-v5', ... });  // ✅ tek mikrofon
```

## Sorun: Watchdog Timeout

`voice_watchdog.sh` port kontrolü için `curl -sf` kullanır. Eğer server yavaş cevap verirse veya port bağlantısı askıda kalırsa, curl default timeout'u (120s) dolana kadar bekler → cron job timeout → "Script timed out after 120s".

**Düzeltme:** Tüm curl çağrılarına `--max-time 5` ekle:
```bash
if ! curl -sf --max-time 5 http://127.0.0.1:3005/ > /dev/null 2>&1; then
```

## Sorun: voice_startup.sh Node'u İkinci Kez Başlatıyor

`~/.profile` içinde `voice_startup.sh` çağrılır. Bu script port 3005 boşsa `nohup node server.mjs &` ile başlatır. Eğer aynı shell oturumunda başka bir komut da `node server.mjs` çalıştırırsa → EADDRINUSE.

**Düzeltme:** `voice_startup.sh` node server'ı başlatmasın — sadece kontrol etsin. Watchdog (2dk'da bir) başlatma işini üstlensin:
```bash
if curl -sf http://127.0.0.1:3005/ > /dev/null 2>&1; then
    log "✅ Voice Agent zaten çalışıyor"
else
    log "ℹ️ Voice Agent başlatılmadı — watchdog 2dk içinde başlatacak"
fi
```

## Özet: Güvenli Oturum Döngüsü

```
startSession()
  → startSoniox() → initSoniox()
    → SonioxClient({ api_key })
    → recording = client.realtime.record({ model, ... })
    → recording.on('result', handler)    // transkripsiyon hazır
      → processWithLLM(text)
        → stopSoniox()                    // recording durdur
        → setStatus('thinking')
        → fetch /api/chat
        → showResponse(streaming)
        → playTTS()
          → audio.onended → finishTts()
            → isSpeaking = false          // ✅
            → isProcessing = false        // ✅ KRİTİK
            → releaseMicrophone()         // ✅ stream temizle
            → startSoniox()               // yeni tura başla
```
