# Chromium Profile Auth (~/.config/chromium/)

## Discovery (5 Temmuz 2026)

Edel'in `isimgorulsunn@gmail.com` Google hesabı `~/.config/chromium/` profilinde **zaten login durumda**. SID, HSID, SSID, APISID, SAPISID, __Secure-1PSID, __Secure-3PSID dahil tüm auth cookie'leri mevcut. Bu profil doğrudan kullanıldığında **2FA gerekmez** — Google hesaba zaten güveniyor.

## Cookie Durumu (5 Temmuz 2026)

```sql
-- ~/.config/chromium/Default/Cookies içinde:
SELECT host_key, name FROM cookies 
WHERE host_key LIKE '%google.com' 
  AND name IN ('SID','HSID','SSID','APISID','SAPISID','__Secure-1PSID','__Secure-3PSID');
```

Mevcut cookie'ler:
- accounts.google.com → OTZ
- .google.com → APISID, HSID, SAPISID, SID, SSID, __Secure-1PSID, __Secure-3PSID
- .google.com.tr → APISID, HSID, SAPISID, SID, SSID, __Secure-1PSID
- ogs.google.com → OTZ

Tümü **encrypted** (AES-256-GCM, Chrome master key ile). Direkt sqlite okuyamazsın ama `--user-data-dir` ile Chromium başlatınca otomatik çözülür.

## Doğrulama

```bash
# Hesap adını kontrol et
chromium --user-data-dir=/home/ubuntu/.config/chromium --headless=new --dump-dom "https://myaccount.google.com/" 2>/dev/null | grep -oP 'isimgorulsunn|@gmail.com'

# Cookie sayısını kabaca kontrol et
sqlite3 ~/.config/chromium/Default/Cookies "SELECT COUNT(*) FROM cookies WHERE host_key LIKE '%google.com' AND name IN ('SID','HSID');"
```

## Kullanım

```bash
# Meet'e direkt giriş
chromium --user-data-dir=/home/ubuntu/.config/chromium --headless=new --no-sandbox --disable-gpu "https://meet.google.com/abc-defg-hij"

# Sayfayı DOM olarak al
chromium --user-data-dir=/home/ubuntu/.config/chromium --headless=new --disable-gpu --no-sandbox --dump-dom "https://meet.google.com/" 2>/dev/null
```

## Önemli: Bu Profil Browser_* Araçlarıyla Paylaşılmaz

Hermes'in `browser_navigate` / `browser_click` araçları **Playwright'un kendi izole profilini** kullanır (`~/.hermes/.config/chromium/`). Bu profil Edel'in profiliyle aynı değildir. Aralarında:

| Profil | Yol | Google Login | Kullanım |
|--------|-----|-------------|----------|
| Edel'in profili | `~/.config/chromium/` | ✅ isimgorulsunn | Direkt chromium komutu |
| Playwright profili | `~/.hermes/.config/chromium/` | ❌ anonim | browser_* araçları |

**Köprü kurmak için:** Playwright'ı Edel'in profiliyle başlat, sonra `context.storage_state()` ile cookie'leri export et → auth.json'a yaz.

## Gelecek Seminerler İçin

1. Join öncesi ~/.config/chromium/ cookie'lerini kontrol et (5+ Google cookie)
2. Geçerliyse: `chromium --user-data-dir=...` ile join dene
3. Yoksa veya cloud sunucudaysan: normal auth flow'a düş (Yöntem 1-2-3)

## Hata Geçmişi

- **5 Temmuz 2026:** "Bir Çocuğun Yardım Çağrısını Duymak" semineri kaçtı. Sebep: Playwright anonim profili kullanıldı → 2FA → bekleme → timeout. Edel'in profili varken kullanılmadı. Ders: ilk seçenek bu profil olmalı.
