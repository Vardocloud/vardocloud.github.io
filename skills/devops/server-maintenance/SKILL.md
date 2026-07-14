---
name: server-maintenance
description: "Sunucu sağlığı, crash-loop önleme, kaynak izleme ve disk temizliği — Vanitas sunucusu (Oracle ARM64, 6GB RAM) için koruma katmanları."
version: 1.0.0
metadata:
  hermes:
    tags: [server, maintenance, watchdog, crash-loop, cleanup, monitoring]
    category: devops
---

# Server Maintenance — Vanitas Koruma Katmanları

Sunucu: Oracle Cloud ARM64, 0.5 OCPU, 5.8GB RAM, Ubuntu 22.04.

## Token-Free Monitoring (no_agent Scripts)

Tekrarlayan API/durum kontrollerinde LLM token'ı harcamamak için `no_agent=true`
cron job + Python script pattern'i. Instagram takip kontrolü, API health check,
dosya sistemi izleme gibi deterministik kontroller için idealdir.

### Pattern

```
Cron (no_agent=true) → Python script → API/curl → State file (JSON)
                                                   ↓
                                          Değişiklik var mı?
                                          ├─ Hayır → sessiz (boş stdout)
                                          └─ Evet → stdout'a yaz → Telegram
```

### Kritik Kurallar

| Kural | Nedeni |
|-------|--------|
| `/usr/bin/curl` tam path | Cron ortamında PATH sınırlı |
| `ALL_PROXY=""` env | WARP proxy ile çakışmayı önler |
| HTTP kodu kontrolü | 403/401 hatalarında sessiz çık |
| State file ile ilk çalıştırma sessiz | `if not prev: sys.exit(0)` |
| `os.makedirs(dirname, exist_ok=True)` | State dizini yoksa oluştur |
| Stdout boş = sessiz | no_agent cron job'lar boş çıktıda mesaj göndermez |

### Örnek: Instagram Takip Kontrolü

Script: `~/.hermes/scripts/ig_takip_kontrol.py`
Cron: `every 30m`, deliver: Operasyon Karargahı (thread 16)
Detay: `instagram` skill → `references/no-agent-polling.md`

## Koruma Katmanları

| Katman | Araç | Ne yapar? |
|--------|------|-----------|
| 1 | **Watchdog** | Her dakika crash-loop tespiti → otomatik disable + Telegram |
| 2 | **Post-update fix** | `hermes update` çalıştığında `post-update-fix.sh` otomatik çalışır — `.env` API key kontrolü, proxy service doğrulama, HTTP ping testi |
| 3 | **Chromium cleanup** | 15dk'da bir idle Chromium'ları temizler (30dk + <%1 CPU) — ancak NOT: CDP portu açık olan Chromium'ları (NotebookLM auth) öldürmez |
| 4 | **Docker restart** | `on-failure:5` — sonsuz restart loop'unu engeller |
| 5 | **Journal vacuum** | 7 günlük log limiti |
| 6 | **Cron load distribution** | Provider başına job dağılımı — proxy darboğazı önleme (bkz. `references/cron-provider-load-distribution.md`) |
| 8 | **Pollinations Proxy systemd** | `hermes-pollinations-proxy.service` — Restart=always, 3sn; gateway'den bağımsız |

## Scriptler

- `scripts/watchdog.sh` — Crash-loop tespit + load kontrolü + Telegram uyarısı
- `scripts/post-update-fix.sh` — `/update` sonrası proxy/API key doğrulama (update komutuna otomatik eklendi)
- `scripts/post-update-check.sh` — Servis binary varlık kontrolü (legacy)
- `scripts/chromium-cleanup.sh` — İdle Chromium process temizliği

## Cron Job'lar

| Job | Schedule | Script |
|-----|----------|--------|
| Watchdog | `* * * * *` (her dk) | watchdog.sh |
| Chromium Cleanup | `*/15 * * * *` | chromium-cleanup.sh |

