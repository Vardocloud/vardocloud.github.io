# Browser WARP Doğrulama ve Debug

## Hızlı Doğrulama

Browser'ın WARP'tan geçtiğini doğrulamak için `ifconfig.me`'ye git:

| Gösterge | WARP ✅ | WARP ❌ |
|----------|---------|---------|
| IP | 104.x (Cloudflare) | 76.x (residential) veya 193.x (Oracle) |
| UA | Linux + Chrome | Mac + Chrome |
| `via` header | Yok | `1.1 google` |
| engine | `chrome` | `auto` (veya GEÇERSIZ `local`) |

## Debug Sırası

Browser beklenmedik davranıyorsa (block, timeout, cloud IP):

**Adım 1: Log oku**
```bash
journalctl --user -u hermes-gateway --since "5m ago" | grep -iE "browser|engine|warn"
```
- `Unknown browser engine` → config'de geçersiz değer var
- `timed out` → bağlantı sorunu
- `browser 'open' timed out` → engine cloud'a düşmüş

**Adım 2: Engine doğrula**
- Geçerli: `auto`, `chrome`, `lightpanda`
- GEÇERSİZ: `local` → sessizce `auto`'ya düşer

**Adım 3: Proxy kontrol**
- ALL_PROXY env değişkeni `socks5://127.0.0.1:1080` olmalı

**Adım 4: warp-proxy servisi**
```bash
systemctl is-active warp-proxy
curl -x socks5h://127.0.0.1:1080 https://www.cloudflare.com/cdn-cgi/trace | grep warp
```
→ `warp=plus` olmalı

**Adım 5: ifconfig.me testi**
Browser'la `https://ifconfig.me` → IP 104.x, `via: 1.1 google` YOK

## Kritik Kurallar

1. **Tool 2x aynı hata → log oku, strateji değiştir.** 3. deneme çözüm değil.
2. **Skill enum değerlerini --help ile doğrula.** `engine: local` skill'de yazıyordu ama geçerli değil.
3. **"Çalışıyor" demeden test et.** Config değişikliğinden sonra ifconfig.me zorunlu.

## Vaka: Skool WARP Debug (29 May 2026)

- Belirti: Skool'a browser ile erişim yok (403/timeout)
- Varsayım: WARP çalışıyor (proxy testi yeşil)
- Gerçek: `engine: local` → `auto`'ya düşmüş → cloud browser → WARP bypass
- Log anahtarı: `Unknown browser engine 'local' (valid: auto, chrome, lightpanda), falling back to 'auto'`
- Çözüm: `engine: chrome` + gateway restart
- Log okunduktan sonra: 3 dakika
- Log okunmadan önce: 15 dakika (3 retry döngüsü)
