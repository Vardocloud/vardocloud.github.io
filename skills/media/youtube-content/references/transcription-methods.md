# Transkripsiyon Yöntemleri Karşılaştırması

## Platform Karşılaştırması

| Yöntem | ARM64 (Oracle) | x86_64 (Docker/Lokal) | RAM (her ikisi) | Doğruluk |
|--------|---------------|----------------------|-----------------|----------|
| YouTube auto-caption + WARP | ~3sn | ~3sn (proxy'siz) | 0 | İyi (bazen bozuk) |
| Pollinations whisper | ~32sn/10dk | ~5sn/12dk (tahmini) | 0 (uzak) | Çok iyi ✅ |
| Yerel faster-whisper small | ~1.1x realtime | ~0.04x realtime (16dk→40sn) | ~360MB | Çok iyi ✅ |

## Pollinations Whisper Detay

- Endpoint: `POST https://gen.pollinations.ai/v1/audio/transcriptions`
- Model: `whisper`
- Auth: Bearer token (POLLINATIONS_API_KEY)
- Parametreler: `model=whisper`, `language=tr`, `file=@audio.wav`
- **Maliyet:** ~0.0020 pollen / 16dk video (WAV 31MB). Bakiye yetmezse HTTP 402 `PAYMENT_REQUIRED`
- **Balance check:** Pollinations'ta ~0.0003 pollen varsa Whisper isteği başarısız olur. Method 3'e (faster-whisper) geç.

### ARM64 Benchmark (27 May 2026 — Oracle Cloud)
- 10dk MP3 (128kbps, 9.2MB): **32 saniye**
- 60dk MP3 (128kbps, 56MB): 524 timeout — çok büyük!

### x86_64 Benchmark (12 Tem 2026 — Docker/Lokal, 6GB RAM limit)
- 16:37dk WAV (31MB): **~40 saniye** faster-whisper small (işlem + model load)
- 16:37dk WAV (31MB): Pollinations bakiye yetmediği için test edilemedi (~0.0020 pollen gerek)

### Dosya Boyutu Limiti
- **Pollinations güvenli:** ~20MB WAV (~12dk)
- **Pollinations timeout risk:** 31MB+ (yine de çalışabilir)
- **Çözüm:** 20MB+ için `ffmpeg -f segment -segment_time 600 -ar 16000 -ac 1` ile parçalara böl
- **faster-whisper limit yok:** Doğrudan streaming, her boyutta ses işlenebilir

## Yerel Whisper Small Detay

- Kütüphane: faster-whisper 1.2.1
- Model: Systran/faster-whisper-small (~464MB disk)
- Load time: 9-15sn (ilk), sonraki çağrılarda cached
- RAM: ~360MB total (model + runtime)
- Compute: CPU, int8 quantization
- ARM64 hız: ~1.1x realtime (1sn ses = 1.1sn işlem)
- **x86_64 hız: ~0.04x realtime (16dk video ≈ 40sn işlem)** — Oracle'dan ~25 kat hızlı!
- Türkçe: language detection prob 1.00

## SRT Overlapping Sorunu

YouTube auto-caption SRT çıktısı her segment için 3 overlapping blok içerir:
1. Tam metin (örn. "Merhaba sevgili dostum. Öyle bir zaman diliminde yaşıyoruz ki")
2. İlk yarı + satır sonu (örn. "Merhaba sevgili dostum. Öyle bir zaman␍␊")
3. İkinci yarı (örn. "diliminde yaşıyoruz ki iyi bir insan␍␊")

Temiz transkript için sadece ilk tam metin bloğunu al.
- clean_srt.py zaman damgalarını temizler (3x dedup YAPMAZ)
- Metin hala okunabilir olduğu sürece overlap sorunu yok sayılabilir
- Tamamen okunamaz durumda Method 2'ye geç
