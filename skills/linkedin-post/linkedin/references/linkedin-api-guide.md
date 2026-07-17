---
name: linkedin-api
description: "LinkedIn API entegrasyonu — OAuth 2.0 token yönetimi, Posts API (/rest/posts) ile post oluşturma, görsel yükleme. ugcPosts → Posts API migrasyonu."
version: 1.0.0
metadata:
  hermes:
    tags: [linkedin, api, oauth, posts, integration]
    category: linkedin-post
---

# LinkedIn API Entegrasyonu

## 🔑 ZORUNLU: Token Kontrol Adımı (Her İşlem Öncesi)

**ÖNCE token durumunu kontrol et:**

```bash
cd ~/.hermes/linkedin-poster && python3 -c "
from linkedin_client import LinkedInClient
import os, json, time
client = LinkedInClient()
if os.path.exists(client.token_path):
    with open(client.token_path) as f:
        data = json.load(f)
    remaining = data.get('expires_in', 0) - (time.time() - data.get('created_at', 0))
    print(f'Token: {\"✅\" if remaining > 0 else \"❌\"} ({remaining/86400:.1f} gün kaldı)')
else:
    print('Token: ❌ Dosya yok')
```

**Karar:**
- `expires_in_days > 7` → ✅ **Token geçerli, OAuth gerekmez.** Direkt post akışına geç.
- `expires_in_days <= 7` → ⚠️ **Token yakında bitecek.** Refresh dene, olmazsa OAuth başlat.
- Token yok / hata → 🔄 **OAuth akışı başlat** (auth URL + callback server).

**Önemli:** Token dosyası `~/.hermes/secrets/linkedin_token.json` içinde, `linkedin-poster/` altında değil!

## Ne Zaman Kullanılır

- LinkedIn token yenileme veya OAuth flow başlatma
- `linkedin_client.py` veya `linkedin_api.py` ile post paylaşma
- LinkedIn API hata ayıklama (401, 403, 404, 400)
- Yeni bir LinkedIn OAuth token'ı alma

## ⚠️ LinkedIn API Migrasyonu (Haziran 2026)

LinkedIn Marketing Version 202505 (May 2025) **sunset edildi**. Eski `ugcPosts` endpoint'i artık çalışmaz.

### Değişenler

| Eski (ugcPosts — KALDIRILDI) | Yeni (Posts API — ZORUNLU) |
|---|---|
| `POST /v2/ugcPosts` | `POST /rest/posts` |
| `LinkedIn-Version` header opsiyoneldi | **`Linkedin-Version: YYYYMM` zorunlu** |
| `specificContent.com.linkedin.ugc.ShareContent.shareCommentary` | `commentary` (düz string alanı) |
| `specificContent.com.linkedin.ugc.ShareContent.shareMediaCategory` | `content.media.id` (ayrı alan) |
| `visibility.com.linkedin.ugc.MemberNetworkVisibility` | `visibility` (düz enum — `"PUBLIC"`) |
| Post ID: `location` header'da | Post ID: **`x-restli-id`** header'da |
| `isReshareDisabledByAuthor` yok | `isReshareDisabledByAuthor: false` eklenmeli |

### Değişmeyenler

- Görsel/video upload flow: `POST /v2/assets?action=registerUpload` hala çalışıyor
- User info endpoint: `GET /v2/userinfo` değişmedi
- Token exchange: `POST /oauth/v2/accessToken` değişmedi
- OAuth scope: `w_member_social` (kişisel hesap) hala geçerli
- Auth URL formatı: değişmedi

## OAuth 2.0 Token Yönetimi

### Auth URL Oluşturma

```python
scope = "openid profile email w_member_social"
auth_url = (
    "https://www.linkedin.com/oauth/v2/authorization"
    "?response_type=code"
    "&client_id={CLIENT_ID}"
    "&redirect_uri={REDIRECT_URI}"
    "&scope={scope}"
)
```

**Redirect URI stratejisi:**
- **Birincil:** `http://localhost/callback` — manuel kod kopyalama (callback server gerekmez)
- **Yedek:** Port 80'de callback server (Oracle Cloud VCN'de 8888 kapalı!)
- **Port çakışması:** SearXNG 8888'de çalışıyorsa farklı port kullan

### Token Exchange

```python
# Authorization code → Access Token
POST https://www.linkedin.com/oauth/v2/accessToken
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
code={CODE}
redirect_uri={REDIRECT_URI}
client_id={CLIENT_ID}
client_secret={CLIENT_SECRET}
```

### Token Refresh

```python
POST https://www.linkedin.com/oauth/v2/accessToken
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
refresh_token={REFRESH_TOKEN}
client_id={CLIENT_ID}
client_secret={CLIENT_SECRET}
```

Access token 60 gün geçerli, refresh token ile yenilenebilir.

### Person ID (URN) Alma

```python
GET https://api.linkedin.com/v2/userinfo
Authorization: Bearer {access_token}
# Response: {"sub": "abc123", ...}
# URN: f"urn:li:person:{sub}"
```

