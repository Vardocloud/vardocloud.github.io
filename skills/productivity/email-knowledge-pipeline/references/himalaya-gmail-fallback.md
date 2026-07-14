# Himalaya IMAP Fallback — OAuth Expired Olduğunda

Gmail OAuth token'ı her 7 günde bir expire olur. Refresh token da expired/revoked olduğunda (ör: oturum açma değişikliği, uzun süre kullanılmama), Google API'ye erişim tamamen kesilir. Bu durumda **Himalaya CLI + IMAP App Password** güvenilir alternatiftir.

## Ön Koşul

Himalaya IMAP daha önce kurulmuş ve yapılandırılmış olmalı:
- Konfigürasyon: `~/.config/himalaya/config.toml`
- App Password: `~/.config/himalaya/gmail_pass` (16 haneli, 4'lü gruplar halinde)
- Araç: `which himalaya` ile kurulu olduğu doğrulanabilir

## Himalaya Sorgu Sözdizimi (ÖNEMLİ)

Himalaya'nın sorgu sözdizimi **standart IMAP değildir.** Doğrudan argüman olarak yazılır, `--query` flag'i YOKTUR:

```bash
# DOĞRU
himalaya envelope list from "apa.org"

# YANLIŞ — "--query" flag'i tanınmaz
himalaya envelope list --query "from:apa.org"
```

Desteklenen operatörler: `from <pattern>`, `to <pattern>`, `subject <pattern>`, `before <date>`, `after <date>`, `date <date>`, `body <pattern>`, `flag <flag>`, `not`, `and`, `or`

## Tracking Link Çıkarma

Email body'sinde subscription tracking linkleri varsa (örn. APA için `click.info.apa.org/?qs=`):

```bash
# 1. Email'i oku
himalaya message read 571 --account gmail

# 2. Tracking linkini resolve et (asıl URL'yi bul)
curl -sI -L --max-redirs 5 "https://click.info.apa.org/?qs=LONG_QS_STRING" 2>&1 | grep -i "^location:" | tail -1

# 3. Asıl URL public mi kontrol et
curl -sI "https://asıl-url" | grep -i "^http/"
# 200 = public, 403 = üyelik gerekli
```

## OAuth vs IMAP Seçim Kriteri

| Durum | Hangisini Kullan |
|--------|-----------------|
| OAuth token valid | `google_api.py` (standart pipeline) |
| OAuth REFRESH_FAILED + Himalaya config var | Himalaya IMAP |
| OAuth REFRESH_FAILED + Himalaya config yok | OAuth yenile (bkz: google-workspace skill) |
| İkisi de çalışmıyor | Browser login dene (son çare) |

## Sık Kullanılan Sorgular

```bash
# APA mailleri
himalaya envelope list from "apa.org" order by date

# Skool bildirimleri  
himalaya envelope list from "skool.com" order by date

# Okunmamış mailler (IMAP flag ile)
himalaya envelope list flag unseen

# Belirli tarihten sonra
himalaya envelope list from "apa.org" after 2026-07-01
```
