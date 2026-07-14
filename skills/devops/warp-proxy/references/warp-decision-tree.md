# WARP Karar Ağacı — Vanitas Otomatik Karar Verir

## Genel Kural
**WARP = SON ÇARE.** Önce dene, hata alırsan WARP'a geç.

## Karar Ağacı

```
İstek geliyor
    ↓
[1] Bot korumalı site mi? (Cloudflare/Akamai/Incapsula challenge)
    EVET → WARP KULLAN: curl -x "socks5h://warp:1080"
    HAYIR → devam et
    ↓
[2] Google servisi mi? (YouTube, Meet, Gmail API, Drive)
    EVET → WARP KULLAN (datacenter IP engeli var)
    HAYIR → devam et
    ↓
[3] 403/401/Access Denied hatası aldın mı?
    EVET → WARP ile tekrar dene
    HAYIR → devam et
    ↓
[4] Dosya indirme (PDF, zip, large file)
    EVET → Önce normal dene → hata olursa WARP
    HAYIR → devam et
    ↓
[5] YouTube video indirme
    EVET → WARP + PO token gerekebilir
    HAYIR → devam et
    ↓
[6] API çağrısı (Gmail, LinkedIn, vs.)
    EVET → Normal dene (API'ler genelde sorunsuz)
    HAYIR → devam et
    ↓
[7] Normal web browsing / arama
    EVET → WARP KULLANMA (yavaşlatır)
    ↓
SONUÇ: Direkt bağlan, WARP kullanma
```

## Hızlı Karar Tablosu

| Durum | WARP? | Komut |
|-------|-------|-------|
| Bot challenge sayfası | ✅ EVET | `curl -x socks5h://warp:1080 ...` |
| YouTube/Meet/Gmail | ✅ EVET | `ALL_PROXY=socks5://warp:1080 yt-dlp ...` |
| 403 hatası | ✅ EVET | Tekrar dene WARP ile |
| Dosya indirme (hata) | ✅ EVET | WARP ile tekrar dene |
| Normal web arama | ❌ HAYIR | Direkt curl/web_search |
| API çağrısı | ❌ HAYIR | Direkt istek |
| Telegram mesajlaşma | ❌ HAYIR | ASLA WARP kullanma |
| SSH | ❌ HAYIR | ASLA WARP kullanma |

## Uygulama Kuralları

### 1. Otomatik Algılama
Bot korumalı site algılama:
```bash
# Yanıt 212 byte veya "challenge-platform" içeriyorsa → bot koruması
curl -s "URL" | grep -c "challenge-platform"
```

### 2. WARP Kullanırken
```bash
# curl
curl -x "socks5h://warp:1080" "URL"

# yt-dlp
ALL_PROXY=socks5://warp:1080 yt-dlp "URL"

# Python requests
import requests
requests.get("URL", proxies={"https": "socks5h://warp:1080"})
```

### 3. WARP Kontrolü
```bash
# WARP durumunu kontrol et
curl -x "socks5h://warp:1080" https://www.cloudflare.com/cdn-cgi/trace | grep warp
# warp=plus olmalı
```

### 4. WARP Durdurma
```bash
# SADECE acil durumda
sudo systemctl stop warp-proxy
# ❌ ASLA ALL_PROXY'yi global tanımlama (Telegram kopar)
```

## Pitfall: ALL_PROXY Kuralı
- ❌ `export ALL_PROXY=socks5://...` → TÜM trafiği bozar
- ✅ `ALL_PROXY=socks5://... komut` → Sadece o komutu etkiler

## WARP Durduğunda
1. `systemctl status warp-proxy` → durumu kontrol et
2. `sudo systemctl restart warp-proxy` → yeniden başlat
3. Hala çalışmıyorsa → WireGuard arayüzünü kontrol et: `sudo wg show`
