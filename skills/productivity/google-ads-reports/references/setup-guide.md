# Google Ads Script Kurulum Kılavuzu

## Adım Adım

1. **Google Ads hesabına gir**
   - `ads.google.com`

2. **Scriptler sayfasını aç**
   - Araçlar ve Ayarlar (Tools & Settings) → Toplu İşlemler (Bulk Actions) → **Scripts**

3. **Yeni Script oluştur**
   - "+" butonuna tıkla
   - "Yeni Script" seç

4. **Kodu yapıştır**
   - `~/.hermes/scripts/google_ads_script.gs` dosyasındaki kodun tamamını kopyala
   - Script editörüne yapıştır
   - E-posta adresini kontrol et (varsayılan: `isimgorulsunn@gmail.com`)

5. **İzinleri ver**
   - "Kaydet" dediğinde Google Ads API izinleri isteyecek
   - "Authorize" / "İzin Ver" de

6. **Test et**
   - "Önizleme" (Preview) butonuna tıkla
   - Script çalışıp Gmail'ine test e-postası gönderecek

7. **Schedule et**
   - "Schedule" / "Zamanlama" seç
   - Sıklık: **Günlük** (Daily)
   - Saat: **09:00** (sabah raporu için)
   - "Kaydet"
