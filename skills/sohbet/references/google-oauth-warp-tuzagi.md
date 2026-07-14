# Google OAuth & WARP Tuzağı

> Keşif tarihi: 29 May 2026 | Oturum: Vanitas dönüşümü

## WARP SOCKS5 → Google API Engeli

**Semptom:** Google API çağrıları (Gmail, Calendar, OAuth, PubMed) SOCKS5 proxy üzerinden
`Connection reset by peer` veya `REFRESH_FAILED` hatası verir.

**Kök neden:** WARP SOCKS5 proxy'si (warp:1080) Google'ın veri merkezi IP'lerini
tespit edip engellemesine neden oluyor. Google, SOCKS5 üzerinden gelen trafiğe güvenmiyor.

**Kalıcı çözüm:** Tüm Google API çağrılarında `ALL_PROXY=""` kullan:

```bash
# Gmail
ALL_PROXY="" python3 google_api.py gmail search "is:unread"

# OAuth refresh
ALL_PROXY="" python3 setup.py --check
ALL_PROXY="" python3 setup.py --auth-url
ALL_PROXY="" python3 setup.py --auth-code "CODE"

# PubMed Entrez
ALL_PROXY="" python3 -c "from Bio import Entrez; ..."
```

## Google OAuth Token Yenileme

**Token ömrü:** Google Cloud Console "Testing" modunda **7 gün**. 
"Production" moda geçilirse 6 aya kadar uzar.

**Refresh token neden işe yaramaz:**
- Token 7 günden eskiyse (Testing modu)
- Kullanıcı şifre değiştirdiyse
- Token revoke edildiyse
- 6 aydır hiç kullanılmadıysa

**Manuel yenileme adımları (3 adım, 60 saniye):**

```bash
# 1. Auth URL üret
ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url

# 2. URL'i Edel'e gönder → tıklasın → Google girişi → localhost:1 hatası → adres çubuğundaki URL'i kopyalasın

# 3. Kodu exchange et (60 saniye içinde!)
ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "KOD"
```

**Otomatik canlı tutma:** `refresh_google_token.sh` cron'u her gece 03:00'te 
basit bir Gmail sorgusu yaparak token'ı canlı tutar.

## Etkilenen Tüm Servisler

| Servis | ALL_PROXY="" şart mı? |
|--------|----------------------|
| Google OAuth | ✅ EVET |
| Gmail API | ✅ EVET |
| Google Calendar | ✅ EVET |
| PubMed Entrez | ✅ EVET |
| YouTube (yt-dlp) | ❌ WARP ile çalışır |
| Semantic Scholar | ❌ WARP ile çalışır |
| Instagram | ❌ WARP şart |
| DeepSeek API | ⚠️ WARP ile takılabilir |
