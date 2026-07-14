# Instagram API Endpoints (Cookie Auth)

## Çalışan Endpoint'ler

### Profil Bilgisi
```
GET https://www.instagram.com/api/v1/users/web_profile_info/?username=<username>
```
**Dönen:**
```json
{
  "data": {
    "user": {
      "username": "bardopsikoloji",
      "full_name": "bardopsikoloji",
      "biography": "...",
      "external_url": null,
      "edge_followed_by": {"count": 26},
      "edge_follow": {"count": 4},
      "edge_owner_to_timeline_media": {"count": 71},
      "profile_pic_url": "...",
      "is_private": false
    }
  }
}
```

### Son Postlar
```
GET https://www.instagram.com/api/v1/feed/user/<user_id>/?count=6
```
**Dönen:**
```json
{
  "items": [{
    "code": "DYDHTD9jlMD",
    "caption": {"text": "..."},
    "like_count": 0,
    "comment_count": 1,
    "taken_at": 1746619200
  }]
}
```

## Çalışmayan Endpoint'ler

| Endpoint | Hata | Neden |
|---|---|---|
| `i.instagram.com/api/v1/users/X/info/` | Boş user objesi | Yeni API yapısı |
| `www.instagram.com/api/v1/accounts/current_user/` | Boş JSON | Farklı auth bekliyor |
| HTML scraping (`instagram.com/username/`) | Veri CSR'da | React/SSR, curl HTML'de veri yok |

## Gerekli Header'lar (HER ZAMAN)

```
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15
X-CSRFToken: <cookie'deki csrftoken değeri>
X-IG-App-ID: 936619743392459
X-Requested-With: XMLHttpRequest
```

## WARP Zorunlu

Tüm istekler `--socks5 127.0.0.1:1080` ile WARP üzerinden gitmeli. WARP'sız istek Oracle Cloud IP'sini gösterir → Instagram `checkpoint_required` döner.

## Headless Browser

Cookie'leri direkt enjekte edemediği için şimdilik çalışmıyor. Playwright kurulumu gerekiyor (TODO).

## Test Tarihi

2026-05-28: Cookie + WARP ile profil bilgisi ve son postlar başarıyla çekildi (Edel'in @bardopsikoloji hesabı).