## NotebookLM Cookie Auth — Headless Chrome Refresh

NotebookLM MCP server cookie-based auth kullanır. Google cookie'leri ~6 ayda bir expire olur. ARM64 sunucuda Snap Chromium X11 sorunları çıkardığı için **Playwright Chromium** (headless) kullanılır.

### Infrastructure

- Chrome binary: `~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome`
- Auth CLI: `~/.local/bin/nlm`
- Refresh script: `~/.nlm/refresh_cookies.py`
- Cron script: `~/.hermes/scripts/nlm-auth-refresh.sh`
- Auth cron: `0 */12 * * *` — her 12 saatte bir
- Cron job ID: `e8cb75a82a56`
- Auth config dir: `~/.notebooklm-mcp-cli/`

### Headless Chrome Çalıştırma

X server / Xvfb / Xauthority gerektirmez. Snap Chromium'dan bağımsız:

```bash
CHROME_BIN=~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome
PROFILE_DIR=~/.cache/nlm-chrome-profile

$CHROME_BIN --headless=new --no-sandbox --disable-gpu \
  --disable-dev-shm-usage --remote-debugging-port=9222 \
  --user-data-dir=$PROFILE_DIR --no-first-run about:blank
```

### Auth Refresh Akışı

1. Cron tetikler → `nlm-auth-refresh.sh`
2. `nlm login --check` — valid mi?
   - EVET → `update_auth_json()` → çık
   - HAYIR → headless Chrome başlat (CDP 9222) → `nlm login --cdp-url` → Chrome'u öldür → auth.json yenile
3. Başarısızsa → Telegram alert (manuel login gerekli)

### Chromium Cleanup Uyumu

`chromium-cleanup.sh` idle Chromium'ları temizler. NotebookLM auth için çalışan headless Chrome aktif CDP portu açık olduğu için idle sayılmaz, öldürülmez.

### Pitfalls

- **Snap Chromium kullanma:** `chromium-browser` (snap) ARM64'te X11 sorunu çıkarır (ProcessSingleton, Xauthority, DISPLAY). Playwright'ın bağımsız binary'si kullanılmalı.
- **nlm login timeout:** CDP login 300sn bekleyebilir. `--force` ile mevcut profile zorla kullanılır.
- **auth.json ayrı:** `nlm login` cookie'leri `profiles/default/` altına yazar. MCP server'ın okuduğu `auth.json` ayrı dosyadır — `update_auth_json()` fonksiyonu ile senkronize edilir.
- **Gateway restart:** Cookie'ler yenilendikten sonra MCP server'ın yeni cookie'leri görmesi için Hermes gateway restart edilmelidir.

### Gateway Restart Timeout (Deactivating Loop)

`systemctl --user restart hermes-gateway` bazen **deactivating (stop-sigterm)** durumunda takılıp timeout yiyebilir. Gateway SIGTERM alır ama işlemi bitiremez (genelde Telegram flood control beklerken).

**Belirti:**
```
systemctl --user restart hermes-gateway
→ [Command timed out after 15s]
systemctl --user status hermes-gateway
→ Active: deactivating (stop-sigterm)
```

**Çözüm — Sert öldürme:**
```bash
# 1. Main PID'i bul
systemctl --user status hermes-gateway | grep "Main PID"
# 2. Zorla öldür
kill -9 <PID>
# 3. Temizlendiğini doğrula
pgrep -a gateway || echo "Temiz"
# 4. Yeniden başlat
systemctl --user start hermes-gateway
```

**Neden olur:** Gateway Telegram flood control limitine takıldığında 27+ saniye bekler. Bu sırada SIGTERM alırsa bekleme döngüsünden çıkamaz ve "deactivating" durumunda kalır. `SIGTERM`'e yanıt vermeyen bir bekleyen thread varsa systemd "stop-sigterm" state'inde sonsuza kadar bekler (systemd `TimeoutStopSec` varsayılanı 90sn, o da geçerse SIGKILL atar ama çoğu CLI restart işlemi daha erken timeout verir).

