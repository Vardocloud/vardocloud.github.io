# GPT-Live Competitive Research — 13 Temmuz 2026

## Kaynaklar
- [OpenAI Introducing GPT-Live](https://openai.com/index/introducing-gpt-live/) (8 Tem 2026)
- [TechCrunch: OpenAI releases new voice models](https://techcrunch.com/2026/07/08/openai-releases-new-voice-models-for-more-natural-live-conversations/)
- [Medium: GPT-Live-1, Interrupted](https://medium.com/data-science-collective/gpt-live-1-interrupted-what-openais-full-duplex-voice-model-does-81dca727858e)
- [Technology.org: GPT-Live Voice AI Models](https://www.technology.org/2026/07/09/openai-gpt-live-full-duplex-voice-models/)
- [yage.ai: Don't Be Fooled by Full-Duplex](https://yage.ai/share/gpt-live-voice-programming-paradigm-en-20260709.html)

## Mimari

GPT-Live, cascaded STT→LLM→TTS sistemlerinin aksine **çift katmanlı** bir mimari kullanır:

```
┌─────────────────────────────────────────────┐
│  ETKİLEŞİM KATMANI (GPT-Live-1)             │
│  • Hafif model, full-duplex konuşma akışı    │
│  • Sürekli dinler + konuşur (paralel token)  │
│  • Backchannel sinyalleri ("mhmm", "hı hı")  │
│  • Turn-taking doğal emergent (state machine  │
│    değil — paralel token üretiminden çıkar)  │
│  • Kendi başına tool çağıramaz, kod yazamaz  │
└──────────────────────┬──────────────────────┘
                       │ delegasyon
                       ▼
┌─────────────────────────────────────────────┐
│  AKIL KATMANI (GPT-5.5)                      │
│  • Ağır model: web arama, hesaplama, kod     │
│  • Arka planda çalışır, ses katmanını        │
│    bloklamaz                                  │
│  • Sonuçlar araya girmeden konuşmaya enjekte │
└─────────────────────────────────────────────┘
```

## Vanitas ile Karşılaştırma

| Özellik | GPT-Live-1 | Vanitas v16 |
|---------|-----------|-------------|
| **Full-duplex** | ✅ Native (model seviyesi) | ✅ AudioWorklet + VAD (sistem seviyesi) |
| **Backchannel** | ✅ "mhmm", "yeah", "hı hı" | ❌ Henüz yok |
| **Barge-in** | ✅ Model kendi karar verir | ✅ GainNode(0) + isSpeaking |
| **Delegasyon** | ✅ GPT-5.5 arka planda | 🟡 Dual-path planlandı (Groq + Hermes) |
| **Aksan (Türkçe)** | ⚠️ Yabancı aksan mevcut | ✅ Soniox dil-bağımsız |
| **Gecikme** | Çok düşük | ⚠️ Bazen gecikmeli |
| **Gürültü filtresi** | ✅ Çok iyi | ⚠️ VAD bazen yanlış tetiklenir |
| **Ses klonlama** | ✅ 9 preset ses | ✅ Soniox'ta 20sn klip |
| **Fiyat** | 💰 $32-$64/saat | 💵 ~$0.70/saat (Soniox TTS) |
| **API** | Geliştirici API'si henüz yayında değil | Açık (HTTP + WS) |

## Vanitas'a Çıkarımlar

### Kısa Vade (Hemen Yapılabilir)
1. **Backchannel sinyalleri** — Konuşurken araya kısa onay sesleri ("hı hı", "anladım", "evet"). VAD konuşma algılayınca kısa bir ses dosyası oynat. ~2 satır JS.

### Orta Vade
2. **Dual-path delegasyon** — Zaten planlanmıştı (Groq hızlı + Hermes derin). GPT-Live'in interaction/work ayrımının bizdeki karşılığı.

### Uzun Vade
3. **Voice cloning** — Soniox 20sn referans klip ile özel ses. Edel'in sesini klonlamak için ideal.
4. **Konuşma hafızası** — GPT-Live'in background processing'i gibi, konuşma bağlamını session'lar arası taşımak.

## GPT-Live Zayıf Noktaları

- **Türkçe aksan sorunu** — TechCrunch ve YouTuber(Ömer Coşkun) aynı sorunu rapor etmiş. İngilizce aksanlı sesler Türkçe'de doğal durmuyor.
- **Sadece ChatGPT Plus/Pro** — Ücretsiz kullanıcı mini model alıyor.
- **API yok** — Henüz geliştirici API'si yayınlanmadı, sadece ChatGPT içinde.
- **Tool yok** — Ses katmanı kendi başına tool çağıramıyor, her şeyi arka plandaki GPT-5.5'e devrediyor.

## Fiyatlandırma Referansı (gpt-realtime-2.1 API)

| Tier | Text Input | Text Output | Audio Input | Audio Output |
|------|-----------|-------------|-------------|--------------|
| Standard | $4/M token | $24/M token | $32/saat | $64/saat |
| Mini | $0.60/M | $2.40/M | $10/saat | $20/saat |

Vanitas'ın maliyeti bunun ~%1'i (Soniox STT + TTS ~$0.70/saat + Groq LLM ~$0.20/saat).