## Posts API — Post Paylaşma

### Text Post (Yeni API)

```python
import httpx

response = httpx.post(
    "https://api.linkedin.com/rest/posts",
    headers={
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Linkedin-Version": "202605",  # ZORUNLU!
        "Content-Type": "application/json"
    },
    json={
        "author": f"urn:li:person:{user_id}",
        "commentary": "Post içeriği buraya...",
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }
)
# Başarılı → 201, x-restli-id: urn:li:share:...
```

### Görselli Post

```python
# 1. Upload kaydı oluştur
reg_resp = httpx.post(
    "https://api.linkedin.com/v2/assets?action=registerUpload",
    headers={"Authorization": f"Bearer {access_token}", ...},
    json={
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": f"urn:li:person:{user_id}",
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
)
upload_url = reg_resp.json()["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
asset_urn = reg_resp.json()["value"]["asset"]

# 2. Binary image'i PUT ile yükle
httpx.put(upload_url, content=image_bytes, headers={"Content-Type": "application/octet-stream"})

# 3. Posts API ile post oluştur (image referansı ile)
httpx.post("https://api.linkedin.com/rest/posts", ..., json={
    "author": f"urn:li:person:{user_id}",
    "commentary": "Post metni",
    "visibility": "PUBLIC",
    "distribution": {...},
    "content": {
        "media": {
            "title": "Görsel başlığı",
            "id": asset_urn   # "urn:li:digitalmediaAsset:..."
        }
    },
    "lifecycleState": "PUBLISHED",
    "isReshareDisabledByAuthor": False
})
```

## Token Kaybı ve Kurtarma

**Token dosyası** (`linkedin_token.json`) Hermes güncellemeleri sırasında kaybolabilir.
Kurtarma adımları:

1. `linkedin_client.py` içinde `get_auth_url()` ile auth URL oluştur
2. Edel linki tarayıcıda açar, LinkedIn onayı verir
3. Tarayıcı `http://localhost/callback?code=...` adresine yönlenir (sayfa açılmaz — normal)
4. Edel adres çubuğundaki URL'in tamamını kopyalar
5. `code` parametresini parse et → `exchange_code_for_token()` ile token al
6. Token `linkedin_token.json` dosyasına kaydedilir

## Dosya Konumları

| Dosya | İçerik | Not |
|---|---|---|
| `~/.hermes/linkedin-poster/linkedin_client.py` | LinkedIn API client (güncel: Posts API) | Ana client |
| `~/.hermes/secrets/linkedin_token.json` | OAuth access + refresh token | Güncellemede korunur |
| `~/.hermes/linkedin-poster/.env` | `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REDIRECT_URI` | 600 izin |
| `~/.hermes/skills/linkedin-post/linkedin/` | Detaylı LinkedIn skill (OAuth, post, hatalar) | Daha kapsamlı referans |

## Test/Gönderi Güvenliği

**Kesin kural: `lifecycleState: PUBLISHED` olmadan hiçbir post gerçek hesaba gitmez.** Ama yine de:

- ⚠️ Token refresh/test işlemi yaparken ASLA post gönderme endpoint'ine istek atma
- ⚠️ `linkedin_client.py` üzerinde debug yaparken `dry_run=True` parametresi varsa kullan, yoksa hiç post API'sini çağırma
- ⚠️ Edel'in hesabında "VANİTAS DENEMESİ" / test içerikli paylaşımlar çıktığı geçmişte yaşandı — **test amaçlı bile olsa asla post oluşturma**
- ⚠️ Token yenileme için sadece `/oauth/v2/accessToken` endpoint'ini kullan, `/rest/posts` veya `/v2/ugcPosts` ile işlem yapma

### Refresh Token Dayanıklılığı

LinkedIn refresh token'ları, access token süresi dolduktan **çok uzun süre sonra** (örnekte 20.000+ gün) bile çalışır. Access token 60 günlük olsa da refresh token kalıcıdır. Şu durumlarda her zaman refresh dene:

- Token dosyası var ama `expires_in` süresi geçmiş → doğrudan refresh dene
- Token 401 döndü → refresh dene
- Refresh başarısız olursa (HTTP 400 "invalid_grant") → ancak o zaman OAuth akışı başlat

## Sık Hata Durumları

| HTTP | Sebep | Çözüm |
|------|-------|-------|
| 400 | Yanlış payload (eski ugcPosts formatı) | Posts API formatını kullan |
| 401 | Token expire | Refresh token dene, yoksa yeni OAuth |
| 403 | Scope yetkisiz / ürün eksik | Developer Portal → Products → "Share on LinkedIn" |
| 404 | Eski endpoint (ugcPosts) | `/rest/posts` kullan |
| `invalid_redirect_uri` | Developer Portal'da kayıtlı değil | Auth sekmesinde URI'yi kontrol et |
| `x-restli-id` yok | API versiyonu yanlış | `Linkedin-Version` header'ını kontrol et |
