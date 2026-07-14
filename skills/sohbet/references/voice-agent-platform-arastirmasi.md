# Voice Agent Platform Araştırması (14 Haz 2026 — Güncel)

**Bağlam:** Edel için telefon/web üzerinden çalışan, Deepgram STT + Mistral LLM + Deepgram TTS kullanan sesli asistan kurulumu. Manuel pipeline (Python WebSocket relay) debug edilirken sürekli sorun çıktı → hazır platform araştırması yapıldı.

## Kritik Mimari Netleştirme

**Deepgram Voice Agent = Tam sesli asistan.** STT → LLM → TTS hepsi tek WebSocket bağlantısında. Kendi başına çalışır, başka bir platforma bağlanması gerekmez.

**LiveKit = WebRTC altyapısı.** Ses/video aktarımı, bağlantı yönetimi yapar. STT/LLM/TTS yapmaz — bunları plugin olarak bağlarsın. Deepgram Voice Agent'a ALTERNATİF değil, TAMAMLAYICIDIR.

**İlişki:** LiveKit (transport) + Deepgram Voice Agent (AI brain) birlikte kullanılabilir AMA resmi entegrasyon yoktur. Her ikisi de tek başına yeterlidir.

## Karşılaştırma Tablosu (Güncel — 14 Haz 2026)

### Managed Platformlar (No-code / Low-code)

| Platform | Fiyat | Mistral BYO | Free Tier | Mobil | Self-host |
|----------|-------|-------------|-----------|-------|-----------|
| **Vapi.ai** | $0.05/dk + model | ✅ BYO key = $0 | Trial var | ✅ Web SDK | ❌ |
| **Bland AI** | $0.14/dk free | ✅ Dahil | ✅ 2 kredi | ✅ Web | ❌ |
| **Retell AI** | $0.07-0.31/dk | ✅ Multi LLM | ✅ $10 kredi | ✅ Web | ❌ |
| **Play.ai** | Bilinmiyor | Bilinmiyor | Bilinmiyor | ✅ | ❌ |
| **Vocode** | Ücretsiz | ✅ Custom | ✅ MIT | ✅ | ✅ |

### Altyapı / Framework (Self-host)

| Platform | Fiyat | Deepgram Plugin | Mistral Plugin | Mobil | GitHub |
|----------|-------|-----------------|----------------|-------|--------|
| **LiveKit** | Ücretsiz | ✅ Resmi | ✅ Resmi | ✅ WebRTC | 11k ⭐ |
| **Pipecat** | Ücretsiz | ✅ | ✅ | ✅ | 4k ⭐ |

## Öneri Sıralaması

### 🥇 Deepgram Voice Agent (direkt API)
**En ucuz, en hızlı yol.** Zaten Deepgram API key'imiz var. Tek yapmamız gereken Settings formatını düzeltmek.

**Artıları:**
- Ek platform kurulumu yok
- Tek WebSocket bağlantısı — basit mimari
- STT + LLM + TTS hepsi Deepgram üzerinden (tek fatura)
- ~25 satır Python kodu yeterli

**Eksileri:**
- Settings validation strict (custom model adı reddedilebiliyor)
- Mobilde WebRTC yok (WebSocket kopmaları)
- Turn detection manuel ayar gerektiriyor

### 🥈 LiveKit + Deepgram Plugin
**En profesyonel, en sağlam.** WebRTC tabanlı, mobil native.

**Artıları:**
- WebRTC → iOS/Android native destek
- Built-in VAD, turn detection, noise cancellation
- Resmi Deepgram ve Mistral plugin'leri
- Apache 2.0 lisans, tamamen ücretsiz

**Eksileri:**
- Docker kurulumu gerek
- İki sistem (LiveKit + Deepgram) yönetimi
- Biraz daha karmaşık mimari

### 🥉 Vapi.ai
**En kolay, ama paralı.** No-code kurulum.

## Deepgram Voice Agent Settings — Pitfall'lar ve Çözümler

### Pitfall 1: `temperature` provider içinde olmalı
```json
// ❌ YANLIŞ — temperature think seviyesinde
{"think": {"provider": {"type": "open_ai"}, "temperature": 0.8}}

// ✅ DOĞRU — temperature provider içinde
{"think": {"provider": {"type": "open_ai", "temperature": 0.8}}}
```

