# Sokuji — Canlı Çeviri Aracı Araştırması

## Genel
- **Proje:** github.com/kizuna-ai-lab/sokuji
- **Yıldız:** ~912
- **Platform:** Cross-platform (Windows, macOS, Linux) + Browser extension (Chrome, Edge)
- **Son güncelleme:** 19 Haz 2026 (çok aktif)

## Ne İşe Yarar
Canlı konuşma çevirisi — webinar, toplantı, videolarda anlık altyazı/ses çevirisi.

## AI Provider'lar

### Bulut (Ücretli)
| Provider | Gecikme | EN→TR Kalite | Not |
|----------|---------|-------------|-----|
| Google Gemini | Orta | ⭐⭐⭐⭐⭐ | Türkçe'de en iyisi |
| OpenAI GPT-4o | Orta | ⭐⭐⭐⭐ | Çok iyi |
| PalabraAI (WebRTC) | Düşük | ⭐⭐⭐⭐ | Canlı için optimize |

### Local (Ücretsiz)
| Model | Tip | Boyut | Not |
|-------|-----|-------|-----|
| Whisper (WASM) | ASR (ses→yazı) | 154MB+ | 99+ dil, Türkçe destekler |
| Opus-MT | Çeviri (CPU) | 5-50MB | 74 dil çifti, hafif |
| TranslateGemma | Çeviri (WebGPU) | ~200MB | Kaliteli, GPU gerekebilir |

**Local mode:** Browser'da WebAssembly + WebGPU ile çalışır. Veri dışarı çıkmaz, internet gerekmez.

## Dil Desteği
- 60+ dil (Türkçe dahil)
- EN→TR: Tüm provider'larda çalışır

## Platform Desteği
- Google Meet, Zoom, Microsoft Teams (web), Discord, YouTube Live
- Browser extension: web versiyonlarında
- Desktop app: tüm sistem sesi

## Alternatifler
- **Google Meet canlı altyazı + çeviri** (Mayıs 2025 beta, ücretsiz)
- **Live Meeting Interpreter** (Chrome extension)
- **LiveKit Translated Captioning** (github.com/livekit-examples/live-translated-captioning)
- **LiveCaptions-Translator** (github.com/SakiRinn/LiveCaptions-Translator, Windows-only, 3.2K ⭐)
