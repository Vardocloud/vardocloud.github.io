# LinkedIn API Integration — Working Reference (Updated 1 Jun 2026)

## Tested & Working

### Text Post (UGC Posts)
```
POST https://api.linkedin.com/v2/ugcPosts
```

**Headers:**
```
Authorization: Bearer <access_token>
X-Restli-Protocol-Version: 2.0.0
LinkedIn-Version: 202505
Content-Type: application/json
```

**Request Body:**
```json
{
    "author": "urn:li:person:hy0rYB54uc",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": "Post metni buraya..."},
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}
```

### Image Post (1 Jun 2026 — test edildi ✅)

İki aşamalı: önce image'i upload et, sonra post body'sine ekle.

**1. Upload kaydı oluştur:**
```
POST https://api.linkedin.com/v2/assets?action=registerUpload
```
```json
{
    "registerUploadRequest": {
        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
        "owner": "urn:li:person:hy0rYB54uc",
        "serviceRelationships": [{
            "relationshipType": "OWNER",
            "identifier": "urn:li:userGeneratedContent"
        }]
    }
}
```
Response → `uploadUrl` + `asset` URN (örn: `urn:li:digitalmediaAsset:...`)

**2. Binary image'i PUT ile yükle:**
```
PUT <uploadUrl>
Content-Type: application/octet-stream
<binary image data>
```

**3. Post body'sinde media ekle:**
```json
{
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": "Post metni"},
            "shareMediaCategory": "IMAGE",
            "media": [{
                "status": "READY",
                "description": {"text": "İlk 200 karakter"},
                "media": "urn:li:digitalmediaAsset:...",
                "title": {"text": "Bardo Psychology"}
            }]
        }
    }
}
```

### Post Silme (1 Jun 2026 — test edildi ✅)

URN **URL-encode edilmeli** (örn: `urn:li:share:7466980800698269698` → `urn%3Ali%3Ashare%3A7466980800698269698`)

```
DELETE https://api.linkedin.com/v2/ugcPosts/urn%3Ali%3Ashare%3A7466980800698269698
```
Başarılı → `204 No Content`

### Token Alımı (OAuth 2.0 Authorization Code Flow)

**Authorization URL:**
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=CLIENT_ID&redirect_uri=http://localhost/callback&scope=openid profile email w_member_social&state=RANDOM
```

**Token Exchange:**
```
POST https://www.linkedin.com/oauth/v2/accessToken
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
code=<CODE_FROM_URL>
redirect_uri=http://localhost/callback
client_id=CLIENT_ID
client_secret=CLIENT_SECRET
```

**Response:** `200 OK`
```json
{
    "access_token": "AQV60O...",
    "expires_in": 5183999,
    "refresh_token": "AQX3VT...",
    "scope": "email,openid,profile,w_member_social"
}
```

### Token Refresh
```
POST https://www.linkedin.com/oauth/v2/accessToken
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
refresh_token=<REFRESH_TOKEN>
client_id=CLIENT_ID
client_secret=CLIENT_SECRET
```

### Person URN (User Info)
```
GET https://api.linkedin.com/v2/userinfo
Authorization: Bearer <access_token>
```
URN format: `urn:li:person:{sub}`

## NOT Tested

- REST Posts API (`/rest/posts`)
- Video upload
- Organization (company page) posting — sadece personal profile

## Pollinations Görsel Üretim (LinkedIn postları için)

Bkz. `references/pollinations-image-gen.md` — model listesi, API key pitfall, flux/nanobanana kullanımı.

## Pollinations Görsel Üretim (LinkedIn postları için)

Bkz. `references/pollinations-image-gen.md` — model listesi, API key pitfall, flux/nanobanana kullanımı.
