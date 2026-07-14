# faster-whisper small — Türkçe Performans Benchmark

**Tarih:** 27 Mayıs 2026
**Sunucu:** Oracle ARM64 (1 CPU, 5.8GB RAM)
**Model:** faster-whisper 1.2.1, `small`, `device=cpu`, `compute_type=int8`

## Sonuçlar

| Metrik | Değer |
|--------|-------|
| Model yükleme (ilk) | 9.6s |
| Model yükleme (cache'li) | 1.8s |
| RAM kullanımı | ~360MB (from ~62MB baseline) |
| Disk kullanımı | 464MB |
| Transkripsiyon hızı | **1.1x realtime** |
| Örnek: 2dk ses | 2dk 14sn işlem |
| Örnek: 20dk video | ~22dk işlem |
| Türkçe dil tespiti | probability 1.00 |
| Türkçe doğruluk | Çok iyi (psikoloji terminolojisi dahil) |

## Örnek Transkripsiyon

Beyhan Budak - "Neden Kötü İnsanlar Daha Zengin ve Başarılı?" videosundan:

> ...gengel olmayabiliyor, hatta seni bazen daha ileri bir noktaya da taşıyabiliyor ve enteresan bir zaman dilimi yine kötü insanların dışarıdan kalabalık gruplar tarafından çok iyi insanlar olarak tanımlandığı, pazarlandığı bir zaman dilimindeyiz. Bu da ister istemez iyi insanları biraz küstürüyor...

## Karar Ağacı (Edel onaylı — 27 May 2026)

```
YouTube videosu var mı?
├─ Evet → auto-caption var mı?
│   ├─ Evet → yt-dlp + WARP ile indir (saniyeler, bedava) ← HER ZAMAN ÖNCE BU
│   └─ Hayır → Pollinations whisper ile transkribe et (~0.05x realtime) ← ANA YOL
└─ Hayır (yerel ses) → Pollinations whisper (büyükse parçala)

Pollinations DOWN ise → yerel faster-whisper small (~1.1x realtime) ← SON ÇARE
```

Yerel whisper **sadece** Pollinations erişilemez olduğunda veya çok küçük (<1dk) işler için.

## Not

1 saniyelik sessiz/sinyal ses transkripsiyonu 10.6s sürdü (10.6x). Bu anormal — gerçek konuşmada encoder cache sayesinde 1.1x'e düşüyor. Benchmark için sessiz ses kullanma.

Pollinations 524 timeout → dosya çok büyük. 10MB (~10dk) güvenli sınır. `ffmpeg -f segment -segment_time 600` ile parçala.
