# Voice Agent Test Buttons

## Neden Gerekli?

Kullanıcı "birinciyi duydum ikinciyi duymadım" dediğinde sorunun TTS'te mi mikrofonda mı olduğunu anlamak için test butonları kritik. Konuşma pipeline'ının her katmanını izole test edebilmek gerekir.

## Üç Katmanlı Test

### 1. 🔊 Test TTS — Edge TTS çalışıyor mu?
- `/api/tts` endpoint'ine sabit bir metin gönder
- Dönen MP3 blob'unu `new Audio()` ile oynat
- Ses geliyorsa: TTS pipeline'ı (Edge TTS CLI → MP3 → browser) çalışıyor
- Ses gelmiyorsa: Server'da `edge-tts` CLI hatası veya browser autoplay policy sorunu

```javascript
async function testTts() {
  const res = await fetch('/api/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'Test sesi, duyuyor musun?' }),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.onended = () => { URL.revokeObjectURL(url); audio.remove(); };
  audio.onerror = (e) => { console.error('TTS test fail:', e); };
  await audio.play();
}
```

### 2. 🎤 Test Mikrofon — Mikrofon çalışıyor mu?
- `getUserMedia` ile 2 saniye kaydet
- `MediaRecorder` ile blob'a çevir
- `new Audio(url)` ile geri oynat
- Kendi sesini duyuyorsan: mikrofon ve hoparlör çalışıyor
- Duymuyorsan: mikrofon izni, codec veya autoplay sorunu

```javascript
async function testMic() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const recorder = new MediaRecorder(stream);
  const chunks = [];
  recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data); };
  recorder.onstop = () => {
    stream.getTracks().forEach(t => t.stop());
    const blob = new Blob(chunks, { type: 'audio/webm' });
    const url = URL.createObjectURL(blob);
    new Audio(url).play();
  };
  recorder.start();
  setTimeout(() => recorder.stop(), 2000);
}
```

### 3. 🎤 Konuşmayı Başlat — Tam pipeline testi
- Web Speech API + VAD + LLM + TTS
- Test butonları 1 ve 2 çalışıyorsa ama bu çalışmıyorsa: sorun VAD, LLM veya pipeline entegrasyonunda

## Kullanıcı Şikayeti → Hızlı Teşhis

| Şikayet | Önce Test Et | Olası Sebep |
|---------|-------------|-------------|
| "Hiçbir şey duymuyorum" | 🔊 Test TTS | Edge TTS CLI hatası, autoplay policy |
| "Beni duymuyor" | 🎤 Test Mikrofon | Mikrofon izni, SpeechRecognition hatası |
| "İlk ses geldi ikinci gelmedi" | 🔊 Test TTS (bekle 5sn sonra tekrar dene) | Async gesture context kaybı, AudioContext suspend |
| "Cevap yazıyor ama ses gelmiyor" | 🔊 Test TTS (hemen dene) | TTS oynatma (decodeAudioData/HTML5 Audio) |
| "%25 yazıyor anlamadım" | Ses tanınamadı rozeti | Voiceprint eşik altı (kısık ses, ortam gürültüsü) |

## ÖNEMLİ: Test Butonları Tüm Session'da Görünür Olmalı

Kullanıcı "Konuşmayı Başlat" ile pipeline testi yaparken sorun yaşarsa, test butonları hala görünür durumda olmalı. Start/stop döngüsü test butonlarını gizlememeli.
