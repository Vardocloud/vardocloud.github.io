---
name: warp-proxy
description: "Cloudflare WARP+ WireGuard SOCKS5 proxy — Oracle Cloud gibi datacenter IP'lerden Google servislerine (YouTube, Meet) erişim engelini aşmak için."
version: 1.0.0
metadata:
  hermes:
    tags: [proxy, vpn, wireguard, warp, google, youtube, meet]
    category: devops
---

# WARP+ SOCKS5 Proxy

Cloudflare WARP+ WireGuard tüneli üzerinden SOCKS5 proxy. Oracle Cloud gibi datacenter IP'lerinden Google servislerine erişim engelini aşar.

## Ne Zaman Kullanılır

**⚠️ KRİTİK: Vanitas otomatik karar verir.** Detaylı karar ağacı: `references/warp-decision-tree.md`

**Kısa Versiyon:**
- Bot korumalı site → WARP KULLAN
- YouTube/Meet/Gmail → WARP KULLAN
- 403/Access Denied hatası → WARP ile tekrar dene
- Normal web/API → WARP KULLANMA (yavaşlatır)
- Telegram/SSH → ASLA WARP kullanma

**ALTIN KURAL:** WARP = SON ÇARE. Önce dene, hata alırsan WARP'a geç.

## Mimari

```
İstemci → SOCKS5 (warp:1080) → wgcf (WARP+ WireGuard) → Cloudflare → İnternet
```

- **Docker container** olarak çalışır (`vanatis-warp`, `vanatis-net` ağı üzerinde)
- Tüm container trafiği WireGuard üzerinden geçer (dedicated container — fwmark gerekmez)
- SOCKS5 proxy `0.0.0.0:1080` üzerinde dinler, Docker ağından `warp:1080` ile erişilebilir
- WARP+ lisansı ile ücretsiz sürümün throttling sorunları aşılır (`account type: unlimited`)
- Account verisi `data/warp/wgcf-account.toml` olarak persistent — restart'ta kaybolmaz

## Kurulum (Docker)

WARP artık ayrı bir Docker container olarak çalışır. Manuel kurulum gerekmez.

### Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `Dockerfile.warp` | Debian slim + wireguard-tools + wgcf + python3 |
| `scripts/warp-entrypoint.sh` | wgcf register → license → WireGuard up → SOCKS5 start |
| `scripts/warp-socks5-proxy.py` | Python SOCKS5 proxy (0.0.0.0:1080) |
| `data/warp/` | WARP account persistence (wgcf-account.toml) |
| `.env` → `WARP_LICENSE_KEY` | WARP+ lisans anahtarı |

### Başlatma / Durdurma

```bash
# Host PC'den (C:\VanitasDocker):
docker compose -f "C:\VanitasDocker\docker-compose.yml" --project-directory "C:\VanitasDocker" up -d warp
docker compose -f "C:\VanitasDocker\docker-compose.yml" --project-directory "C:\VanitasDocker" stop warp
docker compose -f "C:\VanitasDocker\docker-compose.yml" --project-directory "C:\VanitasDocker" restart warp

# Log kontrol:
docker logs vanatis-warp --tail 20
```

### Container İçinden Restart

Vanitas container'ından WARP container'ı restart edilemez (farklı container). Host'dan yapılmalı.

## Kullanım

**⚠️ ALTIN KURAL: ALL_PROXY'yi ASLA global tanımlama.** `.env`'e `ALL_PROXY=socks5://...` yazarsan WARP durduğunda Telegram dahil tüm dış bağlantılar kopar (`httpx.ConnectError`). Sadece ihtiyaç duyan spesifik komutlarda prefix olarak kullan:

```bash
ALL_PROXY=socks5://warp:1080 yt-dlp "URL"
```

WARP'ı durdurman gerekirse ÖNCE `.env`'i kontrol et, ALL_PROXY'nin yorum satırı olduğundan emin ol.

