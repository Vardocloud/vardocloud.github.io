# Playwright ile Karusel Upload — 2026'da Çalışmıyor

## Durum: BROKEN (Instagram Web 2026)

Instagram web sürümü (Haziran 2026 itibarıyla) artık Playwright headless browser ile karusel oluşturmayı desteklemiyor.

## Denenen Yöntemler

### 1. Sidebar "New post" → Popup → "Post" → File dialog

- ✅ `[aria-label="New post"]` butonu sidebar'da bulunuyor (x=24, y=434)
- ✅ Tıklanınca popup menü açılıyor (51 yeni DOM elementi)
- ✅ Popup'ta "Post" seçeneği görünüyor (x=80, y=484)
- ❌ "Post" tıklandığında **file dialog tetiklenmiyor**
- ❌ `page.expect_file_chooser()` timeout'a düşüyor
- **Sonuç:** Popup kapanıyor, sayfa feed'e dönüyor, hiçbir şey olmuyor

### 2. Direkt `/create/select/` URL

- ❌ Instagram bu URL'yi `@create` kullanıcı profili olarak algılıyor
- Title: "Chris Shelley (@create) • Instagram photos and videos"
- Çalışmıyor

### 3. Instagram Upload API (curl)

- `POST /api/v1/upload/photo/` → 404 Page Not Found
- `POST /rupload_igphoto/...` → "Unknown Server Error"
- `POST /api/v1/media/configure_sidecar/` → 429 rate limit
- **Sonuç:** API endpoint'leri çalışmıyor veya rate-limit yiyor

### 4. Playwright input[type="file"] doğrudan

- File input bulunuyor ama `multiple` attribute'u yok
- Tek dosya yüklenebiliyor ama karusel için çoklu dosya ekleme butonu görünmüyor
- **Sonuç:** Karusel oluşturma için yetersiz

## Çalışan Yöntem

**Manuel:** Görselleri + caption'ı kullanıcıya Telegram'dan gönder, kullanıcı telefon uygulamasından karusel olarak yayınlasın.

```
MEDIA:/tmp/karusel_yayin/01_Kapak.jpg
...
```

## Neden Çalışmıyor?

1. **WARP SOCKS5 proxy Instagram CDN'ini blokluyor**
   - Console'da sürekli `ERR_CONNECTION_CLOSED` ve `ERR_PROXY_CONNECTION_FAILED`
   - Instagram'ın static.cdninstagram.com gibi CDN kaynakları yüklenemiyor
   - JS framework'ü düzgün render olmuyor

2. **Instagram Web 2026 post oluşturma akışını değiştirmiş**
   - Eski "file dialog aç → dosya seç" akışı çalışmıyor
   - Yeni akışta Post butonu tıklansa bile file dialog gelmiyor
   - Instagram web'de post oluşturma özelliği kısıtlanmış veya kaldırılmış olabilir

## Alternatif: Proxy'siz Playwright (Sadece Gezinti İçin)

Desktop Instagram sayfası **WARP'sız** daha hızlı ve kararlı yükleniyor:

```python
# WARP'sız Playwright (sadece gezinti/login kontrolü için)
ctx = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    viewport={"width": 1280, "height": 800}
)
```

Bu yöntem sayfa yüklemek, profil bilgisi okumak ve cookie refresh için çalışıyor. Ancak API istekleri için hâlâ WARP gerekli.
