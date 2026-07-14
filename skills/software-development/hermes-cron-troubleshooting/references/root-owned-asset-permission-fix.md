# Root-Owned Hermes Assets — Permission Fix Guide

Cron job'ları `ubuntu` kullanıcısı olarak çalışırken, bazı Hermes asset'leri `root` tarafından oluşturulmuş olabilir. Bu durumda cron script'leri PermissionError ile kırılır.

## Hata Türleri

- `PermissionError: google_token.json` → Token root:600, ubuntu okuyamaz → Alternatif token + env var override
- `PermissionError: sentez_debug/` → Debug dizini root oluşturmuş → Path'i `/tmp/` altına taşı
- `logging: Permission denied: job_recovery.log` → Log root:644, ubuntu yazamaz → Dosyayı sil (dizin sahibi ubuntu)
- `tee: /tmp/security_score.txt Permission denied` → Cron runner root file'ına yazamaz → File yoksa kendiliğinden düzelir

## Tespit

```bash
find /home/ubuntu/.hermes -not -user ubuntu -ls 2>/dev/null
```

## Çözümler

### Token Permission Fix (Google OAuth)

google_token.json root:600 olduğunda tüm Google API script'leri kırılır.

1. `.bak` dosyası varsa oku (root:644 olabilir, ubuntu okur)
2. Google Auth library (google.oauth2.credentials.Credentials) ile refresh token'ı kullan
3. Yeni token'ı ubuntu'nun okuyabileceği bir yola yaz (google_token_ubuntu.json)
4. google_api.py'ye HERMES_GOOGLE_TOKEN_PATH env var override desteği ekle: os.environ.get() kontrolü + Path() fallback
5. Script'lere export HERMES_GOOGLE_TOKEN_PATH ekle

### Debug Dizini Permission Fix

Root-owned data/sentez_debug/ → Path'i /tmp/sentez_debug/ olarak değiştir. /tmp/ world-writable'dir.

### Log Dosyası Permission Fix

Root-owned log dosyasını sil: rm -f <path>. Dizin sahibi (ubuntu) dosyayı silebilir. Sonraki çalışmada ubuntu olarak yeniden oluşur.

## Root-Owned Asset Kaynağı

- entrypoint.sh root olarak başlar, init adımlarında root-owned dosya oluşturabilir
- İlk kurulumda docker exec root ile yapılmış olabilir
- Hermes gateway (hermes gateway process) ubuntu olarak çalışır → cron job'ları da ubuntu

## Önleme

- mkdir(exist_ok=True) root-owned dizini çözmez — path seçimine dikkat et
- /tmp/ altındaki path'ler her zaman güvenli
- Düzenli root-owned dosya taraması cron'a eklenebilir
