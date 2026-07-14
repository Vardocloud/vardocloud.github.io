# YouTube Auto-Caption SRT Overlapping Segments

## Problem

YouTube'un otomatik altyazıları (`--write-auto-subs --sub-lang tr --convert-subs srt`) SRT formatında her segment için **3 overlapping blok** üretir:

```
1
00:00:02,190 --> 00:00:04,510
Bu bir cümledir.

2
00:00:04,510 --> 00:00:06,749
Bu bir cümledir. Bu başka bir

3
00:00:06,749 --> 00:00:08,669
Bu bir cümledir. Bu başka bir cümle.
```

Her segment bir öncekinin son 1-2 kelimesini içerir. Bu, clean_srt.py'nin düzeltemediği bir yapıdır — clean_srt sadece zaman damgası formatını temizler, metin tekrarını dedup etmez.

## Sonuç

Temizlenmiş çıktıda her cümle 3 kere tekrar eder:
```
"Selam arkadaşlar. Yapay zeka ile kod Selam arkadaşlar. Yapay zeka ile kod Selam arkadaşlar. Yapay zeka ile kod yazılan araçların..."
```

## Tespit

`clean_srt.py` çıktısında aynı cümle kalıbı 3'er 3'er tekrarlanıyorsa → overlapping SRT.

## Çözüm

SRT'yi düzeltmeye çalışma. Doğrudan Method 2'ye (Pollinations Whisper) geç:
1. `yt-dlp -f 140` ile ses indir
2. `ffmpeg -ar 16000 -ac 1` ile WAV'a çevir
3. Pollinations Whisper API'ye gönder

Pollinations Whisper her zaman temiz, tekrarsız çıktı verir.

## 9 Haziran 2026 Gözlemi

CodeGraph videosu (12:41, Emrullah Yaprak) — SRT overlapping var, Pollinations Whisper temiz çıktı verdi. Segment 1 (19MB WAV) tek seferde başarıyla işlendi. Segment 2 (5MB WAV) de sorunsuz.