**NotebookLM versiyon güncelleme sonrası ZORUNLU:** `pip install --upgrade notebooklm-mcp-cli` çalıştırdıktan sonra MCP'nin yeni kodu yüklemesi için gateway restart gerekir. Eğer restart takılırsa yukarıdaki sert öldürme yöntemini uygula.

## Docker Konfigürasyonu

Open WebUI restart policy: `on-failure:5`
```bash
docker update --restart=on-failure:5 open-webui
```

## Crash-Loop Senaryosu

OpenClaw örneğinden ders: npm modülü silinmiş ama systemd service dosyası kalmış → `Restart=always` ile sonsuz crash-loop → CPU/RAM tüketimi → sunucu donması.

**Koruma:** Watchdog 5 dk içinde 3+ restart tespit ederse servisi otomatik disable eder.

## Post-Update Bütünlük Kontrolü

`hermes update` (veya `/update` slash command) artık iki aşamalı:

1. **Git pull + pip install** — ana framework güncellemesi
2. **`post-update-fix.sh`** — Pollinations proxy ve API key doğrulama

`post-update-fix.sh` şunları doğrular:
- `.env`'de `POLLINATIONS_API_KEY` satırı var mı
- `hermes-pollinations-proxy.service` aktif mi (değilse başlatır)
- Proxy HTTP 200 dönüyor mu (değilse restart eder + tekrar dener)

Script: `~/.hermes/scripts/post-update-fix.sh`
Hook: Kusursuz — `/update` alias'ına `&& bash ~/.hermes/scripts/post-update-fix.sh` eklendi.

Eski `post-update-check.sh` (binary varlık kontrolü) legacy olarak duruyor, yeni script onun yerini aldı.

## Config Persistence & Shell Hooks

### Config.yaml Neden Kalıcı?

`~/.hermes/` dizini (`$HERMES_HOME`) Hermes git reposunun DIŞINDADIR:
- `~/.hermes/config.yaml` — `git pull` asla dokunamaz, sadece `$HERMES_HOME` içindeki dosyaları okur
- `~/.hermes/.env`, `~/.hermes/secrets/`, `~/.hermes/google_token.json` — hepsi repo dışı, güncellemeden etkilenmez
- Sadece `/data/ubuntu/hermes-agent/` (repo) `git pull` ile güncellenir

`hermes update` akışı repo içinde çalışır: `git stash → git pull → git stash pop`. Sonra `migrate_config()` çalışır — bu fonksiyon `load_config()` ile mevcut kullanıcı config'ini okur, `DEFAULT_CONFIG` ile deep-merge yapar (kullanıcı alanları KORUNUR), sadece eksik alanları ekler ve kaydeder. Hiçbir kullanıcı ayarını silmez, override etmez.

Token/OAuth dosyaları (`secrets/linkedin_token.json`, `google_token.json`, `bardo_instagram.env`) da `$HERMES_HOME` içinde olduğu için aynı korumaya sahiptir.

### Shell Hooks: on_session_start

Hermes `config.yaml` içinde `hooks:` bloğu ile shell script'leri tanımlanabilir. Desteklenen event'lerden biri **`on_session_start`** — her oturum başlangıcında shell script çalıştırır.

**Yapılandırma (`config.yaml` içine):**
```yaml
hooks:
  on_session_start:
    - command: "~/.hermes/scripts/startup-validate.sh"
      timeout: 30
hooks_auto_accept: true   # TTY'siz ortamlar için ZORUNLU
```

**Aktivasyon:** Non-interactive ortam (OpenCode, cron, gateway) için `hooks_auto_accept: true` gereklidir. Yoksa hook sessizce atlanır.

