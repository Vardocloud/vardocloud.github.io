# APA Webinar Registration Flow

APA web seminerlerine kaydolmak için izlenmesi gereken adımlar.

## 1. Webinar Sayfasını Bul

APA webinar sayfaları genelde `www.apa.org/education-career/training/...` altındadır. Web search veya mail içindeki linkten bulunur.

**Kayıt linki örneği:** `https://www.apa.org/education-career/training/mentoring-as-networking`

## 2. Sepete Ekle (ADD TO CART)

APA kendi cart sistemini kullanır. Sayfada "ADD TO CART" butonu vardır.
- **APA üyeleri için:** Ücretsiz ($0)
- **Üye olmayanlar için:** Genelde $49

## 3. APA Hesabına Giriş (SSO ZORUNLU)

ADD TO CART tıklandığında APA login sayfasına yönlendirir. Giriş seçenekleri:
- Email/şifre ile direkt giriş
- **Google ile giriş** (en kolay — APA Google SSO kullanır)
- Tek kullanımlık kod ile giriş

**⚠️ ÖNEMLİ:** APA login sayfası Google SSO yönlendirmesi yapar ve bu **kullanıcı etkileşimi gerektirir.** Vanitas bu adımı otomatik tamamlayamaz — Google hesabı browser'da oturum açık değilse şifre/2FA gerekir.

## 4. Tam Otomatik Olmayan Kayıt İşlemi (Kural)

Vanitas APA webinar kaydını **tamamen otomatik** yapamaz çünkü:
1. APA login → Google SSO → kullanıcı onayı gerekir
2. Sepet/checkout işlemi browser etkileşimi gerektirir
3. Google hesabında oturum açık olmayabilir

**Doğru akış:**
1. Webinar sayfasını bul ve linki çıkar
2. Edel'e kayıt linkini ver — kendi cihazından Google SSO ile giriş yapıp kaydolabilir
3. **Ayrı olarak:** Etkinliği Google Takvim'e eklemeyi teklif et (bu adım tam otomatik)

## 5. Google Takvim'e Ekleme (Tam Otomatik)

Google Calendar API (google-workspace skill) ile etkinlik eklenebilir:
```bash
ALL_PROXY="" python3 google_api.py calendar create \
  --summary "APA Webinar: Mentoring as Networking" \
  --start "2026-06-30T20:00:00+03:00" \
  --end "2026-06-30T21:00:00+03:00" \
  --description "Tanya Menon, PhD - Mentoring as Networking\nKayıt: https://www.apa.org/education-career/training/mentoring-as-networking"
```

## 6. Sık Karşılaşılan Durumlar

| Durum | Aksiyon |
|-------|---------|
| ADD TO CART sayfa değiştirmez | JavaScript gerekli — browser tool ile dene veya Edel'e link ver |
| Google SSO yönlendirmesi kullanıcı şifresi ister | Linki Edel'e ver, kendi yapsın |
| APA üyesi değil ($49) | Edel'e ücret bilgisini bildir, onay almadan kayıt yapma |
| Webinar Zoom üzerinden (apa-org.zoom.us) | Normal — APA webinar'ları Zoom kullanır |
| Kayıt onay maili Zoom'dan gelir ("Onay" konulu) | Mail doğruysa (iCal/.ics varsa) kayıt başarılı demektir |
