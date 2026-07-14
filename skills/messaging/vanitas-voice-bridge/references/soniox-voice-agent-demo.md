# Soniox Voice Agent Demo App

**Keşif:** 28 Haziran 2026 — Soniox onboarding email serisinden (4 mail, 21-27 Haz).

## Ne?

Soniox'un GitHub'da açık kaynak yayınladığı, komple bir **voice-to-voice conversational AI** demo uygulaması.

**Repo:** `soniox/soniox_examples` → `apps/soniox-voice-bot-demo/`
**Docs:** https://soniox.com/docs/demo-apps/soniox-voice-agent

## Mimari

```
Browser mic → Soniox STT (stt-rt-v5) → LLM → Soniox TTS → Browser speaker
                      ↕                              ↕
              VAD (Silero, barge-in)       TTS streaming
```

Üç bileşen:

1. **Python server** (`server/`) — Session orchestration, modular processors:
   - VAD Processor (Silero VAD, speech boundary detection, TTS interrupt)
   - STT Processor (Soniox API real-time transcription)
   - LLM Processor (conversation history, intent, tool calling)
   - TTS Processor (Soniox API real-time speech)
2. **React frontend** (`frontend/`) — Mikrofon yakalama, audio streaming, playback
3. **Twilio proxy** (`twilio/`) — Telefon görüşmesi entegrasyonu (opsiyonel)

## Özellikler

- ✅ **End-to-end real-time:** Fully streaming, düşük gecikme
- ✅ **Multilingual:** Çoklu dil desteği (Türkçe dahil)
- ✅ **Custom persona:** Tek `tools.py` dosyasında kişilik + iş mantığı
- ✅ **Extensible tools:** LLM → harici API / veritabanı bağlantısı
- ✅ **Birden çok kanal:** Web, telefon (Twilio), WebSocket

## Bize Katkısı

Mevcut `vanitas-voice-bridge` (v12/v13) zaten SonioxClient STT kullanıyor. Ama:

| Özellik | Mevcut (v12/v13) | Soniox Demo |
|---------|------------------|-------------|
| STT | SonioxClient (browser) | Soniox API (server-side da olabilir) |
| VAD | Yok (endpoint detection) | **Silero VAD** + barge-in |
| LLM | Groq / Hermes proxy | Herhangi LLM (tool calling destekli) |
| TTS | Edge TTS / Web Speech | **Soniox TTS** (low-latency streaming) |
| Telefon | Yok | **Twilio proxy** hazır |

**Potansiyel:** Eğer Edge TTS yetmezse veya daha doğal bir ses istersek, Soniox TTS'e geçebiliriz. Silero VAD + barge-in pattern'i mevcut sistemimize eklenebilir.

## Pipecat & LiveKit Entegrasyonu

Soniox'un **Pipecat** ve **LiveKit** için özel entegrasyon sayfaları var:

- **Pipecat:** https://soniox.com/docs/integrations/pipecat/voice-agent
  - Pipecat v1.3.0+ ile Soniox STT/TTS kullanımı
  - WebRTC transport (browser → server → browser)
  - Production scaling, bölgesel endpoint desteği
- **LiveKit:** https://soniox.com/docs/integrations/livekit/voice-agent
  - LiveKit real-time altyapısı ile Soniox entegrasyonu
  - Yüksek eşzamanlılık desteği

**Not:** Pipecat daha önce değerlendirilmişti (vanitas-voice-bridge skill'inde "❌ NOT suitable for local mic/speaker architecture" notu var). Ancak Soniox'un Pipecat entegrasyonu **browser WebRTC** senaryosu için — headless local setup için hâlâ uygun değil.

## Soniox MCP Dokümantasyon Sunucusu

Hermes'te `mcp_soniox_docs_*` tool'ları mevcut:
- `soniox_search_docs(query)` — Dokümantasyonda ara
- `soniox_read_page(url)` — Sayfa içeriğini oku
- `soniox_read_section(url, heading)` — Spesifik bölümü oku
- `soniox_full_docs()` — Tüm dokümanları getir (~100K token)

**Pattern (bu oturumda keşfedildi):** Bir servis/posta geldiğinde ve o servisin MCP tool'u varsa (örn. Soniox maili → soniox-docs MCP), mail içeriğini derinleştirmek için MCP tool'unu kullan. Bu, email-knowledge-pipeline için değerli bir teknik.

## İlgili Linkler

- Demo GitHub: https://github.com/soniox/soniox_examples/tree/master/apps/soniox-voice-bot-demo
- Dokümantasyon: https://soniox.com/docs/demo-apps/soniox-voice-agent
- Python SDK: `pip install soniox` → https://github.com/soniox/soniox-python
- JS SDK: `npm install @soniox/client` → https://github.com/soniox/soniox-js
- Discord: https://discord.gg/rWfnk9uM5j
