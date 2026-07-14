# Bitwarden Password Manager — Google Hesap Bilgileri

NotebookLM MCP re-auth için kullanılabilecek Google hesap bilgileri.

## Kayıtlar (bw-serve port 8087, unlocked)

| Item | User ID | Username | Password |
|------|---------|----------|----------|
| `Google-isimgorulsunn` | `8a95abcd-65dd-4aa5-a255-b4660182d7cf` | isimgorulsunn@gmail.com | ✅ Var |
| `google-pro` | `75750341-e3ca-43b7-ab6d-b47b00e0d0ad` | kenshin4155@gmail.com | ✅ Var |
| `APA` | `ddaa4ca8-b147-490d-976b-b4830115b8bc` | isimgorulsunn@gmail.com | ✅ Var |

## Erişim

```bash
# bw-serve API (unlocked) ile şifre al
curl -s http://127.0.0.1:8087/object/item/8a95abcd-65dd-4aa5-a255-b4660182d7cf | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['login']['password'])"
```

**Sensitive Input Protocol:** Şifreyi asla Telegram'a yazma. Script içinde kullan, çıktıda mask.

## Otomatik Login Scripti

`scripts/nlm_cdp_login.py` — Keepalive Chrome'da CDP üzerinden otomatik login.
Bitwarden'dan şifre alır, Playwright ile form doldurur, NotebookLM'e giriş yapar.

## Güvenlik

- bw-serve localhost:8087 (dışa kapalı)
- Şifre Bitwarden vault'ta encrypted
- Script çıktısında şifre maskelenir