### Pitfall 2: Custom endpoint'te model kısıtlaması
Deepgram, `agent.think.provider.model` alanını kendi bilinen modeller listesine karşı doğrular. "mistral-small" gibi bilmediği modelleri REDDEDER → "Error parsing client message. Check the agent.think field."

**Çözüm — Local Proxy:**
1. Deepgram'a bilinen bir model adı ver (örn. "gpt-4o-mini")
2. Endpoint'i localhost'taki bir proxy'ye yönlendir
3. Proxy, gelen istekteki model adını "mistral-small" olarak değiştirip Mistral API'ye iletir
4. Yanıtı Deepgram'a döndürür

```python
# Proxy: localhost:8766
# Deepgram "gpt-4o-mini" → Proxy "mistral-small" → Mistral API
```

### Pitfall 3: `agent.think.provider.model` = custom endpoint'te desteklenmiyor
Deepgram dokümanları: "When using a custom endpoint, the model property is NOT supported." 
→ Model adını endpoint URL'sine veya proxy'ye gömmek gerek.

### Pitfall 4: Browser AudioContext — GainNode zorunlu
Chrome'da `ScriptProcessorNode` sadece output bağlantısı varsa tetiklenir. Ama direkt `ctx.destination`'a bağlamak ECHO (mikrofon→hoparlör loop'u) yaratır.

**Çözüm:** GainNode (gain=0) ile sessiz bağlantı:
```javascript
var silentGain = ctx.createGain();
silentGain.gain.value = 0;
proc.connect(silentGain);
silentGain.connect(ctx.destination);
```

### Pitfall 5: Mobile AudioContext Suspension
iOS Safari'de ses oynatıldıktan sonra AudioContext askıya alınır → ScriptProcessor susar → PCM akmaz → Deepgram "no audio data within timeout window" hatası.

**Çözüm:** `onstatechange` ile auto-resume:
```javascript
ctx.onstatechange = function() {
  if (ctx.state === 'suspended') { ctx.resume(); }
};
```

## Araştırma Kaynakları
- Deepgram Voice Agent docs: https://developers.deepgram.com/docs/voice-agent
- LiveKit Agents: https://docs.livekit.io/agents/
- LiveKit Deepgram plugin: https://github.com/livekit/agents/tree/main/plugins/deepgram
- LiveKit Mistral plugin: https://github.com/livekit/agents/tree/main/plugins/mistralai
- Pipecat docs: https://docs.pipecat.ai
- Vapi.ai: https://vapi.ai
- Bland AI: https://bland.ai
- Retell AI: https://retellai.com

## Pipecat Değerlendirmesi (17 Haz 2026)

**Sonuç: Bizim mimariye UYGUN DEĞİL.**

Pipecat v1.3.0, WebRTC tabanlı istemci-sunucu mimarisi için tasarlanmıştır. Tarayıcı veya mobil istemci → WebRTC → Pipecat sunucu → WebRTC → istemci şeklinde çalışır. `LocalTransport` sınıfı mevcut değildir (local modül var ama sınıf implemente edilmemiş).

**Bizim mimari:** Headless ARM64 sunucuda lokal mikrofon → STT → LLM → TTS → lokal hoparlör. Hiçbir tarayıcı istemcisi yok. Her şey sunucuda.

**Pipecat quickstart bağımlılıkları:**
- Deepgram (STT), OpenAI (LLM), Cartesia (TTS) — bizim stack'imizden farklı
- `pipecat init quickstart` ile scaffold — manuel kod yok
- Tarayıcıda `localhost:7860/client` açmayı gerektiriyor

**Neden denedik:** Düşük gecikme, streaming TTS, barge-in vaatleri. Ama bunların hepsi WebRTC transport üzerinden.

**Çözüm:** Pipecat'siz, kendi pipeline'ımızda streaming TTS ve barge-in implemente edildi (v10.9). Cümle cümle TTS + asyncio.Event tabanlı cancel mekanizması + tarayıcıda AudioContext queue/stop. Pipecat'in getireceği ek değer yok, sadece mimari uyumsuzluk var.
