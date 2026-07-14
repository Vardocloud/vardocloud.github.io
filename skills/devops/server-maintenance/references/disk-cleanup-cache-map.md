# Disk Temizlik Cache Haritası

Sunucu: Oracle ARM64, 45GB disk. 5 Haz 2026'da %99 dolulukta yapılan temizlikten dersler.

## Her Zaman Güvenli (Silinebilir)

Bunlar paket yöneticisi önbellekleridir — çalışan hiçbir servis okumaz. Silinirse yeniden indirilir.

| Dizin | Boyut (gerçek) | Açıklama |
|-------|-----------------|----------|
| `~/.cache/uv` | 6.1GB | pip wheel arşivi (uv) |
| `~/.cache/pip` | 2.8GB | pip wheel arşivi |
| `~/.cache/pnpm` | 437MB | JS paket arşivi |
| `/tmp/pip-unpack-*` | 5.6GB (2 dizin) | pip kurulum artığı |
| `/tmp/snap-private-tmp` | 377MB | Snap temp |
| `~/.cache/pipx` | 27MB | pipx önbellek |

**Toplam kazanç: ~15.3GB** (5 Haz 2026'da test edildi)

## ASLA Silme (Aktif Kullanımda)

| Dizin | Boyut | Kullanan Servis | Risk |
|-------|-------|-----------------|------|
| `~/.cache/huggingface` | 539MB | faster-whisper (STT) | Sesli mesaj çalışmaz |
| `~/.cache/ms-playwright` | 956MB | Instagram, Meet, LinkedIn | Tarayıcı otomasyonu bozulur |
| `~/.cache/camoufox` | 1.3GB | Browser otomasyonu | Anti-fingerprinting profili kaybolur |
| `~/.cache/puppeteer` | 243MB | Puppeteer | Tarayıcı çalışmaz |
| `~/.cache/electron` | 111MB | Electron uygulamaları | Uygulama başlatılamaz |
| `.hermes/hermes-agent/venv` | 5.8GB | Hermes Agent | Hermes ölür |

## Yeniden Kurulabilir (Kurtarma Yolu Varsa)

| Dizin | Boyut | Kurtarma Komutu |
|-------|-------|-----------------|
| `proje/.venv` | 2-5GB | `python3 -m venv .venv && .venv/bin/pip install --cache-dir /data/projects/.pip-cache -r requirements.txt` |
| `proje/node_modules` | 1-2GB | `npm install` / `pnpm install` |

**Püf:** `.venv` yeniden kurarken `--cache-dir` ile pip cache'ini kök disk yerine `/data`'ya yönlendir. EasyOCR gibi PyTorch bağımlılığı olan projelerde `.venv` 4-5GB olabilir — `/data`'da kurmak şart.
**Püf 2:** `.env` dosyası varsa `chmod 600` yapmayı unutma — bot token'ları içerir.

## Silme Karar Ağacı

```
Cache silinecek mi?
├─ pip/uv/pnpm cache? → EVET (paket yöneticisi yeniden indirir)
├─ /tmp/pip-unpack? → EVET (kurulum artığı)
├─ /tmp/snap-*? → EVET (snap temp)
├─ huggingface? → HAYIR (STT modelleri, sesli mesaj için kritik)
├─ playwright/puppeteer/camoufox? → HAYIR (tarayıcı otomasyonu aktif)
├─ electron? → HAYIR
└─ .venv/node_modules? → ÖNCE requirements.txt/package.json yedekle, SONRA sil
```

## Docker Temizliği

```bash
docker system df          # Kullanımı gör
docker system prune -a    # TÜM kullanılmayanları sil (DİKKAT: çalışan container'ları silmez)
docker volume prune       # Kullanılmayan volume'ları sil
```

Open WebUI image: ~4.3GB. Çalışıyorsa silme.

## Kontrol Komutları

```bash
# Genel disk
df -h /

# Cache büyüklükleri
du -sh ~/.cache/*/ | sort -rh | head -15

# Büyük dosyalar (>50MB)
find /home/ubuntu -type f -size +50M -exec ls -lhS {} + 2>/dev/null | head -20

# /tmp analizi
sudo du -sh /tmp/*/ | sort -rh | head -10

# Veritabanları
find /home/ubuntu -name '*.db' -o -name '*.sqlite' | xargs ls -lhS 2>/dev/null | head -10
```