```bash
# YouTube altyazı indirme (--write-auto-subs + --skip-download)
yt-dlp --proxy socks5://warp:1080 --write-auto-subs --sub-lang tr --skip-download --convert-subs srt "URL" -o "/tmp/transcript_%(id)s"

# YouTube metadata
yt-dlp --proxy socks5://warp:1080 --dump-json "URL" -o /dev/null > /tmp/v.json 2>/dev/null

# Python requests (PySocks gerekli)
# uv pip install PySocks
python3 -c "import requests; print(requests.get('URL', proxies={'https': 'socks5h://warp:1080'}).text)"

# curl
curl -x "socks5h://warp:1080" "URL"

# Genel
export ALL_PROXY="socks5://warp:1080"
```

## Doğrulama

```bash
# WARP durumu: warp=plus görmeli
curl -x "socks5h://warp:1080" https://www.cloudflare.com/cdn-cgi/trace | grep warp

# IP değişmeli (Oracle IP'si değil Cloudflare IP'si olmalı)
curl -x "socks5h://warp:1080" https://ifconfig.me
```

## Docker Service (Mevcut)

WARP artık Docker container olarak çalışır. Systemd kullanılmaz.

```yaml
# docker-compose.yml — warp servisi
warp:
  build:
    context: .
    dockerfile: Dockerfile.warp
  container_name: vanatis-warp
  hostname: warp
  volumes:
    - ./data/warp:/data
  environment:
    - WARP_LICENSE_KEY=${WARP_LICENSE_KEY}
  restart: unless-stopped
  cap_add:
    - NET_ADMIN
    - SYS_MODULE
  networks:
    - vanatis-net
  healthcheck:
    test: ["CMD", "python3", "-c", "import socket; s=socket.socket(); s.settimeout(3); r=s.connect_ex(('127.0.0.1',1080)); s.close(); exit(0 if r==0 else 1)"]
    interval: 30s
    start_period: 30s
```

Container `restart: unless-stopped` ile otomatik yeniden başlar. `entrypoint.sh` watchdog içerir.

## WARP+ Lisansı

WARP+ lisansı `.env` dosyasındaki `WARP_LICENSE_KEY` değişkeninden okunur.
Container首次 başlatıldığında `wgcf register` ile hesap oluşturulur, lisans otomatik bağlanır.
Account verisi `data/warp/wgcf-account.toml` olarak saklanır — restart'ta yeniden register gerekmez.
Lisans sadece 5 cihazda kullanılabilir.

## Sınırlamalar

- YouTube video INDİRME (403): Metadata başarılı, ancak video akışı yeni PO token gerektiriyor — WARP+ bile bunu aşamaz. Bu IP engelinden bağımsız bir anti-bot önlemidir.
- MTU 1280: WireGuard overhead'i nedeniyle düşük MTU. Bazı HTTPS bağlantılarında fragmentasyon olabilir.

## Hermes Browser Entegrasyonu (KRİTİK)

Browser tool'u için **iki engine modu** var. Her birinin kendine özgü kullanım alanı var:

### Skool Erişimi İçin Hızlı Başlangıç

Skool topluluklarını kontrol ederken: `engine: auto` (varsayılan) kullan, Skool Cloudflare tarafından korunur — `engine: chrome`/WARP timeout verir. Login bilgileri ve topluluk listesi `references/skool-access.md` dosyasındadır — login gerektiğinde ÖNCE bu dosyayı oku. Şifre `.env`'de değil, referans dosyasındadır.

### `engine: auto` — Browserbase Cloud (VARSAYILAN, çoğu durumda doğru seçenek)

```yaml
browser:
  engine: auto
```

- Browserbase'in residential IP'lerini kullanır
- **APA (Incapsula)**: ✅ Çalışır — gerçek tarayıcı fingerprint'i WAF'ı aşar
- **Skool (Cloudflare)**: ✅ Çalışır — residential IP'ler Cloudflare tarafından bloklanmaz
- **Genel web**: ✅ Çalışır
- **Google servisleri**: ❌ "Sign in to confirm you're not a bot" hatası verebilir
- WARP proxy'sini yok sayar, kendi IP'sini kullanır
- UA: Mac + Chrome 146, `via: 1.1 google` header

### `engine: chrome` — Local Chromium + WARP (SADECE Google servisleri için)