**Wire protocol (stdin'den JSON):** Event adı, session_id, cwd bilgileri iletilir.

**Kullanım senaryoları:**
- Her oturumda kritik dosyaların (`config.yaml`, token'lar) varlığını doğrulamak
- Provider/model ayarlarının kaybolmadığını kontrol etmek
- Kayıp durumunda log/alert göndermek

### Pitfalls

- **`hooks_auto_accept` olmazsa non-interactive ortamda hook kaydolmaz.** OpenCode/cron/gateway gibi TTY'siz ortamlarda `hooks_auto_accept: true` ZORUNLU.
- **Shell hook timeout:** Varsayılan 60sn, maks 300sn. Uzun işlemler için `timeout: N` ile belirt.
- **JSON çıktı sadece `pre_tool_call` (block) ve `pre_llm_call` (context inject)'da işlenir.** Diğer event'lerde stdout/stderr ignore edilir.
- **`config.yaml`'a patch ile yazılamaz:** Değişiklik için `hermes config set` kullan. Ancak `hooks:` alanı elle düzenlenebilir (yaml formatı korunarak).

## WARP Child Process Patlaması (Zombi Değil, Canlı)

WARP proxy her bağlantı için `fork()` yapar (bkz. `/opt/warp-proxy/warp_proxy.py:92`).
Paralel işlemler (Instagram, çoklu tarayıcı) → çoklu child → CPU patlaması.

**Belirti:** `ps aux | grep warp_proxy` → 4+ Python process, hepsi R durumunda, her biri %20-30 CPU.
**Zombiden farkı:** Zombi Z durumundadır, CPU yemez. Bunlar canlı (R), aktif CPU tüketir.
**Teşhis:**
```bash
ps -eo pid,ppid,stat,cmd | grep "[w]arp_proxy.py"
# Ana process: PPID=1 (systemd). Child'lar: PPID=ana-process
```
**Restart yapmadan çözüm:** Ana process'i bırak, fazla child'ları `sudo kill` ile temizle.
Normal `kill` root process'lerinde yetkisiz kalır — `sudo` şart.
Bu yöntem diğer oturumdaki aktif bağlantıyı bozmaz.

**Önlem katmanları:**
1. **Watchdog (her dakika):** 5+ WARP child → otomatik uyarı + temizlik (en eski child + parent korunur, diğerleri `sudo kill`)
2. **Günlük restart cron (03:00):** `systemctl restart warp-proxy` → günlük sıfırlama (script: `~/.hermes/scripts/warp-daily-restart.sh`)

## Zombi Process Alarmı

WARP proxy gibi `fork()` kullanan servisler zombie biriktirebilir. Kontrol:
```bash
ps aux | awk '$8 ~ /Z/' | wc -l   # > 100 ise ALARM
```
Temizlik: parent process restart. Kök neden: `SIGCHLD → SIG_IGN` eksikliği.

## Kaynak Sınırlama

`config.yaml` içinde `delegation.max_concurrent_children` değeri 2'yi aşmamalı.

0.5 OCPU + 6GB RAM için optimal. Her kanban worker MCP spawn eder.
2 worker = 8 MCP process (güvenli). 6 worker = 24 process (donma).

Değişiklik için: `hermes config set delegation.max_concurrent_children 2`

## Acil Durum Kurtarma

Sunucu tamamen donduysa (SSH dahil):
1. Oracle Cloud Console → Instance → Reboot
2. Reboot sonrası: `systemctl --user list-units --failed`
3. Watchdog log kontrolü: `journalctl --user -u hermes-gateway --since '10m ago' | grep -i watchdog`
4. Sorunlu servis: `systemctl --user stop <unit> && systemctl --user disable <unit>`
5. RAM kontrolü: `free -h`
6. WARP proxy restart: `sudo systemctl restart warp-proxy`

## Disk Temizlik Stratejisi (Acil Müdahale)

Disk %90+ dolduğunda uygulanacak güvenli temizlik. Ayrıntılı cache haritası: `references/disk-cleanup-cache-map.md`

### Temizlik Kontrol Listesi
1. `df -h /` — mevcut durum
2. `du -sh ~/.cache/*/ | sort -rh | head -15` — cache haritası
3. Silmeden ÖNCE: aktif servislerin hangi cache'leri kullandığını düşün
4. Her silme sonrası `df -h /` ile doğrula

### Oracle Block Volume (Ek Depolama)
Oracle Always Free: **200GB block storage** (boot dahil). ~150GB daha eklenebilir.
Kurulum: `references/oracle-block-volume.md`

## Docker + Block Volume Kurtarma (Disk Dolu Senaryosu)

### /data/lost+found Pitfall (KRİTİK)

**Mekanizma:** Root disk dolduğunda Docker daemon mount noktası olan `/data`'yı root fs'te boş dizin sanıp içine yazar — `lost+found` dahil oluşur. Sonra block volume mount edilince bu dosyalar gizlenir, unmount'ta tekrar ortaya çıkar ve tekrar mount'u engeller.

**Belirti:** `df -h /` root %100, Docker container'lar `restarting` döngüsünde, `docker logs`'da `"mkdir /data/...: file exists"` hatası.

**Kurtarma sırası:**
```bash
# 1. Docker'ı durdur
sudo systemctl stop docker

# 2. Block volume'u ayır
sudo umount /data

# 3. Root fs'teki /data artıklarını temizle (lost+found vb.)
#    DİKKAT: /data mount edilmeden önce root fs'te ne varsa silinecek
#    Kullanıcı SSH ile yapmalı — Hermes'e bu komutu çalıştırtma

# 4. Volume'u tekrar bağla
sudo mount /dev/sdb1 /data

# 5. Docker'ı başlat + container'ları sırayla restart et
sudo systemctl start docker
docker restart $(docker ps -q)
```

**ÖNEMLİ:** Adım 3'teki temizlik (`/data/*`) mount YOKKEN root fs'te yapılır. Mount varken `/data` içeriği block volume'dur — dokunulmaz.

### Docker Crash-Loop Sonrası Toplu Kurtarma

Tüm container'lar aynı anda `restarting` döngüsüne girdiyse:
```bash
# Tek tek durdur
docker stop $(docker ps -q) 2>/dev/null

# ÖNCE disk temizliği yap, SONRA sırayla başlat
docker start open-webui && sleep 3
docker start <diğer-servis> && sleep 2
```

**Neden sırayla:** Eşzamanlı başlatılan container'lar Docker bridge DNS için yarışır. WARP proxy en son başlatılmalı — diğer servislerin onun SOCKS5 tunnel'ına ihtiyacı olabilir.

## Model Yönlendirme (Dinamik Beyin)

Ucuz/pahalı model arasında geçiş: `references/model-routing-dynamic-brain.md`

## Google Drive Upload

OAuth scope pitfall'ı: `references/google-drive-scope-pitfall.md`

## Model Maliyet Takibi

DeepSeek V4 Pro günlük/aylık maliyet analizi: `references/deepseek-cost-tracking.md`

## Hermes 0.16 Provider Architecture

Provider/model uyuşmazlıkları ve çözüm stratejisi: `references/hermes-provider-architecture.md`

**Özet:** `deepseek` built-in provider'dır ama `deepseek-v4-flash` ve `deepseek-v4-pro` OpenCode model adlarıdır, DeepSeek API'sinde yoktur. `opencode-go` üzerinden yönlendirilmelidir. Pollinations built-in değildir — `custom_providers` ile tanımlıdır.

## Systemd Bot Deployment

Telegram bot'u servis olarak çalıştırma pattern'i: `references/systemd-bot-deployment.md`

## Pollinations Proxy Diagnostics

Pollinations 401/auth hatalarının teşhis ve onarım akışı: `references/pollinations-proxy-diagnostics.md`

## Pitfalls

- **Cron failure debugging:** Diagnostik akışı için `references/cron-failure-debugging.md` — hata türüne göre sınıflandırma, provider sağlık kontrolü, tool limit analizi.
- **mv timeout (5 Haz 2026):** Dosya sistemleri arası `mv` büyük dizinlerde (>2GB) timeout verebilir. Bu seansta 2.1GB hermes-workspace taşınırken 30sn timeout oldu. Workaround: `cp -a kaynak/. hedef/ && rm -rf kaynak` — node_modules gibi yeniden kurulabilir büyük dizinleri önce silmek de işe yarar.
- **Disk formatlama kısıtı:** Yeni disk formatlama komutları Hermes hardline blocklist'inde — ajan çalıştıramaz. Kullanıcı SSH ile elle yapmalı. Detay: `references/oracle-block-volume.md`
- **Kanban worker sayısına gereksiz limit koyma.** Edel'in ihtiyacı olabilir. Asıl sorun crash-loop'lar, kanban değil.
- Watchdog Telegram alert'leri doğrudan bot API ile gönderir — Hermes gateway'e bağımlı değil.
- **Hermes yapılandırma değişikliklerinde daima `hermes config set <key> <value>` komutunu kullan.** Boş değer atamak için: `hermes config set anahtar ''`. Konfigürasyon dosyası korumalı olduğundan diğer yazma yöntemleri çalışmaz.
- **config.yaml korumalı:** `patch` reddedilir, doğrudan `read_file`/`cat`/`grep` yasak. Değişiklik için SADECE `hermes config set <key> <value>` kullan. Nested değerler: `hermes config set model_aliases.hizli.model glm`. Config görüntüleme: `hermes config` (API key'ler otomatik maskelenir).
- **Cron truncation (`Response remained truncated after 3 continuation attempts`):** Kök neden genelde proxy darboğazıdır — task limiti değil. Tek provider'da 5+ eşzamanlı job → proxy kuyruğu → timeout → truncation. Çözüm: job'ları provider'lara dağıt, schedule'ları stagger et. Detay: `references/cron-provider-load-distribution.md`
- **Service dosyasında API key bırakma:** Asla `Environment=` satırında plain text API key bırakma. `.env` + `chmod 600` kullan.

### OpenWebUI + Tailscale Erişim Sorunu (iptables)

**Belirti:** OpenWebUI (port 8080) çalışıyor, `docker ps` healthy gösteriyor, `curl localhost:8080` 200 dönüyor, Tailscale bağlı — ama dışarıdan erişilemiyor.

**Kök neden:** UFW `DENY IN` kuralı iptables'a DROP olarak yansır ve Tailscale arayüzünü (`tailscale0`) de bloklar.

**Teşhis:**
```bash
sudo iptables -L INPUT -n | grep 8080
# DROP  tcp -- 0.0.0.0/0 0.0.0.0/0 tcp dpt:8080  → sorun bu
```

**Çözüm:** Tailscale arayüzü için DROP'tan ÖNCE ACCEPT kuralı ekle:
```bash
sudo iptables -I INPUT 1 -i tailscale0 -p tcp --dport 8080 -j ACCEPT
# Kalıcı kaydet — netfilter-persistent kurulu olmayabilir, doğrudan rules.v4'e yaz:
sudo mkdir -p /etc/iptables && sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
```

**PITFALL — netfilter-persistent eksik:** `sudo netfilter-persistent save` komutu Oracle Cloud Ubuntu imajında yüklü olmayabilir. Doğrudan `/etc/iptables/rules.v4`'e yaz. Dizin yoksa `sudo mkdir -p /etc/iptables` ile oluştur.

Aynı sorun Hermes API (8642) veya başka Tailscale-only servislerde de çıkabilir — port numarasını değiştirerek aynı çözüm uygulanır.

## Telegram Bot Kullanıcı ID Keşfi

Yeni bir Telegram bot kurarken yetkili kullanıcının ID'sini bulma: bot token'ı ile `get_updates` API'sini çağır. Kullanıcı `/start` yazınca ID otomatik yakalanır. `python-telegram-bot` ile `Bot(token).get_updates()` yeterli.
