# Model Karşılaştırma (30 Mayıs 2026)

Pollinations üzerinde test edilen modeller. Tüm testler proxy (`http://127.0.0.1:19999/v1`) üzerinden.

## Final Seçimler

| Görev | Model | Input | Output | Neden |
|-------|-------|-------|--------|-------|
| 🔧 Kod | minimax | 0.30 | 1.20 | SWE-bench 80.2%, en hızlı kod |
| 🔬 Analiz | glm | 1.00 | 3.20 | MMLU #1, BFCL #1 |
| ✍️ Metin | gpt-5.4-mini | 0.75 | 4.50 | 🇹🇷 En iyi Türkçe |
| 📦 Yardımcı | gemma | 0.07 | 0.34 | En ucuz, hızlı |

## Türkçe Pitfall

Modeller İngilizce ve Türkçe'de ÇOK farklı performans gösterir:
- glm: İngilizce Arena CW 1442 → Türkçe "Analyze the Request" üretiyor
- gpt-5.4-mini: Benchmark orta → Türkçe #1

HER ZAMAN hedef dilde test et.

## AUX Model Değişikliği

Gemini-flash-lite-3.1 PAID → gemma (free, iyi Türkçe, iyi vision) olarak değiştirildi.
Config: `auxiliary.vision: provider=pollinations, model=gemma`
