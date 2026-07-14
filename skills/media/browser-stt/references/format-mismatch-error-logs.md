# Gerçek Hata Logları — v10.2 Format Uyuşmazlığı

## Semptom
Kullanıcı konuşuyor, tarayıcı ses gönderiyor, Cloudflare tunnel aktif, ama **hiçbir yanıt yok.** Transkript boş, asistan sessiz.

## v10 (REST modu) Hataları
```
[INFO] 🎙️ Flushing 60 chunks (279KB, ~15.0s)
[INFO] HTTP Request: POST https://api.deepgram.com/v1/listen?... "HTTP/1.1 200 OK"
[INFO] 🔇 Deepgram boş döndü

[INFO] 🎙️ Flushing 23 chunks (106KB, ~5.8s)
[INFO] HTTP Request: POST https://api.deepgram.com/v1/listen?... "HTTP/1.1 400 Bad Request"
[ERROR] Deepgram 400: {"err_code":"Bad Request","err_msg":"Bad Request: failed to process audio: corrupt or unsupported data"}
```

## v10.2 (Streaming WS modu) Hataları
```
[INFO] 🔗 Deepgram streaming connected
[INFO] Deepgram stream ended: received 1011 (internal error) 
       Deepgram did not provide a response message within the timeout window. 
       See https://dpgr.am/net0000
```

## Kök Neden
Browser `MediaRecorder` ile `audio/webm;codecs=opus` formatında **WebM konteynır** üretiyordu. 
Deepgram'a `encoding=opus` parametresiyle bağlanıyorduk → ham opus bekliyordu.
WebM konteynırı ≠ ham opus → "corrupt data" veya timeout.

## Çözüm (v10.3)
1. Browser: `AudioContext` + `ScriptProcessor` → Float32 → Int16 → WebSocket binary
2. Deepgram parametresi: `encoding=linear16&sample_rate=16000`
3. Sunucu: Gelen PCM'i dönüşümsüz ilet

## Doğrulama Adımları
```bash
# 1. Voice agent port kontrolü
ss -tlnp | grep 8765

# 2. CF tunnel canlı mı?
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "https://<tunnel-url>/?token=<token>"
# 200 dönmeli

# 3. Deepgram API kontrolü (API key env'den alınır)
curl -s -H "Authorization: Token <deepgram-api-key>" \
  "https://api.deepgram.com/v1/projects"

# 4. Son seans logları
tail -50 /tmp/voice_agent_v10_3.log
# "🔗 Deepgram streaming connected" ve "💬 [user]:" satırları aranır
# "corrupt data" veya "timeout" görülürse → format uyuşmazlığı
```
