# faster-whisper small — x86_64 Benchmark (12 Tem 2026)

**Tarih:** 12 Temmuz 2026
**Sunucu:** x86_64 (Docker, WSL/Windows), 4 CPU limit, 6GB RAM limit
**Video:** "Makine Anlar mı?" (Türkçe, 16dk 37sn, 31MB WAV)
**Model:** faster-whisper 1.2.1, `small`, `device=cpu`, `compute_type=int8`

## Sonuçlar

| Metrik | Değer |
|--------|-------|
| Model yükleme (ilk) | ~30sn (timeout riski var!) |
| RAM kullanımı | ~500MB |
| Disk kullanımı | 464MB |
| Transkripsiyon hızı | **~0.1-0.2x realtime** |
| 16:37 video → işlem | ~2-3dk (120-180sn) |
| Çıktı satır sayısı | 355 satır (timestamp'li segment) |
| Çıktı boyutu | ~23.7KB metin |

## ARM64 vs x86_64

| Platform | Hız | RAM |
|----------|-----|-----|
| 1x ARM64 (Oracle) | 1.1x realtime | 360MB |
| 4x x86_64 (WSL/Docker) | 0.1-0.2x realtime | 500MB |

## Whisper Türkçe Sınırlamaları

İngilizce özel isimler sistematik hata:
- Claude → "Cloud"
- J-Space → "G-Space" / "Giz Bes"
- Searle → "Seyrılin" / "Sirlin"
- Harnad → "Harnat"
- Dennett → "Denett"
- Global Workspace Theory → "Global World Space"

Sebep: Whisper Türkçe dil modeli İngilizce proper noun'ları fonetik olarak Türkçeye zorlar. Elle düzeltme gerekir.
