# Cron Scheduling for Meet Join & Zoom Recording

## ISO Format (ZORUNLU)

One-shot cron job'larında schedule parametresi ISO 8601 formatında yazılmalıdır:

```bash
# ✅ DOĞRU — ISO format
schedule="2026-07-05T20:25:00+03:00"

# ❌ YANLIŞ — "once at" prefix çalışmaz, next_run_at: null olur
schedule="once at 2026-07-05 20:25"
```

## Timing Rules

- **Join için:** Toplantı başlangıcından **5 dakika önce** tetikle (20:30 toplantısı → 20:25 cron'u)
- **ffmpeg geçiş için:** Seminer değişim saatinde tam tetikle (18:00 → 18:00 cron'u)
- **Süre sınırı:** `repeat=1` (one-shot) kullan. Çoklu geçişlerde her biri ayrı cron job

## Pre-flight Checklist

One-shot cron oluşturduktan sonra DOĞRULA:
```bash
cronjob list | grep <job_name>
# → next_run_at: <TARIH>  olmalı, NULL olmamalı!
```

Eğer `next_run_at: null` ise → schedule formatı hatalıdır.

## No-Agent Cron Limitation

**No-agent cron script'lerine argüman geçilemez.** 

```bash
# ❌ ÇALIŞMAZ — argümanlar script path'in parçası sayılır
script="zoom_switch.sh seminer2_1800 01:05:00"

# ✅ DOĞRU — her varyant için ayrı wrapper script
script="zoom_s2.sh"   # içinde seminer2_1800 sabit
```

Her varyant için ayrı bir `.sh` dosyası yaz (`~/.hermes/scripts/` altında), içinde sabit label, path ve süre olsun. `exec` veya `nohup` ile ffmpeg'i başlat.

## 5 Temmuz 2026 — Failed Cron Postmortem

**Olay:** "Bir Çocuğun Yardım Çağrısını Duymak" semineri için 20:25 cron'u tetiklenmedi.

**Sebep:** `schedule="once at 2026-07-05 20:25"` yazıldı — Hermes bu formatı tanımıyor, `next_run_at: null` kalıyor.

**Dersler:**
1. ISO format zorunlu (`2026-07-05T20:25:00+03:00`)
2. Cron oluşturduktan sonra `next_run_at` kontrol et
3. Birincil yöntem cron DEĞİL, direkt `meet_join` tool'u. Cron sadece yedek.
