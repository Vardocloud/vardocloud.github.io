# Groq Model Benchmarks — 17 Temmuz 2026

## Amaç
Sesli görüşme (Vanitas Voice v16) için en iyi Türkçe kalitesi + hız dengesini bulan modeli seçmek.

## Test Metodolojisi
- **Prompt:** Sistem prompt'u + kullanıcı sorusu (Vanitas kişiliği)
- **Model:** llama-3.3-70b-versatile, llama-3.1-8b-instant, meta-llama/llama-4-scout-17b-16e-instruct, qwen/qwen3-32b, qwen/qwen3.6-27b, openai/gpt-oss-20b
- **Token limit:** 80 max_tokens
- **Sıcaklık:** 0.7
- **API:** Groq (LPU inference)
- **Ölçüm:** completion_time (inference süresi), queue_time (kuyruk bekleme), total_time
- **Kalite değerlendirme:** Türkçe doğallık, Vanitas kişiliğine uygunluk, emoji kullanımı, talimatlara uyum

## Sonuçlar

### Hız Karşılaştırması (Basit Selamlaşma)

| Model | Inference | Queue | **Toplam** | 
|-------|-----------|-------|-----------|
| llama-3.3-70b-versatile | 145ms | 52ms | **197ms** |
| llama-3.1-8b-instant | 32ms | 19ms | **51ms** |
| Llama 4 Scout 17B | 61ms | 17ms | **78ms** |
| Qwen3 32B | 222ms | 88ms | 310ms |
| Qwen3.6 27B | 156ms | 47ms | 204ms |

### Persona Testi (Vanitas Kişiliği ile Yanıt)

**Sistem prompt:** "Sen Vanitas, Edel'in yapay zeka yol arkadasi. Sicak, samimi, muzip. Edel'e 'canim' diye hitap et, ama cok nadiren. Kisa ve dogal Turkce konus, emoji kullanma."
**Kullanıcı:** "Vanitas bugun cok yorgunum, hic bir sey yapasim yok. Ne onerirsin?"

| Model | Yanıt | Değerlendirme |
|-------|-------|---------------|
| **llama-3.3-70b** | "Uyuyabilirsin, bir film veya dizi izleyebilirsin. Hatta rahatlayacak bir kitap okuyabilirsin." | 🟢 Doğal, kısa, pratik, Vanitas'a uygun |
| **llama-3.1-8b** | "Canım 😊... Bugün yorgun olduğunu hissettiğin için en iyisi nefes alman ve dinlenmektir..." | 🟡 Emoji kullandı (yasak olmasına rağmen), robotik |
| **Llama 4 Scout 17B** | "Canim, yorgunluk herkesin basini cevirir bazen. Neden bir mizac filmi izlemeyi denemeyelim?" | 🟡 "Mizac" kelime hatası (mizaç ≠ komedi), anlam kayması |

### Kalite × Hız Matrisi

```
                    HIZLI (≤100ms)    ORTA (100-250ms)   YAVAŞ (>250ms)
MÜKEMMEL Türkçe     -                 llama-3.3-70b ✅    -
İYİ Türkçe          Llama 4 Scout     -                  -
ORTA Türkçe         llama-3.1-8b      -                  -
KÖTÜ/Kullanılamaz   -                 Qwen3.6 27B        Qwen3 32B
```

## Karar: llama-3.3-70b-versatile ✅

Gerekçe:
- **En iyi Türkçe kalitesi:** Doğal, akıcı, Vanitas kişiliğine uygun
- **Inference süresi ~150ms:** Sesli görüşme için fazlasıyla yeterli (TTS zaten ~200-400ms ekler)
- **Talimatlara uyum:** Emoji yasağını dinler, kısa cevap verir, "canım"ı nadiren kullanır
- **Kelime hataları yok:** Llama 4'te görülen "mizac" gibi anlam kaymaları yok

Not: 8B modeller sesli görüşme için "parametresi düşük" kalıyor — Vanitas'ın kişilik nüanslarını taşıyamıyor. Qwen serisi `` etiketi yüzünden direkt kullanılamaz.
