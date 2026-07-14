# Heartbeat Query — Voice Agent Entegrasyonu

> **Tarih:** 5 Temmuz 2026
> **İlgili sürüm:** v13.1
> **Dosyalar:** `~/vanitas-web/server.mjs`, `~/vanitas-web/public/index.html`

## Amaç

Voice Agent üzerinden supervisor heartbeat verilerini sesle sorgulayabilmek. "Son task durumu" gibi bir sesli komut → heartbeat.py'ye yönlendir → TTS ile sesli cevap.

## Mimari

```
STT (Web Speech) → text → processWithLLM()
    ↓
Regex eşleşmesi var mı? (heartbeat sorgusu)
    ↓ EVET                          ↓ HAYIR
POST /api/heartbeat              POST /api/chat (Groq)
    ↓                                  ↓
heartbeat.py çıktısı              Groq streaming yanıtı
    ↓                                  ↓
playTTS() ile seslendir          playTTS() ile seslendir
```

## Backend: `/api/heartbeat` Endpoint

**server.mjs** içinde `handleHeartbeat()` fonksiyonu:

```
POST /api/heartbeat
{
  "command": "summary" | "failures" | "query",
  "task_id": "poc-supervisor-task3"  // sadece query için
}
```

Her komut `execSync` ile `python3 ~/.hermes/scripts/heartbeat.py` çağırır:
- `summary` → `heartbeat.py summary --limit 5`
- `failures` → `heartbeat.py failures --limit 5`
- `query` → `heartbeat.py query <task_id>`

Cevap formatı: `{"success": true, "data": "...text... "}`

## Frontend: Heartbeat Routing

**index.html** — `processWithLLM()` içinde STT çıktısı regex ile eşleştirilir:

```javascript
const lower = text.toLowerCase().trim();

// Summary
if (/son (task|görev|işlem).*(durum|ne oldu|özet)/.test(lower) ||
    /task (özeti|durumu)/.test(lower) ||
    /genel durum/.test(lower)) {
  heartbeatCommand = 'summary';
}
// Failures
else if (/(task|görev|işlem).*(hata|neden|başarısız)/.test(lower) ||
         /hatalı task/.test(lower) ||
         /hata raporu/.test(lower)) {
  heartbeatCommand = 'failures';
}
// Query
else if (/(?:task|görev)[\s-]*(\w+(?:-\w+)*)/.test(lower) ||
         /(\w+(?:-\w+)*).*(durum|ne oldu)/.test(lower)) {
  heartbeatCommand = 'query';
  heartbeatTaskId = lower.match(/([\w-]+(?:task|test|poc)[\w-]*)/i)?.[1];
}
```

## TTS: `playTTS()` Fonksiyonu

TTS kodu mevcut Groq akışından ayrılıp ortak `playTTS(text)` fonksiyonuna çıkarıldı:

- Heartbeat cevabı ve Groq yanıtları aynı fonksiyondan geçer
- HTML5 Audio öncelikli, decodeAudioData fallback
- AudioContext resume ile mobil autoplay kilidi açılır

## Test Edilen Komutlar

| Sesli Komut | Yönlenen | Test Durumu |
|-------------|----------|-------------|
| "son task durumu" | summary | ✅ |
| "task özeti" | summary | ✅ |
| "genel durum" | summary | ✅ |
| "hata raporu" | failures | ✅ |
| "taskler neden hata verdi" | failures | ✅ |
| Normal sohbet ("merhaba") | Groq (yönlenmez) | ✅ |
