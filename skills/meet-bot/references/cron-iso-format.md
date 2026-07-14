# One-Shot Cron Job for Meet Events — ISO Format Zorunluluğu

## Problem

`cronjob action=create schedule="once at 2026-07-05 20:25"` → `next_run_at: null`, job hiç tetiklenmez.

## Sebep

Cron scheduler ISO format bekler. `"once at DATE TIME"` formatı parse edilemez.

## Çözüm

ISO format kullan:
```
cronjob action=create \
  schedule="2026-07-05T20:25:00+03:00" \
  name="🎙 Seminer Join" \
  prompt="..." \
  skills=["meet-bot","sohbet"]
```

## Doğrulama

Cron oluşturduktan sonra `cronjob list` ile kontrol et:
- `next_run_at` dolu olmalı (null DEĞİL)
- `state: scheduled` olmalı

## Not

Toplantı saatinden **5 dk önce** kur (20:30 toplantısı için 20:25 schedule).