```yaml
browser:
  engine: chrome
```

- Sunucuda local Chromium başlatır
- ALL_PROXY'e saygı duyar → WARP üzerinden çıkar
- **Google/YouTube/Meet**: ✅ WARP sayesinde çalışır
- **APA (Incapsula)**: ❌ WARP IP'leri Incapsula tarafından bloklanır
- **Skool (Cloudflare)**: ❌ WARP (Cloudflare) IP'leri Skool (Cloudflare) tarafından bloklanır — ironik
- UA: Linux + Chrome 131

### Doğru Strateji: Varsayılan `auto`, gerekince `chrome`

**Günlük kullanımda `engine: auto` ile başla.** Sadece Google servislerine (YouTube, Meet) erişmen gerektiğinde `engine: chrome`'a geç. Ama unutma: `chrome` modundayken APA ve Skool çalışmaz.

### 2. `.env` — ALL_PROXY (sadece chrome modunda etkili)

```bash
ALL_PROXY=socks5://warp:1080
```

### 3. Gateway restart

```bash
systemctl --user restart hermes-gateway
```

**⚠️ Cron mode:** `approvals.cron_mode: deny` ayarıyla cron job'lar `systemctl restart` komutunda `pending_approval` alır ve bloke olur. Browser engine değişikliği yapıldıysa, cron job çalışmadan ÖNCE gateway manuel olarak restart edilmiş olmalıdır. Cron job sırasında engine değiştirilemez.

### Doğrulama

Browser'la `https://ifconfig.me`'ye git, IP Cloudflare (104.x.x.x) olmalı, Oracle (193.x.x.x) değil.  
"via: 1.1 google" görünüyorsa → hala Browserbase cloud'dasin → engine: chrome kontrol et.

### Platform Erişim Matrisi (30 Mayıs 2026)

| Platform | `engine: auto` (Browserbase) | `engine: chrome` (WARP) | En iyi yöntem |
|----------|------------------------------|--------------------------|---------------|
| **APA** (Incapsula) | ✅ Tam metin | ❌ 212 byte boş sayfa | `auto` |
| **Skool** (Cloudflare) | ✅ Çalışıyor, login OK | ❌ Timeout | `auto` |
| **Google/YouTube/Meet** | ❌ "Sign in to confirm" | ✅ WARP aşar | `chrome` |
| **Genel web** | ✅ | ✅ | `auto` (varsayılan) |

### Pitfall: Cloud vs Local

| Gösterge | Browserbase Cloud | Local + WARP |
|----------|-------------------|--------------|
| IP | Residential (ABD, değişken) | Cloudflare (104.x.x.x, DE) |
| UA | Mac + Chrome 146 | Linux + Chrome 131 |
| via header | 1.1 google | Yok |
| WARP çalışır mı? | ❌ (ALL_PROXY yok sayılır) | ✅ |

## Pitfalls

