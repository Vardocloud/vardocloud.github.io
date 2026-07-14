# Facebook Developer → Instagram Graph API Kurulum Rehberi

Instagram otomasyonu (post atma, yorum yönetimi, istatistik, DM) için Facebook Graph API kurulum adımları.

## Ön Koşullar (ZORUNLU)

- Instagram hesabı **Business veya Creator** olmalı (kişisel hesapla Graph API çalışmaz)
- Instagram hesabı bir **Facebook Page'e bağlı** olmalı (izin akışı Page üzerinden geçer)
- **Meta Developer hesabı** (ücretsiz — Facebook hesabınla geliştirici kaydı)

## Adım Adım Kurulum

### 1. Meta Developer hesabı oluştur
developers.facebook.com → Mevcut Facebook hesabınla giriş → Developer hesabın yoksa otomatik oluşur.

### 2. Yeni uygulama oluştur — "Business" türü
- Sağ üst **Create App** → **Business** seç
- Uygulama adı ver (örn: "Bardo Otomasyon")
- İletişim e-posta adresin
- **App ID** ve **App Secret** alırsın → güvenli sakla

### 3. Instagram product'ını ekle
App Dashboard → **Add Product** → **Instagram** → **Set Up**

İki login yöntemi:
- **Instagram Login**: Instagram kullanıcı adı/şifre ile direkt bağlanma
- **Facebook Login** ⭐ (önerilen): Facebook Page'e bağlı Instagram için — daha fazla izin

### 4. Instagram hesabını bağla
**Instagram > API Setup** bölümünden Instagram hesabını ekle. Hesap **public** olmalı.

### 5. Access Token al
Graph API Explorer'da:
- Uygulamanı seç
- Instagram Business ID'yi hedef seç
- İzinleri ekle
- **Generate Token** → **Exchange for Long-Lived Token** (60 gün)

### 6. Instagram Business Account ID'yi bul
PAGE_ID'yi aldıktan sonra:
- Endpoint: `/PAGE_ID?fields=instagram_business_account`
- Yanıt: `{"instagram_business_account": {"id": "17841478124961208"}, "id": "PAGE_ID"}`

## Token Debug

Token alınca hemen test et:
- Endpoint: `/debug_token?input_token=$TOKEN`
- Kontrol edilecek alanlar:
  - `is_valid`: true olmalı
  - `expires_at`: 0 = süresiz/süresi belirsiz; Unix timestamp varsa bitiş tarihi
  - `type`: PAGE (sayfa token'ı) veya USER
  - `scopes`: izin listesi — her bir izin ayrı yetki
  - `granular_scopes`: hangi hedef ID'ler için geçerli

## Hata Kodları

| Hata | Anlamı | Çözüm |
|------|--------|-------|
| 190 / subcode 460 | Token expired | Graph API Explorer'dan yenile |
| 200 / (#200) | İzin yok / App Review bekliyor | instagram_content_publish ve instagram_manage_messages için Meta incelemesi gerekli (1-4 hafta) |
| #17 | Rate limit | Hesap başı ~200 istek/saat |
| #100 | Geçersiz parametre / kişisel hesap | Business/Creator hesaba geçir |

## Bardo Psikoloji — Kayıtlı Değerler

- **Uygulama:** Otonom Psikoloji İçerik Motoru
- **Page ID:** `579065298632893`
- **Instagram Business ID:** `17841478124961208`
- **Token:** `~/.hermes/instagram_graph_token.txt` (chmod 600)
- **İzinler:** instagram_basic, instagram_content_publish, instagram_manage_comments, instagram_manage_insights, pages_manage_posts, publish_video, pages_read_engagement, pages_read_user_content, business_management