| Hata | Sebep | Çözüm |
|------|-------|-------|
| `warp=off` (SOCKS5) | `SO_MARK` ayarlanamıyor — proxy root değil | Proxy'yi `User=root` ile çalıştır. `setsockopt(SOL_SOCKET, 36, 1)` CAP_NET_ADMIN ister |
| `warp=off` (gost) | gost SO_MARK desteklemez | Python proxy kullan (bkz. `scripts/warp-socks5-proxy.py`) |
| Docker container'da çalışmaz | Docker NAT routing'i WireGuard handshake'ini bozar, TCP timeout | Host üzerinde çalıştır, Docker KULLANMA |
| `wg-quick` tüm trafiği yönlendirir | Varsayılan davranış, SSH kopar | `wg-quick` KULLANMA, manuel `wg` + fwmark kullan |
| `wg setconf` Address/MTU satırını tanımaz | wgcf çıktısı wg-quick formatında — `wg setconf` sadece PrivateKey ve [Peer] bilir | Address, DNS, **ve MTU** satırlarını sil. MTU ayarını `ip link set mtu 1280 up dev wgcf` ile yap |
| `docker-warp-socks` v5 lisans desteği yok | Cloudflare policy | wgcf ile doğrudan WireGuard kullan |
| `docker-warp-socks` handshake OK ama veri yok | Free WARP throttling veya Docker NAT | WARP+ lisansı + host WireGuard |
| `ExecStartPre` başarısız (203/EXEC) | Binary yolu yanlış veya tek `sh -c` içinde `-` prefix çalışmaz | Her komutu ayrı `ExecStartPre` yap, tam path kullan (`/usr/bin/wg` değil `wg`) |
| `RTNETLINK answers: File exists` | Önceki oturumdan kalan wgcf arayüzü var | `ExecStartPre` başına `-` koy (ignore failure)
| Browser WARP kullanmıyor, `via: 1.1 google` görünüyor | `engine` yanlış değer (örn. `local`) → `auto`'ya düşüp Browserbase cloud kullanıyor | `journalctl --user -u hermes-gateway --since '5m' \| grep -i "Unknown browser engine"` ile kontrol et. Geçerli: `auto`, `chrome`, `lightpanda`. Doğrusu: `engine: chrome` |
| Cron job'ta gateway restart bloke oluyor (`pending_approval`) | `approvals.cron_mode: deny` — sistem servis restart'ları onay bekler, cron'da onaylanamaz | **Ön koşul:** `engine: chrome` ve gateway restart'ı cron job ÇALIŞMADAN ÖNCE yapılmış olmalı. Config değişikliği sonrası restart için terminalden manuel onay gerek. Cron job sırasında browser engine değiştirilemez. |
| **WARP proxy 503/timeout dönüyor** | WARP servisi çalışır durumda (systemctl active) olmasına rağmen proxy üzerinden yapılan tüm istekler 503 dönebilir. Belirti: `curl -x socks5h://warp:1080 https://httpbin.org/ip` → 503 HTML. Journal'da "Connection reset by peer" hataları görülebilir. Sebep: WARP endpoint'i (engage.cloudflareclient.com) geçici olarak erişilemez, veya Cloudflare WARP IP'leri hedef site tarafından engellenmiş olabilir. | Önce diagnostik yap: `curl -s --socks5 warp:1080 https://cloudflare.com/cdn-cgi/trace | grep warp` — warp=off geliyorsa proxy ayakta değil. `curl -s https://cloudflare.com/cdn-cgi/trace | grep warp` — direkt erişimde warp=on geliyorsa WARP hala çalışıyor ama proxy katmanı bozuk. Çözüm: `sudo systemctl restart warp-proxy` dene. Kalıcı değilse (`journalctl -u warp-proxy --since 1h` içinde sürekli "reset" hatası), wgcf bağlantısını sıfırla: `sudo systemctl stop warp-proxy && sudo ip link del dev wgcf && sudo systemctl start warp-proxy`. Hala düzelmezse Cloudflare WARP+ lisans durumunu kontrol et. |
| **WARP SOCKS5 port 1080 completely down** (12 Tem 2026) | Docker container apparently running (`restart: unless-stopped`) but SOCKS5 proxy port not listening. All proxychains-dependent cron jobs fail silently with exit code 1. WARP daily restart at 03:00 may cause extended downtime if the container fails to restart cleanly. | Check with: `curl -x socks5h://127.0.0.1:1080 -s -o /dev/null -w "%{http_code}" https://cloudflare.com/cdn-cgi/trace 2>&1` — 000 = port not listening. Direct test: `curl -s https://upwork.com` — if works, environment has native IP (WSL/Docker Desktop) and WARP is unnecessary overhead. **Fix:** For dependent cron jobs, design direct-first with proxy fallback (see `upwork-cookie-session` skill — PITFALL: WARP Single Point of Failure). Docker Desktop'ta container'ları host'tan restart et: `docker compose restart warp`. |
| **Zombie process birikmesi** (31 Mayıs 2026) | Python proxy child process'leri `waitpid()` yapmıyor — uzun süre çalışınca binlerce `<defunct>` zombie birikir. 17 saatte ~2969 zombie görüldü, load 6+ | `sudo systemctl restart warp-proxy` ile temizlenir. **Periyodik restart cron job'u önerilir:** günlük 04:00'te restart. |
| `/opt/warp-proxy/` yazma izni | Dizin root'a ait — `cp`直接 başarısız olur | Dosyaları önce `/tmp`'ye yaz, sonra `sudo cp /tmp/X /opt/warp-proxy/X`. `tee` de root ile çalıştırılmalı. |
| Duplicate routing rules | `ip rule add fwmark 1 lookup 100` her çalıştırmada yeni entry ekler — 10+ kural birikebilir | Komutu `2>/dev/null || true` ile çalıştır veya önce `ip rule list \| grep "fwmark 0x1 lookup 100"` ile kontrol et. Tekrar kurulumda önce eski kuralları temizle: `sudo ip rule del fwmark 1 lookup 100` |
| **WARP durunca Telegram kopması** (1 Haz 2026) | ALL_PROXY global tanımlıysa WARP durduğunda tüm bağlantılar (`httpx.ConnectError`) kopar, Telegram mesajlaşması kesilir | ALL_PROXY'yi ASLA global tanımlama. Sadece ihtiyaç duyan komutlarda prefix yap. WARP durdurmadan önce `.env` kontrol et. |
| **WARP + AI web araçları çalışmıyor** (13 Haz 2026) | Bazı AI araçlarının (Mailmeteor, DraftEmail vb.) client-side JS/API çağrıları WARP SOCKS5 proxy'den geçerken bot korumasına takılabilir veya CORS/WebSocket bağlantıları kopabilir. Belirti: submit butonu disabled kalır, fetch istekleri timeout yer, sayfa boş gelir. | `ALL_PROXY=""` ile dene veya proxy'siz Chrome başlat (`ALL_PROXY="" chromium ...`). WARP'ı kapatmak her zaman çözüm değil — bazen site bot detection'a takılır (Browserbase cloud'da çalışır). Önce WARP'sız dene, olmazsa Browserbase'e geç. |

## NotebookLM Dokümantasyonu

Tüm kurulum, kullanım ve sorun giderme dokümanları NotebookLM'de saklanır:

- **Notebook:** [WARP+ SOCKS5 Proxy](https://notebooklm.google.com/notebook/ab310059-3b52-4fb9-8963-20eeabf32fd1)
- **Etiketler:** `warp, wireguard, socks5, proxy, cloudflare, hermes, infra`
- **Kaynak sayısı:** 8 (Mimari, Kullanım, WireGuard Config, Proxy Kodu, Systemd, Kurulum, Sorun Giderme, Referanslar)
- **Auth yenileme:** `python3 ~/.nlm/refresh_cookies.py` — headless Chromium + Xvfb + CDP ile otomatik Google auth yenileme. Manuel login gerekirse bu script çalıştırılır.

## Dosya Adı

Skill'deki `scripts/warp-socks5-proxy.py` ile deployed `/opt/warp-proxy/warp_proxy.py` aynı koddur — production'da kısa dosya adı kullanılır.

## Quick Decision (Vanitas Otomatik)

| Durum | WARP? | Komut |
|-------|-------|-------|
| Bot challenge | ✅ | `curl -x socks5h://warp:1080` |
| YouTube/Meet | ✅ | `ALL_PROXY=socks5://warp:1080 yt-dlp` |
| 403 hatası | ✅ | Tekrar WARP ile |
| Normal web | ❌ | Direkt |
| API | ❌ | Direkt |
| Telegram/SSH | ❌ | ASLA |

Detaylı karar ağacı: `references/warp-decision-tree.md`

## References

- **Browser + WARP teşhis:** `references/browser-antibot-diagnostics.md` — anti-bot katmanları ve karar ağacı
- **Browser debug workflow:** `references/browser-debug-workflow.md` — adım adım doğrulama, debug sırası, kritik kurallar
- **Browser engine debug:** `references/browser-engine-debug.md` — engine misconfig tanı ve düzeltme adımları (2026-05-28)
- **Skool erişim ve login:** `references/skool-access.md` — Skool toplulukları, login akışı, engine seçimi
- **wgcf kurulum:** `references/wgcf-workflow.md` — Adım adım wgcf kayıt, lisans bağlama, WireGuard test, PO token notları
